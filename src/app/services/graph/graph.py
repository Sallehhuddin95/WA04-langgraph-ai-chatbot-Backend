"""Graph wiring. Owns edge order, retry counter, and checkpoints.

StateGraph: router -> retriever -> grader -> generator with a bounded
retry loop. Checkpointer is in-memory until the checkpoint-postgres
swap lands (migration 0004 is still a placeholder).

``run_turn`` keeps the same node order as a plain runner. The service
calls ``run_turn``. ``build_graph`` returns the compiled StateGraph.
"""

from __future__ import annotations

import uuid

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.services.graph.generator import (
    direct_reply,
    generate_reply,
    ungrounded_reply,
    vision_reply,
)
from app.services.graph.grader import MAX_RETRIES, grade_draft, needs_retry
from app.services.graph.retriever import retrieve_docs
from app.services.graph.router import route_turn
from app.services.graph.state import ChatState


def _router_node(state: ChatState) -> ChatState:
    state["trace_id"] = state.get("trace_id") or str(uuid.uuid4())
    state["retry_count"] = int(state.get("retry_count", 0) or 0)
    return route_turn(state)


def _bump_retry(state: ChatState) -> ChatState:
    state["retry_count"] = int(state.get("retry_count", 0)) + 1
    return state


def _route_after_router(state: ChatState) -> str:
    if state.get("image_urls"):
        return "vision"
    if state.get("intent_category") == "simple_chat":
        return "direct"
    return "retriever"


def _check_after_generator(state: ChatState) -> str:
    if state.get("is_grounded", False):
        return END
    if needs_retry(state) and int(state.get("retry_count", 0)) < MAX_RETRIES:
        return "bump_retry"
    return "fallback"


def _fallback_node(state: ChatState) -> ChatState:
    return ungrounded_reply(state)


def build_graph():
    """Compile the chat StateGraph with an in-memory checkpointer."""
    builder = StateGraph(ChatState)
    builder.add_node("router", _router_node)
    builder.add_node("direct", direct_reply)
    builder.add_node("vision", vision_reply)
    builder.add_node("retriever", retrieve_docs)
    builder.add_node("grader", grade_draft)
    builder.add_node("generator", generate_reply)
    builder.add_node("bump_retry", _bump_retry)
    builder.add_node("fallback", _fallback_node)
    builder.add_edge(START, "router")
    builder.add_conditional_edges(
        "router",
        _route_after_router,
        {
            "direct": "direct",
            "retriever": "retriever",
            "vision": "vision",
        },
    )
    builder.add_edge("vision", END)
    builder.add_edge("direct", END)
    builder.add_edge("retriever", "grader")
    builder.add_edge("grader", "generator")
    builder.add_conditional_edges(
        "generator",
        _check_after_generator,
        {END: END, "bump_retry": "bump_retry", "fallback": "fallback"},
    )
    builder.add_edge("bump_retry", "retriever")
    builder.add_edge("fallback", END)
    return builder.compile(checkpointer=MemorySaver())


def run_turn(state: ChatState) -> ChatState:
    """Run one turn through router, retriever, grader, generator."""
    state["trace_id"] = state.get("trace_id") or str(uuid.uuid4())
    state["retry_count"] = int(state.get("retry_count", 0) or 0)

    route_turn(state)
    if state.get("image_urls"):
        vision_reply(state)
        return state
    if state.get("intent_category") == "simple_chat":
        state["retrieved_docs"] = []
        state["is_grounded"] = False
        state["grounding_score"] = 0.0
        direct_reply(state)
        # Direct path never cites; keep the no-citation invariant.
        state["citations"] = []
        return state

    retrieve_docs(state)
    grade_draft(state)
    generate_reply(state)

    while needs_retry(state) and int(state.get("retry_count", 0)) < MAX_RETRIES:
        state["retry_count"] = int(state.get("retry_count", 0)) + 1
        # Retry re-fetches docs for the same query (stub) then regrades.
        # TODO(retry): vary the query or filter per attempt when real
        # recall lands, instead of repeating the same call.
        retrieve_docs(state)
        grade_draft(state)
        generate_reply(state)
        if state.get("is_grounded", False):
            break

    if not state.get("is_grounded", False):
        ungrounded_reply(state)

    return state

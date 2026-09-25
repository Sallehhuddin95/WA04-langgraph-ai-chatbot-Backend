# 0007 Use Multi-Model Routing With Bounded Grounding

## Status

Accepted

## Context

Chat traffic mixes small talk, doc questions, and multi-step tasks. One model for all nodes costs too much or grades poorly. Unbounded retries add latency and looping bills.

The graph needs cheap triage, strict grounding checks, and one strong writer. It also needs a fixed retry cap with a safe fallback.

## Decision

Use three intent values:

- `simple_chat`: greeting or small talk with no doc need
- `rag_search`: question that needs retrieved docs
- `complex_task`: multi-step task that needs retrieve plus planned generation

Assign models per node:

- router: DeepSeek V4 Flash, input user text plus short history, output `intent_category`
- retriever: embedding search only, no LLM
- grader: DeepSeek V4 Flash, input draft plus docs, output `is_grounded` plus score
- generator: Muse Spark 1.3, input messages plus filtered docs, output reply plus `citations`

Apply bounded grounding:

- max 2 grader retries per turn
- retry only on `rag_search` and `complex_task`
- each retry narrows or refetches docs, then regenerates
- after 2 failed grades, return fallback with `is_grounded=false` and no citations

Apply the citation rule:

- if `is_grounded=true`, response must include at least one entry in `citations`
- each citation must map to a retrieved chunk id
- if `is_grounded=false`, response must carry an empty `citations` list and a plain-language notice

## Consequences

Benefits:

- cheap models handle triage and grading
- strong model focuses on final writing
- retry cap bounds cost and latency
- citation rule makes grounding checks observable

Costs and tradeoffs:

- two model vendors means two keys, quotas, and failure modes
- prompts must stay in sync across router, grader, and generator
- fallback replies can feel thin when docs score poorly

## Alternatives Considered

### One Model for All Nodes

Rejected. It overpays for triage or weakens grading. Per-node models fit cost to task.

### Unbounded Retry Until Grounded

Rejected. It risks loops, slow turns, and runaway cost. A fixed cap with fallback is safer.

### Citations Optional on Grounded Replies

Rejected. Optional citations hide grounding gaps. Required citations keep the contract testable.

"""App entry. Wires routers plus CORS for the web frontend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.chat import router as chat_router


def create_app() -> FastAPI:
    app = FastAPI(title="LangGraph AI Chatbot Backend")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Retry-After"],
    )
    app.include_router(auth_router)
    app.include_router(chat_router)
    return app


app = create_app()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

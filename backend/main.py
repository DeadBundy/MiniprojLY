from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database.database import Base, engine, get_db
from backend.routers import journal, chat, emotions, reports


def create_app() -> FastAPI:
    app = FastAPI(
        title="Mental Health Monitoring System",
        description=(
            "AI-assisted mental wellness journaling and conversational system. "
            "This is NOT a medical or psychological diagnosis tool."
        ),
        version="0.1.0",
    )

    # CORS for local dev (React on 3000)
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create DB tables on startup for demo purposes
    @app.on_event("startup")
    def on_startup() -> None:
        Base.metadata.create_all(bind=engine)

    # Health check
    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    # Include feature routers
    app.include_router(journal.router, prefix="/api/journal", tags=["journal"])
    app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
    app.include_router(emotions.router, prefix="/api/emotions", tags=["emotions"])
    app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

    return app


app = create_app()


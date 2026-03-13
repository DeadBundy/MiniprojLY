from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.tables import EmotionEvent
from backend.schemas import EmotionEventCreate


router = APIRouter()


@router.post("", response_model=dict)
def create_event(payload: EmotionEventCreate, db: Session = Depends(get_db)) -> dict:
    if payload.source not in {"text", "face"}:
        raise HTTPException(status_code=400, detail="Invalid source")

    created_at = payload.created_at or datetime.utcnow()
    ev = EmotionEvent(
        user_id=payload.user_id,
        source=payload.source,
        emotion=payload.emotion,
        score=payload.score,
        created_at=created_at,
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return {"id": ev.id}


@router.get("/recent", response_model=list[dict])
def recent(user_id: int, limit: int = 200, db: Session = Depends(get_db)) -> list[dict]:
    limit = max(1, min(500, limit))
    q = (
        db.query(EmotionEvent)
        .filter(EmotionEvent.user_id == user_id)
        .order_by(EmotionEvent.created_at.desc())
        .limit(limit)
    )
    return [
        {
            "id": x.id,
            "source": x.source,
            "emotion": x.emotion,
            "score": x.score,
            "created_at": x.created_at,
        }
        for x in q.all()
    ]


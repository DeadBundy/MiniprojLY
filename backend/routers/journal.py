from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from models.tables import JournalEntry, EmotionEvent
from backend.schemas import JournalCreate, JournalOut
from utils.emotion import classify_text_emotion


router = APIRouter()


@router.post("", response_model=JournalOut)
def create_entry(payload: JournalCreate, db: Session = Depends(get_db)) -> JournalOut:
    emo = classify_text_emotion(payload.content)
    entry = JournalEntry(
        user_id=payload.user_id,
        content=payload.content,
        detected_emotion=emo.label,
        emotion_score=emo.score,
    )
    db.add(entry)
    db.flush()

    db.add(
        EmotionEvent(
            user_id=payload.user_id,
            source="text",
            emotion=emo.label,
            score=emo.score,
        )
    )
    db.commit()
    db.refresh(entry)
    return JournalOut.model_validate(entry, from_attributes=True)


@router.get("", response_model=list[JournalOut])
def list_entries(user_id: int, db: Session = Depends(get_db)) -> list[JournalOut]:
    q = (
        db.query(JournalEntry)
        .filter(JournalEntry.user_id == user_id)
        .order_by(JournalEntry.created_at.desc())
        .limit(200)
    )
    return [JournalOut.model_validate(x, from_attributes=True) for x in q.all()]


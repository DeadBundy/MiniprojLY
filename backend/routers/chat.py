from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from models.tables import ChatMessage, EmotionEvent
from backend.schemas import ChatSend, ChatMessageOut
from utils.safety import check_crisis, crisis_response_message, DISCLAIMER, CRISIS_RESOURCES_EXAMPLE
from utils.emotion import classify_text_emotion
from utils.llm import generate_supportive_reply


router = APIRouter()


@router.post("/send", response_model=dict)
def send_message(payload: ChatSend, db: Session = Depends(get_db)) -> dict:
    crisis = check_crisis(payload.message)
    emo = classify_text_emotion(payload.message)

    user_msg = ChatMessage(
        user_id=payload.user_id,
        role="user",
        content=payload.message,
        detected_emotion=emo.label,
        emotion_score=emo.score,
    )
    db.add(user_msg)
    db.flush()
    db.add(
        EmotionEvent(
            user_id=payload.user_id,
            source="text",
            emotion=emo.label,
            score=emo.score,
        )
    )

    if crisis.is_crisis:
        assistant_text = f"{crisis_response_message()}\n\n{DISCLAIMER}\n\nResources: {CRISIS_RESOURCES_EXAMPLE}"
    else:
        assistant_text = generate_supportive_reply(payload.message, detected_emotion=emo.label).content
        assistant_text = f"{assistant_text}\n\n{DISCLAIMER}"

    assistant_msg = ChatMessage(
        user_id=payload.user_id,
        role="assistant",
        content=assistant_text,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(user_msg)
    db.refresh(assistant_msg)

    return {
        "user": ChatMessageOut.model_validate(user_msg, from_attributes=True),
        "assistant": ChatMessageOut.model_validate(assistant_msg, from_attributes=True),
        "is_crisis": crisis.is_crisis,
    }


@router.get("/history", response_model=list[ChatMessageOut])
def history(user_id: int, db: Session = Depends(get_db)) -> list[ChatMessageOut]:
    q = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(500)
    )
    return [ChatMessageOut.model_validate(x, from_attributes=True) for x in q.all()]

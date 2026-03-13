from __future__ import annotations

from datetime import datetime, date
from pydantic import BaseModel, Field


class JournalCreate(BaseModel):
    user_id: int = Field(..., ge=1)
    content: str = Field(..., min_length=1)


class JournalOut(BaseModel):
    id: int
    user_id: int
    content: str
    created_at: datetime
    detected_emotion: str | None = None
    emotion_score: float | None = None


class ChatSend(BaseModel):
    user_id: int = Field(..., ge=1)
    message: str = Field(..., min_length=1)


class ChatMessageOut(BaseModel):
    id: int
    user_id: int
    role: str
    content: str
    created_at: datetime
    detected_emotion: str | None = None
    emotion_score: float | None = None


class EmotionEventCreate(BaseModel):
    user_id: int = Field(..., ge=1)
    source: str = Field(..., pattern="^(text|face)$")
    emotion: str = Field(..., min_length=1)
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    created_at: datetime | None = None


class DailySummaryOut(BaseModel):
    day: date
    summary: str
    wellness_score: int


class WeeklyReportOut(BaseModel):
    start_day: date
    end_day: date
    dominant_emotions: list[tuple[str, int]]
    journaling_days: int
    avg_wellness_score: float


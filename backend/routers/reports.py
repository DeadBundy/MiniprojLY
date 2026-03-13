from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from models.tables import EmotionEvent, JournalEntry, DailySummary
from backend.schemas import DailySummaryOut, WeeklyReportOut
from utils.summarize import summarize_day, wellness_score_for_day, week_range_ending


router = APIRouter()


@router.post("/daily", response_model=DailySummaryOut)
def generate_daily(user_id: int, day: date | None = None, db: Session = Depends(get_db)) -> DailySummaryOut:
    day = day or date.today()
    start_dt = datetime(day.year, day.month, day.day)
    end_dt = start_dt + timedelta(days=1)

    journal_count = (
        db.query(JournalEntry)
        .filter(JournalEntry.user_id == user_id)
        .filter(JournalEntry.created_at >= start_dt, JournalEntry.created_at < end_dt)
        .count()
    )

    events = (
        db.query(EmotionEvent)
        .filter(EmotionEvent.user_id == user_id)
        .filter(EmotionEvent.created_at >= start_dt, EmotionEvent.created_at < end_dt)
        .all()
    )

    text_emotions = [e.emotion for e in events if e.source == "text"]
    face_emotions = [e.emotion for e in events if e.source == "face"]
    all_emotions = [e.emotion for e in events]

    summary_text = summarize_day(day=day, emotions=all_emotions, journal_count=journal_count)
    score = wellness_score_for_day(text_emotions=text_emotions, face_emotions=face_emotions, journal_count=journal_count)

    existing = (
        db.query(DailySummary)
        .filter(DailySummary.user_id == user_id, DailySummary.day == day)
        .one_or_none()
    )
    if existing:
        existing.summary = summary_text
        existing.wellness_score = score
        db.commit()
    else:
        db.add(DailySummary(user_id=user_id, day=day, summary=summary_text, wellness_score=score))
        db.commit()

    return DailySummaryOut(day=day, summary=summary_text, wellness_score=score)


@router.get("/weekly", response_model=WeeklyReportOut)
def weekly_report(user_id: int, end_day: date | None = None, db: Session = Depends(get_db)) -> WeeklyReportOut:
    end_day = end_day or date.today()
    start_day, end_day = week_range_ending(end_day)

    start_dt = datetime(start_day.year, start_day.month, start_day.day)
    end_dt = datetime(end_day.year, end_day.month, end_day.day) + timedelta(days=1)

    events = (
        db.query(EmotionEvent)
        .filter(EmotionEvent.user_id == user_id)
        .filter(EmotionEvent.created_at >= start_dt, EmotionEvent.created_at < end_dt)
        .all()
    )
    dominant = Counter([e.emotion for e in events]).most_common(5)

    journaling_days = (
        db.query(JournalEntry.created_at)
        .filter(JournalEntry.user_id == user_id)
        .filter(JournalEntry.created_at >= start_dt, JournalEntry.created_at < end_dt)
        .all()
    )
    journaling_days = len({d[0].date() for d in journaling_days})

    summaries = (
        db.query(DailySummary)
        .filter(DailySummary.user_id == user_id)
        .filter(DailySummary.day >= start_day, DailySummary.day <= end_day)
        .all()
    )
    avg_score = (sum(s.wellness_score for s in summaries) / len(summaries)) if summaries else 0.0

    return WeeklyReportOut(
        start_day=start_day,
        end_day=end_day,
        dominant_emotions=dominant,
        journaling_days=journaling_days,
        avg_wellness_score=avg_score,
    )


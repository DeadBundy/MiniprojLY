from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta


def summarize_day(*, day: date, emotions: list[str], journal_count: int) -> str:
    """
    Starter summarizer based on stored emotions.
    Replace with an NLP summarization model later.
    """
    if not emotions and journal_count == 0:
        return f"On {day.isoformat()}, there were no entries. Consider a short check-in journal prompt."

    top = Counter(emotions).most_common(2)
    if not top:
        return f"On {day.isoformat()}, you journaled {journal_count} time(s)."

    dominant = top[0][0]
    secondary = top[1][0] if len(top) > 1 else None
    if secondary and secondary != dominant:
        return (
            f"On {day.isoformat()}, your dominant emotion was {dominant}, with some {secondary}. "
            f"You journaled {journal_count} time(s)."
        )
    return f"On {day.isoformat()}, your dominant emotion was {dominant}. You journaled {journal_count} time(s)."


def wellness_score_for_day(*, text_emotions: list[str], face_emotions: list[str], journal_count: int) -> int:
    """
    Simple 0-100 score for demo:
    - more journaling nudges upward
    - negative emotions nudge downward
    """
    score = 50
    score += min(20, journal_count * 5)

    negative_text = {"sadness", "anger", "fear"}
    negative_face = {"sad"}
    score -= sum(3 for e in text_emotions if e in negative_text)
    score -= sum(2 for e in face_emotions if e in negative_face)

    positive_text = {"joy"}
    positive_face = {"happy"}
    score += sum(2 for e in text_emotions if e in positive_text)
    score += sum(1 for e in face_emotions if e in positive_face)

    return int(max(0, min(100, score)))


def week_range_ending(day: date) -> tuple[date, date]:
    start = day - timedelta(days=6)
    return start, day


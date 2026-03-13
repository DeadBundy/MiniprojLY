from __future__ import annotations

import re
from dataclasses import dataclass


DISCLAIMER = (
    "Important: This system is for supportive journaling and reflection only. "
    "It is NOT a replacement for professional therapy and does NOT provide medical or psychological diagnosis."
)


CRISIS_RESOURCES_EXAMPLE = [
    {"name": "Local emergency number", "contact": "112 / 911 (depending on your country)"},
    {"name": "988 Suicide & Crisis Lifeline (US)", "contact": "Call or text 988"},
    {"name": "Samaritans (UK & ROI)", "contact": "Call 116 123"},
]


_CRISIS_PATTERNS = [
    r"\b(i want to die)\b",
    r"\b(i wanna die)\b",
    r"\b(kill myself)\b",
    r"\b(end my life)\b",
    r"\b(suicide)\b",
    r"\b(self harm)\b",
    r"\b(self-harm)\b",
]


@dataclass(frozen=True)
class CrisisCheckResult:
    is_crisis: bool
    matched: str | None


def check_crisis(text: str) -> CrisisCheckResult:
    t = (text or "").lower()
    for pat in _CRISIS_PATTERNS:
        m = re.search(pat, t)
        if m:
            return CrisisCheckResult(is_crisis=True, matched=m.group(0))
    return CrisisCheckResult(is_crisis=False, matched=None)


def crisis_response_message() -> str:
    return (
        "I'm really sorry you're feeling this way. You deserve support right now. "
        "If you are in immediate danger or might harm yourself, please call your local emergency number now. "
        "If you can, reach out to a trusted person nearby. "
        "You can also contact a crisis helpline (examples below)."
    )


def format_crisis_resources() -> str:
    """
    Render the example crisis resources as readable bullet points.
    """
    lines = ["Here are some example crisis resources:"]
    for r in CRISIS_RESOURCES_EXAMPLE:
        name = r.get("name", "").strip()
        contact = r.get("contact", "").strip()
        if not name and not contact:
            continue
        lines.append(f"- {name}: {contact}")
    return "\n".join(lines)



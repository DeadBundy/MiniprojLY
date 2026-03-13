from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMResponse:
    content: str


SYSTEM_GUARDRAILS = (
    "You are a supportive, empathetic mental wellness companion. "
    "You must NOT diagnose medical or psychological conditions. "
    "Encourage reflection, journaling, and healthy coping strategies. "
    "If the user expresses self-harm or suicide intent, respond with crisis support guidance and resources. "
    "Keep responses concise and kind."
)


def generate_supportive_reply(user_text: str, *, detected_emotion: str | None = None) -> LLMResponse:
    """
    Starter offline response generator.
    Swap this with an LLM API (OpenAI/Anthropic/etc.) by using LLM_API_KEY and LLM_MODEL env vars.
    """
    _ = os.getenv("LLM_API_KEY")  # reserved for later
    emotion_hint = f" (emotion: {detected_emotion})" if detected_emotion else ""

    # Simple reflective template
    reply = (
        f"Thank you for sharing{emotion_hint}. "
        "What part of this feels most intense for you right now? "
        "If you're open to it, try writing one sentence about what you need today."
    )
    return LLMResponse(content=reply)


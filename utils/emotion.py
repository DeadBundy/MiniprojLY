from __future__ import annotations

from dataclasses import dataclass


TEXT_EMOTIONS = ["joy", "sadness", "anger", "fear", "neutral"]
FACE_EMOTIONS = ["happy", "sad", "surprised", "neutral"]


@dataclass(frozen=True)
class EmotionResult:
    label: str
    score: float


def classify_text_emotion(text: str) -> EmotionResult:
    """
    Starter heuristic classifier.
    Replace with HuggingFace pipeline or hosted model later.
    """
    t = (text or "").lower()

    joy_words = ["happy", "joy", "excited", "grateful", "relieved", "good"]
    sadness_words = ["sad", "down", "depressed", "cry", "lonely", "hopeless"]
    anger_words = ["angry", "mad", "furious", "irritated", "annoyed"]
    fear_words = ["anxious", "scared", "afraid", "fear", "panic", "worried", "stress"]

    def hit(words: list[str]) -> int:
        return sum(1 for w in words if w in t)

    scores = {
        "joy": hit(joy_words),
        "sadness": hit(sadness_words),
        "anger": hit(anger_words),
        "fear": hit(fear_words),
        "neutral": 0,
    }

    best = max(scores.items(), key=lambda kv: kv[1])
    if best[1] == 0:
        return EmotionResult(label="neutral", score=0.5)
    # Normalize to (0.6..0.95) for demo
    score = min(0.95, 0.6 + 0.1 * best[1])
    return EmotionResult(label=best[0], score=score)


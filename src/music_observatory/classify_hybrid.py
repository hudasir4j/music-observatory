"""Classifier stack: supervised → prototype ML → rules."""

from pathlib import Path

from music_observatory.classify import classify_track
from music_observatory.classify_ml import MIN_SCORE, classify_track_ml

MODEL_PATH = Path("models/mood_logreg.joblib")
SUPERVISED_MIN_CONFIDENCE = 0.45


def classify_track_hybrid(
    name: str,
    duration_ms: int | None,
    artists: str = "",
) -> tuple[str, str, float]:
    """
    Returns (mood, source, score).

    source: "supervised" | "ml" | "rules"
    score: supervised confidence, or prototype similarity, or 0.0 for rules
    """
    # 1) Supervised path (if model file exists)
    if MODEL_PATH.exists():
        try:
            from music_observatory.classify_supervised import (
                classify_track_supervised,
            )

            mood, confidence = classify_track_supervised(name, artists)
            if confidence >= SUPERVISED_MIN_CONFIDENCE:
                return mood, "supervised", confidence
        except Exception:
            # Model corrupt / dependency issue → fall through
            pass

    # 2) Prototype embedding path
    ml_mood, score = classify_track_ml(name)
    if score >= MIN_SCORE and ml_mood != "unclassified":
        return ml_mood, "ml", score

    # 3) Rules fallback
    rules_mood = classify_track(name, duration_ms)
    return rules_mood, "rules", score
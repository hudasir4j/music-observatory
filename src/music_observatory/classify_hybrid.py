"""Hybrid mood classifier: embeddings first, rules fallback."""

from music_observatory.classify import classify_track
from music_observatory.classify_ml import MIN_SCORE, classify_track_ml


def classify_track_hybrid(name: str, duration_ms: int | None) -> tuple[str, str, float]:
    """
    Returns (mood, source, score).

    source is "ml" or "rules".
    score is the ML similarity (0.0 when rules win).
    """
    ml_mood, score = classify_track_ml(name)
    if score >= MIN_SCORE and ml_mood != "unclassified":
        return ml_mood, "ml", score

    rules_mood = classify_track(name, duration_ms)
    return rules_mood, "rules", score
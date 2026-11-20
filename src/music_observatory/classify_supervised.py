"""Predict mood with the trained LogisticRegression model."""

from pathlib import Path

import joblib
import numpy as np

from music_observatory.classify_ml import get_model

MODEL_PATH = Path("models/mood_logreg.joblib")


def classify_track_supervised(name: str, artists: str = "") -> tuple[str, float]:
    """
    Returns (mood, confidence).

    confidence = max predicted class probability.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Missing {MODEL_PATH}. Run: python -m music_observatory.train_mood_model"
        )

    bundle = joblib.load(MODEL_PATH)
    clf = bundle["classifier"]
    encoder = bundle["label_encoder"]

    text = f"{name} | {artists}".strip(" |")
    emb = get_model().encode([text])
    X = np.asarray(emb)

    proba = clf.predict_proba(X)[0]
    best_i = int(proba.argmax())
    mood = encoder.inverse_transform([best_i])[0]
    confidence = float(proba[best_i])
    return mood, confidence
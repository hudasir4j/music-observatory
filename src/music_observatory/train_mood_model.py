"""Train a supervised mood classifier from human labels."""

from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder

from music_observatory.classify_ml import get_model
from music_observatory.db import get_connection

MODEL_PATH = Path("models/mood_logreg.joblib")


def load_labeled_rows() -> list[tuple[str, str, str]]:
    """Return list of (spotify_id, text, mood_human)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT spotify_id, name, artists, mood_human
                FROM track_mood_labels
                ORDER BY labeled_at
                """
            )
            rows = cur.fetchall()

    out = []
    for spotify_id, name, artists, mood_human in rows:
        text = f"{name} | {artists}"
        out.append((spotify_id, text, mood_human))
    return out


def main() -> None:
    rows = load_labeled_rows()
    if len(rows) < 10:
        raise SystemExit(f"Need more labels (have {len(rows)}). Aim for 30+.")

    texts = [r[1] for r in rows]
    y_text = [r[2] for r in rows]

    print(f"Labeled tracks: {len(rows)}")
    print("Class counts:")
    for mood in sorted(set(y_text)):
        print(f"  {mood}: {y_text.count(mood)}")

    embedder = get_model()
    print("Embedding texts...")
    X = embedder.encode(texts)
    X = np.asarray(X)

    encoder = LabelEncoder()
    y = encoder.fit_transform(y_text)

    clf = LogisticRegression(max_iter=2000)

    # Cross-validation: train on some folds, test on held-out folds
    # With tiny/rare classes this can warn or fail — we'll handle that.
    try:
        scores = cross_val_score(clf, X, y, cv=min(5, len(rows) // 2))
        print(
            f"CV accuracy: {scores.mean():.3f} "
            f"(std {scores.std():.3f}) over {len(scores)} folds"
        )
        print(f"Per-fold: {[round(s, 3) for s in scores]}")
    except ValueError as exc:
        print(f"Cross-val skipped ({exc}). Training on all data anyway.")

    # Fit final model on ALL labeled data for use in the app
    clf.fit(X, y)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "classifier": clf,
            "label_encoder": encoder,
            "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        },
        MODEL_PATH,
    )
    print(f"Saved model → {MODEL_PATH}")
    print("Baseline to beat: hybrid ~28% on your labeled set.")


if __name__ == "__main__":
    main()
from pathlib import Path

from music_observatory.classify_hybrid import classify_track_hybrid


def test_hybrid_uses_ml_when_score_high(monkeypatch):
    monkeypatch.setattr(
        "music_observatory.classify_hybrid.MODEL_PATH",
        Path("/tmp/definitely-missing-mood-model.joblib"),
    )

    def fake_ml(name):
        return "hype", 0.8

    monkeypatch.setattr(
        "music_observatory.classify_hybrid.classify_track_ml",
        fake_ml,
    )
    mood, source, score = classify_track_hybrid("anything", 200_000)
    assert mood == "hype"
    assert source == "ml"
    assert score == 0.8


def test_hybrid_falls_back_to_rules_when_ml_weak(monkeypatch):
    monkeypatch.setattr(
        "music_observatory.classify_hybrid.MODEL_PATH",
        Path("/tmp/definitely-missing-mood-model.joblib"),
    )

    def fake_ml(name):
        return "unclassified", 0.1

    monkeypatch.setattr(
        "music_observatory.classify_hybrid.classify_track_ml",
        fake_ml,
    )
    mood, source, score = classify_track_hybrid("Heartbreak Hotel", 200_000)
    assert mood == "going_thru_it"
    assert source == "rules"


def test_hybrid_uses_supervised_when_confident(monkeypatch):
    monkeypatch.setattr(
        "music_observatory.classify_hybrid.MODEL_PATH",
        Path("models/mood_logreg.joblib"),
    )
    # Force exists() True even if path weird in CI
    monkeypatch.setattr(Path, "exists", lambda self: True)

    import music_observatory.classify_hybrid as hybrid_mod

    def fake_supervised(name, artists=""):
        return "in_love", 0.9

    monkeypatch.setattr(
        hybrid_mod,
        "classify_track_supervised",
        fake_supervised,
        raising=False,
    )
    # Because import is inside the function, patch the module function instead:
    monkeypatch.setattr(
        "music_observatory.classify_supervised.classify_track_supervised",
        fake_supervised,
    )

    mood, source, score = classify_track_hybrid("x", 200_000, "y")
    assert mood == "in_love"
    assert source == "supervised"
    assert score == 0.9
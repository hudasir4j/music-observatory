from music_observatory.classify_hybrid import classify_track_hybrid


def test_hybrid_uses_ml_when_score_high(monkeypatch):
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
    def fake_ml(name):
        return "unclassified", 0.1

    monkeypatch.setattr(
        "music_observatory.classify_hybrid.classify_track_ml",
        fake_ml,
    )
    mood, source, score = classify_track_hybrid("Heartbreak Hotel", 200_000)
    assert mood == "going_thru_it"
    assert source == "rules"
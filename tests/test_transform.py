"""Unit tests for Spotify dict → DB row transform."""

from music_observatory.ingest_search import transform_track


def test_transform_track_flattens_artists():
    track = {
        "id": "abc123",
        "name": "Partition",
        "artists": [{"name": "Beyoncé"}, {"name": "Guest"}],
        "album": {"name": "BEYONCÉ"},
        "duration_ms": 353613,
    }

    row = transform_track(track)

    assert row == (
        "abc123",
        "Partition",
        "Beyoncé, Guest",
        "BEYONCÉ",
        353613,
    )
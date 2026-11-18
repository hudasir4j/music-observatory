"""API smoke tests that do not need Postgres."""

from fastapi.testclient import TestClient

from music_observatory.api import app

client = TestClient(app)


def test_root_health():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
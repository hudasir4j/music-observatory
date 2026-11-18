from pathlib import Path
from fastapi.responses import FileResponse

from fastapi import FastAPI
from music_observatory.db import get_connection

from pydantic import BaseModel, Field
from music_observatory.apply_moods import apply_moods
from music_observatory.ingest_search import load_tracks, transform_track
from music_observatory.search_tracks import search_tracks


app = FastAPI(title = "Music Observatory", version="0.1.0")

@app.get("/")
def root():
    return {"message": "Music Observatory API is running"}

@app.get("/tracks")
def get_tracks():
    sql = """
        SELECT spotify_id, name, artists, album, duration_ms, mood, fetched_at
        FROM tracks
        ORDER BY fetched_at DESC;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    
    tracks = []
    for spotify_id, name, artists, album, duration_ms, mood, fetched_at in rows:
        tracks.append({
            "spotify_id": spotify_id,
            "name": name,
            "artists": artists,
            "album": album,
            "duration_ms": duration_ms,
            "mood": mood,
            "fetched_at": fetched_at.isoformat() if fetched_at else None,
        })

        return {"count": len(tracks), "tracks": tracks}

@app.get("/moods/summary")
def mood_summary():
    """Count tracks per mood label."""
    sql = """
        SELECT mood, COUNT(*) AS track_count
        FROM tracks
        GROUP BY mood
        ORDER BY track_count DESC;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    summary = [
        {"mood": mood if mood is not None else "unlabeled", "count": count}
        for mood, count in rows
    ]
    return {"summary": summary}


class IngestRequest(BaseModel):
    query: str = Field(min_length = 1, desciption = "Song search text")
    limit: int = Field(default = 5, ge = 1, le = 10, description = "Max search results")

@app.post("/ingest")
def ingest_tracks(body: IngestRequest):
    items = search_tracks(body.query, limit = body.limit)
    if not items:
        return {
            "query": body.query,
            "inserted_or seen": 0,
            "message": "No spotify tracks for the given query",
            "tracks": []
        }
    
    rows = [transform_track(t) for t in items]
    load_tracks(rows)
    apply_moods()

    placeholders = ",".join(["%s"] * len(rows))
    ids = [r[0] for r in rows]
    sql = f"""
        SELECT spotify_id, name, artists, mood, duration_ms
        FROM tracks
        WHERE spotify_id IN ({placeholders})
        ORDER BY name;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, ids)
            saved = cur.fetchall()
    tracks = [
        {
            "spotify_id": spotify_id,
            "name": name,
            "artists": artists,
            "mood": mood,
            "duration_ms": duration_ms,
        }
        for spotify_id, name, artists, mood, duration_ms in saved
    ]
    return {
        "query": body.query,
        "count": len(tracks),
        "tracks": tracks,
    }

STATIC_DIR = Path(__file__).parent / "static"

@app.get("/app")
def app_ui():
    return FileResponse(STATIC_DIR / "index.html")
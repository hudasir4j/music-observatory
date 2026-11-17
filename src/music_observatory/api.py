from fastapi import FastAPI
from music_observatory.db import get_connection

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


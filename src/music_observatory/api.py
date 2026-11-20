from pathlib import Path
from fastapi.responses import FileResponse

from fastapi import FastAPI
from music_observatory.db import get_connection

from pydantic import BaseModel, Field
from music_observatory.apply_moods import apply_moods
from music_observatory.ingest_search import load_tracks, transform_track
from music_observatory.search_tracks import search_tracks

import os
from collections import Counter

from fastapi import HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from music_observatory.classify_hybrid import classify_track_hybrid
from music_observatory.spotify_oauth import (
    build_login_url,
    exchange_code_for_token,
    fetch_top_tracks,
    new_state,
    fetch_me,
)

from music_observatory.labels import (
    VALID_MOODS,
    accuracy_report,
    fetch_labels_map,
    upsert_label,
)

from music_observatory.save_brief import save_brief, mood_headline


app = FastAPI(title = "Music Observatory", version="0.1.0")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "dev-insecure-secret"),
)

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


@app.get("/auth/login")
def auth_login(request: Request):
    state = new_state()
    request.session["oauth_state"] = state
    return RedirectResponse(build_login_url(state))


@app.get("/auth/callback")
def auth_callback(request: Request, code: str | None = None, state: str | None = None):
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code/state from Spotify")

    expected = request.session.get("oauth_state")
    if not expected or state != expected:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    token_data = exchange_code_for_token(code)
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access_token in Spotify response")

    request.session["spotify_access_token"] = access_token
    request.session.pop("oauth_state", None)

    return RedirectResponse("/brief", status_code=303)


@app.get("/auth/logout")
def auth_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/brief", status_code=303)


@app.get("/api/brief")
def api_brief(request: Request):
    access_token = request.session.get("spotify_access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not logged in")

    time_range = "short_term"
    me = fetch_me(access_token)
    spotify_user_id = me["id"]
    display_name = me.get("display_name")

    items = fetch_top_tracks(access_token, limit=20, time_range=time_range)

    tracks = []
    for t in items:
        name = t.get("name") or "(no name)"
        duration_ms = t.get("duration_ms")
        artists = ", ".join(a.get("name", "?") for a in t.get("artists", []))
        mood, source, score = classify_track_hybrid(name, duration_ms)
        tracks.append(
            {
                "spotify_id": t.get("id"),
                "name": name,
                "artists": artists,
                "duration_ms": duration_ms,
                "mood": mood,
                "source": source,
                "ml_score": round(score, 3),
            }
        )

    ids = [t["spotify_id"] for t in tracks if t.get("spotify_id")]
    human_map = fetch_labels_map(ids)  # import fetch_labels_map too
    for t in tracks:
        t["mood_human"] = human_map.get(t["spotify_id"])

    report = accuracy_report(tracks)

    brief_id = save_brief(
        spotify_user_id=spotify_user_id,
        display_name=display_name,
        time_range=time_range,
        tracks=tracks,
    )

    counts = Counter(t["mood"] for t in tracks)
    summary = [{"mood": mood, "count": count} for mood, count in counts.most_common()]

    return {
        "brief_id": brief_id,
        "user": {"spotify_user_id": spotify_user_id, "display_name": display_name},
        "time_range": time_range,
        "count": len(tracks),
        "summary": summary,
        "headline": mood_headline(summary, display_name),
        "tracks": tracks,
        "from_cache": False,
        "accuracy": report,
    }


@app.get("/brief")
def brief_page():
    return FileResponse(STATIC_DIR / "brief.html")


@app.get("/api/brief/latest")
def api_brief_latest(request: Request):
    access_token = request.session.get("spotify_access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not logged in")

    me = fetch_me(access_token)
    spotify_user_id = me["id"]
    display_name = me.get("display_name")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, time_range, created_at
                FROM briefs
                WHERE spotify_user_id = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (spotify_user_id,),
            )
            brief_row = cur.fetchone()
            if not brief_row:
                raise HTTPException(status_code=404, detail="No saved brief yet")

            brief_id, time_range, created_at = brief_row

            cur.execute(
                """
                SELECT spotify_id, name, artists, duration_ms, mood, source, ml_score
                FROM brief_tracks
                WHERE brief_id = %s
                ORDER BY name
                """,
                (brief_id,),
            )
            rows = cur.fetchall()

    tracks = [
        {
            "spotify_id": spotify_id,
            "name": name,
            "artists": artists,
            "duration_ms": duration_ms,
            "mood": mood,
            "source": source,
            "ml_score": ml_score,
        }
        for spotify_id, name, artists, duration_ms, mood, source, ml_score in rows
    ]

    ids = [t["spotify_id"] for t in tracks if t.get("spotify_id")]
    human_map = fetch_labels_map(ids)  # import fetch_labels_map too
    for t in tracks:
        t["mood_human"] = human_map.get(t["spotify_id"])

    report = accuracy_report(tracks)

    counts = Counter(t["mood"] for t in tracks if t["mood"])
    summary = [{"mood": m, "count": c} for m, c in counts.most_common()]

    return {
        "brief_id": brief_id,
        "created_at": created_at.isoformat() if created_at else None,
        "user": {"spotify_user_id": spotify_user_id, "display_name": display_name},
        "time_range": time_range,
        "count": len(tracks),
        "summary": summary,
        "headline": mood_headline(summary, display_name),
        "tracks": tracks,
        "from_cache": True,
        "accuracy": report,
    }
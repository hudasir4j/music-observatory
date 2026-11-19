"""Persist a classified listening brief to Postgres."""

from music_observatory.db import get_connection


def save_brief(
    spotify_user_id: str,
    display_name: str | None,
    time_range: str,
    tracks: list[dict],
) -> int:
    """
    Save user + brief + brief_tracks.

    `tracks` items should look like:
      {
        "spotify_id": ...,
        "name": ...,
        "artists": ...,
        "duration_ms": ...,
        "mood": ...,
        "source": ...,
        "ml_score": ...,
      }

    Returns the new brief id.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Upsert user: insert, or update name if they already exist
            cur.execute(
                """
                INSERT INTO users (spotify_user_id, display_name)
                VALUES (%s, %s)
                ON CONFLICT (spotify_user_id)
                DO UPDATE SET display_name = EXCLUDED.display_name
                """,
                (spotify_user_id, display_name),
            )

            cur.execute(
                """
                INSERT INTO briefs (spotify_user_id, time_range)
                VALUES (%s, %s)
                RETURNING id
                """,
                (spotify_user_id, time_range),
            )
            brief_id = cur.fetchone()[0]

            rows = [
                (
                    brief_id,
                    t["spotify_id"],
                    t["name"],
                    t["artists"],
                    t.get("duration_ms"),
                    t.get("mood"),
                    t.get("source"),
                    t.get("ml_score"),
                )
                for t in tracks
                if t.get("spotify_id")
            ]

            cur.executemany(
                """
                INSERT INTO brief_tracks (
                    brief_id, spotify_id, name, artists,
                    duration_ms, mood, source, ml_score
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (brief_id, spotify_id) DO NOTHING
                """,
                rows,
            )

        conn.commit()

    return brief_id

def mood_headline(summary: list[dict], display_name: str | None = None) -> str:
    """Build a one-line product headline from mood counts."""
    if not summary:
        who = display_name or "You"
        return f"{who}: no tracks in this brief yet."

    top = summary[0]
    mood = top["mood"]
    count = top["count"]
    total = sum(item["count"] for item in summary)
    pct = round(100 * count / total) if total else 0
    who = display_name or "You"

    pretty = {
        "going_thru_it": "going through it",
        "locked_in": "locked in",
        "hype": "hype",
        "chill": "chill",
        "unclassified": "unclassified",
    }.get(mood, mood)

    return f"{who}: you're mostly {pretty} right now ({pct}% of this brief)."
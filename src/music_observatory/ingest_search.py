from music_observatory.db import get_connection
from music_observatory.search_tracks import search_tracks

def transform_track(track: dict) -> tuple:
    spotify_id = track["id"]
    name = track.get("name") or "(no name)"
    artists = ", ".join(a.get("name", "?") for a in track.get('artists', []))
    album = (track.get("album") or {}).get("name")
    duration_ms = track.get("duration_ms")
    return (spotify_id, name, artists, album, duration_ms)


def load_tracks(row: list[tuple]) -> int:
    sql = """
        INSERT INTO tracks (spotify_id, name, artists, album, duration_ms)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (spotify_id) DO NOTHING
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, rows)
            inserted = cur.rowcount
        conn.commit()
    return inserted


if __name__ == "__main__":
    query = "Partition"
    items = search_tracks(query)

    if not items:
        raise SystemExit(f"No tracks found for {query!r}")

    rows = [transform_track(t) for t in items]
    load_tracks(rows)


    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT spotify_id, name, artists FROM tracks ORDER BY name;"
            )
            saved = cur.fetchall()

    print(f"Search returned {len(items)} track(s).")
    print(f"Database now has {len(saved)} track row(s):")

    for spotify_id, name, artists in saved:
        print(f"- {name} — {artists} — {spotify_id}")
from music_observatory.db import get_connection


def list_tracks():
    """Return all tracks as a list of tuples"""

    sql = """
        SELECT spotify_id, name, artists, album, duration_ms, fetched_at
        FROM tracks
        ORDER BY fetched_at DESC;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)       # send SELECT
            rows = cur.fetchall()  # get all result rows
    return rows


def list_tracks_longer_than(min_ms: int):
    """Testing filters, ex: duration_ms greater than min_ms"""

    sql = """
        SELECT name, artists, duration_ms
        FROM tracks
        WHERE duration_ms > %s
        ORDER BY duration_ms DESC;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (min_ms,))  # (min_ms,) is a one-item tuple
            rows = cur.fetchall()
    return rows


if __name__ == "__main__":
    print("=== All tracks ===")
    for row in list_tracks():
        spotify_id, name, artists, album, duration_ms, fetched_at = row
        print(f"- {name} | {artists} | {duration_ms} ms | {spotify_id}")

    print("\n=== Tracks longer than 3 minutes (180000 ms) ===")
    for name, artists, duration_ms in list_tracks_longer_than(180_000):
        minutes = duration_ms / 1000 / 60
        print(f"- {name} | {artists} | {minutes:.2f} min")
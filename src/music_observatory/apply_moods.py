from music_observatory.classify import classify_track
from music_observatory.db import get_connection

def apply_moods() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT spotify_id, name, duration_ms FROM tracks;")
            tracks = cur.fetchall()

            for spotify_id, name, duration_ms in tracks:
                mood = classify_track(name, duration_ms)
                cur.execute(
                    "UPDATE tracks SET mood = %s WHERE spotify_id = %s;",
                    (mood, spotify_id),
                )

        conn.commit()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT mood, COUNT(*)
                FROM tracks
                GROUP BY mood
                ORDER BY COUNT(*) DESC;
                """
            )

            counts = cur.fetchall()
            
            cur.execute("SELECT name, mood, duration_ms FROM tracks ORDER BY name;")
            rows = cur.fetchall()

    print("=== Mood Counts ===")
    for mood, count in counts:
        print(f"{mood}: {count}")
    
    print("\n=== Per Track ===")
    for name, mood, duration_ms in rows:
        print(f"- {name} -> {mood} ({duration_ms} ms)")
    

if __name__ == "__main__":
    apply_moods()
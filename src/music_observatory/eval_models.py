"""Compare hybrid vs supervised against human labels."""

from music_observatory.classify_hybrid import classify_track_hybrid
from music_observatory.classify_supervised import classify_track_supervised
from music_observatory.db import get_connection


def main() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT name, artists, mood_human FROM track_mood_labels"
            )
            rows = cur.fetchall()

    hybrid_ok = 0
    supervised_ok = 0
    n = len(rows)

    for name, artists, human in rows:
        h_mood, _, _ = classify_track_hybrid(name, None)
        s_mood, _ = classify_track_supervised(name, artists)
        hybrid_ok += h_mood == human
        supervised_ok += s_mood == human
        mark_h = "✓" if h_mood == human else "✗"
        mark_s = "✓" if s_mood == human else "✗"
        print(
            f"{mark_h}{mark_s} {name[:40]:40} "
            f"human={human:15} hybrid={h_mood:15} supervised={s_mood}"
        )

    print("\n=== Summary ===")
    print(f"Hybrid:      {hybrid_ok}/{n} = {hybrid_ok/n:.1%}")
    print(f"Supervised:  {supervised_ok}/{n} = {supervised_ok/n:.1%}")
    print(
        "Note: supervised was trained on these same labels, "
        "so this in-sample score is optimistic. Prefer the CV score from training."
    )


if __name__ == "__main__":
    main()
"""Human mood labels and accuracy helpers."""

from music_observatory.db import get_connection

VALID_MOODS = {
    "going_thru_it",
    "hype",
    "locked_in",
    "chill",
    "in_love",
    "unclassified",
}


def upsert_label(
    spotify_id: str,
    name: str,
    artists: str,
    mood_human: str,
) -> None:
    if mood_human not in VALID_MOODS:
        raise ValueError(f"Invalid mood_human: {mood_human}")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO track_mood_labels (spotify_id, name, artists, mood_human)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (spotify_id)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    artists = EXCLUDED.artists,
                    mood_human = EXCLUDED.mood_human,
                    labeled_at = NOW()
                """,
                (spotify_id, name, artists, mood_human),
            )
        conn.commit()


def fetch_labels_map(spotify_ids: list[str]) -> dict[str, str]:
    """Return {spotify_id: mood_human} for the ids we have labels for."""
    if not spotify_ids:
        return {}

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT spotify_id, mood_human
                FROM track_mood_labels
                WHERE spotify_id = ANY(%s)
                """,
                (spotify_ids,),
            )
            rows = cur.fetchall()
    return {spotify_id: mood for spotify_id, mood in rows}


def accuracy_report(predicted: list[dict]) -> dict:
    """
    predicted items need: spotify_id, mood (model prediction)

    Compares against track_mood_labels.
    """
    ids = [t["spotify_id"] for t in predicted if t.get("spotify_id")]
    human = fetch_labels_map(ids)

    compared = []
    for t in predicted:
        sid = t.get("spotify_id")
        if sid not in human:
            continue
        compared.append(
            {
                "spotify_id": sid,
                "name": t.get("name"),
                "predicted": t.get("mood"),
                "human": human[sid],
                "correct": t.get("mood") == human[sid],
            }
        )

    total = len(compared)
    correct = sum(1 for c in compared if c["correct"])
    return {
        "labeled": total,
        "correct": correct,
        "accuracy": (correct / total) if total else None,
        "examples": compared,
    }
def upsert_labels(labels: list[dict]) -> int:
    """
    Upsert many human labels.
    Each dict: spotify_id, name, artists, mood_human
    Returns how many were written.
    """
    if not labels:
        return 0

    for row in labels:
        if row["mood_human"] not in VALID_MOODS:
            raise ValueError(f"Invalid mood_human: {row['mood_human']}")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO track_mood_labels (spotify_id, name, artists, mood_human)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (spotify_id)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    artists = EXCLUDED.artists,
                    mood_human = EXCLUDED.mood_human,
                    labeled_at = NOW()
                """,
                [
                    (r["spotify_id"], r["name"], r["artists"], r["mood_human"])
                    for r in labels
                ],
            )
        conn.commit()
    return len(labels)
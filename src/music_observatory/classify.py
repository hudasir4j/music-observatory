GOING_THRU_IT_WORDS = {
    "cry", "hurt", "alone", "tears", "broken", "miss", "gone", "sad",
    "heartbreak", "pain", "lonely",
}
HYPE_WORDS = {
    "party", "dance", "jump", "fire", "lit", "boss", "run", "power",
    "energy", "hype",
}

def classify_track(name: str, duration_ms: int | None) -> str:
    text = (name or "").lower()

    if any(word in text for word in GOING_THRU_IT_WORDS):
        return "going_thru_it"
    if any(word in text for word in HYPE_WORDS):
        return "hype"

    if duration_ms is not None:
        if duration_ms < 180_000:
            return "locked_in"
        if duration_ms > 270_000:
            return "chill"
    
    return "unclassified"
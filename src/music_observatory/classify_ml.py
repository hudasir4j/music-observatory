""" embedding mood classifier (prototype similarity) """

from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


PROTOTYPES: dict[str, list[str]] = {
    "going_thru_it": [
        "heartbreak and crying alone",
        "feeling sad, hurt, and lonely",
        "missing someone and emotional pain",
    ],
    "hype": [
        "party dance energy and excitement",
        "hype anthem for the club",
        "confident powerful fire track",
    ],
    "locked_in": [
        "focused grind workout concentration",
        "locked in and determined",
        "intense focus music",
    ],
    "chill": [
        "calm relaxing late night vibes",
        "soft chill atmospheric mood",
        "peaceful unwind music",
    ],
}

MIN_SCORE = 0.25

@lru_cache(maxsize = 1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def classify_track_ml(name:str) -> tuple[str, float]:
    text = (name or "").strip()
    if not text:
        return "unclassified", 0.0

    model = get_model()
    prototype_labels: list[str] = []
    prototype_texts: list[str] = []
    for label, phrases in PROTOTYPES.items():
        for phrase in phrases:
            prototype_labels.append(label)
            prototype_texts.append(phrase)

    title_vec = model.encode([text])
    proto_vecs = model.encode(prototype_texts)

    sims = cosine_similarity(title_vec, proto_vecs)[0]
    best_index = int(sims.argmax())
    best_score = float(sims[best_index])
    best_label = prototype_labels[best_index]

    if best_score < MIN_SCORE:
        return "unclassified", best_score

    return best_label, best_score

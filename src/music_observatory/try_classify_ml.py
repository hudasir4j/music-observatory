from music_observatory.classify_ml import classify_track_ml

examples = [
    "Heartbreak Hotel",
    "Crazy in Love",
    "drivers license",
    "Party Anthem",
    "Partition",
    "Soft Late Night Rain",
]

for title in examples:
    mood, score = classify_track_ml(title)
    print(f"{title!r:30} → {mood:15} score={score:.3f}")
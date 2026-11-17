import requests
from music_observatory.search_tracks import search_tracks

query = "Partition"
items = search_tracks(query)

if not items:
        raise SystemExit(f"No tracks found for query: {query!r}")

print(f"Found {len(items)} result(s) for Partition:")
for i, track in enumerate(items, start=1):
    name = track.get("name", "(no name)")
    track_id = track.get("id", "(no id)")
    artists = [a.get("name", "?") for a in track.get("artists", [])]
    print(f"{i}. {name} — {artists} — id={track_id}")

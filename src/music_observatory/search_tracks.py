import requests
from music_observatory.spotify_auth import get_access_token


def search_tracks(query: str, limit: int = 5) -> list[dict]:
    access_token = get_access_token()

    search_response = requests.get(
        "https://api.spotify.com/v1/search",
        headers = {"Authorization": f"Bearer {access_token}"},
        params = {
            "q": query,
            "type": "track",
            "limit": 5,
        },
        timeout = 30
    )

    print("Search HTTP Status: ", search_response.status_code)
    search_response.raise_for_status()

    payload = search_response.json()
    return payload.get("tracks", {}).get("items", [])

if __name__ == "__main__":
    query = "Blinding Lights"
    items = search_tracks(query)

    if not items:
        raise SystemExit(f"No tracks found for query: {query!r}")

    print(f"Found {len(items)} result(s) for {query!r}:\n")
    for i, track in enumerate(items, start=1):
        name = track.get("name", "(no name)")
        track_id = track.get("id", "(no id)")
        artists = [a.get("name", "?") for a in track.get("artists", [])]
        print(f"{i}. {name} — {artists} — id={track_id}")
    
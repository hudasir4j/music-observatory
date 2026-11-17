import os
import requests
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

if not client_id or not client_secret:
    raise SystemExit (
        "Missing Spotify Client ID and/or Client Secret "
        "Copy .env.example to .env and fill in the right values."
        )


token_response = requests.post(
    "https://accounts.spotify.com/api/token",
    data={"grant_type": "client_credentials"},
    auth=(client_id, client_secret),
    timeout=30,
)

token_response.raise_for_status()
access_token = token_response.json()['access_token']

query = "Dancing on My Own"

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

items = payload.get("tracks", {}).get("items", [])

if not items:
    raise SystemExit(f"No tracks found for the query {query!r}:\n")

for i, track in enumerate(items, start = 1):
    name = track.get("name", "(no name)")
    track_id = track.get("id", "(no id)")
    artists = [a.get('name', '?') for a in track.get("artists", [])]
    album = track.get("album", {}).get("name", "no album name")

    print(f"{i}. {name}")
    print(f"   artists: {artists}")
    print(f"   album:   {album}")
    print(f"   id:      {track_id}")
    print()
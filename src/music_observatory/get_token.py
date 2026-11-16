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

token_url = "https://accounts.spotify.com/api/token"


response = requests.post(
    token_url,
    data = {"grant_type": "client_credentials"},
    auth = (client_id, client_secret),
    timeout = 30
)

print("HTTP status: ", response.status_code)
print("Response JSON keys: ", list(response.json().keys()))

token = response.json().get('access_token', '')
print("token recieved: ", bool(token))
print("token preview (first 8 chars): ", token[:8] + "..." if token else "NONE" )

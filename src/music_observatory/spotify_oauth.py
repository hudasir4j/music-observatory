"""Spotify Auth Code - user log in"""

import os
import secrets
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

load_dotenv()

AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
TOP_TRACKS_URL = "https://api.spotify.com/v1/me/top/tracks"

def _client_id() -> str:
    value = os.getenv("SPOTIFY_CLIENT_ID")
    if not value:
        raise SystemExit("Missing SPOTIFY_CLIENT_ID")
    return value

def _client_secret() -> str:
    value = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not value:
        raise SystemExit("Missing SPOTIFY_CLIENT_SECRET")
    return value

def _redirect_uri() -> str:
    value = os.getenv("SPOTIFY_REDIRECT_URI")
    if not value:
        raise SystemExit("Missing SPOTIFY_REDIRECT_URI")
    return value


def _scopes() -> str:
    return os.getenv("SPOTIFY_SCOPES", "user-top-read")

def new_state() -> str:
    return secrets.token_urlsafe(16)

def build_login_url(state:str)-> str:
    params = {
        "client_id": _client_id(),
        "response_type": "code",
        "redirect_uri": _redirect_uri(),
        "scope": _scopes(),
        "state": state,
    }
    return f"{AUTHORIZE_URL}?{urlencode(params)}"

def exchange_code_for_token(code: str) -> dict:
    response = requests.post(
        TOKEN_URL,
        data = {
            "grant_type": "authorization_code",
            "code" : code,
            "redirect_uri": _redirect_uri(),
        },
        auth = (_client_id(), _client_secret()),
        timeout = 30,
    )
    response.raise_for_status()
    return response.json()

def fetch_top_tracks(access_token: str, limit: int = 20, time_range: str = "short term") -> list[dict]:
    response = requests.get(
        TOP_TRACKS_URL,
        headers = {"Authorization": f"Bearer {access_token}"},
        params = {"limit": limit, "time_range": time_range},
        timeout = 30
    )
    response.raise_for_status()
    return response.json().get("items", [])


ME_URL = "https://api.spotify.com/v1/me"


def fetch_me(access_token: str) -> dict:
    response = requests.get(
        ME_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
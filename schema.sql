-- Music Observatory schema (v1)
-- Apply with: psql -d music_observatory -f schema.sql

CREATE TABLE IF NOT EXISTS tracks (
    spotify_id   TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    artists      TEXT NOT NULL,
    album        TEXT,
    duration_ms  INTEGER,
    fetched_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    mood         TEXT
);
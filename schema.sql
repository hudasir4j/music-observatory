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

CREATE TABLE IF NOT EXISTS users (
    spotify_user_id TEXT PRIMARY KEY,
    display_name    TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS briefs (
    id              BIGSERIAL PRIMARY KEY,
    spotify_user_id TEXT NOT NULL REFERENCES users(spotify_user_id),
    time_range      TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS brief_tracks (
    brief_id     BIGINT NOT NULL REFERENCES briefs(id) ON DELETE CASCADE,
    spotify_id   TEXT NOT NULL,
    name         TEXT NOT NULL,
    artists      TEXT NOT NULL,
    duration_ms  INTEGER,
    mood         TEXT,
    source       TEXT,
    ml_score     DOUBLE PRECISION,
    PRIMARY KEY (brief_id, spotify_id)
);
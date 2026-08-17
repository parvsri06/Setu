-- Setu — Central Database Schema (PostgreSQL + PostGIS)
-- Source of truth for field definitions: shared/record_schema.json
-- Run `CREATE EXTENSION IF NOT EXISTS postgis;` once per database before this file.

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS devices (
    device_id       TEXT PRIMARY KEY,
    first_seen_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_bridge_at  TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS records (
    id              TEXT PRIMARY KEY,                -- device_id:local_counter
    device_id       TEXT NOT NULL REFERENCES devices(device_id),
    local_counter   INTEGER NOT NULL,
    captured_at     TIMESTAMPTZ NOT NULL,
    location        GEOMETRY(Point, 4326) NOT NULL,  -- built from latitude/longitude on ingest
    survey_data     JSONB NOT NULL,                  -- flexible fields, see shared/record_schema.json
    received_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    record_hash     TEXT NOT NULL,
    UNIQUE (device_id, local_counter)                -- dedup safety net at the DB level
);

CREATE INDEX IF NOT EXISTS idx_records_location ON records USING GIST (location);
CREATE INDEX IF NOT EXISTS idx_records_captured_at ON records (captured_at);

-- Claims pipeline is being designed separately per team decision — not built yet.
-- Placeholder only, do not implement until that design is done:
-- CREATE TABLE claims ( ... );

-- Damage assessment (satellite image analysis) also scoped for later:
-- CREATE TABLE damage_assessments ( ... );

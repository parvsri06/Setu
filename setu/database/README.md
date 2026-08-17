# Setu Database

- `schema.sql` — Postgres + PostGIS DDL, the source of truth for the central DB
- `seed_dummy_data.sql` — a couple of dummy records for local testing, never used in the real demo
- `local_schema.md` — the equivalent SQLite/Room mapping for the Android side
- `migrations/` — after the first `schema.sql` apply, put changes here as numbered files

## Applying locally (once you're ready — not needed yet)
```
createdb setu
psql setu -f schema.sql
psql setu -f seed_dummy_data.sql   # optional
```

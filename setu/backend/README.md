# Setu Backend

FastAPI service. Structure only right now — nothing installed, several
functions are `TODO`/`NotImplementedError` stubs.

## Setup (once you're actually ready to run it — not needed yet)
1. `pip install -r requirements.txt`
2. Set the `DATABASE_URL` environment variable
3. Apply `../database/schema.sql` to your Postgres instance
4. `uvicorn app.main:app --reload`

## Layout
- `app/main.py` — entrypoint, wires up the routers
- `app/models.py` — Pydantic models (the API contract), matches `../shared/record_schema.json`
- `app/db_models.py` — SQLAlchemy models, matches `../database/schema.sql`
- `app/routers/records.py` — batch ingestion endpoint
- `app/routers/claims.py` — placeholder only, claims pipeline is a separate design effort
- `app/services/hash_chain.py`, `dedup.py` — core logic, currently stubbed

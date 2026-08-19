# Relief Registry — Backend

Cloud **sync hub** for the offline-first disaster registry. Responder phones sync signed
registration batches here when they reach an internet point; the backend dedupes, merges, and
exports a verified list for government compensation (DBT/PFMS).

**Stack:** Python 3.13 · FastAPI 0.141 · Uvicorn · SQLAlchemy 2.0 + Alembic · PostgreSQL (central)
· SQLite (local dev default) · PyJWT + cryptography

## Prerequisites

- **Python 3.11+** — this machine has 3.13. Nothing else to install system-wide (deps live in
  the project-local `.venv`).

## Setup (new machine)

```bash
cd backend
python -m venv .venv                        # create the virtual environment (once)
source .venv/Scripts/activate               # Windows Git Bash
# on Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt             # install all dependencies into .venv
```

Verify it works:

```bash
uvicorn app.main:app --reload               # start the dev server on :8000
curl http://127.0.0.1:8000/health           # → {"status": "ok", "service": "relief-registry-backend"}
curl http://127.0.0.1:8000/health/db        # → {"status": "ok", "database": "reachable", ...}
```

Interactive API docs (demo-ready): `http://127.0.0.1:8000/docs`

## PostgreSQL (production / when the DB teammate's schema is ready)

Without any env var, the backend runs on a local SQLite file (`./relief_registry.db`) — same code,
zero setup. To use PostgreSQL:

```bash
export DATABASE_URL="postgresql+psycopg://user:password@host:5432/relief_registry"
uvicorn app.main:app --reload
```

Migrations use Alembic: `alembic upgrade head` (see `docs/database-schema.md`).

## Useful commands

| Command | What it does |
|---|---|
| `pip install -r requirements.txt` | install deps into `.venv` |
| `uvicorn app.main:app --reload` | dev server on :8000 with auto-reload |
| `python -m pytest` | run the test suite |
| `python -m pytest tests/test_health.py -q` | run one test file |

(Activate the venv first, or call the interpreter directly: `.venv/Scripts/python -m pytest`)

## Project structure

```
backend/
├── .venv/                # virtual environment — the "toolchain" (never commit)
├── requirements.txt      # the dependency manifest (add a line → pip install -r)
├── .env.example          # template for DATABASE_URL / JWT_SECRET / DEV_API_KEY
├── .gitignore            # .venv/, __pycache__/, *.db, .env
├── app/
│   ├── config.py         # DATABASE_URL, JWT_SECRET, DEV_API_KEY … env vars, dev-safe defaults
│   ├── db.py             # SQLAlchemy engine + session + Base + init_db()
│   ├── models.py         # ORM models (mirror the teammate's Postgres schema)
│   ├── schemas.py        # pydantic request/response models + validation
│   ├── security.py       # JWT, dev-key gate, Aadhaar masking
│   ├── main.py           # FastAPI app + routers + health endpoints
│   └── routers/          # sync (upload/download), auth, export, admin
└── tests/                # conftest + test_health / test_sync / test_auth / test_admin
```

## Docs — what lives where

All docs live in **`docs/`** (README stays here by convention — this is the entry point):

| Doc | What's in it |
|---|---|
| **`docs/implementation.md`** | **The plan** — the phase-by-phase roadmap with "done when" checks |
| **`docs/design.md`** | Why it's built this way: scope, stack decisions, security, sync protocol, export, testing, deployment, open decisions, glossary |
| **`docs/database-schema.md`** | The database schema (DB teammate hand-off) |
| **`docs/api-contract.md`** | The API interface — the JSON shapes the app/BLE team codes against |
| **`docs/backend-lessons.md`** | The beginner's guide that grows with the code |

Repo root: workflow + security diagrams in `../Workflow diagram/` (`relief-registry-workflow*.png`,
`backend-security-design-*.png`).

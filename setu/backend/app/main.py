"""Relief Registry backend — FastAPI entry point.

Jobs: receive signed survey batches from responder devices, dedupe/merge into the
central registry, serve the merged registry back (delta download), and export a
verified CSV for government compensation (DBT/PFMS/SDRF).

Phases implemented: 1 (scaffold+health), 2 (models), 3 (upload), 4 (dedupe),
5 (download), 6 (auth), 7 (export), 8 (admin), 9 (tests). Production deploy is
phase 10 (needs VPS + real DATABASE_URL/JWT_SECRET/DEV_API_KEY + TLS).
"""
from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from . import models  # noqa: F401  (register models on Base.metadata)
from .config import DATABASE_URL
from .db import SessionLocal, init_db
from .routers import admin, auth, export, sync

app = FastAPI(
    title="Relief Registry Backend",
    description=(
        "Sync hub for the offline relief-camp registry. Receives records from "
        "responder devices, dedupes by (Aadhaar, flood date), and exports the "
        "verified list for government compensation."
    ),
    version="0.2.0",
)


@app.on_event("startup")
def _startup():
    init_db()

app.include_router(sync.router)
app.include_router(auth.router)
app.include_router(export.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    """Liveness check — is the service up?"""
    return {"status": "ok", "service": "relief-registry-backend"}


@app.get("/health/db")
def health_db():
    """Readiness check — is the database reachable and answering queries?"""
    try:
        with SessionLocal() as db:
            result = db.execute(text("SELECT 1")).scalar_one()
        return {"status": "ok", "database": "reachable", "result": result, "url": DATABASE_URL}
    except Exception as exc:  # pragma: no cover - error path
        raise HTTPException(status_code=500, detail=f"Database unreachable: {exc}")

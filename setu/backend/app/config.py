"""Central configuration for the Relief Registry backend.

Everything here comes from environment variables so the same code runs
locally (SQLite, zero setup) and in production (PostgreSQL / Neon).

Set DATABASE_URL to point at PostgreSQL:
    export DATABASE_URL="postgresql+psycopg://user:password@host:5432/Setu"
"""
from __future__ import annotations

import os

# Default: local SQLite file so the backend runs with zero setup on any machine.
# In production, set DATABASE_URL to your PostgreSQL connection string.
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite:///./relief_registry.db",
)

# Bind address/port for uvicorn
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))

# JWT signing secret (Design B). MUST be set to a long random value in production.
JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-only-secret-change-me")
JWT_ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "3600"))

# Dev/shared API key used to gate export + admin endpoints ("admins = us").
# Set this to a long random value in production.
DEV_API_KEY: str = os.getenv("DEV_API_KEY", "dev-only-api-key-change-me")

DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("1", "true", "yes", "on")

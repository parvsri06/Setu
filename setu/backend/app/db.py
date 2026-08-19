"""SQLAlchemy engine + session wiring.

Works with SQLite out of the box (the default in config.py) and switches to
PostgreSQL the moment DATABASE_URL is set. The schema itself lives in the
`schema` package / Alembic migrations (step 2 of the roadmap) — this module
only owns the connection.

SQLite needs check_same_thread=False for FastAPI's threadpool; PostgreSQL
doesn't accept that kwarg, so it's applied conditionally.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base class for all ORM models (used by the schema step)."""


def get_db():
    """FastAPI dependency that yields a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create tables if they don't exist.

    The teammate's PostgreSQL is the source of truth (already built). This only
    adds any missing tables — currently just ``export_logs`` — and is harmless
    on the existing schema. On SQLite dev it creates the whole schema.
    """
    # Import models so they register on Base.metadata before create_all.
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)

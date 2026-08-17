"""Setu backend — FastAPI entrypoint."""

from fastapi import FastAPI
from app.routers import records, claims

app = FastAPI(title="Setu Backend")

app.include_router(records.router)
app.include_router(claims.router)


@app.get("/health")
def health():
    return {"status": "ok"}

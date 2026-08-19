# Relief Registry — Backend Implementation Plan

> **This file is ONLY the plan + status.** The phase-by-phase roadmap with "done when" checks.
> Supporting docs:
> | Doc | What's in it |
> |---|---|
> | `README.md` | How to run: setup, structure, commands |
> | `design.md` | Why it's built this way: scope, stack, security, sync, export, decisions |
> | `database-schema.md` | The database schema (DB teammate hand-off) |
> | `api-contract.md` | The API interface the app codes against |
> | `backend-lessons.md` | The beginner's guide that grows with the code |

**Status legend:** ✅ implemented and verified · 🚧 planned · ⏸️ deferred

---

## 1. What's built so far

| Phase | Status | Proof |
|---|---|---|
| 1 Scaffold + health | ✅ | `GET /health`, `GET /health/db` → 200; `pytest` green |
| 2 Schema + models | ✅ | `app/models.py` mirrors `db/setu_postgresql.sql`; `init_db()` creates tables |
| 3 Upload endpoint | ✅ | `POST /api/v1/sync/upload` validates + upserts; tests green |
| 4 Dedupe + upsert | ✅ | `UNIQUE(user_id, damage_date)` → duplicate counted, not overwritten |
| 5 Download/delta | ✅ | `GET /api/v1/sync/download?since=` returns delta + `nextCursor` |
| 6 Auth (JWT + dev key) | ✅ | `POST /api/v1/auth/login`; `require_dev` gates export/admin (Design A dropped) |
| 7 Export | ✅ | `GET /api/v1/export/verified` CSV (masked Aadhaar) + `export_logs` row |
| 8 Admin endpoints | ✅ | `/admin/surveys`, `/stats`, `/audit`, `/sync-logs` (read-only, dev-gated) |
| 9 Test pass | ✅ | `pytest` green (health, sync, auth, export, admin) |
| 10 Deploy | 🚧 | needs VPS + real `DATABASE_URL`/`JWT_SECRET`/`DEV_API_KEY` + TLS |

---

## 2. The plan (phase by phase)

| # | Phase | Deliverable | Done when |
|---|---|---|---|
| 1 | ✅ Scaffold + health | FastAPI app, `/health` + `/health/db` | verified live |
| 2 | ✅ Schema + models | `app/models.py` matching the teammate's Postgres; `init_db()` | tables round-trip on SQLite |
| 3 | ✅ Upload | `POST /api/v1/sync/upload` with validation | valid → 200 accepted; malformed → 422 |
| 4 | ✅ Dedupe + upsert | `user_id`+`damage_date` unique; duplicate counted | 2 same → 1 accepted + 1 duplicate |
| 5 | ✅ Download/delta | `GET /api/v1/sync/download?since=` | full pull + delta pull work |
| 6 | ✅ Auth | JWT login + `require_dev` (X-Dev-Key / Bearer) | export without key → 403; with key → 200 |
| 7 | ✅ Export | `GET /api/v1/export/verified` CSV + audit | CSV downloads; Aadhaar masked; audit row |
| 8 | ✅ Admin | read-only dev-gated views | returns data; 403 without key |
| 9 | ✅ Test pass | unit + integration tests | `pytest` green |
| 10 | 🚧 Deploy | uvicorn/gunicorn on a VPS, env config, TLS | server boots under systemd; HTTPS reachable |

### Open decisions that still apply
| Status | Item | Affects |
|---|---|---|
| ✅ RESOLVED | Schema source = teammate's Postgres (`db/setu_postgresql.sql`) | phases 2–8 |
| ✅ RESOLVED | Raw Aadhaar stored (prototype risk) | export/contract |
| ✅ RESOLVED | Dedupe = `UNIQUE(user_id, damage_date)` | phase 4 |
| ✅ RESOLVED | Auth = JWT + dev key; Design A (Ed25519) dropped | phase 6 |
| ⏸️ OPEN | Export column set (SDRF per-household vs per-individual) | phase 7 |
| ⏸️ OPEN | Admin 2FA (stretch) | phase 6 |

### Testing rule
Every phase ships with a test that proves its "done when" check (see `tests/`).

# Relief Registry — Backend Design & Decisions

> The "why" and "how" of the backend: what it is, the locked stack, security, sync protocol,
> export, testing, deployment, open decisions, and glossary. The phase-by-phase plan is in
> `implementation.md`; the interface is `api-contract.md`; the schema is `database-schema.md`.
>
> Status legend: ✅ implemented and verified · 🚧 planned · ⏸️ deferred (blocked on a decision)

---

## 1. What the backend is (and is not)

**The backend is a cloud sync hub.** It is one small service with four jobs:

1. **Receive** signed batches of registrations from responder phones (they sync only when they
   reach an internet point).
2. **Dedupe + merge** by unique ID into the camp registry (last-write-wins on conflicts).
3. **Serve** the merged registry back to responder phones (`download` with delta updates) — this is
   the "Camp B" answer: data physically rides with responders, and any responder whose phone
   syncs gets the full merged registry.
4. **Export** a verified, deduplicated list (CSV) for the administration to hand to the existing
   government payment system (DBT / PFMS / SDRF). The backend does **not** pay anyone — it produces
   the trustworthy list.

**What the backend is NOT:**

- ❌ A web portal. There is no internet in the camps; citizens never touch the backend. Search is
  on-device in the Android app.
- ❌ A payment system. It only exports the verified list.
- ❌ An identity verification service. Aadhaar verification (QR scan) happens offline on the device.

**The trust property that drives every security decision:** the exported list decides who gets
government compensation. So the backend must make it possible to prove *who entered what, when,
and that nothing was altered afterward.*

---

## 2. Stack & technology decisions (locked)

| Concern | Choice | Version | Why |
|---|---|---|---|
| Language | **Python** | 3.13 (this machine) | The backend developer's strongest language — velocity matters more than framework symmetry at this scale |
| Framework | **FastAPI** | 0.141.1 | Automatic pydantic validation (this app's whole job is rejecting bad data), free OpenAPI docs at `/docs`, minimal |
| ASGI server | **Uvicorn** | 0.52.3 | `--reload` for dev, production-ready |
| Database (central) | **PostgreSQL** | via psycopg 3.3.4 | Owned by the DB teammate; the backend connects to it in production via `DATABASE_URL` |
| Database (dev default) | **SQLite** (file) | via SQLAlchemy 2.0.52 | Zero-setup local dev; one env var flips to Postgres |
| ORM | **SQLAlchemy 2.0** | 2.0.52 | Dialect-agnostic — dev SQLite, prod Postgres, same models |
| Migrations | **Alembic** | 1.19.1 | Versioned schema migrations — the hand-off mechanism with the DB teammate |
| Auth libs | PyJWT + cryptography | 2.13.0 / 50.0.0 | Design B (JWT) and Design A (Ed25519 signing) |
| Tests | pytest + httpx | 9.1.1 / 0.28.1 | Smoke tests + per-endpoint integration tests |

**Decision record — why these were chosen (and the honest alternatives):**

- **FastAPI over Ktor:** the backend's value is its *logic* (validation, dedupe, auth, export), not
  its framework. FastAPI gives automatic pydantic validation (malformed sync batches → clean 400s,
  zero code), free interactive docs at `/docs` (a demo asset + teammate onboarding), and the most
  mature Postgres tooling (SQLAlchemy + Alembic). The Ktor argument — sharing Kotlin models with the
  Android app — is structurally weak here: the app↔backend boundary is JSON over HTTPS, so there is
  no cross-boundary type safety to gain either way, and the record schema is trivial to keep in
  sync. A Ktor scaffold was built and removed on 2026-08-16 after this re-decision.
- **PostgreSQL (central) over SQLite:** the DB teammate owns PostgreSQL for the central registry — a
  reasonable call for a project that may outlive the hackathon. The backend connects to it via
  `DATABASE_URL`. SQLite stays as the *local dev default* so any teammate runs the server with zero
  setup; the ORM serves both from the same models.
- **Alembic over raw DDL:** versioned migrations are how a backend dev and a DB person collaborate
  cleanly — the DB teammate writes the migration, everyone runs it.

**Verified working together (2026-08-16):** Python 3.13 venv, FastAPI 0.141.1, Uvicorn 0.52.3,
SQLAlchemy 2.0.52, psycopg 3.3.4, Alembic 1.19.1, PyJWT 2.13.0, cryptography 50.0.0 —
`/health` and `/health/db` both verified live, `pytest` green.

---

## 3. API surface

> Full JSON shapes and error format live in **`api-contract.md`** — the app/BLE team codes
> against that file. This section summarizes the surface.

| Method | Path | Purpose | Auth | Status |
|---|---|---|---|---|
| GET | `/health` | liveness | none | ✅ |
| POST | `/api/v1/auth/login` | dev token (JWT) from shared DEV_API_KEY | DEV_API_KEY | ✅ |
| POST | `/api/v1/sync/upload` | push a batch of surveys | none (validated) | ✅ |
| GET | `/api/v1/sync/download?since=<cursor>` | pull delta of merged registry | none (Aadhaar masked) | ✅ |
| GET | `/api/v1/export/verified` | download verified list as CSV | dev key / JWT | ✅ |
| GET | `/api/v1/admin/surveys` · `/stats` | inspect registry | dev key / JWT | ✅ |
| GET | `/api/v1/admin/audit` · `/sync-logs` | audit + sync trail | dev key / JWT | ✅ |

> **Changed from the original plan:** there is no `register-device` / responder-device table, so
> **Design A (Ed25519 device signing) was dropped**. Auth is **JWT + a shared dev key** (Design B
> only). "Responders" in the admin surface are not modeled — admin endpoints are read-only and gated
> for the builders ("admins = us").

**Versioning:** all business endpoints under `/api/v1/`. Breaking changes bump the version.

**Sync semantics (the important part):**

- **Upload** = an envelope `{campId, responderId, deviceId, collectedAt, records[], signature}`.
  Server: verify signature → validate every record → dedupe by `uniqueId` → upsert (last-write-wins)
  → write a `sync_log` row → respond `{batchId, accepted, duplicates, rejected}`.
- **Download** = `?since=<cursor>` returns only records changed after the cursor, plus the next
  cursor. First sync (no cursor) returns everything. This is how Camp B's app converges without
  ever being "pushed" anything.
- **Conflict rule:** unique ID wins; newest `collectedAt` wins between two records with the same ID.
  No tombstones in the MVP (a record that's wrong is corrected in place and re-exported).

---

## 4. Authentication & security design

> **Revised (2026-08-18):** the teammate's schema has **no responders/device table**, so
> **Design A (Ed25519 device signing) was dropped**. The backend implements **Design B only**:
> a JWT issued from a shared `DEV_API_KEY` (`POST /api/v1/auth/login`), plus the raw `X-Dev-Key`
> header as a shortcut. Export and admin routes are gated by `require_dev` (JWT *or* `X-Dev-Key`).
> There is no user/role table — "admins = us" (the builders).

- **Design B (admin/dev console): central token.** The shared dev key exchanges for a short-lived
  JWT; protected routes check it. 2FA is a stretch goal (see §9).
- **Data protection:** TLS everywhere (deploy phase); **Aadhaar is masked in all outputs**
  (download + export) even though it is stored raw; every export writes an `export_logs` row.
- **API hardening:** input validation on every upload field via pydantic (malformed → 422, never
  reaches DB); secrets via environment variables (`JWT_SECRET`, `DEV_API_KEY`, `DATABASE_URL`).

Implemented: ✅ auth (Phase 6) as JWT + dev key; export/admin gated. The `/health` endpoints are
intentionally unauthenticated.

---

## 5. Sync protocol (how a sync actually flows)

```
Responder phone (offline camp)            Cloud backend
        │  collects records, signs batch
        │
        │  ── reaches internet point ──►  POST /api/v1/sync/upload
        │                                1. verify signature (Design A)
        │                                2. validate each record (schema + required fields)
        │                                3. dedupe by unique_id; upsert last-write-wins
        │                                4. append sync_log
        │  ◄── {batchId, accepted, duplicates, rejected} ──
        │
        │  GET /api/v1/sync/download?since=<cursor>
        │  ◄── {records changed since cursor, nextCursor} ──
        │
        ▼  app merges downloaded records into on-device registry
```

- The **BLE fan-out** (app distribution + collection) is entirely device-side and never touches
  the backend — the backend only sees HTTP(S) JSON.
- **Delta cursors** make repeated downloads cheap: a phone that syncs daily only pulls what changed.

---

## 6. Export (verified list)

- **Format:** CSV attachment (`Content-Disposition: attachment`), UTF-8 BOM.
- **Rows:** one row per **casualty** (survey-level columns repeated). Columns are **provisional**
  pending the SDRF/DBT form decision — see `api-contract.md` §2.
- **Semantics:** only `is_synced = true` surveys; deduplicated by construction
  (`UNIQUE(user_id, damage_date)`).
- **Privacy:** Aadhaar is **masked** (`XXXX-XXXX-1234`) in the output — the raw value is never
  emitted, even though it is stored raw.
- **Audit:** every export writes an `export_logs` row (who, when, how many rows). The original
  `audit_logs` only tracks survey-status changes, so `export_logs` was added.
- ⏸️ Deferred: exact column set (SDRF per-household vs per-individual) — confirm before finalizing.

---

## 7. Testing strategy

- **Unit:** dedupe logic, validation rules, signature verification — pure functions, no server.
- **Integration:** FastAPI `TestClient` per endpoint against a temporary SQLite file (see
  `tests/test_health.py` pattern). FastAPI's dependency injection makes swapping the DB trivial.
- **Manual:** curl/Postman against `uvicorn`; the interactive docs at `/docs` double as a manual
  test console; seed-data generator (`scripts/` in phase 9).
- **Golden rule:** every phase ships with a test that proves its "done when" check
  (`implementation.md` §2).

---

## 8. Deployment

- Host: any small VPS (1 GB RAM is plenty) or a free tier.
- Python: install Python 3.11+ on the VPS; create the venv; `pip install -r requirements.txt`.
- Run: `uvicorn app.main:app --host 0.0.0.0 --port 8000` under systemd (Restart=always), or
  gunicorn with multiple uvicorn workers if it ever needs them.
- Config via env: `DATABASE_URL` (PostgreSQL), `JWT_SECRET` (long random value), `PORT` — see
  `README.md`.
- TLS: Caddy or nginx reverse proxy (one-liner with Caddy).
- Migrations: `alembic upgrade head` on deploy (or in the systemd ExecStartPre).
- Backup: Postgres `pg_dump` on a cron — the DB teammate owns this.
- Scale-up path: none needed — the same code already runs against Postgres in production.

---

## 9. Open decisions & deferred items

| # | Decision | Impact | Needed by |
|---|---|---|---|
| 1 | ~~Unique ID scheme~~ **RESOLVED 2026-08-16** — Aadhaar is required by the Setu form; `unique_id` = salted SHA-256 of Aadhaar, computed on-device, opaque to the server | dedupe key (phase 4) + export (phase 7) | ✅ no longer blocking |
| 2 | **Export column set** (SDRF per-household vs per-individual) | phase 7 | before phase 7 |
| 3 | Server-side search endpoint or not (search is on-device) | API surface | before phase 8 |
| 4 | Admin 2FA (stretch) | phase 6 | hackathon-time permitting |
| 5 | Noise protocol (encrypt P2P channel, device-side) | backend unaffected; sync payloads already signed | out of backend scope |
| 6 | **Photos in the sync payload**: v1 = metadata only (`fileName`/`sizeBytes`/`mimeType`); actual bytes deferred (heavy for the offline channel) | contract + export | ✅ **confirmed 2026-08-16** (user decision: metadata only) |
| 7 | **Survey ID generation**: app-local at submit (`AFS-YYYY-######`); backend validates format + uniqueness | contract | default chosen; confirm with frontend |
| 8 | **District list** (Screen 2 dropdown): static in the app for the prototype; optional backend reference endpoint later | API surface | prototype default: static in app |
| 9 | **Consent flag**: not in the Setu mockup — dropped from the payload | contract | add back only if the form gains a consent checkbox |

### Resolved since the plan (2026-08-18)
- **Schema source of truth:** the teammate's Postgres DDL (`db/setu_postgresql.sql`) — backend
  models mirror it exactly. The earlier `uniqueId`/hash/`AFS-`/array ideas were dropped.
- **Raw Aadhaar stored** in `users.aadhaar_number` (prototype decision; flag for production review).
- **Dedupe** = `UNIQUE(user_id, damage_date)` (one Aadhaar per flood event), not last-write-wins.
- **Design A (Ed25519) dropped** — no device table; auth is JWT + shared dev key (Design B only).
- **survey_number** is server-generated (`SC-<YYYY>-<seq>`), not app-generated.

---

## 10. Glossary

- **Responder** — trained person who carries the app to camps, collects forms, syncs to the cloud.
- **Camp** — relief camp / booth; has an id and location.
- **Batch** — one signed upload envelope containing many records.
- **Store-and-forward** — collect offline, sync when connectivity exists. The core pattern.
- **Fan-out** — Bluetooth mesh that spreads the app/registry phone-to-phone (device-side only).
- **Unique ID** — the person's dedupe key (salted hash of Aadhaar).
- **DBT / PFMS / SDRF** — existing government payout rails (Direct Benefit Transfer, Public
  Financial Management System, State Disaster Response Fund). The backend feeds these with a list.

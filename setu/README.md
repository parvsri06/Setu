# Setu — Offline-First Disaster Survey & Bluetooth Mesh Sync

Offline-first Android app for disaster survey data collection. Captures
survey records with zero internet, syncs them across nearby phones over
Bluetooth (Nearby Connections API), and bridges to the backend once any
phone in the mesh reaches connectivity — designed to keep working through
weeks of a total network outage.

## Repo layout

| Folder | What's in it |
|---|---|
| `android-app/` | Kotlin + Compose app — capture UI, local Room DB, Bluetooth mesh sync layer |
| `backend/` | FastAPI service — batch ingestion, hash-chain, (future) claims pipeline |
| `database/` | Postgres/PostGIS schema, migrations, dummy seed data |
| `shared/record_schema.json` | **Canonical record schema.** Change a field here first, and tell the team — android-app and backend are both built against this file. |
| `docs/` | Architecture diagrams and the phased build plan |

## Status

This is a **structure-only skeleton** — no dependencies are installed, and
most files are stubs with `TODO`s. It exists so everyone can start from the
same layout and the same schema instead of merging four disconnected
starting points later.

## Start here

1. Read `docs/architecture.md` for the full system design.
2. Read `docs/build-plan.md` for the day-by-day phase plan and your specific tasks.
3. Read `shared/record_schema.json` before writing any code that touches a record — it's the contract every other piece depends on.

## Team

| Area | Folder |
|---|---|
| Bluetooth mesh sync | `android-app/app/src/main/java/com/setu/app/mesh/`, `sync/` |
| Frontend / UI | `android-app/app/src/main/java/com/setu/app/ui/` |
| Backend | `backend/` |
| Database | `database/` |

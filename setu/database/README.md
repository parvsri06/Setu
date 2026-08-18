# SETU Database

## Technology Stack

- SQLite (Mobile Database)
- FastAPI (Backend)
- PostgreSQL (Neon Cloud Database)

---

## Local Database

File:

setu.db

Schema:

setu_sqlite.sql

---

## Cloud Database

File:

setu_postgresql.sql

Database:

setu

---

## Synchronization Workflow

APK
↓

SQLite
↓

FastAPI
↓

PostgreSQL (Neon)

---

## Local Data Retention Policy

- Store data offline
- Synchronize immediately when the internet becomes available
- Keep synchronized records locally for 24 hours
- Delete records older than 24 hours

---

## Duplicate Prevention

Rule:

One Aadhaar + One Flood Event = One Submission

---

## Tables

- users
- surveys
- damage_images
- casualties
- relief_camps
- sync_logs
- audit_logs

---
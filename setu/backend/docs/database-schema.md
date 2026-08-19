# Relief Registry — Database Schema

> **Who owns this:** shared with the DB teammate. The backend implements it in `app/models.py`
> (SQLAlchemy models). The authoritative DDL is `db/setu_postgresql.sql` (Neon Postgres) and
> `db/setu_sqlite.sql` (on-device SQLite). This document summarizes it.
>
> **Status:** ✅ implemented in the backend. The backend models match this schema; an extra
> `export_logs` table was added for export auditing.

---

## Databases

- **Production:** PostgreSQL / Neon — the cloud central registry (`Setu` database).
- **Dev default:** SQLite file (`./relief_registry.db`) — zero setup; same models via the ORM.
- **On-device:** `db/setu.db` (SQLite) is the APK's offline store — the backend never touches it.

PKs are `UUID` (Postgres) / `UUID`-as-string (SQLite). The backend uses the dialect-agnostic
`Uuid` type so one model serves both.

---

## Tables

### `users` — every citizen recorded
| column | type | notes |
|---|---|---|
| user_id | UUID PK | default `gen_random_uuid()` |
| full_name | VARCHAR(100) | |
| father_name | VARCHAR(100) | |
| mobile_number | VARCHAR(10) | UNIQUE, `^[0-9]{10}$` |
| aadhaar_number | VARCHAR(12) | UNIQUE, `^[0-9]{12}$` — **stored raw** (prototype decision) |
| family_id | VARCHAR(20) | nullable |
| created_at | TIMESTAMP | default now |

### `surveys` — one per submission
| column | type | notes |
|---|---|---|
| survey_id | UUID PK | |
| survey_number | VARCHAR(20) UNIQUE | server-generated `SC-<YYYY>-<seq>` (trigger/sequence) |
| user_id | UUID FK → users | |
| village / district / post_office / police_station | VARCHAR(100) | |
| pin_code | VARCHAR(6) | `^[0-9]{6}$` |
| disaster_type | VARCHAR(50) | |
| other_disaster_type | VARCHAR(100) | nullable |
| damage_date | DATE | **part of dedupe key** |
| damage_area | TEXT | single string (not array) |
| other_damage_area | VARCHAR(100) | nullable |
| damage_description | TEXT | nullable |
| survey_status | VARCHAR(20) | `draft` / `offline` / `synced` |
| is_synced | BOOLEAN | |
| created_at / updated_at | TIMESTAMP | `updated_at` maintained by trigger |

**Dedupe constraint:** `UNIQUE(user_id, damage_date)` — one submission per Aadhaar per flood event.

### `damage_images` — image references only
| column | type | notes |
|---|---|---|
| image_id | UUID PK | |
| survey_id | UUID FK → surveys | |
| image_url | TEXT | path/URL string (bytes stay on device) |
| uploaded_at | TIMESTAMP | |

### `casualties` — affected people
| column | type | notes |
|---|---|---|
| casualty_id | UUID PK | |
| survey_id | UUID FK → surveys | |
| person_name | VARCHAR(100) | |
| age | INTEGER | 0–120 |
| gender | VARCHAR(20) | `Male` / `Female` / `Other` |
| status | VARCHAR(20) | `Alive` / `Missing` / `Not Alive` |
| current_location | TEXT | |

### `relief_camps`
| column | type | notes |
|---|---|---|
| camp_id | UUID PK | |
| survey_id | UUID FK → surveys | |
| staying_in_camp | BOOLEAN | |
| camp_name / camp_location | VARCHAR(100) | nullable |
| camp_address | TEXT | nullable |
| nearest_landmark | VARCHAR(200) | nullable |

### `sync_logs` — one row per survey sync
| column | type | notes |
|---|---|---|
| sync_id | UUID PK | |
| survey_id | UUID FK → surveys | |
| sync_status | VARCHAR(20) | `pending` / `synced` / `failed` |
| synced_at | TIMESTAMP | |

### `audit_logs` — survey status changes
| column | type | notes |
|---|---|---|
| log_id | UUID PK | |
| survey_id | UUID | nullable |
| old_status / new_status | VARCHAR(20) | |
| changed_at | TIMESTAMP | |

### `export_logs` — **added by backend** (export auditing)
| column | type | notes |
|---|---|---|
| export_id | UUID PK | |
| exported_by | VARCHAR(100) | dev key / token subject |
| row_count | INTEGER | |
| exported_at | TIMESTAMP | |
| note | TEXT | |

---

## Aadhaar note (legal)

The schema stores the **raw Aadhaar**. UIDAI guidance is to store only a masked value + a one-way
hash. Mark this for review before any production/government hand-off. The backend masks Aadhaar in
all *outputs* (download + export).

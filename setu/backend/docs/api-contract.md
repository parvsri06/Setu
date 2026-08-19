# Relief Registry — API Contract

> **Who this is for:** the Android app developer (sync client) and anyone building against the
> backend. Code against this file. If a shape here is wrong, change **this file first**, then
> both sides.
>
> Base URL: `http://<host>:8000` (dev: `http://127.0.0.1:8000`). All business endpoints are
> versioned: `/api/v1/...`. Requests and responses are JSON (`application/json`) unless noted.
>
> Status: ✅ implemented · 🚧 planned. **This contract now reflects the real database schema
> (`db/setu_postgresql.sql`), not the earlier draft — the earlier `uniqueId`/`AFS-`/array ideas
> were dropped.**

---

## 1. Record shape (the survey — single source of truth)

One submission = **one survey** for one user, with nested **casualties[]** (the affected people),
an optional **relief_camp**, and **images[]**. The user is identified by Aadhaar.

```json
{
  "user": {
    "full_name": "Shubh",
    "father_name": "Sample Father",
    "mobile_number": "9876543210",
    "aadhaar_number": "123456789012",
    "family_id": null
  },
  "village": "Sample Village",
  "district": "Barpeta",
  "post_office": "Sample PO",
  "police_station": "Sample PS",
  "pin_code": "781001",
  "disaster_type": "Flood",
  "other_disaster_type": null,
  "damage_date": "2026-08-15",
  "damage_area": "House",
  "other_damage_area": null,
  "damage_description": "House partially damaged",
  "casualties": [
    {
      "person_name": "Shubh",
      "age": 20,
      "gender": "Male",
      "status": "Alive",
      "current_location": "Sample Village"
    }
  ],
  "relief_camp": {
    "staying_in_camp": true,
    "camp_name": "ABC Relief Camp",
    "camp_location": "XYZ Village, Assam",
    "camp_address": null,
    "nearest_landmark": "Near School"
  },
  "images": [
    { "image_url": "img_001.jpg" }
  ]
}
```

### Fields

| field | type | notes |
|---|---|---|
| `user.full_name` | string (req) | |
| `user.father_name` | string (req) | |
| `user.mobile_number` | string **10 digits** (req) | validated; UNIQUE in DB |
| `user.aadhaar_number` | string **12 digits** (req) | validated; UNIQUE in DB; stored **raw** (see §5) |
| `user.family_id` | string \| null | optional |
| `village` `district` `post_office` `police_station` | string (req) | |
| `pin_code` | string **6 digits** (req) | |
| `disaster_type` | string (req) | e.g. `Flood` |
| `other_disaster_type` | string \| null | shown when disaster_type = "Other" |
| `damage_date` | string `YYYY-MM-DD` (req) | the flood event date — **part of the dedupe key** |
| `damage_area` | string (req) | **single string**, not an array |
| `other_damage_area` | string \| null | |
| `damage_description` | string \| null | |
| `casualties[]` | array | 0+ affected persons |
| `relief_camp` | object \| null | present when staying in a camp |
| `images[]` | array of `{image_url}` | path/URL string only (bytes stay on device) |

#### `casualties[]` (Screen 4 — Casualties)

| field | type | notes |
|---|---|---|
| `person_name` | string | |
| `age` | int `0..120` | |
| `gender` | `"Male"` \| `"Female"` \| `"Other"` | |
| `status` | `"Alive"` \| `"Missing"` \| `"Not Alive"` | |
| `current_location` | string | |

#### `relief_camp`

| field | type | notes |
|---|---|---|
| `staying_in_camp` | boolean | if false, rest may be null |
| `camp_name` / `camp_location` / `camp_address` / `nearest_landmark` | string \| null | |

---

## 2. Endpoints

### `GET /health` ✅ / `GET /health/db` ✅
Liveness / DB readiness.

### `POST /api/v1/sync/upload` ✅
Push a batch of surveys.

```json
// request
{
  "surveys": [ { /* §1 shape */ }, { /* §1 shape */ } ]
}
```

```json
// 200 response
{
  "batchId": "batch-0a1b2c3d",
  "accepted": 2,
  "duplicates": 0,
  "rejected": 0,
  "rejectedDetails": [
    { "survey_number": "SC-2026-000123", "outcome": "accepted" }
  ]
}
```

Rules:
- Each survey's `user` is upserted by `aadhaar_number`.
- **Dedupe:** a survey is a **duplicate** if the same user already has a survey for the same
  `damage_date` (`UNIQUE(user_id, damage_date)`). Duplicates are **counted, not overwritten**
  (no last-write-wins). The batch still succeeds for the rest.
- Malformed surveys (bad mobile/aadhaar/pin, invalid enum, age out of range) are rejected with a
  `422` validation error before touching the DB.
- `survey_number` (e.g. `SC-2026-000123`) is **server-generated** — do not send one.

### `GET /api/v1/sync/download?since=<cursor>` ✅
Pull the merged registry, delta-only.

```
GET /api/v1/sync/download?since=2026-08-15T10:30:00Z
```

```json
// 200 response
{
  "since": "2026-08-15T10:30:00Z",
  "surveys": [ { /* §1 shape, plus survey_id/survey_number/status/timestamps */ } ],
  "nextCursor": "2026-08-15T11:00:00Z"
}
```

Rules:
- Omit `since` → returns the **entire** registry + a cursor.
- Pass the previous `nextCursor` → returns only surveys whose `updated_at` is newer.
- Aadhaar in the download payload is **masked** (`XXXX-XXXX-1234`).

### `POST /api/v1/auth/login` ✅
Exchange the shared dev key for a JWT (optional convenience; export/admin also accept `X-Dev-Key` directly).

```json
// request
{ "api_key": "<DEV_API_KEY>" }
// 200
{ "token": "eyJ...", "expiresIn": 3600, "role": "admin" }
// 401 on wrong key
```

### `GET /api/v1/export/verified` ✅ (dev-gated)
Download the verified list as **CSV** (`Content-Disposition: attachment`, UTF-8 BOM).
Requires `Authorization: Bearer <token>` **or** header `X-Dev-Key: <DEV_API_KEY>`.

- Only `is_synced = true` surveys are exported.
- Aadhaar is **masked** (`XXXX-XXXX-1234`) in the output — the raw value is never emitted.
- Every export writes an `export_logs` row.
- Columns are **provisional** pending the final SDRF/DBT form decision (one row per casualty).

### `GET /api/v1/admin/surveys` · `/stats` · `/audit` · `/sync-logs` ✅ (dev-gated)
Read-only inspection for the builders ("admins = us"). All require the dev key/JWT.
There is **no device-revoke** endpoint — the schema has no responders/device table.

---

## 3. Errors

```json
{ "error": { "code": "invalid_batch", "message": "..." } }
```

| HTTP | code examples |
|---|---|
| 400 | `invalid_cursor` |
| 401 | `unauthorized` |
| 403 | `forbidden` |
| 422 | validation errors (pydantic) on upload fields |
| 500 | `internal_error` |

---

## 4. Conventions

- Timestamps: ISO-8601 UTC (`Z` suffix).
- IDs: UUIDs (Postgres) / UUID strings (SQLite).
- `survey_number` server-generated: `SC-<YYYY>-<seq>`.
- Auth: `Authorization: Bearer <token>` or `X-Dev-Key: <key>` on protected routes.
- Versioning: breaking changes → `/api/v2/`.

---

## 5. Aadhaar note

The current database stores the **raw 12-digit Aadhaar** (`users.aadhaar_number`). This is a
deliberate prototype decision (UIDAI best practice is to store only masked + a salted hash; flag
this before any production/government hand-off). Dedupe is by raw Aadhaar + `damage_date`.

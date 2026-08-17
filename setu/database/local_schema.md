# Local (Room / SQLite) Schema

SQLite has no PostGIS geometry type — store latitude/longitude as plain
REAL columns on-device. They only get combined into a PostGIS point once
the backend receives the record from a bridge phone.

| Field | SQLite type | Notes |
|---|---|---|
| id | TEXT PRIMARY KEY | `device_id:local_counter` |
| device_id | TEXT | |
| local_counter | INTEGER | |
| captured_at | TEXT | ISO 8601 string |
| latitude | REAL | |
| longitude | REAL | |
| survey_data | TEXT | JSON-encoded string |
| record_hash | TEXT | |

Matches the Room entity in
`android-app/app/src/main/java/com/setu/app/data/local/SurveyRecord.kt`.

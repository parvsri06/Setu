# SETU - Database Team Documentation

Version: 1.0

Prepared By: Database Team

Project: SETU - Disaster Survey Application

Domain: Flood Damage Assessment and Disaster Management

---

# Objective

The database team designed a hybrid database architecture consisting of:

1. SQLite (Local Mobile Database)

2. PostgreSQL (Central Cloud Database)

The application follows an offline-first approach.

Users can continue filling out surveys even without an internet connection.

When an internet connection becomes available, the application automatically synchronizes the locally stored data with the central PostgreSQL database.

---

# Database Architecture

```

                    Android APK

                          │

                          ▼

                 SQLite (Local Database)

                          │

              Offline Data Collection

                          │

                          ▼

                   FastAPI Backend

                          │

                          ▼

               PostgreSQL (Neon Database)

                          │

                          ▼

                   Admin Dashboard

```

---

# Database Team Responsibilities

The database team has completed the following:

- Database design

- Database normalization

- SQLite database implementation

- PostgreSQL database implementation

- Table creation

- Primary key implementation

- Foreign key implementation

- Check constraints

- Unique constraints

- Trigger implementation

- Index optimization

- Audit logging

- Duplicate submission prevention

- Database documentation

---

# Local Database (SQLite)

File:

```
setu.db
```

Schema:

```
setu_sqlite.sql
```

Purpose:

- Store survey data locally

- Allow offline submissions

- Store data when no internet connection is available

- Synchronize data automatically

- Delete synchronized data after 24 hours

---

# Central Database (PostgreSQL)

Database:

```
Setu
```

Cloud Provider:

```
Neon PostgreSQL
```

Schema:

```
setu_postgresql.sql
```

Purpose:

- Store all survey data permanently

- Aggregate data from all users

- Generate reports

- Support the admin dashboard

---

# SQLite Tables

## users

Purpose:

Stores personal information.

Columns:

- user_id

- full_name

- father_name

- mobile_number

- aadhaar_number

- family_id

- created_at

---

## surveys

Purpose:

Stores flood damage survey information.

Columns:

- survey_id

- survey_number

- user_id

- village

- district

- post_office

- police_station

- pin_code

- disaster_type

- other_disaster_type

- damage_date

- damage_area

- other_damage_area

- damage_description

- survey_status

- is_synced

- created_at

- updated_at

---

## damage_images

Purpose:

Stores image paths.

Columns:

- image_id

- survey_id

- image_path

- uploaded_at

---

## casualties

Purpose:

Stores casualty information.

Columns:

- casualty_id

- survey_id

- person_name

- age

- gender

- status

- current_location

---

## relief_camps

Purpose:

Stores relief camp information.

Columns:

- camp_id

- survey_id

- staying_in_camp

- camp_name

- camp_location

- camp_address

- nearest_landmark

---

## sync_logs

Purpose:

Tracks synchronization between SQLite and PostgreSQL.

Columns:

- sync_id

- survey_id

- sync_status

- synced_at

---

## audit_logs

Purpose:

Tracks survey status changes.

Columns:

- log_id

- survey_id

- old_status

- new_status

- changed_at

---

# PostgreSQL Tables

The PostgreSQL database contains the same table structure as SQLite.

Tables:

- users

- surveys

- damage_images

- casualties

- relief_camps

- sync_logs

- audit_logs

---

# Database Constraints

## Mobile Number Validation

Rules:

- Exactly 10 digits

- Must be unique

---

## Aadhaar Validation

Rules:

- Exactly 12 digits

- Must be unique

---

## PIN Code Validation

Rules:

- Exactly 6 digits

---

## Age Validation

Rules:

- Minimum = 0

- Maximum = 120

---

## Gender Validation

Allowed values:

- Male

- Female

- Other

---

## Casualty Status Validation

Allowed values:

- Alive

- Missing

- Not Alive

---

## Survey Status Validation

Allowed values:

- draft

- offline

- synced

---

# Duplicate Submission Prevention

Duplicate submissions are prevented at the database level.

Validation rules:

```
One User + One Damage Date = One Survey
```

The database automatically rejects duplicate submissions.

If a duplicate survey is detected, the backend should return:

```
This form is invalid.
It has already been submitted once.
```

---

# Trigger Implementation

## Trigger 1

Name:

```
trg_generate_survey_number
```

Purpose:

Automatically generates survey numbers.

Example:

```
SC-2026-000001

SC-2026-000002

SC-2026-000003
```

---

## Trigger 2

Name:

```
trg_update_modified_time
```

Purpose:

Automatically updates the `updated_at` column.

---

## Trigger 3

Name:

```
trg_audit_record
```

Purpose:

Tracks survey status changes.

---

# Synchronization Workflow

```

User fills out the form

        │

        ▼

Store data in SQLite

        │

        ▼

Internet available?

        │

    ┌───┴───┐

    │       │

   NO      YES

    │       │

    ▼       ▼

Wait    Send data to FastAPI

            │

            ▼

Store data in PostgreSQL

            │

            ▼

Update survey_status

            │

            ▼

survey_status = synced

            │

            ▼

Keep local data for 24 hours

            │

            ▼

Delete local records

```

---

# Image Storage Policy

Images are not stored directly inside the database.

SQLite stores:

```
/images/flood_image_001.jpg
```

PostgreSQL stores:

```
https://server/uploads/flood_image_001.jpg
```

Only image paths or image URLs are stored.

---

# Backend Team Responsibilities

The backend team must implement:

- FastAPI API endpoints

- SQLite database connection

- PostgreSQL database connection

- Synchronization logic

- Duplicate submission handling

- Automatic synchronization

- Automatic deletion after 24 hours

- API validation

- Error handling

---

# Database Files Provided

```
database/

├── setu.db

├── setu_sqlite.sql

├── setu_postgresql.sql

├── README.md

├── DATABASE_TEAM_GUIDE.md

└── .env.example

```

---

# Current Status

| Component | Status |
| ---------- | ------- |
| Database Design | Completed |
| SQLite Database | Completed |
| PostgreSQL Database | Completed |
| Constraints | Completed |
| Triggers | Completed |
| Documentation | Completed |
| FastAPI Integration | Pending |
| API Development | Pending |
| Synchronization | Pending |

---

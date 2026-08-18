# SETU - Database Workflow Documentation

Version: 1.0

Project: SETU - Disaster Survey Application

Prepared By: Database Team

---

# Database Workflow

The SETU application follows an **offline-first architecture**.

The application continues to collect survey data even when there is no internet connection.

All data is initially stored inside the mobile device using SQLite.

Once an internet connection becomes available, the FastAPI backend transfers the data to the central PostgreSQL database.

---

# Complete System Workflow

```

Citizen

   │

   ▼

Android APK

   │

   ▼

SQLite Database

(Offline Storage)

   │

   ▼

FastAPI Backend

(API Layer)

   │

   ▼

Neon PostgreSQL

(Central Database)

   │

   ▼

Admin Dashboard

```

---

# Survey Workflow

```

Personal Details

        │

        ▼

Location Details

        │

        ▼

Flood Damage Details

        │

        ▼

Casualty Information

        │

        ▼

Relief Camp Information

        │

        ▼

Review Form

        │

        ▼

Submit Survey

```

---

# Offline Workflow

```

User submits the survey

        │

        ▼

Store data inside SQLite

        │

        ▼

Internet available?

        │

   ┌────┴────┐

   │         │

  NO        YES

   │         │

   ▼         ▼

Keep      Synchronize

waiting   with FastAPI

             │

             ▼

      Send to PostgreSQL

             │

             ▼

      Update survey status

             │

             ▼

      survey_status=synced

             │

             ▼

      Keep local copy

         for 24 hours

             │

             ▼

      Delete local record

```

---

# Database Relationship Diagram

```

users

│

└──────────────┐

               │

               ▼

           surveys

               │

    ┌──────────┼──────────┐

    │          │          │

    ▼          ▼          ▼

damage_images  casualties  relief_camps

               │

               ▼

           sync_logs

               │

               ▼

           audit_logs

```

---

# Entity Relationship (ER) Diagram

```

users

----------------------------------

user_id (PK)

full_name

father_name

mobile_number

aadhaar_number

family_id

created_at

----------------------------------



surveys

----------------------------------

survey_id (PK)

survey_number

user_id (FK)

village

district

post_office

police_station

pin_code

disaster_type

other_disaster_type

damage_date

damage_area

other_damage_area

damage_description

survey_status

is_synced

created_at

updated_at

----------------------------------



damage_images

----------------------------------

image_id (PK)

survey_id (FK)

image_url

uploaded_at

----------------------------------



casualties

----------------------------------

casualty_id (PK)

survey_id (FK)

person_name

age

gender

status

current_location

----------------------------------



relief_camps

----------------------------------

camp_id (PK)

survey_id (FK)

staying_in_camp

camp_name

camp_location

camp_address

nearest_landmark

----------------------------------



sync_logs

----------------------------------

sync_id (PK)

survey_id (FK)

sync_status

synced_at

----------------------------------



audit_logs

----------------------------------

log_id (PK)

survey_id (FK)

old_status

new_status

changed_at

----------------------------------

```

---

# Database Constraints

## users

### Mobile Number

```
Exactly 10 digits

Must be unique
```

---

### Aadhaar Number

```
Exactly 12 digits

Must be unique
```

---

## surveys

### PIN Code

```
Exactly 6 digits
```

---

### Survey Status

Allowed values:

```
draft

offline

synced
```

---

## casualties

### Age

```
0-120
```

---

### Gender

Allowed values:

```
Male

Female

Other
```

---

### Casualty Status

Allowed values:

```
Alive

Missing

Not Alive
```

---

## sync_logs

Allowed values:

```
pending

synced

failed
```

---

# Duplicate Submission Workflow

```

New survey submitted

        │

        ▼

Check user_id

        │

        ▼

Check damage_date

        │

        ▼

Duplicate found?

        │

   ┌────┴────┐

   │         │

  YES        NO

   │         │

   ▼         ▼

Reject     Accept

survey      survey

```

---

# Database Triggers

## Trigger 1

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

```
trg_update_modified_time
```

Purpose:

Automatically updates the `updated_at` field.

---

## Trigger 3

```
trg_audit_record
```

Purpose:

Creates audit records whenever `survey_status` changes.

---

# Synchronization Requirements

The FastAPI backend must implement the following workflow.

---

## Upload unsynchronized surveys

SQL query:

```sql
SELECT *
FROM surveys
WHERE is_synced = FALSE;
```

---

## Mark a survey as synchronized

SQL query:

```sql
UPDATE surveys
SET
    survey_status='synced',
    is_synced=TRUE
WHERE survey_id=?;
```

---

## Delete local data after 24 hours

SQLite query:

```sql
DELETE
FROM surveys
WHERE
    is_synced=1
AND
    created_at <=
    datetime('now','-24 hours');
```

---

# Database Files

```

database/

├── setu.db

├── setu_sqlite.sql

├── setu_postgresql.sql

├── README.md

├── DATABASE_TEAM_GUIDE.md

├── DATABASE_WORKFLOW.md

└── Tech_Stack.md

```

---

# Database Team Deliverables

Completed:

- SQLite database

- PostgreSQL database

- Constraints

- Triggers

- Views

- Indexes

- Audit logging

- Duplicate prevention

- Documentation

# SETU - Technical Stack Documentation

---

# Project Overview

**Project Name:** SETU

**Domain:** Disaster Management

**Prototype Type:** Mobile-based Flood Damage Survey Application

**Primary Goal:**

To provide an offline-first disaster survey system that allows citizens to submit flood damage information through a mobile application and automatically synchronize the collected data with a central cloud database when an internet connection becomes available.

---

# System Architecture

```

Citizen

↓

Android Mobile Application (APK)

↓

Local SQLite Database

↓

FastAPI Backend

↓

Neon PostgreSQL Database

↓

Admin Dashboard

```

---

# Local Database Stack

| Component | Technology |
| --- | --- |
| Database | SQLite |
| Database File | setu.db |
| SQL Script | setu_sqlite.sql |
| Database Type | Embedded |
| Storage Type | Offline |
| Synchronization | Automatic |

---

# Cloud Database Stack

| Component | Technology |
| --- | --- |
| Database | PostgreSQL |
| Cloud Provider | Neon |
| Database Name | Setu |
| SQL Script | setu_postgresql.sql |
| Connection Type | SSL |
| Port | 5432 |

---

# Database Architecture

## SQLite (Mobile Database)

Purpose:

- Store data offline
- Continue collecting data without an internet connection
- Store images locally
- Hold synchronized records for 24 hours
- Delete synchronized records after 24 hours

### SQLite Tables

- users
- surveys
- damage_images
- casualties
- relief_camps
- sync_logs
- audit_logs

---

## PostgreSQL (Central Database)

Purpose:

- Store all survey data permanently
- Aggregate data from all users
- Generate reports
- Support the admin dashboard

### PostgreSQL Tables

- users
- surveys
- damage_images
- casualties
- relief_camps
- sync_logs
- audit_logs

---

# Data Synchronization Workflow

```

Internet Available?

│

├── YES

│ ↓

│ FastAPI sends data to PostgreSQL

│ ↓

│ survey_status = synced

│ ↓

│ Keep records for 24 hours

│ ↓

│ Delete local records

│

└── NO

↓

Store data in SQLite

↓

Wait for an internet connection

↓

Synchronize automatically

```

---

# Duplicate Submission Prevention

The application prevents duplicate survey submissions.

Validation Layers:

1. Unique Aadhaar Number

2. Unique Mobile Number

3. Unique Survey Constraint

4. PostgreSQL Constraints

5. FastAPI Validation

---

# Image Storage Strategy

Images are not stored directly inside the database.

SQLite:

```
/images/photo_001.jpg
```

PostgreSQL:

```
https://server.com/uploads/photo_001.jpg
```

Only image paths or image URLs are stored.

---

# Database Files

```

database/

├── setu.db

├── setu_sqlite.sql

└── setu_postgresql.sql

```

---

# Environment Variables

```

.env.example

```

Variables:

- DATABASE_URL
- POSTGRES_SERVER
- POSTGRES_PORT
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- SQLITE_DATABASE
- SYNC_INTERVAL_MINUTES
- LOCAL_RETENTION_HOURS

---

# Backend Dependencies

## Install FastAPI

```bash
pip install fastapi
```

## Install Uvicorn

```bash
pip install uvicorn
```

## Install SQLAlchemy

```bash
pip install sqlalchemy
```

## Install Psycopg

```bash
pip install psycopg[binary]
```

## Install Pydantic

```bash
pip install pydantic
```

## Install Environment Variable Support

```bash
pip install python-dotenv
```


---

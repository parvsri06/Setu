-- ============================================================
-- SETU SQLITE DATABASE
-- Offline Mobile Database for the SETU Disaster Survey App
-- ============================================================

-- ============================================================
-- ENABLE FOREIGN KEY SUPPORT
-- SQLite does not enable foreign keys automatically.
-- ============================================================

PRAGMA foreign_keys = ON;

-- ============================================================
-- TABLE 1: USERS
-- Purpose:
-- Stores personal information entered in the survey.
-- ============================================================

CREATE TABLE IF NOT EXISTS users
(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,

    full_name TEXT NOT NULL,

    father_name TEXT NOT NULL,

    mobile_number TEXT NOT NULL UNIQUE,

    aadhaar_number TEXT NOT NULL UNIQUE,

    family_id TEXT,

    created_at DATETIME DEFAULT (datetime('now', 'localtime')),

    CHECK(length(mobile_number) = 10),

    CHECK(length(aadhaar_number) = 12)
);

-- ============================================================
-- TABLE 2: SURVEYS
-- Purpose:
-- Stores location and flood damage information.
-- One user can create one survey for one disaster event.
-- ============================================================

CREATE TABLE IF NOT EXISTS surveys
(
    survey_id INTEGER PRIMARY KEY AUTOINCREMENT,

    survey_number TEXT UNIQUE,

    user_id INTEGER NOT NULL,

    village TEXT NOT NULL,

    district TEXT NOT NULL,

    post_office TEXT NOT NULL,

    police_station TEXT NOT NULL,

    pin_code TEXT NOT NULL,

    disaster_type TEXT NOT NULL,

    other_disaster_type TEXT,

    damage_date DATE NOT NULL,

    damage_area TEXT NOT NULL,

    other_damage_area TEXT,

    damage_description TEXT,

    survey_status TEXT DEFAULT 'offline',

    is_synced INTEGER DEFAULT 0,

    created_at DATETIME DEFAULT (datetime('now', 'localtime')),

    updated_at DATETIME DEFAULT (datetime('now', 'localtime')),

    FOREIGN KEY (user_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE,

    CHECK(length(pin_code) = 6),

    CHECK
    (
        survey_status IN
        (
            'draft',
            'offline',
            'synced'
        )
    ),

    -- Prevent duplicate submissions

    UNIQUE(user_id, damage_date)
);

-- ============================================================
-- TABLE 3: DAMAGE IMAGES
-- Purpose:
-- Stores image paths only.
-- Actual image files remain in device storage.
-- ============================================================

CREATE TABLE IF NOT EXISTS damage_images
(
    image_id INTEGER PRIMARY KEY AUTOINCREMENT,

    survey_id INTEGER NOT NULL,

    image_path TEXT NOT NULL,

    uploaded_at DATETIME DEFAULT (datetime('now', 'localtime')),

    FOREIGN KEY (survey_id)
    REFERENCES surveys(survey_id)
    ON DELETE CASCADE
);

-- ============================================================
-- TABLE 4: CASUALTIES
-- Purpose:
-- Stores multiple affected people in a single survey.
-- ============================================================

CREATE TABLE IF NOT EXISTS casualties
(
    casualty_id INTEGER PRIMARY KEY AUTOINCREMENT,

    survey_id INTEGER NOT NULL,

    person_name TEXT NOT NULL,

    age INTEGER NOT NULL,

    gender TEXT NOT NULL,

    status TEXT NOT NULL,

    current_location TEXT NOT NULL,

    FOREIGN KEY (survey_id)
    REFERENCES surveys(survey_id)
    ON DELETE CASCADE,

    CHECK(age >= 0 AND age <= 120),

    CHECK
    (
        gender IN
        (
            'Male',
            'Female',
            'Other'
        )
    ),

    CHECK
    (
        status IN
        (
            'Alive',
            'Missing',
            'Not Alive'
        )
    )
);

-- ============================================================
-- TABLE 5: RELIEF CAMPS
-- Purpose:
-- Stores relief camp information.
-- ============================================================

CREATE TABLE IF NOT EXISTS relief_camps
(
    camp_id INTEGER PRIMARY KEY AUTOINCREMENT,

    survey_id INTEGER NOT NULL,

    staying_in_camp INTEGER DEFAULT 0,

    camp_name TEXT,

    camp_location TEXT,

    camp_address TEXT,

    nearest_landmark TEXT,

    FOREIGN KEY (survey_id)
    REFERENCES surveys(survey_id)
    ON DELETE CASCADE
);

-- ============================================================
-- TABLE 6: SYNC LOGS
-- Purpose:
-- Tracks synchronization between SQLite and PostgreSQL.
-- ============================================================

CREATE TABLE IF NOT EXISTS sync_logs
(
    sync_id INTEGER PRIMARY KEY AUTOINCREMENT,

    survey_id INTEGER NOT NULL,

    sync_status TEXT DEFAULT 'pending',

    synced_at DATETIME DEFAULT (datetime('now', 'localtime')),

    FOREIGN KEY (survey_id)
    REFERENCES surveys(survey_id)
    ON DELETE CASCADE,

    CHECK
    (
        sync_status IN
        (
            'pending',
            'synced',
            'failed'
        )
    )
);

-- ============================================================
-- TABLE 7: AUDIT LOGS
-- Purpose:
-- Tracks status changes.
-- ============================================================

CREATE TABLE IF NOT EXISTS audit_logs
(
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,

    survey_id INTEGER,

    old_status TEXT,

    new_status TEXT,

    changed_at DATETIME DEFAULT (datetime('now', 'localtime'))
);

-- ============================================================
-- TRIGGER 1: AUTO-GENERATE SURVEY NUMBER
-- Example:
-- SC-2026-000001
-- SC-2026-000002
-- ============================================================

CREATE TRIGGER IF NOT EXISTS generate_survey_number

AFTER INSERT

ON surveys

FOR EACH ROW

BEGIN

    UPDATE surveys

    SET survey_number =
    (
        'SC-'
        || strftime('%Y', 'now')
        || '-'
        || printf('%06d', NEW.survey_id)
    )

    WHERE survey_id = NEW.survey_id;

END;

-- ============================================================
-- TRIGGER 2: AUTO-UPDATE MODIFICATION TIMESTAMP
-- ============================================================

CREATE TRIGGER IF NOT EXISTS update_modified_time

AFTER UPDATE

ON surveys

FOR EACH ROW

BEGIN

    UPDATE surveys

    SET updated_at =
    datetime('now', 'localtime')

    WHERE survey_id = NEW.survey_id;

END;

-- ============================================================
-- TRIGGER 3: CREATE AUDIT RECORD
-- ============================================================

CREATE TRIGGER IF NOT EXISTS create_audit_record

AFTER UPDATE OF survey_status

ON surveys

FOR EACH ROW

BEGIN

    INSERT INTO audit_logs
    (
        survey_id,
        old_status,
        new_status
    )

    VALUES
    (
        NEW.survey_id,
        OLD.survey_status,
        NEW.survey_status
    );

END;

-- ============================================================
-- VIEW: ADMIN DASHBOARD
-- Purpose:
-- Displays survey information in a single view.
-- ============================================================

CREATE VIEW IF NOT EXISTS survey_dashboard

AS

SELECT

    s.survey_number,

    u.full_name,

    u.mobile_number,

    s.village,

    s.district,

    s.disaster_type,

    s.damage_date,

    s.survey_status,

    s.created_at

FROM surveys s

JOIN users u

ON s.user_id = u.user_id;

-- ============================================================
-- DELETE SYNCHRONIZED RECORDS OLDER THAN 24 HOURS
-- Run this query periodically from the FastAPI backend.
-- ============================================================

DELETE FROM damage_images

WHERE survey_id IN
(
    SELECT survey_id

    FROM surveys

    WHERE is_synced = 1

    AND created_at <=
    datetime('now', '-24 hours', 'localtime')
);

DELETE FROM casualties

WHERE survey_id IN
(
    SELECT survey_id

    FROM surveys

    WHERE is_synced = 1

    AND created_at <=
    datetime('now', '-24 hours', 'localtime')
);

DELETE FROM relief_camps

WHERE survey_id IN
(
    SELECT survey_id

    FROM surveys

    WHERE is_synced = 1

    AND created_at <=
    datetime('now', '-24 hours', 'localtime')
);

DELETE FROM surveys

WHERE is_synced = 1

AND created_at <=
datetime('now', '-24 hours', 'localtime');

-- ============================================================
-- TEST DATA
-- Uncomment these queries if you want to test the database.
-- ============================================================

/*

INSERT INTO users
(
    full_name,
    father_name,
    mobile_number,
    aadhaar_number
)

VALUES
(
    'Akarsh Kumar',
    'Test User',
    '9876543210',
    '123456789012'
);

INSERT INTO surveys
(
    user_id,
    village,
    district,
    post_office,
    police_station,
    pin_code,
    disaster_type,
    damage_date,
    damage_area
)

VALUES
(
    1,
    'Village A',
    'District A',
    'Post Office A',
    'Police Station A',
    '800001',
    'Flood',
    '2026-08-17',
    'House'
);

*/

-- ============================================================
-- VERIFY TABLES
-- ============================================================

/*

SELECT * FROM users;

SELECT * FROM surveys;

SELECT * FROM damage_images;

SELECT * FROM casualties;

SELECT * FROM relief_camps;

SELECT * FROM sync_logs;

SELECT * FROM audit_logs;

SELECT * FROM survey_dashboard;

*/
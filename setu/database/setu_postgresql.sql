-- ============================================================
-- SETU POSTGRESQL DATABASE
-- Central Cloud Database for the SETU Disaster Survey App
-- Backend: FastAPI
-- Database: Neon PostgreSQL
-- ============================================================



-- ============================================================
-- ENABLE REQUIRED EXTENSION
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;



-- ============================================================
-- TABLE 1: USERS
-- Purpose:
-- Stores citizen information collected through the APK.
-- ============================================================

CREATE TABLE IF NOT EXISTS users
(
    user_id UUID PRIMARY KEY
    DEFAULT gen_random_uuid(),

    full_name VARCHAR(100) NOT NULL,

    father_name VARCHAR(100) NOT NULL,

    mobile_number VARCHAR(10) NOT NULL,

    aadhaar_number VARCHAR(12) NOT NULL,

    family_id VARCHAR(20),

    created_at TIMESTAMP
    DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_mobile
    UNIQUE (mobile_number),

    CONSTRAINT uq_aadhaar
    UNIQUE (aadhaar_number),

    CONSTRAINT chk_mobile
    CHECK (mobile_number ~ '^[0-9]{10}$'),

    CONSTRAINT chk_aadhaar
    CHECK (aadhaar_number ~ '^[0-9]{12}$')
);



-- ============================================================
-- TABLE 2: SURVEYS
-- Purpose:
-- Stores flood survey information.
-- ============================================================

CREATE TABLE IF NOT EXISTS surveys
(
    survey_id UUID PRIMARY KEY
    DEFAULT gen_random_uuid(),

    survey_number VARCHAR(20) UNIQUE,

    user_id UUID NOT NULL,

    village VARCHAR(100) NOT NULL,

    district VARCHAR(100) NOT NULL,

    post_office VARCHAR(100) NOT NULL,

    police_station VARCHAR(100) NOT NULL,

    pin_code VARCHAR(6) NOT NULL,

    disaster_type VARCHAR(50) NOT NULL,

    other_disaster_type VARCHAR(100),

    damage_date DATE NOT NULL,

    damage_area TEXT NOT NULL,

    other_damage_area VARCHAR(100),

    damage_description TEXT,

    survey_status VARCHAR(20)
    DEFAULT 'offline',

    is_synced BOOLEAN
    DEFAULT FALSE,

    created_at TIMESTAMP
    DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP
    DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user
    FOREIGN KEY (user_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE,

    CONSTRAINT chk_pin_code
    CHECK (pin_code ~ '^[0-9]{6}$'),

    CONSTRAINT chk_survey_status
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

    CONSTRAINT uq_duplicate_submission

    UNIQUE
    (
        user_id,
        damage_date
    )
);



-- ============================================================
-- TABLE 3: DAMAGE IMAGES
-- Purpose:
-- Stores image URLs.
-- ============================================================

CREATE TABLE IF NOT EXISTS damage_images
(
    image_id UUID PRIMARY KEY
    DEFAULT gen_random_uuid(),

    survey_id UUID NOT NULL,

    image_url TEXT NOT NULL,

    uploaded_at TIMESTAMP
    DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_damage_image

    FOREIGN KEY (survey_id)

    REFERENCES surveys(survey_id)

    ON DELETE CASCADE
);



-- ============================================================
-- TABLE 4: CASUALTIES
-- Purpose:
-- Stores information about affected people.
-- ============================================================

CREATE TABLE IF NOT EXISTS casualties
(
    casualty_id UUID PRIMARY KEY
    DEFAULT gen_random_uuid(),

    survey_id UUID NOT NULL,

    person_name VARCHAR(100) NOT NULL,

    age INTEGER NOT NULL,

    gender VARCHAR(20) NOT NULL,

    status VARCHAR(20) NOT NULL,

    current_location TEXT NOT NULL,

    CONSTRAINT fk_casualty

    FOREIGN KEY (survey_id)

    REFERENCES surveys(survey_id)

    ON DELETE CASCADE,

    CONSTRAINT chk_age

    CHECK (age BETWEEN 0 AND 120),

    CONSTRAINT chk_gender

    CHECK
    (
        gender IN
        (
            'Male',
            'Female',
            'Other'
        )
    ),

    CONSTRAINT chk_person_status

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
    camp_id UUID PRIMARY KEY
    DEFAULT gen_random_uuid(),

    survey_id UUID NOT NULL,

    staying_in_camp BOOLEAN
    DEFAULT FALSE,

    camp_name VARCHAR(100),

    camp_location VARCHAR(100),

    camp_address TEXT,

    nearest_landmark TEXT,

    CONSTRAINT fk_relief_camp

    FOREIGN KEY (survey_id)

    REFERENCES surveys(survey_id)

    ON DELETE CASCADE
);



-- ============================================================
-- TABLE 6: SYNC LOGS
-- Purpose:
-- Tracks synchronization from SQLite to PostgreSQL.
-- ============================================================

CREATE TABLE IF NOT EXISTS sync_logs
(
    sync_id UUID PRIMARY KEY
    DEFAULT gen_random_uuid(),

    survey_id UUID NOT NULL,

    sync_status VARCHAR(20)
    DEFAULT 'pending',

    synced_at TIMESTAMP
    DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_sync

    FOREIGN KEY (survey_id)

    REFERENCES surveys(survey_id)

    ON DELETE CASCADE,

    CONSTRAINT chk_sync_status

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
-- Tracks changes in survey status.
-- ============================================================

CREATE TABLE IF NOT EXISTS audit_logs
(
    log_id UUID PRIMARY KEY
    DEFAULT gen_random_uuid(),

    survey_id UUID,

    old_status VARCHAR(20),

    new_status VARCHAR(20),

    changed_at TIMESTAMP
    DEFAULT CURRENT_TIMESTAMP
);



-- ============================================================
-- FUNCTION 1: UPDATE MODIFICATION TIMESTAMP
-- ============================================================

CREATE OR REPLACE FUNCTION update_modified_time()

RETURNS TRIGGER

AS
$$

BEGIN

    NEW.updated_at = CURRENT_TIMESTAMP;

    RETURN NEW;

END;

$$

LANGUAGE plpgsql;



-- ============================================================
-- TRIGGER 1: UPDATE MODIFICATION TIMESTAMP
-- ============================================================

DROP TRIGGER IF EXISTS trg_update_modified_time
ON surveys;

CREATE TRIGGER trg_update_modified_time

BEFORE UPDATE

ON surveys

FOR EACH ROW

EXECUTE FUNCTION update_modified_time();



-- ============================================================
-- FUNCTION 2: CREATE AUDIT RECORD
-- ============================================================

CREATE OR REPLACE FUNCTION create_audit_record()

RETURNS TRIGGER

AS
$$

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

    RETURN NEW;

END;

$$

LANGUAGE plpgsql;



-- ============================================================
-- TRIGGER 2: AUDIT LOG
-- ============================================================

DROP TRIGGER IF EXISTS trg_audit_record
ON surveys;

CREATE TRIGGER trg_audit_record

AFTER UPDATE

ON surveys

FOR EACH ROW

WHEN
(
    OLD.survey_status
    IS DISTINCT FROM
    NEW.survey_status
)

EXECUTE FUNCTION create_audit_record();



-- ============================================================
-- FUNCTION 3: GENERATE SURVEY NUMBER
-- Example:
-- SC-2026-000001
-- ============================================================

CREATE SEQUENCE IF NOT EXISTS survey_sequence
START 1;

CREATE OR REPLACE FUNCTION generate_survey_number()

RETURNS TRIGGER

AS
$$

BEGIN

    NEW.survey_number :=

        'SC-'

        || EXTRACT(YEAR FROM CURRENT_DATE)

        || '-'

        || LPAD
        (
            nextval('survey_sequence')::TEXT,
            6,
            '0'
        );

    RETURN NEW;

END;

$$

LANGUAGE plpgsql;



-- ============================================================
-- TRIGGER 3: GENERATE SURVEY NUMBER
-- ============================================================

DROP TRIGGER IF EXISTS trg_generate_survey_number
ON surveys;

CREATE TRIGGER trg_generate_survey_number

BEFORE INSERT

ON surveys

FOR EACH ROW

EXECUTE FUNCTION generate_survey_number();



-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_users_mobile

ON users(mobile_number);

CREATE INDEX IF NOT EXISTS idx_surveys_user

ON surveys(user_id);

CREATE INDEX IF NOT EXISTS idx_surveys_status

ON surveys(survey_status);

CREATE INDEX IF NOT EXISTS idx_damage_images_survey

ON damage_images(survey_id);

CREATE INDEX IF NOT EXISTS idx_casualties_survey

ON casualties(survey_id);



-- ============================================================
-- VIEW: SURVEY DASHBOARD
-- ============================================================

CREATE OR REPLACE VIEW survey_dashboard

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
-- TESTING COMMANDS
-- Uncomment if needed.
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

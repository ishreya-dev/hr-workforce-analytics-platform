-- schema.sql (v2.0)
-- Star schema DDL for HR Attrition & Workforce Analytics
-- Scope: matches the ~33-column cleaned output of ETL/Python/data_cleaning.py,
-- built from the full 43-column Excel source (Architecture/DataArchitecture.md
-- is the source of truth for this design).
--
-- CHANGE LOG (v1.0 -> v2.0):
-- - Grain key changed from emp_no (hrdata.csv, disproven derivation) to
--   employee_number (verified real source identifier) — see
--   Architecture/DataArchitecture.md Section 2.1.
-- - Fact table widened from 11 to ~28 measures: compensation (monthly_income,
--   daily_rate, hourly_rate, monthly_rate), tenure (years_at_company,
--   years_in_current_role, years_since_last_promotion, years_with_curr_manager,
--   total_working_years), over_time, work_life_balance, environment_satisfaction,
--   job_involvement, relationship_satisfaction, performance_rating, job_level,
--   stock_option_level, percent_salary_hike, num_companies_worked,
--   distance_from_home, training_times_last_year.
--
-- Portability note: written for SQLite (local dev). For Postgres, replace
-- INTEGER PRIMARY KEY AUTOINCREMENT with SERIAL PRIMARY KEY / GENERATED
-- ALWAYS AS IDENTITY. No other syntax here is SQLite-specific.

DROP TABLE IF EXISTS Fact_Employee;
DROP TABLE IF EXISTS Dim_JobRole;
DROP TABLE IF EXISTS Dim_Department;
DROP TABLE IF EXISTS Dim_Education;
DROP TABLE IF EXISTS Dim_MaritalStatus;
DROP TABLE IF EXISTS staging_employee;

-- Staging: 1:1 copy of the cleaned CSV, no transformation applied yet.
CREATE TABLE staging_employee (
    employee_number             INTEGER PRIMARY KEY,
    gender                      TEXT NOT NULL,
    marital_status              TEXT NOT NULL,
    age_band                    TEXT NOT NULL,
    age                         INTEGER NOT NULL,
    department                  TEXT NOT NULL,
    education                   TEXT NOT NULL,
    education_field             TEXT NOT NULL,
    job_role                    TEXT NOT NULL,
    job_level                   INTEGER NOT NULL,
    business_travel             TEXT NOT NULL,
    attrition                   TEXT NOT NULL,
    job_satisfaction            INTEGER NOT NULL,
    environment_satisfaction    INTEGER NOT NULL,
    relationship_satisfaction   INTEGER NOT NULL,
    job_involvement             INTEGER NOT NULL,
    work_life_balance           INTEGER NOT NULL,
    performance_rating          INTEGER NOT NULL,
    over_time                   TEXT NOT NULL,
    monthly_income              INTEGER NOT NULL,
    daily_rate                  INTEGER NOT NULL,
    hourly_rate                 INTEGER NOT NULL,
    monthly_rate                INTEGER NOT NULL,
    percent_salary_hike         INTEGER NOT NULL,
    stock_option_level          INTEGER NOT NULL,
    total_working_years         INTEGER NOT NULL,
    years_at_company            INTEGER NOT NULL,
    years_in_current_role       INTEGER NOT NULL,
    years_since_last_promotion  INTEGER NOT NULL,
    years_with_curr_manager     INTEGER NOT NULL,
    num_companies_worked        INTEGER NOT NULL,
    distance_from_home          INTEGER NOT NULL,
    training_times_last_year    INTEGER NOT NULL
);

-- Dimension tables

CREATE TABLE Dim_Department (
    DepartmentKey   INTEGER PRIMARY KEY AUTOINCREMENT,
    DepartmentName  TEXT NOT NULL UNIQUE
);

CREATE TABLE Dim_JobRole (
    JobRoleKey     INTEGER PRIMARY KEY AUTOINCREMENT,
    JobRoleName    TEXT NOT NULL,
    DepartmentKey  INTEGER NOT NULL REFERENCES Dim_Department(DepartmentKey),
    UNIQUE (JobRoleName, DepartmentKey)
);

-- EducationLevel is read directly as text from the source (verified by
-- inspection: the raw "Education" column already arrives as labels like
-- "Bachelor's Degree", not a 1-5 integer as originally assumed — no
-- numeric->label mapping needed, Architecture/DataArchitecture.md Section 3).
CREATE TABLE Dim_Education (
    EducationKey    INTEGER PRIMARY KEY AUTOINCREMENT,
    EducationLevel  TEXT NOT NULL,
    EducationField  TEXT NOT NULL,
    UNIQUE (EducationLevel, EducationField)
);

CREATE TABLE Dim_MaritalStatus (
    MaritalStatusKey   INTEGER PRIMARY KEY AUTOINCREMENT,
    MaritalStatusName  TEXT NOT NULL UNIQUE
);

-- Fact table: grain = one row per employee (employee_number)
-- No Dim_Date: the source still has no hire/term/review date field of any
-- kind after the rebuild (Architecture/DataArchitecture.md Section 1/6) —
-- not modeled because it does not exist, not omitted by accident.

CREATE TABLE Fact_Employee (
    employee_number             INTEGER PRIMARY KEY,
    DepartmentKey                INTEGER NOT NULL REFERENCES Dim_Department(DepartmentKey),
    JobRoleKey                   INTEGER NOT NULL REFERENCES Dim_JobRole(JobRoleKey),
    EducationKey                 INTEGER NOT NULL REFERENCES Dim_Education(EducationKey),
    MaritalStatusKey             INTEGER NOT NULL REFERENCES Dim_MaritalStatus(MaritalStatusKey),
    age                          INTEGER NOT NULL,
    age_band                     TEXT NOT NULL,
    gender                       TEXT NOT NULL,
    job_level                    INTEGER NOT NULL,
    business_travel              TEXT NOT NULL,
    job_satisfaction             INTEGER NOT NULL,
    environment_satisfaction     INTEGER NOT NULL,
    relationship_satisfaction    INTEGER NOT NULL,
    job_involvement              INTEGER NOT NULL,
    work_life_balance            INTEGER NOT NULL,
    performance_rating           INTEGER NOT NULL,
    over_time                    TEXT NOT NULL CHECK (over_time IN ('Yes', 'No')),
    monthly_income               INTEGER NOT NULL,
    daily_rate                   INTEGER NOT NULL,
    hourly_rate                  INTEGER NOT NULL,
    monthly_rate                 INTEGER NOT NULL,
    percent_salary_hike          INTEGER NOT NULL,
    stock_option_level           INTEGER NOT NULL,
    total_working_years          INTEGER NOT NULL,
    years_at_company             INTEGER NOT NULL,
    years_in_current_role        INTEGER NOT NULL,
    years_since_last_promotion   INTEGER NOT NULL,
    years_with_curr_manager      INTEGER NOT NULL,
    num_companies_worked         INTEGER NOT NULL,
    distance_from_home           INTEGER NOT NULL,
    training_times_last_year     INTEGER NOT NULL,
    attrition                    TEXT NOT NULL CHECK (attrition IN ('Yes', 'No'))
);
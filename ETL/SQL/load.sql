-- 02_load.sql
-- Populates dimension and fact tables from staging_employee.
--
-- Loading staging_employee itself from Data/processed/hrdata_clean.csv is a
-- database-specific bulk-load step (SQLite: .import via CLI or a script;
-- Postgres: COPY) and is intentionally NOT written as portable SQL here —
-- see ETL/SQL/run_sql_pipeline.py for the local dev harness that does this.
-- Everything below this point (staging -> dims -> fact) IS portable SQL.

-- Dim_Department
INSERT INTO Dim_Department (DepartmentName)
SELECT DISTINCT department FROM staging_employee ORDER BY department;

-- Dim_MaritalStatus
INSERT INTO Dim_MaritalStatus (MaritalStatusName)
SELECT DISTINCT marital_status FROM staging_employee ORDER BY marital_status;

-- Dim_Education (level x field combinations actually present in the data)
INSERT INTO Dim_Education (EducationLevel, EducationField)
SELECT DISTINCT education, education_field FROM staging_employee
ORDER BY education, education_field;

-- Dim_JobRole (roles roll up to the department they're most associated with
-- in this snapshot; a role could in principle span departments, but in this
-- dataset each job_role maps to exactly one department)
INSERT INTO Dim_JobRole (JobRoleName, DepartmentKey)
SELECT DISTINCT s.job_role, d.DepartmentKey
FROM staging_employee s
JOIN Dim_Department d ON d.DepartmentName = s.department
ORDER BY s.job_role;

-- Fact_Employee: join staging back to each dimension to resolve keys
-- (v2.0: employee_number is the grain key, not emp_no — Architecture/DataArchitecture.md
-- Section 2.1 — and the fact table now carries the full ~28-measure widened shape from
-- schema.sql, not the old 11-column v1.0 shape.)
INSERT INTO Fact_Employee (
    employee_number, DepartmentKey, JobRoleKey, EducationKey, MaritalStatusKey,
    age, age_band, gender, job_level, business_travel,
    job_satisfaction, environment_satisfaction, relationship_satisfaction,
    job_involvement, work_life_balance, performance_rating, over_time,
    monthly_income, daily_rate, hourly_rate, monthly_rate, percent_salary_hike,
    stock_option_level, total_working_years, years_at_company,
    years_in_current_role, years_since_last_promotion, years_with_curr_manager,
    num_companies_worked, distance_from_home, training_times_last_year, attrition
)
SELECT
    s.employee_number,
    d.DepartmentKey,
    jr.JobRoleKey,
    ed.EducationKey,
    ms.MaritalStatusKey,
    s.age,
    s.age_band,
    s.gender,
    s.job_level,
    s.business_travel,
    s.job_satisfaction,
    s.environment_satisfaction,
    s.relationship_satisfaction,
    s.job_involvement,
    s.work_life_balance,
    s.performance_rating,
    s.over_time,
    s.monthly_income,
    s.daily_rate,
    s.hourly_rate,
    s.monthly_rate,
    s.percent_salary_hike,
    s.stock_option_level,
    s.total_working_years,
    s.years_at_company,
    s.years_in_current_role,
    s.years_since_last_promotion,
    s.years_with_curr_manager,
    s.num_companies_worked,
    s.distance_from_home,
    s.training_times_last_year,
    s.attrition
FROM staging_employee s
JOIN Dim_Department d       ON d.DepartmentName = s.department
JOIN Dim_JobRole jr          ON jr.JobRoleName = s.job_role AND jr.DepartmentKey = d.DepartmentKey
JOIN Dim_Education ed        ON ed.EducationLevel = s.education AND ed.EducationField = s.education_field
JOIN Dim_MaritalStatus ms    ON ms.MaritalStatusName = s.marital_status;

-- Row-count sanity check (LLD.md Section 4): every stage must reconcile to
-- the same employee count. Run this after loading and compare to staging.
-- SELECT
--     (SELECT COUNT(*) FROM staging_employee) AS staging_count,
--     (SELECT COUNT(*) FROM Fact_Employee)     AS fact_count;
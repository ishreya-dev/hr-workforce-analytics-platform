-- views.sql (v2.0)
-- Governed views — the canonical, reusable data products that Power BI
-- numbers are checked against (TRD Section 7).
--
-- CHANGE LOG (v1.0 -> v2.0): added vw_compensation_summary and
-- vw_tenure_summary now that income/tenure fields are in scope (BRD Section 6).

DROP VIEW IF EXISTS vw_attrition_rate;
DROP VIEW IF EXISTS vw_department_summary;
DROP VIEW IF EXISTS vw_satisfaction_summary;
DROP VIEW IF EXISTS vw_compensation_summary;
DROP VIEW IF EXISTS vw_tenure_summary;

-- Single source of truth for overall attrition rate
CREATE VIEW vw_attrition_rate AS
SELECT
    COUNT(*) AS total_headcount,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) AS attrition_count,
    ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
FROM Fact_Employee;

-- Single source of truth for department-level summary (feeds the
-- Department Attrition Rank KPI and the department chart)
CREATE VIEW vw_department_summary AS
SELECT
    d.DepartmentName,
    COUNT(*) AS headcount,
    SUM(CASE WHEN f.attrition = 'Yes' THEN 1 ELSE 0 END) AS attrition_count,
    ROUND(100.0 * SUM(CASE WHEN f.attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct,
    ROUND(AVG(f.job_satisfaction), 2) AS avg_job_satisfaction
FROM Fact_Employee f
JOIN Dim_Department d ON d.DepartmentKey = f.DepartmentKey
GROUP BY d.DepartmentName;

-- Single source of truth for the Job Satisfaction Index and
-- Low-Satisfaction Share KPIs
CREATE VIEW vw_satisfaction_summary AS
SELECT
    ROUND(AVG(job_satisfaction), 2) AS job_satisfaction_index,
    ROUND(AVG(environment_satisfaction), 2) AS environment_satisfaction_index,
    ROUND(AVG(work_life_balance), 2) AS work_life_balance_index,
    ROUND(100.0 * SUM(CASE WHEN job_satisfaction <= 2 THEN 1 ELSE 0 END) / COUNT(*), 2) AS low_satisfaction_share_pct
FROM Fact_Employee;

-- New (v2.0): compensation-vs-attrition — the fields this workbook actually
-- has, contrary to v1.0's "no compensation data exists" scoping error.
CREATE VIEW vw_compensation_summary AS
SELECT
    attrition,
    COUNT(*) AS headcount,
    ROUND(AVG(monthly_income), 2) AS avg_monthly_income,
    ROUND(AVG(percent_salary_hike), 2) AS avg_percent_salary_hike,
    ROUND(AVG(stock_option_level), 2) AS avg_stock_option_level
FROM Fact_Employee
GROUP BY attrition;

-- New (v2.0): tenure-vs-attrition and overtime-vs-attrition, also
-- previously out-of-scope on the incorrect assumption these fields
-- didn't exist (BRD Section 4).
CREATE VIEW vw_tenure_summary AS
SELECT
    attrition,
    over_time,
    COUNT(*) AS headcount,
    ROUND(AVG(years_at_company), 2) AS avg_years_at_company,
    ROUND(AVG(total_working_years), 2) AS avg_total_working_years,
    ROUND(AVG(years_since_last_promotion), 2) AS avg_years_since_last_promotion
FROM Fact_Employee
GROUP BY attrition, over_time;
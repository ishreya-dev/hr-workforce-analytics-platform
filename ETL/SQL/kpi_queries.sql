-- kpi_queries.sql (v2.0)
-- One query per KPI committed in Business/BRD.md Section 6.
-- Every one of these must reconcile exactly against the corresponding
-- Power BI card (see Testing/kpi_reconciliation.md once that folder is built —
-- HLD.md Section 6).

-- KPI: Total Headcount
SELECT COUNT(*) AS total_headcount
FROM Fact_Employee;

-- KPI: Active Employees
SELECT COUNT(*) AS active_employees
FROM Fact_Employee
WHERE attrition = 'No';

-- KPI: Attrition Rate (overall)
SELECT
    ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
FROM Fact_Employee;

-- KPI: Average Age
SELECT ROUND(AVG(age), 2) AS average_age
FROM Fact_Employee;

-- KPI: Job Satisfaction Index (average, 1-4 scale)
SELECT ROUND(AVG(job_satisfaction), 2) AS job_satisfaction_index
FROM Fact_Employee;

-- KPI: Low-Satisfaction Share (employees reporting satisfaction <= 2)
SELECT
    ROUND(100.0 * SUM(CASE WHEN job_satisfaction <= 2 THEN 1 ELSE 0 END) / COUNT(*), 2) AS low_satisfaction_share_pct
FROM Fact_Employee;

-- KPI (new, v2.0): Average Monthly Income by attrition status
SELECT
    attrition,
    ROUND(AVG(monthly_income), 2) AS avg_monthly_income
FROM Fact_Employee
GROUP BY attrition;

-- KPI (new, v2.0): Average Tenure (Years At Company) by attrition status
SELECT
    attrition,
    ROUND(AVG(years_at_company), 2) AS avg_years_at_company
FROM Fact_Employee
GROUP BY attrition;

-- KPI (new, v2.0): Overtime-Attrition Rate
SELECT
    over_time,
    COUNT(*) AS headcount,
    ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
FROM Fact_Employee
GROUP BY over_time;

-- KPI: Department Attrition Rank (window function — ranks departments by
-- attrition rate, highest first; see attrition_deep_dive.sql for the
-- fuller version with row-level detail)
WITH dept_attrition AS (
    SELECT
        d.DepartmentName,
        COUNT(*) AS headcount,
        SUM(CASE WHEN f.attrition = 'Yes' THEN 1 ELSE 0 END) AS attrition_count,
        ROUND(100.0 * SUM(CASE WHEN f.attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
    FROM Fact_Employee f
    JOIN Dim_Department d ON d.DepartmentKey = f.DepartmentKey
    GROUP BY d.DepartmentName
)
SELECT
    DepartmentName,
    headcount,
    attrition_count,
    attrition_rate_pct,
    RANK() OVER (ORDER BY attrition_rate_pct DESC) AS attrition_rank
FROM dept_attrition
ORDER BY attrition_rank;
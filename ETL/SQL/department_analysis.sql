-- department_analysis.sql (v2.0)
-- Department-level breakdowns supporting the "which departments lose people
-- fastest" business question (Business/BRD.md Section 3).

-- Department summary: headcount, attrition, satisfaction, and (new)
-- compensation/tenure signals
SELECT
    d.DepartmentName,
    COUNT(*) AS headcount,
    SUM(CASE WHEN f.attrition = 'Yes' THEN 1 ELSE 0 END) AS attrition_count,
    ROUND(100.0 * SUM(CASE WHEN f.attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct,
    ROUND(AVG(f.job_satisfaction), 2) AS avg_job_satisfaction,
    ROUND(AVG(f.age), 1) AS avg_age,
    ROUND(AVG(f.monthly_income), 2) AS avg_monthly_income,
    ROUND(AVG(f.years_at_company), 2) AS avg_years_at_company
FROM Fact_Employee f
JOIN Dim_Department d ON d.DepartmentKey = f.DepartmentKey
GROUP BY d.DepartmentName
ORDER BY attrition_rate_pct DESC;

-- Department x Job Role attrition (finer-grained view within each department)
SELECT
    d.DepartmentName,
    jr.JobRoleName,
    COUNT(*) AS headcount,
    SUM(CASE WHEN f.attrition = 'Yes' THEN 1 ELSE 0 END) AS attrition_count,
    ROUND(100.0 * SUM(CASE WHEN f.attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
FROM Fact_Employee f
JOIN Dim_Department d ON d.DepartmentKey = f.DepartmentKey
JOIN Dim_JobRole jr    ON jr.JobRoleKey = f.JobRoleKey
GROUP BY d.DepartmentName, jr.JobRoleName
HAVING COUNT(*) >= 5   -- suppress noisy rates from very small job-role cells
ORDER BY attrition_rate_pct DESC;

-- Department x Business Travel (does travel frequency compound with department?)
SELECT
    d.DepartmentName,
    f.business_travel,
    COUNT(*) AS headcount,
    ROUND(100.0 * SUM(CASE WHEN f.attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
FROM Fact_Employee f
JOIN Dim_Department d ON d.DepartmentKey = f.DepartmentKey
GROUP BY d.DepartmentName, f.business_travel
ORDER BY d.DepartmentName, attrition_rate_pct DESC;

-- New (v2.0): Department x Over Time — was out of scope in v1.0
SELECT
    d.DepartmentName,
    f.over_time,
    COUNT(*) AS headcount,
    ROUND(100.0 * SUM(CASE WHEN f.attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct,
    ROUND(AVG(f.monthly_income), 2) AS avg_monthly_income
FROM Fact_Employee f
JOIN Dim_Department d ON d.DepartmentKey = f.DepartmentKey
GROUP BY d.DepartmentName, f.over_time
ORDER BY d.DepartmentName, attrition_rate_pct DESC;
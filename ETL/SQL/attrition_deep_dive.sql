-- Row-level detail behind the Department Attrition Rank KPI
-- (kpi_queries.sql references this file for "the fuller version with
-- row-level detail" — it was a 0-byte placeholder in v1.0; written here).

-- Every employee who left, with the segment fields most likely to explain why,
-- ranked within their department by tenure (shortest-tenure leavers first —
-- often the highest-signal group for early-attrition analysis).
SELECT
    f.employee_number,
    d.DepartmentName,
    jr.JobRoleName,
    f.age,
    f.age_band,
    f.gender,
    ms.MaritalStatusName,
    f.job_satisfaction,
    f.environment_satisfaction,
    f.work_life_balance,
    f.over_time,
    f.monthly_income,
    f.years_at_company,
    f.years_since_last_promotion,
    f.num_companies_worked,
    RANK() OVER (
        PARTITION BY d.DepartmentName
        ORDER BY f.years_at_company ASC
    ) AS shortest_tenure_rank_in_dept
FROM Fact_Employee f
JOIN Dim_Department d    ON d.DepartmentKey = f.DepartmentKey
JOIN Dim_JobRole jr       ON jr.JobRoleKey = f.JobRoleKey
JOIN Dim_MaritalStatus ms ON ms.MaritalStatusKey = f.MaritalStatusKey
WHERE f.attrition = 'Yes'
ORDER BY d.DepartmentName, shortest_tenure_rank_in_dept;

-- Department attrition rank with the underlying row-level leaver detail
-- summarized alongside it (bridges this file's detail back to the
-- aggregate KPI in kpi_queries.sql, so both can be reviewed together
-- during KPI reconciliation).
SELECT
    d.DepartmentName,
    COUNT(*) AS leavers,
    ROUND(AVG(f.years_at_company), 2) AS avg_tenure_at_departure,
    ROUND(AVG(f.monthly_income), 2) AS avg_income_at_departure,
    SUM(CASE WHEN f.over_time = 'Yes' THEN 1 ELSE 0 END) AS leavers_on_overtime,
    ROUND(100.0 * SUM(CASE WHEN f.over_time = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_leavers_on_overtime
FROM Fact_Employee f
JOIN Dim_Department d ON d.DepartmentKey = f.DepartmentKey
WHERE f.attrition = 'Yes'
GROUP BY d.DepartmentName
ORDER BY leavers DESC;
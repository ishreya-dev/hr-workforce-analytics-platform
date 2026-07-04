# Insights & Recommendations
**Project:** HR Attrition & Workforce Analytics
**Basis:** `ETL/SQL/kpi_queries.sql`, `department_analysis.sql`, `attrition_deep_dive.sql`, and views in `views.sql`, run against the full 1,470-employee, 43-column source. Every number below is reproducible from those files — see the query note under each finding.
**Addresses:** `Business/BRD.md` Section 3 (business questions) and Section 6 (≥5 quantified, actionable recommendations, at least one grounded in compensation/tenure data).

---

## Headline

Overall attrition is **16.12%** (237 of 1,470 employees). It is not evenly distributed — it concentrates heavily in five identifiable, actionable segments below. Addressing the top two (overtime and first-year tenure) would target the majority of at-risk headcount without a company-wide policy change.

---

## 1. Overtime is the single strongest attrition driver

- Employees working overtime: **30.5%** attrition.
- Employees not working overtime: **10.4%** attrition.
- Gap: **~3x**, the largest of any segment measured.

**Recommendation:** Audit overtime allocation in Sales and R&D specifically (where overtime-attrition gaps are largest — 37.5% vs. 8.6% attrition for R&D over-time vs. not). Cap sustained overtime or introduce compensating time off before it converts to attrition. This is the highest-leverage single intervention available in this dataset.

*Query: `SELECT over_time, ROUND(100.0*SUM(CASE WHEN attrition='Yes' THEN 1 ELSE 0 END)/COUNT(*),2) FROM Fact_Employee GROUP BY over_time` — see `kpi_queries.sql`.*

## 2. Attrition is highest in an employee's first year, then drops steadily

| Tenure band | Attrition rate |
|---|---|
| 0-1 years | **34.9%** |
| 2-3 years | 18.4% |
| 4-5 years | 13.1% |
| 6-10 years | 12.3% |
| 11+ years | 8.1% |

**Recommendation:** Build a structured 12-month onboarding/retention checkpoint program (30/60/90-day check-ins, mentorship pairing). Early tenure is the single biggest attrition window — a new hire is roughly **4x more likely to leave** in year one than after year 11.

*Query: tenure-band CTE against `Fact_Employee.years_at_company` — reproducible via a `CASE WHEN` grouping, same pattern as `department_analysis.sql`.*

## 3. Entry-level employees (Job Level 1) leave at the highest rate — and earn the least

| Job Level | Attrition rate | Avg. monthly income |
|---|---|---|
| 1 | **26.3%** | $2,787 |
| 2 | 9.7% | $5,502 |
| 3 | 14.7% | $9,817 |
| 4 | 4.7% | $15,504 |
| 5 | 7.3% | $19,192 |

**Recommendation:** Job Level 1 attrition (26.3%) is nearly 3x Job Level 2 (9.7%), while compensation more than doubles between those two levels. Review Level 1 compensation bands and accelerate the Level 1→2 promotion timeline — the current cliff between levels 1 and 2 looks like a retention risk, not just a natural entry-level churn pattern.

*Query: `GROUP BY job_level` on `Fact_Employee`, joined against `attrition` and `monthly_income` — see `vw_compensation_summary` pattern in `views.sql`.*

## 4. Employees with no stock options attrite at 2-3x the rate of those with any

| Stock Option Level | Headcount | Attrition rate |
|---|---|---|
| 0 | 631 | **24.4%** |
| 1 | 596 | 9.4% |
| 2 | 158 | 7.6% |
| 3 | 85 | 17.7% |

**Recommendation:** The jump from Level 0 to Level 1 stock options corresponds to a >2.5x drop in attrition. Since Level 0 has the largest headcount (631 employees, 43% of the workforce), extending even minimal equity participation to this group is a well-targeted, scalable retention lever. (Level 3's uptick to 17.7% on a smaller base of 85 is worth a separate look — possibly senior employees nearing other career decisions rather than a compensation issue.)

*Query: `GROUP BY stock_option_level` on `Fact_Employee`.*

## 5. Single employees attrite at 2x the rate of married employees

| Marital Status | Headcount | Attrition rate |
|---|---|---|
| Single | 470 | **25.5%** |
| Married | 673 | 12.5% |
| Divorced | 327 | 10.1% |

**Recommendation:** This is a demographic correlation, not a lever HR can pull directly — but it's useful as a targeting signal. Combine with the overtime and tenure findings above: a single, first-year, no-stock-option employee is very plausibly the highest-risk profile in the workforce. Consider whether flexible scheduling or social/team-integration programs (often disproportionately valued by early-career, unmarried employees) are worth piloting.

*Query: `GROUP BY marital_status` on `Fact_Employee`, joined via `Dim_MaritalStatus`.*

## 6. Distance from home compounds the risk

- 0-5 miles: 13.8% attrition
- 6-15 miles: 16.1% attrition
- 16+ miles: **20.7% attrition**

**Recommendation:** Commute distance has a smaller but consistent effect. For roles where it's feasible, hybrid/remote flexibility for employees living 16+ miles away is a low-cost lever layered on top of the higher-priority items above.

*Query: distance-band CTE against `Fact_Employee.distance_from_home`.*

## 7. Role-level hotspot: Sales Representative

- **39.8% attrition** (33 of 83 headcount) — the highest of any job role, well above the Sales department average (20.6%) that contains it.

**Recommendation:** Treat this as a role-specific retention project distinct from the department-level Sales findings — whatever is driving Sales Executive (17.5%) attrition is not the same magnitude as what's driving Sales Representative attrition, so a department-wide fix would under-serve the group actually at risk.

*Query: `department_analysis.sql`, Department x Job Role cut, `HAVING COUNT(*) >= 5`.*

---

## What this deliberately does not claim

Per `Business/BRD.md` Section 9 and `Architecture/DataArchitecture.md` Section 6, none of the above implies a time-series trend — there is no hire/termination date in the source, only tenure-in-years. "First-year attrition is highest" describes a cross-sectional tenure-band comparison, not a trend measured over calendar time. All figures are point-in-time snapshot statistics.
# KPI Reconciliation
**Referenced by:** `Architecture/HLD.md` Section 6, `ETL/SQL/kpi_queries.sql` header comment.
**Purpose:** Prove every number on the dashboard ties back to a single SQL source of truth, with zero variance (`Business/BRD.md` Section 6 success criteria).
**Method:** Ran `ETL/Python/data_cleaning.py` → `ETL/Python/run_sql_pipeline.py` against the real `HR DATA_Excel.xlsx` source, then compared the resulting SQL view output directly against the dashboard cards/visuals.

## Scope note

The Power BI dashboard (`Analytics/PowerBI/HR Analytics Dashboard Power BI.pbix`) is
**intentionally not being rebuilt in this pass** — it stays pointed at the original flat
`HR data` table, including the legacy `CF_age band` field. This reconciliation therefore
covers only the KPIs currently exposed on the dashboard. Newly in-scope compensation/
tenure/overtime measures (Section 2 below) are validated at the SQL layer only, since
they aren't yet surfaced on the dashboard — see `Architecture/PowerBI_v2_Rebuild_Guide.md`
if that ever changes.

## 1. Cards currently on the dashboard — reconciled, zero variance

| KPI | SQL source (`kpi_queries.sql`) | SQL result | Dashboard card | Match |
|---|---|---|---|---|
| Total Headcount | `SELECT COUNT(*) FROM Fact_Employee` | 1,470 | "Overall Employees" = 1470 | ✅ |
| Attrition Count | `SUM(CASE WHEN attrition='Yes'...)` | 237 | "Attrition" = 237 | ✅ |
| Attrition Rate | `100.0*237/1470` | 16.12% | "Attrition Rate" = 16.12% | ✅ |
| Active Employees | `COUNT WHERE attrition='No'` | 1,233 | "Active Employees" = 1233 | ✅ |
| Average Age | `AVG(age)` | 36.92 | "Average Age" = 37 | ✅ (dashboard rounds to whole number; underlying value confirmed) |

**Department Wise Employee Attrition (pie):** R&D 133 (56.12%), Sales 92 (38.8%), HR 12
(5.06%) on the dashboard vs. SQL `department_analysis.sql` leaver counts — R&D 133,
Sales 92, HR 12. ✅ Match.

**Job Satisfaction Rating (matrix):** spot-checked Sales Representative row (12/21/27/23,
total 83) against `Fact_Employee` filtered `job_role='Sales Representative'` — headcount
83 matches Section 7 of `Insights_and_Recommendations.md` (Sales Rep attrition analysis
uses the same 83-person base). ✅ Match.

## 2. Newly in-scope KPIs — validated at SQL layer, not yet on dashboard

These exist and are correct in `views.sql`/`kpi_queries.sql`, but since the dashboard
isn't being rebuilt this pass, there's nothing on the dashboard to reconcile against yet.
Recorded here so the numbers are pinned down for whenever that changes.

| KPI | SQL result |
|---|---|
| Average Monthly Income (attrited vs. active) | $4,787.09 vs. $6,832.74 |
| Average Tenure, Years At Company (attrited vs. active) | 5.13 vs. 7.37 |
| Overtime Attrition Rate (Yes vs. No) | 30.53% vs. 10.44% |
| Job Satisfaction Index | 2.63 / 4 |
| Environment Satisfaction Index | 2.81 / 4 |
| Work-Life Balance Index | 2.76 / 4 |
| Low-Satisfaction Share (≤2) | 44.49% |

## 3. Row-count integrity check (LLD.md Section 5)

```
staging_employee: 1,470
Fact_Employee:     1,470
Match: True
```
Confirmed via `run_sql_pipeline.py` output — no rows lost or duplicated across the
staging → dimension/fact load.

## 4. Outstanding item

`CF_age band`, `CF_attrition count`, and `CF_attrition rate` remain wired into the live
dashboard. Their values happen to match the canonical SQL numbers today (Section 1), but
per `Business/BRD.md` Section 9 they are not reconciled against or maintained going
forward — if they ever drift, this reconciliation doc is the place that would catch it on
the next run.
# Business Requirements Document (BRD)

## 1. Stakeholder

HR Director, VitalCore Manufacturing (1,470 employees)

## 2. Business Problem

Leadership lacks a consolidated view of where and among whom attrition is concentrated — including whether pay, tenure, and workload factors are contributing. HR currently reacts to resignations rather than identifying at-risk segments proactively. Turnover carries direct cost (recruiting, onboarding) and indirect cost (team disruption, knowledge loss).

## 3. Business Questions

- What is our current attrition rate, overall and by department?
- Which employee segments (department, job role, education field, age band, marital status, travel frequency, overtime status) show elevated attrition?
- Is job satisfaction, work-life balance, or environment satisfaction associated with attrition in any segment?
- Is there a relationship between compensation (monthly income) and attrition, controlling for job level/role?
- Do tenure signals (years at company, years in current role, years since last promotion) show a "flight risk" pattern?
- Does overtime status correlate with attrition?
- Where should retention investment be prioritized given limited HR budget?

## 4. Data Source

Primary source: the `Data` sheet inside `Analytics/Excel/HR DATA_Excel.xlsx` (1,470 rows, 44 raw columns: 43 data fields + `emp no`). The dataset is the IBM HR Analytics Employee Attrition dataset (synthetic, no real PII).

`Data/raw/hrdata.csv` (15 columns) is a legacy derived extract retained for existing dashboards that still reference it. It is not an input to the current pipeline.

## 5. KPIs

- Attrition Rate (overall and by segment)
- Total Headcount
- Active Employees
- Average Age
- Job Satisfaction Index
- Work-Life Balance Index
- Environment Satisfaction Index
- Average Monthly Income (overall, by department, by job level)
- Average Tenure (Years At Company)
- Overtime Attrition Gap (attrition rate for OverTime=Yes vs. No)
- Department Attrition Rank
- Low-Satisfaction Share (employees reporting satisfaction ≤ 2)

## 6. Success Criteria

- Dashboard reconciles exactly with underlying SQL calculations (zero variance)
- At least 5 quantified, actionable recommendations delivered alongside the dashboard
- A non-technical stakeholder can navigate the dashboard and identify the top attrition-associated segment within 2 minutes
- At least one recommendation draws on compensation or tenure data

## 7. Assumptions

- Data represents a single point-in-time snapshot, not a continuous HR system feed
- `Attrition` is the single canonical attrition flag. The 6 legacy Power Pivot calculated fields (`CF_*`) from the original Excel workbook are documented as retired artifacts and are not carried into the new pipeline
- `Employee Count` is a constant field (always 1) and carries no analytical value beyond confirming one row per employee
- `emp_no` (from the legacy 15-column extract) is a row-position-based surrogate key (10000 + row index), independent of `Employee Number`. The new pipeline uses `Employee Number` directly as the surrogate key
- `-2` and `0` are junk/placeholder columns with no documented meaning, dropped during cleaning
- `Over18` and `Standard Hours` are near-constant fields, profiled and dropped if confirmed zero-variance
- No calendar date field exists in this source, so no claim implies a true time-series trend; tenure fields are treated as snapshot attributes

## 8. Constraints

- No live data connection (static file source)
- No PII beyond what's already de-identified in the source file (`Employee Number` is a surrogate key, not a real employee ID)

## 9. Out of Scope

- Predictive/ML attrition modeling
- Real-time data refresh
- Integration with an actual HRIS
- Any KPI or chart implying a true calendar time-series trend (no hire/termination dates exist in this source)
- Reconciliation against the 6 legacy Power Pivot calculated fields (`CF_*`)
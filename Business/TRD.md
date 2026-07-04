# Technical Requirements Document (TRD)

## 1. Functional Requirements

- **FR1:** Pipeline must ingest the raw 43-column source and produce a validated, cleaned dataset without adding or inferring any field not present in the source
- **FR2:** SQL layer must reproduce every KPI shown in Power BI, queryable independently, using only fields present in the source (or fields derived purely from them)
- **FR3:** Power BI must expose documented DAX measures for every visible KPI
- **FR4:** Every visual must map to a documented business question from BRD Section 3
- **FR5:** Any chart or narrative claim referencing a true calendar date/time-series trend must be flagged as unavailable-data rather than omitted silently
- **FR6:** The pipeline must never write to or modify the raw source files. The existing Power BI and Tableau dashboards read directly from the raw files and must keep working unchanged. Pipeline only ever reads raw, writes processed
- **FR7:** Pipeline must NOT attempt to reconcile against the 6 legacy `CF_*` Power Pivot calculated fields — these are out of scope. The pipeline computes its own canonical measures directly from `Attrition`

## 2. Non-Functional Requirements

- **Reproducibility:** pipeline runs end-to-end from a clean clone with one command
- **Transparency:** every transformation logged; no silent data changes
- **Maintainability:** config-driven paths/constants, no hardcoded values in logic
- **Portability:** SQL scripts runnable on SQLite (zero-install) or PostgreSQL

## 3. Technology Stack

Python 3.11+ (pandas, openpyxl for the Excel source), SQLite/PostgreSQL, Power BI Desktop, Git/GitHub.

## 4. Data Sources

Primary source: the `Data` sheet inside `Analytics/Excel/HR DATA_Excel.xlsx` (also duplicated in `HR Analytics Dashboard Excel Project.xlsx`, and mirrored as the `"HR data"` Power Query table inside the `.pbix`) — 1,470 rows, 44 raw columns (43 data fields + `emp no`), no nulls confirmed during profiling.

`Data/raw/hrdata.csv` (15 columns) is retained as a legacy derived extract — it is not re-derived from or reconciled against the 43-column source in this pipeline version; it remains untouched for the existing dashboards that still point at it (FR6).

### 4.1 Identifier Resolution

Three identifier-like fields exist across the sources:

| Field | Source | Format | Notes |
|-------|--------|--------|-------|
| `Employee Number` | 43-col source | Sequential int, gaps present (1, 2, 4, 5, 7, 8, 10...) | The source system's real identifier. Adopted as the surrogate key going forward |
| `emp no` | 43-col source | String codes (`"STAFF-1"`, `"STAFF-2"`...) | Human-readable label derived from `Employee Number`; not used as a join key |
| `emp_no` | `hrdata.csv` legacy extract | Sequential int, no gaps (10001–11470) | Row-position surrogate key (10000 + row_index), generated independently when the extract was created, unrelated to any real source identifier |

**Verification method:** row-by-row comparison of `Age` and `Gender` between `hrdata.csv` and the 43-column source confirmed 100% positional alignment — i.e., row *N* in one file is the same employee as row *N* in the other, purely by file order, not by a shared key value. This is documented explicitly because it is fragile: if either file is ever independently re-sorted, this alignment breaks silently with no error raised.

**Decision:** the new pipeline is built entirely on `Employee Number` as PK. `emp_no` and its row-order dependency are not carried forward into the new schema.

### 4.2 Verified Full Source Schema

| Column | Type | Notes |
|--------|------|-------|
| `Employee Number` | integer | Adopted PK. Gaps present in the sequence — this is expected and not an error |
| `emp no` | string | `"STAFF-N"` label, cosmetic, not used as key |
| `Age` | integer | |
| `Attrition` | string | Yes/No — canonical attrition flag |
| `Business Travel` | string | Non-Travel / Travel_Rarely / Travel_Frequently |
| `Daily Rate` | integer | |
| `Department` | string | Sales / R&D / HR |
| `Distance From Home` | integer | |
| `Education` | integer | 1–5 scale |
| `Education Field` | string | |
| `Employee Count` | integer | Constant = 1 — zero-variance, drop in cleaning |
| `Environment Satisfaction` | integer | 1–4 scale |
| `Gender` | string | Female / Male |
| `Hourly Rate` | integer | |
| `Job Involvement` | integer | 1–4 scale |
| `Job Level` | integer | 1–5 |
| `Job Role` | string | |
| `Job Satisfaction` | integer | 1–4 scale |
| `Marital Status` | string | Single / Married / Divorced |
| `Monthly Income` | integer | Compensation field |
| `Monthly Rate` | integer | |
| `Num Companies Worked` | integer | |
| `Over18` | string | Expected near-constant; profile and drop if confirmed zero-variance |
| `Over Time` | string | Yes/No |
| `Percent Salary Hike` | integer | |
| `Performance Rating` | integer | |
| `Relationship Satisfaction` | integer | 1–4 scale |
| `Standard Hours` | integer | Expected near-constant; profile and drop if confirmed zero-variance |
| `Stock Option Level` | integer | 0–3 |
| `Total Working Years` | integer | |
| `Training Times Last Year` | integer | |
| `Work Life Balance` | integer | 1–4 scale |
| `Years At Company` | integer | Tenure field |
| `Years In Current Role` | integer | |
| `Years Since Last Promotion` | integer | |
| `Years With Curr Manager` | integer | |
| `-2` | integer | Confirmed constant (single value, -2, across all rows) — junk, drop |
| `0` | integer | Confirmed constant (single value, 0, across all rows) — junk, drop |

**Legacy calculated fields (Excel Power Pivot layer, NOT part of the modeled pipeline):** `CF_age band`, `CF_attrition label`, `CF_attrition count`, `CF_attrition counts`, `CF_attrition rate`, `CF_current Employee`. Documented here for completeness and to explain why they appear in the workbook, but per BRD Section 7/9 they are not cross-validated against or reproduced — the new pipeline computes its own measures from `Attrition` directly.

## 5. ETL Requirements

- **Extract:** read the 43-column `Data` sheet from the Excel workbook as-is, no in-place edits
- **Transform:** Python cleaning (drop constant/junk columns with logged reasons, validate categorical and numeric domains, standardize `Title Case With Spaces` column names to `snake_case`) + SQL modeling (dimension/fact)
- **Load:** processed CSV feeds SQL staging; SQL views feed Power BI

## 6. Data Modeling Requirements (Star Schema)

`Fact_Employee` carries the measures:

- `Fact_Employee`: `employee_number` (PK), `DepartmentKey` (FK), `JobRoleKey` (FK), `EducationKey` (FK), `MaritalStatusKey` (FK), `age`, `gender`, `business_travel`, `job_satisfaction`, `environment_satisfaction`, `work_life_balance`, `job_involvement`, `relationship_satisfaction`, `performance_rating`, `job_level`, `monthly_income`, `daily_rate`, `hourly_rate`, `monthly_rate`, `percent_salary_hike`, `stock_option_level`, `over_time`, `total_working_years`, `years_at_company`, `years_in_current_role`, `years_since_last_promotion`, `years_with_curr_manager`, `num_companies_worked`, `distance_from_home`, `training_times_last_year`, `attrition`
- `Dim_Department`: `DepartmentKey`, `DepartmentName`
- `Dim_JobRole`: `JobRoleKey`, `JobRoleName`, `DepartmentKey`
- `Dim_Education`: `EducationKey`, `EducationLevel` (raw 1–5 integer mapped to a label), `EducationField`
- `Dim_MaritalStatus`: `MaritalStatusKey`, `MaritalStatusName`

No `Dim_Date` — there is no date field of any kind in the source (confirmed unchanged after rebuild). Tenure fields (`Years At Company`, etc.) remain integer attributes on the fact table, not a time dimension.

`age_band` is no longer a raw source field in the 43-column data (it existed only in the legacy 15-column extract, likely derived from `CF_age band`) — it is recomputed by the pipeline from `Age` using documented bin boundaries, not treated as a source-provided field.

## 7. SQL Requirements

DDL for the expanded fact/dimension tables above; KPI queries must use explicit, commented CTEs/window functions where relevant (e.g., `RANK() OVER (ORDER BY attrition_rate DESC)` for department ranking, and a new tenure-band or income-quartile CTE for the compensation/tenure KPIs); views layer is the canonical source Power BI numbers are checked against.

## 8. Python Requirements

- Deterministic cleaning (same input always produces same output)
- Validation checks specific to this schema:
  - `Employee Number` uniqueness
  - `Age` within a plausible working-age range (16–75)
  - All 1–4/1–5 satisfaction-style scales within their documented bounds
  - `Employee Count` is constant (confirms one-row-per-employee grain) before being dropped
  - `Over18` and `Standard Hours` profiled for zero variance; dropped with logged reason if confirmed
  - `-2` and `0` dropped with logged reason (confirmed constant, undocumented meaning)
- No destructive operations without a logged rationale
- No cross-validation against the legacy `CF_*` fields (FR7) — they are not read by the pipeline at all

## 9. Power BI Requirements

**Status: not implemented — deliberate scope decision, not an oversight.** The `.pbix` is unchanged from the pre-rescope version: it still runs on the flat `HR data` table and the legacy `CF_age band` field, with no explicit named DAX measures and no star-schema relationships. This was audited directly against the live file (report layout JSON) and confirmed to reconcile correctly against the new SQL layer today (`Testing/kpi_reconciliation.md`) despite the implementation gap.

The requirements below describe the target state **if** a Power BI rebuild is done in a future iteration — they are not a claim that this has been built.

- All measures explicit and named (no bare implicit aggregations)
- Data model relationships documented against Section 6
- Visual layout unchanged from original except new tooltips/drill-throughs for compensation and tenure measures

## 10. Security

No real PII in this dataset (`Employee Number` is a surrogate key from a synthetic/open dataset). Still document as if it mattered — no credentials committed to the repo; `.gitignore` excludes any local `.env`/config secrets even though none are currently required.

## 11. Error Handling

Python scripts fail loudly (raise, don't silently pass) on schema mismatches — e.g., if a future data refresh removes a column this pipeline depends on, the script should flag "missing expected column" rather than silently proceeding with a partial schema.

## 12. Logging

Every pipeline run logs: timestamp, row counts in/out, transformations applied, dropped-column rationale for each of `Employee Count`/`Over18`/`Standard Hours`/`-2`/`0`, and any validation failures.

## 13. Risks

- **Row-order fragility:** since the legacy `hrdata.csv` extract's row order was the only implicit link to the 43-column source, and the new pipeline no longer depends on that extract, this risk is retired going forward — but is documented here as the reason the pipeline was rebuilt on `Employee Number` rather than continuing to patch around `emp_no`
- **Legacy artifact drift:** the 6 `CF_*` Power Pivot fields in the Excel workbook will silently diverge from the new pipeline's canonical measures over time since they are no longer touched. This is accepted per BRD Section 9 — the Excel workbook's Power Pivot layer is treated as a frozen legacy artifact, not a live component
- Public/derived dataset may look generic without strong original documentation — mitigated by the BRD/TRD/architecture depth, not by the data itself

## 14. Deployment

Local-only for portfolio scope; a deployment guide documents exact reproduction steps (clone → install requirements → run pipeline → open PBIX).
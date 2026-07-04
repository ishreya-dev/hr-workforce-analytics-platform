# Data Architecture

## 1. Star Schema

```
                    Dim_Department
                          │
Dim_JobRole ───── Fact_Employee ───── Dim_Education
                          │
                    Dim_MaritalStatus
```

4 dimension tables around one fact table. No `Dim_Date` — the source file has no hire date, termination date, review date, or any other temporal field. Adding a date dimension here would mean fabricating one, so it is deliberately absent.

## 2. Fact Table — `Fact_Employee`

### 2.1 Grain and Key

Grain: **one row per employee**, keyed on `Employee Number`.

| Column | Source | Type | Notes |
|--------|--------|------|-------|
| `EmployeeNumber` | raw | PK, integer | Source system's own identifier. Gaps in sequence expected, not an error |
| `DepartmentKey` | derived | FK → Dim_Department | |
| `JobRoleKey` | derived | FK → Dim_JobRole | |
| `EducationKey` | derived | FK → Dim_Education | |
| `MaritalStatusKey` | derived | FK → Dim_MaritalStatus | |
| `age` | raw | integer | |
| `gender` | raw | string | Female/Male |
| `business_travel` | raw | string | Non-Travel / Travel_Rarely / Travel_Frequently |
| `job_satisfaction` | raw | integer, 1–4 | |
| `environment_satisfaction` | raw | integer, 1–4 | |
| `work_life_balance` | raw | integer, 1–4 | |
| `job_involvement` | raw | integer, 1–4 | |
| `relationship_satisfaction` | raw | integer, 1–4 | |
| `performance_rating` | raw | integer | |
| `job_level` | raw | integer, 1–5 | |
| `monthly_income` | raw | integer | Compensation |
| `daily_rate`, `hourly_rate`, `monthly_rate` | raw | integer | Compensation |
| `percent_salary_hike` | raw | integer | |
| `stock_option_level` | raw | integer, 0–3 | |
| `over_time` | raw | string, Yes/No | |
| `total_working_years` | raw | integer | Tenure |
| `years_at_company` | raw | integer | Tenure |
| `years_in_current_role` | raw | integer | Tenure |
| `years_since_last_promotion` | raw | integer | Tenure |
| `years_with_curr_manager` | raw | integer | Tenure |
| `num_companies_worked` | raw | integer | |
| `distance_from_home` | raw | integer | |
| `training_times_last_year` | raw | integer | |
| `attrition` | raw | string, Yes/No | Canonical attrition flag |

`age_band` is **not** a raw column in the 43-column source (it only existed in the legacy 15-column extract). It is recomputed by the pipeline from `age` using documented bin boundaries, and treated as a derived display attribute, not stored as if sourced.

### 2.2 Fields Dropped, and Why

| Column | Reason |
|--------|--------|
| `Employee Count` | Constant = 1 across all rows — zero-variance, confirmed during profiling |
| `Over18` | Expected near-constant; profiled and dropped if confirmed zero-variance |
| `Standard Hours` | Expected near-constant; profiled and dropped if confirmed zero-variance |
| `-2` | Confirmed constant (single value, -2, all 1,470 rows) — unlabeled, no documented meaning, junk column |
| `0` | Confirmed constant (single value, 0, all 1,470 rows) — unlabeled, no documented meaning, junk column |
| `emp no` (string label) | Cosmetic `"STAFF-N"` label derived from `Employee Number`; not needed once `Employee Number` is the key |
| `CF_age band`, `CF_attrition label`, `CF_attrition count`, `CF_attrition counts`, `CF_attrition rate`, `CF_current Employee` | Legacy Power Pivot calculated fields from the Excel workbook. Documented as retired artifacts, not carried into the new pipeline — the pipeline computes its own canonical measures directly from `Attrition` rather than reconciling against five undocumented derived fields |

## 3. Dimension Tables

- **`Dim_Department`**: `DepartmentKey`, `DepartmentName` — 3 values (Sales, R&D, HR)
- **`Dim_JobRole`**: `JobRoleKey`, `JobRoleName`, `DepartmentKey` (roles roll up to departments) — 9 values
- **`Dim_Education`**: `EducationKey`, `EducationLevel`, `EducationField` — 5 levels × 6 fields. `EducationLevel` is sourced from the raw 1–5 integer with a documented label mapping
- **`Dim_MaritalStatus`**: `MaritalStatusKey`, `MaritalStatusName` — 3 values (Single, Married, Divorced)

## 4. Relationships

All dimension tables relate to `Fact_Employee` one-to-many on their respective keys — standard star schema, single-direction filter flow, no snowflaking needed at this data volume/complexity (1,470 rows, 4 small dimensions, ~30-column fact table).

## 5. Data Lineage

`HR DATA_Excel.xlsx (Data sheet, raw, untouched)` → `hrdata_clean.csv (Python-validated, 43→~30 cols)` → `SQL staging table` → `SQL dimension + fact tables` → `SQL KPI views (vw_*)` → `Power BI data model` → `Power BI measures/visuals`.

The legacy `Data/raw/hrdata.csv` (15-column extract) is **not** part of this lineage going forward — it remains on disk, untouched, solely because the existing Power BI/Tableau dashboards still point at it. It is not read by the new pipeline.

## 6. Schema Design Notes

- **Compensation** is modeled directly on `Fact_Employee` rather than a separate bridge table, since compensation here is a single point-in-time snapshot value per employee, not a history requiring its own fact/bridge structure
- **`Dim_Date` cannot be built** — there is no calendar date field anywhere in the 43-column source, only tenure-in-years integers. This is a deliberate scope decision driven by data availability
- **SCDs for job-role/department transfers cannot be built** — the source is a single snapshot with no history of prior roles/departments
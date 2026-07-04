# Low-Level Design (LLD) / Data Flow

## 1. Detailed Data Flow

```
HR DATA_Excel.xlsx, "Data" sheet (raw) — 1,470 rows, 44 raw columns, 0 nulls confirmed
   │
   ▼  ETL/Python/data_cleaning.py
   ├─ read the Excel "Data" sheet (openpyxl/pandas), never the legacy hrdata.csv
   ├─ profile every column (dtype, uniqueness, value domain) — log results, never silently drop rows
   ├─ drop Employee Count (constant = 1 — zero-variance, confirmed during profiling)
   ├─ profile Over18 and Standard Hours; drop each with a logged reason if confirmed zero-variance
   ├─ drop the two unlabeled junk columns -2 and 0 (confirmed constant, no documented meaning)
   ├─ drop emp no (cosmetic "STAFF-N" label) — Employee Number is used as the key instead
   ├─ do NOT read or reference the 6 legacy CF_* Power Pivot fields — out of scope, not cross-validated
   ├─ standardize column names from "Title Case With Spaces" to snake_case (explicit mapping, not assumed)
   ├─ recompute age_band from age using documented bin boundaries (age_band is not a raw source field)
   ├─ validate age within plausible working-age bounds (16–75)
   ├─ validate all 1–4/1–5 satisfaction-style scales within documented bounds
   ├─ standardize dtypes (categoricals vs. numerics)
   └─ export → Data/processed/hrdata_clean.csv
   │
   ▼  ETL/SQL/schema.sql + load.sql
   ├─ staging table (1:1 with cleaned CSV)
   ├─ dimension tables: Dim_Department, Dim_JobRole, Dim_Education, Dim_MaritalStatus
   ├─ fact table: Fact_Employee (grain = one row per Employee Number, ~30 measures)
   └─ KPI views: vw_attrition_rate, vw_department_summary, vw_satisfaction_summary, vw_compensation_summary, vw_tenure_summary
   │
   ▼  Power BI
   ├─ import processed data / connect to SQL views
   ├─ confirm star schema relationships match Architecture/DataArchitecture.md
   ├─ documented, named DAX measures layer (no bare implicit aggregations), including new income/tenure/overtime measures
   └─ existing dashboard pages — visually unchanged
   │
   ▼  Business Insights + Recommendations Report
```

## 2. Sequence for a Single Pipeline Run

`User triggers ETL/Python/data_cleaning.py → script reads the Excel "Data" sheet → domain/consistency validation runs → log written → clean CSV written → SQL scripts executed against clean CSV → views created → Power BI refresh reads from clean CSV/SQL views → dashboard updates → analyst reviews KPI reconciliation (Testing/) → insights report authored.`

Single linear pipeline, not a DAG — the source remains one static file with no upstream dependencies. The width of the fact table increased, but the shape of the flow did not; the added columns didn't require added pipeline complexity, only added validation rules.

## 3. Identifier Resolution Detail

v1.0 left the relationship between `hrdata.csv`'s `emp_no` and the wider dataset's identifiers as an unverified assumption (`emp_no = 10000 + Employee Number`). That has now been checked and resolved:

| Step | Finding |
|------|---------|
| 1. Compared `emp_no` sequence to `Employee Number` sequence | `emp_no` is fully sequential (10001–11470, no gaps). `Employee Number` has gaps (1, 2, 4, 5, 7, 8, 10...). The two sequences cannot be related by a fixed offset |
| 2. Hypothesis `10000 + Employee Number` tested directly | False — mismatches appear as soon as the first gap in `Employee Number` is reached |
| 3. Row-position alignment tested instead | `Age` and `Gender` compared row-by-row between `hrdata.csv` and the Excel `Data` sheet — 100% match at every row index |
| **Conclusion** | `emp_no` is a **row-position surrogate key** (`10000 + row_index`), generated independently for the legacy extract. It has no formulaic relationship to `Employee Number` or `emp no` |

**Design consequence:** the new pipeline does not attempt to join or reconcile against `hrdata.csv` at all. It treats `Employee Number` (from the Excel source) as the sole surrogate key, sidestepping the row-order fragility entirely rather than documenting around it.

## 4. Cross-Field Validation Detail

The decision (BRD Section 7) is:

- `Attrition` (Yes/No) is the **sole canonical field**, read directly from the source
- The 5 legacy `CF_*` fields are **not read by the pipeline at all** — no cross-validation is performed against them, and no assertion is written comparing them to `Attrition`
- This is a narrower, more defensible validation surface than v1.0's three-way cross-check, and avoids building assertions against fields whose Power Pivot formulas were never independently confirmed

## 5. Error Handling in the Flow

- Missing expected column at load time → raise, halt pipeline, do not proceed with a partial schema
- Any row failing a numeric/categorical domain check → logged with `Employee Number`, pipeline continues (data-quality flag, not a hard stop, since it doesn't corrupt the rest of the row)
- SQL row-count sanity check after each transform step (staging → dimension/fact → views) — counts must reconcile to 1,470 employees at every stage
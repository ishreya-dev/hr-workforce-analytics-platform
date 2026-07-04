# High-Level Design (HLD)

## 1. Purpose

End-to-end system design for the HR analytics pipeline, covering component interactions and data flow from raw source to dashboard.

## 2. Architecture Diagram

```
┌──────────────┐   ┌──────────────────┐   ┌───────────────┐   ┌────────────────┐   ┌──────────────────┐
│  Raw Data    │→ │  Python Cleaning │→ │  SQL Layer    │→ │  Power BI Model │→ │  Dashboard +      │
│  (Excel      │   │  & Validation    │   │  (KPIs/Views) │   │  (star schema)  │   │  Business Insight │
│  Data sheet) │   │                  │   │               │   │                 │   │                   │
└──────────────┘   └──────────────────┘   └───────────────┘   └────────────────┘   └──────────────────┘
```

## 3. Component Overview

| Component | Responsibility | Notes |
|-----------|----------------|-------|
| Raw Data | Single source of truth: the `Data` sheet inside the Excel workbook, never edited in place | 1,470 rows, 44 raw columns, 0 nulls confirmed; the legacy `Data/raw/hrdata.csv` (15 cols) is retained untouched only because existing dashboards still read it, but is not an input to this pipeline |
| Python Cleaning & Validation | Drop constant/junk columns (`Employee Count`, `Over18`, `Standard Hours` if confirmed zero-variance, `-2`, `0`), validate categorical/numeric domains, standardize column naming to `snake_case` | No cross-validation against the 6 legacy `CF_*` Power Pivot fields — those are documented as retired, not reconciled against |
| SQL Layer | Star schema + KPI views, the reconciliation source of truth | 4 dimension tables + 1 wide fact table (~30 measures) — no `Dim_Date` |
| Power BI Model | Unchanged from the original dashboard — deliberately out of scope for this rebuild | Still runs on the flat `HR data` table, including the legacy `CF_age band` field. Numbers reconcile correctly against the new SQL layer today (`Testing/kpi_reconciliation.md`), but the DAX-measures/star-schema rebuild described elsewhere in this doc set has not been implemented in the `.pbix` |
| Dashboard + Insights | Existing visuals + written recommendations | Every recommendation traceable to a field in the verified 43-column schema |

## 4. Key Design Constraints

- Non-destructive to the existing Power BI dashboard layout
- No fabricated columns. If a KPI can't be built from the real source fields, it goes in Future Enhancements, not into the model as a placeholder
- Every number shown anywhere must be reconcilable back to a single SQL view (formal testing lives in the `Testing/` folder)

## 5. Out of Scope (Architectural Consequences)

- No pay-equity statistical modeling (e.g., regression-adjusted pay-gap analysis) — descriptive compensation-vs-attrition views are in scope, inferential modeling is not
- No time-series or trend component of any kind — every visual in this architecture is a cross-sectional snapshot view, not a trend view, because no calendar date field exists in the source. This is a structural property of the design, not a missing feature
- No reconciliation against the legacy `CF_*` Power Pivot fields in the Excel workbook — those are frozen legacy artifacts

## 6. Folder Structure

```
Business/ · Architecture/ · Data/ · ETL/ · Analytics/
```

A `Testing/` folder (for KPI reconciliation docs) exists in the repository.
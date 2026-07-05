# Technical Requirements Document (TRD)

**Project:** HR Attrition & Workforce Analytics Platform

**Version:** 1.0

**Prepared By:** Shreya Kumari

**Document Type:** Technical Requirements Document

**Status:** Final

---

# 1. Purpose

This document defines the technical requirements, architecture, implementation standards, and system specifications for the HR Attrition & Workforce Analytics Platform.

The solution transforms raw HR employee records into business intelligence through an automated Python ETL pipeline, a SQL dimensional data warehouse, and interactive Power BI dashboards.

This document complements the Business Requirements Document (BRD) by describing how business requirements are implemented from a technical perspective.

---

# 2. System Overview

The platform consists of four major layers.

```
Raw Dataset

↓

Python ETL

↓

SQLite Data Warehouse

↓

Power BI Dashboard
```

The system performs:

- Automated data ingestion
- Data validation
- Data cleaning
- SQL dimensional modeling
- KPI generation
- Interactive visualization

---

# 3. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | Import the complete HR dataset without modifying the original source. |
| FR-02 | Validate data quality before processing. |
| FR-03 | Produce a cleaned analytics-ready dataset. |
| FR-04 | Build SQL Star Schema tables. |
| FR-05 | Generate reusable SQL KPI Views. |
| FR-06 | Ensure Power BI KPIs reconcile with SQL outputs. |
| FR-07 | Support interactive dashboard filtering. |
| FR-08 | Preserve raw source files throughout processing. |
| FR-09 | Log every transformation performed by the ETL pipeline. |
| FR-10 | Maintain deterministic processing for identical inputs. |

---

# 4. Non-Functional Requirements

| Category | Requirement |
|-----------|-------------|
| Performance | ETL completes successfully on the full dataset. |
| Reliability | Pipeline executes without data loss. |
| Scalability | Modular architecture supports future enhancements. |
| Maintainability | Configuration-driven implementation. |
| Portability | SQL scripts support SQLite and PostgreSQL. |
| Transparency | Every transformation is logged. |
| Reproducibility | Complete pipeline executes from a fresh clone. |

---

# 5. Technology Stack

| Layer | Technology |
|---------|------------|
| Programming | Python 3.11+ |
| Data Processing | Pandas, NumPy |
| Excel Processing | openpyxl |
| Database | SQLite |
| SQL | ANSI SQL |
| Dashboard | Microsoft Power BI |
| Version Control | Git & GitHub |
| Documentation | Markdown |
| Testing | pytest |

---

# 6. Data Sources

## Primary Dataset

| Attribute | Details |
|------------|---------|
| Dataset | IBM HR Analytics Employee Attrition |
| Records | 1,470 |
| Features | 43 |
| Format | Excel |
| PII | None |

Primary input:

```
Analytics/Excel/HR DATA_Excel.xlsx
```

The ETL pipeline always reads from this file.

---

## Legacy Dataset

```
Data/raw/hrdata.csv
```

This file exists only for backward compatibility with legacy dashboards.

It is **never modified** by the ETL pipeline.

---

# 7. Identifier Strategy

Three identifier fields exist across the source files.

| Field | Purpose |
|---------|---------|
| Employee Number | Primary Key |
| emp no | Human-readable employee label |
| emp_no | Legacy row-order identifier |

### Design Decision

The new analytics platform adopts **Employee Number** as the canonical primary key.

Legacy identifiers are retained only for historical compatibility and are not used within the dimensional model.

---
# 8. Source Data Schema

The HR Analytics dataset contains employee demographic, employment, compensation, satisfaction, and workforce information used throughout the analytics pipeline.

## Dataset Summary

| Attribute | Value |
|------------|------:|
| Total Records | 1,470 |
| Employee Attributes | 43 |
| Dataset Type | Structured HR Dataset |
| Missing Values | None |
| Primary Identifier | Employee Number |

---

## Core Employee Attributes

| Category | Fields |
|-----------|--------|
| Employee | Employee Number, Age, Gender, Marital Status |
| Organization | Department, Job Role, Job Level |
| Compensation | Monthly Income, Daily Rate, Hourly Rate, Monthly Rate |
| Employment | Total Working Years, Years At Company, Years In Current Role |
| Satisfaction | Job Satisfaction, Environment Satisfaction, Relationship Satisfaction, Work Life Balance |
| Performance | Performance Rating, Percent Salary Hike |
| Workforce | Business Travel, Distance From Home, Over Time |
| Education | Education, Education Field |
| Benefits | Stock Option Level |
| Attrition | Attrition |

---

## Removed During Data Cleaning

The following columns are profiled and removed because they provide no analytical value.

| Column | Reason |
|----------|--------|
| Employee Count | Constant value |
| Over18 | Constant value |
| Standard Hours | Constant value |
| -2 | Undocumented constant field |
| 0 | Undocumented constant field |

These columns are removed during ETL and are fully documented within pipeline logs.

---

# 9. ETL Requirements

The ETL pipeline transforms raw HR data into an analytics-ready dataset suitable for SQL reporting and Power BI visualization.

---

## Extract

The extraction layer:

- Reads the original Excel workbook.
- Preserves the raw dataset.
- Validates schema consistency.
- Loads data into memory for preprocessing.

Source:

```
Analytics/Excel/HR DATA_Excel.xlsx
```

---

## Transform

Transformation includes:

- Missing value validation
- Duplicate detection
- Constant column identification
- Invalid record detection
- Column standardization
- Data type validation
- Feature preparation
- Snake_case conversion

No business information is inferred during transformation.

---

## Load

The processed dataset is exported to:

```
Data/processed/
```

The cleaned dataset is then loaded into SQLite where the dimensional warehouse is created.

---

# 10. Data Validation Rules

The pipeline validates every dataset before loading.

| Validation | Rule |
|------------|------|
| Employee Number | Unique |
| Age | 16–75 |
| Satisfaction Scores | 1–4 |
| Education Level | 1–5 |
| Attrition | Yes / No |
| Employee Count | Constant |
| Stock Option Level | 0–3 |
| Performance Rating | Valid Scale |

Pipeline execution stops immediately if validation fails.

---

# 11. Data Cleaning Strategy

The cleaning process follows deterministic rules to ensure reproducibility.

### Standardization

- Convert column names to snake_case
- Remove unnecessary whitespace
- Normalize categorical values

---

### Column Removal

Columns with zero analytical value are removed.

Examples include:

- Employee Count
- Over18
- Standard Hours

---

### Data Integrity

The pipeline never:

- modifies source files
- fabricates values
- silently removes records
- ignores validation failures

---

### Logging

Every transformation is recorded including:

- Timestamp
- Rows processed
- Columns removed
- Validation status
- Errors
- Processing duration

---

# 12. Data Modeling Requirements

The analytics platform implements a dimensional Star Schema.

---

## Fact Table

### Fact_Employee

Stores workforce metrics and employee measures.

Example attributes include:

- employee_number
- department_key
- job_role_key
- education_key
- marital_status_key
- age
- gender
- monthly_income
- attrition
- years_at_company
- total_working_years
- job_satisfaction
- work_life_balance
- environment_satisfaction
- performance_rating
- over_time
- stock_option_level

---

## Dimension Tables

| Dimension | Description |
|------------|-------------|
| Dim_Department | Department information |
| Dim_JobRole | Employee job roles |
| Dim_Education | Education level & field |
| Dim_MaritalStatus | Marital status |
| Dim_BusinessTravel | Travel frequency |

---

## Design Principles

The Star Schema is designed to:

- Reduce query complexity.
- Improve dashboard performance.
- Enable reusable SQL views.
- Support scalable reporting.
- Simplify Power BI relationships.

---

## Design Decisions

### No Date Dimension

The dataset contains no calendar dates.

Therefore:

- No Date Dimension exists.
- No Time Intelligence calculations are implemented.
- Tenure remains a descriptive employee attribute rather than a date hierarchy.

---

### Age Bands

Age bands are generated during ETL using documented business rules.

They are not stored within the original dataset.

---

# 13. SQL Layer

The SQL layer serves as the analytical foundation of the platform. It transforms the cleaned HR dataset into a dimensional data warehouse and provides reusable SQL views for reporting and dashboard consumption.

---

## SQL Components

| Component | Purpose |
|-----------|---------|
| `schema.sql` | Creates the dimensional database schema |
| `load.sql` | Loads processed data into staging and fact/dimension tables |
| `views.sql` | Creates reusable analytical SQL views |
| `kpi_queries.sql` | Calculates workforce KPIs |
| `department_analysis.sql` | Department-level workforce analysis |
| `attrition_deep_dive.sql` | Detailed employee attrition analysis |

---

## SQL Responsibilities

The SQL layer is responsible for:

- Building the Star Schema
- Creating Fact and Dimension tables
- Loading cleaned employee data
- Generating reusable business KPIs
- Supporting Power BI reporting
- Maintaining a single source of truth for analytical calculations

---

## SQL Design Principles

- Explicit SQL queries
- Readable Common Table Expressions (CTEs)
- Modular analytical views
- Reusable KPI calculations
- Standardized naming conventions

---

# 14. Python ETL Layer

Python automates the complete preprocessing workflow before data is loaded into the analytical database.

---

## ETL Responsibilities

The ETL pipeline performs:

- Data ingestion
- Data profiling
- Schema validation
- Data cleaning
- Feature preparation
- Data transformation
- Process logging
- Export to SQL staging

---

## Validation Rules

The pipeline validates:

- Employee Number uniqueness
- Age range (16–75)
- Satisfaction score limits
- Education scale (1–5)
- Performance Rating scale
- Employee Count consistency
- Constant-value columns
- Duplicate records

---

## Processing Rules

The ETL pipeline:

- Never modifies the original dataset.
- Never fabricates missing information.
- Removes only documented constant fields.
- Records every transformation.
- Produces deterministic output for identical inputs.

---

## Output

The ETL pipeline generates:

```
Processed Dataset

↓

SQLite Database

↓

Fact Tables

↓

Dimension Tables

↓

SQL Views
```

---

# 15. Power BI Layer

Power BI serves as the presentation layer of the analytics platform and provides interactive dashboards for workforce analysis.

---

## Dashboard Objectives

The dashboard enables HR stakeholders to:

- Monitor workforce KPIs
- Analyze employee attrition
- Explore workforce demographics
- Identify high-risk employee groups
- Support strategic HR decision-making

---

## Dashboard Pages

The report contains multiple analytical views, including:

- Executive Workforce Dashboard
- Education-Level Analysis
- Department Analysis
- Employee Demographics
- Attrition Analysis
- KPI Summary

---

## Dashboard Features

- Interactive slicers
- Dynamic KPI cards
- Cross-filtering
- Responsive visualizations
- Drill-down reporting
- Education-level filtering

---

## Key Measures

The dashboard includes measures such as:

- Employee Count
- Active Employees
- Attrition Count
- Attrition Rate
- Average Age
- Average Monthly Income
- Average Job Satisfaction
- Average Years at Company

---

## Validation

Dashboard KPIs are validated against the SQL analytical layer to ensure consistency between SQL outputs and Power BI visualizations.

---

# 16. Security

Although the dataset is synthetic and contains no Personally Identifiable Information (PII), enterprise development practices are followed.

Security measures include:

- Raw data is preserved as read-only.
- Sensitive configuration files are excluded using `.gitignore`.
- No credentials are stored in the repository.
- Pipeline operates only on local processed datasets.
- Source data remains unchanged throughout processing.

---

# 17. Error Handling

The platform follows a fail-fast strategy.

If unexpected conditions occur, execution stops immediately and provides descriptive error messages.

Examples include:

- Missing required columns
- Duplicate primary keys
- Invalid categorical values
- Invalid numerical ranges
- Schema mismatches
- File access failures

No silent failures are permitted.

---

# 18. Logging & Monitoring

Each pipeline execution records:

- Execution timestamp
- Input row count
- Output row count
- Processing duration
- Validation status
- Removed columns
- Transformation summary
- Error details (if applicable)

These logs improve reproducibility and simplify troubleshooting.

---
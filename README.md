# HR Workforce Analytics Platform

End-to-end workforce analytics platform that transforms raw HR data into actionable business insights through an automated Python ETL pipeline, SQL dimensional modeling, and interactive Power BI dashboards.

**Tech Stack:** Python • SQL • SQLite • Power BI • Excel • Pytest • GitHub Actions

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![SQLite](https://img.shields.io/badge/SQLite-3.40%2B-green)
![PowerBI](https://img.shields.io/badge/Power_BI-Desktop-red)
![Tests](https://img.shields.io/badge/Tests-65_Passed-success)
![Coverage](https://img.shields.io/badge/Coverage-80.9%25-success)
![CI](https://img.shields.io/badge/CI-GitHub_Actions-success)
![License](https://img.shields.io/badge/license-MIT-orange)

## Features

- Automated Python ETL pipeline with profiling and validation
- SQL star schema with governed KPI views
- Interactive Power BI dashboard
- KPI reconciliation against the raw source
- Unit and integration test suite (pytest)
- GitHub Actions CI on every push/PR
- Full technical documentation (BRD, TRD, HLD, LLD, data architecture)

## Data Source

[IBM HR Analytics Employee Attrition dataset](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) (1,470 employees, synthetic — no real PII). Uses the full 43-column version of the dataset.

## Pipeline

```
Analytics/Excel/HR DATA_Excel.xlsx ("Data" sheet, raw)
    → ETL/Python/data_cleaning.py   (profile, validate, drop junk/constant cols, rename, export)
    → Data/processed/hrdata_clean.csv
    → ETL/SQL/schema.sql             (star schema DDL)
    → ETL/SQL/load.sql               (staging → dimensions → Fact_Employee)
    → ETL/SQL/views.sql              (governed KPI views)
    → Power BI (imports from the same star schema)
```

## Key Findings

| KPI                           |                        Value |
|--------------------------------|------------------------------:|
| Employees                      |                         1,470 |
| Overall Attrition Rate         |                         16.1% |
| Highest-Risk Role              | Sales Representative (39.8%) |
| Highest-Risk Department        |            Sales (20.6%) |
| Overtime Attrition             |                         30.5% |
| Non-Overtime Attrition         |                         10.4% |
| Avg. Monthly Income (Leavers)  |                        $4,787 |
| Avg. Monthly Income (Stayers)  |                        $6,833 |
| Avg. Tenure (Leavers)          |                    5.1 years |
| Avg. Tenure (Stayers)          |                    7.4 years |

**Overtime is the strongest single attrition signal** — employees working overtime leave at roughly 3x the rate of those who don't.

Full KPI definitions and reconciliation queries live in `ETL/SQL/kpi_queries.sql`, `department_analysis.sql`, and `attrition_deep_dive.sql`.

## Quality Assurance

| Metric        | Status         |
|----------------|---------------|
| Unit Tests     | ✅ 65 Passed  |
| Test Coverage  | ✅ 80.9%      |
| Black          | ✅ Passed     |
| isort          | ✅ Passed     |
| flake8         | ✅ Passed     |
| mypy           | ✅ Passed     |
| CI Pipeline    | ✅ Passing    |

## Tech Stack

**Data Engineering:** Python, Pandas, SQLite
**Analytics:** SQL, Power BI, Excel
**Engineering:** Pytest, GitHub Actions, Black, isort, flake8, mypy, pre-commit

## Project Structure

```
Analytics/      Excel workbook + dashboard, Power BI .pbix, Tableau
Architecture/   HLD, LLD, DataArchitecture, system diagram
Business/       BRD, TRD, insights and recommendations
Data/raw/       Legacy 15-column extract (untouched, read only by pre-existing dashboards)
Data/processed/ Output of the Python cleaning pipeline (generated, not committed)
ETL/Python/     data_cleaning.py, run_sql_pipeline.py, utils/config.py
ETL/SQL/        schema.sql, load.sql, views.sql, kpi_queries.sql, department_analysis.sql, attrition_deep_dive.sql
Testing/        KPI reconciliation documentation
tests/          Automated test suite (pytest)
```

## Local Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run pipeline
python ETL/Python/data_cleaning.py
python ETL/Python/run_sql_pipeline.py
```

`run_sql_pipeline.py` builds a local SQLite database (`ETL/SQL/hr_analytics.db`) so the SQL layer can be tested independently of Power BI.

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=ETL --cov-report=html

# Run specific test file
pytest tests/unit/test_data_cleaning.py -v
```

## Code Quality

| Tool       | Purpose                    |
|------------|-----------------------------|
| Black      | Code formatting             |
| isort      | Import sorting              |
| flake8     | Style enforcement           |
| mypy       | Static type checking        |
| pytest     | Unit & integration testing  |
| pre-commit | Automated pre-commit checks |

```bash
# Format code
black ETL/ tests/

# Sort imports
isort ETL/ tests/

# Lint
flake8 ETL/

# Type check
mypy ETL/
```

## Continuous Integration

Every push and pull request automatically runs:

- Unit and integration tests
- Coverage validation
- Code formatting checks (Black, isort)
- Static analysis (flake8, mypy)

## Data Notes

- 1,470 employees, 44 raw columns (43 fields + a cosmetic `emp no` label)
- No calendar date field exists in the source (no hire/termination date) — every KPI is a cross-sectional snapshot, not a time series
- The 6 legacy Excel Power Pivot calculated fields (`CF_*`) are documented but not used in the pipeline — `Attrition` is the sole canonical flag
- Full technical rationale and identifier resolution live in `Business/TRD.md`

## Documentation

| Document | Coverage |
|----------|----------|
| `Business/BRD.md` | Business problem, KPIs, scope, assumptions, sign-off |
| `Business/TRD.md` | Technical requirements, verified schema, identifier resolution |
| `Architecture/HLD.md` | Component-level system design |
| `Architecture/LLD.md` | Detailed data flow, sequence, error handling |
| `Architecture/DataArchitecture.md` | Star schema, fact/dimension design, lineage |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding standards, and pull request process.

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting and security best practices.

## License

MIT License — see [LICENSE](LICENSE) file.

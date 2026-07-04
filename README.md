# HR Attrition & Workforce Analytics

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![SQLite](https://img.shields.io/badge/SQLite-3.40%2B-green)
![PowerBI](https://img.shields.io/badge/Power_BI-Desktop-red)
![License](https://img.shields.io/badge/license-MIT-orange)

End-to-end HR analytics pipeline: raw Excel source → validated Python cleaning pipeline → SQL star schema with KPI views → Power BI dashboard.

## Data Source

[IBM HR Analytics Employee Attrition dataset](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) (1,470 employees, synthetic — no real PII). Uses the full 43-column version of the dataset.

## Repository Structure

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

### Local Setup

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

## Data Characteristics

- 1,470 employees, 44 raw columns (43 fields + a cosmetic `emp no` label)
- Compensation fields (`monthly_income`, `daily_rate`, `hourly_rate`, `monthly_rate`), tenure fields (`years_at_company`, `years_since_last_promotion`, etc.), and overtime status are modeled in `Fact_Employee`
- No calendar date field exists in the source (no hire/termination date) — every KPI and visual is a cross-sectional snapshot
- The 6 legacy Excel Power Pivot calculated fields (`CF_*`) are documented but not read or reconciled against — `Attrition` is the sole canonical flag

## Key Findings

From the SQL KPI views, reconciled against the pipeline:

- **Overall attrition: 16.1%** (237 of 1,470 employees)
- **Overtime is the strongest single attrition signal**: 30.5% attrition for employees working overtime vs. 10.4% for those who aren't — a 3x gap
- **Sales Representative is the highest-risk role**: 39.8% attrition
- **Leavers earn less and stay less long**: avg. monthly income $4,787 vs. $6,833 for stayers; avg. tenure 5.1 vs. 7.4 years
- **Department attrition ranks**: Sales (20.6%) > HR (19.1%) > R&D (13.8%)

Full KPI definitions and reconciliation queries live in `ETL/SQL/kpi_queries.sql`, `department_analysis.sql`, and `attrition_deep_dive.sql`.

## Design Documents

| Document | Coverage |
|----------|----------|
| `Business/BRD.md` | Business problem, KPIs, scope, assumptions, sign-off |
| `Business/TRD.md` | Technical requirements, verified schema, identifier resolution |
| `Architecture/HLD.md` | Component-level system design |
| `Architecture/LLD.md` | Detailed data flow, sequence, error handling |
| `Architecture/DataArchitecture.md` | Star schema, fact/dimension design, lineage |

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

Automated quality checks:

- **Black** for code formatting (line length: 100)
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking
- **pre-commit hooks** for automated checks before commits
- **pytest** for testing with 80%+ coverage requirement

Run quality checks:

```bash
# Format code
black ETL/ tests/

# Sort imports
isort ETL/ tests/

# Lint
flake8 ETL/ tests/

# Type check
mypy ETL/
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding standards, and pull request process.

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting and security best practices.

## License

MIT License — see [LICENSE](LICENSE) file
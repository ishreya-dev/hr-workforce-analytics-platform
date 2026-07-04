import os
from pathlib import Path

# Repo root = four levels up from this file
# (ETL/Python/utils/config.py -> Python -> ETL -> repo root)
REPO_ROOT = Path(__file__).resolve().parents[3]

# Environment mode
ENV: str = os.getenv("ENV", "development")

# --- Source (read-only, never modified) ---
# Support environment variable overrides for deployment flexibility
RAW_WORKBOOK_PATH: Path = Path(
    os.getenv("RAW_WORKBOOK_PATH", str(REPO_ROOT / "Analytics" / "Excel" / "HR DATA_Excel.xlsx"))
)
RAW_SHEET_NAME: str = os.getenv("RAW_SHEET_NAME", "Data")

# Legacy artifact — referenced ONLY for documentation/awareness. Never read,
# never written, never joined against. The existing dashboards own this file.
LEGACY_HRDATA_CSV_PATH: Path = REPO_ROOT / "Data" / "raw" / "hrdata.csv"

# --- Pipeline outputs ---
# Support environment variable overrides for deployment flexibility
PROCESSED_DIR: Path = REPO_ROOT / "Data" / "processed"
PROCESSED_DATA_PATH: Path = Path(
    os.getenv("PROCESSED_DATA_PATH", str(PROCESSED_DIR / "hrdata_clean.csv"))
)
LOG_DIR: Path = Path(os.getenv("LOG_DIR", str(REPO_ROOT / "ETL" / "Python" / "logs")))

# Hard constraint (BRD Section 5 / TRD FR6): this pipeline must never write
# to RAW_WORKBOOK_PATH or LEGACY_HRDATA_CSV_PATH under any circumstance.
assert (
    RAW_WORKBOOK_PATH.resolve() != PROCESSED_DATA_PATH.resolve()
), "Raw and processed paths must never collide."
assert (
    LEGACY_HRDATA_CSV_PATH.resolve() != PROCESSED_DATA_PATH.resolve()
), "Legacy and processed paths must never collide."


# --- Validation constants (must be defined before validate_config() is called) ---
AGE_MIN, AGE_MAX = 16, 75
SCALE_1_4_MIN, SCALE_1_4_MAX = 1, 4
JOB_LEVEL_MIN, JOB_LEVEL_MAX = 1, 5
STOCK_OPTION_MIN, STOCK_OPTION_MAX = 0, 3
PERFORMANCE_RATING_MIN, PERFORMANCE_RATING_MAX = 1, 4


def _validate_env() -> None:
    """Validate environment configuration."""
    valid_envs = ["development", "staging", "production", "test"]
    if ENV not in valid_envs:
        raise ValueError(f"Invalid ENV '{ENV}'. Must be one of: {', '.join(valid_envs)}")


def _validate_paths() -> None:
    """Validate and create required directories."""
    if not RAW_WORKBOOK_PATH.parent.exists():
        raise ValueError(
            f"RAW_WORKBOOK_PATH parent directory does not exist: "
            f"{RAW_WORKBOOK_PATH.parent}"
        )

    # Ensure PROCESSED_DIR exists (will be created during pipeline execution)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Ensure LOG_DIR exists (will be created during pipeline execution)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _get_config_range(env_var: str, default: int) -> int:
    """Get numeric range value from environment or default."""
    return int(os.getenv(env_var, default))


def _validate_range(name: str, config_min: int, config_max: int, default_min: int, default_max: int) -> None:
    """Validate that a numeric range is valid (min < max)."""
    if config_min >= config_max:
        raise ValueError(
            f"{name} ({config_min}) must be less than {name.replace('_MIN', '_MAX')} ({config_max})"
        )
    if default_min >= default_max:
        raise ValueError(
            f"{name.replace('_MIN', '')}({default_min}) must be less than "
            f"{name.replace('_MIN', '')}({default_max})"
        )


def _validate_numeric_ranges() -> None:
    """Validate all numeric configuration ranges."""
    # Get configurable ranges from environment
    config_age_min = _get_config_range("AGE_MIN", AGE_MIN)
    config_age_max = _get_config_range("AGE_MAX", AGE_MAX)
    config_scale_min = _get_config_range("SCALE_1_4_MIN", SCALE_1_4_MIN)
    config_scale_max = _get_config_range("SCALE_1_4_MAX", SCALE_1_4_MAX)
    config_job_level_min = _get_config_range("JOB_LEVEL_MIN", JOB_LEVEL_MIN)
    config_job_level_max = _get_config_range("JOB_LEVEL_MAX", JOB_LEVEL_MAX)
    config_stock_min = _get_config_range("STOCK_OPTION_MIN", STOCK_OPTION_MIN)
    config_stock_max = _get_config_range("STOCK_OPTION_MAX", STOCK_OPTION_MAX)
    config_perf_min = _get_config_range("PERFORMANCE_RATING_MIN", PERFORMANCE_RATING_MIN)
    config_perf_max = _get_config_range("PERFORMANCE_RATING_MAX", PERFORMANCE_RATING_MAX)

    # Validate each range
    _validate_range("AGE_MIN", config_age_min, config_age_max, AGE_MIN, AGE_MAX)
    _validate_range("SCALE_1_4_MIN", config_scale_min, config_scale_max, SCALE_1_4_MIN, SCALE_1_4_MAX)
    _validate_range("JOB_LEVEL_MIN", config_job_level_min, config_job_level_max, JOB_LEVEL_MIN, JOB_LEVEL_MAX)
    _validate_range("STOCK_OPTION_MIN", config_stock_min, config_stock_max, STOCK_OPTION_MIN, STOCK_OPTION_MAX)
    _validate_range("PERFORMANCE_RATING_MIN", config_perf_min, config_perf_max, PERFORMANCE_RATING_MIN, PERFORMANCE_RATING_MAX)


def validate_config() -> None:
    """
    Validate configuration on startup.

    Raises:
        ValueError: If configuration is invalid
    """
    _validate_env()
    _validate_paths()
    _validate_numeric_ranges()


# --- Expected raw schema (verified against the actual workbook — TRD Section 4.2) ---
# Title-case-with-spaces, exactly as they appear in the Excel header row.
EXPECTED_RAW_COLUMNS = [
    "Employee Number",
    "emp no",
    "Age",
    "Attrition",
    "Business Travel",
    "Daily Rate",
    "Department",
    "Distance From Home",
    "Education",
    "Education Field",
    "Employee Count",
    "Environment Satisfaction",
    "Gender",
    "Hourly Rate",
    "Job Involvement",
    "Job Level",
    "Job Role",
    "Job Satisfaction",
    "Marital Status",
    "Monthly Income",
    "Monthly Rate",
    "Num Companies Worked",
    "Over18",
    "Over Time",
    "Percent Salary Hike",
    "Performance Rating",
    "Relationship Satisfaction",
    "Standard Hours",
    "Stock Option Level",
    "Total Working Years",
    "Training Times Last Year",
    "Work Life Balance",
    "Years At Company",
    "Years In Current Role",
    "Years Since Last Promotion",
    "Years With Curr Manager",
    "-2",
    "0",
]

# Legacy Power Pivot calculated fields (TRD Section 4.2). Documented for
# awareness only — NEVER read by this pipeline, never cross-validated
# against (BRD Section 9 / TRD FR7 / LLD Section 4).
LEGACY_CALCULATED_FIELDS_NOT_USED = [
    "CF_age band",
    "CF_attrition label",
    "CF_attrition count",
    "CF_attrition counts",
    "CF_attrition rate",
    "CF_current Employee",
]

# Raw (Title Case With Spaces) -> cleaned (snake_case) column name mapping.
# Explicit, not assumed (v1.0 error item D). Columns dropped during cleaning
# are omitted here on purpose (see COLUMNS_TO_DROP) and not renamed.
COLUMN_RENAME_MAP = {
    "Employee Number": "employee_number",
    "Age": "age",
    "Attrition": "attrition",
    "Business Travel": "business_travel",
    "Daily Rate": "daily_rate",
    "Department": "department",
    "Distance From Home": "distance_from_home",
    "Education": "education",
    "Education Field": "education_field",
    "Environment Satisfaction": "environment_satisfaction",
    "Gender": "gender",
    "Hourly Rate": "hourly_rate",
    "Job Involvement": "job_involvement",
    "Job Level": "job_level",
    "Job Role": "job_role",
    "Job Satisfaction": "job_satisfaction",
    "Marital Status": "marital_status",
    "Monthly Income": "monthly_income",
    "Monthly Rate": "monthly_rate",
    "Num Companies Worked": "num_companies_worked",
    "Over Time": "over_time",
    "Percent Salary Hike": "percent_salary_hike",
    "Performance Rating": "performance_rating",
    "Relationship Satisfaction": "relationship_satisfaction",
    "Stock Option Level": "stock_option_level",
    "Total Working Years": "total_working_years",
    "Training Times Last Year": "training_times_last_year",
    "Work Life Balance": "work_life_balance",
    "Years At Company": "years_at_company",
    "Years In Current Role": "years_in_current_role",
    "Years Since Last Promotion": "years_since_last_promotion",
    "Years With Curr Manager": "years_with_curr_manager",
}

# Columns dropped during cleaning, with the reason logged for each.
# "Over18" and "Standard Hours" are profiled at runtime (validate_zero_variance_columns)
# and only actually dropped if the zero-variance assumption is confirmed on the
# live data — they are listed here as the *expected* outcome, not an unconditional drop.
COLUMNS_TO_DROP = {
    "Employee Count": (
        "constant across all rows (confirmed = 1, zero-variance, no analytical value)"
    ),
    "emp no": (
        "cosmetic 'STAFF-N' label derived from Employee Number; redundant once "
        "Employee Number is the key"
    ),
    "-2": (
        "unlabeled column, confirmed constant (-2) across all rows — "
        "undocumented placeholder/junk artifact"
    ),
    "0": (
        "unlabeled column, confirmed constant (0) across all rows — "
        "undocumented placeholder/junk artifact"
    ),
}
CONDITIONAL_DROP_CANDIDATES = {
    "Over18": (
        "expected near-constant ('Y' for all rows) — profiled at runtime, "
        "dropped only if confirmed zero-variance"
    ),
    "Standard Hours": (
        "expected near-constant (e.g. 80 for all rows) — profiled at runtime, "
        "dropped only if confirmed zero-variance"
    ),
}

# Validation domains
VALID_GENDER = {"Female", "Male"}
VALID_MARITAL_STATUS = {"Single", "Married", "Divorced"}
VALID_DEPARTMENT = {"Sales", "Research & Development", "R&D", "Human Resources", "HR"}
VALID_BUSINESS_TRAVEL = {"Non-Travel", "Travel_Rarely", "Travel_Frequently"}
VALID_ATTRITION = {"Yes", "No"}
VALID_OVER_TIME = {"Yes", "No"}

# Education is VERIFIED to already arrive as a text label in this workbook
# (e.g. "Bachelor's Degree", "High School") — NOT a raw 1-5 integer as
# originally assumed before testing against the real file. Confirmed by
# direct inspection: dtype is string, values are the 5 labels below.
# No numeric->label mapping is needed or applied.
VALID_EDUCATION = {
    "High School",
    "Associates Degree",
    "Bachelor's Degree",
    "Master's Degree",
    "Doctoral Degree",
}

# age_band is NOT a raw source field in the 43-column data (DataArchitecture
# Section 2.1) — it is recomputed here from `age` using documented bins,
# matching the band boundaries used in the legacy hrdata.csv extract for
# continuity, but generated fresh rather than trusted from any source file.
AGE_BAND_BINS = [0, 24, 34, 44, 54, 200]
AGE_BAND_LABELS = ["Under 25", "25 - 34", "35 - 44", "45 - 54", "Over 55"]


# Validate configuration on import (after all constants are defined)
# Note: validate_config() uses local variables for environment overrides,
# it does not modify the global constants defined above
validate_config()

"""
data_cleaning.py (v2.0)

Reads the full 43-column HR dataset from the Excel workbook's "Data" sheet,
validates it against the documented schema (Business/TRD.md Section 4.2),
drops confirmed-junk/constant columns with a logged reason, standardizes
column names to snake_case, recomputes age_band, and writes a cleaned CSV
to Data/processed/.

HARD CONSTRAINT (BRD Section 5 / TRD FR6 — non-destructive, unchanged from v1.0):
This script must NEVER write to or modify the raw workbook, and must NEVER
read, write, or reference the legacy Data/raw/hrdata.csv extract. The
existing Power BI and Tableau dashboards read their own sources directly and
must keep working unchanged. This script only ever reads the raw workbook
and writes to the processed CSV.

CHANGE LOG (v1.0 -> v2.0):
- Source switched from Data/raw/hrdata.csv (15 cols) to the Excel workbook's
  full "Data" sheet (43+ cols) — see TRD.md Section 0/4.
- No cross-validation against attrition/attrition_label/active_employee
  (those field names don't exist in the real source) or against the 6
  legacy CF_* Power Pivot fields — TRD FR7, LLD Section 4.
- age_band is recomputed from age rather than read as a raw column.
- Added type hints and input validation (PR-03)
- Added environment variable support (PR-02)
- Refactored for dependency injection: all paths and config passed as
  parameters (PR-04)

Usage:
    python data_cleaning.py
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

# Add repo root to sys.path when running as script for direct execution
if __name__ == "__main__":
    _repo_root = str(Path(__file__).resolve().parent.parent.parent)
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

from ETL.Python.utils.config import (
    AGE_BAND_BINS,
    AGE_BAND_LABELS,
    AGE_MAX,
    AGE_MIN,
    COLUMN_RENAME_MAP,
    COLUMNS_TO_DROP,
    CONDITIONAL_DROP_CANDIDATES,
    EXPECTED_RAW_COLUMNS,
    JOB_LEVEL_MAX,
    JOB_LEVEL_MIN,
    LEGACY_CALCULATED_FIELDS_NOT_USED,
    LEGACY_HRDATA_CSV_PATH,
    LOG_DIR,
    PERFORMANCE_RATING_MAX,
    PERFORMANCE_RATING_MIN,
    PROCESSED_DATA_PATH,
    PROCESSED_DIR,
    RAW_SHEET_NAME,
    RAW_WORKBOOK_PATH,
    SCALE_1_4_MAX,
    SCALE_1_4_MIN,
    STOCK_OPTION_MAX,
    STOCK_OPTION_MIN,
    VALID_ATTRITION,
    VALID_BUSINESS_TRAVEL,
    VALID_DEPARTMENT,
    VALID_EDUCATION,
    VALID_GENDER,
    VALID_MARITAL_STATUS,
    VALID_OVER_TIME,
)


def setup_logging(
    log_dir: Optional[Path] = None, logger_name: str = "hr_cleaning"
) -> logging.Logger:
    """
    Setup logging configuration for the pipeline.

    Args:
        log_dir: Directory for log files (defaults to LOG_DIR from config)
        logger_name: Name for the logger instance

    Returns:
        Configured logger instance with file and console handlers
    """
    if log_dir is None:
        log_dir = LOG_DIR

    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"cleaning_run_{datetime.now():%Y%m%d_%H%M%S}.log"

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    file_handler = logging.FileHandler(log_path)
    console_handler = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler.setFormatter(fmt)
    console_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(
        f"Reminder: legacy extract at {LEGACY_HRDATA_CSV_PATH} is never read or "
        "written by this script (BRD Section 5 / TRD FR6)."
    )
    return logger


def load_raw(
    logger: logging.Logger,
    raw_workbook_path: Optional[Path] = None,
    raw_sheet_name: Optional[str] = None,
) -> pd.DataFrame:
    """
    Load and validate the raw Excel workbook.

    Args:
        logger: Logger instance for pipeline logging
        raw_workbook_path: Path to Excel workbook (defaults to config value)
        raw_sheet_name: Sheet name to read (defaults to config value)

    Returns:
        Validated DataFrame with raw HR data

    Raises:
        FileNotFoundError: If workbook doesn't exist
        ValueError: If schema validation fails
    """
    if raw_workbook_path is None:
        raw_workbook_path = RAW_WORKBOOK_PATH
    if raw_sheet_name is None:
        raw_sheet_name = RAW_SHEET_NAME

    if not raw_workbook_path.exists():
        error_msg = f"Raw workbook not found at {raw_workbook_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    try:
        df = pd.read_excel(raw_workbook_path, sheet_name=raw_sheet_name, engine="openpyxl")
    except Exception as e:
        error_msg = f"Failed to read Excel file: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

    logger.info(
        f"Loaded raw workbook: {raw_workbook_path} [sheet={raw_sheet_name}] — "
        f"{len(df)} rows, {len(df.columns)} columns"
    )

    # Normalize column labels that may arrive as non-strings (e.g. the "-2"/"0"
    # junk headers can be read as ints by pandas) so schema comparison is reliable.
    df.columns = [str(c).strip() for c in df.columns]

    missing_cols = set(EXPECTED_RAW_COLUMNS) - set(df.columns)
    unexpected_cols = (
        set(df.columns) - set(EXPECTED_RAW_COLUMNS) - set(LEGACY_CALCULATED_FIELDS_NOT_USED)
    )

    if missing_cols:
        error_msg = f"Missing expected columns: {sorted(missing_cols)}"
        logger.error(error_msg)
        raise ValueError(
            f"Schema mismatch: raw workbook is missing expected columns {sorted(missing_cols)}. "
            "Halting rather than proceeding with a partial schema (TRD Section 11)."
        )
    if unexpected_cols:
        logger.warning(
            f"Unexpected columns found that are not in the documented schema: {sorted(unexpected_cols)}. "
            "This may indicate a workbook change — review Business/TRD.md Section 4.2 before proceeding."
        )

    present_legacy_fields = [c for c in LEGACY_CALCULATED_FIELDS_NOT_USED if c in df.columns]
    if present_legacy_fields:
        df = df.drop(columns=present_legacy_fields)
        logger.info(
            f"Dropped {len(present_legacy_fields)} legacy CF_* calculated fields from the "
            f"working frame (present in workbook but out of scope per TRD FR7): "
            f"{present_legacy_fields}"
        )
    return df


def validate_uniqueness(df: pd.DataFrame, logger: logging.Logger) -> None:
    """
    Validate that Employee Number is unique (one row per employee).

    Args:
        df: DataFrame to validate
        logger: Logger instance for logging results
    """
    dup_count = df["Employee Number"].duplicated().sum()
    if dup_count > 0:
        logger.warning(
            f"Found {dup_count} duplicate Employee Number values — grain assumption violated."
        )
    else:
        logger.info(
            f"Employee Number uniqueness check passed: "
            f"{df['Employee Number'].nunique()}/{len(df)} unique."
        )


def validate_constant_column(df: pd.DataFrame, col: str, logger: logging.Logger) -> bool:
    """
    Check if a column is constant (single unique value across all rows).

    Args:
        df: DataFrame to check
        col: Column name to validate
        logger: Logger instance for logging results

    Returns:
        True if column is constant, False otherwise
    """
    n_unique = df[col].nunique(dropna=False)
    if n_unique == 1:
        logger.info(
            f"'{col}' confirmed constant (single value: {df[col].iloc[0]!r}) across all rows."
        )
        return True
    logger.warning(
        f"'{col}' expected to be constant but found {n_unique} distinct values — "
        "NOT dropping; this assumption did not hold on this data and needs review."
    )
    return False


def validate_categorical_domains(df: pd.DataFrame, logger: logging.Logger) -> None:
    """
    Validate that categorical columns contain only expected values.

    Args:
        df: DataFrame to validate
        logger: Logger instance for logging results
    """
    checks = [
        ("Gender", VALID_GENDER),
        ("Marital Status", VALID_MARITAL_STATUS),
        ("Department", VALID_DEPARTMENT),
        ("Business Travel", VALID_BUSINESS_TRAVEL),
        ("Attrition", VALID_ATTRITION),
        ("Over Time", VALID_OVER_TIME),
        ("Education", VALID_EDUCATION),
    ]
    for col, valid_set in checks:
        found = set(df[col].dropna().unique())
        unexpected = found - valid_set
        if unexpected:
            logger.warning(
                f"Column '{col}' has unexpected values not in documented domain: {unexpected}"
            )
        else:
            logger.info(f"Domain check passed for '{col}': {sorted(found)}")


def validate_numeric_ranges(df: pd.DataFrame, logger: logging.Logger) -> None:
    """
    Validate that numeric columns fall within expected ranges.

    Args:
        df: DataFrame to validate
        logger: Logger instance for logging results
    """
    range_checks = [
        ("Age", AGE_MIN, AGE_MAX),
        ("Job Satisfaction", SCALE_1_4_MIN, SCALE_1_4_MAX),
        ("Environment Satisfaction", SCALE_1_4_MIN, SCALE_1_4_MAX),
        ("Relationship Satisfaction", SCALE_1_4_MIN, SCALE_1_4_MAX),
        ("Job Involvement", SCALE_1_4_MIN, SCALE_1_4_MAX),
        ("Work Life Balance", SCALE_1_4_MIN, SCALE_1_4_MAX),
        ("Performance Rating", PERFORMANCE_RATING_MIN, PERFORMANCE_RATING_MAX),
        ("Job Level", JOB_LEVEL_MIN, JOB_LEVEL_MAX),
        ("Stock Option Level", STOCK_OPTION_MIN, STOCK_OPTION_MAX),
    ]
    for col, lo, hi in range_checks:
        bad = df[(df[col] < lo) | (df[col] > hi)]
        if len(bad) > 0:
            logger.warning(
                f"{len(bad)} rows have '{col}' outside [{lo}, {hi}]: "
                f"Employee Number {bad['Employee Number'].tolist()}"
            )
        else:
            logger.info(f"'{col}' range check passed: all values within [{lo}, {hi}].")


def drop_columns(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    """
    Drop constant/junk columns with logged rationale.

    Args:
        df: DataFrame to process
        logger: Logger instance for logging results

    Returns:
        DataFrame with dropped columns removed
    """
    # Unconditional drops (already-verified constant/junk — TRD Section 4.2)
    for col, reason in COLUMNS_TO_DROP.items():
        if col in df.columns:
            df = df.drop(columns=[col])
            logger.info(f"Dropped column '{col}': {reason}")

    # Conditional drops — profile live data before dropping, don't assume
    for col, expected_reason in CONDITIONAL_DROP_CANDIDATES.items():
        if col in df.columns:
            if validate_constant_column(df, col, logger):
                df = df.drop(columns=[col])
                logger.info(f"Dropped column '{col}': {expected_reason}")
            else:
                logger.warning(
                    f"Retaining column '{col}' — zero-variance assumption did not hold; "
                    "review before treating it as a KPI input."
                )
    return df


def add_age_band(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    """
    Recompute age_and from Age using documented bin boundaries.

    Args:
        df: DataFrame to process
        logger: Logger instance for logging results

    Returns:
        DataFrame with age_band column added
    """
    df["age_band"] = pd.cut(
        df["Age"], bins=AGE_BAND_BINS, labels=AGE_BAND_LABELS, right=True
    )
    logger.info(
        f"Recomputed 'age_band' from 'Age' using bins {AGE_BAND_BINS} -> "
        f"{AGE_BAND_LABELS} (age_band is not a raw source field in the 43-column "
        "data — DataArchitecture.md Section 2.1)."
    )
    return df


def rename_columns(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    """
    Standardize column names from Title Case With Spaces to snake_case.

    Args:
        df: DataFrame to process
        logger: Logger instance for logging results

    Returns:
        DataFrame with renamed columns
    """
    applicable_map = {k: v for k, v in COLUMN_RENAME_MAP.items() if k in df.columns}
    df = df.rename(columns=applicable_map)
    logger.info(
        f"Renamed {len(applicable_map)} columns from 'Title Case With Spaces' to snake_case."
    )
    return df


def standardize_dtypes(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    """
    Standardize data types for optimal storage and performance.

    Args:
        df: DataFrame to process
        logger: Logger instance for logging results

    Returns:
        DataFrame with standardized dtypes
    """
    categorical_cols = [
        c
        for c in [
            "gender",
            "marital_status",
            "age_band",
            "department",
            "education",
            "education_field",
            "job_role",
            "business_travel",
            "attrition",
            "over_time",
        ]
        if c in df.columns
    ]
    for col in categorical_cols:
        df[col] = df[col].astype("category")

    integer_cols = [
        c
        for c in [
            "employee_number",
            "age",
            "daily_rate",
            "distance_from_home",
            "environment_satisfaction",
            "hourly_rate",
            "job_involvement",
            "job_level",
            "job_satisfaction",
            "monthly_income",
            "monthly_rate",
            "num_companies_worked",
            "percent_salary_hike",
            "performance_rating",
            "relationship_satisfaction",
            "stock_option_level",
            "total_working_years",
            "training_times_last_year",
            "work_life_balance",
            "years_at_company",
            "years_in_current_role",
            "years_since_last_promotion",
            "years_with_curr_manager",
        ]
        if c in df.columns
    ]
    for col in integer_cols:
        df[col] = df[col].astype("int64")

    logger.info(
        f"Standardized dtypes: {len(categorical_cols)} columns -> category, "
        f"{len(integer_cols)} columns -> int64."
    )
    return df


def export_clean(
    df: pd.DataFrame,
    logger: logging.Logger,
    processed_data_path: Optional[Path] = None,
    processed_dir: Optional[Path] = None,
) -> None:
    """
    Export cleaned DataFrame to CSV.

    Args:
        df: Cleaned DataFrame to export
        logger: Logger instance for logging results
        processed_data_path: Output CSV path (defaults to config value)
        processed_dir: Output directory (defaults to config value)
    """
    if processed_data_path is None:
        processed_data_path = PROCESSED_DATA_PATH
    if processed_dir is None:
        processed_dir = PROCESSED_DIR

    processed_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_data_path, index=False)
    logger.info(
        f"Exported cleaned dataset to {processed_data_path} — "
        f"{len(df)} rows, {len(df.columns)} columns."
    )
    logger.info(
        "Reminder (BRD Section 5 / TRD FR6): this file is additive only. "
        "The existing Power BI and Tableau dashboards remain pointed at their "
        f"original sources, including the untouched legacy extract at "
        f"{LEGACY_HRDATA_CSV_PATH}."
    )


def run_pipeline(
    raw_workbook_path: Optional[Path] = None,
    raw_sheet_name: Optional[str] = None,
    processed_data_path: Optional[Path] = None,
    processed_dir: Optional[Path] = None,
    log_dir: Optional[Path] = None,
    logger: Optional[logging.Logger] = None,
) -> Dict[str, Any]:
    """
    Run the complete data cleaning pipeline with dependency injection.

    Args:
        raw_workbook_path: Path to Excel workbook (defaults to config value)
        raw_sheet_name: Sheet name to read (defaults to config value)
        processed_data_path: Output CSV path (defaults to config value)
        processed_dir: Output directory (defaults to config value)
        log_dir: Log directory (defaults to config value)
        logger: Logger instance (defaults to creating a new one)

    Returns:
        Dictionary with pipeline results and metadata

    Raises:
        FileNotFoundError: If raw workbook doesn't exist
        ValueError: If schema validation fails
        RuntimeError: If Excel reading fails
    """
    if logger is None:
        logger = setup_logging(log_dir)

    logger.info("=== HR data cleaning pipeline run started (v2.0, full 43-column source) ===")

    row_count_in = None
    try:
        df = load_raw(logger, raw_workbook_path, raw_sheet_name)
        row_count_in = len(df)

        validate_uniqueness(df, logger)
        validate_categorical_domains(df, logger)
        validate_numeric_ranges(df, logger)

        df = drop_columns(df, logger)
        df = add_age_band(df, logger)
        df = rename_columns(df, logger)
        df = standardize_dtypes(df, logger)

        export_clean(df, logger, processed_data_path, processed_dir)

        row_count_out = len(df)
        logger.info(
            f"Row count reconciliation: in={row_count_in}, out={row_count_out}, "
            f"dropped_rows={row_count_in - row_count_out} (expected: 0 — no rows "
            "are ever dropped, only columns)."
        )
        logger.info("=== Pipeline run completed successfully ===")

        return {
            "success": True,
            "rows_in": row_count_in,
            "rows_out": row_count_out,
            "columns_out": len(df.columns),
            "processed_path": processed_data_path or PROCESSED_DATA_PATH,
        }

    except FileNotFoundError as e:
        logger.error(f"Input file not found: {e}")
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        raise
    except Exception as e:
        logger.exception("Unexpected pipeline failure")
        raise RuntimeError(f"Pipeline failed: {str(e)}") from e


def main() -> None:
    """
    Main pipeline execution function.

    Orchestrates the data cleaning pipeline:
    1. Setup logging
    2. Load raw data from Excel
    3. Validate data quality
    4. Clean and transform data
    5. Export cleaned data

    Raises:
        FileNotFoundError: If raw workbook doesn't exist
        ValueError: If schema validation fails
        RuntimeError: If Excel reading fails
    """
    run_pipeline()


if __name__ == "__main__":
    main()

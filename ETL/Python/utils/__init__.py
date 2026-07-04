"""
Utility modules for HR Attrition & Workforce Analytics ETL pipeline.

This package contains:
- config: Configuration management with environment variable support
- logger: Structured logging utilities
- exceptions: Custom exception hierarchy
- validators: Input validation functions
"""

from .config import (
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
    REPO_ROOT,
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

__version__ = "2.0.0"

__all__ = [
    # Config exports
    "REPO_ROOT",
    "RAW_WORKBOOK_PATH",
    "RAW_SHEET_NAME",
    "PROCESSED_DATA_PATH",
    "PROCESSED_DIR",
    "LOG_DIR",
    "LEGACY_HRDATA_CSV_PATH",
    "EXPECTED_RAW_COLUMNS",
    "LEGACY_CALCULATED_FIELDS_NOT_USED",
    "COLUMN_RENAME_MAP",
    "COLUMNS_TO_DROP",
    "CONDITIONAL_DROP_CANDIDATES",
    "VALID_GENDER",
    "VALID_MARITAL_STATUS",
    "VALID_DEPARTMENT",
    "VALID_BUSINESS_TRAVEL",
    "VALID_ATTRITION",
    "VALID_OVER_TIME",
    "VALID_EDUCATION",
    "AGE_MIN",
    "AGE_MAX",
    "SCALE_1_4_MIN",
    "SCALE_1_4_MAX",
    "JOB_LEVEL_MIN",
    "JOB_LEVEL_MAX",
    "STOCK_OPTION_MIN",
    "STOCK_OPTION_MAX",
    "PERFORMANCE_RATING_MIN",
    "PERFORMANCE_RATING_MAX",
    "AGE_BAND_BINS",
    "AGE_BAND_LABELS",
]

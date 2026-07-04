"""
run_sql_pipeline.py (v2.0)

Local dev harness for the SQL layer. SQLite has no portable SQL statement
for bulk-loading a CSV — so this script does that one non-portable step in
Python, then executes schema.sql -> load.sql -> views.sql exactly as
written, unmodified.

This builds hr_analytics.db in this folder for local testing/reconciliation
only. It reads Data/processed/hrdata_clean.csv (produced by data_cleaning.py
from the Excel source — never the legacy hrdata.csv) and never touches the
existing Power BI/Tableau dashboards (BRD Section 5 / TRD FR6).

CHANGE LOG (v1.0 -> v2.0): corrected REPO_ROOT depth and file names
(01_schema.sql -> schema.sql, etc. — no numeric prefixes anywhere in the
real repo tree); added attrition_deep_dive.sql to the run sequence now that
it's no longer an empty placeholder.
- Added environment variable support for configuration management (PR-02)
- Added type hints and improved error handling (PR-03)
- Refactored for dependency injection: all paths and config passed as
  parameters (PR-04)

Usage:
    python run_sql_pipeline.py
"""

import logging
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

# Add repo root to sys.path when running as script for direct execution
if __name__ == "__main__":
    _repo_root = str(Path(__file__).resolve().parent.parent.parent)
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

from ETL.Python.utils.config import (
    LOG_DIR,
    PROCESSED_DATA_PATH,
    REPO_ROOT,
)


def setup_logging(
    log_dir: Optional[Path] = None, logger_name: str = "sql_pipeline"
) -> logging.Logger:
    """
    Setup logging configuration for the SQL pipeline.

    Args:
        log_dir: Directory for log files (defaults to LOG_DIR from config)
        logger_name: Name for the logger instance

    Returns:
        Configured logger instance with file and console handlers
    """
    if log_dir is None:
        log_dir = LOG_DIR

    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "sql_pipeline.log"

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def run_sql_file(conn: sqlite3.Connection, path: Path, logger: logging.Logger) -> None:
    """
    Execute SQL script from file.

    Args:
        conn: SQLite connection
        path: Path to SQL file
        logger: Logger instance for logging results

    Raises:
        FileNotFoundError: If SQL file doesn't exist
        sqlite3.Error: If SQL execution fails
    """
    if not path.exists():
        error_msg = f"Expected SQL file not found: {path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    try:
        with open(path, "r") as f:
            sql_content = f.read()
        conn.executescript(sql_content)
        logger.info(f"Executed SQL script: {path.name}")
    except sqlite3.Error as e:
        error_msg = f"Failed to execute SQL script {path.name}: {e}"
        logger.error(error_msg)
        raise


def run_sql_pipeline(
    processed_data_path: Optional[Path] = None,
    db_path: Optional[Path] = None,
    sql_dir: Optional[Path] = None,
    log_dir: Optional[Path] = None,
    logger: Optional[logging.Logger] = None,
) -> Dict[str, Any]:
    """
    Run the complete SQL pipeline with dependency injection.

    Args:
        processed_data_path: Path to cleaned CSV (defaults to config value)
        db_path: Path to output SQLite database (defaults to ETL/SQL/hr_analytics.db)
        sql_dir: Directory containing SQL scripts (defaults to ETL/SQL/)
        log_dir: Directory for log files (defaults to config value)
        logger: Logger instance (defaults to creating a new one)

    Returns:
        Dictionary with pipeline results and metadata

    Raises:
        FileNotFoundError: If required files don't exist
        sqlite3.Error: If database operations fail
        RuntimeError: If pipeline execution fails
    """
    # Set defaults from config if not provided
    if processed_data_path is None:
        processed_data_path = PROCESSED_DATA_PATH
    if db_path is None:
        db_path = REPO_ROOT / "ETL" / "SQL" / "hr_analytics.db"
    if sql_dir is None:
        sql_dir = REPO_ROOT / "ETL" / "SQL"
    if logger is None:
        logger = setup_logging(log_dir)

    logger.info("=== SQL pipeline run started ===")

    # Validate inputs
    if not processed_data_path.exists():
        error_msg = f"{processed_data_path} not found — " "run ETL/Python/data_cleaning.py first."
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    if db_path.exists():
        db_path.unlink()
        logger.info(f"Removed existing database: {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        # 1. Schema (DDL) — creates staging + dimension + fact tables
        logger.info("Creating database schema...")
        run_sql_file(conn, sql_dir / "schema.sql", logger)

        # 2. Load staging (the one non-portable, driver-specific step)
        logger.info(f"Loading data from {processed_data_path}...")
        try:
            df = pd.read_csv(processed_data_path)
            df.to_sql("staging_employee", conn, if_exists="append", index=False)
            logger.info(f"Loaded {len(df)} rows into staging_employee")
        except Exception as e:
            error_msg = f"Failed to load CSV data: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

        # 3. Populate dimensions + fact from staging (pure, portable SQL)
        logger.info("Populating dimension and fact tables...")
        run_sql_file(conn, sql_dir / "load.sql", logger)

        # 4. Create governed views
        logger.info("Creating KPI views...")
        run_sql_file(conn, sql_dir / "views.sql", logger)

        # Commit transaction
        conn.commit()
        logger.info("Transaction committed successfully")

        # Row-count reconciliation check
        staging_count = conn.execute("SELECT COUNT(*) FROM staging_employee").fetchone()[0]
        fact_count = conn.execute("SELECT COUNT(*) FROM Fact_Employee").fetchone()[0]
        match = staging_count == fact_count

        logger.info(
            f"Row-count reconciliation: staging={staging_count}, fact={fact_count}, "
            f"match={match}"
        )

        if not match:
            logger.warning("Row count mismatch between staging and fact table!")

        # Display view results (optional - don't fail if views don't exist)
        for view in [
            "vw_attrition_rate",
            "vw_department_summary",
            "vw_satisfaction_summary",
            "vw_compensation_summary",
            "vw_tenure_summary",
        ]:
            try:
                logger.info(f"\n--- {view} ---")
                for row in conn.execute(f"SELECT * FROM {view}"):
                    logger.info(f"  {row}")
            except sqlite3.OperationalError:
                logger.debug(f"View {view} not found or not accessible - skipping display")

        logger.info(f"\nDatabase built at {db_path}")
        logger.info("=== SQL pipeline run completed successfully ===")

        return {
            "success": True,
            "db_path": db_path,
            "staging_count": staging_count,
            "fact_count": fact_count,
            "row_count_match": match,
        }

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
        raise RuntimeError(f"Database operation failed: {e}") from e
    except Exception as e:
        logger.exception("Unexpected pipeline failure")
        conn.rollback()
        raise RuntimeError(f"Pipeline failed: {str(e)}") from e
    finally:
        conn.close()
        logger.info("Database connection closed")


def main() -> None:
    """
    Main pipeline execution function.

    Orchestrates the SQL pipeline:
    1. Validate inputs
    2. Create database schema
    3. Load data from CSV to staging
    4. Populate dimensions and fact tables
    5. Create views
    6. Verify results

    Raises:
        FileNotFoundError: If required files don't exist
        sqlite3.Error: If database operations fail
        RuntimeError: If pipeline execution fails
    """
    run_sql_pipeline()


if __name__ == "__main__":
    main()

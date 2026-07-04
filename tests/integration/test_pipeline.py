"""
Integration tests for the complete ETL pipeline.

Tests end-to-end functionality including:
- Full pipeline execution
- Data flow between components
- Database creation and population
- KPI view generation
"""

import logging
import sqlite3
from pathlib import Path

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_workbook(tmp_path: Path, sample_employee_data: pd.DataFrame) -> Path:
    """
    Create a temporary Excel workbook for testing.

    Args:
        tmp_path: Pytest temporary directory fixture
        sample_employee_data: Sample DataFrame to write

    Returns:
        Path to temporary Excel workbook
    """
    workbook_path = tmp_path / "test_hr_data.xlsx"
    sample_employee_data.to_excel(workbook_path, sheet_name="Data", index=False)
    return workbook_path


@pytest.fixture
def temp_processed_csv(tmp_path: Path, sample_clean_data: pd.DataFrame) -> Path:
    """
    Create a temporary processed CSV for SQL pipeline testing.

    Args:
        tmp_path: Pytest temporary directory fixture
        sample_clean_data: Clean DataFrame to write

    Returns:
        Path to temporary CSV file
    """
    csv_path = tmp_path / "hrdata_clean.csv"
    sample_clean_data.to_csv(csv_path, index=False)
    return csv_path


# ---------------------------------------------------------------------------
# Test Full Pipeline Execution
# ---------------------------------------------------------------------------


class TestFullPipeline:
    """Tests for complete ETL pipeline execution."""

    def test_pipeline_creates_processed_csv(
        self, temp_workbook: Path, tmp_path: Path, test_logger: logging.Logger
    ) -> None:
        """Test that pipeline creates processed CSV file."""
        from ETL.Python.data_cleaning import run_pipeline

        output_path = tmp_path / "hrdata_clean.csv"

        # Run pipeline with explicit paths
        result = run_pipeline(
            raw_workbook_path=temp_workbook,
            processed_data_path=output_path,
            log_dir=tmp_path / "logs",
            logger=test_logger,
        )

        # Verify output file exists
        assert output_path.exists()
        assert result["success"] is True

    def test_pipeline_preserves_row_count(
        self,
        temp_workbook: Path,
        tmp_path: Path,
        test_logger: logging.Logger,
        sample_employee_data: pd.DataFrame,
    ) -> None:
        """Test that pipeline preserves all rows (no row drops)."""
        from ETL.Python.data_cleaning import run_pipeline

        output_path = tmp_path / "hrdata_clean.csv"

        # Run pipeline with explicit paths
        run_pipeline(
            raw_workbook_path=temp_workbook,
            processed_data_path=output_path,
            log_dir=tmp_path / "logs",
            logger=test_logger,
        )

        # Verify row count
        output_df = pd.read_csv(output_path)
        assert len(output_df) == len(sample_employee_data)

    def test_pipeline_drops_constant_columns(
        self, temp_workbook: Path, tmp_path: Path, test_logger: logging.Logger
    ) -> None:
        """Test that pipeline drops constant columns."""
        from ETL.Python.data_cleaning import run_pipeline

        output_path = tmp_path / "hrdata_clean.csv"

        # Run pipeline with explicit paths
        run_pipeline(
            raw_workbook_path=temp_workbook,
            processed_data_path=output_path,
            log_dir=tmp_path / "logs",
            logger=test_logger,
        )

        # Verify constant columns are dropped
        output_df = pd.read_csv(output_path)
        assert "Employee Count" not in output_df.columns
        assert "emp no" not in output_df.columns
        assert "-2" not in output_df.columns
        assert "0" not in output_df.columns

    def test_pipeline_renames_columns(
        self, temp_workbook: Path, tmp_path: Path, test_logger: logging.Logger
    ) -> None:
        """Test that pipeline renames columns to snake_case."""
        from ETL.Python.data_cleaning import run_pipeline

        output_path = tmp_path / "hrdata_clean.csv"

        # Run pipeline with explicit paths
        run_pipeline(
            raw_workbook_path=temp_workbook,
            processed_data_path=output_path,
            log_dir=tmp_path / "logs",
            logger=test_logger,
        )

        # Verify columns are renamed
        output_df = pd.read_csv(output_path)
        assert "employee_number" in output_df.columns
        assert "business_travel" in output_df.columns
        assert "Employee Number" not in output_df.columns


# ---------------------------------------------------------------------------
# Test SQL Pipeline
# ---------------------------------------------------------------------------


class TestSQLPipeline:
    """Tests for SQL pipeline execution."""

    def test_sql_pipeline_creates_database(
        self, temp_processed_csv: Path, tmp_path: Path, test_logger: logging.Logger
    ) -> None:
        """Test that SQL pipeline creates SQLite database."""
        from ETL.Python.run_sql_pipeline import run_sql_pipeline

        db_path = tmp_path / "hr_analytics.db"

        # Run SQL pipeline with explicit paths
        result = run_sql_pipeline(
            processed_data_path=temp_processed_csv,
            db_path=db_path,
            sql_dir=Path(__file__).parent.parent.parent / "ETL" / "SQL",
            log_dir=tmp_path / "logs",
            logger=test_logger,
        )

        # Verify database exists
        assert db_path.exists()
        assert result["success"] is True

    def test_sql_pipeline_creates_tables(
        self, temp_processed_csv: Path, tmp_path: Path, test_logger: logging.Logger
    ) -> None:
        """Test that SQL pipeline creates all required tables."""
        from ETL.Python.run_sql_pipeline import run_sql_pipeline

        db_path = tmp_path / "hr_analytics.db"

        # Run SQL pipeline with explicit paths
        run_sql_pipeline(
            processed_data_path=temp_processed_csv,
            db_path=db_path,
            sql_dir=Path(__file__).parent.parent.parent / "ETL" / "SQL",
            log_dir=tmp_path / "logs",
            logger=test_logger,
        )

        # Verify tables exist
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check for required tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        assert "staging_employee" in tables
        assert "Fact_Employee" in tables
        assert "Dim_Department" in tables
        assert "Dim_JobRole" in tables
        assert "Dim_Education" in tables
        assert "Dim_MaritalStatus" in tables

        conn.close()

    def test_sql_pipeline_creates_views(
        self, temp_processed_csv: Path, tmp_path: Path, test_logger: logging.Logger
    ) -> None:
        """Test that SQL pipeline creates all KPI views."""
        from ETL.Python.run_sql_pipeline import run_sql_pipeline

        db_path = tmp_path / "hr_analytics.db"

        # Run SQL pipeline with explicit paths
        run_sql_pipeline(
            processed_data_path=temp_processed_csv,
            db_path=db_path,
            sql_dir=Path(__file__).parent.parent.parent / "ETL" / "SQL",
            log_dir=tmp_path / "logs",
            logger=test_logger,
        )

        # Verify views exist
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        views = [row[0] for row in cursor.fetchall()]

        assert "vw_attrition_rate" in views
        assert "vw_department_summary" in views
        assert "vw_satisfaction_summary" in views
        assert "vw_compensation_summary" in views
        assert "vw_tenure_summary" in views

        conn.close()

    def test_sql_pipeline_row_count_reconciliation(
        self,
        temp_processed_csv: Path,
        tmp_path: Path,
        test_logger: logging.Logger,
        sample_clean_data: pd.DataFrame,
    ) -> None:
        """Test that row counts match between staging and fact tables."""
        from ETL.Python.run_sql_pipeline import run_sql_pipeline

        db_path = tmp_path / "hr_analytics.db"

        # Run SQL pipeline with explicit paths
        run_sql_pipeline(
            processed_data_path=temp_processed_csv,
            db_path=db_path,
            sql_dir=Path(__file__).parent.parent.parent / "ETL" / "SQL",
            log_dir=tmp_path / "logs",
            logger=test_logger,
        )

        # Verify row counts match
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM staging_employee")
        staging_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Fact_Employee")
        fact_count = cursor.fetchone()[0]

        assert staging_count == fact_count
        assert staging_count == len(sample_clean_data)

        conn.close()

    def test_sql_pipeline_attrition_rate_calculation(
        self, temp_processed_csv: Path, tmp_path: Path, test_logger: logging.Logger
    ) -> None:
        """Test that attrition rate is calculated correctly."""
        from ETL.Python.run_sql_pipeline import run_sql_pipeline

        db_path = tmp_path / "hr_analytics.db"

        # Run SQL pipeline with explicit paths
        run_sql_pipeline(
            processed_data_path=temp_processed_csv,
            db_path=db_path,
            sql_dir=Path(__file__).parent.parent.parent / "ETL" / "SQL",
            log_dir=tmp_path / "logs",
            logger=test_logger,
        )

        # Query attrition rate
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT attrition_rate_pct FROM vw_attrition_rate")
        result = cursor.fetchone()

        # Should have a result (exact value depends on test data)
        assert result is not None
        assert len(result) == 1
        assert 0 <= result[0] <= 100

        conn.close()


# ---------------------------------------------------------------------------
# Test Error Handling
# ---------------------------------------------------------------------------


class TestPipelineErrorHandling:
    """Tests for pipeline error handling."""

    def test_missing_workbook_raises_error(
        self, tmp_path: Path, test_logger: logging.Logger
    ) -> None:
        """Test that missing workbook raises FileNotFoundError."""
        from ETL.Python.data_cleaning import run_pipeline

        non_existent_path = tmp_path / "nonexistent.xlsx"
        output_path = tmp_path / "output.csv"

        with pytest.raises(FileNotFoundError):
            run_pipeline(
                raw_workbook_path=non_existent_path,
                processed_data_path=output_path,
                log_dir=tmp_path / "logs",
                logger=test_logger,
            )

    def test_missing_csv_raises_error(self, tmp_path: Path, test_logger: logging.Logger) -> None:
        """Test that missing CSV raises FileNotFoundError."""
        from ETL.Python.run_sql_pipeline import run_sql_pipeline

        non_existent_csv = tmp_path / "nonexistent.csv"
        db_path = tmp_path / "test.db"

        with pytest.raises(FileNotFoundError):
            run_sql_pipeline(
                processed_data_path=non_existent_csv,
                db_path=db_path,
                sql_dir=Path(__file__).parent.parent.parent / "ETL" / "SQL",
                log_dir=tmp_path / "logs",
                logger=test_logger,
            )

    def test_invalid_schema_raises_error(self, tmp_path: Path, test_logger: logging.Logger) -> None:
        """Test that schema validation errors are raised."""
        from ETL.Python.data_cleaning import run_pipeline

        # Create workbook with missing columns
        bad_df = pd.DataFrame(
            {
                "Employee Number": [1, 2, 3],
                "Age": [25, 30, 35],
            }
        )

        bad_workbook = tmp_path / "bad_data.xlsx"
        bad_df.to_excel(bad_workbook, sheet_name="Data", index=False)

        output_path = tmp_path / "output.csv"

        # Should raise ValueError for missing columns
        with pytest.raises(ValueError, match="Schema mismatch"):
            run_pipeline(
                raw_workbook_path=bad_workbook,
                processed_data_path=output_path,
                log_dir=tmp_path / "logs",
                logger=test_logger,
            )


# ---------------------------------------------------------------------------
# Test Data Quality
# ---------------------------------------------------------------------------


class TestDataQuality:
    """Tests for data quality validation."""

    def test_no_null_values_in_key_columns(
        self, temp_workbook: Path, tmp_path: Path, test_logger: logging.Logger
    ) -> None:
        """Test that key columns have no null values."""
        from ETL.Python.data_cleaning import run_pipeline

        output_path = tmp_path / "hrdata_clean.csv"

        # Run pipeline
        run_pipeline(
            raw_workbook_path=temp_workbook,
            processed_data_path=output_path,
            log_dir=tmp_path / "logs",
            logger=test_logger,
        )

        # Verify no nulls in key columns
        output_df = pd.read_csv(output_path)

        key_columns = ["employee_number", "age", "gender", "department", "attrition"]
        for col in key_columns:
            if col in output_df.columns:
                assert output_df[col].isnull().sum() == 0, f"Column {col} has null values"

    def test_categorical_columns_have_valid_values(
        self, temp_workbook: Path, tmp_path: Path, test_logger: logging.Logger
    ) -> None:
        """Test that categorical columns contain only valid values."""
        from ETL.Python.data_cleaning import run_pipeline

        output_path = tmp_path / "hrdata_clean.csv"

        # Run pipeline
        run_pipeline(
            raw_workbook_path=temp_workbook,
            processed_data_path=output_path,
            log_dir=tmp_path / "logs",
            logger=test_logger,
        )

        # Verify categorical values
        output_df = pd.read_csv(output_path)

        # Check gender values
        if "gender" in output_df.columns:
            valid_genders = {"Female", "Male"}
            assert set(output_df["gender"].unique()).issubset(valid_genders)

        # Check attrition values
        if "attrition" in output_df.columns:
            valid_attrition = {"Yes", "No"}
            assert set(output_df["attrition"].unique()).issubset(valid_attrition)

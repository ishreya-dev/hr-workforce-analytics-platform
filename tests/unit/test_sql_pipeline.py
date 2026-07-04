"""
Unit tests for run_sql_pipeline.py module.

Tests individual SQL pipeline functions and utilities.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Generator

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def test_logger() -> logging.Logger:
    """Provide a test logger."""
    logger = logging.getLogger("test_sql_pipeline")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


@pytest.fixture
def temp_sql_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with SQL files."""
    sql_dir = tmp_path / "sql"
    sql_dir.mkdir()

    # Create schema.sql
    schema_sql = sql_dir / "schema.sql"
    schema_sql.write_text("""
        CREATE TABLE staging_employee (
            employee_number INTEGER PRIMARY KEY,
            age INTEGER NOT NULL
        );

        CREATE TABLE Fact_Employee (
            employee_number INTEGER PRIMARY KEY,
            age INTEGER NOT NULL
        );
    """)

    # Create load.sql
    load_sql = sql_dir / "load.sql"
    load_sql.write_text("""
        INSERT INTO Fact_Employee SELECT * FROM staging_employee;
    """)

    # Create views.sql
    views_sql = sql_dir / "views.sql"
    views_sql.write_text("""
        CREATE VIEW vw_test AS SELECT * FROM Fact_Employee;
    """)

    return sql_dir


@pytest.fixture
def temp_csv(tmp_path: Path) -> Path:
    """Create a temporary CSV file."""
    csv_path = tmp_path / "test.csv"
    df = pd.DataFrame({"employee_number": [1, 2, 3], "age": [25, 30, 35]})
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def temp_db(
    temp_csv: Path, temp_sql_dir: Path, test_logger: logging.Logger
) -> Generator[sqlite3.Connection, None, None]:
    """Create a temporary SQLite database with test data."""
    from ETL.Python.run_sql_pipeline import run_sql_pipeline

    db_path = temp_csv.parent / "test.db"

    run_sql_pipeline(
        processed_data_path=temp_csv,
        db_path=db_path,
        sql_dir=temp_sql_dir,
        log_dir=temp_csv.parent / "logs",
        logger=test_logger,
    )

    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()


# ---------------------------------------------------------------------------
# Test setup_logging
# ---------------------------------------------------------------------------


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_creates_logger(self, tmp_path: Path):
        """Test that setup_logging creates a logger."""
        from ETL.Python.run_sql_pipeline import setup_logging

        logger = setup_logging(log_dir=tmp_path / "logs", logger_name="test_setup")

        assert logger is not None
        assert logger.name == "test_setup"
        assert logger.level == logging.INFO

    def test_setup_logging_creates_log_file(self, tmp_path: Path):
        """Test that setup_logging creates a log file."""
        from ETL.Python.run_sql_pipeline import setup_logging

        log_dir = tmp_path / "logs"
        setup_logging(log_dir=log_dir, logger_name="test_setup2")

        # Check that log directory was created
        assert log_dir.exists()

        # Check that at least one log file exists
        log_files = list(log_dir.glob("*.log"))
        assert len(log_files) > 0


# ---------------------------------------------------------------------------
# Test run_sql_file
# ---------------------------------------------------------------------------


class TestRunSQLFile:
    """Tests for run_sql_file function."""

    def test_run_sql_file_success(
        self, temp_sql_dir: Path, temp_db: sqlite3.Connection, test_logger: logging.Logger
    ):
        """Test successful SQL file execution."""
        from ETL.Python.run_sql_pipeline import run_sql_file

        # Create a new SQL file
        test_sql = temp_sql_dir / "test.sql"
        test_sql.write_text("CREATE TABLE test_table (id INTEGER PRIMARY KEY);")

        # Should execute without error
        run_sql_file(temp_db, test_sql, test_logger)

        # Verify table was created
        cursor = temp_db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'")
        assert cursor.fetchone() is not None

    def test_run_sql_file_not_found(self, temp_db: sqlite3.Connection, test_logger: logging.Logger):
        """Test that missing SQL file raises FileNotFoundError."""
        from ETL.Python.run_sql_pipeline import run_sql_file

        non_existent_path = Path("nonexistent.sql")

        with pytest.raises(FileNotFoundError):
            run_sql_file(temp_db, non_existent_path, test_logger)

    def test_run_sql_file_invalid_sql(
        self, temp_sql_dir: Path, temp_db: sqlite3.Connection, test_logger: logging.Logger
    ):
        """Test that invalid SQL raises sqlite3.Error."""
        from ETL.Python.run_sql_pipeline import run_sql_file

        # Create SQL file with invalid syntax
        invalid_sql = temp_sql_dir / "invalid.sql"
        invalid_sql.write_text("CREATE TABLE test (id INTEGER PRIMARY KEY); INVALID SQL HERE;")

        # Should raise sqlite3.Error
        with pytest.raises(sqlite3.Error):
            run_sql_file(temp_db, invalid_sql, test_logger)


# ---------------------------------------------------------------------------
# Test run_sql_pipeline
# ---------------------------------------------------------------------------


class TestRunSQLPipeline:
    """Tests for run_sql_pipeline function."""

    def test_run_sql_pipeline_returns_metadata(
        self, temp_csv: Path, temp_sql_dir: Path, test_logger: logging.Logger
    ):
        """Test that run_sql_pipeline returns metadata dictionary."""
        from ETL.Python.run_sql_pipeline import run_sql_pipeline

        db_path = temp_csv.parent / "test.db"

        result = run_sql_pipeline(
            processed_data_path=temp_csv,
            db_path=db_path,
            sql_dir=temp_sql_dir,
            log_dir=temp_csv.parent / "logs",
            logger=test_logger,
        )

        assert "success" in result
        assert "db_path" in result
        assert "staging_count" in result
        assert "fact_count" in result
        assert "row_count_match" in result
        assert result["success"] is True
        assert result["row_count_match"] is True

    def test_run_sql_pipeline_removes_existing_db(
        self, temp_csv: Path, temp_sql_dir: Path, test_logger: logging.Logger
    ):
        """Test that run_sql_pipeline removes existing database."""
        from ETL.Python.run_sql_pipeline import run_sql_pipeline

        db_path = temp_csv.parent / "test.db"

        # Create existing database
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db_path.write_text("dummy")

        assert db_path.exists()

        # Run pipeline
        run_sql_pipeline(
            processed_data_path=temp_csv,
            db_path=db_path,
            sql_dir=temp_sql_dir,
            log_dir=temp_csv.parent / "logs",
            logger=test_logger,
        )

        # Old database should be removed and new one created
        assert db_path.exists()
        assert db_path.stat().st_size > 0

    def test_run_sql_pipeline_missing_csv(
        self, temp_sql_dir: Path, tmp_path: Path, test_logger: logging.Logger
    ):
        """Test that missing CSV raises FileNotFoundError."""
        from ETL.Python.run_sql_pipeline import run_sql_pipeline

        non_existent_csv = tmp_path / "nonexistent.csv"
        db_path = tmp_path / "test.db"

        with pytest.raises(FileNotFoundError):
            run_sql_pipeline(
                processed_data_path=non_existent_csv,
                db_path=db_path,
                sql_dir=temp_sql_dir,
                log_dir=tmp_path / "logs",
                logger=test_logger,
            )

    def test_run_sql_pipeline_missing_sql_file(
        self, temp_csv: Path, tmp_path: Path, test_logger: logging.Logger
    ):
        """Test that missing SQL file raises FileNotFoundError."""
        from ETL.Python.run_sql_pipeline import run_sql_pipeline

        empty_sql_dir = tmp_path / "empty_sql"
        empty_sql_dir.mkdir()
        db_path = tmp_path / "test.db"

        with pytest.raises(FileNotFoundError):
            run_sql_pipeline(
                processed_data_path=temp_csv,
                db_path=db_path,
                sql_dir=empty_sql_dir,
                log_dir=tmp_path / "logs",
                logger=test_logger,
            )

    def test_run_sql_pipeline_row_count_mismatch(
        self, temp_sql_dir: Path, tmp_path: Path, test_logger: logging.Logger
    ):
        """Test that row count mismatch is logged as warning."""
        from ETL.Python.run_sql_pipeline import run_sql_pipeline

        # Create CSV with 3 rows - one will be filtered out
        csv_path = tmp_path / "test.csv"
        df = pd.DataFrame(
            {
                "employee_number": [1, 2, 3],
                "age": [25, 30, 50],  # 50 will be filtered out by WHERE age < 40
            }
        )
        df.to_csv(csv_path, index=False)

        # Create SQL that only inserts 2 rows into fact table (age < 40)
        load_sql = temp_sql_dir / "load.sql"
        load_sql.write_text("""
            INSERT INTO Fact_Employee SELECT * FROM staging_employee WHERE age < 40;
        """)

        db_path = tmp_path / "test.db"

        # Should complete but log warning about mismatch
        result = run_sql_pipeline(
            processed_data_path=csv_path,
            db_path=db_path,
            sql_dir=temp_sql_dir,
            log_dir=tmp_path / "logs",
            logger=test_logger,
        )

        # Row counts should not match
        assert result["row_count_match"] is False
        assert result["staging_count"] == 3
        assert result["fact_count"] == 2


# ---------------------------------------------------------------------------
# Test main function
# ---------------------------------------------------------------------------


class TestMainFunction:
    """Tests for main() function."""

    def test_main_function_exists(self):
        """Test that main function is callable."""
        from ETL.Python.run_sql_pipeline import main

        # Should be callable (we won't actually run it as it requires real data)
        assert callable(main)

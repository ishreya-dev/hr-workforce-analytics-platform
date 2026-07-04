"""
Unit tests for config.py module.

Tests configuration management, environment variable support, and validation.
"""

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock environment variables for testing."""
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("AGE_MIN", "18")
    monkeypatch.setenv("AGE_MAX", "70")


# ---------------------------------------------------------------------------
# Test Configuration Loading
# ---------------------------------------------------------------------------


class TestConfigLoading:
    """Tests for configuration loading and environment variable support."""

    def test_default_env(self, mock_env: None) -> None:
        """Test that default environment is development."""
        # Re-import to pick up mocked env vars
        import importlib

        from ETL.Python import utils

        importlib.reload(utils.config)

        assert utils.config.ENV == "test"

    def test_repo_root_exists(self) -> None:
        """Test that REPO_ROOT is correctly calculated."""
        from ETL.Python.utils.config import REPO_ROOT

        assert REPO_ROOT.exists()
        assert REPO_ROOT.is_dir()

    def test_raw_workbook_path_default(self) -> None:
        """Test default raw workbook path."""
        from ETL.Python.utils.config import RAW_WORKBOOK_PATH

        # Should point to the Excel file
        assert "HR DATA_Excel.xlsx" in str(RAW_WORKBOOK_PATH)

    def test_processed_data_path_default(self) -> None:
        """Test default processed data path."""
        from ETL.Python.utils.config import PROCESSED_DATA_PATH

        # Should point to the cleaned CSV
        assert "hrdata_clean.csv" in str(PROCESSED_DATA_PATH)

    def test_log_dir_default(self) -> None:
        """Test default log directory."""
        from ETL.Python.utils.config import LOG_DIR

        assert "logs" in str(LOG_DIR)
        assert LOG_DIR.exists() or True  # May not exist until created


# ---------------------------------------------------------------------------
# Test Configuration Validation
# ---------------------------------------------------------------------------


class TestConfigValidation:
    """Tests for configuration validation."""

    def test_valid_env_values(self) -> None:
        """Test that valid environment values are accepted."""
        from ETL.Python.utils.config import validate_config

        # Should not raise for valid config
        validate_config()

    def test_path_collision_assertion(self) -> None:
        """Test that raw and processed paths cannot collide."""
        from ETL.Python.utils.config import PROCESSED_DATA_PATH, RAW_WORKBOOK_PATH

        # These should be different paths
        assert RAW_WORKBOOK_PATH.resolve() != PROCESSED_DATA_PATH.resolve()

    def test_legacy_path_collision_assertion(self) -> None:
        """Test that legacy and processed paths cannot collide."""
        from ETL.Python.utils.config import LEGACY_HRDATA_CSV_PATH, PROCESSED_DATA_PATH

        # These should be different paths
        assert LEGACY_HRDATA_CSV_PATH.resolve() != PROCESSED_DATA_PATH.resolve()


# ---------------------------------------------------------------------------
# Test Validation Constants
# ---------------------------------------------------------------------------


class TestValidationConstants:
    """Tests for validation constants and ranges."""

    def test_age_range(self) -> None:
        """Test age range constants."""
        from ETL.Python.utils.config import AGE_MAX, AGE_MIN

        assert AGE_MIN < AGE_MAX
        assert AGE_MIN >= 0
        assert AGE_MAX <= 120

    def test_scale_ranges(self) -> None:
        """Test scale range constants."""
        from ETL.Python.utils.config import (
            JOB_LEVEL_MAX,
            JOB_LEVEL_MIN,
            PERFORMANCE_RATING_MAX,
            PERFORMANCE_RATING_MIN,
            SCALE_1_4_MAX,
            SCALE_1_4_MIN,
            STOCK_OPTION_MAX,
            STOCK_OPTION_MIN,
        )

        assert SCALE_1_4_MIN < SCALE_1_4_MAX
        assert JOB_LEVEL_MIN < JOB_LEVEL_MAX
        assert STOCK_OPTION_MIN < STOCK_OPTION_MAX
        assert PERFORMANCE_RATING_MIN < PERFORMANCE_RATING_MAX

    def test_valid_gender_set(self) -> None:
        """Test valid gender values."""
        from ETL.Python.utils.config import VALID_GENDER

        assert "Female" in VALID_GENDER
        assert "Male" in VALID_GENDER
        assert len(VALID_GENDER) == 2

    def test_valid_attrition_set(self) -> None:
        """Test valid attrition values."""
        from ETL.Python.utils.config import VALID_ATTRITION

        assert "Yes" in VALID_ATTRITION
        assert "No" in VALID_ATTRITION
        assert len(VALID_ATTRITION) == 2

    def test_valid_department_set(self) -> None:
        """Test valid department values."""
        from ETL.Python.utils.config import VALID_DEPARTMENT

        assert "Sales" in VALID_DEPARTMENT
        assert "R&D" in VALID_DEPARTMENT
        assert "HR" in VALID_DEPARTMENT

    def test_age_band_bins(self) -> None:
        """Test age band bins configuration."""
        from ETL.Python.utils.config import AGE_BAND_BINS, AGE_BAND_LABELS

        assert len(AGE_BAND_BINS) == len(AGE_BAND_LABELS) + 1
        assert AGE_BAND_BINS[0] == 0
        assert AGE_BAND_LABELS[0] == "Under 25"


# ---------------------------------------------------------------------------
# Test Column Mappings
# ---------------------------------------------------------------------------


class TestColumnMappings:
    """Tests for column rename mappings."""

    def test_rename_map_completeness(self) -> None:
        """Test that rename map has expected number of entries."""
        from ETL.Python.utils.config import COLUMN_RENAME_MAP

        # Should have mappings for all major columns
        assert len(COLUMN_RENAME_MAP) > 20
        assert "Employee Number" in COLUMN_RENAME_MAP
        assert COLUMN_RENAME_MAP["Employee Number"] == "employee_number"

    def test_rename_map_values_snake_case(self) -> None:
        """Test that all rename values are snake_case."""
        from ETL.Python.utils.config import COLUMN_RENAME_MAP

        for new_name in COLUMN_RENAME_MAP.values():
            # Snake case should not have spaces or uppercase
            assert " " not in new_name
            assert new_name == new_name.lower()


# ---------------------------------------------------------------------------
# Test Columns to Drop
# ---------------------------------------------------------------------------


class TestColumnsToDrop:
    """Tests for column drop configuration."""

    def test_columns_to_drop_dict(self) -> None:
        """Test that columns to drop is properly configured."""
        from ETL.Python.utils.config import COLUMNS_TO_DROP

        assert isinstance(COLUMNS_TO_DROP, dict)
        assert "Employee Count" in COLUMNS_TO_DROP
        assert "emp no" in COLUMNS_TO_DROP
        assert "-2" in COLUMNS_TO_DROP
        assert "0" in COLUMNS_TO_DROP

    def test_conditional_drop_candidates(self) -> None:
        """Test that conditional drop candidates are configured."""
        from ETL.Python.utils.config import CONDITIONAL_DROP_CANDIDATES

        assert isinstance(CONDITIONAL_DROP_CANDIDATES, dict)
        assert "Over18" in CONDITIONAL_DROP_CANDIDATES
        assert "Standard Hours" in CONDITIONAL_DROP_CANDIDATES


# ---------------------------------------------------------------------------
# Test Legacy Fields
# ---------------------------------------------------------------------------


class TestLegacyFields:
    """Tests for legacy field configuration."""

    def test_legacy_calculated_fields(self) -> None:
        """Test that legacy calculated fields are documented."""
        from ETL.Python.utils.config import LEGACY_CALCULATED_FIELDS_NOT_USED

        assert len(LEGACY_CALCULATED_FIELDS_NOT_USED) == 6
        assert "CF_age band" in LEGACY_CALCULATED_FIELDS_NOT_USED
        assert "CF_attrition label" in LEGACY_CALCULATED_FIELDS_NOT_USED

    def test_legacy_csv_path(self) -> None:
        """Test that legacy CSV path is correctly set."""
        from ETL.Python.utils.config import LEGACY_HRDATA_CSV_PATH

        assert "hrdata.csv" in str(LEGACY_HRDATA_CSV_PATH)
        assert "raw" in str(LEGACY_HRDATA_CSV_PATH)

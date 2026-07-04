"""
Unit tests for data_cleaning.py module.

Tests individual data cleaning and validation functions.
"""

import logging

import numpy as np
import pandas as pd
import pytest

from ETL.Python.data_cleaning import (
    add_age_band,
    drop_columns,
    rename_columns,
    standardize_dtypes,
    validate_categorical_domains,
    validate_constant_column,
    validate_numeric_ranges,
    validate_uniqueness,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_raw_df() -> pd.DataFrame:
    """Provide a sample raw DataFrame for testing."""
    return pd.DataFrame(
        {
            "Employee Number": [1, 2, 3, 4, 5],
            "emp no": ["STAFF-1", "STAFF-2", "STAFF-3", "STAFF-4", "STAFF-5"],
            "Age": [25, 30, 35, 40, 45],
            "Attrition": ["Yes", "No", "No", "Yes", "No"],
            "Business Travel": [
                "Travel_Rarely",
                "Non-Travel",
                "Travel_Frequently",
                "Travel_Rarely",
                "Non-Travel",
            ],
            "Daily Rate": [1000, 1500, 2000, 1200, 1100],
            "Department": ["Sales", "R&D", "HR", "Sales", "R&D"],
            "Distance From Home": [5, 10, 15, 8, 12],
            "Education": [
                "Bachelor's Degree",
                "Master's Degree",
                "Doctoral Degree",
                "Bachelor's Degree",
                "Associates Degree",
            ],
            "Education Field": [
                "Life Sciences",
                "Medical",
                "Life Sciences",
                "Marketing",
                "Technical Degree",
            ],
            "Employee Count": [1, 1, 1, 1, 1],
            "Environment Satisfaction": [3, 3, 4, 2, 3],
            "Gender": ["Female", "Male", "Female", "Male", "Female"],
            "Hourly Rate": [50, 75, 100, 60, 55],
            "Job Involvement": [3, 2, 3, 2, 3],
            "Job Level": [1, 2, 3, 2, 1],
            "Job Role": [
                "Sales Representative",
                "Research Scientist",
                "HR Manager",
                "Sales Executive",
                "Lab Technician",
            ],
            "Job Satisfaction": [2, 3, 4, 2, 3],
            "Marital Status": ["Single", "Married", "Single", "Married", "Divorced"],
            "Monthly Income": [3000, 5000, 8000, 4500, 3500],
            "Monthly Rate": [20000, 25000, 30000, 22000, 21000],
            "Num Companies Worked": [2, 3, 1, 2, 2],
            "Over18": ["Y", "Y", "Y", "Y", "Y"],
            "Over Time": ["Yes", "No", "No", "Yes", "No"],
            "Percent Salary Hike": [12, 15, 18, 13, 11],
            "Performance Rating": [3, 3, 4, 3, 3],
            "Relationship Satisfaction": [2, 3, 3, 4, 2],
            "Standard Hours": [80, 80, 80, 80, 80],
            "Stock Option Level": [0, 1, 2, 0, 1],
            "Total Working Years": [5, 10, 15, 7, 6],
            "Training Times Last Year": [2, 3, 2, 3, 2],
            "Work Life Balance": [2, 3, 3, 2, 3],
            "Years At Company": [2, 5, 10, 3, 4],
            "Years In Current Role": [1, 3, 5, 2, 2],
            "Years Since Last Promotion": [1, 2, 3, 1, 2],
            "Years With Curr Manager": [2, 4, 8, 3, 3],
            "-2": [-2, -2, -2, -2, -2],
            "0": [0, 0, 0, 0, 0],
        }
    )


@pytest.fixture
def test_logger() -> logging.Logger:
    """Provide a test logger."""
    logger = logging.getLogger("test_data_cleaning")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


# ---------------------------------------------------------------------------
# Test validate_uniqueness
# ---------------------------------------------------------------------------


class TestValidateUniqueness:
    """Tests for validate_uniqueness function."""

    def test_unique_employee_numbers(self, sample_raw_df, test_logger, caplog):
        """Test that unique employee numbers pass validation."""
        with caplog.at_level(logging.INFO):
            validate_uniqueness(sample_raw_df, test_logger)
            assert "uniqueness check passed" in caplog.text
            assert "5/5 unique" in caplog.text

    def test_duplicate_employee_numbers(self, test_logger, caplog):
        """Test that duplicate employee numbers are detected."""
        df = pd.DataFrame({"Employee Number": [1, 2, 2, 3, 4], "Age": [25, 30, 35, 40, 45]})
        with caplog.at_level(logging.WARNING):
            validate_uniqueness(df, test_logger)
            assert "duplicate" in caplog.text.lower()
            assert "1 duplicate" in caplog.text


# ---------------------------------------------------------------------------
# Test validate_constant_column
# ---------------------------------------------------------------------------


class TestValidateConstantColumn:
    """Tests for validate_constant_column function."""

    def test_constant_column_detected(self, sample_raw_df, test_logger, caplog):
        """Test that constant columns are detected."""
        with caplog.at_level(logging.INFO):
            result = validate_constant_column(sample_raw_df, "Employee Count", test_logger)
            assert result is True
            assert "confirmed constant" in caplog.text

    def test_non_constant_column(self, sample_raw_df, test_logger, caplog):
        """Test that non-constant columns are identified."""
        with caplog.at_level(logging.WARNING):
            result = validate_constant_column(sample_raw_df, "Age", test_logger)
            assert result is False
            assert "not dropping" in caplog.text.lower()

    def test_missing_column(self, test_logger):
        """Test handling of missing column."""
        df = pd.DataFrame({"Age": [25, 30, 35]})
        with pytest.raises(KeyError):
            validate_constant_column(df, "Employee Count", test_logger)


# ---------------------------------------------------------------------------
# Test validate_categorical_domains
# ---------------------------------------------------------------------------


class TestValidateCategoricalDomains:
    """Tests for validate_categorical_domains function."""

    def test_valid_domains(self, sample_raw_df, test_logger, caplog):
        """Test that valid categorical domains pass."""
        with caplog.at_level(logging.INFO):
            validate_categorical_domains(sample_raw_df, test_logger)
            assert "Domain check passed" in caplog.text

    def test_invalid_gender_values(self, test_logger, caplog):
        """Test detection of invalid gender values."""
        df = pd.DataFrame(
            {
                "Gender": ["Female", "Male", "Unknown"],
                "Marital Status": ["Single", "Married", "Single"],
                "Department": ["Sales", "R&D", "HR"],
                "Business Travel": ["Travel_Rarely", "Non-Travel", "Travel_Frequently"],
                "Attrition": ["Yes", "No", "No"],
                "Over Time": ["Yes", "No", "No"],
                "Education": ["Bachelor's Degree", "Master's Degree", "High School"],
            }
        )
        with caplog.at_level(logging.WARNING):
            validate_categorical_domains(df, test_logger)
            assert "unexpected values" in caplog.text.lower()


# ---------------------------------------------------------------------------
# Test validate_numeric_ranges
# ---------------------------------------------------------------------------


class TestValidateNumericRanges:
    """Tests for validate_numeric_ranges function."""

    def test_valid_ranges(self, sample_raw_df, test_logger, caplog):
        """Test that valid numeric ranges pass."""
        with caplog.at_level(logging.INFO):
            validate_numeric_ranges(sample_raw_df, test_logger)
            assert "range check passed" in caplog.text

    def test_out_of_range_age(self, test_logger, caplog):
        """Test detection of out-of-range age values."""
        df = pd.DataFrame(
            {
                "Age": [25, 30, 80],  # 80 is out of range
                "Employee Number": [1, 2, 3],
                "Job Satisfaction": [3, 3, 3],
                "Environment Satisfaction": [3, 3, 3],
                "Relationship Satisfaction": [3, 3, 3],
                "Job Involvement": [3, 3, 3],
                "Work Life Balance": [3, 3, 3],
                "Performance Rating": [3, 3, 3],
                "Job Level": [1, 2, 3],
                "Stock Option Level": [0, 1, 2],
            }
        )
        with caplog.at_level(logging.WARNING):
            validate_numeric_ranges(df, test_logger)
            assert "outside" in caplog.text.lower()


# ---------------------------------------------------------------------------
# Test drop_columns
# ---------------------------------------------------------------------------


class TestDropColumns:
    """Tests for drop_columns function."""

    def test_drop_constant_columns(self, sample_raw_df, test_logger):
        """Test dropping of constant columns."""
        result = drop_columns(sample_raw_df, test_logger)
        assert "Employee Count" not in result.columns
        assert "emp no" not in result.columns
        assert "-2" not in result.columns
        assert "0" not in result.columns

    def test_retain_non_constant_columns(self, sample_raw_df, test_logger):
        """Test that non-constant columns are retained."""
        result = drop_columns(sample_raw_df, test_logger)
        assert "Age" in result.columns
        assert "Attrition" in result.columns

    def test_drop_logging(self, sample_raw_df, test_logger, caplog):
        """Test that column drops are logged."""
        with caplog.at_level(logging.INFO):
            drop_columns(sample_raw_df, test_logger)
            assert "Dropped column" in caplog.text


# ---------------------------------------------------------------------------
# Test add_age_band
# ---------------------------------------------------------------------------


class TestAddAgeBand:
    """Tests for add_age_band function."""

    def test_age_band_added(self, sample_raw_df, test_logger):
        """Test that age_band column is added."""
        result = add_age_band(sample_raw_df, test_logger)
        assert "age_band" in result.columns

    def test_age_band_values(self, sample_raw_df, test_logger):
        """Test that age_band values are correct."""
        result = add_age_band(sample_raw_df, test_logger)
        # Age 25 should be in "25 - 34" band
        assert result.loc[0, "age_band"] == "25 - 34"
        # Age 35 should be in "35 - 44" band
        assert result.loc[2, "age_band"] == "35 - 44"

    def test_age_band_logging(self, sample_raw_df, test_logger, caplog):
        """Test that age_band computation is logged."""
        with caplog.at_level(logging.INFO):
            add_age_band(sample_raw_df, test_logger)
            assert "age_band" in caplog.text.lower()


# ---------------------------------------------------------------------------
# Test rename_columns
# ---------------------------------------------------------------------------


class TestRenameColumns:
    """Tests for rename_columns function."""

    def test_columns_renamed(self, sample_raw_df, test_logger):
        """Test that columns are renamed to snake_case."""
        result = rename_columns(sample_raw_df, test_logger)
        assert "employee_number" in result.columns
        assert "Employee Number" not in result.columns
        assert "business_travel" in result.columns
        assert "Business Travel" not in result.columns

    def test_rename_logging(self, sample_raw_df, test_logger, caplog):
        """Test that column renaming is logged."""
        with caplog.at_level(logging.INFO):
            rename_columns(sample_raw_df, test_logger)
            assert "Renamed" in caplog.text


# ---------------------------------------------------------------------------
# Test standardize_dtypes
# ---------------------------------------------------------------------------


class TestStandardizeDtypes:
    """Tests for standardize_dtypes function."""

    def test_categorical_columns(self, sample_raw_df, test_logger):
        """Test that categorical columns are converted to category dtype."""
        # First rename columns
        df = rename_columns(sample_raw_df, test_logger)
        # Then standardize dtypes
        result = standardize_dtypes(df, test_logger)

        assert isinstance(result["gender"].dtype, pd.CategoricalDtype)
        assert isinstance(result["department"].dtype, pd.CategoricalDtype)
        assert isinstance(result["attrition"].dtype, pd.CategoricalDtype)

    def test_integer_columns(self, sample_raw_df, test_logger):
        """Test that integer columns are converted to int64."""
        df = rename_columns(sample_raw_df, test_logger)
        result = standardize_dtypes(df, test_logger)

        assert result["age"].dtype == np.int64
        assert result["monthly_income"].dtype == np.int64
        assert result["job_level"].dtype == np.int64

    def test_dtype_logging(self, sample_raw_df, test_logger, caplog):
        """Test that dtype standardization is logged."""
        df = rename_columns(sample_raw_df, test_logger)
        with caplog.at_level(logging.INFO):
            standardize_dtypes(df, test_logger)
            assert "Standardized dtypes" in caplog.text

"""
Shared pytest fixtures for HR Attrition & Workforce Analytics test suite.

This module provides common fixtures used across unit and integration tests.
"""

import logging
import sqlite3
import tempfile
from pathlib import Path
from typing import Generator

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Logging fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def test_logger() -> logging.Logger:
    """Provide a test logger instance."""
    logger = logging.getLogger("test")
    logger.setLevel(logging.DEBUG)

    # Add console handler if not already present
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_employee_data() -> pd.DataFrame:
    """
    Provide a minimal sample DataFrame for unit testing.

    This represents a small subset of the full dataset with all required columns.
    """
    return pd.DataFrame(
        {
            # Identifiers
            "Employee Number": [1, 2, 3, 4, 5],
            "emp no": ["STAFF-1", "STAFF-2", "STAFF-3", "STAFF-4", "STAFF-5"],
            # Demographics
            "Age": [25, 30, 35, 40, 45],
            "Gender": ["Female", "Male", "Female", "Male", "Female"],
            "Marital Status": ["Single", "Married", "Single", "Married", "Divorced"],
            # Job info
            "Department": ["Sales", "R&D", "HR", "Sales", "R&D"],
            "Job Role": [
                "Sales Representative",
                "Research Scientist",
                "HR Manager",
                "Sales Executive",
                "Lab Technician",
            ],
            "Job Level": [1, 2, 3, 2, 1],
            "Business Travel": [
                "Travel_Rarely",
                "Non-Travel",
                "Travel_Frequently",
                "Travel_Rarely",
                "Non-Travel",
            ],
            # Satisfaction (1-4 scale)
            "Job Satisfaction": [2, 3, 4, 2, 3],
            "Environment Satisfaction": [3, 3, 4, 2, 3],
            "Relationship Satisfaction": [2, 3, 3, 4, 2],
            "Job Involvement": [3, 2, 3, 2, 3],
            "Work Life Balance": [2, 3, 3, 2, 3],
            # Performance
            "Performance Rating": [3, 3, 4, 3, 3],
            "Over Time": ["Yes", "No", "No", "Yes", "No"],
            # Compensation
            "Monthly Income": [3000, 5000, 8000, 4500, 3500],
            "Daily Rate": [1000, 1500, 2000, 1200, 1100],
            "Hourly Rate": [50, 75, 100, 60, 55],
            "Monthly Rate": [20000, 25000, 30000, 22000, 21000],
            "Percent Salary Hike": [12, 15, 18, 13, 11],
            "Stock Option Level": [0, 1, 2, 0, 1],
            # Tenure
            "Total Working Years": [5, 10, 15, 7, 6],
            "Years At Company": [2, 5, 10, 3, 4],
            "Years In Current Role": [1, 3, 5, 2, 2],
            "Years Since Last Promotion": [1, 2, 3, 1, 2],
            "Years With Curr Manager": [2, 4, 8, 3, 3],
            # Other
            "Num Companies Worked": [2, 3, 1, 2, 2],
            "Distance From Home": [5, 10, 15, 8, 12],
            "Training Times Last Year": [2, 3, 2, 3, 2],
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
            # Target
            "Attrition": ["Yes", "No", "No", "Yes", "No"],
            # Constant/junk columns (to be dropped)
            "Employee Count": [1, 1, 1, 1, 1],
            "Over18": ["Y", "Y", "Y", "Y", "Y"],
            "Standard Hours": [80, 80, 80, 80, 80],
            "-2": [-2, -2, -2, -2, -2],
            "0": [0, 0, 0, 0, 0],
        }
    )


@pytest.fixture
def sample_clean_data() -> pd.DataFrame:
    """
    Provide a sample DataFrame that has already been cleaned.

    This represents the expected output after data_cleaning.py processing.
    """
    return pd.DataFrame(
        {
            "employee_number": [1, 2, 3, 4, 5],
            "gender": pd.Categorical(["Female", "Male", "Female", "Male", "Female"]),
            "marital_status": pd.Categorical(
                ["Single", "Married", "Single", "Married", "Divorced"]
            ),
            "age_band": pd.Categorical(["25 - 34", "25 - 34", "35 - 44", "35 - 44", "35 - 44"]),
            "age": [25, 30, 35, 40, 45],
            "department": pd.Categorical(["Sales", "R&D", "HR", "Sales", "R&D"]),
            "education": pd.Categorical(
                [
                    "Bachelor's Degree",
                    "Master's Degree",
                    "Doctoral Degree",
                    "Bachelor's Degree",
                    "Associates Degree",
                ]
            ),
            "education_field": pd.Categorical(
                ["Life Sciences", "Medical", "Life Sciences", "Marketing", "Technical Degree"]
            ),
            "job_role": pd.Categorical(
                [
                    "Sales Representative",
                    "Research Scientist",
                    "HR Manager",
                    "Sales Executive",
                    "Lab Technician",
                ]
            ),
            "job_level": [1, 2, 3, 2, 1],
            "business_travel": pd.Categorical(
                ["Travel_Rarely", "Non-Travel", "Travel_Frequently", "Travel_Rarely", "Non-Travel"]
            ),
            "attrition": pd.Categorical(["Yes", "No", "No", "Yes", "No"]),
            "job_satisfaction": [2, 3, 4, 2, 3],
            "environment_satisfaction": [3, 3, 4, 2, 3],
            "relationship_satisfaction": [2, 3, 3, 4, 2],
            "job_involvement": [3, 2, 3, 2, 3],
            "work_life_balance": [2, 3, 3, 2, 3],
            "performance_rating": [3, 3, 4, 3, 3],
            "over_time": pd.Categorical(["Yes", "No", "No", "Yes", "No"]),
            "monthly_income": [3000, 5000, 8000, 4500, 3500],
            "daily_rate": [1000, 1500, 2000, 1200, 1100],
            "hourly_rate": [50, 75, 100, 60, 55],
            "monthly_rate": [20000, 25000, 30000, 22000, 21000],
            "percent_salary_hike": [12, 15, 18, 13, 11],
            "stock_option_level": [0, 1, 2, 0, 1],
            "total_working_years": [5, 10, 15, 7, 6],
            "years_at_company": [2, 5, 10, 3, 4],
            "years_in_current_role": [1, 3, 5, 2, 2],
            "years_since_last_promotion": [1, 2, 3, 1, 2],
            "years_with_curr_manager": [2, 4, 8, 3, 3],
            "num_companies_worked": [2, 3, 1, 2, 2],
            "distance_from_home": [5, 10, 15, 8, 12],
            "training_times_last_year": [2, 3, 2, 3, 2],
        }
    )


# ---------------------------------------------------------------------------
# Temporary directory fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for test artifacts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_db_path(temp_dir: Path) -> Path:
    """Provide a path for a temporary SQLite database."""
    return temp_dir / "test.db"


# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def test_db(
    temp_db_path: Path, sample_clean_data: pd.DataFrame
) -> Generator[sqlite3.Connection, None, None]:
    """
    Provide a test SQLite database with sample data loaded.

    This fixture:
    1. Creates a temporary SQLite database
    2. Creates the star schema
    3. Loads sample data
    4. Yields the connection
    5. Cleans up after the test
    """
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()

    # Create dimension tables
    cursor.executescript("""
        CREATE TABLE Dim_Department (
            DepartmentKey INTEGER PRIMARY KEY AUTOINCREMENT,
            DepartmentName TEXT NOT NULL UNIQUE
        );

        CREATE TABLE Dim_JobRole (
            JobRoleKey INTEGER PRIMARY KEY AUTOINCREMENT,
            JobRoleName TEXT NOT NULL,
            DepartmentKey INTEGER NOT NULL REFERENCES Dim_Department(DepartmentKey),
            UNIQUE (JobRoleName, DepartmentKey)
        );

        CREATE TABLE Dim_Education (
            EducationKey INTEGER PRIMARY KEY AUTOINCREMENT,
            EducationLevel TEXT NOT NULL,
            EducationField TEXT NOT NULL,
            UNIQUE (EducationLevel, EducationField)
        );

        CREATE TABLE Dim_MaritalStatus (
            MaritalStatusKey INTEGER PRIMARY KEY AUTOINCREMENT,
            MaritalStatusName TEXT NOT NULL UNIQUE
        );

        CREATE TABLE Fact_Employee (
            employee_number INTEGER PRIMARY KEY,
            DepartmentKey INTEGER NOT NULL REFERENCES Dim_Department(DepartmentKey),
            JobRoleKey INTEGER NOT NULL REFERENCES Dim_JobRole(JobRoleKey),
            EducationKey INTEGER NOT NULL REFERENCES Dim_Education(EducationKey),
            MaritalStatusKey INTEGER NOT NULL REFERENCES Dim_MaritalStatus(MaritalStatusKey),
            age INTEGER NOT NULL,
            age_band TEXT NOT NULL,
            gender TEXT NOT NULL,
            job_level INTEGER NOT NULL,
            business_travel TEXT NOT NULL,
            job_satisfaction INTEGER NOT NULL,
            environment_satisfaction INTEGER NOT NULL,
            relationship_satisfaction INTEGER NOT NULL,
            job_involvement INTEGER NOT NULL,
            work_life_balance INTEGER NOT NULL,
            performance_rating INTEGER NOT NULL,
            over_time TEXT NOT NULL CHECK (over_time IN ('Yes', 'No')),
            monthly_income INTEGER NOT NULL,
            daily_rate INTEGER NOT NULL,
            hourly_rate INTEGER NOT NULL,
            monthly_rate INTEGER NOT NULL,
            percent_salary_hike INTEGER NOT NULL,
            stock_option_level INTEGER NOT NULL,
            total_working_years INTEGER NOT NULL,
            years_at_company INTEGER NOT NULL,
            years_in_current_role INTEGER NOT NULL,
            years_since_last_promotion INTEGER NOT NULL,
            years_with_curr_manager INTEGER NOT NULL,
            num_companies_worked INTEGER NOT NULL,
            distance_from_home INTEGER NOT NULL,
            training_times_last_year INTEGER NOT NULL,
            attrition TEXT NOT NULL CHECK (attrition IN ('Yes', 'No'))
        );
    """)

    # Insert dimension data
    departments = [("Sales",), ("R&D",), ("HR",)]
    cursor.executemany("INSERT INTO Dim_Department (DepartmentName) VALUES (?)", departments)

    job_roles = [
        ("Sales Representative", 1),
        ("Sales Executive", 1),
        ("Research Scientist", 2),
        ("Lab Technician", 2),
        ("HR Manager", 3),
    ]
    cursor.executemany(
        "INSERT INTO Dim_JobRole (JobRoleName, DepartmentKey) VALUES (?, ?)", job_roles
    )

    education = [
        ("Bachelor's Degree", "Life Sciences"),
        ("Master's Degree", "Medical"),
        ("Doctoral Degree", "Life Sciences"),
        ("Associates Degree", "Technical Degree"),
    ]
    cursor.executemany(
        "INSERT INTO Dim_Education (EducationLevel, EducationField) VALUES (?, ?)", education
    )

    marital_status = [("Single",), ("Married",), ("Divorced",)]
    cursor.executemany(
        "INSERT INTO Dim_MaritalStatus (MaritalStatusName) VALUES (?)", marital_status
    )

    # Insert fact data (simplified - using hardcoded keys for test data)
    fact_data = [
        (
            1,
            1,
            1,
            1,
            1,
            25,
            "25 - 34",
            "Female",
            1,
            "Travel_Rarely",
            2,
            3,
            2,
            3,
            2,
            3,
            "Yes",
            3000,
            1000,
            50,
            20000,
            12,
            0,
            5,
            2,
            1,
            1,
            2,
            2,
            5,
            2,
            "Yes",
        ),
        (
            2,
            2,
            2,
            2,
            2,
            30,
            "25 - 34",
            "Male",
            2,
            "Non-Travel",
            3,
            3,
            3,
            2,
            3,
            3,
            "No",
            5000,
            1500,
            75,
            25000,
            15,
            1,
            10,
            5,
            3,
            2,
            4,
            3,
            10,
            3,
            "No",
        ),
        (
            3,
            3,
            3,
            3,
            1,
            35,
            "35 - 44",
            "Female",
            3,
            "Travel_Frequently",
            4,
            4,
            3,
            3,
            3,
            4,
            "No",
            8000,
            2000,
            100,
            30000,
            18,
            2,
            15,
            10,
            5,
            3,
            8,
            1,
            15,
            2,
            "No",
        ),
        (
            4,
            1,
            2,
            1,
            2,
            40,
            "35 - 44",
            "Male",
            2,
            "Travel_Rarely",
            2,
            2,
            4,
            2,
            2,
            3,
            "Yes",
            4500,
            1200,
            60,
            22000,
            13,
            0,
            7,
            3,
            2,
            1,
            3,
            2,
            8,
            3,
            "Yes",
        ),
        (
            5,
            2,
            4,
            4,
            3,
            45,
            "35 - 44",
            "Female",
            1,
            "Non-Travel",
            3,
            3,
            2,
            3,
            3,
            3,
            "No",
            3500,
            1100,
            55,
            21000,
            11,
            1,
            6,
            4,
            2,
            2,
            3,
            2,
            12,
            2,
            "No",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO Fact_Employee VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        fact_data,
    )

    conn.commit()

    yield conn

    conn.close()


# ---------------------------------------------------------------------------
# Configuration fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock environment variables for testing."""
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

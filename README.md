<div align="center">

# 📊 HR Attrition & Workforce Analytics Platform

### Enterprise Workforce Intelligence using Python • SQL • Power BI

Transforming employee data into actionable workforce intelligence through automated ETL pipelines, dimensional SQL modeling, and interactive Power BI dashboards.

<br>

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![SQL](https://img.shields.io/badge/SQL-Star%20Schema-336791?style=for-the-badge)
![MIT License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)

</div>

---

## 📖 Overview

This project demonstrates the complete lifecycle of an enterprise HR analytics solution—from raw employee records to executive-level business intelligence.

The solution combines **Python**, **SQL**, and **Power BI** to automate data preparation, implement a dimensional data warehouse, calculate workforce KPIs, and deliver interactive dashboards that help HR teams monitor employee attrition, workforce demographics, job satisfaction, and organizational trends.

Unlike a standalone Power BI dashboard, this repository showcases the entire analytics engineering workflow including:

- Automated Python ETL pipeline
- Data validation & preprocessing
- SQL Star Schema implementation
- Business KPI generation
- Interactive Power BI reporting
- Business & technical documentation
- Testing and quality assurance

---

## 📌 Project Snapshot

| Metric | Value |
|---------|------:|
| Employees Analyzed | **1,470** |
| Dataset Attributes | **43** |
| Dashboard Pages | **6** |
| Business KPIs | **25+** |
| SQL Views | **10+** |
| ETL Language | **Python** |
| Database | **SQLite** |
| Visualization | **Power BI** |

---

# 📷 Dashboard Gallery

The Power BI solution provides multiple interactive dashboard views for workforce analysis. Users can dynamically filter employees by education level while monitoring workforce KPIs, demographics, and attrition patterns.

## Executive Workforce Dashboard

<p align="center">
<img src="assets/dashboard/executive_dashboard.png" width="900">
</p>

---

## Education-Level Workforce Analysis

<table>
<tr>
<td align="center">

### Associate Degree

<img src="assets/associate_degree.png" width="430">

</td>

<td align="center">

### Bachelor's Degree

<img src="assets/bachelors_degree.png" width="430">

</td>
</tr>

<tr>
<td align="center">

### Doctoral Degree

<img src="assets/doctoral_degree.png" width="430">

</td>

<td align="center">

### High School

<img src="assets/high_school.png" width="430">

</td>
</tr>

<tr>
<td colspan="2" align="center">

### Master's Degree

<img src="assets/masters_degree.png" width="430">

</td>
</tr>
</table>

---

# 🎥 Interactive Dashboard Walkthrough

The project includes a complete walkthrough demonstrating dashboard navigation, KPI interactions, dynamic slicers, and business insights.

<p align="center">
<img src="assets/HRProject.gif" width="900">
</p>

---
# 🎯 Business Problem

Human Resource teams often rely on static reports and spreadsheets that make it difficult to monitor workforce health, identify attrition trends, and understand employee demographics in real time.

Without centralized analytics, organizations face challenges such as:

- Identifying departments with high employee turnover.
- Understanding the impact of education, age, and gender on attrition.
- Tracking workforce composition across business units.
- Measuring employee satisfaction and retention indicators.
- Delivering timely, data-driven insights to HR leadership.

This project addresses these challenges by building an end-to-end HR analytics platform that automates data preparation, structures information into a dimensional data model, and delivers interactive Power BI dashboards for executive decision-making.

---

# 🎯 Project Objectives

The primary objectives of this project are to:

- Automate HR data cleaning and validation using Python.
- Build a scalable SQL Star Schema for analytical reporting.
- Develop reusable SQL views for business KPIs.
- Design an interactive Power BI dashboard for workforce monitoring.
- Enable HR leaders to identify attrition patterns and workforce trends.
- Demonstrate an end-to-end Business Intelligence workflow suitable for enterprise environments.

---

# 🏗 Solution Architecture

```mermaid
flowchart LR

A[Raw Excel Dataset]
B[Python ETL Pipeline]
C[Data Validation & Cleaning]
D[Processed Dataset]
E[SQLite Data Warehouse]
F[Star Schema]
G[SQL KPI Views]
H[Power BI Dashboard]
I[Business Insights]

A --> B
B --> C
C --> D
D --> E
E --> F
F --> G
G --> H
H --> I
```

---

# 🔄 Data Pipeline

The analytics workflow follows a structured ETL process:

```text
Raw Excel Dataset
        │
        ▼
Python Data Cleaning
        │
        ▼
Validation & Profiling
        │
        ▼
Processed Dataset
        │
        ▼
SQLite Database
        │
        ▼
Star Schema
        │
        ▼
SQL KPI Views
        │
        ▼
Power BI Dashboard
        │
        ▼
Executive Insights
```

---

# 📂 Repository Structure

| Folder | Description |
|---------|-------------|
| **Analytics/** | Power BI dashboard, Excel workbook, dashboard assets |
| **Architecture/** | High-Level Design (HLD), Low-Level Design (LLD), Data Architecture |
| **Business/** | BRD, TRD, Business Insights and Recommendations |
| **Data/raw/** | Original IBM HR Analytics dataset |
| **Data/processed/** | Cleaned dataset generated by Python ETL |
| **ETL/Python/** | Data preprocessing, validation, automation scripts |
| **ETL/SQL/** | Database schema, SQL scripts, KPI queries and analytical views |
| **Testing/** | KPI reconciliation documentation |
| **tests/** | Automated unit and integration tests |

---

# 🛠 Technology Stack

| Category | Technologies |
|-----------|--------------|
| **Programming Language** | Python |
| **Database** | SQLite |
| **SQL** | SQL (DDL, DML, Views) |
| **Data Processing** | Pandas, NumPy |
| **Business Intelligence** | Microsoft Power BI |
| **Spreadsheet** | Microsoft Excel |
| **Version Control** | Git, GitHub |
| **Testing** | pytest |
| **Code Quality** | Black, flake8, isort, mypy |
| **Documentation** | Markdown, Mermaid |

---

# 📊 Dataset Information

| Attribute | Details |
|------------|---------|
| Dataset | IBM HR Analytics Employee Attrition |
| Records | 1,470 Employees |
| Features | 43 Employee Attributes |
| Data Type | Structured HR Dataset |
| Source | IBM Sample HR Dataset (Kaggle) |
| Personally Identifiable Information | None (Synthetic Dataset) |

---

# 📈 Data Model

The project implements a dimensional Star Schema to support analytical reporting and Power BI visualization.

### Fact Table

- Fact_Employee

### Dimension Tables

- Dim_Department
- Dim_JobRole
- Dim_Education
- Dim_Gender
- Dim_BusinessTravel
- Dim_MaritalStatus
- Dim_OverTime

The dimensional model enables efficient aggregation, KPI calculations, and interactive dashboard filtering.

---

# ⚙ ETL & Data Engineering Pipeline

The project follows a modular ETL architecture that converts raw HR data into a clean, analytics-ready dataset for SQL reporting and Power BI visualization.

```text
Raw Excel Dataset
        │
        ▼
Data Profiling & Validation
        │
        ▼
Data Cleaning & Transformation
        │
        ▼
Processed Dataset
        │
        ▼
SQLite Data Warehouse
        │
        ▼
Star Schema Modeling
        │
        ▼
SQL Views & KPI Generation
        │
        ▼
Power BI Dashboard
```

---

### Pipeline Components

| Stage | Description |
|--------|-------------|
| Data Profiling | Identifies missing values, duplicate records, and schema inconsistencies |
| Data Cleaning | Removes redundant fields, standardizes column names, validates records |
| Data Transformation | Prepares analytics-ready tables for reporting |
| SQL Modeling | Creates Star Schema with Fact and Dimension tables |
| KPI Layer | Generates reusable SQL Views for business reporting |
| Visualization | Interactive dashboards developed in Microsoft Power BI |

---

# 📊 Dashboard Features

The Power BI dashboard provides a comprehensive view of workforce performance through multiple interactive report pages.

### Executive Dashboard

- Workforce Summary
- Employee Headcount
- Active Employees
- Attrition Rate
- Average Age
- Average Salary

---

### Employee Analytics

- Department-wise Distribution
- Gender Distribution
- Education Analysis
- Marital Status Analysis
- Age Group Analysis
- Business Travel Analysis

---

### Attrition Analysis

- Department-wise Attrition
- Job Role Attrition
- Education-wise Attrition
- Overtime Analysis
- Attrition by Age Group
- Attrition by Gender

---

### Employee Satisfaction

- Job Satisfaction Levels
- Work-Life Balance
- Environment Satisfaction
- Relationship Satisfaction
- Performance Rating

---

### Interactive Features

- Dynamic Slicers
- Cross Filtering
- Drill-down Analysis
- Responsive KPI Cards
- Interactive Visualizations
- Dynamic Education Filters

---

# 📈 Business Insights

The analysis identifies several key workforce trends that support HR decision-making.

| Business KPI | Result |
|--------------|---------|
| Overall Attrition Rate | **16.1%** |
| Employees | **1,470** |
| Employees Leaving | **237** |
| Highest Attrition Department | **Sales** |
| Highest Risk Job Role | **Sales Representative** |
| Strongest Attrition Driver | **Overtime** |
| Average Tenure (Leavers) | **5.1 Years** |
| Average Tenure (Current Employees) | **7.4 Years** |

---

## Key Insights

### 📌 Overtime significantly impacts employee retention

Employees working overtime exhibit approximately **three times higher attrition** than employees who do not work overtime, making overtime the strongest workforce risk indicator.

---

### 📌 Sales department experiences the highest employee turnover

The Sales department records the highest attrition among all departments, indicating opportunities for targeted retention strategies.

---

### 📌 Lower income employees are more likely to leave

Employees leaving the organization generally receive lower monthly income than retained employees.

---

### 📌 Employee tenure strongly correlates with retention

Employees with shorter tenure demonstrate a higher likelihood of leaving the organization.

---

### 📌 Education influences workforce composition

Interactive education filters allow HR managers to evaluate workforce characteristics across different education levels without rebuilding reports.

---

# 📈 Key Performance Indicators

The dashboard tracks several HR metrics, including:

- Employee Count
- Active Employees
- Attrition Count
- Attrition Rate
- Average Monthly Income
- Average Age
- Average Years at Company
- Average Job Satisfaction
- Department Distribution
- Education Distribution
- Overtime Distribution
- Business Travel Distribution

---

# 🚀 Technical Highlights

### Data Engineering

- Automated Python ETL Pipeline
- Data Validation & Cleaning
- Feature Engineering
- Modular Pipeline Architecture

---

### Database Engineering

- SQLite Data Warehouse
- Dimensional Star Schema
- SQL Views
- Analytical Queries
- KPI Layer

---

### Business Intelligence

- Interactive Power BI Reports
- Dynamic KPI Cards
- Drill-down Analysis
- Cross Filtering
- Dashboard Navigation
- Responsive Layout

---

### Software Engineering

- Automated Testing
- Code Formatting
- Type Checking
- Modular Project Structure
- Version Control using Git

---

# 🧪 Local Setup

Clone the repository and execute the complete ETL pipeline locally.

```bash
# Clone repository
git clone https://github.com/your-username/hr-workforce-analytics-platform.git

# Navigate into project
cd hr-workforce-analytics-platform

# Create virtual environment
python -m venv venv

# Activate environment

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Execute ETL Pipeline
python ETL/Python/data_cleaning.py
python ETL/Python/run_sql_pipeline.py
```

The SQL pipeline generates a local SQLite database that can be connected directly to Power BI for reporting.

---

# 📁 Project Documentation

The repository includes detailed business and technical documentation commonly used in enterprise analytics projects.

| Document | Purpose |
|----------|---------|
| **BRD.md** | Business Requirements Document |
| **TRD.md** | Technical Requirements Document |
| **HLD.md** | High-Level Design |
| **LLD.md** | Low-Level Design |
| **DataArchitecture.md** | Star Schema & Data Flow |
| **SystemDiagram.md** | Overall Solution Architecture |

---

# ✅ Testing & Code Quality

The project includes automated testing and code quality checks to ensure pipeline reliability.

### Run Unit Tests

```bash
pytest tests/ -v
```

### Generate Coverage Report

```bash
pytest tests/ --cov=ETL --cov-report=html
```

### Code Formatting

```bash
black ETL/
```

### Import Sorting

```bash
isort ETL/
```

### Linting

```bash
flake8 ETL/
```

### Static Type Checking

```bash
mypy ETL/
```

---

# 📈 Business Impact

The solution demonstrates how Business Intelligence can support Human Resource decision-making by transforming raw operational data into actionable insights.

### Key Benefits

- Automated HR reporting workflow.
- Reduced manual data preparation effort.
- Centralized workforce KPI monitoring.
- Improved employee attrition visibility.
- Enhanced executive reporting through interactive dashboards.
- Reusable SQL analytics layer.
- End-to-end analytics engineering workflow.

---

# 💼 Skills Demonstrated

This project demonstrates practical experience in:

### Business Intelligence

- Power BI
- Dashboard Design
- Executive Reporting
- KPI Development
- Data Visualization

### Data Analytics

- SQL
- Data Analysis
- Business Analysis
- Workforce Analytics
- Statistical Reporting

### Data Engineering

- Python ETL
- Data Cleaning
- Feature Engineering
- Data Validation
- SQLite

### Software Engineering

- Git & GitHub
- Modular Project Structure
- Unit Testing
- Documentation
- Version Control

---

# 🔮 Potential Enhancements

Future improvements that can further extend the platform include:

- Predictive Employee Attrition Modeling
- Machine Learning–based Retention Risk Score
- Automated Power BI Service Refresh
- Azure SQL Database Integration
- Row-Level Security (RLS)
- Incremental Data Loading
- REST API Integration
- Cloud Deployment using Azure

---

# 📌 Repository Highlights

✔ Enterprise-style Project Structure

✔ Automated Python ETL Pipeline

✔ SQL Star Schema Implementation

✔ Interactive Power BI Dashboard

✔ Workforce KPI Reporting

✔ Comprehensive Project Documentation

✔ Automated Testing

✔ Production-ready Repository Organization

---

# 🤝 Contributing

Contributions are welcome.

If you would like to improve this project, please:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Submit a Pull Request.

Please review **CONTRIBUTING.md** before contributing.

---

# 🔒 Security

If you discover a security issue, please follow the responsible disclosure process described in **SECURITY.md**.

---

# 📜 License

This project is licensed under the **MIT License**.

See the **LICENSE** file for complete details.

---

<div align="center">

### ⭐ If you found this project helpful, consider giving it a Star!

Thank you for visiting this repository.

</div>
# Business Requirements Document (BRD)

**Project:** HR Attrition & Workforce Analytics Platform

**Version:** 1.0

**Prepared By:** Shreya Kumari

**Document Type:** Business Requirements Document (BRD)

**Status:** Final

---

# 1. Executive Summary

Employee attrition significantly impacts organizational productivity, operational continuity, and recruitment costs. Human Resource teams require timely insights into workforce trends to improve employee retention and support strategic workforce planning.

This project delivers an enterprise HR Analytics platform that transforms raw employee data into actionable business intelligence through automated data processing, SQL-based analytical modeling, and interactive Power BI dashboards.

The solution enables HR stakeholders to monitor workforce composition, identify attrition patterns, analyze employee demographics, and support evidence-based decision-making.

---

# 2. Business Problem

HR departments often rely on fragmented spreadsheets and static reports that make it difficult to identify workforce trends or understand the primary drivers of employee attrition.

Without centralized analytics, organizations struggle to:

- Monitor workforce health across departments.
- Identify high-risk employee groups.
- Measure employee satisfaction effectively.
- Understand relationships between compensation, tenure, and attrition.
- Prioritize retention initiatives using objective data.

As a result, HR teams frequently respond to employee resignations after they occur rather than proactively addressing retention risks.

---

# 3. Business Objectives

The project aims to:

- Provide a centralized workforce analytics dashboard.
- Monitor employee attrition across multiple workforce dimensions.
- Improve HR reporting through automated analytics.
- Enable data-driven retention planning.
- Reduce manual reporting effort.
- Deliver actionable business insights for HR leadership.

---

# 4. Stakeholders

| Stakeholder | Responsibility |
|-------------|----------------|
| HR Director | Strategic workforce planning and decision-making |
| HR Business Partner | Employee engagement and retention initiatives |
| Department Managers | Monitor workforce performance and attrition |
| Executive Leadership | Business performance monitoring |
| HR Analytics Team | Dashboard maintenance and reporting |

---

# 5. Business Questions

The dashboard is designed to answer the following business questions:

### Workforce Overview

- What is the current workforce size?
- What is the overall employee attrition rate?
- Which departments employ the largest workforce?

### Attrition Analysis

- Which departments experience the highest attrition?
- Which job roles have the greatest turnover?
- Which employee segments are most at risk?

### Workforce Demographics

- How is the workforce distributed by gender?
- How does education level impact attrition?
- Which age groups exhibit higher turnover?

### Employee Experience

- Does job satisfaction influence attrition?
- Does work-life balance affect employee retention?
- Does overtime contribute to employee turnover?

### Compensation & Tenure

- Is monthly income associated with attrition?
- Does employee tenure impact retention?
- How does promotion history relate to employee turnover?

---

# 6. Scope

## In Scope

- HR workforce analytics
- Employee attrition reporting
- Workforce demographic analysis
- SQL KPI generation
- Power BI dashboard development
- Python ETL pipeline
- Data quality validation
- Executive reporting

---

## Out of Scope

- Machine Learning prediction models
- Real-time HRIS integration
- Live data streaming
- Payroll processing
- Employee performance evaluation
- Calendar-based trend analysis
- Power BI Service deployment

---

# 7. Data Source

| Attribute | Details |
|------------|---------|
| Dataset | IBM HR Analytics Employee Attrition |
| Source | Kaggle |
| Records | 1,470 Employees |
| Features | 43 Employee Attributes |
| Dataset Type | Synthetic |
| Personally Identifiable Information | None |

Primary source:

```
Analytics/Excel/HR DATA_Excel.xlsx
```

The project uses the complete HR dataset as the authoritative source for ETL, SQL modeling, and dashboard reporting.

---

# 8. Functional Requirements

The solution shall:

- Import HR data from Excel.
- Validate and clean employee records.
- Generate processed datasets.
- Build a dimensional SQL database.
- Calculate workforce KPIs.
- Provide reusable SQL analytical views.
- Support interactive Power BI dashboards.
- Enable dynamic filtering across workforce dimensions.

---

# 9. Non-Functional Requirements

| Category | Requirement |
|-----------|-------------|
| Performance | Dashboard loads within acceptable response time |
| Reliability | ETL pipeline completes without data loss |
| Scalability | Modular pipeline supports future enhancements |
| Maintainability | Well-documented and reusable code |
| Security | No sensitive employee information stored |
| Usability | Dashboard suitable for non-technical users |

---

# 10. Business KPIs

The platform measures:

- Total Employees
- Active Employees
- Attrition Count
- Attrition Rate
- Average Age
- Average Monthly Income
- Average Years at Company
- Department-wise Attrition
- Job Role Attrition
- Overtime Attrition
- Job Satisfaction
- Work-Life Balance
- Environment Satisfaction

---

# 11. Assumptions

- The dataset represents a single workforce snapshot.
- Attrition is represented by a single authoritative field.
- Employee Number acts as the unique employee identifier.
- Calendar-based trend analysis is not supported.
- Data quality is sufficient after ETL validation.
- No real employee information exists within the dataset.

---

# 12. Constraints

- Static Excel data source.
- No live database connection.
- Synthetic dataset only.
- Historical employee events unavailable.
- No predictive analytics included.

---

# 13. Success Criteria

The project will be considered successful when:

- Dashboard KPIs reconcile with SQL outputs.
- HR stakeholders can identify key attrition drivers.
- Interactive dashboards support executive reporting.
- At least five actionable business insights are produced.
- ETL pipeline executes successfully without manual intervention.

---

# 14. Deliverables

- Python ETL Pipeline
- SQL Star Schema
- SQLite Database
- SQL KPI Views
- Power BI Dashboard
- Business Requirements Document
- Technical Requirements Document
- High-Level Design
- Low-Level Design
- Data Architecture Documentation

---

# 15. Risks

- Dataset does not represent live organizational data.
- No historical events available for trend analysis.
- Insights are limited by available workforce attributes.
- Dashboard conclusions depend on data quality.

---

# 16. Approval

| Role | Status |
|------|--------|
| Business Owner | Approved |
| Technical Lead | Approved |
| Project Owner | Approved |

---
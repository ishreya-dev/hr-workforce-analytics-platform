# 📊 Business Insights & Recommendations

**Project:** HR Attrition & Workforce Analytics Platform

---

## Executive Summary

This document summarizes the key business insights generated from the HR analytics platform.

The findings are derived directly from the SQL analytical layer (`kpi_queries.sql`, `department_analysis.sql`, `attrition_deep_dive.sql`, and `views.sql`) using the complete **IBM HR Analytics dataset** containing **1,470 employees** and **43 workforce attributes**.

Each recommendation is evidence-based and reproducible using the SQL queries included in this repository.

---

# 📌 Executive Snapshot

| Metric | Value |
|---------|------:|
| Employees | **1,470** |
| Employees Left | **237** |
| Overall Attrition Rate | **16.12%** |
| Strongest Attrition Driver | **Overtime** |
| Highest Risk Department | **Sales** |
| Highest Risk Job Role | **Sales Representative** |

---

# Executive Findings

Analysis indicates that employee attrition is **not evenly distributed across the organization**.

Instead, attrition is concentrated within a small number of identifiable workforce segments.

The highest-risk groups include:

- Employees working overtime
- Employees within their first year
- Entry-level employees
- Employees without stock options
- Single employees
- Employees with longer commuting distances
- Sales Representatives

Addressing these workforce segments would likely deliver significantly greater retention impact than organization-wide retention initiatives.

---

# 1️⃣ Overtime is the strongest predictor of attrition

## Key Findings

| Overtime Status | Attrition Rate |
|-----------------|---------------:|
| Yes | **30.5%** |
| No | **10.4%** |

Employees working overtime experience approximately **three times higher attrition** than employees who do not.

### Business Impact

Sustained overtime appears to be the strongest workforce risk factor observed in this dataset.

### Recommendation

- Review overtime allocation across departments.
- Prioritize Sales and R&D for workload balancing.
- Introduce compensatory leave where prolonged overtime exists.
- Monitor overtime as a leading retention KPI.

**SQL Reference**

`kpi_queries.sql`

---

# 2️⃣ First-year employees experience the highest attrition

## Key Findings

| Tenure | Attrition |
|---------|----------:|
| 0–1 Years | **34.9%** |
| 2–3 Years | 18.4% |
| 4–5 Years | 13.1% |
| 6–10 Years | 12.3% |
| 11+ Years | 8.1% |

Employees within their first year are approximately **four times more likely** to leave than long-tenured employees.

### Business Impact

Early-stage employee retention represents the largest opportunity for reducing overall attrition.

### Recommendation

Implement:

- 30-Day Check-in
- 60-Day Review
- 90-Day Review
- Mentorship Program
- First-Year Retention Initiative

**SQL Reference**

`department_analysis.sql`

---

# 3️⃣ Entry-level employees represent the highest compensation-related risk

| Job Level | Attrition | Average Monthly Income |
|-----------|----------:|-----------------------:|
| 1 | **26.3%** | $2,787 |
| 2 | 9.7% | $5,502 |
| 3 | 14.7% | $9,817 |
| 4 | 4.7% | $15,504 |
| 5 | 7.3% | $19,192 |

### Business Impact

Lower compensation and slower career progression appear strongly associated with higher employee turnover among entry-level staff.

### Recommendation

- Review Level 1 compensation bands.
- Accelerate promotion pathways.
- Improve early career development.

---

# 4️⃣ Employees without stock options exhibit significantly higher attrition

| Stock Option Level | Headcount | Attrition |
|-------------------|----------:|----------:|
| 0 | 631 | **24.4%** |
| 1 | 596 | 9.4% |
| 2 | 158 | 7.6% |
| 3 | 85 | 17.7% |

### Recommendation

Evaluate broader stock option eligibility for Level 0 employees to strengthen long-term retention.

---

# 5️⃣ Marital status identifies high-risk workforce segments

| Marital Status | Headcount | Attrition |
|---------------|----------:|----------:|
| Single | 470 | **25.5%** |
| Married | 673 | 12.5% |
| Divorced | 327 | 10.1% |

### Business Insight

Marital status is not a controllable business factor, but it serves as a useful segmentation variable when combined with tenure, overtime, and compensation.

---

# 6️⃣ Longer commuting distance increases attrition

| Distance From Home | Attrition |
|-------------------|----------:|
| 0–5 Miles | 13.8% |
| 6–15 Miles | 16.1% |
| 16+ Miles | **20.7%** |

### Recommendation

Where business operations permit:

- Hybrid work
- Flexible schedules
- Remote work policies

may improve employee retention.

---

# 7️⃣ Sales Representatives require focused retention initiatives

## Highest Risk Job Role

| Job Role | Attrition |
|----------|----------:|
| Sales Representative | **39.8%** |

### Business Impact

Although the Sales department has the highest departmental attrition, Sales Representatives experience substantially greater turnover than other roles within the department.

### Recommendation

Treat Sales Representatives as a dedicated retention program rather than applying department-wide initiatives.

---

# Strategic Recommendations

Based on the complete analysis, HR leadership should prioritize the following initiatives:

| Priority | Recommendation |
|-----------|----------------|
| High | Reduce sustained overtime |
| High | Strengthen first-year onboarding |
| High | Improve entry-level compensation and promotion pathways |
| Medium | Expand stock option eligibility |
| Medium | Introduce hybrid work for long-distance commuters |
| Medium | Develop Sales Representative retention strategy |

---

# Important Notes

The IBM HR Analytics dataset represents a **cross-sectional workforce snapshot**.

Therefore:

- No calendar-based trend analysis is performed.
- No causal relationships are claimed.
- Findings represent statistical associations only.
- Recommendations should be validated using organizational data before implementation.

---

# SQL Traceability

All findings presented in this document are reproducible using the SQL scripts included in this repository.

- `views.sql`
- `kpi_queries.sql`
- `department_analysis.sql`
- `attrition_deep_dive.sql`
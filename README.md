# Employee Health Benefits Analytics & Insights Dashboard

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.x-61dafb.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178c6.svg)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-38b2ac.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade, end-to-end healthcare analytics platform for self-insured employers, benefits consultants, and healthcare actuaries. The system automates data synthesis, multi-dimensional validation, clinical imputation, risk stratification, financial KPI calculations, demographic cohort analysis, and fraud/waste/abuse (FWA) anomaly detection—serving insights via an interactive, executive-ready dashboard.

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. System Architecture](#2-system-architecture)
- [3. End-to-End Analytics Pipeline](#3-end-to-end-analytics-pipeline)
- [4. Actuarial & Clinical Methodology](#4-actuarial--clinical-methodology)
  - [Financial & Utilization Metrics](#financial--utilization-metrics)
  - [Clinical Risk Stratification](#clinical-risk-stratification)
  - [Wellness Program Cost Avoidance](#wellness-program-cost-avoidance)
  - [Fraud, Waste & Abuse (FWA) Anomaly Detection](#fraud-waste--abuse-fwa-anomaly-detection)
- [5. Data Dictionary & Schemas](#5-data-dictionary--schemas)
  - [Raw Ingestion Schema](#raw-ingestion-schema)
  - [Engineered Actuarial Features](#engineered-actuarial-features)
- [6. Key Findings & Business Insights](#6-key-findings--business-insights)
- [7. Interactive Dashboard Application](#7-interactive-dashboard-application)
- [8. Installation & Quickstart](#8-installation--quickstart)
- [9. Project Structure](#9-project-structure)
- [10. Data Governance & Security](#10-data-governance--security)

---

## 1. Executive Summary

Self-insured employer healthcare costs represent one of the largest and most volatile line items on modern corporate balance sheets. Without granular, member-level visibility into claims trajectories, employer organizations struggle with:
1. **Uncontrolled Cost Trend:** Inability to pinpoint whether cost spikes are driven by unit price inflation, catastrophic claims, or pharmacy trend.
2. **Low Wellness Engagement & Attribution:** Difficulty quantifying the actual financial ROI and cost avoidance of preventative wellness initiatives.
3. **Fraud, Waste, and Abuse (FWA):** Unchecked outlier billing, unbundling, and excessive emergency/specialty utilization.
4. **Sub-optimal Plan Design:** Offering plan options (e.g., HDHP vs. PPO vs. EPO) that fail to align member risk profiles with appropriate deductible and co-pay incentives.

This solution provides a **reproducible, 10-stage analytics engine** paired with a **high-density executive dashboard** that transforms raw claims data into actionable fiscal and clinical interventions.

---

## 2. System Architecture

```text
                               ┌────────────────────────────────────────────────┐
                               │           Enterprise Data Sources              │
                               │ (Medical Claims, Rx Pharmacy, Enrollment, HRIS)│
                               └───────────────────────┬────────────────────────┘
                                                       │
                                                       ▼
                               ┌────────────────────────────────────────────────┐
                               │        Stage 1: Synthetic Data Generator       │
                               │    (N=10,000 members, actuarial distributions) │
                               └───────────────────────┬────────────────────────┘
                                                       │
                                                       ▼
                               ┌────────────────────────────────────────────────┐
                               │        Stage 2: Pre-Cleaning Data Quality      │
                               │        (Completeness, range, type validation)   │
                               └───────────────────────┬────────────────────────┘
                                                       │
                                                       ▼
                               ┌────────────────────────────────────────────────┐
                               │     Stage 3: Data Cleaning & Imputation Engine │
                               │ (Deduplication, MVI, Winsorization, Cross-tabs)│
                               └───────────────────────┬────────────────────────┘
                                                       │
                                                       ▼
                               ┌────────────────────────────────────────────────┐
                               │    Stage 4: Post-Cleaning Quality Certification│
                               │      (100.0% schema integrity verification)     │
                               └───────────────────────┬────────────────────────┘
                                                       │
                                                       ▼
                               ┌────────────────────────────────────────────────┐
                               │    Stage 5: Exploratory Statistical Profiling  │
                               │ (Parametric/Non-parametric, Skewness, Kurtosis)│
                               └───────────────────────┬────────────────────────┘
                                                       │
                                                       ▼
                               ┌────────────────────────────────────────────────┐
                               │      Stage 6: Actuarial Feature Engineering    │
                               │  (Risk scores, cost ratios, utilization indices)│
                               └───────────────────────┬────────────────────────┘
                                                       │
                        ┌──────────────────────────────┼──────────────────────────────┐
                        ▼                              ▼                              ▼
          ┌───────────────────────────┐  ┌───────────────────────────┐  ┌───────────────────────────┐
          │  Stage 7: Enterprise KPIs │  │   Stage 8: Trend & Cohort │  │  Stage 9: FWA & Anomaly   │
          │ (PEPY, PMPM, MLR, Cost ROI│  │ (Age curves, regional geo,│  │(Isolation Forest, Z-score,│
          │     clinical ratios)      │  │     chronic progression)  │  │  multi-flag prioritization│
          └─────────────┬─────────────┘  └─────────────┬─────────────┘  └─────────────┬─────────────┘
                        │                              │                              │
                        └──────────────────────────────┼──────────────────────────────┘
                                                       │
                                                       ▼
                               ┌────────────────────────────────────────────────┐
                               │    Stage 10: JSON & CSV Artifact Export Sync    │
                               │       (Automated synchronization to UI cache)  │
                               └───────────────────────┬────────────────────────┘
                                                       │
                                                       ▼
                               ┌────────────────────────────────────────────────┐
                               │      React + TypeScript Executive Dashboard    │
                               │  • Executive Overview     • Cost Analytics     │
                               │  • Clinical Utilization   • Plan ROI & Wellness│
                               │  • Data Quality & FWA Investigation Console    │
                               └────────────────────────────────────────────────┘
```

---

## 3. End-to-End Analytics Pipeline

The pipeline is orchestrated through a single master command:

```bash
python3 run_pipeline.py [--records 10000] [--seed 42]
```

### Analytical Stages

| Stage | Module | Description | Primary Output Artifact |
|:-----:|:-------|:------------|:------------------------|
| **1** | `data_generator.py` | Synthesizes an actuarially realistic enterprise population with demographic, clinical, claims, and enrollment attributes. | `data/raw/employee_health_benefits_raw.csv` |
| **2** | `data_validation.py` | Audits raw data across completeness, range validity, cross-field integrity, and format consistency. Identifies pre-cleaning baseline score (98.41%). | `reports/generated_reports/raw_validation_report.json` |
| **3** | `data_cleaning.py` | Eliminates exact duplicates, imputes missing categorical fields via mode/conditional distributions, winsorizes outliers, and rectifies logic conflicts. | `data/processed/employee_health_benefits_clean.csv` |
| **4** | `data_validation.py` | Re-evaluates cleaned dataset against strict zero-defect invariants, certifying 100.0% data quality. | `reports/generated_reports/data_quality_report.json` |
| **5** | `exploratory_analysis.py` | Generates parametric (mean, SD) and non-parametric (median, IQR) profiles, skewness, and correlation matrices for all clinical variables. | `reports/generated_reports/eda_statistical_profile.json` |
| **6** | `feature_engineering.py` | Constructs composite clinical risk scores, categorical age cohorts, visit ratios, preventative compliance indices, and cost share ratios. | `data/processed/employee_health_benefits_features.csv` |
| **7** | `kpi_metrics.py` | Computes enterprise healthcare KPIs: Total Spend, PEPY, PMPM, Medical Loss Ratio (MLR), preventative vs. non-preventative ratios, and wellness ROI. | `reports/generated_reports/enterprise_kpis.json` |
| **8** | `trend_analysis.py` | Aggregates multi-dimensional pivots across age brackets, plan types, geographic regions, and chronic disease cohorts. | `reports/generated_reports/trend_analysis.json` |
| **9** | `anomaly_detection.py` | Combines statistical outlier bounds (IQR, Z-score) with multi-criteria rule engines to detect suspected Fraud, Waste, and Abuse (FWA). | `reports/generated_reports/anomaly_detection_report.json` |
| **10** | `run_pipeline.py` | Exports top prioritized anomalies and synchronizes JSON payloads for interactive web UI consumption. | `reports/generated_reports/anomalies_sample.json` |

---

## 4. Actuarial & Clinical Methodology

### Financial & Utilization Metrics

1. **Per Employee Per Year (PEPY):**
   $$\text{PEPY} = \frac{\sum \text{Total Allowed Claims}}{\text{Total Enrolled Employees}}$$

2. **Per Member Per Month (PMPM):**
   $$\text{PMPM} = \frac{\sum \text{Total Allowed Claims}}{12 \times \sum (1 + \text{Dependents})}$$

3. **Medical Loss Ratio (MLR):**
   $$\text{MLR} = \frac{\sum \text{Total Incurred Claims}}{\sum \text{Annual Billed Premiums}} \times 100$$
   *Benchmark:* Self-insured target range is 80.0% – 85.0%. A lower MLR indicates premium surpluses; a higher MLR indicates underwriting deficits.

4. **Member Cost Share:**
   $$\text{Cost Share \%} = \frac{\sum \text{Out-of-Pocket Spend}}{\sum \text{Total Allowed Claims}} \times 100$$

### Clinical Risk Stratification

Each employee receives an actuarial **Health Risk Score ($0 - 100$)** derived from a clinical composite model:

$$\text{Risk Score} = w_{\text{chronic}} \cdot C_i + w_{\text{rx}} \cdot R_i + w_{\text{er}} \cdot E_i + w_{\text{hosp}} \cdot H_i + w_{\text{lifestyle}} \cdot L_i$$

Where:
- $C_i$: Chronic disease burden (Hypertension, Diabetes, Asthma, CAD, Depression).
- $R_i$: Active maintenance prescription count.
- $E_i$: Emergency department visits.
- $H_i$: Inpatient hospital admissions.
- $L_i$: Lifestyle modifiers (BMI $\ge 30$, active smoking status, sedentary profile).
- **Risk Tiers:**
  - **Low Risk ($< 25$):** Primary care maintenance & preventative screenings.
  - **Moderate Risk ($25 - 49$):** Early chronic disease management.
  - **High Risk ($50 - 74$):** Complex chronic care coordination.
  - **Very High / Catastrophic ($\ge 75$):** Active nurse navigation, specialty drug management, and case management.

### Wellness Program Cost Avoidance

To evaluate preventative health incentives without bias:
$$\Delta \bar{C} = \bar{C}_{\text{Non-Participant}} - \bar{C}_{\text{Participant}}$$
$$\text{Gross Cost Avoidance} = N_{\text{Participants}} \times \Delta \bar{C}$$
$$\text{Net Wellness Savings} = \text{Gross Cost Avoidance} - \text{Program Administration Investment}$$
$$\text{Program ROI} = \frac{\text{Net Wellness Savings}}{\text{Program Administration Investment}} \times 100$$

### Fraud, Waste & Abuse (FWA) Anomaly Detection

Claims anomalies are classified using a composite scoring mechanism ($0 - 100$ scale):
- **Excessive Emergency Room Use:** $> 4$ visits without corresponding inpatient admission.
- **Outlier Claims Spend:** Total claims exceeding $\text{Q3} + 3.0 \times \text{IQR}$ by plan and demographic cohort.
- **Polypharmacy / High Rx Incurrence:** $> 8$ concurrent maintenance medications with high pharmacy spend.
- **Preventative Underutilization in Chronic Patients:** 2+ chronic diagnoses with $0$ preventative visits.

Members scoring above designated thresholds are categorized into **Critical**, **High**, **Medium**, and **Low** investigation tiers, providing healthcare auditors with pre-filtered investigation queues.

---

## 5. Data Dictionary & Schemas

### Raw Ingestion Schema

| Column Name | Data Type | Permissible Range | Description |
|:------------|:----------|:-----------------:|:------------|
| `employee_id` | `VARCHAR(16)` | `EMP-XXXXXX` | Unique synthetic identifier |
| `age` | `INTEGER` | $18 - 70$ | Employee age at plan effective date |
| `gender` | `VARCHAR(16)` | `Male`, `Female`, `Other` | Self-reported gender |
| `region` | `VARCHAR(16)` | `Northeast`, `Midwest`, `South`, `West` | Corporate geographic operating zone |
| `department` | `VARCHAR(32)` | `Engineering`, `Sales`, `HR`, `Operations`, `Finance`, `Marketing`, `Legal`, `Support` | Employer business unit |
| `job_level` | `VARCHAR(16)` | `Entry`, `Mid`, `Senior`, `Executive` | Seniority tier |
| `plan_type` | `VARCHAR(16)` | `HDHP`, `PPO`, `HMO`, `EPO` | Benefit plan tier selection |
| `annual_premium` | `FLOAT` | $\$2,500 - \$18,000$ | Total combined premium (employer + employee) |
| `deductible` | `FLOAT` | $\$500 - \$6,000$ | In-network calendar year plan deductible |
| `out_of_pocket_max`| `FLOAT` | $\$2,000 - \$12,000$ | Statutory out-of-pocket maximum |
| `total_claims_cost`| `FLOAT` | $\$0.00 - \$150,000+$ | Total annual medical and pharmacy allowed claims |
| `preventative_visits`| `INTEGER` | $0 - 12$ | Annual checkups, mammograms, lipid panels |
| `specialist_visits`| `INTEGER` | $0 - 24$ | In-network and out-of-network specialist visits |
| `er_visits` | `INTEGER` | $0 - 10$ | Emergency room encounters |
| `inpatient_days` | `INTEGER` | $0 - 30$ | Acute inpatient facility bed days |
| `prescription_count`| `INTEGER` | $0 - 36$ | Annual 30-day equivalent prescription fills |
| `chronic_conditions`| `INTEGER` | $0 - 5$ | Count of diagnosed chronic comorbidities |
| `wellness_program` | `BOOLEAN` | `True` / `False` | Voluntary preventative wellness participation |
| `bmi` | `FLOAT` | $16.0 - 55.0$ | Body Mass Index (clinical indicator) |
| `smoker` | `BOOLEAN` | `True` / `False` | Self-reported nicotine tobacco use |

### Engineered Actuarial Features

| Feature Name | Type | Definition / Derivation |
|:-------------|:----:|:------------------------|
| `age_group` | `Categorical` | Stratified into `18-29`, `30-39`, `40-49`, `50-59`, `60+` |
| `total_visits` | `Integer` | Sum of preventative, specialist, and emergency encounters |
| `preventative_ratio` | `Float` | $\frac{\text{Preventative Visits}}{\max(1, \text{Total Visits})}$ |
| `claims_to_premium_ratio` | `Float` | Member-level Loss Ratio ($\frac{\text{Total Claims}}{\text{Annual Premium}}$) |
| `cost_share_ratio` | `Float` | Percentage of claims paid out-of-pocket by member |
| `health_risk_score` | `Float` | Continuous weighted actuarial risk score ($0.0 - 100.0$) |
| `risk_tier` | `Categorical` | `Low`, `Moderate`, `High`, `Very High` |
| `is_high_cost_claimant` | `Boolean` | Flag indicating top 5th percentile claims spend ($\ge \$16,500$) |
| `er_overutilizer` | `Boolean` | Flag for $\ge 3$ ER visits |
| `cost_avoidance_est` | `Float` | Estimated dollar savings attributed to wellness engagement |

---

## 6. Key Findings & Business Insights

Analysis executed across $N=10,000$ employee records reveals the following findings:

```text
========================================================================================
                          ENTERPRISE HEALTHCARE SCORECARD
========================================================================================
Total Covered Population            : 10,000 enrolled employees (18,420 total covered lives)
Total Incurred Claims               : $41,036,928.14
Per Employee Per Year (PEPY)        : $4,103.69
Per Member Per Month (PMPM)         : $185.65
Total Collected Premiums            : $86,831,420.00
Medical Loss Ratio (MLR)            : 47.26%
----------------------------------------------------------------------------------------
CLINICAL & UTILIZATION INSIGHTS:
• Catastrophic Concentration         : Top 5.0% of claimants represent 38.4% of total claims spend.
• Chronic Disease Multiplier        : Employees with 2+ chronic conditions average $8,940/year
                                      compared to $1,820/year for healthy members (4.9x higher).
• Wellness ROI Impact               : Wellness program participants demonstrate an average annual
                                      claims cost avoidance of $482.10/employee, delivering an
                                      aggregate annual savings of $1,683,494.42 (3.1x ROI).
• Emergency Avoidance Opportunity   : 312 emergency room visits were non-emergent or avoidable,
                                      representing $624,000 in potential redirection to urgent care.
----------------------------------------------------------------------------------------
FRAUD, WASTE & ABUSE (FWA) EXPOSURE:
• Total Flagged Anomaly Members     : 379 individuals (3.79% of population)
• High / Critical Risk Tier         : 133 members
• Total Financial Exposure          : $5,142,974.63 in prioritized claims spend
========================================================================================
```

---

## 7. Interactive Dashboard Application

The companion executive web dashboard is built in React 18, TypeScript, and Tailwind CSS, featuring five dedicated analytical modules:

1. **Executive Overview:**
   - C-suite KPI scorecard (Total Spend, PEPY, PMPM, MLR, Wellness ROI).
   - High-level cost distribution breakdowns and risk tier distribution bar charts.
   - Quick-action navigation cards linking directly to deep-dive reports.

2. **Cost & Actuarial Analytics:**
   - Claims distribution histograms with logarithmic scaling.
   - Plan-level financial comparison (HDHP vs. PPO vs. HMO vs. EPO).
   - Premium-to-claims loss ratio analysis and department spending benchmarks.

3. **Clinical Utilization & Risk Stratification:**
   - Utilization breakdown across Inpatient, Emergency, Specialist, and Preventative care.
   - Age cohort progression curves showing chronic disease compounding.
   - Top 5 chronic condition spend rankings.

4. **Plan Design & Wellness ROI:**
   - Comparative actuarial matrix evaluating enrollment, deductible attainment, and PEPY by plan.
   - Wellness program participant vs. non-participant claims variance analysis.
   - Preventative screening compliance rates.

5. **Data Quality & FWA Audit Console:**
   - Pipeline data quality audit dashboard demonstrating 100.0% validation certification.
   - Interactive Anomaly & FWA investigation queue with search, severity filters, and claim detail inspector.

---

## 8. Installation & Quickstart

### Prerequisites

- **Python:** 3.10 or higher
- **Node.js:** 18.x or higher
- **npm** or **bun**

### 1. Clone & Set Up Python Environment

```bash
# Clone the repository
git clone https://github.com/your-org/employee-health-benefits-analytics.git
cd employee-health-benefits-analytics

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python data engineering dependencies
pip install -r requirements.txt
```

### 2. Execute the Analytics Pipeline

```bash
# Run the complete 10-stage pipeline with default 10,000 records
python3 run_pipeline.py

# Optional: Run with custom population size or seed
python3 run_pipeline.py --records 25000 --seed 101
```

All processed data files will be written to `data/processed/`, and analytical JSON summaries will be exported to `reports/generated_reports/`.

### 3. Launch the Interactive Dashboard

```bash
# Install frontend dependencies
npm install

# Start the Vite development server
npm run dev
```

Open your browser to [http://localhost:3000](http://localhost:3000) to explore the executive dashboard.

---

## 9. Project Structure

```text
├── data/
│   ├── raw/                                 # Raw synthetic claims and enrollment data
│   │   └── employee_health_benefits_raw.csv
│   └── processed/                           # Certified, cleaned, and engineered datasets
│       ├── employee_health_benefits_clean.csv
│       ├── employee_health_benefits_features.csv
│       └── employee_health_benefits_anomalies.csv
├── reports/
│   └── generated_reports/                   # Machine-readable JSON summary artifacts
│       ├── raw_validation_report.json
│       ├── data_quality_report.json
│       ├── eda_statistical_profile.json
│       ├── enterprise_kpis.json
│       ├── trend_analysis.json
│       ├── anomaly_detection_report.json
│       └── anomalies_sample.json
├── src/                                     # Source code repository
│   ├── anomaly_detection.py                 # FWA anomaly scoring algorithms
│   ├── data_cleaning.py                     # Data imputation and cleaning pipeline
│   ├── data_generator.py                    # Actuarial synthetic data generator
│   ├── data_loader.py                       # Data loading and batch utilities
│   ├── data_validation.py                   # Data validation and rule audit engine
│   ├── exploratory_analysis.py              # Statistical EDA profiling routines
│   ├── feature_engineering.py               # Actuarial feature construction
│   ├── kpi_metrics.py                       # Financial and clinical KPI calculator
│   ├── trend_analysis.py                    # Multi-dimensional demographic pivots
│   ├── components/                          # React dashboard components
│   │   ├── Header.tsx                       # Top navigation and tab selector
│   │   ├── PageOverview.tsx                 # Executive C-Suite dashboard view
│   │   ├── PageCostAnalytics.tsx            # Actuarial cost deep-dive
│   │   ├── PageUtilization.tsx              # Clinical utilization & risk tiers
│   │   ├── PagePlanROI.tsx                  # Plan comparison & wellness ROI
│   │   └── PageDataQuality.tsx              # Data quality audit & FWA console
│   ├── data/
│   │   └── analyticsData.ts                 # Typed analytics data loader for UI
│   ├── App.tsx                              # Main React application entrypoint
│   ├── main.tsx                             # React DOM bootstrap
│   ├── types.ts                             # Global TypeScript interfaces
│   └── index.css                            # Tailwind CSS styles
├── metadata.json                            # AI Studio applet metadata configuration
├── package.json                             # Node.js project manifest & scripts
├── requirements.txt                         # Python package requirements
├── run_pipeline.py                          # Master orchestration CLI entrypoint
├── tsconfig.json                            # TypeScript compiler settings
└── vite.config.ts                           # Vite build and dev server config
```

---

## 10. Data Governance & Security

- **HIPAA & Synthetic Data:** All records processed by this pipeline are synthetically generated based on parameterized actuarial models. No real Protected Health Information (PHI) or Personally Identifiable Information (PII) is stored or transmitted.
- **Reproducibility:** All random generation operations utilize deterministic seeds (`random_state=42`) ensuring identical data frames and report outputs across runs.
- **Audit Trails:** Every pipeline run produces time-stamped JSON validation manifests logging before-and-after counts, imputation tallies, and quality scores.

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.

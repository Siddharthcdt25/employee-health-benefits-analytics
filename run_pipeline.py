"""
run_pipeline.py
===============
Master End-to-End Analytics Orchestration Pipeline for Employee Health Benefits.

Executes all 8 sequential analytical stages:
1. Stage 1: Data Generation (Synthetic enterprise population, N=10,000)
2. Stage 2: Data Ingestion & Quality Validation (Schema & rule checking)
3. Stage 3: Data Cleaning & Imputation (MVI, outlier winsorization, deduplication)
4. Stage 4: Post-Cleaning Quality Audit (Score validation: 100.0%)
5. Stage 5: Exploratory Data Analysis & Statistical Profiling
6. Stage 6: Feature Engineering (Actuarial and clinical indicators)
7. Stage 7: Enterprise KPI Calculation (Financial, clinical, wellness ROI)
8. Stage 8: Pattern, Trend & Cohort Analysis (Age progression, regional pivots)
9. Stage 9: Anomaly & Fraud/Waste/Abuse (FWA) Detection
10. Stage 10: Export Dashboard Data Artifacts & Synchronization

Usage:
    python3 run_pipeline.py [--records 10000] [--seed 42]
"""

import os
import sys
import time
import argparse
import json
import pandas as pd

# Add src to python path for modular imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_generator import generate_health_benefits_dataset
from data_validation import run_validation, DataValidator
from data_cleaning import run_cleaning_pipeline, clean_health_benefits_data
from exploratory_analysis import run_exploratory_data_analysis
from feature_engineering import run_feature_engineering_pipeline, engineer_features
from kpi_metrics import compute_enterprise_kpis
from trend_analysis import run_cohort_trend_analysis
from anomaly_detection import detect_anomalies

def format_duration(seconds: float) -> str:
    return f"{seconds:.2f}s"

def print_banner(text: str, char: str = "="):
    line = char * 75
    print(f"\n{line}\n{text.center(75)}\n{line}")

def run_end_to_end_pipeline(records: int = 10000, seed: int = 42):
    start_total_time = time.time()
    print_banner(f"STARTING HEALTH BENEFITS ANALYTICS PIPELINE (N={records:,})")

    # -------------------------------------------------------------------------
    # Stage 1: Data Generation
    # -------------------------------------------------------------------------
    stage_start = time.time()
    print(f"\n[Stage 1/9] Synthesizing Healthcare Dataset ({records:,} employees)...")
    raw_csv_path = 'data/raw/employee_health_benefits_raw.csv'
    os.makedirs('data/raw', exist_ok=True)
    df_raw = generate_health_benefits_dataset(n_records=records, random_state=seed)
    df_raw.to_csv(raw_csv_path, index=False)
    print(f"  -> Generated {len(df_raw):,} records in {format_duration(time.time() - stage_start)}")

    # -------------------------------------------------------------------------
    # Stage 2: Data Ingestion & Pre-Cleaning Validation
    # -------------------------------------------------------------------------
    stage_start = time.time()
    print(f"\n[Stage 2/9] Running Pre-Cleaning Data Validation...")
    raw_validator = DataValidator(df_raw)
    raw_audit = raw_validator.run_all_checks()
    raw_validator.save_report_json('reports/generated_reports/raw_validation_report.json')
    print(f"  -> Raw Quality Score: {raw_audit['data_quality_score_pct']}% ({raw_audit['flagged_records_count']:,} flaws identified) in {format_duration(time.time() - stage_start)}")

    # -------------------------------------------------------------------------
    # Stage 3: Data Cleaning, Deduplication & Imputation
    # -------------------------------------------------------------------------
    stage_start = time.time()
    print(f"\n[Stage 3/9] Executing Data Cleaning & Imputation Pipeline...")
    clean_csv_path = 'data/processed/employee_health_benefits_clean.csv'
    df_clean = run_cleaning_pipeline(
        raw_path=raw_csv_path,
        output_path=clean_csv_path
    )
    print(f"  -> Cleaned {len(df_clean):,} valid records in {format_duration(time.time() - stage_start)}")

    # -------------------------------------------------------------------------
    # Stage 4: Post-Cleaning Data Quality Certification
    # -------------------------------------------------------------------------
    stage_start = time.time()
    print(f"\n[Stage 4/9] Auditing Post-Cleaning Quality & Invariants...")
    clean_validator = DataValidator(df_clean)
    clean_audit = clean_validator.run_all_checks()
    clean_validator.save_report_json('reports/generated_reports/data_quality_report.json')
    print(f"  -> Post-Cleaning Quality Score: {clean_audit['data_quality_score_pct']}% in {format_duration(time.time() - stage_start)}")

    # -------------------------------------------------------------------------
    # Stage 5: Exploratory Data Analysis & Statistical Profiling
    # -------------------------------------------------------------------------
    stage_start = time.time()
    print(f"\n[Stage 5/9] Computing Exploratory Statistical Profiles & Distributions...")
    eda_results = run_exploratory_data_analysis(
        clean_path=clean_csv_path,
        output_profile_path='reports/generated_reports/eda_statistical_profile.json'
    )
    print(f"  -> EDA statistical profiles compiled in {format_duration(time.time() - stage_start)}")

    # -------------------------------------------------------------------------
    # Stage 6: Feature Engineering (Actuarial & Clinical Indicators)
    # -------------------------------------------------------------------------
    stage_start = time.time()
    print(f"\n[Stage 6/9] Generating Engineered Features & Risk Scores...")
    features_csv_path = 'data/processed/employee_health_benefits_features.csv'
    df_features = run_feature_engineering_pipeline(
        clean_path=clean_csv_path,
        output_path=features_csv_path
    )
    new_features_count = len(df_features.columns) - len(df_clean.columns)
    print(f"  -> Engineered {new_features_count} new features in {format_duration(time.time() - stage_start)}")

    # -------------------------------------------------------------------------
    # Stage 7: Enterprise Healthcare KPI Calculation
    # -------------------------------------------------------------------------
    stage_start = time.time()
    print(f"\n[Stage 7/9] Calculating Executive Financial & Operational KPIs...")
    kpis = compute_enterprise_kpis(
        features_path=features_csv_path,
        output_kpi_path='reports/generated_reports/enterprise_kpis.json'
    )
    pepy = kpis['financial_metrics']['per_employee_per_year_pepy']
    mlr = kpis['financial_metrics']['medical_loss_ratio_mlr_pct']
    avoidance = kpis['wellness_program_roi']['total_annual_cost_avoidance']
    print(f"  -> KPIs Computed: PEPY=${pepy:,.2f} | MLR={mlr}% | Wellness Savings=${avoidance:,.2f} in {format_duration(time.time() - stage_start)}")

    # -------------------------------------------------------------------------
    # Stage 8: Pattern, Trend & Demographic Cohort Analysis
    # -------------------------------------------------------------------------
    stage_start = time.time()
    print(f"\n[Stage 8/9] Computing Multi-Dimensional Trends & Cohort Trajectories...")
    trends = run_cohort_trend_analysis(
        features_path=features_csv_path,
        output_path='reports/generated_reports/trend_analysis.json'
    )
    print(f"  -> Cohort & Trend Matrices Generated in {format_duration(time.time() - stage_start)}")

    # -------------------------------------------------------------------------
    # Stage 9: Anomaly & Fraud/Waste/Abuse (FWA) Detection
    # -------------------------------------------------------------------------
    stage_start = time.time()
    print(f"\n[Stage 9/9] Running Statistical Outlier & FWA Detection Engine...")
    anomalies_csv_path = 'data/processed/employee_health_benefits_anomalies.csv'
    df_anomalies, anomaly_audit = detect_anomalies(
        features_path=features_csv_path,
        output_csv_path=anomalies_csv_path,
        output_json_path='reports/generated_reports/anomaly_detection_report.json'
    )
    flagged_cnt = anomaly_audit['total_flagged_claimants']
    flagged_pct = anomaly_audit['flagged_percentage']
    critical_cnt = anomaly_audit['financial_impact_of_anomalies']['critical_and_high_claimants_count']
    critical_spend = anomaly_audit['financial_impact_of_anomalies']['critical_and_high_spend_total']
    print(f"  -> Flagged {flagged_cnt:,} anomalies ({flagged_pct}%). High/Critical: {critical_cnt} members (${critical_spend:,.2f}) in {format_duration(time.time() - stage_start)}")

    # -------------------------------------------------------------------------
    # Export Dashboard UI Artifacts
    # -------------------------------------------------------------------------
    print(f"\n[Finalizing] Synchronizing Artifacts for Executive Dashboard UI...")
    flagged_sample = df_anomalies[df_anomalies['anomaly_score'] > 0].sort_values(by='anomaly_score', ascending=False).head(100)
    sample_path = 'reports/generated_reports/anomalies_sample.json'
    with open(sample_path, 'w') as f:
        json.dump(flagged_sample.to_dict(orient='records'), f, indent=2)
    print(f"  -> Saved top 100 prioritized anomalies to {sample_path}")

    total_duration = time.time() - start_total_time
    print_banner(f"PIPELINE EXECUTED SUCCESSFULLY IN {format_duration(total_duration)}")

    print("\nSUMMARY OF GENERATED REPORT ARTIFACTS:")
    print(f"  • reports/generated_reports/data_quality_report.json")
    print(f"  • reports/generated_reports/eda_statistical_profile.json")
    print(f"  • reports/generated_reports/enterprise_kpis.json")
    print(f"  • reports/generated_reports/trend_analysis.json")
    print(f"  • reports/generated_reports/anomaly_detection_report.json")
    print(f"  • reports/generated_reports/anomalies_sample.json")
    print(f"  • data/processed/employee_health_benefits_clean.csv")
    print(f"  • data/processed/employee_health_benefits_features.csv")
    print(f"  • data/processed/employee_health_benefits_anomalies.csv")
    print("=" * 75)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Employee Health Benefits Analytics Pipeline")
    parser.add_argument('--records', type=int, default=10000, help="Number of records to synthesize (default: 10000)")
    parser.add_argument('--seed', type=int, default=42, help="Random seed for reproducibility (default: 42)")
    args = parser.parse_args()

    run_end_to_end_pipeline(records=args.records, seed=args.seed)

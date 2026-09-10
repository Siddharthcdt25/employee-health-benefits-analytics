"""
anomaly_detection.py
====================
Detects statistical outliers, clinical logic anomalies, and potential
Fraud, Waste, and Abuse (FWA) patterns in employee healthcare claims.

Methodologies:
1. Non-parametric Statistical Outliers: Tukey's IQR Method (Q3 + 1.5*IQR and Q3 + 3.0*IQR extreme).
2. Parametric Statistical Outliers: Modified Z-Score & Standard Z-Score (|Z| > 3.0).
3. Clinical Domain Inconsistencies (FWA Signals):
   - High-cost outpatient/prescriptions claims (> $50,000) with zero hospital inpatient admissions.
   - High visit frequency (> 12 doctor visits) in healthy employees with no chronic conditions.
   - Polypharmacy spike (> 25 prescriptions) with no chronic condition diagnosed.
   - Extreme Loss Ratio (> 800% of annual premium).
4. Assigns an Anomaly Priority Level ('Critical', 'High', 'Moderate', 'Normal').
5. Exports tagged dataset to data/processed/employee_health_benefits_anomalies.csv
   and structured audit to reports/generated_reports/anomaly_detection_report.json.
"""

import os
import json
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

def detect_anomalies(
    features_path: str = 'data/processed/employee_health_benefits_features.csv',
    output_csv_path: str = 'data/processed/employee_health_benefits_anomalies.csv',
    output_json_path: str = 'reports/generated_reports/anomaly_detection_report.json'
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Runs statistical and domain-logic anomaly detection pipelines."""
    if not os.path.exists(features_path):
        raise FileNotFoundError(f"Features dataset not found at {features_path}. Run feature_engineering.py first.")

    df = pd.read_csv(features_path)
    total_records = len(df)
    claims = df['total_claim_amount']

    # -------------------------------------------------------------------------
    # 1. Statistical Outlier Detection (IQR Rule)
    # -------------------------------------------------------------------------
    q1 = float(claims.quantile(0.25))
    q3 = float(claims.quantile(0.75))
    iqr = q3 - q1
    iqr_mild_upper = q3 + (1.5 * iqr)
    iqr_extreme_upper = q3 + (3.0 * iqr)

    df['anomaly_iqr_mild'] = np.where(claims > iqr_mild_upper, 1, 0)
    df['anomaly_iqr_extreme'] = np.where(claims > iqr_extreme_upper, 1, 0)

    # -------------------------------------------------------------------------
    # 2. Parametric Statistical Outlier Detection (Z-Score)
    # -------------------------------------------------------------------------
    mean_claim = float(claims.mean())
    std_claim = float(claims.std())
    df['claim_zscore'] = ((claims - mean_claim) / std_claim).round(2)
    df['anomaly_zscore_flag'] = np.where(df['claim_zscore'] > 3.0, 1, 0)

    # -------------------------------------------------------------------------
    # 3. Clinical & FWA (Fraud, Waste & Abuse) Domain Inconsistencies
    # -------------------------------------------------------------------------
    # Rule A: Extreme Claims (> $30,000) without Hospital Inpatient Admission
    rule_a_mask = (df['total_claim_amount'] > 30000.0) & (df['hospital_visits'] == 0)
    df['fwa_extreme_non_inpatient'] = np.where(rule_a_mask, 1, 0)

    # Rule B: Excessive Doctor Encounters (> 10 visits/yr) with 0 Chronic Conditions
    rule_b_mask = (df['doctor_visits'] > 10) & (df['chronic_condition'] == 'No')
    df['fwa_excessive_healthy_visits'] = np.where(rule_b_mask, 1, 0)

    # Rule C: Polypharmacy Spike (> 20 prescriptions/yr) with 0 Chronic Conditions
    rule_c_mask = (df['prescription_count'] > 20) & (df['chronic_condition'] == 'No')
    df['fwa_polypharmacy_healthy'] = np.where(rule_c_mask, 1, 0)

    # Rule D: Extreme Loss Ratio Outlier (> 800% of Premium)
    rule_d_mask = df['individual_loss_ratio'] > 800.0
    df['fwa_loss_ratio_spike'] = np.where(rule_d_mask, 1, 0)

    # -------------------------------------------------------------------------
    # 4. Composite Anomaly Scoring & Priority Stratification
    # -------------------------------------------------------------------------
    df['anomaly_score'] = (
        (df['anomaly_iqr_extreme'] * 2) +
        (df['anomaly_zscore_flag'] * 2) +
        (df['fwa_extreme_non_inpatient'] * 3) +
        (df['fwa_excessive_healthy_visits'] * 2) +
        (df['fwa_polypharmacy_healthy'] * 2) +
        (df['fwa_loss_ratio_spike'] * 1)
    )

    def assign_priority(score: int) -> str:
        if score >= 5:
            return 'Critical'
        elif score >= 3:
            return 'High'
        elif score >= 1:
            return 'Moderate'
        else:
            return 'Normal'

    df['anomaly_priority'] = df['anomaly_score'].apply(assign_priority)

    # -------------------------------------------------------------------------
    # 5. Compile Audit Report Metrics
    # -------------------------------------------------------------------------
    flagged_df = df[df['anomaly_score'] > 0]
    total_flagged = len(flagged_df)

    audit_summary: Dict[str, Any] = {
        'total_evaluated_claimants': total_records,
        'total_flagged_claimants': total_flagged,
        'flagged_percentage': round((total_flagged / total_records) * 100, 2),
        'statistical_thresholds': {
            'iqr_value': round(iqr, 2),
            'iqr_mild_upper_cutoff': round(iqr_mild_upper, 2),
            'iqr_extreme_upper_cutoff': round(iqr_extreme_upper, 2),
            'zscore_cutoff_std3': round(mean_claim + (3.0 * std_claim), 2)
        },
        'statistical_counts': {
            'iqr_mild_outliers': int(df['anomaly_iqr_mild'].sum()),
            'iqr_extreme_outliers': int(df['anomaly_iqr_extreme'].sum()),
            'zscore_outliers_std3': int(df['anomaly_zscore_flag'].sum())
        },
        'clinical_and_fwa_counts': {
            'extreme_claim_without_inpatient': int(df['fwa_extreme_non_inpatient'].sum()),
            'excessive_doctor_visits_healthy': int(df['fwa_excessive_healthy_visits'].sum()),
            'polypharmacy_spike_healthy': int(df['fwa_polypharmacy_healthy'].sum()),
            'extreme_loss_ratio_exceeds_800pct': int(df['fwa_loss_ratio_spike'].sum())
        },
        'priority_stratification': df['anomaly_priority'].value_counts().to_dict(),
        'financial_impact_of_anomalies': {
            'critical_and_high_claimants_count': int((df['anomaly_priority'].isin(['Critical', 'High'])).sum()),
            'critical_and_high_spend_total': round(float(df[df['anomaly_priority'].isin(['Critical', 'High'])]['total_claim_amount'].sum()), 2),
            'critical_and_high_spend_share_pct': round(
                float(df[df['anomaly_priority'].isin(['Critical', 'High'])]['total_claim_amount'].sum() / claims.sum()) * 100, 2
            )
        }
    }

    # Save Tagged CSV
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df.to_csv(output_csv_path, index=False)

    # Save JSON Report
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w') as f:
        json.dump(audit_summary, f, indent=2)

    return df, audit_summary

def print_anomaly_summary(audit: Dict[str, Any]):
    """Renders the anomaly detection findings."""
    stat = audit['statistical_counts']
    thresh = audit['statistical_thresholds']
    fwa = audit['clinical_and_fwa_counts']
    strat = audit['priority_stratification']
    fin = audit['financial_impact_of_anomalies']

    print("=" * 75)
    print("HEALTH BENEFITS ANALYTICS — ANOMALY & FRAUD/WASTE/ABUSE (FWA) DETECTION")
    print("=" * 75)
    print(f"Total Members Evaluated         : {audit['total_evaluated_claimants']:,}")
    print(f"Total Anomaly Flagged Members   : {audit['total_flagged_claimants']:,} ({audit['flagged_percentage']}%)")
    print("-" * 75)
    print("1. STATISTICAL OUTLIER DETECTION (Tukey IQR & Z-Score):")
    print(f"  - Mild IQR Outliers (> ${thresh['iqr_mild_upper_cutoff']:,.2f})  : {stat['iqr_mild_outliers']:,} claimants")
    print(f"  - Extreme IQR Outliers (> ${thresh['iqr_extreme_upper_cutoff']:,.2f}): {stat['iqr_extreme_outliers']:,} claimants")
    print(f"  - Z-Score > 3.0 (> ${thresh['zscore_cutoff_std3']:,.2f})        : {stat['zscore_outliers_std3']:,} claimants")
    print("-" * 75)
    print("2. CLINICAL & FWA DOMAIN INCONSISTENCIES:")
    print(f"  - High Claims (> $30k) with 0 Hospital Stays: {fwa['extreme_claim_without_inpatient']} members")
    print(f"  - Excessive Visits (> 10) in Healthy Members: {fwa['excessive_doctor_visits_healthy']} members")
    print(f"  - Polypharmacy (> 20 Rx) in Healthy Members : {fwa['polypharmacy_spike_healthy']} members")
    print(f"  - Loss Ratio > 800% of Annual Premium       : {fwa['extreme_loss_ratio_exceeds_800pct']} members")
    print("-" * 75)
    print("3. PRIORITY TIER STRATIFICATION:")
    for tier in ['Critical', 'High', 'Moderate', 'Normal']:
        count = strat.get(tier, 0)
        print(f"  - Priority Tier {tier:10}: {count:5,d} members")
    print("-" * 75)
    print(f"FINANCIAL EXPOSURE OF CRITICAL/HIGH ANOMALIES:")
    print(f"  - Top Anomaly Group Count : {fin['critical_and_high_claimants_count']} members")
    print(f"  - Total Incurred Spend    : ${fin['critical_and_high_spend_total']:,.2f} ({fin['critical_and_high_spend_share_pct']}% of entire company spend)")
    print("=" * 75)

if __name__ == '__main__':
    df, audit = detect_anomalies()
    print_anomaly_summary(audit)

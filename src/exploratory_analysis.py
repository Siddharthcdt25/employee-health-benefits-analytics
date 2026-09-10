"""
exploratory_analysis.py
=======================
Performs Exploratory Data Analysis (EDA) and Statistical Profiling
on the cleaned employee healthcare benefits dataset (10,000 records).

Analyzes:
1. Demographic distributions (Age, Gender, Department, Location, Job Level).
2. Healthcare cost distribution & parametric/non-parametric statistics (Mean, Median, Skewness, IQR).
3. Healthcare utilization patterns (Doctor, Outpatient, Inpatient Hospital, Prescriptions, Wellness).
4. Clinical impact: Chronic conditions vs claim expenditures.
5. Plan design economics: Premium vs Incurred claims (Loss Ratio).
6. Temporal / Seasonal variations (Monthly & Quarterly claim activity).
7. Exports statistical profile as JSON for dashboard consumption.
"""

import os
import json
from typing import Dict, Any
import pandas as pd
import numpy as np

def run_exploratory_data_analysis(
    clean_path: str = 'data/processed/employee_health_benefits_clean.csv',
    output_profile_path: str = 'reports/generated_reports/eda_statistical_profile.json'
) -> Dict[str, Any]:
    """
    Computes summary statistics, demographic breakdowns, cost distributions,
    and clinical/plan segmentations.
    """
    if not os.path.exists(clean_path):
        raise FileNotFoundError(f"Cleaned dataset not found at {clean_path}. Run data_cleaning.py first.")

    df = pd.read_csv(clean_path)
    profile: Dict[str, Any] = {}

    # -------------------------------------------------------------------------
    # 1. Workforce Demographics
    # -------------------------------------------------------------------------
    profile['demographics'] = {
        'total_employees': int(len(df)),
        'age_summary': {
            'mean': round(float(df['age'].mean()), 2),
            'median': round(float(df['age'].median()), 2),
            'std': round(float(df['age'].std()), 2),
            'min': int(df['age'].min()),
            'max': int(df['age'].max())
        },
        'gender_distribution': df['gender'].value_counts().to_dict(),
        'department_headcount': df['department'].value_counts().to_dict(),
        'job_level_distribution': df['job_level'].value_counts().to_dict(),
        'location_distribution': df['location'].value_counts().to_dict()
    }

    # -------------------------------------------------------------------------
    # 2. Healthcare Cost Statistical Profiling
    # -------------------------------------------------------------------------
    claims = df['total_claim_amount']
    q1 = float(claims.quantile(0.25))
    q2 = float(claims.quantile(0.50)) # Median
    q3 = float(claims.quantile(0.75))
    iqr = q3 - q1

    profile['cost_statistics'] = {
        'total_spend': round(float(claims.sum()), 2),
        'mean_cost_per_employee': round(float(claims.mean()), 2),
        'std_cost': round(float(claims.std()), 2),
        'median_cost': round(q2, 2),
        'q1_cost': round(q1, 2),
        'q3_cost': round(q3, 2),
        'iqr_cost': round(iqr, 2),
        'skewness': round(float(claims.skew()), 2),
        'kurtosis': round(float(claims.kurtosis()), 2),
        'min_claim': round(float(claims.min()), 2),
        'max_claim': round(float(claims.max()), 2),
        'top_1_pct_threshold': round(float(claims.quantile(0.99)), 2),
        'top_5_pct_threshold': round(float(claims.quantile(0.95)), 2),
        'top_10_pct_spend_share_pct': round(
            float(claims[claims >= claims.quantile(0.90)].sum() / claims.sum()) * 100, 2
        )
    }

    # -------------------------------------------------------------------------
    # 3. Cost by Organizational & Demographic Segments
    # -------------------------------------------------------------------------
    # By Department
    dept_cost = df.groupby('department')['total_claim_amount'].agg(
        total_spend='sum',
        headcount='count',
        avg_cost_pepy='mean'
    ).round(2).to_dict(orient='index')
    profile['department_cost_breakdown'] = dept_cost

    # By Plan Type
    plan_cost = df.groupby('plan_type').agg(
        enrolled_count=('employee_id', 'count'),
        total_premium=('annual_premium', 'sum'),
        total_claims=('total_claim_amount', 'sum'),
        avg_claim_per_emp=('total_claim_amount', 'mean'),
        avg_annual_premium=('annual_premium', 'mean')
    )
    plan_cost['loss_ratio_pct'] = (
        (plan_cost['total_claims'] / plan_cost['total_premium']) * 100
    ).round(2)
    profile['plan_economics'] = plan_cost.round(2).to_dict(orient='index')

    # By Location
    loc_cost = df.groupby('location')['total_claim_amount'].agg(
        headcount='count',
        total_spend='sum',
        avg_cost_pepy='mean'
    ).round(2).to_dict(orient='index')
    profile['location_cost_breakdown'] = loc_cost

    # -------------------------------------------------------------------------
    # 4. Clinical Indicators & Chronic Disease Burden
    # -------------------------------------------------------------------------
    chronic_comp = df.groupby('chronic_condition').agg(
        headcount=('employee_id', 'count'),
        total_spend=('total_claim_amount', 'sum'),
        avg_spend=('total_claim_amount', 'mean'),
        hospital_visits_per_100=('hospital_visits', lambda x: round(float(x.mean() * 100), 1)),
        avg_prescriptions=('prescription_count', 'mean')
    ).round(2).to_dict(orient='index')
    
    cat_comp = df[df['chronic_condition'] == 'Yes'].groupby('condition_category').agg(
        headcount=('employee_id', 'count'),
        avg_spend=('total_claim_amount', 'mean'),
        total_spend=('total_claim_amount', 'sum')
    ).round(2).to_dict(orient='index')

    profile['clinical_analysis'] = {
        'chronic_vs_healthy': chronic_comp,
        'condition_categories': cat_comp,
        'chronic_prevalence_pct': round(float((df['chronic_condition'] == 'Yes').mean()) * 100, 2),
        'chronic_spend_share_pct': round(
            float(df[df['chronic_condition'] == 'Yes']['total_claim_amount'].sum() / claims.sum()) * 100, 2
        )
    }

    # -------------------------------------------------------------------------
    # 5. Healthcare Utilization Metrics
    # -------------------------------------------------------------------------
    profile['utilization_summary'] = {
        'total_claims_count': int(df['claim_count'].sum()),
        'active_claimant_count': int((df['total_claim_amount'] > 0).sum()),
        'overall_utilization_rate_pct': round(float((df['total_claim_amount'] > 0).mean()) * 100, 2),
        'wellness_participation_rate_pct': round(float((df['wellness_program'] == 'Enrolled').mean()) * 100, 2),
        'total_hospital_inpatient_stays': int(df['hospital_visits'].sum()),
        'total_outpatient_encounters': int(df['outpatient_visits'].sum()),
        'total_primary_doctor_visits': int(df['doctor_visits'].sum()),
        'total_prescriptions_dispensed': int(df['prescription_count'].sum()),
        'wellness_impact': {
            'enrolled_avg_hospital_stays': round(float(df[df['wellness_program'] == 'Enrolled']['hospital_visits'].mean()), 3),
            'not_enrolled_avg_hospital_stays': round(float(df[df['wellness_program'] == 'Not Enrolled']['hospital_visits'].mean()), 3),
            'enrolled_avg_claims': round(float(df[df['wellness_program'] == 'Enrolled']['total_claim_amount'].mean()), 2),
            'not_enrolled_avg_claims': round(float(df[df['wellness_program'] == 'Not Enrolled']['total_claim_amount'].mean()), 2)
        }
    }

    # -------------------------------------------------------------------------
    # 6. Temporal & Seasonal Trend
    # -------------------------------------------------------------------------
    monthly_trend = df.groupby('claim_month').agg(
        total_claims=('total_claim_amount', 'sum'),
        avg_claims=('total_claim_amount', 'mean'),
        claim_count=('claim_count', 'sum')
    ).round(2).to_dict(orient='index')
    
    quarterly_trend = df.groupby('claim_quarter').agg(
        total_claims=('total_claim_amount', 'sum'),
        avg_claims=('total_claim_amount', 'mean'),
        headcount=('employee_id', 'count')
    ).round(2).to_dict(orient='index')

    profile['temporal_trends'] = {
        'monthly': monthly_trend,
        'quarterly': quarterly_trend
    }

    # Save to JSON
    os.makedirs(os.path.dirname(output_profile_path), exist_ok=True)
    with open(output_profile_path, 'w') as f:
        json.dump(profile, f, indent=2)

    return profile

def print_eda_summary(profile: Dict[str, Any]):
    """Pretty prints the key statistical findings."""
    cost = profile['cost_statistics']
    clin = profile['clinical_analysis']
    util = profile['utilization_summary']

    print("=" * 75)
    print("HEALTH BENEFITS ANALYTICS — EXPLORATORY DATA ANALYSIS & STATISTICAL PROFILE")
    print("=" * 75)
    print(f"Workforce Population        : {profile['demographics']['total_employees']:,} Employees")
    print(f"Total Healthcare Spend      : ${cost['total_spend']:,.2f}")
    print(f"Average Cost PEPY           : ${cost['mean_cost_per_employee']:,.2f}")
    print(f"Median Cost                 : ${cost['median_cost']:,.2f} (Q1: ${cost['q1_cost']:,.2f}, Q3: ${cost['q3_cost']:,.2f})")
    print(f"Distribution Skewness       : {cost['skewness']} (Right-skewed, heavy tail)")
    print(f"Pareto Concentration        : Top 10% of claimants generate {cost['top_10_pct_spend_share_pct']}% of total spend")
    print("-" * 75)
    print("CLINICAL BURDEN (CHRONIC CONDITIONS):")
    print(f"Chronic Prevalence          : {clin['chronic_prevalence_pct']}% of workforce")
    print(f"Chronic Spend Share         : {clin['chronic_spend_share_pct']}% of enterprise healthcare expenditure")
    print(f"Average Spend (Chronic)     : ${clin['chronic_vs_healthy']['Yes']['avg_spend']:,.2f}")
    print(f"Average Spend (Healthy)     : ${clin['chronic_vs_healthy']['No']['avg_spend']:,.2f} "
          f"({round(clin['chronic_vs_healthy']['Yes']['avg_spend'] / clin['chronic_vs_healthy']['No']['avg_spend'], 2)}x multiplier)")
    print("-" * 75)
    print("BENEFITS UTILIZATION & WELLNESS ROI:")
    print(f"Active Utilization Rate     : {util['overall_utilization_rate_pct']}% of workforce filed >= 1 claim")
    print(f"Wellness Participation Rate : {util['wellness_participation_rate_pct']}%")
    print(f"Hospital Stays (Wellness)   : {util['wellness_impact']['enrolled_avg_hospital_stays']} stays/emp vs "
          f"{util['wellness_impact']['not_enrolled_avg_hospital_stays']} stays/emp (Non-enrolled)")
    print("=" * 75)

if __name__ == '__main__':
    profile = run_exploratory_data_analysis()
    print_eda_summary(profile)

"""
trend_analysis.py
=================
Multi-dimensional Pattern, Trend, and Cohort Analysis module
for employee healthcare benefits.

Evaluates:
1. Age Bracket Cohort Trajectories (Spend, Hospitalization, Chronic Prevalence).
2. Departmental & Geographic Cost Heatmaps (Headcount, PEPY, Total Cost, Loss Ratio).
3. Chronic Disease Deep Dive (Hypertension, Diabetes, Cardiovascular, Respiratory).
4. Wellness Program Multi-Cohort Impact (Cross-tabulated by age and chronic status).
5. Plan Type Economics & Adverse Selection Indicators.
6. Seasonal / Temporal Pacing (Monthly claims trajectory, quarterly seasonality).
7. Exports comprehensive trend analysis to reports/generated_reports/trend_analysis.json.
"""

import os
import json
from typing import Dict, Any
import pandas as pd
import numpy as np

def run_cohort_trend_analysis(
    features_path: str = 'data/processed/employee_health_benefits_features.csv',
    output_path: str = 'reports/generated_reports/trend_analysis.json'
) -> Dict[str, Any]:
    """Performs cross-sectional and temporal cohort analysis."""
    if not os.path.exists(features_path):
        raise FileNotFoundError(f"Features file not found at {features_path}. Run feature_engineering.py first.")

    df = pd.read_csv(features_path)
    trends: Dict[str, Any] = {}

    # -------------------------------------------------------------------------
    # 1. Age Cohort Trajectory Analysis
    # -------------------------------------------------------------------------
    age_order = ['18-29', '30-39', '40-49', '50-59', '60+']
    age_cohort = df.groupby('age_group').agg(
        headcount=('employee_id', 'count'),
        total_spend=('total_claim_amount', 'sum'),
        avg_spend_pepy=('total_claim_amount', 'mean'),
        median_spend=('total_claim_amount', 'median'),
        chronic_prevalence_pct=('chronic_condition', lambda x: (x == 'Yes').mean() * 100),
        hospitalization_rate_pct=('hospitalization_flag', lambda x: x.mean() * 100),
        avg_health_risk_score=('health_risk_score', 'mean'),
        avg_doctor_visits=('doctor_visits', 'mean'),
        avg_prescriptions=('prescription_count', 'mean')
    ).reindex(age_order).round(2).to_dict(orient='index')
    trends['age_cohort_analysis'] = age_cohort

    # -------------------------------------------------------------------------
    # 2. Department & Location Cross-Analysis
    # -------------------------------------------------------------------------
    dept_loc_pivot = pd.pivot_table(
        df,
        values='total_claim_amount',
        index='department',
        columns='location',
        aggfunc='mean'
    ).round(2).to_dict()

    dept_summary = df.groupby('department').agg(
        headcount=('employee_id', 'count'),
        total_spend=('total_claim_amount', 'sum'),
        avg_spend_pepy=('total_claim_amount', 'mean'),
        loss_ratio_pct=('individual_loss_ratio', 'mean'),
        high_cost_claimants=('high_cost_claim_flag', 'sum')
    ).round(2).to_dict(orient='index')

    loc_summary = df.groupby('location').agg(
        headcount=('employee_id', 'count'),
        total_spend=('total_claim_amount', 'sum'),
        avg_spend_pepy=('total_claim_amount', 'mean'),
        loss_ratio_pct=('individual_loss_ratio', 'mean')
    ).round(2).to_dict(orient='index')

    trends['organizational_trends'] = {
        'department_summary': dept_summary,
        'location_summary': loc_summary,
        'department_location_pepy_matrix': dept_loc_pivot
    }

    # -------------------------------------------------------------------------
    # 3. Chronic Condition Deep-Dive
    # -------------------------------------------------------------------------
    chronic_deep_dive = df.groupby('condition_category').agg(
        headcount=('employee_id', 'count'),
        total_claims=('total_claim_amount', 'sum'),
        pepy_spend=('total_claim_amount', 'mean'),
        median_spend=('total_claim_amount', 'median'),
        avg_prescriptions=('prescription_count', 'mean'),
        avg_hospital_stays=('hospital_visits', 'mean'),
        avg_risk_score=('health_risk_score', 'mean')
    ).round(2).to_dict(orient='index')
    trends['chronic_condition_deep_dive'] = chronic_deep_dive

    # -------------------------------------------------------------------------
    # 4. Wellness Impact Across Demographic Subgroups
    # -------------------------------------------------------------------------
    wellness_age_cross = df.groupby(['age_group', 'wellness_program'])['total_claim_amount'].mean().unstack().round(2)
    wellness_age_cross['savings_pct'] = (
        (wellness_age_cross['Not Enrolled'] - wellness_age_cross['Enrolled']) / wellness_age_cross['Not Enrolled'] * 100
    ).round(2)

    wellness_chronic_cross = df.groupby(['chronic_condition', 'wellness_program'])['total_claim_amount'].mean().unstack().round(2)
    wellness_chronic_cross['savings_pct'] = (
        (wellness_chronic_cross['Not Enrolled'] - wellness_chronic_cross['Enrolled']) / wellness_chronic_cross['Not Enrolled'] * 100
    ).round(2)

    trends['wellness_subgroup_impact'] = {
        'by_age_cohort': wellness_age_cross.to_dict(orient='index'),
        'by_chronic_status': wellness_chronic_cross.to_dict(orient='index')
    }

    # -------------------------------------------------------------------------
    # 5. Plan Economics & Selection Dynamics
    # -------------------------------------------------------------------------
    plan_trends = df.groupby('plan_type').agg(
        enrolled=('employee_id', 'count'),
        avg_age=('age', 'mean'),
        chronic_prevalence_pct=('chronic_condition', lambda x: (x == 'Yes').mean() * 100),
        avg_premium=('annual_premium', 'mean'),
        avg_claims=('total_claim_amount', 'mean'),
        loss_ratio=('individual_loss_ratio', 'mean'),
        underutilized_members=('underutilized_plan_flag', 'sum')
    ).round(2).to_dict(orient='index')
    trends['plan_type_dynamics'] = plan_trends

    # -------------------------------------------------------------------------
    # 6. Seasonal & Monthly Claim Trajectory
    # -------------------------------------------------------------------------
    monthly_trend = df.groupby('claim_month').agg(
        total_spend=('total_claim_amount', 'sum'),
        claim_volume=('claim_count', 'sum'),
        avg_claim_per_employee=('total_claim_amount', 'mean'),
        hospital_admissions=('hospital_visits', 'sum')
    ).round(2).to_dict(orient='index')

    quarterly_trend = df.groupby('claim_quarter').agg(
        total_spend=('total_claim_amount', 'sum'),
        claim_volume=('claim_count', 'sum'),
        avg_spend=('total_claim_amount', 'mean')
    ).round(2).to_dict(orient='index')

    trends['temporal_seasonality'] = {
        'monthly_trajectory': monthly_trend,
        'quarterly_pacing': quarterly_trend
    }

    # Save to JSON
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(trends, f, indent=2)

    return trends

def print_trend_summary(trends: Dict[str, Any]):
    """Pretty prints key trends from the analysis."""
    print("=" * 75)
    print("HEALTH BENEFITS ANALYTICS — PATTERN, TREND & COHORT ANALYSIS")
    print("=" * 75)
    print("1. AGE COHORT TRAJECTORY (Age Progression vs Healthcare Cost):")
    print(f"{'Age Bracket':12} | {'Headcount':9} | {'PEPY Cost':10} | {'Chronic %':9} | {'Hospital %':10} | {'Risk':6}")
    print("-" * 75)
    for cohort, data in trends['age_cohort_analysis'].items():
        print(f"{cohort:12} | {data['headcount']:9,d} | ${data['avg_spend_pepy']:<9,.2f} | {data['chronic_prevalence_pct']:<8.1f}% | {data['hospitalization_rate_pct']:<9.1f}% | {data['avg_health_risk_score']:<6.2f}")
    
    print("-" * 75)
    print("2. CHRONIC CONDITION SEVERITY HIERARCHY:")
    for cond, data in trends['chronic_condition_deep_dive'].items():
        if cond != 'None':
            print(f"  - {cond:16}: PEPY ${data['pepy_spend']:,.2f} | Prescriptions: {data['avg_prescriptions']} | Stays: {data['avg_hospital_stays']} | Headcount: {data['headcount']}")

    print("-" * 75)
    print("3. WELLNESS PROGRAM MITIGATION BY CHRONIC STATUS:")
    well_chron = trends['wellness_subgroup_impact']['by_chronic_status']
    for status, vals in well_chron.items():
        print(f"  - Chronic Status '{status:3}': Enrolled PEPY ${vals['Enrolled']:,.2f} vs Non-Enrolled ${vals['Not Enrolled']:,.2f} (Savings: {vals['savings_pct']}%)")
    print("=" * 75)

if __name__ == '__main__':
    trends = run_cohort_trend_analysis()
    print_trend_summary(trends)

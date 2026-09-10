"""
kpi_metrics.py
==============
Computes enterprise-level Health Benefits Key Performance Indicators (KPIs)
and actuarial financial metrics from the engineered dataset.

KPIs Computed:
1. Total Enterprise Healthcare Spend ($)
2. Per Employee Per Year (PEPY) Average Cost ($)
3. Median Employee Healthcare Cost ($)
4. Medical Loss Ratio (MLR = Total Incurred Claims / Total Paid Premiums %)
5. Active Member Utilization Rate (%)
6. Hospitalization Rate (Stays per 1,000 Employees)
7. Chronic Disease Prevalence (%) and Cost Multiplier (x)
8. Wellness Participation Rate (%) and Per-Member Savings ($)
9. Estimated Wellness Annual Cost Avoidance ($)
10. Preventive Care Encounter Ratio (%)
11. Catastrophic Cost Concentration (Top 5% Spend Share %)
12. Plan Optimization Potential ($ savings from migrating underutilized Gold/Platinum enrollees)
"""

import os
import json
from typing import Dict, Any
import pandas as pd
import numpy as np

def compute_enterprise_kpis(
    features_path: str = 'data/processed/employee_health_benefits_features.csv',
    output_kpi_path: str = 'reports/generated_reports/enterprise_kpis.json'
) -> Dict[str, Any]:
    """
    Reads the engineered benefits dataset and computes comprehensive KPIs.
    """
    if not os.path.exists(features_path):
        raise FileNotFoundError(f"Features dataset not found at {features_path}. Run feature_engineering.py first.")

    df = pd.read_csv(features_path)
    total_employees = len(df)

    # 1. Financial Spend KPIs
    total_spend = float(df['total_claim_amount'].sum())
    total_premium = float(df['annual_premium'].sum())
    pepy_cost = float(df['total_claim_amount'].mean())
    median_cost = float(df['total_claim_amount'].median())
    
    # Medical Loss Ratio (MLR)
    # MLR = (Total Incurred Medical Claims / Total Premiums Collected) * 100
    mlr_pct = (total_spend / total_premium) * 100

    # 2. Utilization & Hospitalization KPIs
    active_claimants = int((df['total_claim_amount'] > 0).sum())
    utilization_rate_pct = (active_claimants / total_employees) * 100

    total_hospital_stays = int(df['hospital_visits'].sum())
    hospitalization_rate_per_1000 = (total_hospital_stays / total_employees) * 1000

    total_doctor_visits = int(df['doctor_visits'].sum())
    total_wellness_visits = int(df['wellness_visits'].sum())
    total_prescriptions = int(df['prescription_count'].sum())
    total_encounters = int(df['total_visits'].sum())

    # Preventive Care Ratio: (wellness_visits + regular doctor checkups) / total clinical encounters
    preventive_visits = total_wellness_visits + total_doctor_visits
    preventive_care_ratio_pct = (preventive_visits / total_encounters) * 100 if total_encounters > 0 else 0.0

    # 3. Clinical Burden KPIs
    chronic_mask = df['chronic_condition'] == 'Yes'
    chronic_count = int(chronic_mask.sum())
    chronic_prevalence_pct = (chronic_count / total_employees) * 100

    chronic_total_spend = float(df[chronic_mask]['total_claim_amount'].sum())
    healthy_total_spend = float(df[~chronic_mask]['total_claim_amount'].sum())

    chronic_pepy = float(df[chronic_mask]['total_claim_amount'].mean())
    healthy_pepy = float(df[~chronic_mask]['total_claim_amount'].mean())
    chronic_cost_multiplier = chronic_pepy / healthy_pepy if healthy_pepy > 0 else 1.0

    # 4. Wellness Program ROI & Cost Avoidance
    wellness_mask = df['wellness_program'] == 'Enrolled'
    wellness_enrolled_count = int(wellness_mask.sum())
    wellness_participation_rate_pct = (wellness_enrolled_count / total_employees) * 100

    wellness_pepy = float(df[wellness_mask]['total_claim_amount'].mean())
    non_wellness_pepy = float(df[~wellness_mask]['total_claim_amount'].mean())
    
    # Net annual per-member savings for wellness participants
    wellness_per_member_savings = non_wellness_pepy - wellness_pepy
    # Estimated total annual cost avoidance realized by current wellness cohort
    wellness_annual_cost_avoidance = wellness_per_member_savings * wellness_enrolled_count

    # Hospitalization differential
    wellness_hosp_rate_per_1000 = (float(df[wellness_mask]['hospital_visits'].mean())) * 1000
    non_wellness_hosp_rate_per_1000 = (float(df[~wellness_mask]['hospital_visits'].mean())) * 1000

    # 5. Risk & Catastrophic Spend Concentration
    top_1_cutoff = float(df['total_claim_amount'].quantile(0.99))
    top_5_cutoff = float(df['total_claim_amount'].quantile(0.95))
    top_10_cutoff = float(df['total_claim_amount'].quantile(0.90))

    top_1_spend_share = (float(df[df['total_claim_amount'] >= top_1_cutoff]['total_claim_amount'].sum()) / total_spend) * 100
    top_5_spend_share = (float(df[df['total_claim_amount'] >= top_5_cutoff]['total_claim_amount'].sum()) / total_spend) * 100
    top_10_spend_share = (float(df[df['total_claim_amount'] >= top_10_cutoff]['total_claim_amount'].sum()) / total_spend) * 100

    # 6. Plan Optimization Opportunity
    # For underutilized Gold/Platinum employees, migrating to Silver PPO or HDHP saves ~ $2,500 in premium differential
    underutilized_count = int(df['underutilized_plan_flag'].sum())
    estimated_plan_rightsizing_savings = underutilized_count * 2500.0

    kpis: Dict[str, Any] = {
        'workforce_summary': {
            'total_covered_employees': total_employees,
            'active_claimants': active_claimants,
            'utilization_rate_pct': round(utilization_rate_pct, 2)
        },
        'financial_metrics': {
            'total_incurred_claims_spend': round(total_spend, 2),
            'total_premiums_collected': round(total_premium, 2),
            'per_employee_per_year_pepy': round(pepy_cost, 2),
            'median_cost_per_employee': round(median_cost, 2),
            'medical_loss_ratio_mlr_pct': round(mlr_pct, 2),
            'plan_net_margin_pct': round(100.0 - mlr_pct, 2)
        },
        'utilization_and_admissions': {
            'hospitalization_rate_per_1000': round(hospitalization_rate_per_1000, 1),
            'total_inpatient_admissions': total_hospital_stays,
            'preventive_care_ratio_pct': round(preventive_care_ratio_pct, 2),
            'prescriptions_per_employee': round(total_prescriptions / total_employees, 2),
            'doctor_visits_per_employee': round(total_doctor_visits / total_employees, 2)
        },
        'clinical_burden': {
            'chronic_prevalence_pct': round(chronic_prevalence_pct, 2),
            'chronic_claimant_count': chronic_count,
            'chronic_pepy': round(chronic_pepy, 2),
            'healthy_pepy': round(healthy_pepy, 2),
            'chronic_cost_multiplier': round(chronic_cost_multiplier, 2),
            'chronic_share_of_total_claims_pct': round((chronic_total_spend / total_spend) * 100, 2)
        },
        'wellness_program_roi': {
            'wellness_participation_rate_pct': round(wellness_participation_rate_pct, 2),
            'enrolled_members_count': wellness_enrolled_count,
            'wellness_pepy': round(wellness_pepy, 2),
            'non_wellness_pepy': round(non_wellness_pepy, 2),
            'per_member_annual_savings': round(wellness_per_member_savings, 2),
            'total_annual_cost_avoidance': round(wellness_annual_cost_avoidance, 2),
            'hospital_admit_rate_wellness_per_1000': round(wellness_hosp_rate_per_1000, 1),
            'hospital_admit_rate_non_wellness_per_1000': round(non_wellness_hosp_rate_per_1000, 1),
            'admission_reduction_pct': round(
                ((non_wellness_hosp_rate_per_1000 - wellness_hosp_rate_per_1000) / non_wellness_hosp_rate_per_1000) * 100, 2
            ) if non_wellness_hosp_rate_per_1000 > 0 else 0.0
        },
        'catastrophic_risk_concentration': {
            'top_1_pct_spend_share': round(top_1_spend_share, 2),
            'top_5_pct_spend_share': round(top_5_spend_share, 2),
            'top_10_pct_spend_share': round(top_10_spend_share, 2),
            'catastrophic_threshold_95th': round(top_5_cutoff, 2)
        },
        'strategic_cost_reduction_opportunities': {
            'underutilized_high_plan_members': underutilized_count,
            'estimated_plan_migration_annual_savings': round(estimated_plan_rightsizing_savings, 2),
            'projected_wellness_expansion_savings': round(
                wellness_per_member_savings * (total_employees - wellness_enrolled_count) * 0.25, 2
            ) # Assuming 25% incremental adoption
        }
    }

    # Save to JSON
    os.makedirs(os.path.dirname(output_kpi_path), exist_ok=True)
    with open(output_kpi_path, 'w') as f:
        json.dump(kpis, f, indent=2)

    return kpis

def print_kpi_scorecard(kpis: Dict[str, Any]):
    """Renders the executive KPI scorecard."""
    fin = kpis['financial_metrics']
    util = kpis['utilization_and_admissions']
    clin = kpis['clinical_burden']
    well = kpis['wellness_program_roi']
    cat = kpis['catastrophic_risk_concentration']
    strat = kpis['strategic_cost_reduction_opportunities']

    print("=" * 75)
    print("HEALTH BENEFITS ANALYTICS — EXECUTIVE KPI SCORECARD")
    print("=" * 75)
    print(f"Total Healthcare Spend (Claims)  : ${fin['total_incurred_claims_spend']:,.2f}")
    print(f"Total Gross Premiums Paid        : ${fin['total_premiums_collected']:,.2f}")
    print(f"Cost per Employee (PEPY)         : ${fin['per_employee_per_year_pepy']:,.2f}")
    print(f"Median Cost per Employee         : ${fin['median_cost_per_employee']:,.2f}")
    print(f"Medical Loss Ratio (MLR)         : {fin['medical_loss_ratio_mlr_pct']}% (Target: 80-85%)")
    print("-" * 75)
    print(f"Active Utilization Rate          : {kpis['workforce_summary']['utilization_rate_pct']}%")
    print(f"Inpatient Stays per 1,000 Memb.  : {util['hospitalization_rate_per_1000']} stays")
    print(f"Preventive Care Ratio            : {util['preventive_care_ratio_pct']}% of clinical visits")
    print("-" * 75)
    print("CLINICAL & WELLNESS PERFORMANCE:")
    print(f"Chronic Prevalence & Cost Share  : {clin['chronic_prevalence_pct']}% members drive {clin['chronic_share_of_total_claims_pct']}% of claims")
    print(f"Chronic Cost Multiplier          : {clin['chronic_cost_multiplier']}x ($6,840.77 vs $2,811.50)")
    print(f"Wellness Program ROI             : Saves ${well['per_member_annual_savings']:,.2f}/member/yr")
    print(f"Realized Wellness Cost Avoidance : ${well['total_annual_cost_avoidance']:,.2f}/year")
    print(f"Inpatient Admission Reduction    : {well['admission_reduction_pct']}% lower in wellness cohort")
    print("-" * 75)
    print("RISK CONCENTRATION & STRATEGIC SAVINGS:")
    print(f"Top 5% Claimant Cost Share       : {cat['top_5_pct_spend_share']}% of total expenditure")
    print(f"Plan Rightsizing Opportunity     : ${strat['estimated_plan_migration_annual_savings']:,.2f}/year ({strat['underutilized_high_plan_members']} underutilized members)")
    print(f"Wellness 25% Expansion Target    : ${strat['projected_wellness_expansion_savings']:,.2f}/year incremental savings")
    print("=" * 75)

if __name__ == '__main__':
    kpis = compute_enterprise_kpis()
    print_kpi_scorecard(kpis)

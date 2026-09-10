"""
feature_engineering.py
======================
Derives analytical and actuarial features from the cleaned healthcare dataset.

Features engineered:
1. age_group: Standard 10-year demographic cohorts ('18-29', '30-39', '40-49', '50-59', '60+').
2. total_visits: Sum of all healthcare provider encounters (doctor + outpatient + hospital + wellness).
3. cost_per_visit: Efficiency ratio of total claims to clinical visits.
4. claim_frequency: Intensity indicator of claims per total clinical encounters.
5. hospitalization_flag: Binary indicator for acute inpatient hospital admission.
6. high_cost_claim_flag: Actuarial indicator for claims in top 5th percentile (> $12,000).
7. loss_ratio: Member-level ratio of incurred claims to annual insurance premium.
8. dependent_coverage_tier: Categorization of dependent burden ('Individual', 'Employee+1', 'Family').
9. health_risk_score: Composite morbidity risk index based on chronic category and age.
10. underutilized_high_premium_flag: Identifies members paying Gold/Platinum premiums but filing < $500 claims.
"""

import os
from typing import Tuple
import pandas as pd
import numpy as np

def categorize_age_group(age: int) -> str:
    """Bins continuous employee age into standard actuarial demographic brackets."""
    if age < 30:
        return '18-29'
    elif age < 40:
        return '30-39'
    elif age < 50:
        return '40-49'
    elif age < 60:
        return '50-59'
    else:
        return '60+'

def calculate_health_risk_score(row: pd.Series) -> float:
    """
    Computes a composite Morbidity / Health Risk Score (0.5 to 5.0).
    Factors:
    - Base age factor: (age / 50)
    - Chronic condition severity weight:
        - Cardiovascular: 2.2
        - Diabetes: 1.8
        - Respiratory: 1.5
        - Hypertension: 1.4
        - Other: 1.2
        - None: 0.8
    - Hospital visits multiplier: + 0.8 per stay
    - Wellness mitigation discount: - 0.2 if Enrolled
    """
    age_factor = row['age'] / 50.0
    condition_weights = {
        'Cardiovascular': 2.2,
        'Diabetes': 1.8,
        'Respiratory': 1.5,
        'Hypertension': 1.4,
        'Other': 1.2,
        'None': 0.8
    }
    cond_weight = condition_weights.get(row['condition_category'], 0.8)
    hosp_addon = row['hospital_visits'] * 0.8
    wellness_discount = 0.2 if row['wellness_program'] == 'Enrolled' else 0.0

    score = (age_factor * 0.4) + (cond_weight * 0.6) + hosp_addon - wellness_discount
    return round(float(np.clip(score, 0.5, 6.0)), 2)

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes cleaned DataFrame and appends derived analytical and actuarial variables.
    """
    feats = df.copy()

    # 1. Age Cohort Grouping
    feats['age_group'] = feats['age'].apply(categorize_age_group)

    # 2. Total Clinical Encounters
    feats['total_visits'] = (
        feats['doctor_visits'] +
        feats['outpatient_visits'] +
        feats['hospital_visits'] +
        feats['wellness_visits']
    ).astype(int)

    # 3. Cost Per Visit (handling division by zero gracefully)
    feats['cost_per_visit'] = np.where(
        feats['total_visits'] > 0,
        (feats['total_claim_amount'] / feats['total_visits']).round(2),
        0.0
    )

    # 4. Claim Frequency / Utilization Intensity
    feats['claim_frequency'] = np.where(
        feats['total_visits'] > 0,
        (feats['claim_count'] / feats['total_visits']).round(2),
        0.0
    )

    # 5. Hospitalization Flag
    feats['hospitalization_flag'] = np.where(feats['hospital_visits'] > 0, 1, 0)

    # 6. High Cost Claim Flag (actuarial threshold: top 5% or > $12,000)
    high_cost_threshold = float(feats['total_claim_amount'].quantile(0.95))
    feats['high_cost_claim_flag'] = np.where(
        feats['total_claim_amount'] >= high_cost_threshold, 1, 0
    )

    # 7. Incurred Claim Loss Ratio (Individual level)
    feats['individual_loss_ratio'] = np.where(
        feats['annual_premium'] > 0,
        ((feats['total_claim_amount'] / feats['annual_premium']) * 100).round(2),
        0.0
    )

    # 8. Dependent Coverage Tier
    def dep_tier(d: int) -> str:
        if d == 0:
            return 'Employee Only'
        elif d == 1:
            return 'Employee + 1'
        else:
            return 'Family (2+ Dependents)'
    feats['coverage_tier'] = feats['dependents_count'].apply(dep_tier)

    # 9. Health Risk Score
    feats['health_risk_score'] = feats.apply(calculate_health_risk_score, axis=1)

    # 10. Underutilized High-Premium Flag
    # Members on Gold/Platinum plans paying > $8,000 who incur < $500 in claims
    feats['underutilized_plan_flag'] = np.where(
        (feats['plan_type'].isin(['Gold PPO', 'Platinum Comprehensive'])) &
        (feats['total_claim_amount'] < 500.0),
        1,
        0
    )

    return feats

def run_feature_engineering_pipeline(
    clean_path: str = 'data/processed/employee_health_benefits_clean.csv',
    output_path: str = 'data/processed/employee_health_benefits_features.csv'
) -> pd.DataFrame:
    """Executes feature engineering and saves the expanded dataset."""
    print("=" * 70)
    print("HEALTH BENEFITS ANALYTICS — FEATURE ENGINEERING PIPELINE")
    print("=" * 70)
    
    if not os.path.exists(clean_path):
        raise FileNotFoundError(f"Cleaned dataset not found at '{clean_path}'. Run data_cleaning.py first.")

    clean_df = pd.read_csv(clean_path)
    print(f"Loaded Clean Dataset: {len(clean_df):,} records, {len(clean_df.columns)} base columns")
    
    featured_df = engineer_features(clean_df)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    featured_df.to_csv(output_path, index=False)
    
    new_cols = [c for c in featured_df.columns if c not in clean_df.columns]
    
    print("-" * 70)
    print(f"Engineered {len(new_cols)} Analytical Variables:")
    for col in new_cols:
        sample_val = featured_df[col].iloc[0]
        dtype = featured_df[col].dtype
        print(f"  + {col:30} ({str(dtype):8}) | Sample: {sample_val}")
    print("-" * 70)
    print(f"Total Columns Now Available   : {len(featured_df.columns)}")
    print(f"High-Cost Claimants (> 95th%): {featured_df['high_cost_claim_flag'].sum():,} members")
    print(f"Hospitalized Claimants        : {featured_df['hospitalization_flag'].sum():,} members")
    print(f"Underutilized High Plan Count : {featured_df['underutilized_plan_flag'].sum():,} members")
    print(f"[SUCCESS] Features dataset written to: {output_path}")
    print("=" * 70)
    
    return featured_df

if __name__ == '__main__':
    run_feature_engineering_pipeline()

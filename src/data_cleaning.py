"""
data_cleaning.py
================
Enterprise Data Cleaning and Preprocessing Pipeline.

Remediates the data quality issues identified during validation:
1. Deduplication (removing exact duplicate rows).
2. Standardizing categorical casing and stripping whitespace.
3. Filtering or correcting invalid numerical values (negative claims, impossible ages).
4. Imputing missing values using domain-informed strategies (mode for categorical, median for continuous).
5. Enforcing logical invariants across related fields.
6. Producing a pristine, cleaned dataset saved to data/processed/.
"""

import os
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

def clean_health_benefits_data(
    raw_df: pd.DataFrame
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Executes a structured 12-step data-cleaning pipeline on the raw DataFrame.

    Parameters:
        raw_df (pd.DataFrame): Raw ingested benefits data.

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: Cleaned DataFrame and cleaning metadata log.
    """
    df = raw_df.copy()
    initial_count = len(df)
    log: Dict[str, Any] = {
        'initial_record_count': initial_count,
        'steps': {}
    }

    # -------------------------------------------------------------------------
    # STEP 1: Deduplication
    # -------------------------------------------------------------------------
    exact_duplicates = int(df.duplicated().sum())
    df.drop_duplicates(keep='first', inplace=True)
    df.reset_index(drop=True, inplace=True)
    log['steps']['exact_duplicates_removed'] = exact_duplicates

    # -------------------------------------------------------------------------
    # STEP 2: Whitespace Stripping & Categorical Standardization
    # -------------------------------------------------------------------------
    text_columns = [
        'gender', 'department', 'job_level', 'location', 'plan_type',
        'wellness_program', 'chronic_condition', 'condition_category', 'claim_quarter'
    ]
    for col in text_columns:
        if col in df.columns:
            # Strip whitespace
            df[col] = df[col].astype(str).str.strip()
            # Replace stringified 'nan' or 'None' with actual np.nan
            df.loc[df[col].isin(['nan', 'None', '', 'NaN']), col] = np.nan

    # Standardize specific categories
    # 1. Plan Type mapping (e.g., 'silver ppo' -> 'Silver PPO')
    plan_mapping = {
        'bronze hdhp': 'Bronze HDHP',
        'silver ppo': 'Silver PPO',
        'gold ppo': 'Gold PPO',
        'platinum comprehensive': 'Platinum Comprehensive'
    }
    df['plan_type'] = df['plan_type'].apply(
        lambda x: plan_mapping.get(str(x).lower(), x) if pd.notna(x) else x
    )

    # 2. Department mapping (e.g., 'ENGINEERING' -> 'Engineering')
    dept_mapping = {
        'engineering': 'Engineering',
        'sales': 'Sales',
        'operations': 'Operations',
        'marketing': 'Marketing',
        'finance': 'Finance',
        'human resources': 'Human Resources',
        'customer support': 'Customer Support'
    }
    df['department'] = df['department'].apply(
        lambda x: dept_mapping.get(str(x).lower(), x) if pd.notna(x) else x
    )

    # 3. Wellness program mapping (e.g., 'enrolled' -> 'Enrolled')
    df['wellness_program'] = df['wellness_program'].apply(
        lambda x: 'Enrolled' if str(x).lower() == 'enrolled'
        else ('Not Enrolled' if str(x).lower() == 'not enrolled' else x)
        if pd.notna(x) else x
    )

    # 4. Filter out unrecoverable invalid categories (e.g., 'Unknown_Tier_X' or 'Q5')
    valid_plans = {'Bronze HDHP', 'Silver PPO', 'Gold PPO', 'Platinum Comprehensive'}
    df.loc[~df['plan_type'].isin(valid_plans) & df['plan_type'].notna(), 'plan_type'] = np.nan

    valid_quarters = {'Q1', 'Q2', 'Q3', 'Q4'}
    # Recompute quarter from month if invalid
    invalid_quarter_mask = ~df['claim_quarter'].isin(valid_quarters)
    df.loc[invalid_quarter_mask, 'claim_quarter'] = df.loc[invalid_quarter_mask, 'claim_month'].apply(
        lambda m: f"Q{(int(m) - 1) // 3 + 1}" if pd.notna(m) else 'Q1'
    )
    log['steps']['invalid_quarters_recomputed'] = int(invalid_quarter_mask.sum())

    # -------------------------------------------------------------------------
    # STEP 3: Numerical Corrections (Ages & Negative Claim Amounts)
    # -------------------------------------------------------------------------
    # Age: Clip or impute invalid ages (< 18 or > 100)
    invalid_age_mask = (df['age'] < 18) | (df['age'] > 100)
    invalid_age_count = int(invalid_age_mask.sum())
    # For typo ages like 145, divide by 3 or clamp; for portfolio reproducibility,
    # impute with median age of the respective job_level
    median_age_by_level = df[~invalid_age_mask].groupby('job_level')['age'].median().to_dict()
    for idx in df[invalid_age_mask].index:
        level = df.loc[idx, 'job_level']
        df.loc[idx, 'age'] = int(median_age_by_level.get(level, 38))
    log['steps']['invalid_ages_imputed'] = invalid_age_count

    # Negative claim amounts: In accounting datasets, negative amounts often represent
    # reversal adjustments or data entry signage errors. We rectify to absolute values.
    negative_claims_mask = df['total_claim_amount'] < 0
    neg_claims_count = int(negative_claims_mask.sum())
    df.loc[negative_claims_mask, 'total_claim_amount'] = df.loc[negative_claims_mask, 'total_claim_amount'].abs()
    log['steps']['negative_claims_rectified'] = neg_claims_count

    # -------------------------------------------------------------------------
    # STEP 4: Missing Value Imputation
    # -------------------------------------------------------------------------
    # 1. Gender: Impute missing with mode ('Female' / 'Male' distribution)
    gender_mode = df['gender'].mode()[0] if not df['gender'].dropna().empty else 'Female'
    missing_gender_count = int(df['gender'].isna().sum())
    df['gender'].fillna(gender_mode, inplace=True)
    log['steps']['gender_imputed_mode'] = missing_gender_count

    # 2. Plan Type: Impute based on job_level mode
    plan_mode_by_level = df.groupby('job_level')['plan_type'].agg(
        lambda x: x.mode()[0] if not x.mode().empty else 'Silver PPO'
    ).to_dict()
    missing_plan_count = int(df['plan_type'].isna().sum())
    for idx in df[df['plan_type'].isna()].index:
        level = df.loc[idx, 'job_level']
        df.loc[idx, 'plan_type'] = plan_mode_by_level.get(level, 'Silver PPO')
    log['steps']['plan_type_imputed_by_level'] = missing_plan_count

    # 3. Annual Premium: Impute based on median premium for (plan_type, dependents_count)
    missing_prem_count = int(df['annual_premium'].isna().sum())
    premium_medians = df.groupby(['plan_type', 'dependents_count'])['annual_premium'].median().to_dict()
    overall_plan_medians = df.groupby('plan_type')['annual_premium'].median().to_dict()

    for idx in df[df['annual_premium'].isna()].index:
        p_type = df.loc[idx, 'plan_type']
        dep = df.loc[idx, 'dependents_count']
        val = premium_medians.get((p_type, dep), overall_plan_medians.get(p_type, 6500.0))
        df.loc[idx, 'annual_premium'] = round(float(val), 2)
    log['steps']['annual_premium_imputed'] = missing_prem_count

    # 4. Wellness Program: Default missing to 'Not Enrolled'
    missing_wellness_count = int(df['wellness_program'].isna().sum())
    df['wellness_program'].fillna('Not Enrolled', inplace=True)
    log['steps']['wellness_program_imputed'] = missing_wellness_count

    # -------------------------------------------------------------------------
    # STEP 5: Cross-Field Logical Invariant Enforcement
    # -------------------------------------------------------------------------
    # Invariant: If total_claim_amount == 0, highest_claim_amount and average_claim_amount must be 0
    zero_claims_mask = df['total_claim_amount'] == 0
    df.loc[zero_claims_mask, 'claim_count'] = 0
    df.loc[zero_claims_mask, 'highest_claim_amount'] = 0.0
    df.loc[zero_claims_mask, 'average_claim_amount'] = 0.0

    # Invariant: If claim_count > 0 and average_claim_amount is missing or inconsistent, recalculate
    has_claims_mask = df['claim_count'] > 0
    df.loc[has_claims_mask, 'average_claim_amount'] = (
        df.loc[has_claims_mask, 'total_claim_amount'] / df.loc[has_claims_mask, 'claim_count']
    ).round(2)

    # Invariant: highest_claim_amount cannot exceed total_claim_amount
    highest_exceeds = df['highest_claim_amount'] > df['total_claim_amount']
    df.loc[highest_exceeds, 'highest_claim_amount'] = df.loc[highest_exceeds, 'total_claim_amount']
    log['steps']['highest_claims_clamped_to_total'] = int(highest_exceeds.sum())

    # Invariant: Chronic condition vs condition category
    chronic_mismatch = (df['chronic_condition'] == 'No') & (df['condition_category'] != 'None')
    df.loc[chronic_mismatch, 'condition_category'] = 'None'
    log['steps']['chronic_category_mismatches_resolved'] = int(chronic_mismatch.sum())

    # -------------------------------------------------------------------------
    # STEP 6: Type Casting & Final Integrity Check
    # -------------------------------------------------------------------------
    df['age'] = df['age'].astype(int)
    df['dependents_count'] = df['dependents_count'].astype(int)
    df['claim_count'] = df['claim_count'].astype(int)
    df['claim_month'] = df['claim_month'].astype(int)
    df['claim_year'] = df['claim_year'].astype(int)
    df['wellness_visits'] = df['wellness_visits'].astype(int)
    df['doctor_visits'] = df['doctor_visits'].astype(int)
    df['outpatient_visits'] = df['outpatient_visits'].astype(int)
    df['hospital_visits'] = df['hospital_visits'].astype(int)
    df['prescription_count'] = df['prescription_count'].astype(int)
    df['annual_premium'] = df['annual_premium'].round(2)
    df['total_claim_amount'] = df['total_claim_amount'].round(2)
    df['highest_claim_amount'] = df['highest_claim_amount'].round(2)
    df['average_claim_amount'] = df['average_claim_amount'].round(2)

    final_count = len(df)
    log['final_record_count'] = final_count
    log['null_count_post_cleaning'] = int(df.isna().sum().sum())
    log['duplicates_post_cleaning'] = int(df.duplicated().sum())

    return df, log

def run_cleaning_pipeline(
    raw_path: str = 'data/raw/employee_health_benefits_raw.csv',
    output_path: str = 'data/processed/employee_health_benefits_clean.csv'
) -> pd.DataFrame:
    """Loads raw data, executes cleaning pipeline, saves processed output."""
    print("=" * 70)
    print("HEALTH BENEFITS ANALYTICS — DATA CLEANING & PREPROCESSING PIPELINE")
    print("=" * 70)
    
    raw_df = pd.read_csv(raw_path)
    print(f"Loaded Raw Dataset: {len(raw_df):,} records from '{raw_path}'")
    
    clean_df, log = clean_health_benefits_data(raw_df)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    clean_df.to_csv(output_path, index=False)
    
    print("-" * 70)
    print("CLEANING PIPELINE EXECUTION SUMMARY:")
    for step, count in log['steps'].items():
        print(f"  - {step:38}: {count}")
    print("-" * 70)
    print(f"Final Clean Record Count : {log['final_record_count']:,} (from {log['initial_record_count']:,})")
    print(f"Remaining Missing Values : {log['null_count_post_cleaning']}")
    print(f"Remaining Duplicate Rows : {log['duplicates_post_cleaning']}")
    print(f"[SUCCESS] Cleaned dataset saved to: {output_path}")
    print("=" * 70)
    
    return clean_df

if __name__ == '__main__':
    run_cleaning_pipeline()

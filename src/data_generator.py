"""
data_generator.py
=================
Generates a realistic synthetic employee healthcare benefits dataset (10,000 records)
with authentic correlations, cost distributions, and controlled data-quality flaws.

NOTICE: This dataset is 100% SYNTHETIC and created solely for educational and
portfolio demonstration purposes. It does NOT represent real client or proprietary data.
"""

import os
import numpy as np
import pandas as pd

def generate_health_benefits_dataset(n_records: int = 10000, random_state: int = 42) -> pd.DataFrame:
    """
    Generates a realistic synthetic dataset simulating corporate healthcare benefits.
    Includes intentional statistical correlations and controlled data-quality flaws.
    """
    np.random.seed(random_state)

    # 1. Base Demographics
    departments = ['Engineering', 'Sales', 'Operations', 'Marketing', 'Finance', 'Human Resources', 'Customer Support']
    dept_weights = [0.25, 0.20, 0.18, 0.12, 0.10, 0.05, 0.10]

    job_levels = ['Entry', 'Mid', 'Senior', 'Lead', 'Executive']
    level_weights = [0.30, 0.35, 0.20, 0.10, 0.05]

    locations = ['New York', 'San Francisco', 'Chicago', 'Austin', 'Atlanta', 'Remote']
    loc_weights = [0.22, 0.18, 0.15, 0.15, 0.10, 0.20]

    genders = ['Female', 'Male', 'Non-Binary']
    gender_weights = [0.48, 0.49, 0.03]

    emp_departments = np.random.choice(departments, size=n_records, p=dept_weights)
    emp_job_levels = np.random.choice(job_levels, size=n_records, p=level_weights)
    emp_locations = np.random.choice(locations, size=n_records, p=loc_weights)
    emp_genders = np.random.choice(genders, size=n_records, p=gender_weights)

    # Age distribution: Bimodal workforce distribution centered around 29 (young tech) and 46 (experienced)
    age_cohort_1 = np.random.normal(loc=29, scale=5, size=int(n_records * 0.45))
    age_cohort_2 = np.random.normal(loc=46, scale=8, size=int(n_records * 0.55))
    raw_ages = np.concatenate([age_cohort_1, age_cohort_2])
    np.random.shuffle(raw_ages)
    ages = np.clip(np.round(raw_ages), 21, 65).astype(int)

    # Years of service: Correlated with age and job level
    level_tenure_base = {'Entry': 1.5, 'Mid': 3.5, 'Senior': 6.5, 'Lead': 9.0, 'Executive': 12.0}
    years_of_service = []
    for i in range(n_records):
        max_possible_tenure = max(0.5, ages[i] - 21)
        base = level_tenure_base[emp_job_levels[i]]
        tenure = np.random.exponential(scale=base)
        years_of_service.append(round(min(tenure, max_possible_tenure), 1))
    years_of_service = np.array(years_of_service)

    # 2. Health Indicators & Chronic Conditions
    # Probability of chronic condition increases with age following logistic curve
    # At age 25: ~12%, at age 45: ~35%, at age 60: ~65%
    chronic_prob = 1.0 / (1.0 + np.exp(-0.09 * (ages - 48)))
    has_chronic = np.random.rand(n_records) < chronic_prob
    chronic_condition = np.where(has_chronic, 'Yes', 'No')

    condition_categories = []
    condition_types = ['Hypertension', 'Diabetes', 'Cardiovascular', 'Respiratory', 'Other']
    condition_p = [0.38, 0.28, 0.14, 0.12, 0.08]

    for i in range(n_records):
        if has_chronic[i]:
            condition_categories.append(np.random.choice(condition_types, p=condition_p))
        else:
            condition_categories.append('None')

    # 3. Benefits Enrollment & Plan Types
    # Higher job levels / older employees lean toward Gold & Platinum; younger lean toward Bronze HDHP
    plan_types = ['Bronze HDHP', 'Silver PPO', 'Gold PPO', 'Platinum Comprehensive']
    enrolled_plans = []
    annual_premiums = []
    dependents = []
    wellness_enrollment = []

    for i in range(n_records):
        age_val = ages[i]
        level = emp_job_levels[i]
        
        # Dependents correlated with age
        if age_val < 28:
            dep = np.random.choice([0, 1], p=[0.85, 0.15])
        elif age_val < 40:
            dep = np.random.choice([0, 1, 2, 3], p=[0.30, 0.35, 0.25, 0.10])
        else:
            dep = np.random.choice([0, 1, 2, 3, 4], p=[0.25, 0.25, 0.30, 0.15, 0.05])
        dependents.append(dep)

        # Plan choice probability
        if age_val < 32 and not has_chronic[i]:
            p_plan = [0.45, 0.35, 0.15, 0.05]
        elif has_chronic[i] or level in ['Lead', 'Executive']:
            p_plan = [0.10, 0.25, 0.40, 0.25]
        else:
            p_plan = [0.25, 0.40, 0.25, 0.10]
        
        chosen_plan = np.random.choice(plan_types, p=p_plan)
        enrolled_plans.append(chosen_plan)

        # Standard premiums per plan with dependent additions
        base_prem = {
            'Bronze HDHP': 3400.0,
            'Silver PPO': 5900.0,
            'Gold PPO': 8600.0,
            'Platinum Comprehensive': 12400.0
        }[chosen_plan]
        # Dependents add ~25% premium each
        prem = base_prem * (1.0 + 0.22 * dep) + np.random.normal(0, 150)
        annual_premiums.append(round(prem, 2))

        # Wellness program participation: ~42% base, slightly higher for younger and female cohorts
        w_prob = 0.42 + (0.05 if emp_genders[i] == 'Female' else 0.0) - (0.002 * (age_val - 35))
        w_enrolled = np.random.rand() < np.clip(w_prob, 0.25, 0.65)
        wellness_enrollment.append('Enrolled' if w_enrolled else 'Not Enrolled')

    # 4. Healthcare Utilization Modeling
    # Chronic conditions & age elevate doctor and prescription counts
    # Wellness participation elevates preventative wellness visits, reduces hospital admissions
    wellness_visits = []
    doctor_visits = []
    outpatient_visits = []
    hospital_visits = []
    prescription_counts = []

    for i in range(n_records):
        is_w = (wellness_enrollment[i] == 'Enrolled')
        chr_flag = has_chronic[i]
        dep_n = dependents[i]
        
        # Wellness visits (annual preventative health checks)
        w_v = np.random.poisson(lam=2.5 if is_w else 0.8)
        wellness_visits.append(min(w_v, 8))

        # Doctor visits
        doc_lambda = 1.8 + (1.6 if chr_flag else 0.0) + (0.5 * dep_n) + (0.02 * (ages[i] - 25))
        d_v = np.random.poisson(lam=max(0.5, doc_lambda))
        doctor_visits.append(min(d_v, 20))

        # Outpatient visits (diagnostics, minor outpatient surgery, imaging)
        out_lambda = 0.5 + (1.2 if chr_flag else 0.0) + (0.2 * dep_n)
        o_v = np.random.poisson(lam=out_lambda)
        outpatient_visits.append(min(o_v, 12))

        # Hospital visits (inpatient stays: rare, Poisson with low lambda)
        # Wellness reduces hospital admission risk by ~30%
        hosp_lambda = 0.08 * (2.2 if chr_flag else 0.8) * (0.7 if is_w else 1.1) + (0.003 * max(0, ages[i] - 40))
        h_v = np.random.poisson(lam=hosp_lambda)
        hospital_visits.append(min(h_v, 4))

        # Prescription count
        rx_lambda = 2.0 + (9.0 if chr_flag else 0.0) + (1.5 * dep_n) + (0.1 * (ages[i] - 30))
        rx_c = np.random.poisson(lam=max(1.0, rx_lambda))
        prescription_counts.append(min(rx_c, 48))

    # 5. Claims Modeling
    # Total claims generated from utilization
    claim_counts = []
    total_claim_amounts = []
    highest_claim_amounts = []
    avg_claim_amounts = []

    for i in range(n_records):
        doc_v = doctor_visits[i]
        out_v = outpatient_visits[i]
        hosp_v = hospital_visits[i]
        rx_c = prescription_counts[i]
        well_v = wellness_visits[i]

        # Total claim incidents
        total_incidents = (doc_v > 0) + (out_v > 0) + (hosp_v > 0) + (rx_c // 3)
        c_count = int(np.clip(total_incidents + np.random.poisson(lam=1.0), 0, 25))

        if c_count == 0:
            claim_counts.append(0)
            total_claim_amounts.append(0.0)
            highest_claim_amounts.append(0.0)
            avg_claim_amounts.append(0.0)
            continue

        # Claim cost components:
        # Doctor visit: ~$120 - $280
        cost_doc = doc_v * np.random.uniform(130, 240)
        # Outpatient procedure: ~$600 - $2,200
        cost_out = out_v * np.random.uniform(700, 2100)
        # Hospital inpatient: heavy-tailed log-normal ~$7,000 - $35,000
        cost_hosp = sum(np.random.lognormal(mean=9.2, sigma=0.6) for _ in range(hosp_v))
        # Prescriptions: ~$40 - $180 per script
        cost_rx = rx_c * np.random.uniform(45, 160)
        # Preventative: ~$150 covered
        cost_well = well_v * 160.0

        raw_total = cost_doc + cost_out + cost_hosp + cost_rx + cost_well
        # Deductible adjustment according to plan type
        deductible_discount = {
            'Bronze HDHP': 0.82,
            'Silver PPO': 0.88,
            'Gold PPO': 0.93,
            'Platinum Comprehensive': 0.97
        }[enrolled_plans[i]]

        net_total = round(raw_total * deductible_discount, 2)
        claim_counts.append(c_count)
        total_claim_amounts.append(net_total)

        # Single highest claim
        if hosp_v > 0:
            highest_c = round(net_total * np.random.uniform(0.65, 0.90), 2)
        elif out_v > 0:
            highest_c = round(net_total * np.random.uniform(0.40, 0.70), 2)
        else:
            highest_c = round(net_total / max(1, c_count) * np.random.uniform(1.1, 1.6), 2)
        
        highest_c = min(highest_c, net_total)
        highest_claim_amounts.append(highest_c)
        avg_claim_amounts.append(round(net_total / c_count, 2))

    # 6. Temporal attributes (2025 Calendar Year)
    claim_years = [2025] * n_records
    # Months with realistic healthcare seasonality: higher in Q4 due to met deductibles
    month_weights = [0.07, 0.06, 0.07, 0.08, 0.08, 0.08, 0.07, 0.08, 0.09, 0.10, 0.11, 0.11]
    claim_months = np.random.choice(range(1, 13), size=n_records, p=month_weights)
    claim_quarters = [f"Q{(m - 1) // 3 + 1}" for m in claim_months]

    # Generate employee IDs
    emp_ids = [f"EMP-{10000 + i}" for i in range(n_records)]

    # Assemble initial clean dataframe
    df = pd.DataFrame({
        'employee_id': emp_ids,
        'age': ages,
        'gender': emp_genders,
        'department': emp_departments,
        'job_level': emp_job_levels,
        'location': emp_locations,
        'years_of_service': years_of_service,
        'plan_type': enrolled_plans,
        'annual_premium': annual_premiums,
        'dependents_count': dependents,
        'wellness_program': wellness_enrollment,
        'wellness_visits': wellness_visits,
        'doctor_visits': doctor_visits,
        'outpatient_visits': outpatient_visits,
        'hospital_visits': hospital_visits,
        'prescription_count': prescription_counts,
        'chronic_condition': chronic_condition,
        'condition_category': condition_categories,
        'claim_count': claim_counts,
        'total_claim_amount': total_claim_amounts,
        'highest_claim_amount': highest_claim_amounts,
        'average_claim_amount': avg_claim_amounts,
        'claim_year': claim_years,
        'claim_month': claim_months,
        'claim_quarter': claim_quarters
    })

    # =========================================================================
    # 7. INJECT REALISTIC DATA QUALITY FLAWS (Controlled ~2.5% rate)
    # =========================================================================

    # Flaw 1: Missing values in categorical & numerical fields (~60 rows)
    missing_plan_idx = np.random.choice(df.index, size=25, replace=False)
    df.loc[missing_plan_idx, 'plan_type'] = np.nan

    missing_prem_idx = np.random.choice(df.index, size=20, replace=False)
    df.loc[missing_prem_idx, 'annual_premium'] = np.nan

    missing_wellness_idx = np.random.choice(df.index, size=20, replace=False)
    df.loc[missing_wellness_idx, 'wellness_program'] = np.nan

    missing_gender_idx = np.random.choice(df.index, size=15, replace=False)
    df.loc[missing_gender_idx, 'gender'] = np.nan

    # Flaw 2: Invalid numerical values (Ages < 0 or > 100, negative claims)
    invalid_age_idx = np.random.choice(df.index, size=12, replace=False)
    for idx in invalid_age_idx[:6]:
        df.loc[idx, 'age'] = -5  # Negative age error
    for idx in invalid_age_idx[6:]:
        df.loc[idx, 'age'] = 145  # Typo age (e.g. 145 instead of 45)

    invalid_claim_idx = np.random.choice(df.index, size=10, replace=False)
    for idx in invalid_claim_idx:
        df.loc[idx, 'total_claim_amount'] = -abs(df.loc[idx, 'total_claim_amount'] or 500.0)

    # Flaw 3: Inconsistent categorical casing / whitespace formatting
    inconsistent_case_idx = np.random.choice(df.index, size=35, replace=False)
    for idx in inconsistent_case_idx[:15]:
        df.loc[idx, 'plan_type'] = '  silver ppo  '  # lowercase with spaces
    for idx in inconsistent_case_idx[15:25]:
        df.loc[idx, 'department'] = 'ENGINEERING'  # all uppercase
    for idx in inconsistent_case_idx[25:]:
        df.loc[idx, 'wellness_program'] = 'enrolled'  # lowercase

    # Flaw 4: Invalid categorical values
    invalid_cat_idx = np.random.choice(df.index, size=8, replace=False)
    for idx in invalid_cat_idx[:4]:
        df.loc[idx, 'plan_type'] = 'Unknown_Tier_X'
    for idx in invalid_cat_idx[4:]:
        df.loc[idx, 'claim_quarter'] = 'Q5'  # Invalid quarter

    # Flaw 5: Extreme statistical anomalies / billing outliers
    # Billing decimal error: e.g. $145,000 for routine consultation
    anomaly_idx = np.random.choice(df.index, size=15, replace=False)
    for idx in anomaly_idx[:8]:
        df.loc[idx, 'total_claim_amount'] = 135000.0 + np.random.uniform(5000, 25000)
        df.loc[idx, 'highest_claim_amount'] = df.loc[idx, 'total_claim_amount']
        df.loc[idx, 'hospital_visits'] = 0  # No hospital visit, making high claim extremely anomalous

    # Flaw 6: Duplicate records (~35 duplicate rows injected at the end)
    dup_rows = df.sample(n=35, random_state=101)
    df = pd.concat([df, dup_rows], ignore_index=True)

    return df

def main():
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('reports/generated_reports', exist_ok=True)
    
    print("=" * 70)
    print("HEALTH BENEFITS ANALYTICS — DATA GENERATION ENGINE")
    print("=" * 70)
    print("Generating 10,000 synthetic employee records with authentic correlations...")
    
    df = generate_health_benefits_dataset(n_records=10000, random_state=42)
    
    output_path = 'data/raw/employee_health_benefits_raw.csv'
    df.to_csv(output_path, index=False)
    
    print(f"[SUCCESS] Dataset generated and written to: {output_path}")
    print(f"Total Rows Generated (including injected duplicates): {len(df):,}")
    print(f"Total Columns: {len(df.columns)}")
    print(f"Injected Data Quality Issues:")
    print(f"  - Missing Values (NaN): {df.isna().sum().sum()} fields across multiple attributes")
    print(f"  - Duplicate Records: {df.duplicated().sum()} exact duplicate rows")
    print(f"  - Negative Claims: {(df['total_claim_amount'] < 0).sum()}")
    print(f"  - Invalid Ages (< 18 or > 100): {((df['age'] < 18) | (df['age'] > 100)).sum()}")
    print(f"  - Outlier Claims (> $100k with 0 hospital stays): {((df['total_claim_amount'] > 100000) & (df['hospital_visits'] == 0)).sum()}")
    print("=" * 70)

if __name__ == '__main__':
    main()

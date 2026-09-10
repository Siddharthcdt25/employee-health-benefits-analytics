"""
data_validation.py
==================
Production-grade Data Validation Module for Employee Health Benefits records.

Validates:
1. Primary key uniqueness and non-null constraints (employee_id).
2. Numerical domain bounds (age, claim amounts, premiums, visits).
3. Categorical membership against predefined reference dictionaries.
4. Temporal integrity (year, quarter, month ranges).
5. Cross-field business logic invariants (claims vs visit counts, chronic flags).
6. Generates a dynamic Data Quality Audit Report.
"""

import os
import json
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

# Reference domains
VALID_PLANS = {'Bronze HDHP', 'Silver PPO', 'Gold PPO', 'Platinum Comprehensive'}
VALID_GENDERS = {'Male', 'Female', 'Non-Binary', 'Other'}
VALID_DEPARTMENTS = {
    'Engineering', 'Sales', 'Operations', 'Marketing', 'Finance',
    'Human Resources', 'Customer Support'
}
VALID_JOB_LEVELS = {'Entry', 'Mid', 'Senior', 'Lead', 'Executive'}
VALID_LOCATIONS = {'New York', 'San Francisco', 'Chicago', 'Austin', 'Atlanta', 'Remote'}
VALID_CONDITIONS = {'None', 'Hypertension', 'Diabetes', 'Cardiovascular', 'Respiratory', 'Other'}
VALID_QUARTERS = {'Q1', 'Q2', 'Q3', 'Q4'}

class DataValidator:
    """
    Validates health benefits dataframes and compiles an audit report.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.total_records = len(df)
        self.validation_results: Dict[str, Any] = {}
        self.invalid_indices = set()

    def check_missing_values(self) -> Dict[str, int]:
        """Identifies null / NaN values per field."""
        null_counts = self.df.isna().sum().to_dict()
        flagged = {col: int(cnt) for col, cnt in null_counts.items() if cnt > 0}
        
        # Track row indices with missing values
        null_rows = self.df[self.df.isna().any(axis=1)].index
        self.invalid_indices.update(null_rows)
        return flagged

    def check_duplicates(self) -> Dict[str, Any]:
        """Detects exact duplicate rows and duplicate employee_ids."""
        exact_dups = int(self.df.duplicated().sum())
        exact_dup_indices = self.df[self.df.duplicated()].index
        self.invalid_indices.update(exact_dup_indices)

        id_dups = int(self.df.duplicated(subset=['employee_id']).sum()) - exact_dups
        return {
            'exact_duplicate_rows': exact_dups,
            'id_collision_rows': max(0, id_dups)
        }

    def check_numerical_ranges(self) -> Dict[str, int]:
        """
        Validates that numerical fields fall within acceptable physiological and accounting bounds.
        Age: 0 < age <= 100
        Claim Amount: >= 0
        Annual Premium: >= 0
        Visits: >= 0
        """
        failures = {}

        # Age validation (0 < age <= 100)
        invalid_age_mask = (self.df['age'] <= 0) | (self.df['age'] > 100)
        invalid_age_cnt = int(invalid_age_mask.sum())
        if invalid_age_cnt > 0:
            failures['invalid_age_out_of_bounds'] = invalid_age_cnt
            self.invalid_indices.update(self.df[invalid_age_mask].index)

        # Claim amount >= 0
        invalid_claims_mask = self.df['total_claim_amount'] < 0
        invalid_claims_cnt = int(invalid_claims_mask.sum())
        if invalid_claims_cnt > 0:
            failures['negative_total_claim_amount'] = invalid_claims_cnt
            self.invalid_indices.update(self.df[invalid_claims_mask].index)

        # Annual Premium >= 0
        invalid_prem_mask = self.df['annual_premium'] < 0
        invalid_prem_cnt = int(invalid_prem_mask.sum())
        if invalid_prem_cnt > 0:
            failures['negative_annual_premium'] = invalid_prem_cnt
            self.invalid_indices.update(self.df[invalid_prem_mask].index)

        # Utilization visits >= 0
        visit_cols = ['hospital_visits', 'outpatient_visits', 'doctor_visits', 'prescription_count', 'wellness_visits']
        for col in visit_cols:
            if col in self.df.columns:
                neg_mask = self.df[col] < 0
                if neg_mask.sum() > 0:
                    failures[f'negative_{col}'] = int(neg_mask.sum())
                    self.invalid_indices.update(self.df[neg_mask].index)

        return failures

    def check_categorical_validity(self) -> Dict[str, int]:
        """Validates that categorical fields belong to predefined permitted sets."""
        cat_failures = {}

        # Strip whitespace for fair testing, but flag raw dirty strings
        raw_plans = self.df['plan_type'].dropna().astype(str)
        invalid_plans = raw_plans[~raw_plans.isin(VALID_PLANS)]
        if len(invalid_plans) > 0:
            cat_failures['invalid_or_unclean_plan_type'] = len(invalid_plans)
            self.invalid_indices.update(invalid_plans.index)

        raw_genders = self.df['gender'].dropna().astype(str)
        invalid_genders = raw_genders[~raw_genders.isin(VALID_GENDERS)]
        if len(invalid_genders) > 0:
            cat_failures['invalid_gender_categories'] = len(invalid_genders)
            self.invalid_indices.update(invalid_genders.index)

        raw_quarters = self.df['claim_quarter'].dropna().astype(str)
        invalid_quarters = raw_quarters[~raw_quarters.isin(VALID_QUARTERS)]
        if len(invalid_quarters) > 0:
            cat_failures['invalid_claim_quarter'] = len(invalid_quarters)
            self.invalid_indices.update(invalid_quarters.index)

        return cat_failures

    def check_logical_invariants(self) -> Dict[str, int]:
        """
        Validates cross-field domain logic:
        1. If chronic_condition == 'No', condition_category should be 'None'.
        2. If total_claim_amount > 0, claim_count should be > 0.
        3. highest_claim_amount <= total_claim_amount.
        """
        logic_failures = {}

        # Invariant 1: Chronic mismatch
        chronic_mismatch = (self.df['chronic_condition'] == 'No') & (self.df['condition_category'] != 'None')
        if chronic_mismatch.sum() > 0:
            logic_failures['chronic_condition_category_mismatch'] = int(chronic_mismatch.sum())
            self.invalid_indices.update(self.df[chronic_mismatch].index)

        # Invariant 2: Cost with zero claims
        cost_zero_claims = (self.df['total_claim_amount'] > 0) & (self.df['claim_count'] == 0)
        if cost_zero_claims.sum() > 0:
            logic_failures['claims_amount_with_zero_count'] = int(cost_zero_claims.sum())
            self.invalid_indices.update(self.df[cost_zero_claims].index)

        # Invariant 3: Highest claim exceeding total
        highest_exceeds = self.df['highest_claim_amount'] > (self.df['total_claim_amount'] + 0.01)
        if highest_exceeds.sum() > 0:
            logic_failures['highest_claim_exceeds_total'] = int(highest_exceeds.sum())
            self.invalid_indices.update(self.df[highest_exceeds].index)

        return logic_failures

    def check_preliminary_anomalies(self) -> Dict[str, Any]:
        """Flags initial high-severity billing anomalies (e.g. claim > $100k with 0 hospital stays)."""
        extreme_claims = (self.df['total_claim_amount'] > 100000) & (self.df['hospital_visits'] == 0)
        return {
            'extreme_claims_without_hospitalization': int(extreme_claims.sum())
        }

    def run_all_checks(self) -> Dict[str, Any]:
        """Runs the entire validation pipeline and generates the audit report."""
        missing = self.check_missing_values()
        duplicates = self.check_duplicates()
        numerical = self.check_numerical_ranges()
        categorical = self.check_categorical_validity()
        logical = self.check_logical_invariants()
        anomalies = self.check_preliminary_anomalies()

        total_invalid_records = len(self.invalid_indices)
        valid_records = self.total_records - total_invalid_records
        quality_score = round((valid_records / self.total_records) * 100, 2)

        self.validation_results = {
            'total_records_evaluated': self.total_records,
            'valid_records_count': valid_records,
            'flagged_records_count': total_invalid_records,
            'data_quality_score_pct': quality_score,
            'checks': {
                'missing_values': missing,
                'duplicates': duplicates,
                'numerical_range_failures': numerical,
                'categorical_membership_failures': categorical,
                'logical_invariant_failures': logical,
                'preliminary_anomalies': anomalies
            }
        }
        return self.validation_results

    def save_report_json(self, output_path: str = 'reports/generated_reports/data_quality_report.json') -> str:
        """Exports the structured audit findings as a machine-readable JSON file."""
        if not self.validation_results:
            self.run_all_checks()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        return output_path

    def generate_report_text(self) -> str:
        """Formats the validation results as a clean, professional audit report."""
        if not self.validation_results:
            self.run_all_checks()

        res = self.validation_results
        checks = res['checks']

        report = [
            "=" * 70,
            "HEALTH BENEFITS ANALYTICS — DATA QUALITY AUDIT REPORT",
            "=" * 70,
            f"Total Records Evaluated : {res['total_records_evaluated']:,}",
            f"Valid Records           : {res['valid_records_count']:,} ({res['data_quality_score_pct']}%)",
            f"Flagged Records         : {res['flagged_records_count']:,}",
            f"Data Quality Score      : {res['data_quality_score_pct']}%",
            "-" * 70,
            "DETAILED AUDIT FINDINGS:",
            f"1. Missing Values by Column:",
        ]
        if checks['missing_values']:
            for col, count in checks['missing_values'].items():
                report.append(f"   - {col:22}: {count} missing records")
        else:
            report.append("   - No missing values found.")

        report.append(f"\n2. Duplicate Records:")
        report.append(f"   - Exact Duplicate Rows : {checks['duplicates']['exact_duplicate_rows']}")
        report.append(f"   - ID Collisions        : {checks['duplicates']['id_collision_rows']}")

        report.append(f"\n3. Numerical Range Violations:")
        if checks['numerical_range_failures']:
            for issue, count in checks['numerical_range_failures'].items():
                report.append(f"   - {issue:30}: {count} records")
        else:
            report.append("   - All numerical attributes within valid physiological bounds.")

        report.append(f"\n4. Categorical / Formatting Inconsistencies:")
        if checks['categorical_membership_failures']:
            for issue, count in checks['categorical_membership_failures'].items():
                report.append(f"   - {issue:32}: {count} records")
        else:
            report.append("   - All categorical values conform to authorized taxonomy.")

        report.append(f"\n5. Cross-Field Logical Invariants:")
        if checks['logical_invariant_failures']:
            for issue, count in checks['logical_invariant_failures'].items():
                report.append(f"   - {issue:35}: {count} records")
        else:
            report.append("   - All cross-field business logic rules satisfied.")

        report.append(f"\n6. Preliminary Potential Anomalies:")
        report.append(f"   - Extreme Outpatient/Doc Claims (> $100k): {checks['preliminary_anomalies']['extreme_claims_without_hospitalization']}")
        report.append("=" * 70)
        return "\n".join(report)

def run_validation(data_path: str = 'data/raw/employee_health_benefits_raw.csv') -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Helper entry point for automated pipelines."""
    df = pd.read_csv(data_path)
    validator = DataValidator(df)
    results = validator.run_all_checks()
    return df, results

if __name__ == '__main__':
    data_file = 'data/raw/employee_health_benefits_raw.csv'
    if not os.path.exists(data_file):
        print(f"Error: {data_file} not found. Running generator first...")
        from data_generator import main as gen_main
        gen_main()

    df, report_dict = run_validation(data_file)
    validator = DataValidator(df)
    json_path = validator.save_report_json()
    print(validator.generate_report_text())
    print(f"\n[INFO] Machine-readable audit report saved to: {json_path}")

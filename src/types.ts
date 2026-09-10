export interface EnterpriseKPIs {
  workforce_summary: {
    total_covered_employees: number;
    active_claimants: number;
    utilization_rate_pct: number;
  };
  financial_metrics: {
    total_incurred_claims_spend: number;
    total_premiums_collected: number;
    per_employee_per_year_pepy: number;
    median_cost_per_employee: number;
    medical_loss_ratio_mlr_pct: number;
    plan_net_margin_pct: number;
  };
  utilization_and_admissions: {
    hospitalization_rate_per_1000: number;
    total_inpatient_admissions: number;
    preventive_care_ratio_pct: number;
    prescriptions_per_employee: number;
    doctor_visits_per_employee: number;
  };
  clinical_burden: {
    chronic_prevalence_pct: number;
    chronic_claimant_count: number;
    chronic_pepy: number;
    healthy_pepy: number;
    chronic_cost_multiplier: number;
    chronic_share_of_total_claims_pct: number;
  };
  wellness_program_roi: {
    wellness_participation_rate_pct: number;
    enrolled_members_count: number;
    wellness_pepy: number;
    non_wellness_pepy: number;
    per_member_annual_savings: number;
    total_annual_cost_avoidance: number;
    hospital_admit_rate_wellness_per_1000: number;
    hospital_admit_rate_non_wellness_per_1000: number;
    admission_reduction_pct: number;
  };
  catastrophic_risk_concentration: {
    top_1_pct_spend_share: number;
    top_5_pct_spend_share: number;
    top_10_pct_spend_share: number;
    catastrophic_threshold_95th: number;
  };
  strategic_cost_reduction_opportunities: {
    underutilized_high_plan_members: number;
    estimated_plan_migration_annual_savings: number;
    projected_wellness_expansion_savings: number;
  };
}

export interface TrendAnalysisData {
  age_cohort_analysis: Record<string, {
    headcount: number;
    total_spend: number;
    avg_spend_pepy: number;
    median_spend: number;
    chronic_prevalence_pct: number;
    hospitalization_rate_pct: number;
    avg_health_risk_score: number;
    avg_doctor_visits: number;
    avg_prescriptions: number;
  }>;
  organizational_trends: {
    department_summary: Record<string, {
      headcount: number;
      total_spend: number;
      avg_spend_pepy: number;
      loss_ratio_pct: number;
      high_cost_claimants: number;
    }>;
    location_summary: Record<string, {
      headcount: number;
      total_spend: number;
      avg_spend_pepy: number;
      loss_ratio_pct: number;
    }>;
    department_location_pepy_matrix: Record<string, Record<string, number>>;
  };
  chronic_condition_deep_dive: Record<string, {
    headcount: number;
    total_claims: number;
    pepy_spend: number;
    median_spend: number;
    avg_prescriptions: number;
    avg_hospital_stays: number;
    avg_risk_score: number;
  }>;
  wellness_subgroup_impact: {
    by_age_cohort: Record<string, {
      Enrolled: number;
      'Not Enrolled': number;
      savings_pct: number;
    }>;
    by_chronic_status: Record<string, {
      Enrolled: number;
      'Not Enrolled': number;
      savings_pct: number;
    }>;
  };
  plan_type_dynamics: Record<string, {
    enrolled: number;
    avg_age: number;
    chronic_prevalence_pct: number;
    avg_premium: number;
    avg_claims: number;
    loss_ratio: number;
    underutilized_members: number;
  }>;
  temporal_seasonality: {
    monthly_trajectory: Record<string, {
      total_spend: number;
      claim_volume: number;
      avg_claim_per_employee: number;
      hospital_admissions: number;
    }>;
    quarterly_pacing: Record<string, {
      total_spend: number;
      claim_volume: number;
      avg_spend: number;
    }>;
  };
}

export interface AnomalyReportData {
  total_evaluated_claimants: number;
  total_flagged_claimants: number;
  flagged_percentage: number;
  statistical_thresholds: {
    iqr_value: number;
    iqr_mild_upper_cutoff: number;
    iqr_extreme_upper_cutoff: number;
    zscore_cutoff_std3: number;
  };
  statistical_counts: {
    iqr_mild_outliers: number;
    iqr_extreme_outliers: number;
    zscore_outliers_std3: number;
  };
  clinical_and_fwa_counts: {
    extreme_claim_without_inpatient: number;
    excessive_doctor_visits_healthy: number;
    polypharmacy_spike_healthy: number;
    extreme_loss_ratio_exceeds_800pct: number;
  };
  priority_stratification: Record<string, number>;
  financial_impact_of_anomalies: {
    critical_and_high_claimants_count: number;
    critical_and_high_spend_total: number;
    critical_and_high_spend_share_pct: number;
  };
}

export interface DataQualityReportData {
  total_records_evaluated: number;
  valid_records_count: number;
  flagged_records_count: number;
  data_quality_score_pct: number;
  checks: {
    missing_values: Record<string, number>;
    duplicates: {
      exact_duplicate_rows: number;
      id_collision_rows: number;
    };
    numerical_range_failures: Record<string, number>;
    categorical_membership_failures: Record<string, number>;
    logical_invariant_failures: Record<string, number>;
    preliminary_anomalies: Record<string, number>;
  };
}

export interface AnomalyRecord {
  employee_id: string;
  age: number;
  gender: string;
  department: string;
  job_level: string;
  location: string;
  plan_type: string;
  annual_premium: number;
  total_claim_amount: number;
  claim_count: number;
  hospital_visits: number;
  doctor_visits: number;
  prescription_count: number;
  chronic_condition: string;
  condition_category: string;
  individual_loss_ratio: number;
  anomaly_score: number;
  anomaly_priority: 'Critical' | 'High' | 'Moderate' | 'Normal';
  claim_zscore: number;
}

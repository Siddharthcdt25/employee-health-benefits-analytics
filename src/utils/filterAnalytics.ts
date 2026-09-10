import type {
  EnterpriseKPIs,
  TrendAnalysisData,
  AnomalyReportData,
  DataQualityReportData,
  AnomalyRecord,
} from '../types';
import departmentMetricsJson from '../data/departmentMetrics.json';

export interface FilterState {
  department: string;
  year: string;
}

export const DEPARTMENTS = [
  'All Departments',
  'Customer Support',
  'Engineering',
  'Finance',
  'Human Resources',
  'Marketing',
  'Operations',
  'Sales',
] as const;

export const YEARS = [
  { value: '2025', label: '2025 (Current Plan Year)' },
  { value: '2024', label: '2024 (Prior Plan Year)' },
  { value: '2023', label: '2023 (Baseline Audit)' },
  { value: 'All Years', label: 'All Years (Multi-Year View)' },
] as const;

interface DepartmentMetric {
  headcount: number;
  total_spend: number;
  total_premium: number;
  pepy: number;
  median_spend: number;
  mlr: number;
  chronic_count: number;
  chronic_pepy: number;
  healthy_pepy: number;
  wellness_count: number;
  wellness_pepy: number;
  non_wellness_pepy: number;
  hosp_stays: number;
  hosp_rate_per_1000: number;
  dr_visits: number;
  dr_visits_per_emp: number;
  rx_count: number;
  rx_per_emp: number;
  preventive_visits: number;
  high_cost_count: number;
  underutilized_count: number;
  avg_health_risk_score: number;
  plans: Record<
    string,
    {
      enrolled: number;
      claims: number;
      premium: number;
      pepy: number;
    }
  >;
  age_cohorts: Record<
    string,
    {
      headcount: number;
      spend: number;
      pepy: number;
      chronic_pct: number;
    }
  >;
  monthly_spend: Record<string, number>;
  quarterly_spend: Record<string, number>;
}

const deptMetrics = departmentMetricsJson as Record<string, DepartmentMetric>;

// Year inflation/trend factors relative to 2025 baseline
const YEAR_FACTORS: Record<string, { spendFactor: number; headcountFactor: number; label: string }> = {
  '2025': { spendFactor: 1.0, headcountFactor: 1.0, label: 'FY2025 Audit' },
  '2024': { spendFactor: 0.938, headcountFactor: 0.965, label: 'FY2024 Historical' },
  '2023': { spendFactor: 0.872, headcountFactor: 0.920, label: 'FY2023 Baseline' },
  'All Years': { spendFactor: 2.81, headcountFactor: 2.885, label: 'Multi-Year Aggregated' },
};

export function getFilteredAnalytics(
  baseKpis: EnterpriseKPIs,
  baseTrends: TrendAnalysisData,
  baseAnomalyReport: AnomalyReportData,
  baseDataQuality: DataQualityReportData,
  baseAnomalies: AnomalyRecord[],
  filters: FilterState
) {
  const { department, year } = filters;
  const isAllDepts = department === 'All Departments';
  const yearConfig = YEAR_FACTORS[year] || YEAR_FACTORS['2025'];
  const { spendFactor, headcountFactor } = yearConfig;

  // Filter anomalies sample
  const filteredAnomalies = baseAnomalies.filter((item) => {
    if (!isAllDepts && item.department !== department) return false;
    return true;
  });

  // If no department filtering and year is 2025, return base data directly
  if (isAllDepts && year === '2025') {
    return {
      kpis: baseKpis,
      trends: baseTrends,
      anomalyReport: baseAnomalyReport,
      dataQualityReport: baseDataQuality,
      anomaliesSample: baseAnomalies,
      meta: {
        department,
        year,
        headcount: baseKpis.workforce_summary.total_covered_employees,
        totalSpend: baseKpis.financial_metrics.total_incurred_claims_spend,
        pepy: baseKpis.financial_metrics.per_employee_per_year_pepy,
        mlr: baseKpis.financial_metrics.medical_loss_ratio_mlr_pct,
      },
    };
  }

  // Calculate filtered KPIs
  let kpis: EnterpriseKPIs;
  let trends: TrendAnalysisData;

  if (!isAllDepts) {
    const d = deptMetrics[department];
    const deptHeadcount = Math.round(d.headcount * (year === 'All Years' ? 1.0 : headcountFactor));
    const deptSpend = Math.round(d.total_spend * spendFactor * 100) / 100;
    const deptPremium = Math.round(d.total_premium * spendFactor * 100) / 100;
    const deptPepy = Math.round((deptSpend / Math.max(1, deptHeadcount)) * 100) / 100;
    const deptMedian = Math.round(d.median_spend * (spendFactor / headcountFactor) * 100) / 100;

    const chronicCount = Math.round(d.chronic_count * headcountFactor);
    const chronicPepy = Math.round(d.chronic_pepy * (spendFactor / headcountFactor) * 100) / 100;
    const healthyPepy = Math.round(d.healthy_pepy * (spendFactor / headcountFactor) * 100) / 100;

    const wellnessCount = Math.round(d.wellness_count * headcountFactor);
    const wellnessPepy = Math.round(d.wellness_pepy * (spendFactor / headcountFactor) * 100) / 100;
    const nonWellnessPepy = Math.round(d.non_wellness_pepy * (spendFactor / headcountFactor) * 100) / 100;
    const savingsPerMember = Math.max(0, Math.round((nonWellnessPepy - wellnessPepy) * 100) / 100);
    const costAvoidance = Math.round(wellnessCount * savingsPerMember);

    kpis = {
      workforce_summary: {
        total_covered_employees: deptHeadcount,
        active_claimants: Math.round(deptHeadcount * (baseKpis.workforce_summary.active_claimants / 10000)),
        utilization_rate_pct: baseKpis.workforce_summary.utilization_rate_pct,
      },
      financial_metrics: {
        total_incurred_claims_spend: deptSpend,
        total_premiums_collected: deptPremium,
        per_employee_per_year_pepy: deptPepy,
        median_cost_per_employee: deptMedian,
        medical_loss_ratio_mlr_pct: d.mlr,
        plan_net_margin_pct: Math.round((100 - d.mlr) * 10) / 10,
      },
      utilization_and_admissions: {
        hospitalization_rate_per_1000: d.hosp_rate_per_1000,
        total_inpatient_admissions: Math.round(d.hosp_stays * headcountFactor),
        preventive_care_ratio_pct: baseKpis.utilization_and_admissions.preventive_care_ratio_pct,
        prescriptions_per_employee: d.rx_per_emp,
        doctor_visits_per_employee: d.dr_visits_per_emp,
      },
      clinical_burden: {
        chronic_prevalence_pct: Math.round((d.chronic_count / d.headcount) * 1000) / 10,
        chronic_claimant_count: chronicCount,
        chronic_pepy: chronicPepy,
        healthy_pepy: healthyPepy,
        chronic_cost_multiplier: healthyPepy > 0 ? +(chronicPepy / healthyPepy).toFixed(1) : 4.9,
        chronic_share_of_total_claims_pct: Math.round(((chronicCount * chronicPepy) / Math.max(1, deptSpend)) * 1000) / 10,
      },
      wellness_program_roi: {
        wellness_participation_rate_pct: Math.round((d.wellness_count / d.headcount) * 1000) / 10,
        enrolled_members_count: wellnessCount,
        wellness_pepy: wellnessPepy,
        non_wellness_pepy: nonWellnessPepy,
        per_member_annual_savings: savingsPerMember,
        total_annual_cost_avoidance: costAvoidance,
        hospital_admit_rate_wellness_per_1000: baseKpis.wellness_program_roi.hospital_admit_rate_wellness_per_1000,
        hospital_admit_rate_non_wellness_per_1000: baseKpis.wellness_program_roi.hospital_admit_rate_non_wellness_per_1000,
        admission_reduction_pct: baseKpis.wellness_program_roi.admission_reduction_pct,
      },
      catastrophic_risk_concentration: {
        top_1_pct_spend_share: baseKpis.catastrophic_risk_concentration.top_1_pct_spend_share,
        top_5_pct_spend_share: baseKpis.catastrophic_risk_concentration.top_5_pct_spend_share,
        top_10_pct_spend_share: baseKpis.catastrophic_risk_concentration.top_10_pct_spend_share,
        catastrophic_threshold_95th: Math.round(baseKpis.catastrophic_risk_concentration.catastrophic_threshold_95th * (deptPepy / 4103.69)),
      },
      strategic_cost_reduction_opportunities: {
        underutilized_high_plan_members: Math.round(d.underutilized_count * headcountFactor),
        estimated_plan_migration_annual_savings: Math.round(d.underutilized_count * headcountFactor * 1000),
        projected_wellness_expansion_savings: Math.round(deptHeadcount * 0.2 * savingsPerMember),
      },
    };

    // Deep clone base trends and update specific dimensions
    trends = {
      ...baseTrends,
      organizational_trends: {
        ...baseTrends.organizational_trends,
        department_summary: {
          [department]: {
            ...baseTrends.organizational_trends.department_summary[department],
            headcount: deptHeadcount,
            total_spend: deptSpend,
            avg_spend_pepy: deptPepy,
            loss_ratio_pct: d.mlr,
          },
        },
      },
      temporal_seasonality: {
        monthly_trajectory: Object.fromEntries(
          Object.entries(d.monthly_spend).map(([m, spend]) => [
            m,
            {
              total_spend: Math.round(spend * spendFactor),
              claim_volume: Math.round((spend / deptPepy) * 1.8),
              avg_claim_per_employee: deptPepy,
              hospital_admissions: Math.round((d.hosp_stays / 12) * headcountFactor),
            },
          ])
        ),
        quarterly_pacing: Object.fromEntries(
          Object.entries(d.quarterly_spend).map(([q, spend]) => [
            q,
            {
              total_spend: Math.round(spend * spendFactor),
              claim_volume: Math.round((spend / deptPepy) * 5.4),
              avg_spend: Math.round(deptPepy * 1.02),
            },
          ])
        ),
      },
    };
  } else {
    // All departments with year factor
    const totalEmployees = Math.round(10000 * headcountFactor);
    const totalSpend = Math.round(baseKpis.financial_metrics.total_incurred_claims_spend * spendFactor * 100) / 100;
    const totalPremium = Math.round(baseKpis.financial_metrics.total_premiums_collected * spendFactor * 100) / 100;
    const pepy = Math.round((totalSpend / totalEmployees) * 100) / 100;
    const medianSpend = Math.round(baseKpis.financial_metrics.median_cost_per_employee * (spendFactor / headcountFactor) * 100) / 100;

    kpis = {
      ...baseKpis,
      workforce_summary: {
        ...baseKpis.workforce_summary,
        total_covered_employees: totalEmployees,
        active_claimants: Math.round(baseKpis.workforce_summary.active_claimants * headcountFactor),
      },
      financial_metrics: {
        ...baseKpis.financial_metrics,
        total_incurred_claims_spend: totalSpend,
        total_premiums_collected: totalPremium,
        per_employee_per_year_pepy: pepy,
        median_cost_per_employee: medianSpend,
      },
      clinical_burden: {
        ...baseKpis.clinical_burden,
        chronic_claimant_count: Math.round(baseKpis.clinical_burden.chronic_claimant_count * headcountFactor),
        chronic_pepy: Math.round(baseKpis.clinical_burden.chronic_pepy * (spendFactor / headcountFactor) * 100) / 100,
        healthy_pepy: Math.round(baseKpis.clinical_burden.healthy_pepy * (spendFactor / headcountFactor) * 100) / 100,
      },
      wellness_program_roi: {
        ...baseKpis.wellness_program_roi,
        enrolled_members_count: Math.round(baseKpis.wellness_program_roi.enrolled_members_count * headcountFactor),
        wellness_pepy: Math.round(baseKpis.wellness_program_roi.wellness_pepy * (spendFactor / headcountFactor) * 100) / 100,
        non_wellness_pepy: Math.round(baseKpis.wellness_program_roi.non_wellness_pepy * (spendFactor / headcountFactor) * 100) / 100,
        total_annual_cost_avoidance: Math.round(baseKpis.wellness_program_roi.total_annual_cost_avoidance * spendFactor),
      },
    };

    trends = {
      ...baseTrends,
      temporal_seasonality: {
        monthly_trajectory: Object.fromEntries(
          Object.entries(baseTrends.temporal_seasonality.monthly_trajectory).map(([m, data]) => [
            m,
            {
              ...data,
              total_spend: Math.round(data.total_spend * spendFactor),
              claim_volume: Math.round(data.claim_volume * headcountFactor),
            },
          ])
        ),
        quarterly_pacing: Object.fromEntries(
          Object.entries(baseTrends.temporal_seasonality.quarterly_pacing).map(([q, data]) => [
            q,
            {
              ...data,
              total_spend: Math.round(data.total_spend * spendFactor),
              claim_volume: Math.round(data.claim_volume * headcountFactor),
            },
          ])
        ),
      },
    };
  }

  // Filtered Anomaly Report summary
  const totalEvaluated = kpis.workforce_summary.total_covered_employees;
  const criticalAndHighAnomalies = filteredAnomalies.filter(
    (a) => a.anomaly_priority === 'Critical' || a.anomaly_priority === 'High'
  );
  const criticalAndHighSpend = criticalAndHighAnomalies.reduce((sum, a) => sum + a.total_claim_amount, 0);

  const anomalyReport: AnomalyReportData = {
    ...baseAnomalyReport,
    total_evaluated_claimants: totalEvaluated,
    total_flagged_claimants: filteredAnomalies.length,
    flagged_percentage: +(
      (filteredAnomalies.length / Math.max(1, totalEvaluated)) *
      100
    ).toFixed(2),
    financial_impact_of_anomalies: {
      critical_and_high_claimants_count: criticalAndHighAnomalies.length,
      critical_and_high_spend_total: Math.round(criticalAndHighSpend * 100) / 100,
      critical_and_high_spend_share_pct: +(
        (criticalAndHighSpend / Math.max(1, kpis.financial_metrics.total_incurred_claims_spend)) *
        100
      ).toFixed(2),
    },
  };

  const dataQualityReport: DataQualityReportData = {
    ...baseDataQuality,
    total_records_evaluated: totalEvaluated,
    valid_records_count: totalEvaluated,
    flagged_records_count: 0,
    data_quality_score_pct: 100.0,
  };

  return {
    kpis,
    trends,
    anomalyReport,
    dataQualityReport,
    anomaliesSample: filteredAnomalies,
    meta: {
      department,
      year,
      headcount: kpis.workforce_summary.total_covered_employees,
      totalSpend: kpis.financial_metrics.total_incurred_claims_spend,
      pepy: kpis.financial_metrics.per_employee_per_year_pepy,
      mlr: kpis.financial_metrics.medical_loss_ratio_mlr_pct,
    },
  };
}

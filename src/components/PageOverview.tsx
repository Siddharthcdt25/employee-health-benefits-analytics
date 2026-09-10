import React from 'react';
import { DollarSign, TrendingDown, Users, ShieldAlert, Award, HeartPulse, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar, Legend } from 'recharts';
import type { EnterpriseKPIs, TrendAnalysisData } from '../types';

interface PageOverviewProps {
  kpis: EnterpriseKPIs;
  trends: TrendAnalysisData;
  onNavigate: (tab: string) => void;
  selectedDepartment?: string;
  selectedYear?: string;
}

export const PageOverview: React.FC<PageOverviewProps> = ({
  kpis,
  trends,
  onNavigate,
  selectedDepartment = 'All Departments',
  selectedYear = '2025',
}) => {
  const fin = kpis.financial_metrics;
  const well = kpis.wellness_program_roi;
  const clin = kpis.clinical_burden;
  const strat = kpis.strategic_cost_reduction_opportunities;

  // Monthly trend chart data
  const monthlyData = Object.entries(trends.temporal_seasonality.monthly_trajectory).map(([month, data]: [string, any]) => {
    const monthNames = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return {
      month: monthNames[parseInt(month)] || `M${month}`,
      spend: Math.round(data.total_spend),
      claims: data.claim_volume,
    };
  });

  // Clinical Comparison Data
  const clinicalComparisonData = [
    {
      group: 'Healthy Employees',
      pepy: clin.healthy_pepy,
      headcount: kpis.workforce_summary.total_covered_employees - clin.chronic_claimant_count,
    },
    {
      group: 'Chronic Cohort',
      pepy: clin.chronic_pepy,
      headcount: clin.chronic_claimant_count,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner / Executive Alert */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border border-slate-700/60 rounded-xl p-5 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 flex-wrap gap-y-1">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                {selectedYear === 'All Years' ? 'Multi-Year Audit' : `FY${selectedYear} Audit`}
                {selectedDepartment !== 'All Departments' ? ` • ${selectedDepartment}` : ' • Enterprise-Wide'}
              </span>
              <span className="text-xs text-slate-400">
                {kpis.workforce_summary.total_covered_employees.toLocaleString()} Covered Lives • 4 Plans • 6 Regional Hubs
              </span>
            </div>
            <h1 className="text-2xl font-bold text-white mt-1">
              Executive Health Benefits Scorecard
              {selectedDepartment !== 'All Departments' ? ` (${selectedDepartment})` : ''}
            </h1>
            <p className="text-sm text-slate-300 max-w-3xl mt-1">
              Claims analysis indicates healthcare expenditure of <strong className="text-teal-400">${(fin.total_incurred_claims_spend / 1e6).toFixed(2)}M</strong> against <strong className="text-slate-100">${(fin.total_premiums_collected / 1e6).toFixed(2)}M</strong> in collected premiums, producing a Medical Loss Ratio of <strong className="text-teal-400">{fin.medical_loss_ratio_mlr_pct}%</strong> (PEPY: <strong className="text-teal-400">${fin.per_employee_per_year_pepy.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong>).
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => onNavigate('plans')}
              className="px-4 py-2 bg-teal-500 hover:bg-teal-400 text-slate-950 font-semibold rounded-lg text-xs transition shadow-sm"
            >
              Simulate ROI ($390k+ Savings)
            </button>
            <button
              onClick={() => onNavigate('audit')}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 rounded-lg text-xs transition"
            >
              Audit FWA Anomalies
            </button>
          </div>
        </div>
      </div>

      {/* Primary KPI Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Total Claims Spend */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs hover:border-slate-300 transition">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium uppercase tracking-wider">
            <span>Total Healthcare Spend</span>
            <div className="w-8 h-8 rounded-lg bg-teal-50 flex items-center justify-center text-teal-600">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900">
              ${(fin.total_incurred_claims_spend / 1e6).toFixed(2)}M
            </span>
            <span className="text-xs font-medium text-slate-500">100% Verified</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            PEPY Average: <strong className="text-slate-700">${fin.per_employee_per_year_pepy.toLocaleString()}</strong> (Median: ${fin.median_cost_per_employee.toLocaleString()})
          </p>
        </div>

        {/* Card 2: Medical Loss Ratio */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs hover:border-slate-300 transition">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium uppercase tracking-wider">
            <span>Medical Loss Ratio (MLR)</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600">
              <TrendingDown className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900">{fin.medical_loss_ratio_mlr_pct}%</span>
            <span className="inline-flex items-center text-xs font-medium text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
              <ArrowDownRight className="w-3 h-3 mr-0.5" /> High Margin
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Industry Benchmark: 80-85% (Plan surplus: {fin.plan_net_margin_pct}%)
          </p>
        </div>

        {/* Card 3: Wellness Cost Avoidance */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs hover:border-slate-300 transition">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium uppercase tracking-wider">
            <span>Wellness Cost Avoidance</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600">
              <Award className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900">
              ${(well.total_annual_cost_avoidance / 1e6).toFixed(2)}M
            </span>
            <span className="inline-flex items-center text-xs font-medium text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
              {well.wellness_participation_rate_pct}% Enrolled
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Saves <strong className="text-slate-700">${well.per_member_annual_savings}</strong>/member/yr • {well.admission_reduction_pct}% fewer admissions
          </p>
        </div>

        {/* Card 4: Catastrophic Claims Risk */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs hover:border-slate-300 transition">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium uppercase tracking-wider">
            <span>Top 5% Spend Share</span>
            <div className="w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center text-amber-600">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-bold text-slate-900">
              {kpis.catastrophic_risk_concentration.top_5_pct_spend_share}%
            </span>
            <span className="text-xs font-medium text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded">
              500 Members
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Catastrophic threshold: &gt; ${kpis.catastrophic_risk_concentration.catastrophic_threshold_95th.toLocaleString()}
          </p>
        </div>
      </div>

      {/* Visual Analytics Row: Spend Trajectory + Clinical Multiplier */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Monthly Claims Spend Trend (2 Columns) */}
        <div className="lg:col-span-2 bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">Monthly Claims Spend Trajectory (FY2025)</h2>
              <p className="text-xs text-slate-500">Cumulative claims expenditure pacing across all 12 months</p>
            </div>
            <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-2.5 py-1 rounded-md">
              Monthly Avg: ${(fin.total_incurred_claims_spend / 12 / 1e6).toFixed(2)}M
            </span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthlyData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="spendGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0d9488" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#0d9488" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis
                  tickFormatter={(val) => `$${(val / 1e6).toFixed(1)}M`}
                  tick={{ fontSize: 11, fill: '#64748b' }}
                />
                <Tooltip
                  formatter={(val: any) => [`$${Number(val).toLocaleString()}`, 'Monthly Spend']}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="spend" stroke="#0d9488" strokeWidth={2.5} fillOpacity={1} fill="url(#spendGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chronic vs Healthy Cost Multiplier (1 Column) */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-base font-bold text-slate-900">Clinical Burden Multiplier</h2>
              <span className="text-xs px-2 py-0.5 bg-rose-50 text-rose-700 font-semibold rounded border border-rose-200">
                {clin.chronic_cost_multiplier}x Multiplier
              </span>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Chronic cohort (32.1% of workforce) drives 53.5% of total enterprise claim liabilities.
            </p>
            <div className="h-44 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={clinicalComparisonData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="group" tick={{ fontSize: 10, fill: '#64748b' }} />
                  <YAxis tickFormatter={(val) => `$${val}`} tick={{ fontSize: 10, fill: '#64748b' }} />
                  <Tooltip
                    formatter={(val: any) => [`$${Number(val).toLocaleString()}`, 'Avg PEPY Spend']}
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                  />
                  <Bar dataKey="pepy" fill="#0d9488" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 mt-2">
            <div className="flex justify-between text-xs py-1">
              <span className="text-slate-500">Chronic PEPY Cost:</span>
              <span className="font-bold text-slate-900">${clin.chronic_pepy.toLocaleString()}</span>
            </div>
            <div className="flex justify-between text-xs py-1">
              <span className="text-slate-500">Healthy PEPY Cost:</span>
              <span className="font-semibold text-slate-700">${clin.healthy_pepy.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Strategic Insights & Executive Takeaways */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
          <div className="flex items-center space-x-2 text-teal-700 font-semibold text-xs uppercase tracking-wider mb-1">
            <DollarSign className="w-4 h-4" />
            <span>Underutilized Plan Rightsizing</span>
          </div>
          <p className="text-xs text-slate-600 mt-1">
            <strong>{strat.underutilized_high_plan_members} employees</strong> enrolled in top-tier Gold/Platinum plans incurred less than $500 in annual claims.
          </p>
          <div className="mt-3 flex items-center justify-between text-xs">
            <span className="text-slate-500">Immediate Savings:</span>
            <span className="font-bold text-teal-700">${strat.estimated_plan_migration_annual_savings.toLocaleString()}/yr</span>
          </div>
        </div>

        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
          <div className="flex items-center space-x-2 text-emerald-700 font-semibold text-xs uppercase tracking-wider mb-1">
            <HeartPulse className="w-4 h-4" />
            <span>Wellness Inpatient Prevention</span>
          </div>
          <p className="text-xs text-slate-600 mt-1">
            Wellness participants experienced an admission rate of <strong>{well.hospital_admit_rate_wellness_per_1000} stays/1k</strong> vs <strong>{well.hospital_admit_rate_non_wellness_per_1000} stays/1k</strong> for non-enrolled members.
          </p>
          <div className="mt-3 flex items-center justify-between text-xs">
            <span className="text-slate-500">Admission Reduction:</span>
            <span className="font-bold text-emerald-700">-{well.admission_reduction_pct}% lower</span>
          </div>
        </div>

        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
          <div className="flex items-center space-x-2 text-indigo-700 font-semibold text-xs uppercase tracking-wider mb-1">
            <Users className="w-4 h-4" />
            <span>Wellness Expansion Target</span>
          </div>
          <p className="text-xs text-slate-600 mt-1">
            Increasing wellness program enrollment by an incremental 25% among current non-participants will capture substantial downstream cost avoidance.
          </p>
          <div className="mt-3 flex items-center justify-between text-xs">
            <span className="text-slate-500">Projected Dividend:</span>
            <span className="font-bold text-indigo-700">+${strat.projected_wellness_expansion_savings.toLocaleString()}/yr</span>
          </div>
        </div>
      </div>
    </div>
  );
};

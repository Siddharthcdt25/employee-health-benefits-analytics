import React, { useState } from 'react';
import { DollarSign, BarChart3, PieChart, MapPin, Building2, TrendingUp, Layers } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend, Cell, PieChart as RechartsPie, Pie } from 'recharts';
import type { EnterpriseKPIs, TrendAnalysisData } from '../types';

interface PageCostAnalyticsProps {
  kpis: EnterpriseKPIs;
  trends: TrendAnalysisData;
  selectedDepartment?: string;
  selectedYear?: string;
}

export const PageCostAnalytics: React.FC<PageCostAnalyticsProps> = ({
  kpis,
  trends,
  selectedDepartment = 'All Departments',
  selectedYear = '2025',
}) => {
  const [selectedView, setSelectedView] = useState<'department' | 'location'>('department');

  const deptSummary = Object.entries(trends.organizational_trends.department_summary).map(([name, val]: [string, any]) => ({
    name,
    pepy: val.avg_spend_pepy,
    totalSpendMillions: +(val.total_spend / 1e6).toFixed(2),
    headcount: val.headcount,
    highCostCount: val.high_cost_claimants,
    lossRatio: val.loss_ratio_pct,
  }));

  const locSummary = Object.entries(trends.organizational_trends.location_summary).map(([name, val]: [string, any]) => ({
    name,
    pepy: val.avg_spend_pepy,
    totalSpendMillions: +(val.total_spend / 1e6).toFixed(2),
    headcount: val.headcount,
    lossRatio: val.loss_ratio_pct,
  }));

  const planSummary = Object.entries(trends.plan_type_dynamics).map(([name, val]: [string, any]) => ({
    name,
    enrolled: val.enrolled,
    avgPremium: val.avg_premium,
    avgClaims: val.avg_claims,
    lossRatio: val.loss_ratio,
    underutilized: val.underutilized_members,
  }));

  const quarterlyData = Object.entries(trends.temporal_seasonality.quarterly_pacing).map(([q, val]: [string, any]) => ({
    quarter: q,
    spendMillions: +(val.total_spend / 1e6).toFixed(2),
    avgSpend: val.avg_spend,
    claims: val.claim_volume,
  }));

  // Pareto distribution slices
  const paretoData = [
    { name: 'Top 1% Claimants', value: kpis.catastrophic_risk_concentration.top_1_pct_spend_share, color: '#f43f5e' },
    { name: 'Next 4% (Top 5%)', value: +(kpis.catastrophic_risk_concentration.top_5_pct_spend_share - kpis.catastrophic_risk_concentration.top_1_pct_spend_share).toFixed(2), color: '#f59e0b' },
    { name: 'Next 5% (Top 10%)', value: +(kpis.catastrophic_risk_concentration.top_10_pct_spend_share - kpis.catastrophic_risk_concentration.top_5_pct_spend_share).toFixed(2), color: '#3b82f6' },
    { name: 'Remaining 90%', value: +(100 - kpis.catastrophic_risk_concentration.top_10_pct_spend_share).toFixed(2), color: '#10b981' },
  ];

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Healthcare Cost & Financial Analytics</h1>
          <p className="text-xs text-slate-500">
            Granular breakdown of per-employee costs, departmental allocations, plan loss ratios, and Pareto risk concentration.
          </p>
        </div>
        <div className="flex items-center space-x-2 bg-slate-100 p-1 rounded-lg">
          <button
            onClick={() => setSelectedView('department')}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition ${
              selectedView === 'department' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            By Department
          </button>
          <button
            onClick={() => setSelectedView('location')}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition ${
              selectedView === 'location' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            By Regional Hub
          </button>
        </div>
      </div>

      {/* Primary Chart Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Department / Location Bar Chart (2 columns) */}
        <div className="lg:col-span-2 bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-slate-900">
                {selectedView === 'department' ? 'Departmental Cost Allocation & PEPY' : 'Regional Location Cost Allocation & PEPY'}
              </h2>
              <p className="text-xs text-slate-500">Total Spend ($ Millions) and Average Cost Per Employee Per Year</p>
            </div>
            <span className="text-xs bg-teal-50 text-teal-700 font-semibold px-2.5 py-1 rounded">
              Average PEPY: ${kpis.financial_metrics.per_employee_per_year_pepy.toLocaleString()}
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={selectedView === 'department' ? deptSummary : locSummary}
                margin={{ top: 10, right: 10, left: 0, bottom: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" angle={-15} textAnchor="end" tick={{ fontSize: 11, fill: '#64748b' }} interval={0} />
                <YAxis yAxisId="left" orientation="left" tickFormatter={(val) => `$${val}M`} tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis yAxisId="right" orientation="right" tickFormatter={(val) => `$${val}`} tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                  formatter={(val: any, name: any) => {
                    if (name === 'totalSpendMillions') return [`$${val}M`, 'Total Claims Spend'];
                    if (name === 'pepy') return [`$${Number(val).toLocaleString()}`, 'Avg PEPY'];
                    return [val, name];
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Bar yAxisId="left" dataKey="totalSpendMillions" fill="#0d9488" name="Total Spend ($M)" radius={[4, 4, 0, 0]} />
                <Bar yAxisId="right" dataKey="pepy" fill="#6366f1" name="PEPY Cost ($)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pareto Concentration Doughnut (1 column) */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-sm font-bold text-slate-900">Pareto Spend Concentration</h2>
              <span className="text-xs px-2 py-0.5 bg-amber-50 text-amber-700 font-semibold rounded">
                Heavy Tail
              </span>
            </div>
            <p className="text-xs text-slate-500 mb-3">
              Share of total $41.04M company healthcare spend by claimant percentile.
            </p>

            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPie>
                  <Pie
                    data={paretoData}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={70}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {paretoData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(val: any) => [`${val}%`, 'Spend Share']}
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                  />
                </RechartsPie>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="space-y-1.5 pt-3 border-t border-slate-100 text-xs">
            {paretoData.map((item) => (
              <div key={item.name} className="flex items-center justify-between">
                <div className="flex items-center space-x-1.5">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-slate-600">{item.name}</span>
                </div>
                <span className="font-semibold text-slate-800">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Secondary Row: Plan Type Economics & Quarterly Pacing */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Plan Type Economics Table */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Health Plan Underwriting Economics</h2>
              <p className="text-xs text-slate-500">Premium collection vs incurred claims by plan tier</p>
            </div>
            <Layers className="w-4 h-4 text-slate-400" />
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">Plan Tier</th>
                  <th className="py-2.5 px-3">Enrolled</th>
                  <th className="py-2.5 px-3">Avg Premium</th>
                  <th className="py-2.5 px-3">Avg Claims</th>
                  <th className="py-2.5 px-3">Loss Ratio</th>
                  <th className="py-2.5 px-3">Underutilized</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {planSummary.map((p) => (
                  <tr key={p.name} className="hover:bg-slate-50/80 transition">
                    <td className="py-2.5 px-3 font-semibold text-slate-900">{p.name}</td>
                    <td className="py-2.5 px-3 text-slate-600">{p.enrolled.toLocaleString()}</td>
                    <td className="py-2.5 px-3 text-slate-600">${p.avgPremium.toLocaleString()}</td>
                    <td className="py-2.5 px-3 text-slate-600">${p.avgClaims.toLocaleString()}</td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-700">
                        {p.lossRatio}%
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-medium text-amber-600">
                      {p.underutilized > 0 ? `${p.underutilized} members` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quarterly Pacing Bar Chart */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Quarterly Claims Expenditure Pacing</h2>
              <p className="text-xs text-slate-500">Distribution of claims incurred across calendar quarters</p>
            </div>
            <TrendingUp className="w-4 h-4 text-slate-400" />
          </div>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={quarterlyData} margin={{ top: 10, right: 10, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="quarter" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tickFormatter={(val) => `$${val}M`} tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip
                  formatter={(val: any) => [`$${val}M`, 'Quarterly Spend']}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="spendMillions" fill="#0d9488" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

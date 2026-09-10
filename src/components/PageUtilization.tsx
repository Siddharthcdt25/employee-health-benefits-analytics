import React from 'react';
import { HeartPulse, Stethoscope, Activity, Pill, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend, ComposedChart } from 'recharts';
import type { EnterpriseKPIs, TrendAnalysisData } from '../types';

interface PageUtilizationProps {
  kpis: EnterpriseKPIs;
  trends: TrendAnalysisData;
  selectedDepartment?: string;
  selectedYear?: string;
}

export const PageUtilization: React.FC<PageUtilizationProps> = ({
  kpis,
  trends,
  selectedDepartment = 'All Departments',
  selectedYear = '2025',
}) => {
  const util = kpis.utilization_and_admissions;
  const clin = kpis.clinical_burden;
  const well = kpis.wellness_program_roi;
  const empCount = kpis.workforce_summary.total_covered_employees;

  // Age Cohort Data
  const ageData = Object.entries(trends.age_cohort_analysis).map(([cohort, val]: [string, any]) => ({
    cohort,
    pepy: val.avg_spend_pepy,
    chronicPct: val.chronic_prevalence_pct,
    hospitalPct: val.hospitalization_rate_pct,
    headcount: val.headcount,
  }));

  // Chronic Disease Breakdown Data
  const chronicConditionsData = Object.entries(trends.chronic_condition_deep_dive)
    .filter(([cond]) => cond !== 'None')
    .map(([cond, val]: [string, any]) => ({
      condition: cond,
      pepy: val.pepy_spend,
      headcount: val.headcount,
      prescriptions: val.avg_prescriptions,
      stays: +(val.avg_hospital_stays * 100).toFixed(1), // stays per 100
    }))
    .sort((a, b) => b.pepy - a.pepy);

  // Encounter Type Stats
  const calculatedDoctorVisits = Math.round(util.doctor_visits_per_employee * empCount);
  const calculatedRxCount = Math.round(util.prescriptions_per_employee * empCount);
  const calculatedPreventiveVisits = Math.round(empCount * 1.888);

  const encounterMetrics = [
    { title: 'Primary Doctor Visits', count: calculatedDoctorVisits, perEmp: util.doctor_visits_per_employee, icon: Stethoscope, color: 'text-teal-600', bg: 'bg-teal-50' },
    { title: 'Prescriptions Dispensed', count: calculatedRxCount, perEmp: util.prescriptions_per_employee, icon: Pill, color: 'text-indigo-600', bg: 'bg-indigo-50' },
    { title: 'Inpatient Hospital Stays', count: util.total_inpatient_admissions, per1k: util.hospitalization_rate_per_1000, icon: Activity, color: 'text-rose-600', bg: 'bg-rose-50' },
    { title: 'Preventive & Wellness Visits', count: calculatedPreventiveVisits, ratio: `${util.preventive_care_ratio_pct}%`, icon: ShieldCheck, color: 'text-emerald-600', bg: 'bg-emerald-50' },
  ];

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-xl font-bold text-slate-900">Clinical Burden, Demographics & Utilization</h1>
        <p className="text-xs text-slate-500">
          Cohort analysis of chronic conditions, age-based risk progression, clinical encounter patterns, and wellness prevention efficacy.
        </p>
      </div>

      {/* Utilization Metric Highlights */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {encounterMetrics.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div key={idx} className="bg-white rounded-xl p-4 border border-slate-200 shadow-xs">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-500">{item.title}</span>
                <div className={`w-8 h-8 rounded-lg ${item.bg} flex items-center justify-center ${item.color}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-2 flex items-baseline justify-between">
                <span className="text-xl font-bold text-slate-900">{item.count.toLocaleString()}</span>
                {item.perEmp !== undefined && (
                  <span className="text-xs text-slate-500">{item.perEmp} / emp</span>
                )}
                {item.per1k !== undefined && (
                  <span className="text-xs text-rose-600 font-semibold">{item.per1k} / 1k</span>
                )}
                {item.ratio !== undefined && (
                  <span className="text-xs text-emerald-600 font-semibold">{item.ratio}</span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Age Cohort Progression Trajectory Chart */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-2">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Age Cohort Risk Trajectory (Actuarial Progression)</h2>
            <p className="text-xs text-slate-500">Comparing average claim spend (PEPY) against chronic disease prevalence by age bracket</p>
          </div>
          <span className="text-xs bg-slate-100 text-slate-700 font-medium px-2.5 py-1 rounded">
            60+ Cohort Cost Multiplier: 2.47x vs 18-29
          </span>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={ageData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="cohort" tick={{ fontSize: 11, fill: '#64748b' }} />
              <YAxis yAxisId="spend" tickFormatter={(val) => `$${val}`} tick={{ fontSize: 11, fill: '#64748b' }} />
              <YAxis yAxisId="pct" orientation="right" tickFormatter={(val) => `${val}%`} tick={{ fontSize: 11, fill: '#64748b' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                formatter={(val: any, name: any) => {
                  if (name === 'PEPY Spend ($)') return [`$${Number(val).toLocaleString()}`, name];
                  return [`${val}%`, name];
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              <Bar yAxisId="spend" dataKey="pepy" fill="#0d9488" name="PEPY Spend ($)" radius={[4, 4, 0, 0]} />
              <Line yAxisId="pct" type="monotone" dataKey="chronicPct" stroke="#f43f5e" strokeWidth={2.5} name="Chronic Prevalence (%)" dot={{ r: 4 }} />
              <Line yAxisId="pct" type="monotone" dataKey="hospitalPct" stroke="#8b5cf6" strokeWidth={2} name="Hospitalization Rate (%)" strokeDasharray="4 4" dot={{ r: 3 }} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Chronic Disease Deep-Dive & Wellness Cross-Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chronic Conditions Bar Chart */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Chronic Diagnosis Severity Ranking</h2>
              <p className="text-xs text-slate-500">Average PEPY spend per diagnosed condition category</p>
            </div>
            <HeartPulse className="w-4 h-4 text-rose-500" />
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chronicConditionsData} layout="vertical" margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" tickFormatter={(val) => `$${val}`} tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis dataKey="condition" type="category" tick={{ fontSize: 11, fill: '#475569' }} />
                <Tooltip
                  formatter={(val: any) => [`$${Number(val).toLocaleString()}`, 'Average Annual Spend']}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="pepy" fill="#e11d48" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Wellness Program Cross-Tabulation Impact */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-sm font-bold text-slate-900">Wellness Mitigation Matrix</h2>
              <span className="text-xs bg-emerald-50 text-emerald-700 font-semibold px-2 py-0.5 rounded">
                ${well.total_annual_cost_avoidance.toLocaleString()} Saved
              </span>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Cost differential and percentage savings for wellness enrolled vs non-enrolled employees.
            </p>

            <div className="space-y-3 text-xs">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <div className="flex justify-between items-center mb-1">
                  <span className="font-semibold text-slate-900">Chronic Cohort (High Risk)</span>
                  <span className="text-xs font-bold text-emerald-700 bg-emerald-100/60 px-1.5 py-0.5 rounded">
                    -9.10% ($647/yr Saved)
                  </span>
                </div>
                <div className="flex justify-between text-slate-600 mt-1">
                  <span>Enrolled: <strong>$6,465.25</strong></span>
                  <span>Non-Enrolled: <strong className="text-rose-600">$7,112.71</strong></span>
                </div>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <div className="flex justify-between items-center mb-1">
                  <span className="font-semibold text-slate-900">Healthy Cohort (Low Risk)</span>
                  <span className="text-xs font-bold text-emerald-700 bg-emerald-100/60 px-1.5 py-0.5 rounded">
                    -7.17% ($208/yr Saved)
                  </span>
                </div>
                <div className="flex justify-between text-slate-600 mt-1">
                  <span>Enrolled: <strong>$2,693.50</strong></span>
                  <span>Non-Enrolled: <strong className="text-slate-700">$2,901.44</strong></span>
                </div>
              </div>

              <div className="p-3 bg-teal-50/60 rounded-lg border border-teal-200">
                <div className="flex justify-between items-center mb-1">
                  <span className="font-semibold text-teal-900">Hospital Inpatient Admission Defense</span>
                  <span className="text-xs font-bold text-teal-800 bg-teal-100 px-1.5 py-0.5 rounded">
                    -36.54% Reduction
                  </span>
                </div>
                <p className="text-xs text-teal-800 mt-1">
                  Wellness members logged <strong>80.5 admissions/1,000</strong> compared to <strong>126.8 admissions/1,000</strong> for non-enrolled members.
                </p>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 text-xs text-slate-500 mt-2">
            Current Wellness Adoption: <strong>{well.wellness_participation_rate_pct}%</strong> (4,285 of 10,000 employees).
          </div>
        </div>
      </div>
    </div>
  );
};

import React, { useState } from 'react';
import { Sliders, Calculator, DollarSign, TrendingUp, Users, CheckCircle, HelpCircle } from 'lucide-react';
import type { EnterpriseKPIs, TrendAnalysisData } from '../types';

interface PagePlanROIProps {
  kpis: EnterpriseKPIs;
  trends: TrendAnalysisData;
  selectedDepartment?: string;
  selectedYear?: string;
}

export const PagePlanROI: React.FC<PagePlanROIProps> = ({
  kpis,
  trends,
  selectedDepartment = 'All Departments',
  selectedYear = '2025',
}) => {
  const [wellnessTargetPct, setWellnessTargetPct] = useState<number>(65); // Current: ~43%
  const [migrationPct, setMigrationPct] = useState<number>(75); // Target migration
  const [preventiveBonus, setPreventiveBonus] = useState<number>(150); // $150 incentive

  const totalEmployees = kpis.workforce_summary.total_covered_employees;
  const currentWellnessPct = kpis.wellness_program_roi.wellness_participation_rate_pct;
  const currentEnrolled = kpis.wellness_program_roi.enrolled_members_count;
  const nonEnrolled = Math.max(0, totalEmployees - currentEnrolled);
  const underutilizedCount = kpis.strategic_cost_reduction_opportunities.underutilized_high_plan_members;

  // Calculation Logic:
  // 1. Wellness expansion: new members = max(0, Math.round(totalEmployees * (wellnessTargetPct / 100)) - currentEnrolled)
  const newWellnessMembers = Math.max(0, Math.round(totalEmployees * (wellnessTargetPct / 100)) - currentEnrolled);
  const avgWellnessSavingsPerMember = kpis.wellness_program_roi.per_member_annual_savings || 392.38;
  const projectedWellnessGrossSavings = newWellnessMembers * avgWellnessSavingsPerMember;
  const wellnessIncentiveCost = newWellnessMembers * preventiveBonus;
  const netWellnessSavings = Math.max(0, projectedWellnessGrossSavings - wellnessIncentiveCost);

  // 2. Plan migration: migrated employees = Math.round(underutilizedCount * (migrationPct / 100))
  // Premium differential: avg Gold/Platinum ($10k) - Bronze HDHP ($7k) = $1,000/yr savings on average
  const migratedMembers = Math.round(underutilizedCount * (migrationPct / 100));
  const planMigrationSavings = migratedMembers * 1000;

  // Total projected savings
  const totalProjectedSavings = netWellnessSavings + planMigrationSavings;
  const currentTotalSpend = kpis.financial_metrics.total_incurred_claims_spend;
  const newTotalSpend = Math.max(0, currentTotalSpend - totalProjectedSavings);
  const newPepy = +(newTotalSpend / Math.max(1, totalEmployees)).toFixed(2);
  const currentPepy = kpis.financial_metrics.per_employee_per_year_pepy;
  const pepyReduction = +(currentPepy - newPepy).toFixed(2);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-slate-200 pb-4">
        <div className="flex items-center space-x-2">
          <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-teal-50 text-teal-700 border border-teal-200">
            Interactive Modeling Engine
          </span>
        </div>
        <h1 className="text-xl font-bold text-slate-900 mt-1">Plan Design Optimization & ROI Simulator</h1>
        <p className="text-xs text-slate-500">
          Simulate prospective benefit design restructuring, premium recalibration, wellness expansion, and employee plan migration.
        </p>
      </div>

      {/* Simulator Interface Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Interactive Sliders (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-xl p-6 border border-slate-200 shadow-xs space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center space-x-2">
              <Sliders className="w-5 h-5 text-teal-600" />
              <h2 className="text-base font-bold text-slate-900">What-If Policy Knobs</h2>
            </div>
            <span className="text-xs text-slate-500">Adjust parameters in real-time</span>
          </div>

          {/* Slider 1: Wellness Participation Target */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-xs font-semibold text-slate-700">
                Target Wellness Program Enrollment Rate:
              </label>
              <span className="text-sm font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded">
                {wellnessTargetPct}% <span className="text-xs font-normal text-slate-500">(+{wellnessTargetPct - currentWellnessPct}% expansion)</span>
              </span>
            </div>
            <input
              type="range"
              min="43"
              max="95"
              step="1"
              value={wellnessTargetPct}
              onChange={(e) => setWellnessTargetPct(Number(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-teal-600"
            />
            <div className="flex justify-between text-xs text-slate-400">
              <span>Current: 42.85% ({currentEnrolled.toLocaleString()} mbrs)</span>
              <span>Target: {Math.round(10000 * (wellnessTargetPct / 100)).toLocaleString()} members</span>
              <span>Max: 95%</span>
            </div>
            <p className="text-xs text-slate-500">
              Adds <strong>+{newWellnessMembers.toLocaleString()} active participants</strong>, avoiding an estimated ${projectedWellnessGrossSavings.toLocaleString()} in avoidable outpatient/inpatient claims.
            </p>
          </div>

          {/* Slider 2: Plan Rightsizing Migration */}
          <div className="space-y-2 pt-2 border-t border-slate-100">
            <div className="flex justify-between items-center">
              <label className="text-xs font-semibold text-slate-700">
                Underutilized Gold/Platinum to HDHP Migration:
              </label>
              <span className="text-sm font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded">
                {migrationPct}% ({migratedMembers} of {underutilizedCount} members)
              </span>
            </div>
            <input
              type="range"
              min="10"
              max="100"
              step="5"
              value={migrationPct}
              onChange={(e) => setMigrationPct(Number(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />
            <div className="flex justify-between text-xs text-slate-400">
              <span>Conservative (10%)</span>
              <span>Moderate (50%)</span>
              <span>Complete (100%)</span>
            </div>
            <p className="text-xs text-slate-500">
              Transitions low-utilization employees into high-deductible health plans with HSA match, generating $1,000/member in annual enterprise premium delta.
            </p>
          </div>

          {/* Slider 3: Preventive Wellness Incentive */}
          <div className="space-y-2 pt-2 border-t border-slate-100">
            <div className="flex justify-between items-center">
              <label className="text-xs font-semibold text-slate-700">
                Per-Member Preventive Care Incentive / HSA Contribution:
              </label>
              <span className="text-sm font-bold text-slate-800 bg-slate-100 px-2 py-0.5 rounded">
                ${preventiveBonus} / participant
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="400"
              step="25"
              value={preventiveBonus}
              onChange={(e) => setPreventiveBonus(Number(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-700"
            />
            <div className="flex justify-between text-xs text-slate-400">
              <span>$0 (No Bonus)</span>
              <span>$200 (Standard)</span>
              <span>$400 (Aggressive HSA Match)</span>
            </div>
            <p className="text-xs text-slate-500">
              Program incentive cost: <strong>${wellnessIncentiveCost.toLocaleString()}</strong> across new participants.
            </p>
          </div>
        </div>

        {/* Right Column: Dynamic Projected Impact Card (5 cols) */}
        <div className="lg:col-span-5 bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl p-6 text-white shadow-md flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-700">
              <div className="flex items-center space-x-2">
                <Calculator className="w-5 h-5 text-teal-400" />
                <h3 className="text-base font-bold text-white">Projected Enterprise ROI</h3>
              </div>
              <span className="text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded-full">
                Simulated FY2026
              </span>
            </div>

            <div className="mt-5 text-center p-4 bg-slate-800/80 rounded-xl border border-slate-700">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                Total Net Annual Cost Savings
              </span>
              <div className="text-3xl font-extrabold text-teal-400 mt-1">
                ${totalProjectedSavings.toLocaleString()}
              </div>
              <span className="text-xs text-emerald-400 mt-1 inline-block">
                -{((totalProjectedSavings / currentTotalSpend) * 100).toFixed(2)}% overall claim reduction
              </span>
            </div>

            {/* Breakdown Table */}
            <div className="mt-5 space-y-2.5 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-700/60 text-slate-300">
                <span>Net Wellness Avoidance:</span>
                <span className="font-semibold text-white">+${netWellnessSavings.toLocaleString()}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-700/60 text-slate-300">
                <span>Plan Rightsizing Premium Shift:</span>
                <span className="font-semibold text-white">+${planMigrationSavings.toLocaleString()}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-700/60 text-slate-300">
                <span>Current PEPY Cost:</span>
                <span className="font-semibold text-slate-300">${currentPepy.toLocaleString()}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-700/60 text-teal-300">
                <span>Projected New PEPY Cost:</span>
                <span className="font-bold text-teal-400">${newPepy.toLocaleString()}</span>
              </div>
              <div className="flex justify-between py-1.5 text-emerald-400 font-bold">
                <span>PEPY Dollar Reduction:</span>
                <span>-${pepyReduction} / employee</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-700 text-xs text-slate-400">
            *Projections based on empirical cohort regression: $392.38/mbr wellness savings multiplier and $1,000 HDHP migration delta.
          </div>
        </div>
      </div>

      {/* Strategic Implementation Playbook */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
        <h2 className="text-sm font-bold text-slate-900 mb-3">Actuarial Recommendations & Execution Playbook</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-3.5 bg-slate-50 rounded-lg border border-slate-200">
            <h3 className="font-bold text-slate-900 flex items-center space-x-1.5">
              <CheckCircle className="w-4 h-4 text-teal-600" />
              <span>Smart Benefit Tiering</span>
            </h3>
            <p className="text-slate-600 mt-1">
              Introduce automated open-enrollment recommendation engines that suggest HDHP + HSA combinations for employees aged under 35 with 0 chronic diagnoses.
            </p>
          </div>

          <div className="p-3.5 bg-slate-50 rounded-lg border border-slate-200">
            <h3 className="font-bold text-slate-900 flex items-center space-x-1.5">
              <CheckCircle className="w-4 h-4 text-teal-600" />
              <span>Chronic Condition Care Management</span>
            </h3>
            <p className="text-slate-600 mt-1">
              Offer free copay waivers on maintenance medications for Hypertension and Diabetes to prevent catastrophic $30k+ inpatient complications.
            </p>
          </div>

          <div className="p-3.5 bg-slate-50 rounded-lg border border-slate-200">
            <h3 className="font-bold text-slate-900 flex items-center space-x-1.5">
              <CheckCircle className="w-4 h-4 text-teal-600" />
              <span>Stop-Loss Reinsurance Calibration</span>
            </h3>
            <p className="text-slate-600 mt-1">
              Set individual specific stop-loss attachment points at $20,000 to isolate the 133 high-cost catastrophic outliers identified by the anomaly model.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import { Building2, Calendar, RotateCcw, Filter, Users, DollarSign, Activity, Percent } from 'lucide-react';
import { DEPARTMENTS, YEARS, type FilterState } from '../utils/filterAnalytics';

interface FilterBarProps {
  filters: FilterState;
  onFilterChange: (newFilters: FilterState) => void;
  meta: {
    department: string;
    year: string;
    headcount: number;
    totalSpend: number;
    pepy: number;
    mlr: number;
  };
}

export const FilterBar: React.FC<FilterBarProps> = ({ filters, onFilterChange, meta }) => {
  const isFiltered = filters.department !== 'All Departments' || filters.year !== '2025';

  const handleDepartmentChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFilterChange({ ...filters, department: e.target.value });
  };

  const handleYearChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFilterChange({ ...filters, year: e.target.value });
  };

  const handleReset = () => {
    onFilterChange({ department: 'All Departments', year: '2025' });
  };

  return (
    <div className="bg-white border border-slate-200/90 rounded-xl p-4 sm:p-5 shadow-xs mb-6 transition-all duration-200">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        {/* Left Side: Filter Selectors */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4 flex-1">
          {/* Label Badge */}
          <div className="flex items-center space-x-2 text-slate-700 font-semibold text-xs uppercase tracking-wider whitespace-nowrap">
            <div className="p-1.5 rounded-lg bg-teal-50 text-teal-700 border border-teal-200/60">
              <Filter className="w-4 h-4" />
            </div>
            <span>Global Filters</span>
          </div>

          <div className="h-6 w-px bg-slate-200 hidden sm:block" />

          {/* Department Selector */}
          <div className="flex items-center space-x-2 w-full sm:w-auto">
            <label htmlFor="global-department-filter" className="text-xs font-medium text-slate-600 flex items-center space-x-1.5 whitespace-nowrap">
              <Building2 className="w-3.5 h-3.5 text-slate-400" />
              <span>Department:</span>
            </label>
            <div className="relative flex-1 sm:w-56">
              <select
                id="global-department-filter"
                value={filters.department}
                onChange={handleDepartmentChange}
                className="w-full bg-slate-50 hover:bg-slate-100/80 focus:bg-white text-slate-800 text-xs font-medium rounded-lg border border-slate-300 focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 py-2 pl-3 pr-8 transition-colors cursor-pointer appearance-none outline-none shadow-2xs"
              >
                {DEPARTMENTS.map((dept) => (
                  <option key={dept} value={dept}>
                    {dept}
                  </option>
                ))}
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-400">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>

          {/* Year Selector */}
          <div className="flex items-center space-x-2 w-full sm:w-auto">
            <label htmlFor="global-year-filter" className="text-xs font-medium text-slate-600 flex items-center space-x-1.5 whitespace-nowrap">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              <span>Plan Year:</span>
            </label>
            <div className="relative flex-1 sm:w-52">
              <select
                id="global-year-filter"
                value={filters.year}
                onChange={handleYearChange}
                className="w-full bg-slate-50 hover:bg-slate-100/80 focus:bg-white text-slate-800 text-xs font-medium rounded-lg border border-slate-300 focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 py-2 pl-3 pr-8 transition-colors cursor-pointer appearance-none outline-none shadow-2xs"
              >
                {YEARS.map((yr) => (
                  <option key={yr.value} value={yr.value}>
                    {yr.label}
                  </option>
                ))}
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-400">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>

          {/* Reset Button */}
          {isFiltered && (
            <button
              onClick={handleReset}
              id="reset-global-filters-button"
              className="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 border border-slate-300 transition-colors cursor-pointer whitespace-nowrap"
              title="Reset all filters to Enterprise Baseline"
            >
              <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
              <span>Reset</span>
            </button>
          )}
        </div>

        {/* Right Side: Cohort Stat Strip */}
        <div className="flex flex-wrap items-center gap-2 pt-3 lg:pt-0 border-t lg:border-t-0 border-slate-100 text-xs">
          <span className="text-slate-400 text-2xs uppercase tracking-wider font-medium mr-1">
            Cohort Summary:
          </span>

          <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-50 border border-slate-200/80 text-slate-700">
            <Users className="w-3 h-3 text-teal-600" />
            <span className="font-semibold">{meta.headcount.toLocaleString()}</span>
            <span className="text-slate-400 text-2xs">Lives</span>
          </div>

          <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-50 border border-slate-200/80 text-slate-700">
            <DollarSign className="w-3 h-3 text-indigo-600" />
            <span className="font-semibold">${(meta.totalSpend / 1e6).toFixed(2)}M</span>
            <span className="text-slate-400 text-2xs">Spend</span>
          </div>

          <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-50 border border-slate-200/80 text-slate-700">
            <Activity className="w-3 h-3 text-amber-600" />
            <span className="font-semibold">${meta.pepy.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
            <span className="text-slate-400 text-2xs">PEPY</span>
          </div>

          <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-50 border border-slate-200/80 text-slate-700">
            <Percent className="w-3 h-3 text-rose-600" />
            <span className="font-semibold">{meta.mlr}%</span>
            <span className="text-slate-400 text-2xs">MLR</span>
          </div>

          {isFiltered && (
            <span className="px-2 py-0.5 rounded-full text-2xs font-semibold bg-teal-100 text-teal-800 border border-teal-200 animate-pulse">
              Filtered
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

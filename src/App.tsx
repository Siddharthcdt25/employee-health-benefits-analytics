import React, { useState, useMemo } from 'react';
import { Header } from './components/Header';
import { FilterBar } from './components/FilterBar';
import { PageOverview } from './components/PageOverview';
import { PageCostAnalytics } from './components/PageCostAnalytics';
import { PageUtilization } from './components/PageUtilization';
import { PagePlanROI } from './components/PagePlanROI';
import { PageDataQuality } from './components/PageDataQuality';
import { getFilteredAnalytics, type FilterState } from './utils/filterAnalytics';

import {
  enterpriseKPIs,
  trendAnalysis,
  anomalyReport,
  dataQualityReport,
  anomaliesSample,
} from './data/analyticsData';

export default function App() {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [filters, setFilters] = useState<FilterState>({
    department: 'All Departments',
    year: '2025',
  });

  const filteredData = useMemo(() => {
    return getFilteredAnalytics(
      enterpriseKPIs,
      trendAnalysis,
      anomalyReport,
      dataQualityReport,
      anomaliesSample,
      filters
    );
  }, [filters]);

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 flex flex-col font-sans antialiased">
      {/* Top Header & Tab Navigation */}
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Dashboard Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Global Filtering Bar */}
        <FilterBar
          filters={filters}
          onFilterChange={setFilters}
          meta={filteredData.meta}
        />

        {activeTab === 'overview' && (
          <PageOverview
            kpis={filteredData.kpis}
            trends={filteredData.trends}
            selectedDepartment={filters.department}
            selectedYear={filters.year}
            onNavigate={(tab) => setActiveTab(tab)}
          />
        )}

        {activeTab === 'cost' && (
          <PageCostAnalytics
            kpis={filteredData.kpis}
            trends={filteredData.trends}
            selectedDepartment={filters.department}
            selectedYear={filters.year}
          />
        )}

        {activeTab === 'clinical' && (
          <PageUtilization
            kpis={filteredData.kpis}
            trends={filteredData.trends}
            selectedDepartment={filters.department}
            selectedYear={filters.year}
          />
        )}

        {activeTab === 'plans' && (
          <PagePlanROI
            kpis={filteredData.kpis}
            trends={filteredData.trends}
            selectedDepartment={filters.department}
            selectedYear={filters.year}
          />
        )}

        {activeTab === 'audit' && (
          <PageDataQuality
            anomalyReport={filteredData.anomalyReport}
            dataQualityReport={filteredData.dataQualityReport}
            anomaliesSample={filteredData.anomaliesSample}
            selectedDepartment={filters.department}
            selectedYear={filters.year}
          />
        )}
      </main>

      {/* Corporate Compliance & Metadata Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-slate-800">HealthAnalytics Platform</span>
            <span>•</span>
            <span>HIPAA-Compliant Claims Intelligence Pipeline</span>
          </div>
          <div className="flex items-center space-x-4 text-slate-400">
            <span>Data Ingestion: 10,000 Records</span>
            <span>Clean Quality Score: 100.0%</span>
            <span>Updated: FY2025 Audit</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

import type { EnterpriseKPIs, TrendAnalysisData, AnomalyReportData, DataQualityReportData, AnomalyRecord } from '../types';

import kpisJson from '../../reports/generated_reports/enterprise_kpis.json';
import trendJson from '../../reports/generated_reports/trend_analysis.json';
import anomalyReportJson from '../../reports/generated_reports/anomaly_detection_report.json';
import dataQualityJson from '../../reports/generated_reports/data_quality_report.json';
import anomaliesSampleJson from '../../reports/generated_reports/anomalies_sample.json';

export const enterpriseKPIs = kpisJson as unknown as EnterpriseKPIs;
export const trendAnalysis = trendJson as unknown as TrendAnalysisData;
export const anomalyReport = anomalyReportJson as unknown as AnomalyReportData;
export const dataQualityReport = dataQualityJson as unknown as DataQualityReportData;
export const anomaliesSample = anomaliesSampleJson as unknown as AnomalyRecord[];

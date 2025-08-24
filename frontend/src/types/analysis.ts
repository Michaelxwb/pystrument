// AI分析相关类型定义

export interface AnalysisRequest {
  ai_service?: string
  priority?: 'high' | 'normal' | 'low'
}

export interface BatchAnalysisRequest {
  performance_record_ids: string[]
  ai_service?: string
  priority?: 'high' | 'normal' | 'low'
}

export interface BottleneckAnalysis {
  type: string
  severity: 'high' | 'medium' | 'low'
  function: string
  description: string
  impact: number
}

export interface OptimizationSuggestion {
  category: string
  priority: 'high' | 'medium' | 'low'
  title: string
  description: string
  code_example?: string
  expected_improvement?: string
}

export interface RiskAssessment {
  current_risks?: string[]
  potential_issues?: string[]
  recommendations?: string[]
}

export interface AnalysisResults {
  performance_score: number
  bottleneck_analysis: BottleneckAnalysis[]
  optimization_suggestions: OptimizationSuggestion[]
  risk_assessment: RiskAssessment
}

export interface AnalysisRecord {
  id: string
  performance_record_id: string
  project_key: string
  analysis_type: string
  ai_service: string
  results: AnalysisResults
  task_id?: string
  status: 'processing' | 'completed' | 'failed'
  error_message?: string
  created_at: string
  completed_at?: string
}

export interface TaskStatus {
  task_id: string
  status: 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE'
  result?: any
  traceback?: string
  meta?: {
    step?: string
    progress?: number
    [key: string]: any
  }
}

export interface AnalysisHistory {
  records: AnalysisRecord[]
  total: number
  page: number
  size: number
  pages: number
}

export interface AnalysisSummary {
  total_analyses: number
  completed_analyses: number
  failed_analyses: number
  avg_performance_score: number
  top_bottlenecks: Array<{
    type: string
    count: number
  }>
  recent_trends: Array<{
    date: string
    score: number
    count: number
  }>
}

export interface AIService {
  name: string
  provider: string
  description: string
  capabilities: string[]
}

export interface PerformanceReport {
  id: string
  project_key: string
  report_type: string
  date_range: {
    start: string
    end: string
  }
  summary: {
    total_requests: number
    analyzed_requests: number
    avg_response_time: number
    avg_performance_score: number
    top_bottlenecks: Array<[string, number]>
  }
  generated_at: string
}
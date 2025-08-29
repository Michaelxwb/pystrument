// AI分析相关类型定义

export interface AnalysisRequest {
  ai_service?: string
  priority?: 'high' | 'normal' | 'low'
  parameters?: Record<string, any>
}

export interface BatchAnalysisRequest {
  project_key: string
  record_ids: string[]
  ai_service?: string
  priority?: 'high' | 'normal' | 'low'
  parameters?: Record<string, any>
}

export interface BottleneckAnalysis {
  type: string
  severity: 'high' | 'medium' | 'low'
  function: string
  description: string
  impact: number
  recommendations?: string[]
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
  summary: string
  performance_score: number
  bottlenecks: BottleneckAnalysis[] // 前端使用bottlenecks，对应后端的bottleneck_analysis
  recommendations: string[] // 前端使用recommendations，对应后端的optimization_suggestions的title
  
  // 添加直接对应后端的字段，以便兼容处理
  bottleneck_analysis?: BottleneckAnalysis[]
  optimization_suggestions?: OptimizationSuggestion[]
  risk_assessment?: RiskAssessment
  details?: Record<string, any>
}

export interface AnalysisRecord {
  analysis_id: string
  performance_record_id: string
  project_key: string
  ai_service: string
  results?: AnalysisResults
  task_id: string
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'SUCCESS' | 'FAILURE' | 'CANCELED'
  created_at: string
  updated_at: string
  priority: 'high' | 'normal' | 'low'
}

export interface TaskStatus {
  task_id: string
  status: 'PENDING' | 'IN_PROGRESS' | 'SUCCESS' | 'FAILURE' | 'CANCELED'
  progress: number
  analysis_id?: string
  created_at: string
  updated_at: string
  estimated_completion?: string
  error?: string
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
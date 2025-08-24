import { http } from '@/utils/request'
import type { 
  AnalysisRecord, 
  AnalysisRequest,
  BatchAnalysisRequest,
  AnalysisResults,
  TaskStatus 
} from '@/types/analysis'

export const analysisApi = {
  // 触发单个性能记录的AI分析
  triggerAnalysis(performanceRecordId: string, request: AnalysisRequest) {
    return http.post<{
      analysis_id: string
      task_id: string
      status: string
      estimated_completion: string
    }>(`/v1/analysis/analyze/${performanceRecordId}`, request)
  },

  // 触发批量性能分析
  triggerBatchAnalysis(request: BatchAnalysisRequest) {
    return http.post<{
      batch_task_id: string
      total_records: number
      invalid_records: number
      status: string
    }>('/v1/analysis/batch-analyze', request)
  },

  // 获取分析结果
  getAnalysisResult(analysisId: string) {
    return http.get<AnalysisRecord>(`/v1/analysis/result/${analysisId}`)
  },

  // 获取任务状态
  getTaskStatus(taskId: string) {
    return http.get<TaskStatus>(`/v1/analysis/task-status/${taskId}`)
  },

  // 获取项目的分析历史
  getAnalysisHistory(
    projectKey: string,
    params?: {
      page?: number
      size?: number
      status?: string
      analysis_type?: string
      start_date?: string
      end_date?: string
    }
  ) {
    return http.get<{
      records: AnalysisRecord[]
      total: number
      page: number
      size: number
      pages: number
    }>(`/v1/analysis/history/${projectKey}`, params)
  },

  // 获取项目分析汇总
  getAnalysisSummary(projectKey: string, days?: number) {
    return http.get<{
      total_analyses: number
      completed_analyses: number
      failed_analyses: number
      avg_performance_score: number
      top_bottlenecks: Array<{ type: string; count: number }>
      recent_trends: Array<{ date: string; score: number; count: number }>
    }>(`/v1/analysis/summary/${projectKey}`, { days })
  },

  // 生成性能分析报告
  generatePerformanceReport(
    projectKey: string,
    startDate: string,
    endDate: string,
    reportType: string = 'summary'
  ) {
    return http.post<{
      task_id: string
      status: string
      estimated_completion: string
    }>(`/v1/analysis/report/${projectKey}`, null, {
      params: {
        start_date: startDate,
        end_date: endDate,
        report_type: reportType
      }
    })
  },

  // 获取报告生成状态
  getReportStatus(taskId: string) {
    return http.get<{
      status: string
      report_id?: string
      summary?: any
      progress?: number
      error?: string
    }>(`/v1/analysis/report-status/${taskId}`)
  },

  // 清理项目的分析数据
  cleanupAnalysisData(projectKey: string, days: number = 30) {
    return http.delete<{
      deleted_count: number
      cutoff_date: string
    }>(`/v1/analysis/cleanup/${projectKey}`, { params: { days } })
  },

  // 获取可用的AI服务列表
  getAIServices() {
    return http.get<Array<{
      name: string
      provider: string
      description: string
      capabilities: string[]
    }>>('/v1/analysis/config/ai-services')
  }
}
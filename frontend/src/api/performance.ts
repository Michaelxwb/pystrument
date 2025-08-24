import { http } from '@/utils/request'
import type { PerformanceRecord, PerformanceStats, SlowFunction } from '@/types/performance'

export const performanceApi = {
  // 获取性能记录列表
  getRecords(params?: {
    project_key?: string
    page?: number
    size?: number
    start_time?: string
    end_time?: string
    path?: string
    method?: string
    min_duration?: number
    max_duration?: number
    status_code?: number
  }) {
    return http.get<{
      records: PerformanceRecord[]
      total: number
      page: number
      size: number
      pages: number
    }>('/v1/performance/records', params)
  },
  
  // 获取性能记录详情
  getRecordDetail(traceId: string) {
    return http.get<PerformanceRecord>(`/v1/performance/records/${traceId}`)
  },
  
  // 获取性能统计
  getStats(projectKey: string, period: string = '7d', groupBy: string = 'hour') {
    return http.get<PerformanceStats>(`/v1/performance/stats/${projectKey}`, {
      period,
      group_by: groupBy
    })
  },
  
  // 获取慢函数统计
  getSlowFunctions(projectKey: string, limit: number = 10, minDuration: number = 0.1) {
    return http.get<{
      slow_functions: SlowFunction[]
    }>(`/v1/performance/slow-functions/${projectKey}`, {
      limit,
      min_duration: minDuration
    })
  },
  
  // 导出性能记录
  exportRecords(params: {
    project_key: string
    format?: 'csv' | 'excel'
    start_time?: string
    end_time?: string
    [key: string]: any
  }) {
    return http.get('/v1/performance/export', params, {
      responseType: 'blob'
    })
  }
}
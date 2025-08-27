import { http } from '@/utils/request'

export const dashboardApi = {
  // 获取仪表盘统计数据
  getStats() {
    return http.get<{
      total_projects: number
      total_records: number
      today_analysis: number
      avg_response_time: number
      timestamp: string
    }>('/v1/dashboard/stats')
  },
  
  // 获取最近活跃项目
  getRecentProjects(limit: number = 5) {
    return http.get<Array<{
      key: string
      name: string
      status: string
      recordCount: number
    }>>('/v1/dashboard/recent-projects', { limit })
  },
  
  // 获取最近分析结果
  getRecentAnalysis(limit: number = 5) {
    return http.get<Array<{
      projectName: string
      type: string
      status: string
      createdAt: string
    }>>('/v1/dashboard/recent-analysis', { limit })
  },
  
  // 获取系统信息
  getSystemInfo() {
    return http.get<{
      version: string
      uptime: string
      db_status: string
      redis_status: string
    }>('/v1/dashboard/system-info')
  }
}
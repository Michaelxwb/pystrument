// 项目相关类型定义

export interface ProjectConfig {
  sampling_rate: number
  enabled: boolean
  auto_analysis: boolean
  alert_threshold: {
    response_time: number
    error_rate: number
    memory_usage: number
  }
}

export interface Project {
  project_key: string
  name: string
  description?: string
  framework: string
  status: 'active' | 'inactive' | 'archived'
  config: ProjectConfig
  created_at: string
  updated_at: string
  last_activity?: string
}

export interface ProjectCreate {
  name: string
  description?: string
  framework: string
  config?: Partial<ProjectConfig>
}

export interface ProjectUpdate {
  name?: string
  description?: string
  framework?: string
  status?: 'active' | 'inactive' | 'archived'
  config?: Partial<ProjectConfig>
}

export interface ProjectStats {
  total_requests: number
  today_requests: number
  avg_response_time: number
  max_response_time: number
  analysis_count: number
  last_updated: string
}
// 性能监控相关类型定义

export interface RequestInfo {
  method: string
  path: string
  query_params: Record<string, any>
  headers: Record<string, string>
  user_agent?: string
  remote_ip?: string
}

export interface ResponseInfo {
  status_code: number
  response_size: number
  content_type?: string
}

export interface MemoryUsage {
  peak_memory: number
  memory_delta: number
}

export interface DatabaseMetrics {
  query_count: number
  query_time: number
  slow_queries: number
}

export interface CacheMetrics {
  cache_hits: number
  cache_misses: number
  cache_time: number
}

export interface PerformanceMetrics {
  total_duration: number
  cpu_time: number
  memory_usage: MemoryUsage
  database_metrics: DatabaseMetrics
  cache_metrics: CacheMetrics
}

export interface FunctionCall {
  call_id: string
  parent_call_id?: string
  function_name: string
  file_path: string
  line_number: number
  duration: number
  depth: number
  call_order: number
}

export interface VersionInfo {
  app_version?: string
  git_commit?: string
  deploy_time?: string
}

export interface Environment {
  python_version?: string
  framework_version?: string
  server_info?: string
}

export interface PerformanceRecord {
  project_key: string
  trace_id: string
  request_info: RequestInfo
  response_info: ResponseInfo
  performance_metrics: PerformanceMetrics
  function_calls: FunctionCall[]
  version_info?: VersionInfo
  environment?: Environment
  timestamp: string
  created_at: string
}

export interface PerformanceStats {
  time_series: Array<{
    time: string
    requests: number
    avg_duration: number
    max_duration: number
    min_duration: number
    error_rate: number
  }>
  summary: {
    total_requests: number
    total_errors: number
    overall_avg_duration: number
    overall_error_rate: number
    period: string
  }
}

export interface SlowFunction {
  function_name: string
  file_path: string
  total_calls: number
  total_duration: number
  avg_duration: number
  max_duration: number
  performance_impact: number
}
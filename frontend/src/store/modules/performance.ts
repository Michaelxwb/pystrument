import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { performanceApi } from '@/api/performance'
import type { PerformanceRecord, PerformanceStats, SlowFunction } from '@/types/performance'

export const usePerformanceStore = defineStore('performance', () => {
  // 状态
  const records = ref<PerformanceRecord[]>([])
  const currentRecord = ref<PerformanceRecord | null>(null)
  const stats = ref<PerformanceStats | null>(null)
  const slowFunctions = ref<SlowFunction[]>([])
  const loading = ref(false)
  const total = ref(0)
  const pagination = ref({
    page: 1,
    size: 20
  })
  
  const filters = ref({
    projectKey: '',
    startTime: '',
    endTime: '',
    path: '',
    method: '',
    minDuration: undefined as number | undefined,
    maxDuration: undefined as number | undefined,
    statusCode: undefined as number | undefined
  })
  
  // 计算属性
  const errorRecords = computed(() => 
    records.value.filter(r => r.response_info.status_code >= 400)
  )
  
  const slowRecords = computed(() => 
    records.value.filter(r => r.performance_metrics.total_duration > 1.0)
  )
  
  const avgResponseTime = computed(() => {
    if (records.value.length === 0) return 0
    const total = records.value.reduce((sum, r) => sum + r.performance_metrics.total_duration, 0)
    return Number((total / records.value.length).toFixed(3))
  })
  
  const errorRate = computed(() => {
    if (records.value.length === 0) return 0
    const errorCount = errorRecords.value.length
    return Number((errorCount / records.value.length * 100).toFixed(2))
  })
  
  // 方法
  const fetchRecords = async (params?: {
    page?: number
    size?: number
    [key: string]: any
  }) => {
    try {
      loading.value = true
      
      const queryParams = {
        page: params?.page || pagination.value.page,
        size: params?.size || pagination.value.size,
        ...filters.value,
        ...params
      }
      
      // 移除空值
      Object.keys(queryParams).forEach(key => {
        if (queryParams[key as keyof typeof queryParams] === '' || queryParams[key as keyof typeof queryParams] === undefined) {
          delete queryParams[key as keyof typeof queryParams]
        }
      })
      
      const response = await performanceApi.getRecords(queryParams)
      
      if (response.code === 0) {
        records.value = response.data.records
        total.value = response.data.total
        pagination.value.page = response.data.page
        pagination.value.size = response.data.size
      }
      
      return response
    } catch (error) {
      console.error('获取性能记录失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  const fetchRecordDetail = async (traceId: string) => {
    try {
      loading.value = true
      const response = await performanceApi.getRecordDetail(traceId)
      
      if (response.code === 0) {
        currentRecord.value = response.data
      }
      
      return response
    } catch (error) {
      console.error('获取性能记录详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  const fetchStats = async (projectKey: string, period: string = '7d', groupBy: string = 'hour') => {
    try {
      const response = await performanceApi.getStats(projectKey, period, groupBy)
      
      if (response.code === 0) {
        stats.value = response.data
      }
      
      return response
    } catch (error) {
      console.error('获取性能统计失败:', error)
      throw error
    }
  }
  
  const fetchSlowFunctions = async (
    projectKey: string,
    limit: number = 10,
    minDuration: number = 0.1
  ) => {
    try {
      const response = await performanceApi.getSlowFunctions(projectKey, limit, minDuration)
      
      if (response.code === 0) {
        slowFunctions.value = response.data.slow_functions
      }
      
      return response
    } catch (error) {
      console.error('获取慢函数统计失败:', error)
      throw error
    }
  }
  
  const setFilters = (newFilters: Partial<typeof filters.value>) => {
    filters.value = { ...filters.value, ...newFilters }
  }
  
  const clearFilters = () => {
    filters.value = {
      projectKey: '',
      startTime: '',
      endTime: '',
      path: '',
      method: '',
      minDuration: undefined,
      maxDuration: undefined,
      statusCode: undefined
    }
  }
  
  const setCurrentRecord = (record: PerformanceRecord | null) => {
    currentRecord.value = record
  }
  
  const clearRecords = () => {
    records.value = []
    currentRecord.value = null
    stats.value = null
    slowFunctions.value = []
    total.value = 0
    pagination.value = { page: 1, size: 20 }
  }
  
  const refreshData = async () => {
    if (filters.value.projectKey) {
      await Promise.all([
        fetchRecords(),
        fetchStats(filters.value.projectKey),
        fetchSlowFunctions(filters.value.projectKey)
      ])
    }
  }
  
  const exportRecords = async (format: 'csv' | 'excel' = 'csv') => {
    try {
      // 转换过滤器字段名以匹配API要求
      const apiParams: any = {
        project_key: filters.value.projectKey,
        format,
        start_time: filters.value.startTime || undefined,
        end_time: filters.value.endTime || undefined,
        path: filters.value.path || undefined,
        method: filters.value.method || undefined,
        min_duration: filters.value.minDuration,
        max_duration: filters.value.maxDuration,
        status_code: filters.value.statusCode
      }
      
      // 移除空值
      Object.keys(apiParams).forEach(key => {
        if (apiParams[key] === '' || apiParams[key] === undefined) {
          delete apiParams[key]
        }
      })
      
      const response = await performanceApi.exportRecords(apiParams)
      
      // 处理文件下载
      const blob = new Blob([response.data], { 
        type: format === 'csv' ? 'text/csv' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `performance_records_${Date.now()}.${format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      return true
    } catch (error) {
      console.error('导出性能记录失败:', error)
      throw error
    }
  }
  
  // 实时数据更新（WebSocket）
  const connectWebSocket = (projectKey: string) => {
    const wsUrl = `${import.meta.env.VITE_WS_BASE_URL}/performance/${projectKey}`
    const ws = new WebSocket(wsUrl)
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.type === 'new_record') {
          // 添加新记录到列表开头
          records.value.unshift(data.record)
          
          // 限制列表长度，避免内存占用过大
          if (records.value.length > 1000) {
            records.value = records.value.slice(0, 500)
          }
          
          total.value += 1
        } else if (data.type === 'stats_update') {
          // 更新统计数据
          stats.value = data.stats
        }
      } catch (error) {
        console.error('处理WebSocket消息失败:', error)
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket连接错误:', error)
    }
    
    return ws
  }
  
  return {
    // 状态
    records,
    currentRecord,
    stats,
    slowFunctions,
    loading,
    total,
    pagination,
    filters,
    
    // 计算属性
    errorRecords,
    slowRecords,
    avgResponseTime,
    errorRate,
    
    // 方法
    fetchRecords,
    fetchRecordDetail,
    fetchStats,
    fetchSlowFunctions,
    setFilters,
    clearFilters,
    setCurrentRecord,
    clearRecords,
    refreshData,
    exportRecords,
    connectWebSocket
  }
})
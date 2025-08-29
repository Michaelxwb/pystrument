import { http } from '@/utils/request'

// 系统设置类型定义
export interface SystemSettings {
  basic: {
    platformName: string
    adminEmail: string
    timezone: string
    language: string
  }
  monitor: {
    defaultSamplingRate: number
    dataRetentionDays: number
    slowQueryThreshold: number
    autoCleanup: boolean
  }
  ai: {
    defaultService: string
    apiKey: string
    requestTimeout: number
    autoAnalysis: boolean
  }
  notification: {
    emailEnabled: boolean
    smtpServer: string
    smtpPort: number
    senderEmail: string
    webhookEnabled: boolean
    webhookUrl: string
  }
}

// 系统状态类型定义
export interface SystemStatus {
  database: {
    status: 'normal' | 'warning' | 'error'
    message: string
  }
  redis: {
    status: 'normal' | 'warning' | 'error'
    message: string
  }
  aiService: {
    status: 'normal' | 'warning' | 'error'
    message: string
  }
  storage: {
    used: number
    total: number
    unit: string
  }
}

export const settingsApi = {
  // 获取系统设置
  getSettings() {
    return http.get<SystemSettings>('/v1/settings')
  },

  // 更新系统设置
  updateSettings(settings: SystemSettings) {
    return http.post<{ success: boolean }>('/v1/settings', settings)
  },

  // 获取系统状态
  getSystemStatus() {
    return http.get<SystemStatus>('/v1/settings/status')
  },

  // 测试数据库连接
  testDatabaseConnection() {
    return http.post<{ success: boolean; message: string }>('/v1/settings/test/database')
  },

  // 测试Redis连接
  testRedisConnection() {
    return http.post<{ success: boolean; message: string }>('/v1/settings/test/redis')
  },

  // 测试AI服务连接
  testAIServiceConnection() {
    return http.post<{ success: boolean; message: string }>('/v1/settings/test/ai-service')
  },

  // 清理缓存
  clearCache() {
    return http.post<{ success: boolean; message: string }>('/v1/settings/clear-cache')
  },

  // 导出配置
  exportConfig() {
    return http.get('/v1/settings/export', { responseType: 'blob' })
  },

  // 导入配置
  importConfig(configFile: File) {
    const formData = new FormData()
    formData.append('config', configFile)
    return http.post<{ success: boolean; message: string }>('/v1/settings/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}
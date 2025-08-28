<template>
  <div class="settings">
    <div class="page-header">
      <div class="header-left">
        <span class="title">系统设置</span>
        <span class="subtitle">配置和管理平台各项参数</span>
      </div>
      <div class="header-actions">
        <el-tooltip content="刷新数据" placement="top">
          <el-button type="primary" @click="refreshAll">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-tooltip>
      </div>
    </div>

    <el-row :gutter="24">
      <el-col :span="12">
        <!-- 基本设置 -->
        <div class="settings-section">
          <h3 class="section-title">基本设置 <el-tooltip content="平台基础配置信息" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Setting /></el-icon>
                  <span>平台配置</span>
                </div>
              </div>
            </template>
            <el-form :model="basicSettings" label-width="120px">
              <el-form-item label="平台名称:">
                <el-input v-model="basicSettings.platformName" />
              </el-form-item>
              <el-form-item label="管理员邮箱:">
                <el-input v-model="basicSettings.adminEmail" />
              </el-form-item>
              <el-form-item label="时区:">
                <el-select v-model="basicSettings.timezone">
                  <el-option label="北京时间 (GMT+8)" value="Asia/Shanghai" />
                  <el-option label="UTC" value="UTC" />
                  <el-option label="纽约时间 (GMT-5)" value="America/New_York" />
                </el-select>
              </el-form-item>
              <el-form-item label="语言:">
                <el-select v-model="basicSettings.language">
                  <el-option label="中文" value="zh-CN" />
                  <el-option label="English" value="en-US" />
                </el-select>
              </el-form-item>
            </el-form>
          </el-card>
        </div>

        <!-- 性能监控设置 -->
        <div class="settings-section">
          <h3 class="section-title">性能监控设置 <el-tooltip content="性能监控相关配置" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Monitor /></el-icon>
                  <span>监控配置</span>
                </div>
              </div>
            </template>
            <el-form :model="monitorSettings" label-width="120px">
              <el-form-item label="默认采样率:">
                <el-input-number 
                  v-model="monitorSettings.defaultSamplingRate" 
                  :min="0" 
                  :max="1" 
                  :step="0.1"
                  :precision="1"
                />
                <span style="margin-left: 10px; color: #909399; font-size: 12px;">
                  建议设置为0.1-0.5之间
                </span>
              </el-form-item>
              <el-form-item label="数据保留期:">
                <el-input-number 
                  v-model="monitorSettings.dataRetentionDays" 
                  :min="1" 
                  :max="365"
                />
                <span style="margin-left: 10px; color: #909399; font-size: 12px;">天</span>
              </el-form-item>
              <el-form-item label="慢查询阈值:">
                <el-input-number 
                  v-model="monitorSettings.slowQueryThreshold" 
                  :min="100" 
                  :max="10000"
                />
                <span style="margin-left: 10px; color: #909399; font-size: 12px;">毫秒</span>
              </el-form-item>
              <el-form-item label="自动清理:">
                <el-switch v-model="monitorSettings.autoCleanup" />
                <span style="margin-left: 10px; color: #909399; font-size: 12px;">
                  自动清理过期数据
                </span>
              </el-form-item>
            </el-form>
          </el-card>
        </div>
        
        <!-- 系统状态 -->
        <div class="status-section">
          <h3 class="section-title">系统状态 <el-tooltip content="当前系统运行状态" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
          <el-card v-loading="statusLoading" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><DataLine /></el-icon>
                  <span>运行状态</span>
                  <el-tooltip content="每30秒自动刷新" placement="top">
                    <el-tag size="small" type="info" style="margin-left: 5px;">实时</el-tag>
                  </el-tooltip>
                </div>
                <div class="card-actions">
                  <el-button type="text" @click="refreshStatus">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </div>
              </div>
            </template>
            <div class="system-status">
              <div class="status-item">
                <div class="status-label">
                  <el-icon><DataAnalysis /></el-icon>
                  <span>数据库:</span>
                </div>
                <el-tag :type="getStatusType(systemStatus.database?.status)">
                  {{ getStatusText(systemStatus.database?.status) }}
                </el-tag>
              </div>
              <div class="status-item">
                <div class="status-label">
                  <el-icon><Cpu /></el-icon>
                  <span>Redis:</span>
                </div>
                <el-tag :type="getStatusType(systemStatus.redis?.status)">
                  {{ getStatusText(systemStatus.redis?.status) }}
                </el-tag>
              </div>
              <div class="status-item">
                <div class="status-label">
                  <el-icon><MagicStick /></el-icon>
                  <span>AI服务:</span>
                </div>
                <el-tag :type="getStatusType(systemStatus.aiService?.status)">
                  {{ getStatusText(systemStatus.aiService?.status) }}
                </el-tag>
              </div>
              <div class="status-item">
                <div class="status-label">
                  <el-icon><Histogram /></el-icon>
                  <span>存储空间:</span>
                </div>
                <el-progress 
                  :percentage="getStoragePercentage(systemStatus.storage)" 
                  :status="getStorageStatus(systemStatus.storage)"
                  :stroke-width="10"
                  style="width: 120px;"
                ></el-progress>
              </div>
            </div>
          </el-card>
        </div>
      </el-col>

      <el-col :span="12">
        <!-- AI分析设置 -->
        <div class="settings-section">
          <h3 class="section-title">AI分析设置 <el-tooltip content="AI分析服务相关配置" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><MagicStick /></el-icon>
                  <span>AI配置</span>
                </div>
              </div>
            </template>
            <el-form :model="aiSettings" label-width="120px">
              <el-form-item label="默认AI服务:">
                <el-select v-model="aiSettings.defaultService">
                  <el-option label="OpenAI GPT-4" value="openai-gpt4" />
                  <el-option label="OpenAI GPT-3.5" value="openai-gpt3.5" />
                  <el-option label="本地模型" value="local" />
                </el-select>
              </el-form-item>
              <el-form-item label="API密钥:">
                <el-input 
                  v-model="aiSettings.apiKey" 
                  type="password" 
                  placeholder="请输入OpenAI API密钥"
                  show-password
                />
              </el-form-item>
              <el-form-item label="请求超时:">
                <el-input-number 
                  v-model="aiSettings.requestTimeout" 
                  :min="10" 
                  :max="300"
                />
                <span style="margin-left: 10px; color: #909399; font-size: 12px;">秒</span>
              </el-form-item>
              <el-form-item label="自动分析:">
                <el-switch v-model="aiSettings.autoAnalysis" />
                <span style="margin-left: 10px; color: #909399; font-size: 12px;">
                  新记录自动触发AI分析
                </span>
              </el-form-item>
            </el-form>
          </el-card>
        </div>

        <!-- 通知设置 -->
        <div class="settings-section">
          <h3 class="section-title">通知设置 <el-tooltip content="系统通知相关配置" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Message /></el-icon>
                  <span>通知配置</span>
                </div>
              </div>
            </template>
            <el-form :model="notificationSettings" label-width="120px">
              <el-form-item label="邮件通知:">
                <el-switch v-model="notificationSettings.emailEnabled" />
              </el-form-item>
              <el-form-item label="SMTP服务器:" v-if="notificationSettings.emailEnabled">
                <el-input v-model="notificationSettings.smtpServer" />
              </el-form-item>
              <el-form-item label="SMTP端口:" v-if="notificationSettings.emailEnabled">
                <el-input-number v-model="notificationSettings.smtpPort" :min="1" :max="65535" />
              </el-form-item>
              <el-form-item label="发件邮箱:" v-if="notificationSettings.emailEnabled">
                <el-input v-model="notificationSettings.senderEmail" />
              </el-form-item>
              <el-form-item label="Webhook通知:">
                <el-switch v-model="notificationSettings.webhookEnabled" />
              </el-form-item>
              <el-form-item label="Webhook URL:" v-if="notificationSettings.webhookEnabled">
                <el-input v-model="notificationSettings.webhookUrl" />
              </el-form-item>
            </el-form>
          </el-card>
        </div>
        
        <!-- 操作日志 -->
        <div class="logs-section">
          <h3 class="section-title">操作日志 <el-tooltip content="最近的系统操作记录" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
          <el-card v-loading="logsLoading" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Document /></el-icon>
                  <span>最近操作</span>
                  <el-tooltip content="每30秒自动刷新" placement="top">
                    <el-tag size="small" type="info" style="margin-left: 5px;">实时</el-tag>
                  </el-tooltip>
                </div>
                <div class="card-actions">
                  <el-button type="text" @click="refreshLogs">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </div>
              </div>
            </template>
            <div class="operation-logs">
              <div v-if="operationLogs.length === 0" class="no-data">
                <el-empty description="暂无操作日志" :image-size="60" />
              </div>
              <div v-else v-for="log in operationLogs" :key="log.id" class="log-item">
                <div class="log-header">
                  <div class="log-time">{{ formatDateTime(log.timestamp) }}</div>
                  <el-tag size="small" :type="getActionType(log.action)">{{ getActionText(log.action) }}</el-tag>
                </div>
                <div class="log-content">{{ log.details }}</div>
                <div class="log-operator">操作人: {{ log.operator }}</div>
              </div>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>
    
    <!-- 快捷操作和保存按钮 -->
    <el-row :gutter="24" style="margin-top: 24px;">
      <el-col :span="12">
        <!-- 快捷操作 -->
        <div class="actions-section">
          <h3 class="section-title">快捷操作 <el-tooltip content="常用系统维护操作" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Tools /></el-icon>
                  <span>维护操作</span>
                </div>
              </div>
            </template>
            <div class="quick-actions">
              <el-row :gutter="10">
                <el-col :span="12">
                  <el-dropdown @command="handleTestCommand" :disabled="testing">
                    <el-button type="primary" :loading="testing" style="width: 100%">
                      <el-icon><Connection /></el-icon>
                      测试连接
                      <el-icon><ArrowDown /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="all">测试所有连接</el-dropdown-item>
                        <el-dropdown-item command="database">测试数据库连接</el-dropdown-item>
                        <el-dropdown-item command="redis">测试Redis连接</el-dropdown-item>
                        <el-dropdown-item command="ai">测试AI服务连接</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </el-col>
                <el-col :span="12">
                  <el-button type="warning" @click="clearCache" :loading="clearing" style="width: 100%">
                    <el-icon><Delete /></el-icon>
                    清理缓存
                  </el-button>
                </el-col>
              </el-row>
              <el-row :gutter="10" style="margin-top: 10px;">
                <el-col :span="12">
                  <el-button type="success" @click="exportConfig" :loading="exporting" style="width: 100%">
                    <el-icon><Download /></el-icon>
                    导出配置
                  </el-button>
                </el-col>
                <el-col :span="12">
                  <el-button type="info" @click="importConfig" :loading="importing" style="width: 100%">
                    <el-icon><Upload /></el-icon>
                    导入配置
                  </el-button>
                </el-col>
              </el-row>
            </div>
          </el-card>
        </div>
      </el-col>
      
      <el-col :span="12">
        <!-- 保存按钮 -->
        <div class="save-section">
          <h3 class="section-title">设置操作 <el-tooltip content="保存或重置当前设置" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
          <el-card shadow="hover">
            <div style="text-align: center; padding: 20px;">
              <p style="margin-bottom: 20px; color: #606266;">请确保在保存设置前检查所有配置项是否正确</p>
              <el-button type="primary" size="large" @click="saveSettings" :loading="saving" style="margin-right: 20px; min-width: 120px;">
                <el-icon><Check /></el-icon>
                保存设置
              </el-button>
              <el-button size="large" @click="resetSettings" style="min-width: 120px;">
                <el-icon><Refresh /></el-icon>
                重置
              </el-button>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>
    
    <!-- 导入配置对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入配置" width="500px">
      <el-upload
        class="upload-demo"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept=".json"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到这里或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传JSON文件，且不超过500KB
          </div>
        </template>
      </el-upload>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitImport" :loading="importing">
            确认导入
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Check, 
  Refresh, 
  Connection, 
  Delete, 
  Download, 
  Upload, 
  UploadFilled,
  Setting,
  Monitor,
  MagicStick,
  Message,
  DataLine,
  Document,
  Tools,
  QuestionFilled,
  DataAnalysis,
  Cpu,
  Histogram,
  ArrowDown
} from '@element-plus/icons-vue'
import { settingsApi } from '@/api/settings'
import type { SystemSettings, SystemStatus, OperationLog } from '@/api/settings'
import { formatDateTime } from '@/utils/dateUtils'

// 定义组件名称
defineOptions({
  name: 'Settings'
})

// 响应式数据
const basicSettings = ref({
  platformName: '性能分析平台',
  adminEmail: 'admin@example.com',
  timezone: 'Asia/Shanghai',
  language: 'zh-CN'
})

const monitorSettings = ref({
  defaultSamplingRate: 0.3,
  dataRetentionDays: 30,
  slowQueryThreshold: 500,
  autoCleanup: true
})

const aiSettings = ref({
  defaultService: 'openai-gpt3.5',
  apiKey: '',
  requestTimeout: 30,
  autoAnalysis: false
})

const notificationSettings = ref({
  emailEnabled: false,
  smtpServer: '',
  smtpPort: 587,
  senderEmail: '',
  webhookEnabled: false,
  webhookUrl: ''
})

// 系统状态
const systemStatus = ref<SystemStatus>({
  database: { status: 'normal', message: '连接正常' },
  redis: { status: 'normal', message: '连接正常' },
  aiService: { status: 'warning', message: '配置中' },
  storage: { used: 0, total: 0, unit: 'MB' }
})

// 操作日志
const operationLogs = ref<OperationLog[]>([])

// 加载状态
const loading = ref(false)
const saving = ref(false)
const statusLoading = ref(false)
const logsLoading = ref(false)
const testing = ref(false)
const clearing = ref(false)
const exporting = ref(false)
const importing = ref(false)

// 导入对话框
const importDialogVisible = ref(false)
const importFile = ref<File | null>(null)

// 定时器
const statusTimer = ref<number | null>(null)
const logsTimer = ref<number | null>(null)
const autoRefreshInterval = 30000 // 30秒自动刷新

// 初始化
onMounted(async () => {
  await Promise.all([
    loadSettings(),
    loadSystemStatus(),
    loadOperationLogs()
  ])
  
  // 启动自动刷新
  startAutoRefresh()
})

// 在组件卸载时清除定时器
onUnmounted(() => {
  clearAutoRefresh()
})

// 启动自动刷新
const startAutoRefresh = () => {
  // 清除现有定时器
  clearAutoRefresh()
  
  // 设置新的定时器
  statusTimer.value = window.setInterval(() => {
    if (!statusLoading.value) {
      loadSystemStatus()
    }
  }, autoRefreshInterval)
  
  logsTimer.value = window.setInterval(() => {
    if (!logsLoading.value) {
      loadOperationLogs()
    }
  }, autoRefreshInterval)
}

// 清除自动刷新定时器
const clearAutoRefresh = () => {
  if (statusTimer.value) {
    clearInterval(statusTimer.value)
    statusTimer.value = null
  }
  
  if (logsTimer.value) {
    clearInterval(logsTimer.value)
    logsTimer.value = null
  }
}

// 加载设置
const loadSettings = async () => {
  loading.value = true
  try {
    const response = await settingsApi.getSettings()
    const data = response.data
    
    // 更新设置
    basicSettings.value = data.basic
    monitorSettings.value = data.monitor
    aiSettings.value = data.ai
    notificationSettings.value = data.notification
    
    console.log('加载设置成功:', data)
  } catch (error) {
    console.error('加载设置失败:', error)
    ElMessage.error('加载设置失败')
  } finally {
    loading.value = false
  }
}

// 保存设置
const saveSettings = async () => {
  saving.value = true
  try {
    // 准备设置数据
    const settingsData: SystemSettings = {
      basic: basicSettings.value,
      monitor: monitorSettings.value,
      ai: aiSettings.value,
      notification: notificationSettings.value
    }
    
    // 发送请求
    const response = await settingsApi.updateSettings(settingsData)
    
    if (response.data.success) {
      ElMessage.success('设置保存成功')
      // 重新加载操作日志
      await loadOperationLogs()
    } else {
      ElMessage.error('设置保存失败')
    }
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存设置失败')
  } finally {
    saving.value = false
  }
}

// 重置设置
const resetSettings = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置所有设置吗？此操作将恢复到默认配置。',
      '确认重置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 重置为默认值
    basicSettings.value = {
      platformName: '性能分析平台',
      adminEmail: 'admin@example.com',
      timezone: 'Asia/Shanghai',
      language: 'zh-CN'
    }
    
    monitorSettings.value = {
      defaultSamplingRate: 0.3,
      dataRetentionDays: 30,
      slowQueryThreshold: 500,
      autoCleanup: true
    }
    
    aiSettings.value = {
      defaultService: 'openai-gpt3.5',
      apiKey: '',
      requestTimeout: 30,
      autoAnalysis: false
    }
    
    notificationSettings.value = {
      emailEnabled: false,
      smtpServer: '',
      smtpPort: 587,
      senderEmail: '',
      webhookEnabled: false,
      webhookUrl: ''
    }
    
    ElMessage.success('设置已重置为默认值')
  } catch {
    // 用户取消操作
  }
}

// 加载系统状态
const loadSystemStatus = async () => {
  statusLoading.value = true
  try {
    const response = await settingsApi.getSystemStatus()
    systemStatus.value = response.data
  } catch (error) {
    console.error('加载系统状态失败:', error)
    ElMessage.error('加载系统状态失败')
  } finally {
    statusLoading.value = false
  }
}

// 加载操作日志
const loadOperationLogs = async () => {
  logsLoading.value = true
  try {
    const response = await settingsApi.getOperationLogs()
    operationLogs.value = response.data.logs || []
    console.log('加载操作日志成功:', operationLogs.value)
  } catch (error) {
    console.error('加载操作日志失败:', error)
    ElMessage.error('加载操作日志失败')
  } finally {
    logsLoading.value = false
  }
}

// 刷新状态
const refreshStatus = () => {
  loadSystemStatus()
}

// 刷新日志
const refreshLogs = () => {
  loadOperationLogs()
}

// 刷新所有数据
const refreshAll = () => {
  Promise.all([
    loadSettings(),
    loadSystemStatus(),
    loadOperationLogs()
  ]).then(() => {
    ElMessage.success('数据刷新成功')
  })
}

// 处理测试命令
const handleTestCommand = async (command: string) => {
  testing.value = true
  try {
    let successMessage = ''
    let errorMessage = ''
    
    switch (command) {
      case 'all':
        // 测试所有连接
        await testConnection()
        return
      case 'database':
        // 测试数据库连接
        const dbResponse = await settingsApi.testDatabaseConnection()
        successMessage = '数据库连接测试成功'
        errorMessage = '数据库连接测试失败'
        if (dbResponse.data.success) {
          ElMessage.success(dbResponse.data.message || successMessage)
        } else {
          ElMessage.error(dbResponse.data.message || errorMessage)
        }
        break
      case 'redis':
        // 测试Redis连接
        const redisResponse = await settingsApi.testRedisConnection()
        successMessage = 'Redis连接测试成功'
        errorMessage = 'Redis连接测试失败'
        if (redisResponse.data.success) {
          ElMessage.success(redisResponse.data.message || successMessage)
        } else {
          ElMessage.error(redisResponse.data.message || errorMessage)
        }
        break
      case 'ai':
        // 测试AI服务连接
        const aiResponse = await settingsApi.testAIServiceConnection()
        successMessage = 'AI服务连接测试成功'
        errorMessage = 'AI服务连接测试失败'
        if (aiResponse.data.success) {
          ElMessage.success(aiResponse.data.message || successMessage)
        } else {
          ElMessage.error(aiResponse.data.message || errorMessage)
        }
        break
    }
    
    // 更新系统状态
    await loadSystemStatus()
  } catch (error) {
    console.error('测试连接失败:', error)
    ElMessage.error('测试连接失败')
  } finally {
    testing.value = false
  }
}

// 测试连接
const testConnection = async () => {
  testing.value = true
  try {
    // 测试数据库连接
    const dbResponse = await settingsApi.testDatabaseConnection()
    // 测试Redis连接
    const redisResponse = await settingsApi.testRedisConnection()
    // 测试AI服务连接
    const aiResponse = await settingsApi.testAIServiceConnection()
    
    // 检查全部测试是否成功
    if (dbResponse.data.success && redisResponse.data.success && aiResponse.data.success) {
      ElMessage.success('全部连接测试成功')
    } else {
      // 组合错误信息
      const errorMessages = [];
      if (!dbResponse.data.success) errorMessages.push(`数据库: ${dbResponse.data.message || '连接失败'}`)
      if (!redisResponse.data.success) errorMessages.push(`Redis: ${redisResponse.data.message || '连接失败'}`)
      if (!aiResponse.data.success) errorMessages.push(`AI服务: ${aiResponse.data.message || '连接失败'}`)
      
      ElMessage.error(errorMessages.join('\n'))
    }
    
    // 更新系统状态
    await loadSystemStatus()
  } catch (error) {
    console.error('测试连接失败:', error)
    ElMessage.error('测试连接失败')
  } finally {
    testing.value = false
  }
}

// 清理缓存
const clearCache = async () => {
  clearing.value = true
  try {
    const response = await settingsApi.clearCache()
    
    if (response.data.success) {
      ElMessage.success(response.data.message || '缓存清理成功')
      // 更新操作日志
      await loadOperationLogs()
    } else {
      ElMessage.error(response.data.message || '缓存清理失败')
    }
  } catch (error) {
    console.error('清理缓存失败:', error)
    ElMessage.error('清理缓存失败')
  } finally {
    clearing.value = false
  }
}

// 导出配置
const exportConfig = async () => {
  exporting.value = true
  try {
    const response = await settingsApi.exportConfig()
    
    // 创建下载链接
    const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `系统配置_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    ElMessage.success('配置导出成功')
    
    // 更新操作日志
    await loadOperationLogs()
  } catch (error) {
    console.error('导出配置失败:', error)
    ElMessage.error('导出配置失败')
  } finally {
    exporting.value = false
  }
}

// 打开导入配置对话框
const importConfig = () => {
  importDialogVisible.value = true
  importFile.value = null
}

// 处理文件选择
const handleFileChange = (file: any) => {
  importFile.value = file.raw
}

// 提交导入
const submitImport = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择要导入的配置文件')
    return
  }
  
  importing.value = true
  try {
    const response = await settingsApi.importConfig(importFile.value)
    
    if (response.data.success) {
      ElMessage.success(response.data.message || '配置导入成功')
      importDialogVisible.value = false
      
      // 重新加载设置和操作日志
      await Promise.all([
        loadSettings(),
        loadOperationLogs()
      ])
    } else {
      ElMessage.error(response.data.message || '配置导入失败')
    }
  } catch (error) {
    console.error('导入配置失败:', error)
    ElMessage.error('导入配置失败')
  } finally {
    importing.value = false
  }
}

// 获取状态类型
const getStatusType = (status?: string) => {
  if (!status) return 'info'
  
  switch (status) {
    case 'normal':
      return 'success'
    case 'warning':
      return 'warning'
    case 'error':
      return 'danger'
    default:
      return 'info'
  }
}

// 获取状态文本
const getStatusText = (status?: string) => {
  if (!status) return '未知'
  
  switch (status) {
    case 'normal':
      return '正常'
    case 'warning':
      return '警告'
    case 'error':
      return '错误'
    default:
      return status
  }
}

// 获取存储文本
const getStorageText = (storage?: { used: number; total: number; unit: string }) => {
  if (!storage) return '未知'
  
  const usedPercentage = storage.total > 0 ? Math.round(storage.used / storage.total * 100) : 0
  return `${usedPercentage}% (${storage.used}/${storage.total}${storage.unit})`
}

// 获取存储百分比
const getStoragePercentage = (storage?: { used: number; total: number; unit: string }) => {
  if (!storage || storage.total <= 0) return 0
  return Math.round(storage.used / storage.total * 100)
}

// 获取存储状态
const getStorageStatus = (storage?: { used: number; total: number; unit: string }) => {
  if (!storage || storage.total <= 0) return ''
  const percentage = (storage.used / storage.total) * 100
  
  if (percentage >= 90) return 'exception'
  if (percentage >= 70) return 'warning'
  return 'success'
}

// 获取操作类型标签类型
const getActionType = (action?: string) => {
  if (!action) return 'info'
  
  switch (action) {
    case 'update_settings':
      return 'primary'
    case 'clear_cache':
      return 'warning'
    case 'export_config':
      return 'success'
    case 'import_config':
      return 'success'
    case 'test_connection':
      return 'info'
    default:
      return 'info'
  }
}

// 获取操作类型文本
const getActionText = (action?: string) => {
  if (!action) return '未知操作'
  
  switch (action) {
    case 'update_settings':
      return '更新设置'
    case 'clear_cache':
      return '清理缓存'
    case 'export_config':
      return '导出配置'
    case 'import_config':
      return '导入配置'
    case 'test_connection':
      return '连接测试'
    default:
      return action
  }
}

</script>

<style scoped>
.settings {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.title {
  font-size: 20px;
  font-weight: 600;
  margin-right: 10px;
}

.subtitle {
  font-size: 14px;
  color: #909399;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.settings-section, .status-section, .logs-section, .actions-section, .save-section {
  margin-bottom: 24px;
}

.el-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.el-card__body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.section-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  font-weight: 500;
}

.card-title .el-icon {
  margin-right: 8px;
}

.system-status {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-label {
  display: flex;
  align-items: center;
  font-weight: 500;
}

.status-label .el-icon {
  margin-right: 5px;
  font-size: 16px;
}

.operation-logs {
  max-height: 300px;
  height: 220px;
  overflow-y: auto;
  scrollbar-width: thin;
}

.log-item {
  padding: 10px;
  border-bottom: 1px solid #ebeef5;
  background-color: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 8px;
}

.log-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.log-time {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
  font-weight: 500;
}

.log-content {
  font-size: 14px;
  color: #303133;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.log-operator {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  text-align: right;
  font-style: italic;
}

.no-data {
  padding: 20px;
  text-align: center;
}
</style>

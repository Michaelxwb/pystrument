<template>
  <div class="settings">
    <div class="page-header">
      <h1>系统设置</h1>
      <p>配置性能监控平台的各项参数</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <!-- 基本设置 -->
        <el-card>
          <template #header>
            <span>基本设置</span>
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

        <!-- 性能监控设置 -->
        <el-card style="margin-top: 20px;">
          <template #header>
            <span>性能监控设置</span>
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

        <!-- AI分析设置 -->
        <el-card style="margin-top: 20px;">
          <template #header>
            <span>AI分析设置</span>
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

        <!-- 通知设置 -->
        <el-card style="margin-top: 20px;">
          <template #header>
            <span>通知设置</span>
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

        <!-- 保存按钮 -->
        <div style="margin-top: 20px; text-align: center;">
          <el-button type="primary" size="large" @click="saveSettings">
            <el-icon><Check /></el-icon>
            保存设置
          </el-button>
          <el-button size="large" @click="resetSettings">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </div>
      </el-col>

      <el-col :span="8">
        <!-- 系统状态 -->
        <el-card>
          <template #header>
            <span>系统状态</span>
          </template>
          <div class="system-status">
            <div class="status-item">
              <span class="status-label">数据库:</span>
              <el-tag type="success">正常</el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">Redis:</span>
              <el-tag type="success">正常</el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">AI服务:</span>
              <el-tag type="warning">配置中</el-tag>
            </div>
            <div class="status-item">
              <span class="status-label">存储空间:</span>
              <span>75% (12GB/16GB)</span>
            </div>
          </div>
        </el-card>

        <!-- 操作日志 -->
        <el-card style="margin-top: 20px;">
          <template #header>
            <span>最近操作</span>
          </template>
          <div class="operation-logs">
            <div class="log-item">
              <div class="log-time">2024-01-20 15:30</div>
              <div class="log-content">更新了监控设置</div>
            </div>
            <div class="log-item">
              <div class="log-time">2024-01-20 14:15</div>
              <div class="log-content">创建了新项目</div>
            </div>
            <div class="log-item">
              <div class="log-time">2024-01-20 13:45</div>
              <div class="log-content">配置AI服务</div>
            </div>
          </div>
        </el-card>

        <!-- 快捷操作 -->
        <el-card style="margin-top: 20px;">
          <template #header>
            <span>快捷操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="testConnection">
              <el-icon><Connection /></el-icon>
              测试连接
            </el-button>
            <el-button @click="clearCache">
              <el-icon><Delete /></el-icon>
              清理缓存
            </el-button>
            <el-button @click="exportConfig">
              <el-icon><Download /></el-icon>
              导出配置
            </el-button>
            <el-button @click="importConfig">
              <el-icon><Upload /></el-icon>
              导入配置
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

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

const saveSettings = async () => {
  try {
    // 这里后续接入真实API
    console.log('保存设置:', {
      basic: basicSettings.value,
      monitor: monitorSettings.value,
      ai: aiSettings.value,
      notification: notificationSettings.value
    })
    
    ElMessage.success('设置保存成功')
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存设置失败')
  }
}

const resetSettings = () => {
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
  
  ElMessage.info('设置已重置')
}

const testConnection = () => {
  ElMessage.info('连接测试功能正在开发中')
}

const clearCache = () => {
  ElMessage.info('清理缓存功能正在开发中')
}

const exportConfig = () => {
  ElMessage.info('导出配置功能正在开发中')
}

const importConfig = () => {
  ElMessage.info('导入配置功能正在开发中')
}
</script>

<style lang="scss" scoped>
.settings {
  .page-header {
    margin-bottom: 24px;
    
    h1 {
      margin: 0 0 8px 0;
      color: #303133;
      font-size: 24px;
      font-weight: 600;
    }
    
    p {
      margin: 0;
      color: #909399;
      font-size: 14px;
    }
  }
  
  .system-status {
    .status-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
      
      .status-label {
        color: #606266;
        font-size: 14px;
      }
    }
  }
  
  .operation-logs {
    .log-item {
      padding: 8px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
      
      .log-time {
        font-size: 12px;
        color: #909399;
        margin-bottom: 4px;
      }
      
      .log-content {
        font-size: 14px;
        color: #303133;
      }
    }
  }
  
  .quick-actions {
    display: flex;
    flex-direction: column;
    gap: 12px;
    
    .el-button {
      justify-content: flex-start;
    }
  }
}
</style>
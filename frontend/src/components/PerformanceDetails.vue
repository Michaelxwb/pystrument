<template>
  <div class="performance-details">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 基本信息 -->
      <el-tab-pane label="基本信息" name="basic">
        <div class="basic-info">
          <el-descriptions title="请求信息" :column="2" border>
            <el-descriptions-item label="请求路径">
              {{ record.request_info?.path || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="请求方法">
              <el-tag :type="getMethodTagType(record.request_info?.method)" size="small">
                {{ record.request_info?.method || '-' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态码">
              <el-tag :type="getStatusTagType(record.response_info?.status_code)" size="small">
                {{ record.response_info?.status_code || '-' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="用户代理">
              {{ record.request_info?.user_agent || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="客户端IP">
              {{ record.request_info?.remote_ip || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="请求时间">
              {{ formatDateTime(record.timestamp) }}
            </el-descriptions-item>
          </el-descriptions>
          
          <el-descriptions title="响应信息" :column="2" border style="margin-top: 20px;">
            <el-descriptions-item label="响应大小">
              {{ formatBytes(record.response_info?.response_size) }}
            </el-descriptions-item>
            <el-descriptions-item label="内容类型">
              {{ record.response_info?.content_type || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="响应头数量">
              {{ Object.keys(record.response_info?.headers || {}).length }}
            </el-descriptions-item>
            <el-descriptions-item label="处理时间">
              {{ (record.performance_metrics?.total_duration * 1000).toFixed(2) }}ms
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-tab-pane>
      
      <!-- 性能指标 -->
      <el-tab-pane label="性能指标" name="metrics">
        <div class="metrics-info">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card>
                <template #header>
                  <span>时间指标</span>
                </template>
                <div class="metric-item">
                  <div class="metric-label">总耗时</div>
                  <div class="metric-value large">
                    {{ (record.performance_metrics?.total_duration * 1000).toFixed(2) }}ms
                  </div>
                </div>
                <div class="metric-item">
                  <div class="metric-label">CPU时间</div>
                  <div class="metric-value">
                    {{ (record.performance_metrics?.cpu_time * 1000).toFixed(2) }}ms
                  </div>
                </div>
                <div class="metric-item">
                  <div class="metric-label">等待时间</div>
                  <div class="metric-value">
                    {{ ((record.performance_metrics?.total_duration - record.performance_metrics?.cpu_time) * 1000).toFixed(2) }}ms
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="12">
              <el-card>
                <template #header>
                  <span>内存指标</span>
                </template>
                <div class="metric-item">
                  <div class="metric-label">峰值内存</div>
                  <div class="metric-value large">
                    {{ formatBytes(record.performance_metrics?.memory_usage?.peak_memory * 1024 * 1024) }}
                  </div>
                </div>
                <div class="metric-item">
                  <div class="metric-label">起始内存</div>
                  <div class="metric-value">
                    {{ formatBytes(record.performance_metrics?.memory_usage?.start_memory * 1024 * 1024) }}
                  </div>
                </div>
                <div class="metric-item">
                  <div class="metric-label">内存增长</div>
                  <div class="metric-value">
                    {{ formatBytes((record.performance_metrics?.memory_usage?.peak_memory - record.performance_metrics?.memory_usage?.start_memory) * 1024 * 1024) }}
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
          
          <el-card style="margin-top: 20px;">
            <template #header>
              <span>函数调用统计</span>
            </template>
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value">{{ record.function_calls?.length || 0 }}</div>
                  <div class="stat-label">总函数调用</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value">{{ getSlowFunctionsCount() }}</div>
                  <div class="stat-label">慢函数 (>100ms)</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value">{{ getMaxDepth() }}</div>
                  <div class="stat-label">最大调用深度</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value">{{ getUniqueFilesCount() }}</div>
                  <div class="stat-label">涉及文件数</div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </div>
      </el-tab-pane>
      
      <!-- 环境信息 -->
      <el-tab-pane label="环境信息" name="environment">
        <div class="environment-info">
          <el-descriptions title="运行环境" :column="2" border>
            <el-descriptions-item label="Python版本">
              {{ record.environment?.python_version || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="框架版本">
              {{ record.environment?.framework_version || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="操作系统">
              {{ record.environment?.platform || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="主机名">
              {{ record.environment?.hostname || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="进程ID">
              {{ record.environment?.process_id || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="线程ID">
              {{ record.environment?.thread_id || '-' }}
            </el-descriptions-item>
          </el-descriptions>
          
          <el-card style="margin-top: 20px;">
            <template #header>
              <span>请求头信息</span>
            </template>
            <el-table
              :data="getRequestHeaders()"
              style="width: 100%"
              max-height="300"
            >
              <el-table-column prop="key" label="Header名称" width="200" />
              <el-table-column prop="value" label="Header值" />
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>
      
      <!-- 原始数据 -->
      <el-tab-pane label="原始数据" name="raw">
        <div class="raw-data">
          <el-card>
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>原始JSON数据</span>
                <el-button size="small" @click="copyRawData">复制数据</el-button>
              </div>
            </template>
            <el-input
              v-model="rawDataText"
              type="textarea"
              :rows="20"
              readonly
              class="raw-data-textarea"
            />
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineProps, defineEmits } from 'vue'
import { ElMessage } from 'element-plus'
import type { PerformanceRecord } from '@/types/performance'

// Props
const props = defineProps<{
  record: PerformanceRecord
}>()

// Emits
const emits = defineEmits<{
  close: []
}>()

// 响应式数据
const activeTab = ref('basic')

// 计算属性
const rawDataText = computed(() => {
  return JSON.stringify(props.record, null, 2)
})

// 方法
const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const formatBytes = (bytes: number) => {
  if (!bytes || bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getMethodTagType = (method: string) => {
  const typeMap: Record<string, string> = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger'
  }
  return typeMap[method] || 'info'
}

const getStatusTagType = (statusCode: number) => {
  if (statusCode >= 200 && statusCode < 300) return 'success'
  if (statusCode >= 400 && statusCode < 500) return 'warning'
  if (statusCode >= 500) return 'danger'
  return 'info'
}

const getSlowFunctionsCount = () => {
  if (!props.record.function_calls) return 0
  return props.record.function_calls.filter(call => call.duration > 0.1).length
}

const getMaxDepth = () => {
  if (!props.record.function_calls) return 0
  return Math.max(...props.record.function_calls.map(call => call.depth || 0))
}

const getUniqueFilesCount = () => {
  if (!props.record.function_calls) return 0
  const files = new Set(props.record.function_calls.map(call => call.file_path))
  return files.size
}

const getRequestHeaders = () => {
  const headers = props.record.request_info?.headers || {}
  return Object.entries(headers).map(([key, value]) => ({ key, value }))
}

const copyRawData = async () => {
  try {
    await navigator.clipboard.writeText(rawDataText.value)
    ElMessage.success('数据已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}
</script>

<style scoped>
.performance-details {
  min-height: 500px;
}

.basic-info,
.metrics-info,
.environment-info,
.raw-data {
  padding: 20px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.metric-item:last-child {
  border-bottom: none;
}

.metric-label {
  color: #606266;
  font-size: 14px;
}

.metric-value {
  font-weight: bold;
  color: #303133;
  font-size: 16px;
}

.metric-value.large {
  font-size: 20px;
  color: #409eff;
}

.stat-item {
  text-align: center;
  padding: 20px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.raw-data-textarea {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 12px;
}

.raw-data-textarea :deep(.el-textarea__inner) {
  background-color: #f8f9fa;
  color: #495057;
}
</style>
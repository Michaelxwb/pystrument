<template>
  <div class="project-detail">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="$router.go(-1)" type="text" class="back-button">
          <el-icon><ArrowLeft /></el-icon>
          返回项目列表
        </el-button>
        <span class="title">{{ project.name || '项目详情' }}</span>
      </div>
      <div class="header-actions">
        <el-tooltip content="刷新所有数据" placement="top">
          <el-button type="primary" @click="refreshAll">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-tooltip>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card v-loading="loading">
          <template #header>
            <div class="card-header">
              <div class="card-title">
                <el-icon><Document /></el-icon>
                <span>项目信息</span>
              </div>
            </div>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="项目名称">{{ project.name || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="项目键">{{ project.project_key || projectKey }}</el-descriptions-item>
            <el-descriptions-item label="技术框架">{{ project.framework || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="项目URL">
              <span v-if="project.base_url">{{ project.base_url }}</span>
              <span v-else class="text-muted">未设置</span>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="project.status === 'active' ? 'success' : 'info'">
                {{ project.status === 'active' ? '活跃' : '闲置' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDateTime(project.created_at) || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="更新时间">
              {{ formatDateTime(project.updated_at) || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="最后活跃">
              {{ formatDateTime(project.last_activity) || '无' }}
            </el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">
              {{ project.description || '暂无描述' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card style="margin-top: 20px;" v-loading="recordsLoading">
          <template #header>
            <div class="card-header">
              <div class="card-title">
                <el-icon><DataLine /></el-icon>
                <span>最近性能记录</span>
              </div>
              <div class="card-actions">
                <el-button size="small" type="primary" @click="loadRecentRecords">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </div>
          </template>
          <div v-if="recentRecords.length === 0" class="empty-data">
            <el-empty description="暂无性能记录数据" />
          </div>
          <el-table v-else :data="recentRecords" style="width: 100%" stripe border>
            <el-table-column prop="path" label="请求路径" min-width="180" show-overflow-tooltip>
              <template #default="scope">
                <el-tag :type="getMethodTagType(scope.row.method)" size="small" effect="plain">
                  {{ scope.row.method }}
                </el-tag>
                <span style="margin-left: 8px;">{{ scope.row.path }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="耗时" width="100" sortable>
              <template #default="scope">
                <el-tooltip :content="getDurationTooltip(scope.row.duration)" placement="top">
                  <span :class="getDurationClass(scope.row.duration)">
                    {{ scope.row.duration }}ms
                  </span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态码" width="100" sortable>
              <template #default="scope">
                <el-tag 
                  size="small" 
                  :type="getStatusTagType(scope.row.status)"
                  effect="dark"
                >
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="timestamp" label="时间" width="160" sortable>
              <template #default="scope">
                <el-tooltip :content="formatFullDateTime(scope.row.timestamp)" placement="top">
                  <span>{{ formatDateTime(scope.row.timestamp) }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="scope">
                <el-button type="primary" size="small" @click="viewDetail(scope.row)" circle>
                  <el-icon><View /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="view-more" v-if="recentRecords.length > 0">
            <el-button type="text" @click="router.push(`/performance?project_key=${projectKey}`)">
              查看更多 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card v-loading="statsLoading">
          <template #header>
            <div class="card-header">
              <div class="card-title">
                <el-icon><Odometer /></el-icon>
                <span>性能统计</span>
              </div>
              <div class="card-actions">
                <el-button size="small" type="primary" @click="loadProjectStats">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </div>
          </template>
          <div class="stats-container">
            <div class="stat-item">
              <div class="stat-icon total-icon"><el-icon><DataAnalysis /></el-icon></div>
              <div class="stat-value">{{ projectStats.totalRecords }}</div>
              <div class="stat-label">总请求数</div>
            </div>
            <div class="stat-item">
              <div class="stat-icon avg-icon"><el-icon><Timer /></el-icon></div>
              <div class="stat-value">{{ projectStats.avgDuration }}ms</div>
              <div class="stat-label">平均响应时间</div>
            </div>
            <div class="stat-item">
              <div class="stat-icon slow-icon"><el-icon><Warning /></el-icon></div>
              <div class="stat-value">{{ projectStats.slowQueries }}</div>
              <div class="stat-label">慢查询数</div>
            </div>
            <div class="stat-item">
              <div class="stat-icon error-icon"><el-icon><CircleClose /></el-icon></div>
              <div class="stat-value">{{ projectStats.errorRate }}%</div>
              <div class="stat-label">错误率</div>
            </div>
          </div>
          <div class="view-more">
            <el-button type="text" @click="router.push(`/performance?project_key=${projectKey}`)">
              查看详细统计 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </el-card>

        <el-card style="margin-top: 20px;" v-loading="configSaving">
          <template #header>
            <div class="card-header">
              <div class="card-title">
                <el-icon><Setting /></el-icon>
                <span>项目配置</span>
              </div>
            </div>
          </template>
          <div class="config-container">
            <div class="config-item">
              <span class="config-label">监控状态:</span>
              <el-switch v-model="config.enabled" @change="updateConfig" />
            </div>
            <div class="config-item">
              <span class="config-label">采样率:</span>
              <el-input-number 
                v-model="config.samplingRate" 
                :min="0" 
                :max="1" 
                :step="0.1"
                :precision="1"
                size="small"
                @change="updateConfig"
              />
            </div>
            <div class="config-item">
              <span class="config-label">自动分析:</span>
              <el-switch v-model="config.autoAnalysis" @change="updateConfig" />
            </div>
          </div>
          <el-alert
            v-if="!config.enabled"
            type="warning"
            :closable="false"
            title="监控已禁用"
            description="该项目的性能监控功能已禁用，将不会收集新的性能数据。"
            show-icon
            style="margin-top: 16px;"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ArrowLeft, 
  Refresh, 
  Document, 
  DataLine, 
  Odometer, 
  DataAnalysis, 
  Timer, 
  Warning, 
  CircleClose, 
  Setting,
  View,
  ArrowRight
} from '@element-plus/icons-vue'
import { projectApi } from '@/api/project'
import { performanceApi } from '@/api/performance'
import type { Project } from '@/types/project'
import type { PerformanceRecord } from '@/types/performance'
import { formatDateTime, formatFullDateTime } from '@/utils/dateUtils'

// 定义组件名称
defineOptions({
  name: 'ProjectDetail'
})

const route = useRoute()
const router = useRouter()

// Props
const props = defineProps<{
  projectKey: string
}>()

// 响应式数据
const projectKey = ref(props.projectKey || route.params.projectKey as string)
const loading = ref(false)
const statsLoading = ref(false)
const recordsLoading = ref(false)
const configSaving = ref(false)

const project = ref<Partial<Project>>({
  name: '',
  project_key: projectKey.value,
  framework: '',
  base_url: '',
  status: 'active',
  description: '',
  created_at: '',
  updated_at: '',
  last_activity: ''
})

const projectStats = ref({
  totalRecords: 0,
  avgDuration: 0,
  slowQueries: 0,
  errorRate: 0
})

const config = ref({
  enabled: true,
  samplingRate: 0.3,
  autoAnalysis: false
})

const recentRecords = ref<Array<{
  trace_id: string,
  path: string,
  method: string,
  duration: number,
  status: number,
  timestamp: string
}>>([])

onMounted(() => {
  loadProjectData()
  loadProjectStats()
  loadRecentRecords()
})

const loadProjectData = async () => {
  if (!projectKey.value) {
    ElMessage.error('项目键不能为空')
    return
  }
  
  loading.value = true
  try {
    const response = await projectApi.getProjectDetail(projectKey.value)
    const projectData = response.data
    
    // 更新项目数据
    project.value = {
      name: projectData.name || '',
      project_key: projectData.project_key || projectKey.value,
      framework: projectData.framework || '',
      base_url: projectData.base_url || '',
      status: projectData.status || 'active',
      description: projectData.description || '',
      created_at: projectData.created_at || '',
      updated_at: projectData.updated_at || '',
      last_activity: projectData.last_activity || ''
    }
    
    // 更新项目配置
    if (projectData.config) {
      config.value = {
        enabled: projectData.config.enabled ?? true,
        samplingRate: projectData.config.sampling_rate ?? 0.3,
        autoAnalysis: projectData.config.auto_analysis ?? false
      }
    }
    
    console.log('项目数据加载成功:', project.value)
  } catch (error) {
    console.error('加载项目数据失败:', error)
    ElMessage.error('加载项目数据失败')
  } finally {
    loading.value = false
  }
}

// 加载项目统计数据
const loadProjectStats = async () => {
  if (!projectKey.value) return
  
  statsLoading.value = true
  try {
    const response = await projectApi.getProjectStats(projectKey.value)
    const stats = response.data
    
    projectStats.value = {
      totalRecords: stats.total_requests || 0,
      avgDuration: stats.avg_response_time || 0,
      slowQueries: await getSlowQueriesCount(),
      errorRate: stats.total_requests > 0 
        ? ((stats.failed_requests || 0) / stats.total_requests * 100).toFixed(1)
        : 0
    }
    
    console.log('项目统计加载成功:', projectStats.value)
  } catch (error) {
    console.error('加载项目统计失败:', error)
    ElMessage.warning('加载项目统计数据失败')
  } finally {
    statsLoading.value = false
  }
}

// 获取慢查询数量
const getSlowQueriesCount = async (): Promise<number> => {
  try {
    const response = await performanceApi.getSlowFunctions(projectKey.value, 100)
    return response.data.slow_functions?.length || 0
  } catch (error) {
    console.error('获取慢查询数量失败:', error)
    return 0
  }
}

// 加载最近性能记录
const loadRecentRecords = async () => {
  if (!projectKey.value) return
  
  recordsLoading.value = true
  try {
    const response = await performanceApi.getRecords({
      project_key: projectKey.value,
      page: 1,
      size: 10
    })
    
    recentRecords.value = response.data.records.map(record => ({
      trace_id: record.trace_id,
      path: record.request_path || '/',
      method: record.request_method || 'GET',
      duration: Math.round((record.duration || 0) * 1000), // 转为毫秒
      status: record.status_code || 200,
      timestamp: record.timestamp || ''
    }))
    
    console.log('最近性能记录加载成功:', recentRecords.value)
  } catch (error) {
    console.error('加载最近性能记录失败:', error)
    ElMessage.warning('加载最近性能记录失败')
  } finally {
    recordsLoading.value = false
  }
}

// 更新项目配置
const updateConfig = async () => {
  if (!projectKey.value) return
  
  configSaving.value = true
  try {
    const updateData = {
      config: {
        enabled: config.value.enabled,
        sampling_rate: config.value.samplingRate,
        auto_analysis: config.value.autoAnalysis
      }
    }
    
    await projectApi.updateProject(projectKey.value, updateData)
    ElMessage.success('项目配置更新成功')
    console.log('项目配置已更新:', updateData)
  } catch (error) {
    console.error('更新项目配置失败:', error)
    ElMessage.error('更新项目配置失败')
  } finally {
    configSaving.value = false
  }
}

// 刷新所有数据
const refreshAll = () => {
  loadProjectData()
  loadProjectStats()
  loadRecentRecords()
  ElMessage.success('数据刷新成功')
}

const getMethodTagType = (method: string) => {
  const types: Record<string, string> = {
    'GET': 'success',
    'POST': 'primary',
    'PUT': 'warning',
    'DELETE': 'danger'
  }
  return types[method] || 'info'
}

const getStatusTagType = (status: number) => {
  if (status >= 200 && status < 300) return 'success'
  if (status >= 400 && status < 500) return 'warning'
  if (status >= 500) return 'danger'
  return 'info'
}

const getDurationClass = (duration: number) => {
  if (duration > 1000) return 'duration-very-slow'
  if (duration > 500) return 'duration-slow'
  if (duration > 200) return 'duration-normal'
  return 'duration-fast'
}

const getDurationTooltip = (duration: number) => {
  if (duration > 1000) return '响应时间很长，需要优化'
  if (duration > 500) return '响应时间较长，建议检查'
  if (duration > 200) return '响应时间正常'
  return '响应时间很快'
}



const viewDetail = (record: any) => {
  router.push(`/performance/${record.trace_id}`)
}
</script>

<style lang="scss" scoped>
.project-detail {
  padding-top: 15px;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;
      
      .back-button {
        padding: 0;
      }
      
      .title {
        font-size: 24px;
        font-weight: 600;
        color: #303133;
      }
    }
    
    .header-actions {
      display: flex;
      gap: 12px;
    }
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .card-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 500;
      color: #303133;
    }
    
    .card-actions {
      display: flex;
      gap: 8px;
    }
  }
  
  .stats-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    
    .stat-item {
      text-align: center;
      padding: 16px;
      background: #f8f9fa;
      border-radius: 8px;
      transition: all 0.3s;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
      }
      
      .stat-icon {
        width: 36px;
        height: 36px;
        line-height: 36px;
        margin: 0 auto 8px;
        border-radius: 50%;
        font-size: 18px;
        color: #fff;
      }
      
      .total-icon {
        background: linear-gradient(135deg, #409eff, #52a7ff);
      }
      
      .avg-icon {
        background: linear-gradient(135deg, #67c23a, #76c94f);
      }
      
      .slow-icon {
        background: linear-gradient(135deg, #e6a23c, #ebb563);
      }
      
      .error-icon {
        background: linear-gradient(135deg, #f56c6c, #f78989);
      }
      
      .stat-value {
        font-size: 20px;
        font-weight: bold;
        color: #303133;
        margin-bottom: 4px;
      }
      
      .stat-label {
        font-size: 12px;
        color: #909399;
      }
    }
  }
  
  .config-container {
    .config-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
      
      .config-label {
        color: #606266;
        font-size: 14px;
      }
    }
  }
  
  .empty-data {
    text-align: center;
    padding: 40px 0;
  }
  
  .view-more {
    margin-top: 16px;
    text-align: center;
  }
  
  .duration-fast {
    color: #67C23A;
    font-weight: 500;
  }
  
  .duration-normal {
    color: #409EFF;
    font-weight: 500;
  }
  
  .duration-slow {
    color: #E6A23C;
    font-weight: 500;
  }
  
  .duration-very-slow {
    color: #F56C6C;
    font-weight: 500;
  }
  
  .text-muted {
    color: #909399;
    font-style: italic;
  }
}
</style>
<template>
  <div class="project-detail">
    <div class="page-header">
      <el-button @click="$router.go(-1)" type="text">
        <el-icon><ArrowLeft /></el-icon>
        返回项目列表
      </el-button>
      <h1>{{ project.name || '项目名称' }}</h1>
      <p>项目键: {{ projectKey }}</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>项目信息</span>
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

        <el-card style="margin-top: 20px;">
          <template #header>
            <span>最近性能记录</span>
          </template>
          <el-table :data="recentRecords" style="width: 100%">
            <el-table-column prop="path" label="请求路径" />
            <el-table-column prop="method" label="方法" width="80">
              <template #default="scope">
                <el-tag size="small" :type="getMethodTagType(scope.row.method)">
                  {{ scope.row.method }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="耗时" width="100">
              <template #default="scope">
                <span :class="getDurationClass(scope.row.duration)">
                  {{ scope.row.duration }}ms
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态码" width="80" />
            <el-table-column prop="timestamp" label="时间" width="160" />
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button type="text" size="small" @click="viewDetail(scope.row)">
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <span>性能统计</span>
          </template>
          <div class="stats-container">
            <div class="stat-item">
              <div class="stat-value">{{ projectStats.totalRecords }}</div>
              <div class="stat-label">总记录数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ projectStats.avgDuration }}ms</div>
              <div class="stat-label">平均响应时间</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ projectStats.slowQueries }}</div>
              <div class="stat-label">慢查询数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ projectStats.errorRate }}%</div>
              <div class="stat-label">错误率</div>
            </div>
          </div>
        </el-card>

        <el-card style="margin-top: 20px;">
          <template #header>
            <span>项目配置</span>
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
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { projectApi } from '@/api/project'
import type { Project } from '@/types/project'

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
  totalRecords: 1234,
  avgDuration: 156,
  slowQueries: 23,
  errorRate: 2.1
})

const config = ref({
  enabled: true,
  samplingRate: 0.3,
  autoAnalysis: false
})

const recentRecords = ref([
  {
    path: '/api/users',
    method: 'GET',
    duration: 123,
    status: 200,
    timestamp: '2024-01-20 15:30:00'
  },
  {
    path: '/api/orders',
    method: 'POST',
    duration: 456,
    status: 201,
    timestamp: '2024-01-20 15:25:00'
  },
  {
    path: '/api/products',
    method: 'GET',
    duration: 89,
    status: 200,
    timestamp: '2024-01-20 15:20:00'
  }
])

onMounted(() => {
  loadProjectData()
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

const getMethodTagType = (method: string) => {
  const types: Record<string, string> = {
    'GET': 'success',
    'POST': 'primary',
    'PUT': 'warning',
    'DELETE': 'danger'
  }
  return types[method] || 'info'
}

const getDurationClass = (duration: number) => {
  if (duration > 500) return 'text-danger'
  if (duration > 200) return 'text-warning'
  return 'text-success'
}

const formatDateTime = (dateString?: string) => {
  if (!dateString) return ''
  try {
    return new Date(dateString).toLocaleString('zh-CN')
  } catch (error) {
    return dateString
  }
}

const viewDetail = (record: any) => {
  router.push(`/performance/${record.traceId}`)
}

const updateConfig = () => {
  console.log('更新项目配置:', config.value)
  // 这里后续接入真实API
}
</script>

<style lang="scss" scoped>
.project-detail {
  .page-header {
    margin-bottom: 24px;
    
    h1 {
      margin: 8px 0;
      color: #303133;
      font-size: 24px;
    }
    
    p {
      margin: 0;
      color: #909399;
      font-size: 14px;
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
      
      .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #409EFF;
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
  
  .text-success {
    color: #67C23A;
  }
  
  .text-warning {
    color: #E6A23C;
  }
  
  .text-danger {
    color: #F56C6C;
  }
  
  .text-muted {
    color: #909399;
    font-style: italic;
  }
}
</style>
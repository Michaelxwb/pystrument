<template>
  <div class="performance-monitor">
    <div class="page-header">
      <h2>性能监控</h2>
      <div class="header-actions">
        <el-select
          v-model="selectedProject"
          placeholder="选择项目"
          style="width: 200px; margin-right: 12px;"
          @change="onProjectChange"
        >
          <el-option
            v-for="project in projects"
            :key="project.project_key"
            :label="project.name"
            :value="project.project_key"
          />
        </el-select>
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <div v-if="selectedProject" class="monitor-content">
      <!-- 性能概览卡片 -->
      <div class="overview-cards">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="metric-card">
              <div class="metric-item">
                <div class="metric-value">{{ overview.total_requests }}</div>
                <div class="metric-label">今日请求数</div>
                <div class="metric-trend">
                  <span :class="overview.requests_trend > 0 ? 'trend-up' : 'trend-down'">
                    {{ overview.requests_trend > 0 ? '↗' : '↘' }}
                    {{ Math.abs(overview.requests_trend) }}%
                  </span>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="metric-card">
              <div class="metric-item">
                <div class="metric-value">{{ overview.avg_response_time }}ms</div>
                <div class="metric-label">平均响应时间</div>
                <div class="metric-trend">
                  <span :class="overview.response_time_trend < 0 ? 'trend-up' : 'trend-down'">
                    {{ overview.response_time_trend < 0 ? '↗' : '↘' }}
                    {{ Math.abs(overview.response_time_trend) }}%
                  </span>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="metric-card">
              <div class="metric-item">
                <div class="metric-value">{{ overview.error_rate }}%</div>
                <div class="metric-label">错误率</div>
                <div class="metric-trend">
                  <span :class="overview.error_rate_trend < 0 ? 'trend-up' : 'trend-down'">
                    {{ overview.error_rate_trend < 0 ? '↗' : '↘' }}
                    {{ Math.abs(overview.error_rate_trend) }}%
                  </span>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="metric-card">
              <div class="metric-item">
                <div class="metric-value">{{ overview.performance_score }}</div>
                <div class="metric-label">性能评分</div>
                <div class="metric-trend">
                  <span :class="overview.score_trend > 0 ? 'trend-up' : 'trend-down'">
                    {{ overview.score_trend > 0 ? '↗' : '↘' }}
                    {{ Math.abs(overview.score_trend) }}
                  </span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 图表区域 -->
      <div class="charts-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card>
              <template #header>
                <div class="chart-header">
                  <span>响应时间趋势</span>
                  <el-select
                    v-model="timeRange"
                    size="small"
                    style="width: 120px"
                    @change="loadChartData"
                  >
                    <el-option label="1小时" value="1h" />
                    <el-option label="6小时" value="6h" />
                    <el-option label="24小时" value="24h" />
                    <el-option label="7天" value="7d" />
                  </el-select>
                </div>
              </template>
              <div ref="responseTimeChartRef" style="height: 300px;"></div>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card>
              <template #header>
                <span>接口性能分布</span>
              </template>
              <div ref="endpointChartRef" style="height: 300px;"></div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 最新性能数据表格 -->
      <div class="performance-table">
        <el-card>
          <template #header>
            <div class="table-header">
              <span>最新性能数据</span>
              <div class="header-filters">
                <el-input
                  v-model="tableFilters.path"
                  placeholder="筛选接口路径"
                  size="small"
                  style="width: 200px; margin-right: 12px;"
                  @keyup.enter="loadPerformanceData"
                />
                <el-select
                  v-model="tableFilters.status_code"
                  placeholder="状态码"
                  size="small"
                  style="width: 120px; margin-right: 12px;"
                  clearable
                >
                  <el-option label="200" value="200" />
                  <el-option label="400" value="400" />
                  <el-option label="500" value="500" />
                </el-select>
                <el-button size="small" @click="loadPerformanceData">搜索</el-button>
              </div>
            </div>
          </template>
          
          <el-table
            v-loading="tableLoading"
            :data="performanceData"
            stripe
          >
            <el-table-column prop="timestamp" label="时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.timestamp) }}
              </template>
            </el-table-column>
            
            <el-table-column prop="request_info.path" label="接口路径" min-width="200">
              <template #default="{ row }">
                <el-tag :type="getMethodTagType(row.request_info.method)" size="small">
                  {{ row.request_info.method }}
                </el-tag>
                <span style="margin-left: 8px;">{{ row.request_info.path }}</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="response_info.status_code" label="状态码" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusTagType(row.response_info.status_code)" size="small">
                  {{ row.response_info.status_code }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="performance_metrics.total_duration" label="响应时间" width="120">
              <template #default="{ row }">
                <span :class="getDurationClass(row.performance_metrics.total_duration)">
                  {{ (row.performance_metrics.total_duration * 1000).toFixed(2) }}ms
                </span>
              </template>
            </el-table-column>
            
            <el-table-column prop="performance_metrics.memory_usage.peak_memory" label="内存使用" width="120">
              <template #default="{ row }">
                {{ (row.performance_metrics.memory_usage?.peak_memory || 0).toFixed(1) }}MB
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  @click="viewDetails(row)"
                >
                  详情
                </el-button>
                <el-button
                  type="warning"
                  size="small"
                  @click="viewCallTrace(row)"
                >
                  调用链
                </el-button>
                <el-button
                  v-if="!row.ai_analysis"
                  type="success"
                  size="small"
                  @click="triggerAIAnalysis(row)"
                  :loading="row.analyzing"
                >
                  AI分析
                </el-button>
                <el-button
                  v-else
                  type="info"
                  size="small"
                  @click="viewAIAnalysis(row)"
                >
                  查看分析
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="table-pagination">
            <el-pagination
              v-model:current-page="tablePagination.page"
              v-model:page-size="tablePagination.size"
              :page-sizes="[10, 20, 50, 100]"
              :total="tablePagination.total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="loadPerformanceData"
              @current-change="loadPerformanceData"
            />
          </div>
        </el-card>
      </div>
    </div>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="showDetailsDialog"
      title="性能详情"
      width="80%"
      top="5vh"
    >
      <performance-details
        v-if="selectedRecord"
        :record="selectedRecord"
        @close="showDetailsDialog = false"
      />
    </el-dialog>

    <!-- 调用链对话框 -->
    <el-dialog
      v-model="showCallTraceDialog"
      title="函数调用链"
      width="90%"
      top="5vh"
    >
      <call-trace-viewer
        v-if="selectedRecord"
        :record="selectedRecord"
        @close="showCallTraceDialog = false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { projectApi } from '@/api/project'
import { performanceApi } from '@/api/performance'
import { analysisApi } from '@/api/analysis'
import type { Project } from '@/types/project'
import type { PerformanceRecord } from '@/types/performance'
import PerformanceDetails from '@/components/PerformanceDetails.vue'
import CallTraceViewer from '@/components/CallTraceViewer.vue'

const router = useRouter()

// 响应式数据
const projects = ref<Project[]>([])
const selectedProject = ref('')
const tableLoading = ref(false)
const performanceData = ref<PerformanceRecord[]>([])
const selectedRecord = ref<PerformanceRecord | null>(null)
const showDetailsDialog = ref(false)
const showCallTraceDialog = ref(false)
const timeRange = ref('24h')

// 图表引用
const responseTimeChartRef = ref<HTMLElement>()
const endpointChartRef = ref<HTMLElement>()
let responseTimeChart: echarts.ECharts | null = null
let endpointChart: echarts.ECharts | null = null

// 概览数据
const overview = reactive({
  total_requests: 0,
  avg_response_time: 0,
  error_rate: 0,
  performance_score: 85,
  requests_trend: 12.5,
  response_time_trend: -8.3,
  error_rate_trend: -2.1,
  score_trend: 5.2
})

// 表格筛选
const tableFilters = reactive({
  path: '',
  status_code: ''
})

// 表格分页
const tablePagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 方法
const loadProjects = async () => {
  try {
    const response = await projectApi.getProjects({ size: 100 })
    projects.value = response.data.projects
    
    if (projects.value.length > 0 && !selectedProject.value) {
      selectedProject.value = projects.value[0].project_key
      await onProjectChange()
    }
  } catch (error) {
    ElMessage.error('加载项目列表失败')
  }
}

const onProjectChange = async () => {
  if (selectedProject.value) {
    await Promise.all([
      loadOverviewData(),
      loadPerformanceData(),
      loadChartData()
    ])
  }
}

const loadOverviewData = async () => {
  if (!selectedProject.value) return
  
  try {
    const response = await projectApi.getProjectStats(selectedProject.value)
    const stats = response.data
    
    overview.total_requests = stats.today_requests || 0
    overview.avg_response_time = Math.round(stats.avg_response_time || 0)
    overview.error_rate = Number((stats.error_rate || 0).toFixed(1))
    overview.performance_score = Math.round(stats.performance_score || 85)
  } catch (error) {
    console.error('加载概览数据失败:', error)
  }
}

const loadPerformanceData = async () => {
  if (!selectedProject.value) return
  
  tableLoading.value = true
  try {
    const params = {
      project_key: selectedProject.value,
      page: tablePagination.page,
      size: tablePagination.size,
      ...tableFilters
    }
    
    const response = await performanceApi.getPerformanceRecords(params)
    
    performanceData.value = response.data.records.map(record => ({
      ...record,
      analyzing: false
    }))
    tablePagination.total = response.data.total
  } catch (error) {
    ElMessage.error('加载性能数据失败')
  } finally {
    tableLoading.value = false
  }
}

const loadChartData = async () => {
  if (!selectedProject.value) return
  
  try {
    const response = await performanceApi.getPerformanceTrends(
      selectedProject.value,
      timeRange.value
    )
    
    const trendData = response.data
    
    // 更新响应时间趋势图
    updateResponseTimeChart(trendData.response_times)
    
    // 更新接口性能分布图
    updateEndpointChart(trendData.endpoint_stats)
  } catch (error) {
    console.error('加载图表数据失败:', error)
  }
}

const updateResponseTimeChart = (data: any[]) => {
  if (!responseTimeChart) return
  
  const option = {
    title: {
      text: '响应时间趋势',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const time = params[0].axisValue
        const value = params[0].value
        return `${time}<br/>响应时间: ${value}ms`
      }
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.time),
      axisLabel: {
        rotate: 45,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      name: '响应时间(ms)',
      nameTextStyle: { fontSize: 10 }
    },
    series: [{
      type: 'line',
      data: data.map(item => item.avg_duration * 1000),
      smooth: true,
      lineStyle: { color: '#409eff' },
      areaStyle: { color: 'rgba(64, 158, 255, 0.1)' }
    }],
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%',
      top: '15%'
    }
  }
  
  responseTimeChart.setOption(option)
}

const updateEndpointChart = (data: any[]) => {
  if (!endpointChart) return
  
  const option = {
    title: {
      text: '接口性能分布',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}ms ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '60%'],
      data: data.map(item => ({
        name: item.path,
        value: item.avg_duration * 1000
      })),
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
  
  endpointChart.setOption(option)
}

const initCharts = () => {
  nextTick(() => {
    if (responseTimeChartRef.value) {
      responseTimeChart = echarts.init(responseTimeChartRef.value)
      window.addEventListener('resize', () => responseTimeChart?.resize())
    }
    
    if (endpointChartRef.value) {
      endpointChart = echarts.init(endpointChartRef.value)
      window.addEventListener('resize', () => endpointChart?.resize())
    }
  })
}

const refreshData = () => {
  onProjectChange()
}

const viewDetails = (record: PerformanceRecord) => {
  selectedRecord.value = record
  showDetailsDialog.value = true
}

const viewCallTrace = (record: PerformanceRecord) => {
  selectedRecord.value = record
  showCallTraceDialog.value = true
}

const triggerAIAnalysis = async (record: PerformanceRecord) => {
  record.analyzing = true
  try {
    const response = await analysisApi.triggerAnalysis(record.id, {
      ai_service: 'default',
      priority: 'normal'
    })
    
    ElMessage.success('AI分析已启动，请稍候查看结果')
    
    // 轮询检查分析结果
    const checkResult = async () => {
      try {
        const statusResponse = await analysisApi.getTaskStatus(response.data.task_id)
        if (statusResponse.data.status === 'SUCCESS') {
          record.ai_analysis = true
          ElMessage.success('AI分析完成')
        } else if (statusResponse.data.status === 'FAILURE') {
          ElMessage.error('AI分析失败')
        } else {
          setTimeout(checkResult, 3000) // 3秒后再检查
        }
      } catch (error) {
        ElMessage.error('检查分析状态失败')
      }
    }
    
    setTimeout(checkResult, 3000)
  } catch (error) {
    ElMessage.error('触发AI分析失败')
  } finally {
    record.analyzing = false
  }
}

const viewAIAnalysis = (record: PerformanceRecord) => {
  router.push(`/analysis/${record.id}`)
}

// 辅助方法
const formatDateTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleString('zh-CN')
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

const getDurationClass = (duration: number) => {
  const ms = duration * 1000
  if (ms < 100) return 'duration-fast'
  if (ms < 500) return 'duration-normal'
  if (ms < 1000) return 'duration-slow'
  return 'duration-very-slow'
}

// 生命周期
onMounted(async () => {
  await loadProjects()
  initCharts()
})
</script>

<style scoped>
.performance-monitor {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
}

.overview-cards {
  margin-bottom: 20px;
}

.metric-card {
  text-align: center;
}

.metric-item {
  padding: 10px;
}

.metric-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.metric-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.metric-trend {
  font-size: 12px;
}

.trend-up {
  color: #67c23a;
}

.trend-down {
  color: #f56c6c;
}

.charts-section {
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.performance-table {
  background: white;
  border-radius: 8px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-filters {
  display: flex;
  align-items: center;
}

.table-pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.duration-fast {
  color: #67c23a;
  font-weight: bold;
}

.duration-normal {
  color: #409eff;
}

.duration-slow {
  color: #e6a23c;
  font-weight: bold;
}

.duration-very-slow {
  color: #f56c6c;
  font-weight: bold;
}
</style>
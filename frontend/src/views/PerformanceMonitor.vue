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
                <el-tag :type="getMethodTagType(row.request_method || 'GET')" size="small">
                  {{ row.request_method || 'GET' }}
                </el-tag>
                <span style="margin-left: 8px;">{{ row.request_path || '/' }}</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="response_info.status_code" label="状态码" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusTagType(row.status_code || 200)" size="small">
                  {{ row.status_code || 200 }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="performance_metrics.total_duration" label="响应时间" width="120">
              <template #default="{ row }">
                <span :class="getDurationClass(row.duration || 0)">
                  {{ ((row.duration || 0) * 1000).toFixed(2) }}ms
                </span>
              </template>
            </el-table-column>
            
            <el-table-column prop="performance_metrics.memory_usage.peak_memory" label="内存使用" width="120">
              <template #default="{ row }">
                {{ (row.memory_peak || 0).toFixed(1) }}MB
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
      <div v-if="showDetailsDialog" class="detail-loading-container">
        <el-skeleton v-if="detailLoading" :rows="10" animated />
        <performance-details
          v-else-if="detailRecord"
          :record="detailRecord"
          @close="showDetailsDialog = false"
        />
        <div v-else class="no-data">
          <el-empty description="无法加载详情数据" />
        </div>
      </div>
    </el-dialog>

    <!-- 调用链对话框 -->
    <el-dialog
      v-model="showCallTraceDialog"
      title="函数调用链"
      width="90%"
      top="5vh"
    >
      <div v-if="showCallTraceDialog" class="detail-loading-container">
        <el-skeleton v-if="detailLoading" :rows="10" animated />
        <call-trace-viewer
          v-else-if="detailRecord"
          :record="detailRecord"
          @close="showCallTraceDialog = false"
        />
        <div v-else class="no-data">
          <el-empty description="无法加载调用链数据" />
        </div>
      </div>
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

// 定义组件名称
defineOptions({
  name: 'PerformanceMonitor'
})

const router = useRouter()

// 响应式数据
const projects = ref<Project[]>([])
const selectedProject = ref('')
const tableLoading = ref(false)
const performanceData = ref<PerformanceRecord[]>([])
const selectedRecord = ref<PerformanceRecord | null>(null)
const detailRecord = ref<PerformanceRecord | null>(null)
const detailLoading = ref(false)
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
    // 过滤掉空值参数
    const filteredParams = Object.fromEntries(
      Object.entries(tableFilters).filter(([_, value]) => value !== '' && value != null)
    )
    
    const params = {
      project_key: selectedProject.value,
      page: tablePagination.page,
      size: tablePagination.size,
      ...filteredParams
    }
    
    const response = await performanceApi.getPerformanceRecords(params)
    
    // 确保每条记录都有必要的字段
    performanceData.value = response.data.records.map(record => ({
      ...record,
      analyzing: false,
      ai_analysis: false,
      // 设置默认值，避免因缺少属性而出错
      request_method: record.request_method || 'GET',
      request_path: record.request_path || '/',
      status_code: record.status_code || 200,
      duration: record.duration || 0,
      memory_peak: record.memory_peak || 0
    }))
    
    tablePagination.total = response.data.total
  } catch (error) {
    console.error('加载性能数据失败:', error)
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

const viewDetails = async (record: any) => {
  // 保存选中记录，并显示详情对话框
  selectedRecord.value = record
  showDetailsDialog.value = true
  detailLoading.value = true
  
  try {
    // 使用 trace_id 获取完整详情
    const response = await performanceApi.getRecordDetail(record.trace_id)
    detailRecord.value = response.data
  } catch (error) {
    console.error('获取性能记录详情失败:', error)
    ElMessage.error('获取性能记录详情失败')
  } finally {
    detailLoading.value = false
  }
}

const viewCallTrace = async (record: any) => {
  // 保存选中记录，并显示调用链对话框
  selectedRecord.value = record
  showCallTraceDialog.value = true
  detailLoading.value = true
  
  try {
    // 使用 trace_id 获取完整详情
    const response = await performanceApi.getRecordDetail(record.trace_id)
    detailRecord.value = response.data
  } catch (error) {
    console.error('获取性能记录详情失败:', error)
    ElMessage.error('获取性能记录详情失败')
  } finally {
    detailLoading.value = false
  }
}

const triggerAIAnalysis = async (record: any) => {
  record.analyzing = true
  try {
    // 使用 trace_id 作为记录ID
    const response = await analysisApi.triggerAnalysis(record.trace_id, {
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

const viewAIAnalysis = (record: any) => {
  // 使用 trace_id 作为记录ID
  router.push(`/analysis/${record.trace_id}`)
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

.metric-card .el-card__body {
  padding: 20px;
}

.metric-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 10px;
}

.metric-label {
  color: #909399;
  font-size: 14px;
}

.metric-trend {
  margin-top: 10px;
  font-size: 12px;
}

.metric-trend.up {
  color: #f56c6c;
}

.metric-trend.down {
  color: #67c23a;
}

.chart-container {
  margin-bottom: 20px;
}

.table-filter {
  margin-bottom: 20px;
}

.table-filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
}

.table-pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.duration-fast {
  color: #67c23a;
}

.duration-normal {
  color: #409eff;
}

.duration-slow {
  color: #e6a23c;
}

.duration-very-slow {
  color: #f56c6c;
  font-weight: bold;
}

.detail-loading-container {
  min-height: 300px;
  padding: 20px;
}

.no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}
</style>
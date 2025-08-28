<template>
  <div class="performance-monitor">
    <div class="page-header">
      <div class="header-left">
        <span class="title">性能监控仪表盘</span>
        <el-select
          v-model="selectedProject"
          placeholder="选择项目"
          style="width: 200px; margin-left: 16px;"
          @change="onProjectChange"
        >
          <el-option
            v-for="project in projects"
            :key="project.project_key"
            :label="project.name"
            :value="project.project_key"
          />
        </el-select>
      </div>
      <div class="header-actions">
        <el-tooltip content="刷新数据" placement="top">
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-tooltip>
        <el-tooltip content="导出数据" placement="top">
          <el-button @click="exportData">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </el-tooltip>
      </div>
    </div>

    <div v-if="selectedProject" class="monitor-content">
      <!-- 性能概览卡片 -->
      <div class="overview-section">
        <h3 class="section-title">性能概览 <el-tooltip content="显示当前项目的核心性能指标" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
        <div class="overview-cards">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-card class="metric-card" shadow="hover">
                <div class="metric-item">
                  <div class="metric-icon request-icon"><el-icon><DataLine /></el-icon></div>
                  <div class="metric-value">{{ overview.total_requests }}</div>
                  <div class="metric-label">今日请求数</div>
                  <div class="metric-trend">
                    <span :class="[overview.requests_trend > 0 ? 'trend-up' : 'trend-down', 'trend-value']">
                      {{ overview.requests_trend > 0 ? '↑' : '↓' }}
                      {{ Math.abs(overview.requests_trend) }}%
                    </span>
                    <span class="trend-label">与昨日同比</span>
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="6">
              <el-card class="metric-card" shadow="hover">
                <div class="metric-item">
                  <div class="metric-icon time-icon"><el-icon><Timer /></el-icon></div>
                  <div class="metric-value">{{ overview.avg_response_time }}ms</div>
                  <div class="metric-label">平均响应时间</div>
                  <div class="metric-trend">
                    <span :class="[overview.response_time_trend < 0 ? 'trend-up' : 'trend-down', 'trend-value']">
                      {{ overview.response_time_trend < 0 ? '↑' : '↓' }}
                      {{ Math.abs(overview.response_time_trend) }}%
                    </span>
                    <span class="trend-label">与昨日同比</span>
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="6">
              <el-card class="metric-card" shadow="hover">
                <div class="metric-item">
                  <div class="metric-icon error-icon"><el-icon><WarningFilled /></el-icon></div>
                  <div class="metric-value">{{ overview.error_rate }}%</div>
                  <div class="metric-label">错误率</div>
                  <div class="metric-trend">
                    <span :class="[overview.error_rate_trend < 0 ? 'trend-up' : 'trend-down', 'trend-value']">
                      {{ overview.error_rate_trend < 0 ? '↑' : '↓' }}
                      {{ Math.abs(overview.error_rate_trend) }}%
                    </span>
                    <span class="trend-label">与昨日同比</span>
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="6">
              <el-card class="metric-card" shadow="hover">
                <div class="metric-item">
                  <div class="metric-icon score-icon"><el-icon><Star /></el-icon></div>
                  <div class="metric-value">{{ overview.performance_score }}</div>
                  <div class="metric-label">性能评分</div>
                  <div class="metric-trend">
                    <span :class="[overview.score_trend > 0 ? 'trend-up' : 'trend-down', 'trend-value']">
                      {{ overview.score_trend > 0 ? '↑' : '↓' }}
                      {{ Math.abs(overview.score_trend) }}
                    </span>
                    <span class="trend-label">与昨日同比</span>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-section">
        <h3 class="section-title">性能图表 <el-tooltip content="监控数据可视化展示" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card shadow="hover" class="chart-card">
              <template #header>
                <div class="chart-header">
                  <div class="chart-title">
                    <el-icon><Odometer /></el-icon>
                    <span>响应时间趋势</span>
                  </div>
                  <div class="chart-actions">
                    <el-radio-group v-model="timeRange" size="small" @change="loadChartData">
                      <el-radio-button label="1h">1小时</el-radio-button>
                      <el-radio-button label="6h">6小时</el-radio-button>
                      <el-radio-button label="24h">24小时</el-radio-button>
                      <el-radio-button label="7d">7天</el-radio-button>
                    </el-radio-group>
                  </div>
                </div>
              </template>
              <div class="chart-container">
                <div v-if="chartLoading" class="chart-loading">
                  <el-skeleton :rows="5" animated />
                </div>
                <div ref="responseTimeChartRef" style="height: 300px;"></div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card shadow="hover" class="chart-card">
              <template #header>
                <div class="chart-header">
                  <div class="chart-title">
                    <el-icon><PieChart /></el-icon>
                    <span>接口性能分布</span>
                  </div>
                  <div class="chart-actions">
                    <el-tooltip content="点击图表可查看详情" placement="top">
                      <el-icon><InfoFilled /></el-icon>
                    </el-tooltip>
                  </div>
                </div>
              </template>
              <div class="chart-container">
                <div v-if="chartLoading" class="chart-loading">
                  <el-skeleton :rows="5" animated />
                </div>
                <div ref="endpointChartRef" style="height: 300px;"></div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 最新性能数据表格 -->
      <div class="performance-table-section">
        <h3 class="section-title">最新性能数据 <el-tooltip content="展示最新的API请求性能记录" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
        <el-card shadow="hover">
          <div class="table-toolbar">
            <div class="filter-group">
              <el-input
                v-model="tableFilters.path"
                placeholder="输入接口路径搜索"
                prefix-icon="Search"
                clearable
                @keyup.enter="loadPerformanceData"
                style="width: 250px; margin-right: 10px;"
              />
              <el-select
                v-model="tableFilters.status_code"
                placeholder="状态码"
                style="width: auto; min-width: 120px; margin-right: 10px;"
                clearable
              >
                <el-option label="成功 (200)" value="200" />
                <el-option label="客户端错误 (400+)" value="400" />
                <el-option label="服务器错误 (500+)" value="500" />
              </el-select>
              <el-button type="primary" @click="loadPerformanceData">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
              <el-button @click="resetTableFilters">
                <el-icon><RefreshRight /></el-icon>
                重置
              </el-button>
            </div>
          </div>
          
          <el-table
            v-loading="tableLoading"
            :data="performanceData"
            stripe
            border
            highlight-current-row
            style="width: 100%"
            :empty-text="'暂无数据'"
            :header-cell-style="{backgroundColor: '#f5f7fa', color: '#606266'}"
          >
            <el-table-column prop="timestamp" label="时间" width="180" sortable>
              <template #default="{ row }">
                <el-tooltip :content="formatFullDateTime(row.timestamp)" placement="top">
                  <span>{{ formatDateTime(row.timestamp) }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            
            <el-table-column prop="request_info.path" label="接口路径" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <el-tag :type="getMethodTagType(row.request_method || 'GET')" size="small" effect="plain">
                  {{ row.request_method || 'GET' }}
                </el-tag>
                <span style="margin-left: 8px;">{{ row.request_path || '/' }}</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="response_info.status_code" label="状态码" width="100" sortable>
              <template #default="{ row }">
                <el-tag :type="getStatusTagType(row.status_code || 200)" size="small" effect="dark">
                  {{ row.status_code || 200 }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="performance_metrics.total_duration" label="响应时间" width="120" sortable>
              <template #default="{ row }">
                <el-tooltip :content="getDurationTooltip(row.duration || 0)" placement="top">
                  <span :class="getDurationClass(row.duration || 0)">
                    {{ ((row.duration || 0) * 1000).toFixed(2) }}ms
                  </span>
                </el-tooltip>
              </template>
            </el-table-column>
            
            <el-table-column prop="performance_metrics.memory_usage.peak_memory" label="内存使用" width="120" sortable>
              <template #default="{ row }">
                <el-tooltip :content="`内存占用峰值: ${(row.memory_peak || 0).toFixed(2)}MB`" placement="top">
                  <span>{{ (row.memory_peak || 0).toFixed(1) }}MB</span>
                </el-tooltip>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="240" fixed="right">
              <template #default="{ row }">
                <div class="table-actions">
                  <el-tooltip content="查看详细性能信息" placement="top">
                    <el-button
                      type="primary"
                      size="small"
                      @click="viewDetails(row)"
                      icon="View"
                      circle
                    />
                  </el-tooltip>
                  <el-tooltip content="查看函数调用链" placement="top">
                    <el-button
                      type="warning"
                      size="small"
                      @click="viewCallTrace(row)"
                      icon="Connection"
                      circle
                    />
                  </el-tooltip>
                  <el-tooltip :content="row.ai_analysis ? '查看分析结果' : 'AI分析该记录'" placement="top">
                    <el-button
                      :type="row.ai_analysis ? 'info' : 'success'"
                      size="small"
                      :icon="row.ai_analysis ? 'Document' : 'Magic-stick'"
                      :loading="row.analyzing"
                      @click="row.ai_analysis ? viewAIAnalysis(row) : triggerAIAnalysis(row)"
                      circle
                    />
                  </el-tooltip>
                </div>
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
              background
              small
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
        <div v-else-if="detailRecord && detailRecord.function_calls && detailRecord.function_calls.length > 0">
          <call-trace-viewer
            :record="detailRecord"
            @close="showCallTraceDialog = false"
          />
        </div>
        <div v-else class="no-data">
          <el-empty description="该记录没有函数调用数据或数据格式不正确" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { 
  Refresh, 
  Download, 
  QuestionFilled, 
  DataLine, 
  Timer, 
  WarningFilled, 
  Star, 
  Odometer, 
  PieChart, 
  InfoFilled,
  RefreshRight,
  Search,
  View,
  Connection,
  Document,
  MagicStick
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { projectApi } from '@/api/project'
import { performanceApi } from '@/api/performance'
import { analysisApi } from '@/api/analysis'
import { formatDateTime, formatFullDateTime } from '@/utils/dateUtils'
import type { Project } from '@/types/project'
import type { PerformanceRecord } from '@/types/performance'
import PerformanceDetails from '@/components/PerformanceDetails.vue'
import CallTraceViewer from '@/components/CallTraceViewer.vue'
import PageTitle from '@/components/PageTitle.vue'

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

// 图表加载状态
const chartLoading = ref(false)

// 表格分页
const tablePagination = reactive({
  page: 1,
  size: 10,
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
  console.log(`项目切换: ${selectedProject.value}`)
  
  if (!selectedProject.value) {
    console.warn('未选择项目，不加载数据')
    return
  }
  
  try {
    // 检查图表是否初始化
    if (!responseTimeChart || !endpointChart) {
      console.log('图表未初始化，先初始化图表')
      initCharts()
      // 等待图表初始化完成
      await new Promise(resolve => setTimeout(resolve, 100))
    }
    
    // 依次加载数据，保证图表最后渲染
    await loadOverviewData()
    await loadPerformanceData()
    await loadChartData()
    
    console.log('项目数据切换完成')
  } catch (error) {
    console.error('切换项目时加载数据失败:', error)
    ElMessage.error('加载项目数据失败，请重试')
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

const resetTableFilters = () => {
  tableFilters.path = ''
  tableFilters.status_code = ''
  loadPerformanceData()
}

const exportData = () => {
  if (!selectedProject.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  
  ElNotification({
    title: '导出功能',
    message: '数据导出功能正在开发中',
    type: 'info'
  })
}



const getDurationTooltip = (duration: number) => {
  const ms = duration * 1000
  if (ms < 100) return `非常快速: ${ms.toFixed(2)}ms`
  if (ms < 500) return `正常响应: ${ms.toFixed(2)}ms`
  if (ms < 1000) return `偏慢: ${ms.toFixed(2)}ms`
  return `非常慢: ${ms.toFixed(2)}ms`
}

const loadChartData = async () => {
  if (!selectedProject.value) {
    console.log('未选择项目，不加载图表数据')
    return
  }
  
  console.log(`加载图表数据: 项目=${selectedProject.value}, 时间范围=${timeRange.value}`)
  chartLoading.value = true
  
  try {
    // 检查图表实例是否初始化
    if (!responseTimeChart || !endpointChartRef.value) {
      console.warn('响应时间图表未初始化，重新初始化...')
      if (responseTimeChartRef.value) {
        responseTimeChart = echarts.init(responseTimeChartRef.value)
        window.addEventListener('resize', () => responseTimeChart?.resize())
        console.log('响应时间图表已重新初始化')
      }
    }
    
    if (!endpointChart || !endpointChartRef.value) {
      console.warn('接口分布图表未初始化，重新初始化...')
      if (endpointChartRef.value) {
        endpointChart = echarts.init(endpointChartRef.value)
        window.addEventListener('resize', () => endpointChart?.resize())
        console.log('接口分布图表已重新初始化')
      }
    }
    
    // 调用API获取数据
    console.log('发起API请求获取趋势数据...')
    const response = await performanceApi.getPerformanceTrends(
      selectedProject.value,
      timeRange.value
    )
    
    // 检查响应数据
    const trendData = response.data
    console.log('趋势数据返回成功:', {
      response_times_count: trendData.response_times?.length || 0,
      endpoint_stats_count: trendData.endpoint_stats?.length || 0
    })
    
    // 更新响应时间趋势图
    updateResponseTimeChart(trendData.response_times)
    
    // 更新接口性能分布图
    updateEndpointChart(trendData.endpoint_stats)
  } catch (error) {
    console.error('加载图表数据失败:', error)
    // 发生错误时显示空图表
    renderEmptyResponseTimeChart()
    renderEmptyEndpointChart()
  } finally {
    chartLoading.value = false
  }
}

const updateResponseTimeChart = (data: any[]) => {
  console.log(`开始更新响应时间趋势图, 数据长度: ${data?.length || 0}`)
  
  if (!responseTimeChart) {
    console.warn('响应时间图表实例不存在，尝试重新初始化')
    if (responseTimeChartRef.value) {
      responseTimeChart = echarts.init(responseTimeChartRef.value)
      window.addEventListener('resize', () => responseTimeChart?.resize())
    } else {
      console.error('响应时间图表容器不存在，无法初始化')
      return
    }
  }
  
  // 检查数据有效性
  if (!data || !Array.isArray(data) || data.length === 0) {
    console.warn('响应时间趋势图数据为空，显示空图表')
    renderEmptyResponseTimeChart()
    return
  }
  
  try {
    // 验证数据完整性
    const validData = data.filter(item => item && item.time && typeof item.avg_duration === 'number')
    if (validData.length === 0) {
      console.warn('所有响应时间趋势数据无效，显示空图表')
      renderEmptyResponseTimeChart()
      return
    }
    
    console.log(`有效数据: ${validData.length}/${data.length} 条`)
    
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
        data: validData.map(item => item.time),
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
        data: validData.map(item => (item.avg_duration || 0) * 1000),
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
    
    console.log('设置响应时间趋势图选项')
    responseTimeChart.setOption(option, true)
    console.log('响应时间趋势图更新完成')
  } catch (error) {
    console.error('更新响应时间趋势图失败:', error)
    renderEmptyResponseTimeChart()
  }
}

const updateEndpointChart = (data: any[]) => {
  console.log(`开始更新接口性能分布图, 数据长度: ${data?.length || 0}`)
  
  if (!endpointChart) {
    console.warn('接口性能分布图实例不存在，尝试重新初始化')
    if (endpointChartRef.value) {
      endpointChart = echarts.init(endpointChartRef.value)
      window.addEventListener('resize', () => endpointChart?.resize())
    } else {
      console.error('接口性能分布图容器不存在，无法初始化')
      return
    }
  }
  
  // 检查数据有效性
  if (!data || !Array.isArray(data) || data.length === 0) {
    console.warn('接口性能分布图数据为空，显示空图表')
    renderEmptyEndpointChart()
    return
  }
  
  try {
    // 验证数据完整性
    const validData = data.filter(item => item && item.path && typeof item.avg_duration === 'number')
    if (validData.length === 0) {
      console.warn('所有接口性能分布数据无效，显示空图表')
      renderEmptyEndpointChart()
      return
    }
    
    console.log(`有效数据: ${validData.length}/${data.length} 条`)
    
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
        data: validData.map(item => ({
          name: item.path || 'unknown',
          value: (item.avg_duration || 0) * 1000
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
    
    console.log('设置接口性能分布图选项')
    endpointChart.setOption(option, true)
    console.log('接口性能分布图更新完成')
  } catch (error) {
    console.error('更新接口性能分布图失败:', error)
    renderEmptyEndpointChart()
  }
}

const initCharts = () => {
  // 使用nextTick确保图表容器已经渲染
  nextTick(() => {
    // 打印日志，帮助调试
    console.log('开始初始化图表...')
    console.log('响应时间图表容器状态:', responseTimeChartRef.value ? '已存在' : '不存在')
    console.log('接口分布图表容器状态:', endpointChartRef.value ? '已存在' : '不存在')
    
    if (responseTimeChartRef.value) {
      // 销毁存在的实例如果存在
      if (responseTimeChart) {
        responseTimeChart.dispose()
      }
      responseTimeChart = echarts.init(responseTimeChartRef.value)
      window.addEventListener('resize', () => responseTimeChart?.resize())
      // 初始化时显示空图表
      renderEmptyResponseTimeChart()
      console.log('响应时间图表初始化完成')
    }
    
    if (endpointChartRef.value) {
      // 销毁存在的实例如果存在
      if (endpointChart) {
        endpointChart.dispose()
      }
      endpointChart = echarts.init(endpointChartRef.value)
      window.addEventListener('resize', () => endpointChart?.resize())
      // 初始化时显示空图表
      renderEmptyEndpointChart()
      console.log('接口分布图表初始化完成')
    }
  })
}

const refreshData = async () => {
  console.log('开始刷新数据...')
  try {
    // 检查是否选择了项目
    if (!selectedProject.value && projects.value.length > 0) {
      console.log('未选择项目，自动选择第一个项目')
      selectedProject.value = projects.value[0].project_key
    }
    
    if (!selectedProject.value) {
      console.warn('无可用项目，无法加载数据')
      return
    }
    
    // 确保图表实例已初始化
    if (!responseTimeChart || !endpointChart) {
      console.log('图表未初始化，重新初始化...')
      initCharts()
      // 等待图表初始化完成
      await new Promise(resolve => setTimeout(resolve, 100))
    }
    
    // 并行加载数据
    await Promise.all([
      loadOverviewData(),
      loadPerformanceData(),
      loadChartData()
    ])
    
    console.log('数据刷新完成')
  } catch (error) {
    console.error('刷新数据失败:', error)
    ElMessage.error('刷新数据失败，请重试')
  }
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
  console.log('查看调用链:', record)
  selectedRecord.value = record
  showCallTraceDialog.value = true
  detailLoading.value = true
  
  try {
    // 使用 trace_id 获取完整详情
    console.log('获取调用链详情, trace_id:', record.trace_id)
    const response = await performanceApi.getRecordDetail(record.trace_id)
    
    console.log('获取到的性能记录详情:', response.data)
    
    // 检查function_calls数据
    if (!response.data.function_calls || !Array.isArray(response.data.function_calls) || response.data.function_calls.length === 0) {
      console.warn('该记录没有函数调用数据:', response.data)
      ElMessage.warning('该记录没有函数调用数据')
    } else {
      console.log('函数调用数据:', response.data.function_calls.length, '条')
    }
    
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
        } else if (statusResponse.data.status === 'IN_PROGRESS') {
          // 如果还在处理中，继续轮询
          setTimeout(checkResult, 3000) // 3秒后再检查
        } else {
          // 其他状态也继续轮询
          setTimeout(checkResult, 3000)
        }
      } catch (error) {
        console.error('检查分析状态失败:', error)
        ElMessage.error('检查分析状态失败')
      }
    }
    
    setTimeout(checkResult, 3000)
  } catch (error) {
    console.error('触发AI分析失败:', error)
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

// 添加空图表渲染方法
const renderEmptyResponseTimeChart = () => {
  console.log('渲染空的响应时间趋势图')
  
  if (!responseTimeChart) {
    console.warn('响应时间图表实例不存在，尝试初始化')
    if (responseTimeChartRef.value) {
      try {
        responseTimeChart = echarts.init(responseTimeChartRef.value)
        window.addEventListener('resize', () => responseTimeChart?.resize())
      } catch (error) {
        console.error('初始化响应时间图表失败:', error)
        return
      }
    } else {
      console.error('响应时间图表容器不存在')
      return
    }
  }
  
  try {
    const option = {
      title: {
        text: '暂无响应时间趋势数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#909399',
          fontSize: 14,
          fontWeight: 'normal'
        }
      },
      xAxis: {
        type: 'category',
        data: []
      },
      yAxis: {
        type: 'value',
        name: '响应时间(ms)'
      },
      series: []
    }
    
    responseTimeChart.setOption(option, true)
    console.log('空响应时间趋势图渲染完成')
  } catch (error) {
    console.error('渲染空响应时间趋势图失败:', error)
  }
}

const renderEmptyEndpointChart = () => {
  console.log('渲染空的接口性能分布图')
  
  if (!endpointChart) {
    console.warn('接口性能分布图实例不存在，尝试初始化')
    if (endpointChartRef.value) {
      try {
        endpointChart = echarts.init(endpointChartRef.value)
        window.addEventListener('resize', () => endpointChart?.resize())
      } catch (error) {
        console.error('初始化接口性能分布图失败:', error)
        return
      }
    } else {
      console.error('接口性能分布图容器不存在')
      return
    }
  }
  
  try {
    const option = {
      title: {
        text: '暂无接口性能分布数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#909399',
          fontSize: 14,
          fontWeight: 'normal'
        }
      },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '60%'],
        data: []
      }]
    }
    
    endpointChart.setOption(option, true)
    console.log('空接口性能分布图渲染完成')
  } catch (error) {
    console.error('渲染空接口性能分布图失败:', error)
  }
}

// 生命周期
onMounted(async () => {
  // 先初始化图表
  initCharts()

  // 添加小延迟，确保图表DOM完全渲染
  await new Promise(resolve => setTimeout(resolve, 100))
  
  // 然后加载数据
  await loadProjects()
  
  // 直接触发刷新操作确保数据加载
  refreshData()
})
</script>

<style scoped>
.performance-monitor {
  padding: 20px 20px 20px 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background-color: #f8f8f8;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  align-items: center;
}

.header-left .title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title .el-icon {
  font-size: 14px;
  color: #909399;
  cursor: help;
}

.overview-section {
  margin-bottom: 24px;
}

.overview-cards {
  margin-bottom: 20px;
}

.metric-card {
  text-align: center;
  transition: all 0.3s;
}

.metric-card:hover {
  transform: translateY(-5px);
}

.metric-card .el-card__body {
  padding: 20px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.metric-icon {
  font-size: 24px;
  margin-bottom: 10px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.request-icon {
  background-color: #409eff;
}

.time-icon {
  background-color: #67c23a;
}

.error-icon {
  background-color: #f56c6c;
}

.score-icon {
  background-color: #e6a23c;
}

.metric-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #303133;
}

.metric-label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 10px;
}

.metric-trend {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 5px;
}

.trend-value {
  font-weight: bold;
  font-size: 14px;
}

.trend-label {
  font-size: 12px;
  color: #909399;
}

.trend-up {
  color: #67c23a;
}

.trend-down {
  color: #f56c6c;
}

.charts-section {
  margin-bottom: 24px;
}

.chart-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.chart-card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.chart-container {
  position: relative;
}

.chart-loading {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.performance-table-section {
  margin-bottom: 20px;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.filter-group {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.table-actions {
  display: flex;
  gap: 8px;
}

.table-pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.duration-fast {
  color: #67c23a;
  font-weight: 500;
}

.duration-normal {
  color: #409eff;
  font-weight: 500;
}

.duration-slow {
  color: #e6a23c;
  font-weight: 500;
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
  flex-direction: column;
  gap: 20px;
  color: #909399;
}

.no-data .el-icon {
  font-size: 48px;
  color: #dcdfe6;
}
</style>
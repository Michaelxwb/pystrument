<template>
  <div class="dashboard">
    <div class="page-header">
      <div class="header-left">
        <span class="title">系统仪表盘</span>
        <span class="subtitle">监控性能分析平台的核心指标</span>
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

    <!-- 平台概览卡片 -->
    <div class="overview-section">
      <h3 class="section-title">平台概览 <el-tooltip content="平台核心指标总览" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
      <div class="overview-cards">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="metric-card" shadow="hover">
              <div class="metric-item">
                <div class="metric-icon projects-icon"><el-icon><Collection /></el-icon></div>
                <div class="metric-value">{{ stats.totalProjects }}</div>
                <div class="metric-label">项目总数</div>
                <div class="metric-desc">平台上的项目总数量</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="metric-card" shadow="hover">
              <div class="metric-item">
                <div class="metric-icon records-icon"><el-icon><Monitor /></el-icon></div>
                <div class="metric-value">{{ stats.totalRecords }}</div>
                <div class="metric-label">性能记录</div>
                <div class="metric-desc">总统计性能记录数量</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="metric-card" shadow="hover">
              <div class="metric-item">
                <div class="metric-icon analysis-icon"><el-icon><DataAnalysis /></el-icon></div>
                <div class="metric-value">{{ stats.todayAnalysis }}</div>
                <div class="metric-label">今日分析</div>
                <div class="metric-desc">今日完成的分析数量</div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="metric-card" shadow="hover">
              <div class="metric-item">
                <div class="metric-icon time-icon"><el-icon><Timer /></el-icon></div>
                <div class="metric-value">{{ stats.avgResponseTime }}ms</div>
                <div class="metric-label">平均响应时间</div>
                <div class="metric-desc">所有接口的平均响应时间</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- 性能与项目状态 -->
    <div class="performance-section">
      <h3 class="section-title">性能与项目状态 <el-tooltip content="展示性能趋势与项目状态" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
      <el-row :gutter="20">
        <!-- 性能趋势图 -->
        <el-col :span="16">
          <el-card shadow="hover" class="chart-card">
            <template #header>
              <div class="chart-header">
                <div class="chart-title">
                  <el-icon><TrendCharts /></el-icon>
                  <span>性能趋势</span>
                </div>
                <div class="chart-actions">
                  <el-radio-group v-model="timeRange" @change="loadPerformanceTrends" size="small">
                    <el-radio-button label="24h">今天</el-radio-button>
                    <el-radio-button label="7d">7天</el-radio-button>
                    <el-radio-button label="30d">30天</el-radio-button>
                  </el-radio-group>
                </div>
              </div>
            </template>
            <div class="chart-container">
              <div v-if="chartLoading" class="chart-loading">
                <el-skeleton :rows="5" animated />
              </div>
              <div ref="performanceChart" style="height: 300px;"></div>
            </div>
          </el-card>
        </el-col>

        <!-- 项目状态 -->
        <el-col :span="8">
          <el-card shadow="hover" class="status-card">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><List /></el-icon>
                  <span>项目状态</span>
                </div>
                <div class="card-actions">
                  <el-tooltip content="刷新项目列表" placement="top">
                    <el-button size="small" @click="refreshProjects" circle>
                      <el-icon><Refresh /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
              </div>
            </template>
            <div class="project-list">
              <template v-if="recentProjects.length > 0">
                <div v-for="project in recentProjects" :key="project.key" class="project-item">
                  <div class="project-info">
                    <div class="project-name">{{ project.name }}</div>
                    <div class="project-status">
                      <el-tag :type="project.status === 'active' ? 'success' : 'info'" size="small" effect="dark">
                        {{ project.status === 'active' ? '活跃' : '闲置' }}
                      </el-tag>
                    </div>
                  </div>
                  <div class="project-metrics">
                    <el-badge :value="project.recordCount" type="primary">
                      <span>记录数</span>
                    </el-badge>
                  </div>
                </div>
              </template>
              <div v-else class="empty-placeholder">
                <el-empty description="暂无项目数据" :image-size="80"></el-empty>
                <el-button type="primary" size="small" style="margin-top: 10px;" @click="goToProjects">
                  创建项目
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 分析结果与系统信息 -->
    <div class="analysis-section">
      <h3 class="section-title">分析结果与系统信息 <el-tooltip content="展示最新分析结果和系统状态" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
      <el-row :gutter="20">
        <!-- 最近分析结果 -->
        <el-col :span="12">
          <el-card shadow="hover" class="data-card">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><DataAnalysis /></el-icon>
                  <span>最近分析结果</span>
                </div>
                <div class="card-actions">
                  <el-tooltip content="刷新分析结果" placement="top">
                    <el-button size="small" @click="refreshAnalysis" circle>
                      <el-icon><Refresh /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
              </div>
            </template>
            <el-table 
              :data="recentAnalysis" 
              style="width: 100%" 
              :empty-text="'暂无分析数据'" 
              :header-cell-style="{backgroundColor: '#f5f7fa', color: '#606266'}"
              border
              stripe
              highlight-current-row
            >
              <el-table-column prop="projectName" label="项目" width="120">
                <template #default="scope">
                  <el-tooltip :content="scope.row.projectName" placement="top">
                    <span>{{ scope.row.projectName }}</span>
                  </el-tooltip>
                </template>
              </el-table-column>
              <el-table-column prop="type" label="类型" width="100">
                <template #default="scope">
                  <el-tag size="small" effect="plain">{{ scope.row.type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="scope">
                  <el-tag 
                    :type="scope.row.status === 'completed' ? 'success' : 'warning'" 
                    size="small"
                    effect="dark"
                  >
                    {{ scope.row.status === 'completed' ? '完成' : '进行中' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="createdAt" label="时间" width="160">
                <template #default="scope">
                  <el-tooltip :content="formatFullDateTime(scope.row.createdAt)" placement="top">
                    <span>{{ formatDateTime(scope.row.createdAt) }}</span>
                  </el-tooltip>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>

        <!-- 系统信息 -->
        <el-col :span="12">
          <el-card shadow="hover" class="data-card">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Monitor /></el-icon>
                  <span>系统信息</span>
                </div>
                <div class="card-actions">
                  <el-tooltip content="刷新系统信息" placement="top">
                    <el-button size="small" @click="refreshSystemInfo" circle>
                      <el-icon><Refresh /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
              </div>
            </template>
            <div class="system-info">
              <div class="info-item">
                <span class="info-label">平台版本:</span>
                <span class="info-value">{{ systemInfo.version }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">运行时间:</span>
                <span class="info-value">{{ systemInfo.uptime }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">数据库状态:</span>
                <el-tag :type="systemInfo.dbStatus === '正常' ? 'success' : 'danger'" size="small" effect="dark">{{ systemInfo.dbStatus }}</el-tag>
              </div>
              <div class="info-item">
                <span class="info-label">Redis状态:</span>
                <el-tag :type="systemInfo.redisStatus === '正常' ? 'success' : 'danger'" size="small" effect="dark">{{ systemInfo.redisStatus }}</el-tag>
              </div>
              <div class="info-item">
                <span class="info-label">CPU使用率:</span>
                <el-progress :percentage="systemInfo.cpuUsage || 0" :color="getCpuUsageColor"></el-progress>
              </div>
              <div class="info-item">
                <span class="info-label">内存使用率:</span>
                <el-progress :percentage="systemInfo.memoryUsage || 0" :color="getMemoryUsageColor"></el-progress>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, 
  Monitor, 
  DataAnalysis, 
  Timer, 
  Collection, 
  TrendCharts, 
  List, 
  QuestionFilled,
  Search
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { dashboardApi } from '@/api/dashboard'
import * as echarts from 'echarts'
import { formatDateTime, formatFullDateTime } from '@/utils/dateUtils'

const router = useRouter()

// 响应式数据
const timeRange = ref('7d')
const performanceChart = ref()
let chartInstance: echarts.ECharts | null = null
const chartLoading = ref(false)

// 加载状态
const loading = ref({
  stats: false,
  projects: false,
  analysis: false,
  systemInfo: false,
  trends: false
})

// 统计数据
const stats = ref({
  totalProjects: 0,
  totalRecords: 0,
  todayAnalysis: 0,
  avgResponseTime: 0
})

// 项目数据
const recentProjects = ref<Array<{
  key: string
  name: string
  status: string
  recordCount: number
}>>([])

// 分析结果
const recentAnalysis = ref<Array<{
  projectName: string
  type: string
  status: string
  createdAt: string
}>>([])

// 系统信息
const systemInfo = ref({
  version: 'v1.0.0',
  uptime: '0天 0小时',
  dbStatus: '正常',
  redisStatus: '正常',
  cpuUsage: 0,
  memoryUsage: 0
})

// 自动刷新定时器
let autoRefreshTimer: number | null = null

// 计算属性
const getCpuUsageColor = computed(() => {
  const usage = systemInfo.value.cpuUsage || 0
  if (usage < 50) return '#67C23A'
  if (usage < 80) return '#E6A23C'
  return '#F56C6C'
})

const getMemoryUsageColor = computed(() => {
  const usage = systemInfo.value.memoryUsage || 0
  if (usage < 60) return '#67C23A'
  if (usage < 85) return '#E6A23C'
  return '#F56C6C'
})

onMounted(() => {
  // 加载所有数据
  loadAllData()
  
  // 设置自动刷新（每60秒）
  autoRefreshTimer = window.setInterval(() => {
    loadAllData()
  }, 60000)
})

onUnmounted(() => {
  // 清除定时器
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
    autoRefreshTimer = null
  }
  
  // 销毁图表实例
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

// 加载所有数据
const loadAllData = () => {
  loadStats()
  loadRecentProjects()
  loadRecentAnalysis()
  loadSystemInfo()
  loadPerformanceTrends()
}

// 加载统计数据
const loadStats = async () => {
  loading.value.stats = true
  try {
    const response = await dashboardApi.getStats()
    
    stats.value = {
      totalProjects: response.data.total_projects,
      totalRecords: response.data.total_records,
      todayAnalysis: response.data.today_analysis,
      avgResponseTime: response.data.avg_response_time
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value.stats = false
  }
}

// 加载最近项目
const loadRecentProjects = async () => {
  loading.value.projects = true
  try {
    const response = await dashboardApi.getRecentProjects()
    recentProjects.value = response.data
  } catch (error) {
    console.error('加载项目数据失败:', error)
    ElMessage.error('加载项目数据失败')
  } finally {
    loading.value.projects = false
  }
}

// 加载最近分析
const loadRecentAnalysis = async () => {
  loading.value.analysis = true
  try {
    const response = await dashboardApi.getRecentAnalysis()
    recentAnalysis.value = response.data
  } catch (error) {
    console.error('加载分析结果失败:', error)
    ElMessage.error('加载分析结果失败')
  } finally {
    loading.value.analysis = false
  }
}

// 加载系统信息
const loadSystemInfo = async () => {
  loading.value.systemInfo = true
  try {
    const response = await dashboardApi.getSystemInfo()
    
    systemInfo.value = {
      version: response.data.version,
      uptime: response.data.uptime,
      dbStatus: response.data.db_status,
      redisStatus: response.data.redis_status,
      cpuUsage: 0, // API响应中没有cpu_usage字段
      memoryUsage: 0 // API响应中没有memory_usage字段
    }
  } catch (error) {
    console.error('加载系统信息失败:', error)
    ElMessage.error('加载系统信息失败')
  } finally {
    loading.value.systemInfo = false
  }
}

// 加载性能趋势数据
const loadPerformanceTrends = async () => {
  loading.value.trends = true
  try {
    const response = await dashboardApi.getPerformanceTrends(timeRange.value)
    await nextTick()
    if (response.data.response_times && response.data.response_times.length > 0) {
      renderChart(response.data.response_times)
    } else {
      // 如果没有数据，显示空图表
      renderEmptyChart()
    }
  } catch (error) {
    console.error('加载性能趋势数据失败:', error)
    ElMessage.error('加载性能趋势数据失败')
    renderEmptyChart()
  } finally {
    loading.value.trends = false
  }
}

// 渲染图表
const renderChart = (data: Array<{
  time: string
  avg_duration: number
  request_count: number
  max_duration: number
  min_duration: number
}>) => {
  if (!performanceChart.value) return
  
  // 初始化图表实例
  if (!chartInstance) {
    chartInstance = echarts.init(performanceChart.value)
  }
  
  // 处理数据
  const times = data.map(item => item.time)
  const avgDurations = data.map(item => item.avg_duration)
  const requestCounts = data.map(item => item.request_count)
  
  // 配置图表选项
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['平均响应时间(ms)', '请求数量']
    },
    xAxis: {
      type: 'category',
      data: times
    },
    yAxis: [
      {
        type: 'value',
        name: '响应时间(ms)',
        position: 'left'
      },
      {
        type: 'value',
        name: '请求数量',
        position: 'right'
      }
    ],
    series: [
      {
        name: '平均响应时间(ms)',
        type: 'line',
        yAxisIndex: 0,
        data: avgDurations,
        smooth: true
      },
      {
        name: '请求数量',
        type: 'bar',
        yAxisIndex: 1,
        data: requestCounts,
        barWidth: 15
      }
    ]
  }
  
  // 设置图表选项
  chartInstance.setOption(option, true)
  
  // 监听窗口大小变化，自适应图表
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
}

// 渲染空图表
const renderEmptyChart = () => {
  if (!performanceChart.value) return
  
  // 初始化图表实例
  if (!chartInstance) {
    chartInstance = echarts.init(performanceChart.value)
  }
  
  // 配置空图表选项
  const option = {
    title: {
      text: '暂无性能趋势数据',
      x: 'center',
      y: 'center',
      textStyle: {
        color: '#909399',
        fontSize: 16,
        fontWeight: 'normal'
      }
    },
    xAxis: {
      type: 'category',
      data: []
    },
    yAxis: [
      {
        type: 'value',
        name: '响应时间(ms)',
        position: 'left'
      },
      {
        type: 'value',
        name: '请求数量',
        position: 'right'
      }
    ],
    series: []
  }
  
  // 设置图表选项
  chartInstance.setOption(option, true)
}

// 刷新方法
const refreshProjects = () => loadRecentProjects()
const refreshAnalysis = () => loadRecentAnalysis()
const refreshSystemInfo = () => loadSystemInfo()

// 刷新所有数据
const refreshAll = () => {
  loadAllData()
  ElMessage.success('数据刷新成功')
}

// 跳转到项目管理页面
const goToProjects = () => {
  router.push('/projects')
}


</script>

<style lang="scss" scoped>
.dashboard {
  padding-top: 15px;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    
    .header-left {
      .title {
        font-size: 24px;
        font-weight: 600;
        color: #303133;
        margin-right: 16px;
      }
      
      .subtitle {
        font-size: 14px;
        color: #909399;
      }
    }
    
    .header-actions {
      display: flex;
      gap: 12px;
    }
  }
  
  .section-title {
    font-size: 18px;
    font-weight: 500;
    color: #303133;
    margin: 24px 0 16px 0;
    
    .el-icon {
      margin-left: 8px;
      color: #909399;
      font-size: 16px;
      vertical-align: middle;
    }
  }
  
  .overview-cards {
    .metric-card {
      .el-card__body {
        padding: 20px;
      }
      
      .metric-item {
        text-align: center;
        
        .metric-icon {
          width: 48px;
          height: 48px;
          line-height: 48px;
          margin: 0 auto 12px;
          border-radius: 50%;
          font-size: 24px;
          color: #fff;
        }
        
        .projects-icon {
          background: linear-gradient(135deg, #409eff, #52a7ff);
        }
        
        .records-icon {
          background: linear-gradient(135deg, #67c23a, #76c94f);
        }
        
        .analysis-icon {
          background: linear-gradient(135deg, #e6a23c, #ebb563);
        }
        
        .time-icon {
          background: linear-gradient(135deg, #f56c6c, #f78989);
        }
        
        .metric-value {
          font-size: 28px;
          font-weight: bold;
          color: #303133;
          margin-bottom: 4px;
        }
        
        .metric-label {
          font-size: 14px;
          color: #606266;
          margin-bottom: 4px;
        }
        
        .metric-desc {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }
  
  .chart-card {
    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .chart-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 500;
        color: #303133;
      }
      
      .chart-actions {
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }
    
    .chart-container {
      position: relative;
      
      .chart-loading {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10;
      }
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
  
  .project-list {
    .project-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
      
      .project-info {
        .project-name {
          font-weight: 500;
          color: #303133;
          margin-bottom: 4px;
        }
      }
      
      .project-metrics {
        font-size: 12px;
        color: #909399;
      }
    }
    
    .empty-placeholder {
      text-align: center;
      padding: 20px 0;
    }
  }
  
  .system-info {
    .info-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
      
      .info-label {
        color: #606266;
        font-size: 14px;
      }
      
      .info-value {
        color: #303133;
        font-weight: 500;
      }
    }
  }
}
</style>
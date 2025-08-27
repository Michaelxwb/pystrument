<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>性能监控仪表板</h1>
      <p>欢迎使用基于 Pyinstrument 的性能分析平台</p>
    </div>

    <el-row :gutter="20">
      <!-- 统计卡片 -->
      <el-col :span="6">
        <el-card class="stat-card" v-loading="loading.stats">
          <div class="stat-content">
            <div class="stat-number">{{ stats.totalProjects }}</div>
            <div class="stat-label">项目总数</div>
          </div>
          <el-icon class="stat-icon" color="#409EFF"><Collection /></el-icon>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" v-loading="loading.stats">
          <div class="stat-content">
            <div class="stat-number">{{ stats.totalRecords }}</div>
            <div class="stat-label">性能记录</div>
          </div>
          <el-icon class="stat-icon" color="#67C23A"><Monitor /></el-icon>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" v-loading="loading.stats">
          <div class="stat-content">
            <div class="stat-number">{{ stats.todayAnalysis }}</div>
            <div class="stat-label">今日分析</div>
          </div>
          <el-icon class="stat-icon" color="#E6A23C"><DataAnalysis /></el-icon>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" v-loading="loading.stats">
          <div class="stat-content">
            <div class="stat-number">{{ stats.avgResponseTime }}ms</div>
            <div class="stat-label">平均响应时间</div>
          </div>
          <el-icon class="stat-icon" color="#F56C6C"><Timer /></el-icon>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 性能趋势图 -->
      <el-col :span="16">
        <el-card v-loading="loading.trends">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>性能趋势</span>
              <el-select v-model="timeRange" @change="loadPerformanceTrends" style="width: 120px;">
                <el-option label="今天" value="24h" />
                <el-option label="7天" value="7d" />
                <el-option label="30天" value="30d" />
              </el-select>
            </div>
          </template>
          <div ref="performanceChart" style="height: 300px;"></div>
        </el-card>
      </el-col>

      <!-- 项目状态 -->
      <el-col :span="8">
        <el-card v-loading="loading.projects">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>项目状态</span>
              <el-button size="small" @click="refreshProjects" :icon="Refresh"></el-button>
            </div>
          </template>
          <div class="project-list">
            <div v-for="project in recentProjects" :key="project.key" class="project-item">
              <div class="project-info">
                <div class="project-name">{{ project.name }}</div>
                <div class="project-status">
                  <el-tag :type="project.status === 'active' ? 'success' : 'info'" size="small">
                    {{ project.status === 'active' ? '活跃' : '闲置' }}
                  </el-tag>
                </div>
              </div>
              <div class="project-metrics">
                <span>{{ project.recordCount }} 条记录</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 最近分析结果 -->
      <el-col :span="12">
        <el-card v-loading="loading.analysis">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>最近分析结果</span>
              <el-button size="small" @click="refreshAnalysis" :icon="Refresh"></el-button>
            </div>
          </template>
          <el-table :data="recentAnalysis" style="width: 100%">
            <el-table-column prop="projectName" label="项目" width="120" />
            <el-table-column prop="type" label="类型" width="80">
              <template #default="scope">
                <el-tag size="small">{{ scope.row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="scope">
                <el-tag 
                  :type="scope.row.status === 'completed' ? 'success' : 'warning'" 
                  size="small"
                >
                  {{ scope.row.status === 'completed' ? '完成' : '进行中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="createdAt" label="时间" />
          </el-table>
        </el-card>
      </el-col>

      <!-- 系统信息 -->
      <el-col :span="12">
        <el-card v-loading="loading.systemInfo">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>系统信息</span>
              <el-button size="small" @click="refreshSystemInfo" :icon="Refresh"></el-button>
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
              <el-tag :type="systemInfo.dbStatus === '正常' ? 'success' : 'danger'" size="small">{{ systemInfo.dbStatus }}</el-tag>
            </div>
            <div class="info-item">
              <span class="info-label">Redis状态:</span>
              <el-tag :type="systemInfo.redisStatus === '正常' ? 'success' : 'danger'" size="small">{{ systemInfo.redisStatus }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { dashboardApi } from '@/api/dashboard'
import * as echarts from 'echarts'

// 定义组件名称
defineOptions({
  name: 'Dashboard'
})

// 响应式数据
const timeRange = ref('7d')
const performanceChart = ref()
let chartInstance: echarts.ECharts | null = null

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
  redisStatus: '正常'
})

// 自动刷新定时器
let autoRefreshTimer: number | null = null

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
      redisStatus: response.data.redis_status
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

// 初始化图表
const initChart = () => {
  // 图表初始化已移至loadPerformanceTrends中
  console.log('初始化性能趋势图表')
}
</script>

<style lang="scss" scoped>
.dashboard {
  .dashboard-header {
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
  
  .stat-card {
    .el-card__body {
      padding: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .stat-content {
      .stat-number {
        font-size: 28px;
        font-weight: bold;
        color: #303133;
        line-height: 1;
      }
      
      .stat-label {
        font-size: 14px;
        color: #909399;
        margin-top: 8px;
      }
    }
    
    .stat-icon {
      font-size: 32px;
      opacity: 0.8;
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
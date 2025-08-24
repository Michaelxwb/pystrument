<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>性能监控仪表板</h1>
      <p>欢迎使用基于 Pyinstrument 的性能分析平台</p>
    </div>

    <el-row :gutter="20">
      <!-- 统计卡片 -->
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.totalProjects }}</div>
            <div class="stat-label">项目总数</div>
          </div>
          <el-icon class="stat-icon" color="#409EFF"><Collection /></el-icon>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.totalRecords }}</div>
            <div class="stat-label">性能记录</div>
          </div>
          <el-icon class="stat-icon" color="#67C23A"><Monitor /></el-icon>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.todayAnalysis }}</div>
            <div class="stat-label">今日分析</div>
          </div>
          <el-icon class="stat-icon" color="#E6A23C"><DataAnalysis /></el-icon>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
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
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>性能趋势</span>
              <el-select v-model="timeRange" style="width: 120px;">
                <el-option label="今天" value="today" />
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
        <el-card>
          <template #header>
            <span>项目状态</span>
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
        <el-card>
          <template #header>
            <span>最近分析结果</span>
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
        <el-card>
          <template #header>
            <span>系统信息</span>
          </template>
          <div class="system-info">
            <div class="info-item">
              <span class="info-label">平台版本:</span>
              <span class="info-value">v1.0.0</span>
            </div>
            <div class="info-item">
              <span class="info-label">运行时间:</span>
              <span class="info-value">{{ uptime }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">数据库状态:</span>
              <el-tag type="success" size="small">正常</el-tag>
            </div>
            <div class="info-item">
              <span class="info-label">Redis状态:</span>
              <el-tag type="success" size="small">正常</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// 定义组件名称
defineOptions({
  name: 'Dashboard'
})

// 响应式数据
const timeRange = ref('7d')
const performanceChart = ref()

const stats = ref({
  totalProjects: 5,
  totalRecords: 1234,
  todayAnalysis: 23,
  avgResponseTime: 145
})

const recentProjects = ref([
  { key: 'proj1', name: '电商系统', status: 'active', recordCount: 456 },
  { key: 'proj2', name: '用户中心', status: 'active', recordCount: 234 },
  { key: 'proj3', name: '订单服务', status: 'idle', recordCount: 123 },
  { key: 'proj4', name: '支付网关', status: 'active', recordCount: 89 }
])

const recentAnalysis = ref([
  { projectName: '电商系统', type: 'AI分析', status: 'completed', createdAt: '2024-01-20 10:30' },
  { projectName: '用户中心', type: '性能报告', status: 'processing', createdAt: '2024-01-20 09:15' },
  { projectName: '订单服务', type: 'AI分析', status: 'completed', createdAt: '2024-01-19 16:45' }
])

const uptime = ref('2天 14小时')

onMounted(() => {
  // 初始化图表
  initChart()
})

const initChart = () => {
  // 这里后续可以集成 ECharts
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
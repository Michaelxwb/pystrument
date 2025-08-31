<template>
  <div class="performance-detail">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="$router.go(-1)" type="text" class="back-button">
          <el-icon><ArrowLeft /></el-icon>
          返回性能监控
        </el-button>
        <span class="title">性能详情</span>
      </div>
      <div class="header-actions">
        <el-tooltip content="刷新数据" placement="top">
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-tooltip>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <!-- 基本信息 -->
        <div class="section">
          <h3 class="section-title">请求信息 <el-tooltip content="性能记录的基本信息" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
          <el-card>
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Document /></el-icon>
                  <span>基本信息</span>
                </div>
              </div>
            </template>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="请求路径">{{ record.path }}</el-descriptions-item>
              <el-descriptions-item label="HTTP方法">
                <el-tag :type="getMethodTagType(record.method)" size="small" effect="dark">
                  {{ record.method }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="状态码">
                <el-tag :type="record.statusCode >= 400 ? 'danger' : (record.statusCode >= 300 ? 'warning' : 'success')" size="small" effect="dark">
                  {{ record.statusCode }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="总耗时">
                <el-tooltip :content="getDurationTooltip(record.totalDuration)" placement="top">
                  <span :class="getDurationClass(record.totalDuration)">
                    {{ record.totalDuration }}ms
                  </span>
                </el-tooltip>
              </el-descriptions-item>
              <el-descriptions-item label="CPU时间">{{ record.cpuTime }}ms</el-descriptions-item>
              <el-descriptions-item label="内存峰值">{{ formatBytes(record.memoryPeak) }}</el-descriptions-item>
              <el-descriptions-item label="请求时间">{{ record.timestamp }}</el-descriptions-item>
              <el-descriptions-item label="项目">{{ record.projectKey }}</el-descriptions-item>
            </el-descriptions>
          </el-card>
        </div>

        <!-- 函数调用链 -->
        <div class="section">
          <h3 class="section-title">函数调用链 <el-tooltip content="函数调用的层级关系和性能数据" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
          <el-card>
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Connection /></el-icon>
                  <span>调用详情</span>
                </div>
                <div class="card-actions">
                  <el-button size="small" @click="expandAll">
                    <el-icon><SortDown /></el-icon>
                    展开全部
                  </el-button>
                  <el-button size="small" @click="collapseAll">
                    <el-icon><SortUp /></el-icon>
                    收起全部
                  </el-button>
                </div>
              </div>
            </template>
            <div class="function-calls">
              <el-tree
                :data="functionCalls"
                :props="treeProps"
                :expand-on-click-node="false"
                node-key="id"
                ref="treeRef"
                highlight-current
              >
                <template #default="{ node, data }">
                  <div class="custom-tree-node">
                    <div class="function-info">
                      <span class="function-name">{{ data.functionName }}</span>
                      <span class="function-file">{{ data.fileName }}:{{ data.lineNumber }}</span>
                    </div>
                    <div class="function-metrics">
                      <el-tooltip :content="getDurationTooltip(data.duration)" placement="top">
                        <span class="duration" :class="getDurationClass(data.duration)">
                          {{ data.duration }}ms
                        </span>
                      </el-tooltip>
                      <span class="percentage">{{ data.percentage }}%</span>
                    </div>
                  </div>
                </template>
              </el-tree>
              <div v-if="functionCalls.length === 0" class="empty-data">
                <el-empty description="暂无函数调用数据" :image-size="80" />
              </div>
            </div>
          </el-card>
        </div>
      </el-col>

      <el-col :span="8">
        <!-- 性能指标 -->
        <div class="section">
          <h3 class="section-title">性能指标 <el-tooltip content="关键性能指标数据" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
          <el-card>
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Odometer /></el-icon>
                  <span>指标详情</span>
                </div>
              </div>
            </template>
            <div class="metrics-container">
              <div class="metric-item">
                <div class="metric-icon primary-icon"><el-icon><Timer /></el-icon></div>
                <div class="metric-content">
                  <div class="metric-label">总耗时</div>
                  <div class="metric-value primary">{{ record.totalDuration }}ms</div>
                </div>
              </div>
              <div class="metric-item">
                <div class="metric-icon success-icon"><el-icon><Cpu /></el-icon></div>
                <div class="metric-content">
                  <div class="metric-label">CPU时间</div>
                  <div class="metric-value success">{{ record.cpuTime }}ms</div>
                </div>
              </div>
              <div class="metric-item">
                <div class="metric-icon warning-icon"><el-icon><Download /></el-icon></div>
                <div class="metric-content">
                  <div class="metric-label">I/O等待</div>
                  <div class="metric-value warning">{{ record.ioWait }}ms</div>
                </div>
              </div>
              <div class="metric-item">
                <div class="metric-icon info-icon"><el-icon><Coin /></el-icon></div>
                <div class="metric-content">
                  <div class="metric-label">内存使用</div>
                  <div class="metric-value info">{{ formatBytes(record.memoryPeak) }}</div>
                </div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 请求详情 -->
        <div class="section">
          <h3 class="section-title">请求详情 <el-tooltip content="HTTP请求的详细信息" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
          <el-card>
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><List /></el-icon>
                  <span>详细信息</span>
                </div>
              </div>
            </template>
            <div class="request-details">
              <div class="detail-section">
                <h4>Headers</h4>
                <div class="detail-content">
                  <div v-for="(value, key) in record.headers" :key="key" class="header-item">
                    <span class="header-key">{{ key }}:</span>
                    <span class="header-value">{{ value }}</span>
                  </div>
                </div>
              </div>
              <div class="detail-section" v-if="record.params && Object.keys(record.params).length > 0">
                <h4>Query Params</h4>
                <div class="detail-content">
                  <pre>{{ JSON.stringify(record.params, null, 2) }}</pre>
                </div>
              </div>
              <div class="detail-section" v-if="record.body">
                <h4>Request Body</h4>
                <div class="detail-content">
                  <pre>{{ JSON.stringify(record.body, null, 2) }}</pre>
                </div>
              </div>
              <div v-if="!record.headers || Object.keys(record.headers).length === 0" class="empty-data">
                <el-empty description="暂无请求详情数据" :image-size="60" />
              </div>
            </div>
          </el-card>
        </div>

        <!-- 操作按钮 -->
        <div class="section">
          <h3 class="section-title">操作 <el-tooltip content="对当前性能记录的操作" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
          <el-card>
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Operation /></el-icon>
                  <span>操作选项</span>
                </div>
              </div>
            </template>
            <div class="action-buttons">
              <el-button type="primary" @click="triggerAnalysis" size="large">
                <el-icon><DataAnalysis /></el-icon>
                AI分析
              </el-button>
              <el-button @click="exportData" size="large">
                <el-icon><Download /></el-icon>
                导出数据
              </el-button>
              <el-button @click="shareReport" size="large">
                <el-icon><Share /></el-icon>
                分享报告
              </el-button>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { performanceApi } from '@/api/performance'
import { ElMessage } from 'element-plus'
import { 
  ArrowLeft, 
  Refresh, 
  Document, 
  Connection, 
  SortDown, 
  SortUp, 
  Odometer, 
  Timer, 
  Cpu, 
  Download as DownloadIcon, 
  Coin, 
  List, 
  Operation, 
  DataAnalysis, 
  Share,
  QuestionFilled
} from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/dateUtils'
import type { PerformanceRecord } from '@/types/performance'

const route = useRoute()
const router = useRouter()

// Props
const props = defineProps<{
  traceId: string
}>()

// 响应式数据
const traceId = ref(props.traceId || route.params.traceId as string)
const treeRef = ref()

interface DetailRecord {
  path: string
  method: string
  statusCode: number
  totalDuration: number
  cpuTime: number
  ioWait: number
  memoryPeak: number
  timestamp: string
  projectKey: string
  headers: Record<string, string>
  params: Record<string, any>
  body: any
}

const record = ref<DetailRecord>({
  path: '/api/users/profile',
  method: 'GET',
  statusCode: 200,
  totalDuration: 234,
  cpuTime: 156,
  ioWait: 78,
  memoryPeak: 2048576,
  timestamp: '2024-01-20 15:30:00',
  projectKey: 'example-project',
  headers: {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0...',
    'Authorization': 'Bearer ***'
  },
  params: {
    page: 1,
    size: 20
  },
  body: null
})

const functionCalls = ref<any[]>([])

const treeProps = {
  children: 'children',
  label: 'functionName'
}

onMounted(() => {
  loadPerformanceData()
})

const loadPerformanceData = async () => {
  try {
    console.log('加载性能数据:', traceId.value)
    const response = await performanceApi.getRecordDetail(traceId.value)
    const data = response.data
    
    // 更新记录数据
    record.value = {
      path: data.request_info?.path || '',
      method: data.request_info?.method || 'GET',
      statusCode: data.response_info?.status_code || 200,
      totalDuration: Math.round((data.performance_metrics?.total_duration || 0) * 1000),
      cpuTime: Math.round((data.performance_metrics?.cpu_time || 0) * 1000),
      ioWait: Math.round(((data.performance_metrics?.total_duration || 0) - (data.performance_metrics?.cpu_time || 0)) * 1000),
      memoryPeak: (data.performance_metrics?.memory_usage?.peak_memory || 0) * 1024 * 1024,
      timestamp: formatDateTime(data.timestamp),
      projectKey: data.project_key,
      headers: data.request_info?.headers || {},
      params: data.request_info?.query_params || {},
      body: null
    }
    
    // 处理函数调用数据
    if (data.function_calls && data.function_calls.length > 0) {
      functionCalls.value = processFunctionCalls(data.function_calls, data.performance_metrics?.total_duration || 0)
    } else {
      functionCalls.value = []
    }
    
    console.log('性能数据加载成功:', data)
  } catch (error) {
    console.error('加载性能数据失败:', error)
    ElMessage.error('加载性能数据失败')
  }
}

// 刷新数据
const refreshData = () => {
  loadPerformanceData()
  ElMessage.success('数据刷新成功')
}

const getMethodTagType = (method: string): 'success' | 'primary' | 'warning' | 'danger' | 'info' => {
  const types: Record<string, 'success' | 'primary' | 'warning' | 'danger' | 'info'> = {
    'GET': 'success',
    'POST': 'primary',
    'PUT': 'warning',
    'DELETE': 'danger'
  }
  return types[method] || 'info'
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

const formatBytes = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 移除本地的formatDateTime函数，使用从dateUtils导入的函数

// 处理函数调用数据，转换为树形结构
const processFunctionCalls = (calls: any[], totalDuration: number) => {
  if (!calls || calls.length === 0) return []
  
  // 按调用顺序排序
  calls.sort((a, b) => a.call_order - b.call_order)
  
  // 创建调用ID映射
  const callMap = new Map()
  calls.forEach(call => {
    callMap.set(call.call_id, {
      id: call.call_id,
      functionName: call.function_name,
      fileName: call.file_path.split('/').pop() || call.file_path,
      lineNumber: call.line_number,
      duration: Math.round(call.duration * 1000),
      percentage: Math.round((call.duration / totalDuration) * 100),
      children: []
    })
  })
  
  // 构建树形结构
  const rootCalls: any[] = []
  calls.forEach(call => {
    const node = callMap.get(call.call_id)
    
    if (call.parent_call_id && callMap.has(call.parent_call_id)) {
      const parent = callMap.get(call.parent_call_id)
      parent.children.push(node)
    } else {
      rootCalls.push(node)
    }
  })
  
  return rootCalls
}

const expandAll = () => {
  if (!treeRef.value) return
  
  // 通过DOM直接操作展开按钮
  const expandButtons = document.querySelectorAll('.el-tree-node__expand-icon:not(.is-leaf):not(.expanded)')
  expandButtons.forEach(button => {
    ;(button as HTMLElement).click()
  })
}

const collapseAll = () => {
  if (!treeRef.value) return
  
  // 通过DOM直接操作已展开的按钮
  const collapseButtons = document.querySelectorAll('.el-tree-node__expand-icon:not(.is-leaf).expanded')
  collapseButtons.forEach(button => {
    ;(button as HTMLElement).click()
  })
}

const triggerAnalysis = () => {
  console.log('触发AI分析')
  ElMessage.info('AI分析功能正在开发中')
  // 这里后续接入真实API
}

const exportData = () => {
  console.log('导出数据')
  ElMessage.info('导出功能正在开发中')
  // 这里后续实现导出功能
}

const shareReport = () => {
  console.log('分享报告')
  ElMessage.info('分享功能正在开发中')
  // 这里后续实现分享功能
}
</script>

<style lang="scss" scoped>
.performance-detail {
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
  
  .metrics-container {
    .metric-item {
      display: flex;
      align-items: center;
      padding: 16px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
      
      .metric-icon {
        width: 40px;
        height: 40px;
        line-height: 40px;
        text-align: center;
        border-radius: 50%;
        margin-right: 12px;
        font-size: 18px;
        color: #fff;
      }
      
      .primary-icon {
        background: linear-gradient(135deg, #409eff, #52a7ff);
      }
      
      .success-icon {
        background: linear-gradient(135deg, #67c23a, #76c94f);
      }
      
      .warning-icon {
        background: linear-gradient(135deg, #e6a23c, #ebb563);
      }
      
      .info-icon {
        background: linear-gradient(135deg, #909399, #a1a4aa);
      }
      
      .metric-content {
        flex: 1;
        
        .metric-label {
          color: #606266;
          font-size: 14px;
          margin-bottom: 4px;
        }
        
        .metric-value {
          font-weight: 600;
          font-size: 18px;
          
          &.primary { color: #409EFF; }
          &.success { color: #67C23A; }
          &.warning { color: #E6A23C; }
          &.info { color: #909399; }
        }
      }
    }
  }
  
  .function-calls {
    max-height: 500px;
    overflow-y: auto;
    
    .custom-tree-node {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      padding: 8px 0;
      
      .function-info {
        display: flex;
        flex-direction: column;
        
        .function-name {
          font-weight: 500;
          color: #303133;
          margin-bottom: 2px;
        }
        
        .function-file {
          font-size: 12px;
          color: #909399;
          font-family: monospace;
        }
      }
      
      .function-metrics {
        display: flex;
        gap: 12px;
        align-items: center;
        
        .duration {
          font-weight: 500;
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 12px;
        }
        
        .duration-fast {
          background: #f0f9ff;
          color: #409eff;
        }
        
        .duration-normal {
          background: #f0f9ff;
          color: #409eff;
        }
        
        .duration-slow {
          background: #fdf6ec;
          color: #e6a23c;
        }
        
        .duration-very-slow {
          background: #fef0f0;
          color: #f56c6c;
        }
        
        .percentage {
          font-size: 12px;
          color: #909399;
        }
      }
    }
    
    .empty-data {
      text-align: center;
      padding: 20px 0;
    }
  }
  
  .request-details {
    .detail-section {
      margin-bottom: 16px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      h4 {
        margin: 0 0 8px 0;
        color: #606266;
        font-size: 14px;
        font-weight: 600;
      }
      
      .detail-content {
        background: #f8f9fa;
        border-radius: 4px;
        padding: 12px;
        font-size: 12px;
        
        .header-item {
          display: flex;
          margin-bottom: 4px;
          
          &:last-child {
            margin-bottom: 0;
          }
          
          .header-key {
            color: #606266;
            font-weight: 500;
            margin-right: 8px;
            min-width: 120px;
          }
          
          .header-value {
            color: #303133;
            word-break: break-all;
            flex: 1;
          }
        }
        
        pre {
          margin: 0;
          white-space: pre-wrap;
          word-break: break-word;
          color: #303133;
          font-family: monospace;
          background: transparent;
        }
      }
    }
    
    .empty-data {
      text-align: center;
      padding: 20px 0;
    }
  }
  
  .action-buttons {
    display: flex;
    flex-direction: column;
    gap: 12px;
    
    .el-button {
      justify-content: flex-start;
    }
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
}
</style>
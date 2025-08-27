<template>
  <div class="performance-detail">
    <div class="page-header">
      <el-button @click="$router.go(-1)" type="text">
        <el-icon><ArrowLeft /></el-icon>
        返回性能监控
      </el-button>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <!-- 基本信息 -->
        <el-card>
          <template #header>
            <span>请求信息</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="请求路径">{{ record.path }}</el-descriptions-item>
            <el-descriptions-item label="HTTP方法">
              <el-tag :type="getMethodTagType(record.method)">{{ record.method }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态码">
              <el-tag :type="record.statusCode >= 400 ? 'danger' : 'success'">
                {{ record.statusCode }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="总耗时">
              <span :class="getDurationClass(record.totalDuration)">
                {{ record.totalDuration }}ms
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="CPU时间">{{ record.cpuTime }}ms</el-descriptions-item>
            <el-descriptions-item label="内存峰值">{{ formatBytes(record.memoryPeak) }}</el-descriptions-item>
            <el-descriptions-item label="请求时间">{{ record.timestamp }}</el-descriptions-item>
            <el-descriptions-item label="项目">{{ record.projectKey }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 函数调用链 -->
        <el-card style="margin-top: 20px;">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>函数调用链</span>
              <div>
                <el-button size="small" @click="expandAll">展开全部</el-button>
                <el-button size="small" @click="collapseAll">收起全部</el-button>
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
            >
              <template #default="{ node, data }">
                <div class="custom-tree-node">
                  <div class="function-info">
                    <span class="function-name">{{ data.functionName }}</span>
                    <span class="function-file">{{ data.fileName }}:{{ data.lineNumber }}</span>
                  </div>
                  <div class="function-metrics">
                    <span class="duration" :class="getDurationClass(data.duration)">
                      {{ data.duration }}ms
                    </span>
                    <span class="percentage">{{ data.percentage }}%</span>
                  </div>
                </div>
              </template>
            </el-tree>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <!-- 性能指标 -->
        <el-card>
          <template #header>
            <span>性能指标</span>
          </template>
          <div class="metrics-container">
            <div class="metric-item">
              <div class="metric-label">总耗时</div>
              <div class="metric-value primary">{{ record.totalDuration }}ms</div>
            </div>
            <div class="metric-item">
              <div class="metric-label">CPU时间</div>
              <div class="metric-value success">{{ record.cpuTime }}ms</div>
            </div>
            <div class="metric-item">
              <div class="metric-label">I/O等待</div>
              <div class="metric-value warning">{{ record.ioWait }}ms</div>
            </div>
            <div class="metric-item">
              <div class="metric-label">内存使用</div>
              <div class="metric-value info">{{ formatBytes(record.memoryPeak) }}</div>
            </div>
          </div>
        </el-card>

        <!-- 请求详情 -->
        <el-card style="margin-top: 20px;">
          <template #header>
            <span>请求详情</span>
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
            <div class="detail-section" v-if="record.params">
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
          </div>
        </el-card>

        <!-- 操作按钮 -->
        <el-card style="margin-top: 20px;">
          <template #header>
            <span>操作</span>
          </template>
          <div class="action-buttons">
            <el-button type="primary" @click="triggerAnalysis">
              <el-icon><DataAnalysis /></el-icon>
              AI分析
            </el-button>
            <el-button @click="exportData">
              <el-icon><Download /></el-icon>
              导出数据
            </el-button>
            <el-button @click="shareReport">
              <el-icon><Share /></el-icon>
              分享报告
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { performanceApi } from '@/api/performance'
import { ElMessage } from 'element-plus'
import { ArrowLeft, DataAnalysis, Download, Share } from '@element-plus/icons-vue'
import PageTitle from '@/components/PageTitle.vue'

const route = useRoute()
const router = useRouter()

// Props
const props = defineProps<{
  traceId: string
}>()

// 响应式数据
const traceId = ref(props.traceId || route.params.traceId as string)
const treeRef = ref()

const record = ref({
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

const functionCalls = ref([
  {
    id: '1',
    functionName: 'get_user_profile',
    fileName: 'user_service.py',
    lineNumber: 45,
    duration: 234,
    percentage: 100,
    children: [
      {
        id: '2',
        functionName: 'validate_token',
        fileName: 'auth.py',
        lineNumber: 23,
        duration: 45,
        percentage: 19.2,
        children: []
      },
      {
        id: '3',
        functionName: 'query_user_data',
        fileName: 'database.py',
        lineNumber: 67,
        duration: 156,
        percentage: 66.7,
        children: [
          {
            id: '4',
            functionName: 'execute_query',
            fileName: 'database.py',
            lineNumber: 89,
            duration: 134,
            percentage: 57.3,
            children: []
          }
        ]
      },
      {
        id: '5',
        functionName: 'format_response',
        fileName: 'serializers.py',
        lineNumber: 12,
        duration: 33,
        percentage: 14.1,
        children: []
      }
    ]
  }
])

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
    }
    
    console.log('性能数据加载成功:', data)
  } catch (error) {
    console.error('加载性能数据失败:', error)
    ElMessage.error('加载性能数据失败')
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

const formatBytes = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDateTime = (dateString?: string) => {
  if (!dateString) return ''
  try {
    return new Date(dateString).toLocaleString('zh-CN')
  } catch (error) {
    return dateString
  }
}

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
  const rootCalls = []
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
  // 这里后续接入真实API
}

const exportData = () => {
  console.log('导出数据')
  // 这里后续实现导出功能
}

const shareReport = () => {
  console.log('分享报告')
  // 这里后续实现分享功能
}
</script>

<style lang="scss" scoped>
.performance-detail {
  padding-top: 15px;
  
  .page-header {
    margin-bottom: 24px;
  }
  
  .metrics-container {
    .metric-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
      
      .metric-label {
        color: #606266;
        font-size: 14px;
      }
      
      .metric-value {
        font-weight: 600;
        font-size: 16px;
        
        &.primary { color: #409EFF; }
        &.success { color: #67C23A; }
        &.warning { color: #E6A23C; }
        &.info { color: #909399; }
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
      padding: 4px 0;
      
      .function-info {
        display: flex;
        flex-direction: column;
        
        .function-name {
          font-weight: 500;
          color: #303133;
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
        
        .duration {
          font-weight: 500;
        }
        
        .percentage {
          font-size: 12px;
          color: #909399;
        }
      }
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
          }
          
          .header-value {
            color: #303133;
            word-break: break-all;
          }
        }
        
        pre {
          margin: 0;
          white-space: pre-wrap;
          word-break: break-word;
          color: #303133;
          font-family: monospace;
        }
      }
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
  
  .text-success {
    color: #67C23A;
  }
  
  .text-warning {
    color: #E6A23C;
  }
  
  .text-danger {
    color: #F56C6C;
  }
}
</style>
<template>
  <div class="performance-details">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 基本信息 -->
      <el-tab-pane label="基本信息" name="basic">
        <div class="basic-info">
          <el-descriptions title="请求信息" :column="2" border>
            <el-descriptions-item label="请求路径">
              {{ record.request_info?.path || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="请求方法">
              <el-tag :type="getMethodTagType(record.request_info?.method)" size="small">
                {{ record.request_info?.method || '-' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态码">
              <el-tag :type="getStatusTagType(record.response_info?.status_code)" size="small">
                {{ record.response_info?.status_code || '-' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="用户代理">
              {{ record.request_info?.user_agent || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="客户端IP">
              {{ record.request_info?.remote_ip || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="请求时间">
              {{ formatDateTime(record.timestamp) }}
            </el-descriptions-item>
          </el-descriptions>
          
          <el-descriptions title="响应信息" :column="2" border style="margin-top: 20px;">
            <el-descriptions-item label="响应大小">
              {{ formatBytes(record.response_info?.response_size) }}
            </el-descriptions-item>
            <el-descriptions-item label="内容类型">
              {{ record.response_info?.content_type || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="响应头数量">
              {{ Object.keys(record.response_info?.headers || {}).length }}
            </el-descriptions-item>
            <el-descriptions-item label="处理时间">
              {{ (record.performance_metrics?.total_duration * 1000).toFixed(2) }}ms
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-tab-pane>
      
      <!-- 性能指标 -->
      <el-tab-pane label="性能指标" name="metrics">
        <div class="metrics-info">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card>
                <template #header>
                  <span>时间指标</span>
                </template>
                <div class="metric-item">
                  <div class="metric-label">总耗时</div>
                  <div class="metric-value large">
                    {{ (record.performance_metrics?.total_duration * 1000).toFixed(2) }}ms
                  </div>
                </div>
                <div class="metric-item">
                  <div class="metric-label">CPU时间</div>
                  <div class="metric-value">
                    {{ (record.performance_metrics?.cpu_time * 1000).toFixed(2) }}ms
                  </div>
                </div>
                <div class="metric-item">
                  <div class="metric-label">等待时间</div>
                  <div class="metric-value">
                    {{ ((record.performance_metrics?.total_duration - record.performance_metrics?.cpu_time) * 1000).toFixed(2) }}ms
                  </div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :span="12">
              <el-card>
                <template #header>
                  <span>内存指标</span>
                </template>
                <div class="metric-item">
                  <div class="metric-label">峰值内存</div>
                  <div class="metric-value large">
                    {{ formatBytes(record.performance_metrics?.memory_usage?.peak_memory * 1024 * 1024) }}
                  </div>
                </div>
                <div class="metric-item">
                  <div class="metric-label">起始内存</div>
                  <div class="metric-value">
                    {{ formatBytes(record.performance_metrics?.memory_usage?.start_memory * 1024 * 1024) }}
                  </div>
                </div>
                <div class="metric-item">
                  <div class="metric-label">内存增长</div>
                  <div class="metric-value">
                    {{ formatBytes((record.performance_metrics?.memory_usage?.peak_memory - record.performance_metrics?.memory_usage?.start_memory) * 1024 * 1024) }}
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
          
          <el-card style="margin-top: 20px;">
            <template #header>
              <span>函数调用统计</span>
            </template>
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value">{{ record.function_calls?.length || 0 }}</div>
                  <div class="stat-label">总函数调用</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value">{{ getSlowFunctionsCount() }}</div>
                  <div class="stat-label">慢函数 (>100ms)</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value">{{ getMaxDepth() }}</div>
                  <div class="stat-label">最大调用深度</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value">{{ getUniqueFilesCount() }}</div>
                  <div class="stat-label">涉及文件数</div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </div>
      </el-tab-pane>
      
      <!-- 函数调用链 -->
      <el-tab-pane label="函数调用链" name="calltrace">
        <div class="calltrace-info">
          <!-- 慢函数列表 -->
          <el-card v-if="slowFunctions.length > 0" class="slow-functions-card">
            <template #header>
              <span>性能瓶颈函数 (耗时 > 100ms)</span>
            </template>
            <div class="slow-functions-list">
              <div
                v-for="func in slowFunctions.slice(0, 10)"
                :key="func.id"
                class="slow-function-item"
                @click="highlightFunction(func)"
              >
                <div class="function-info">
                  <div class="function-name">{{ func.function_name }}</div>
                  <div class="function-file">{{ getShortPath(func.file_path) }}</div>
                </div>
                <div class="function-duration">
                  <span class="duration-value">{{ (func.duration * 1000).toFixed(2) }}ms</span>
                  <div class="duration-bar">
                    <div
                      class="duration-fill"
                      :style="{ width: (func.duration / maxDuration * 100) + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 调用链树形视图 -->
          <el-card class="trace-tree-card" style="margin-top: 20px;">
            <template #header>
              <div class="tree-header">
                <span>调用链树形视图</span>
                <div class="tree-controls">
                  <el-tooltip content="展开全部节点" placement="top">
                    <el-button size="small" type="primary" plain @click="expandAll">
                      <el-icon><ArrowDown /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="收起全部节点" placement="top">
                    <el-button size="small" type="info" plain @click="collapseAll">
                      <el-icon><ArrowUp /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <el-tooltip content="只展开关键节点" placement="top">
                    <el-button size="small" type="warning" plain @click="expandSlowNodes">
                      <el-icon><Warning /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
              </div>
            </template>
            <div v-if="record.function_calls && record.function_calls.length > 0" class="trace-tree">
              <el-tree
                ref="treeRef"
                :data="treeData"
                :props="treeProps"
                node-key="id"
                :expand-on-click-node="false"
                class="custom-tree"
                default-expand-all
              >
                <template #default="{ node, data }">
                  <div class="tree-node" :class="{ 'highlighted': data.highlighted, 'slow-node': data.duration > 0.1 }">
                    <div class="node-main">
                      <div class="node-info">
                        <span class="node-name">{{ data.function_name }}</span>
                        <el-tag
                          v-if="data.duration > 0.1"
                          type="danger"
                          size="small"
                          class="slow-tag"
                        >
                          慢
                        </el-tag>
                      </div>
                      <div class="node-duration">
                        <span :class="getDurationClass(data.duration)">
                          {{ (data.duration * 1000).toFixed(2) }}ms
                        </span>
                      </div>
                    </div>
                    <div class="node-details">
                      <span class="node-file" :title="data.file_path">{{ getShortPath(data.file_path) }}</span>
                      <span v-if="data.line_number" class="node-line">行号: {{ data.line_number }}</span>
                      <span class="node-depth">深度: {{ data.depth }}</span>
                    </div>
                  </div>
                </template>
              </el-tree>
            </div>
            <el-empty v-else description="暂无函数调用数据" />
          </el-card>
        </div>
      </el-tab-pane>
      
      <!-- 环境信息 -->
      <el-tab-pane label="环境信息" name="environment">
        <div class="environment-info">
          <el-descriptions title="运行环境" :column="2" border>
            <el-descriptions-item label="Python版本">
              {{ record.environment?.python_version || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="框架版本">
              {{ record.environment?.framework_version || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="操作系统">
              {{ record.environment?.platform || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="主机名">
              {{ record.environment?.hostname || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="进程ID">
              {{ record.environment?.process_id || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="线程ID">
              {{ record.environment?.thread_id || '-' }}
            </el-descriptions-item>
          </el-descriptions>
          
          <el-card style="margin-top: 20px;">
            <template #header>
              <span>请求头信息</span>
            </template>
            <el-table
              :data="getRequestHeaders()"
              style="width: 100%"
              max-height="300"
            >
              <el-table-column prop="key" label="Header名称" width="200" />
              <el-table-column prop="value" label="Header值" />
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>
      
      <!-- 原始数据 -->
      <el-tab-pane label="原始数据" name="raw">
        <div class="raw-data">
          <el-card>
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>原始JSON数据</span>
                <el-button size="small" @click="copyRawData">复制数据</el-button>
              </div>
            </template>
            <el-input
              v-model="rawDataText"
              type="textarea"
              :rows="20"
              readonly
              class="raw-data-textarea"
            />
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, defineProps, defineEmits } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowDown, ArrowUp, Warning } from '@element-plus/icons-vue'
import type { PerformanceRecord, FunctionCall } from '@/types/performance'
import { formatDateTime } from '@/utils/dateUtils'

// Props
const props = defineProps<{
  record: PerformanceRecord
}>()

// Emits
const emits = defineEmits<{
  close: []
}>()

// 响应式数据
const activeTab = ref('basic')
const treeRef = ref()
const highlightedId = ref('')

// 计算属性
const rawDataText = computed(() => {
  return JSON.stringify(props.record, null, 2)
})

// 获取慢函数列表
const slowFunctions = computed(() => {
  if (!props.record.function_calls) return []
  return props.record.function_calls
    .filter(call => call.duration > 0.1)
    .map(call => ({
      ...call,
      id: call.call_id || `${call.function_name}_${call.depth}_${Math.random()}`
    }))
    .sort((a, b) => b.duration - a.duration)
})

// 获取最大耗时
const maxDuration = computed(() => {
  if (!props.record.function_calls || props.record.function_calls.length === 0) return 0
  return Math.max(...props.record.function_calls.map(call => call.duration))
})

// 构建树形数据
const treeData = computed(() => {
  const calls = props.record.function_calls || []
  if (calls.length === 0) return []
  
  // 创建节点映射
  const nodeMap = new Map()
  const result: any[] = []
  
  // 首先创建所有节点
  for (const call of calls) {
    const node = {
      ...call,
      id: call.call_id || `${call.function_name}_${call.depth}_${Math.random()}`,
      highlighted: highlightedId.value === call.call_id
    }
    nodeMap.set(node.id, node)
    // 也以call_id往Map中存一份，便于后续查找
    if (call.call_id && call.call_id !== node.id) {
      nodeMap.set(call.call_id, node)
    }
  }
  
  // 建立父子关系
  for (const call of calls) {
    const node = nodeMap.get(call.call_id || `${call.function_name}_${call.depth}_${Math.random()}`)
    if (!node) continue
    
    // 有父调用ID的情况
    if (call.parent_call_id) {
      const parentNode = nodeMap.get(call.parent_call_id)
      if (parentNode) {
        if (!parentNode.children) parentNode.children = []
        if (!parentNode.children.some(child => child.id === node.id)) {
          parentNode.children.push(node)
        }
        continue
      }
    }
    
    // 没有父调用ID或找不到父节点的情况
    if (call.depth === 0) {
      if (!result.some(item => item.id === node.id)) {
        result.push(node)
      }
    } else {
      // 找到相同深度的所有函数调用
      const potentialParents = calls.filter(p => 
        p.depth === call.depth - 1 && 
        p.call_order < call.call_order
      )
      
      if (potentialParents.length > 0) {
        // 选择调用顺序最接近当前函数的作为父函数
        const closestParent = potentialParents.reduce((prev, curr) => 
          (call.call_order - curr.call_order < call.call_order - prev.call_order) ? curr : prev
        )
        
        const parentNode = nodeMap.get(closestParent.call_id || `${closestParent.function_name}_${closestParent.depth}_${Math.random()}`)
        if (parentNode) {
          if (!parentNode.children) parentNode.children = []
          if (!parentNode.children.some(child => child.id === node.id)) {
            parentNode.children.push(node)
          }
        } else {
          // 如果找不到父节点，则放到根节点
          if (!result.some(item => item.id === node.id)) {
            result.push(node)
          }
        }
      } else {
        // 如果找不到父函数，则放到根节点
        if (!result.some(item => item.id === node.id)) {
          result.push(node)
        }
      }
    }
  }
  
  return result
})

const treeProps = {
  children: 'children',
  label: 'function_name'
}

// 方法
// 移除本地的formatDateTime函数，使用从dateUtils导入的函数

const formatBytes = (bytes: number) => {
  if (!bytes || bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
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

const getSlowFunctionsCount = () => {
  if (!props.record.function_calls) return 0
  return props.record.function_calls.filter(call => call.duration > 0.1).length
}

const getMaxDepth = () => {
  if (!props.record.function_calls) return 0
  return Math.max(...props.record.function_calls.map(call => call.depth || 0))
}

const getUniqueFilesCount = () => {
  if (!props.record.function_calls) return 0
  const files = new Set(props.record.function_calls.map(call => call.file_path))
  return files.size
}

const getRequestHeaders = () => {
  const headers = props.record.request_info?.headers || {}
  return Object.entries(headers).map(([key, value]) => ({ key, value }))
}

const copyRawData = async () => {
  try {
    await navigator.clipboard.writeText(rawDataText.value)
    ElMessage.success('数据已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 获取所有节点的key
const getAllKeys = () => {
  if (!treeData.value || treeData.value.length === 0) {
    return []
  }
  
  const keys: string[] = []
  
  const getKeys = (nodes: any[]) => {
    if (!nodes) return
    
    for (const node of nodes) {
      if (node.id) {
        keys.push(node.id)
      }
      if (node.children && node.children.length > 0) {
        getKeys(node.children)
      }
    }
  }
  
  getKeys(treeData.value)
  return keys
}

// 获取所有慢节点的key
const getSlowNodeKeys = () => {
  if (!treeData.value || treeData.value.length === 0) {
    return []
  }
  
  const slowKeys: string[] = []
  
  const findSlowNodes = (nodes: any[]) => {
    if (!nodes) return
    
    for (const node of nodes) {
      if (node.id && node.duration > 0.1) { // 超过100ms的节点认为是慢节点
        slowKeys.push(node.id)
      }
      if (node.children && node.children.length > 0) {
        findSlowNodes(node.children)
      }
    }
  }
  
  findSlowNodes(treeData.value)
  return slowKeys
}

// 展开所有节点
const expandAll = () => {
  try {
    const allKeys = getAllKeys()
    if (allKeys.length === 0) {
      ElMessage.info('没有可展开的节点')
      return
    }
    
    if (treeRef.value) {
      for (const key of allKeys) {
        if (treeRef.value.store.nodesMap[key]) {
          treeRef.value.store.nodesMap[key].expanded = true
        }
      }
      treeRef.value.$forceUpdate()
      ElMessage.success(`已展开${allKeys.length}个节点`)
    }
  } catch (error) {
    console.error('展开所有节点失败:', error)
    ElMessage.error('展开操作失败')
  }
}

// 收起所有节点
const collapseAll = () => {
  try {
    const allKeys = getAllKeys()
    if (allKeys.length === 0) {
      ElMessage.info('没有可收起的节点')
      return
    }
    
    if (treeRef.value && treeRef.value.store && treeRef.value.store.nodesMap) {
      for (const key of allKeys) {
        if (treeRef.value.store.nodesMap[key]) {
          treeRef.value.store.nodesMap[key].expanded = false
        }
      }
      treeRef.value.$forceUpdate()
      ElMessage.success('已收起所有节点')
    }
  } catch (error) {
    console.error('收起所有节点失败:', error)
    ElMessage.error('收起操作失败')
  }
}

// 展开慢节点
const expandSlowNodes = async () => {
  try {
    // 先收起所有节点
    await collapseAll()
    
    // 然后获取所有慢节点的key
    const slowKeys = getSlowNodeKeys()
    
    if (slowKeys.length === 0) {
      ElMessage.info('没有发现慢节点')
      return
    }
    
    // 展开包含慢节点的路径
    if (treeRef.value && treeRef.value.store && treeRef.value.store.nodesMap) {
      // 遍历每个慢节点
      for (const key of slowKeys) {
        let currentNode = treeRef.value.store.nodesMap[key]
        
        // 从当前节点向上遍历，展开所有父节点
        while (currentNode && currentNode.parent) {
          currentNode.parent.expanded = true
          currentNode = currentNode.parent
        }
      }
      
      // 强制重新渲染树
      treeRef.value.$forceUpdate()
      ElMessage.success(`已展开${slowKeys.length}个慢节点及其路径`)
    } else {
      ElMessage.warning('无法展开慢节点，请尝试手动展开')
    }
  } catch (error) {
    console.error('展开慢节点失败:', error)
    ElMessage.error('展开慢节点失败')
  }
}

// 高亮选中的函数
const highlightFunction = (func: any) => {
  highlightedId.value = func.id || func.call_id || ''
  
  // 在树中定位并展开到该节点
  if (treeRef.value && (func.id || func.call_id)) {
    // 确保函数调用链标签页是激活的
    activeTab.value = 'calltrace'
    
    // 等待DOM更新后再定位节点
    nextTick(() => {
      if (treeRef.value) {
        try {
          const nodeKey = func.id || func.call_id
          treeRef.value.setCurrentKey(nodeKey)
          
          // 确保节点及其父节点都展开
          let currentNode = treeRef.value.store.nodesMap[nodeKey]
          while (currentNode && currentNode.parent) {
            currentNode.parent.expanded = true
            currentNode = currentNode.parent
          }
          treeRef.value.$forceUpdate()
        } catch (error) {
          console.error('定位节点失败:', error)
        }
      }
    })
  }
}

const getDurationClass = (duration: number) => {
  const ms = duration * 1000
  if (ms < 10) return 'duration-fast'
  if (ms < 50) return 'duration-normal'
  if (ms < 100) return 'duration-slow'
  return 'duration-very-slow'
}

const getShortPath = (path: string) => {
  if (!path) return ''
  const parts = path.split('/')
  return parts.length > 3 ? `.../${parts.slice(-2).join('/')}` : path
}

</script>

<style scoped>
.performance-details {
  min-height: 500px;
}

.basic-info,
.metrics-info,
.environment-info,
.calltrace-info,
.raw-data {
  padding: 20px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.metric-item:last-child {
  border-bottom: none;
}

.metric-label {
  color: #606266;
  font-size: 14px;
}

.metric-value {
  font-weight: bold;
  color: #303133;
  font-size: 16px;
}

.metric-value.large {
  font-size: 20px;
  color: #409eff;
}

.stat-item {
  text-align: center;
  padding: 20px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.raw-data-textarea {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 12px;
}

.raw-data-textarea :deep(.el-textarea__inner) {
  background-color: #f8f9fa;
  color: #495057;
}

/* 慢函数列表样式 */
.slow-functions-card {
  margin-bottom: 20px;
}

.slow-functions-list {
  max-height: 300px;
  overflow-y: auto;
}

.slow-function-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.slow-function-item:hover {
  background: #f5f7fa;
  border-color: #409eff;
}

.function-info {
  flex: 1;
}

.function-name {
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.function-file {
  font-size: 12px;
  color: #909399;
}

.function-duration {
  text-align: right;
  min-width: 120px;
}

.duration-value {
  font-weight: bold;
  color: #f56c6c;
}

.duration-bar {
  width: 100px;
  height: 4px;
  background: #f0f0f0;
  border-radius: 2px;
  margin-top: 4px;
  overflow: hidden;
}

.duration-fill {
  height: 100%;
  background: linear-gradient(90deg, #67c23a, #e6a23c, #f56c6c);
  transition: width 0.3s;
}

.trace-tree-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

/* 调用链树形视图相关样式 */
.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tree-controls {
  display: flex;
  gap: 8px;
}

.trace-tree {
  max-height: 500px;
  overflow-y: auto;
  padding: 8px;
  border-radius: 4px;
  background-color: #fafafa;
}

/* 自定义树形组件样式 */
.custom-tree {
  /* 确保节点间距合适 */
  --el-tree-node-content-height: auto !important;
  --el-tree-node-hover-bg-color: transparent;
}

.custom-tree .el-tree-node__content {
  height: auto !important;
  padding: 8px 0;
  margin-bottom: 4px;
}

.custom-tree .el-tree-node__children {
  padding-left: 16px; /* 增加子节点的缩进距离 */
}

.custom-tree .el-tree-node__expand-icon {
  padding: 8px;
  margin-right: 4px;
  font-size: 14px;
}

.tree-node {
  flex: 1;
  padding: 10px 12px;
  border-radius: 6px;
  transition: all 0.3s ease;
  margin: 3px 0;
  border-left: 3px solid transparent;
  /* 确保内容不会被截断 */
  overflow: visible;
  word-break: break-word;
}

.tree-node:hover {
  background-color: #f0f7ff;
  border-left-color: #409eff;
}

.tree-node.highlighted {
  background: #e6f7ff;
  border-left-color: #409eff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tree-node.slow-node {
  border-left-color: #f56c6c;
}

.tree-node.slow-node:hover {
  background-color: #fff2f0;
}

.node-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start; /* 修改为start而非center，更好处理较长的内容 */
  margin-bottom: 6px;
  flex-wrap: wrap; /* 允许长内容折叠 */
  gap: 8px; /* 内容之间添加间距 */
}

.node-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1; /* 使用flex-grow确保占用可用空间 */
  min-width: 0; /* 允许内容压缩 */
}

.node-name {
  font-weight: 500;
  color: #303133;
  font-family: 'Fira Code', 'Source Code Pro', Menlo, Monaco, Consolas, monospace;
  word-break: break-all; /* 使长函数名能正确折行 */
}

.slow-tag {
  margin-left: 4px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

.node-duration {
  font-weight: bold;
  min-width: 90px;
  text-align: right;
  white-space: nowrap; /* 确保时间不会折行 */
}

.node-details {
  font-size: 12px;
  color: #909399;
  display: flex;
  flex-wrap: wrap; /* 允许折行 */
  gap: 8px;
  background-color: rgba(0, 0, 0, 0.02);
  padding: 5px 8px;
  border-radius: 3px;
  width: 100%; /* 确保可以占满全宽 */
}

.node-file {
  color: #606266;
  flex: 1;
  word-break: break-all; /* 允许路径在任何位置折行 */
  min-width: 100px;
}

.node-line {
  color: #909399;
}

.node-depth {
  color: #b0b0b0;
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
  animation: blink 1.5s infinite;
}

@keyframes blink {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
  100% {
    opacity: 1;
  }
}
</style>
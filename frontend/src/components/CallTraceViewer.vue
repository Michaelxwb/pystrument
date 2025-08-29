<template>
  <div class="call-trace-viewer">
    <div class="trace-header">
      <div class="header-left">
        <h3>函数调用链分析</h3>
        <el-tag type="info" size="small">
          总计 {{ functionCalls.length }} 个函数调用
        </el-tag>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchText"
          placeholder="搜索函数名或文件路径"
          size="small"
          style="width: 250px; margin-right: 12px;"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="sortBy"
          size="small"
          style="width: 120px; margin-right: 12px;"
          @change="sortCalls"
        >
          <el-option label="按时间排序" value="duration" />
          <el-option label="按深度排序" value="depth" />
          <el-option label="按调用顺序" value="order" />
        </el-select>
      </div>
    </div>

    <div class="trace-stats">
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-value">{{ slowFunctions.length }}</div>
            <div class="stat-label">慢函数 (>100ms)</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-value">{{ maxDepth }}</div>
            <div class="stat-label">最大调用深度</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-value">{{ uniqueFiles.size }}</div>
            <div class="stat-label">涉及文件数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-value">{{ totalDuration.toFixed(2) }}ms</div>
            <div class="stat-label">总执行时间</div>
          </div>
        </el-col>
      </el-row>
    </div>

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

    <!-- 调用链树 -->
    <el-card class="trace-tree-card">
      <template #header>
        <div class="tree-header">
          <span>调用链树形视图</span>
          <div class="tree-controls">
            <el-tooltip content="只展开关键节点" placement="top">
              <el-button size="small" type="warning" plain @click="expandSlowNodes">
                <el-icon><Warning /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </div>
      </template>
      <div class="trace-tree">
        <el-tree
          ref="treeRef"
          :data="treeData"
          :props="treeProps"
          :filter-node-method="filterNode"
          :expand-on-click-node="false"
          node-key="id"
          show-checkbox
          @check-change="onNodeCheck"
          class="custom-tree"
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
    </el-card>

    <!-- 详细信息面板 -->
    <el-drawer
      v-model="showDetails"
      title="函数详细信息"
      direction="rtl"
      size="50%"
    >
      <div v-if="selectedFunction" class="function-details">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="函数名">
            {{ selectedFunction.function_name }}
          </el-descriptions-item>
          <el-descriptions-item label="文件路径">
            {{ selectedFunction.file_path }}
          </el-descriptions-item>
          <el-descriptions-item label="行号">
            {{ selectedFunction.line_number || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="调用深度">
            {{ selectedFunction.depth }}
          </el-descriptions-item>
          <el-descriptions-item label="执行时间">
            <span :class="getDurationClass(selectedFunction.duration)">
              {{ (selectedFunction.duration * 1000).toFixed(2) }}ms
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="占总时间比例">
            {{ ((selectedFunction.duration / totalDuration * 1000) * 100).toFixed(2) }}%
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedFunction.children?.length" class="child-functions">
          <h4>子函数调用</h4>
          <el-table :data="selectedFunction.children" size="small">
            <el-table-column prop="function_name" label="函数名" />
            <el-table-column prop="duration" label="耗时" width="100">
              <template #default="{ row }">
                {{ (row.duration * 1000).toFixed(2) }}ms
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, defineProps, defineEmits } from 'vue'
import { ElTree, ElMessage } from 'element-plus'
import { Search, ArrowDown, ArrowUp, Warning } from '@element-plus/icons-vue'
import type { PerformanceRecord, FunctionCall } from '@/types/performance'

// Props
const props = defineProps<{
  record: PerformanceRecord
}>()

// Emits
const emits = defineEmits<{
  close: []
}>()

// 响应式数据
const searchText = ref('')
const sortBy = ref('duration')
const showDetails = ref(false)
const selectedFunction = ref<FunctionCall | null>(null)
const highlightedId = ref('')

// Refs
const treeRef = ref<InstanceType<typeof ElTree>>()

// 计算属性
const functionCalls = computed(() => {
  // 确保有效的function_calls数组
  if (!props.record || !props.record.function_calls || !Array.isArray(props.record.function_calls)) {
    console.warn('无效的function_calls数据:', props.record)
    return []
  }
  
  // 添加id字段，确保每个函数调用都有唯一标识
  return props.record.function_calls.map(call => ({
    ...call,
    id: call.call_id || `${call.function_name}_${call.depth}_${Math.random()}`
  }))
})

const slowFunctions = computed(() => {
  return functionCalls.value
    .filter(call => call.duration > 0.1)
    .sort((a, b) => b.duration - a.duration)
})

const maxDepth = computed(() => {
  return Math.max(...functionCalls.value.map(call => call.depth || 0))
})

const uniqueFiles = computed(() => {
  return new Set(functionCalls.value.map(call => call.file_path))
})

const totalDuration = computed(() => {
  // 使用performance_metrics.total_duration字段的值，转为毫秒单位
  if (props.record && props.record.performance_metrics && props.record.performance_metrics.total_duration !== undefined) {
    return props.record.performance_metrics.total_duration * 1000
  }
  // 回退方案：如果找不到total_duration，则累加所有函数调用的持续时间
  return functionCalls.value.reduce((sum, call) => sum + call.duration, 0) * 1000
})

const maxDuration = computed(() => {
  return Math.max(...functionCalls.value.map(call => call.duration))
})

// 构建树形数据
const treeData = computed(() => {
  const calls = [...functionCalls.value]
  if (calls.length === 0) {
    console.warn('函数调用数据为空')
    return []
  }
  
  console.log('原始函数调用数据:', calls)
  
  // 排序
  if (sortBy.value === 'duration') {
    calls.sort((a, b) => b.duration - a.duration)
  } else if (sortBy.value === 'depth') {
    calls.sort((a, b) => a.depth - b.depth)
  } else { // 'order'
    calls.sort((a, b) => a.call_order - b.call_order)
  }
  
  // 构建树形结构
  const result: any[] = []
  const nodeMap = new Map()
  
  // 首先创建所有节点
  for (const call of calls) {
    const node = {
      ...call,
      id: call.id || call.call_id || `${call.function_name}_${call.depth}_${Math.random()}`,
      children: [],
      highlighted: highlightedId.value === (call.id || call.call_id)
    }
    
    nodeMap.set(node.id, node)
    // 也以call_id往Map中存一份，便于后续查找
    if (call.call_id && call.call_id !== node.id) {
      nodeMap.set(call.call_id, node)
    }
  }
  
  // 然后建立父子关系
  for (const call of calls) {
    const node = nodeMap.get(call.id || call.call_id)
    if (!node) continue
    
    // 有父调用ID的情况
    if (call.parent_call_id) {
      const parentNode = nodeMap.get(call.parent_call_id)
      if (parentNode) {
        if (!parentNode.children.some(child => child.id === node.id)) {
          parentNode.children.push(node)
        }
        continue
      }
    }
    
    // 没有父调用ID或找不到父节点的情况
    // 尝试通过深度判断父子关系
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
        
        const parentNode = nodeMap.get(closestParent.id || closestParent.call_id)
        if (parentNode && !parentNode.children.some(child => child.id === node.id)) {
          parentNode.children.push(node)
        }
      } else {
        // 如果找不到父函数，则放到根节点
        if (!result.some(item => item.id === node.id)) {
          result.push(node)
        }
      }
    }
  }
  
  console.log('生成的树形数据:', result)
  return result
})

const treeProps = {
  children: 'children',
  label: 'function_name'
}

// 方法
const sortCalls = () => {
  // 触发重新计算
}

// 获取所有节点的key
async function getAllKeys() {
  // 如果没有数据，返回空数组
  if (!treeData.value || treeData.value.length === 0) {
    return [];
  }
  
  // 递归获取所有节点的key
  const keys = [];
  
  const getKeys = (nodes) => {
    if (!nodes) return;
    
    for (const node of nodes) {
      if (node.id) {
        keys.push(node.id);
      }
      if (node.children && node.children.length > 0) {
        getKeys(node.children);
      }
    }
  };
  
  getKeys(treeData.value);
  return keys;
}

// 获取所有慢节点的key
async function getSlowNodeKeys() {
  if (!treeData.value || treeData.value.length === 0) {
    return [];
  }
  
  const slowKeys = [];
  
  const findSlowNodes = (nodes) => {
    if (!nodes) return;
    
    for (const node of nodes) {
      if (node.id && node.duration > 0.1) { // 超过100ms的节点认为是慢节点
        slowKeys.push(node.id);
      }
      if (node.children && node.children.length > 0) {
        findSlowNodes(node.children);
      }
    }
  };
  
  findSlowNodes(treeData.value);
  return slowKeys;
}

// 展开所有节点
const expandAll = async () => {
  try {
    const allKeys = await getAllKeys();
    if (allKeys.length === 0) {
      ElMessage.info('没有可展开的节点');
      return;
    }
    
    if (treeRef.value && treeRef.value.setCheckedKeys) {
      // 使用Element Plus的Tree组件内部API
      for (const key of allKeys) {
        treeRef.value.store.nodesMap[key].expanded = true;
      }
      // 强制重新渲染树
      treeRef.value.$forceUpdate();
      ElMessage.success(`已展开${allKeys.length}个节点`);
    } else {
      // 备选方案：使用DOM操作
      const unexpandedNodes = document.querySelectorAll('.el-tree-node:not(.is-expanded) > .el-tree-node__content');
      for (const node of unexpandedNodes) {
        const expandBtn = node.querySelector('.el-tree-node__expand-icon');
        if (expandBtn && !expandBtn.classList.contains('is-leaf')) {
          expandBtn.click();
        }
      }
      ElMessage.success('已展开所有节点');
    }
  } catch (error) {
    console.error('展开所有节点失败:', error);
    ElMessage.error('展开操作失败');
  }
}

// 收起所有节点
const collapseAll = async () => {
  try {
    const allKeys = await getAllKeys();
    if (allKeys.length === 0) {
      ElMessage.info('没有可收起的节点');
      return;
    }
    
    if (treeRef.value && treeRef.value.store && treeRef.value.store.nodesMap) {
      // 使用Element Plus的Tree组件内部API
      for (const key of allKeys) {
        if (treeRef.value.store.nodesMap[key]) {
          treeRef.value.store.nodesMap[key].expanded = false;
        }
      }
      // 强制重新渲染树
      treeRef.value.$forceUpdate();
      ElMessage.success('已收起所有节点');
    } else {
      // 备选方案：使用DOM操作
      const expandedNodes = document.querySelectorAll('.el-tree-node.is-expanded > .el-tree-node__content');
      for (const node of expandedNodes) {
        const expandBtn = node.querySelector('.el-tree-node__expand-icon');
        if (expandBtn && !expandBtn.classList.contains('is-leaf')) {
          expandBtn.click();
        }
      }
      ElMessage.success('已收起所有节点');
    }
  } catch (error) {
    console.error('收起所有节点失败:', error);
    ElMessage.error('收起操作失败');
  }
}

// 只展开慢节点
const expandSlowNodes = async () => {
  try {
    // 先收起所有节点
    await collapseAll();
    
    // 然后获取所有慢节点的key
    const slowKeys = await getSlowNodeKeys();
    
    if (slowKeys.length === 0) {
      ElMessage.info('没有发现慢节点');
      return;
    }
    
    // 展开包含慢节点的路径
    if (treeRef.value && treeRef.value.store && treeRef.value.store.nodesMap) {
      // 遍历每个慢节点
      for (const key of slowKeys) {
        let currentNode = treeRef.value.store.nodesMap[key];
        
        // 从当前节点向上遍历，展开所有父节点
        while (currentNode && currentNode.parent) {
          currentNode.parent.expanded = true;
          currentNode = currentNode.parent;
        }
      }
      
      // 强制重新渲染树
      treeRef.value.$forceUpdate();
      ElMessage.success(`已展开${slowKeys.length}个慢节点及其路径`);
    } else {
      ElMessage.warning('无法展开慢节点，请尝试手动展开');
    }
  } catch (error) {
    console.error('展开慢节点失败:', error);
    ElMessage.error('展开慢节点失败');
  }
}

const highlightFunction = (func: FunctionCall) => {
  highlightedId.value = func.id || ''
  selectedFunction.value = func
  showDetails.value = true
  
  // 在树中定位并展开到该节点
  if (func.id) {
    treeRef.value?.setCurrentKey(func.id)
  }
}

const filterNode = (value: string, data: any) => {
  if (!value) return true
  const searchLower = value.toLowerCase()
  return (
    data.function_name.toLowerCase().includes(searchLower) ||
    data.file_path.toLowerCase().includes(searchLower)
  )
}

const onNodeCheck = (data: any, checked: boolean) => {
  if (checked) {
    highlightFunction(data)
  }
}

const getShortPath = (path: string) => {
  if (!path) return ''
  const parts = path.split('/')
  return parts.length > 3 ? `.../${parts.slice(-2).join('/')}` : path
}

const getDurationClass = (duration: number) => {
  const ms = duration * 1000
  if (ms < 10) return 'duration-fast'
  if (ms < 50) return 'duration-normal'
  if (ms < 100) return 'duration-slow'
  return 'duration-very-slow'
}

// 监听搜索文本变化
watch(searchText, (val) => {
  treeRef.value?.filter(val)
})
</script>

<style scoped>
.call-trace-viewer {
  padding: 20px;
}

.trace-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h3 {
  margin: 0;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
}

.trace-stats {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background: #fafafa;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #606266;
}

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
  max-height: 600px;
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

.function-details {
  padding: 20px;
}

.child-functions {
  margin-top: 20px;
}

.child-functions h4 {
  margin: 0 0 12px 0;
  color: #303133;
}
</style>
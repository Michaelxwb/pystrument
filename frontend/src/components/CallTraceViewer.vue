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
        <el-button size="small" @click="expandAll">全部展开</el-button>
        <el-button size="small" @click="collapseAll">全部折叠</el-button>
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
        <span>调用链树形视图</span>
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
        >
          <template #default="{ node, data }">
            <div class="tree-node" :class="{ 'highlighted': data.highlighted }">
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
                <span class="node-file">{{ getShortPath(data.file_path) }}</span>
                <span v-if="data.line_number" class="node-line">:{{ data.line_number }}</span>
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
import { ElTree } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
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
  return props.record.function_calls || []
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
  return functionCalls.value.reduce((sum, call) => sum + call.duration, 0) * 1000
})

const maxDuration = computed(() => {
  return Math.max(...functionCalls.value.map(call => call.duration))
})

// 构建树形数据
const treeData = computed(() => {
  const calls = [...functionCalls.value]
  
  // 排序
  if (sortBy.value === 'duration') {
    calls.sort((a, b) => b.duration - a.duration)
  } else if (sortBy.value === 'depth') {
    calls.sort((a, b) => a.depth - b.depth)
  }
  
  // 构建树形结构
  const tree: any[] = []
  const nodeMap = new Map()
  
  // 创建节点映射
  calls.forEach(call => {
    const node = {
      ...call,
      id: call.id || `${call.function_name}_${call.depth}_${Math.random()}`,
      children: [],
      highlighted: highlightedId.value === call.id
    }
    nodeMap.set(node.id, node)
  })
  
  // 构建父子关系
  calls.forEach(call => {
    const node = nodeMap.get(call.id || `${call.function_name}_${call.depth}_${Math.random()}`)
    if (call.depth === 0) {
      tree.push(node)
    } else {
      // 找父节点（深度比当前小1的节点）
      const parent = calls.find(parent => 
        parent.depth === call.depth - 1 && 
        calls.indexOf(parent) < calls.indexOf(call)
      )
      if (parent) {
        const parentNode = nodeMap.get(parent.id || `${parent.function_name}_${parent.depth}_${Math.random()}`)
        if (parentNode) {
          parentNode.children.push(node)
        }
      } else {
        tree.push(node)
      }
    }
  })
  
  return tree
})

const treeProps = {
  children: 'children',
  label: 'function_name'
}

// 方法
const sortCalls = () => {
  // 触发重新计算
}

const expandAll = () => {
  treeRef.value?.expandAll()
}

const collapseAll = () => {
  treeRef.value?.collapseAll()
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
}

.trace-tree {
  max-height: 600px;
  overflow-y: auto;
}

.tree-node {
  flex: 1;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.tree-node.highlighted {
  background: #e6f7ff;
  border: 1px solid #409eff;
}

.node-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.node-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-name {
  font-weight: 500;
  color: #303133;
}

.slow-tag {
  margin-left: 4px;
}

.node-duration {
  font-weight: bold;
}

.node-details {
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 8px;
}

.node-file {
  color: #606266;
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
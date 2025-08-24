<template>
  <div class="analysis-results">
    <div class="page-header">
      <h1>AI分析结果</h1>
      <p>查看和管理性能分析结果</p>
    </div>

    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>分析列表</span>
          <div>
            <el-button type="primary" @click="triggerNewAnalysis">
              <el-icon><Plus /></el-icon>
              新建分析
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选条件 -->
      <div class="filter-container">
        <el-form inline>
          <el-form-item label="项目:">
            <el-select v-model="filters.projectKey" placeholder="选择项目" clearable>
              <el-option
                v-for="project in projects"
                :key="project.key"
                :label="project.name"
                :value="project.key"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="状态:">
            <el-select v-model="filters.status" placeholder="选择状态" clearable>
              <el-option label="进行中" value="processing" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
            </el-select>
          </el-form-item>
          <el-form-item label="分析类型:">
            <el-select v-model="filters.analysisType" placeholder="选择类型" clearable>
              <el-option label="AI分析" value="ai_analysis" />
              <el-option label="性能报告" value="performance_report" />
              <el-option label="趋势分析" value="trend_analysis" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="search">搜索</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 分析结果表格 -->
      <el-table :data="analysisResults" style="width: 100%" v-loading="loading">
        <el-table-column prop="projectName" label="项目" width="150" />
        <el-table-column prop="analysisType" label="分析类型" width="120">
          <template #default="scope">
            <el-tag size="small">{{ getAnalysisTypeText(scope.row.analysisType) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)" size="small">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="aiService" label="AI服务" width="100" />
        <el-table-column prop="summary" label="分析摘要" show-overflow-tooltip />
        <el-table-column prop="createdAt" label="创建时间" width="160" />
        <el-table-column prop="completedAt" label="完成时间" width="160" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button 
              type="text" 
              size="small" 
              @click="viewDetail(scope.row)"
              :disabled="scope.row.status !== 'completed'"
            >
              查看详情
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="downloadReport(scope.row)"
              :disabled="scope.row.status !== 'completed'"
            >
              下载报告
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="deleteAnalysis(scope.row)"
              style="color: #f56c6c;"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div style="margin-top: 20px; text-align: center;">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

// 响应式数据
const loading = ref(false)

const filters = ref({
  projectKey: '',
  status: '',
  analysisType: ''
})

const pagination = ref({
  page: 1,
  size: 20,
  total: 0
})

const projects = ref([
  { key: 'proj1', name: '电商系统' },
  { key: 'proj2', name: '用户中心' },
  { key: 'proj3', name: '订单服务' }
])

const analysisResults = ref([
  {
    id: 'analysis_1',
    projectName: '电商系统',
    analysisType: 'ai_analysis',
    status: 'completed',
    aiService: 'OpenAI',
    summary: '发现3个性能瓶颈，建议优化数据库查询',
    createdAt: '2024-01-20 10:30:00',
    completedAt: '2024-01-20 10:35:00'
  },
  {
    id: 'analysis_2',
    projectName: '用户中心',
    analysisType: 'performance_report',
    status: 'processing',
    aiService: 'Local',
    summary: '正在分析中...',
    createdAt: '2024-01-20 11:00:00',
    completedAt: null
  },
  {
    id: 'analysis_3',
    projectName: '订单服务',
    analysisType: 'ai_analysis',
    status: 'failed',
    aiService: 'OpenAI',
    summary: '分析失败：API调用超时',
    createdAt: '2024-01-20 09:15:00',
    completedAt: null
  }
])

onMounted(() => {
  loadAnalysisResults()
})

const loadAnalysisResults = async () => {
  loading.value = true
  try {
    // 这里后续接入真实API
    console.log('加载分析结果')
    await new Promise(resolve => setTimeout(resolve, 1000))
    pagination.value.total = 50
  } catch (error) {
    console.error('加载分析结果失败:', error)
    ElMessage.error('加载分析结果失败')
  } finally {
    loading.value = false
  }
}

const getAnalysisTypeText = (type: string) => {
  const types: Record<string, string> = {
    'ai_analysis': 'AI分析',
    'performance_report': '性能报告',
    'trend_analysis': '趋势分析'
  }
  return types[type] || type
}

const getStatusText = (status: string) => {
  const statusTexts: Record<string, string> = {
    'processing': '进行中',
    'completed': '已完成',
    'failed': '失败'
  }
  return statusTexts[status] || status
}

const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    'processing': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return types[status] || 'info'
}

const search = () => {
  pagination.value.page = 1
  loadAnalysisResults()
}

const resetFilters = () => {
  filters.value = {
    projectKey: '',
    status: '',
    analysisType: ''
  }
  search()
}

const handleSizeChange = (size: number) => {
  pagination.value.size = size
  loadAnalysisResults()
}

const handleCurrentChange = (page: number) => {
  pagination.value.page = page
  loadAnalysisResults()
}

const triggerNewAnalysis = () => {
  ElMessage.info('新建分析功能正在开发中')
}

const viewDetail = (row: any) => {
  router.push(`/analysis/${row.id}`)
}

const downloadReport = (row: any) => {
  ElMessage.info('下载报告功能正在开发中')
}

const deleteAnalysis = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个分析结果吗？此操作不可恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里后续接入真实API
    console.log('删除分析结果:', row.id)
    ElMessage.success('删除成功')
    loadAnalysisResults()
  } catch {
    // 用户取消删除
  }
}
</script>

<style lang="scss" scoped>
.analysis-results {
  .page-header {
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
  
  .filter-container {
    margin-bottom: 20px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
    
    .el-form {
      margin-bottom: 0;
    }
  }
}
</style>
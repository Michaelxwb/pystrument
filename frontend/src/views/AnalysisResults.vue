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
            <el-switch
              v-model="autoRefresh"
              active-text="自动刷新"
              @change="toggleAutoRefresh"
              style="margin-right: 15px;"
            />
            <el-button type="primary" @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
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
            <el-dropdown @command="(cmd) => handleDownloadCommand(scope.row, cmd)" trigger="click">
              <el-button 
                type="text" 
                size="small" 
                :disabled="scope.row.status !== 'completed'"
              >
                下载报告
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="json">JSON格式</el-dropdown-item>
                  <el-dropdown-item command="pdf">PDF格式</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
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
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { analysisApi } from '@/api/analysis'
import { projectApi } from '@/api/project'
import { http } from '@/utils/request'
import { generateAnalysisReportPDF } from '@/utils/reportGenerator'
import type { AnalysisRecord } from '@/types/analysis'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const projects = ref<Array<{key: string, name: string}>>([])
const analysisResults = ref<any[]>([])

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

// 自动刷新相关
const autoRefresh = ref(true)
const refreshInterval = ref<number | null>(null)
const refreshRate = 30000 // 30秒刷新一次

onMounted(async () => {
  await loadProjects()
  await loadAnalysisResults()
  
  // 设置自动刷新
  startAutoRefresh()
})

// 监听筛选条件变化
watch([() => filters.value.projectKey, () => filters.value.status, () => filters.value.analysisType], 
  () => {
    // 当筛选条件变化时，重置页码并重新加载数据
    pagination.value.page = 1
    loadAnalysisResults()
  }
)

const loadProjects = async () => {
  try {
    const response = await projectApi.getProjects()
    projects.value = response.data.projects.map(project => ({
      key: project.project_key,
      name: project.name
    }))
  } catch (error) {
    console.error('加载项目列表失败:', error)
    ElMessage.error('加载项目列表失败')
  }
}

const loadAnalysisResults = async () => {
  loading.value = true
  try {
    console.log('正在加载分析结果数据...')
    
    // 准备查询参数
    const params: any = {
      page: pagination.value.page,
      size: pagination.value.size
    }
    
    if (filters.value.status) {
      params.status = filters.value.status
    }
    
    if (filters.value.analysisType) {
      params.analysis_type = filters.value.analysisType
    }
    
    let response
    
    // 根据是否选择了项目，调用不同的API
    if (filters.value.projectKey) {
      response = await analysisApi.getAnalysisHistory(filters.value.projectKey, params)
    } else {
      // 调用获取所有项目分析记录的API
      response = await http.get('/v1/analysis/history', params)
    }
    
    // 处理响应数据
    const data = response.data
    
    // 更新分析结果和分页信息
    analysisResults.value = data.records.map((record: AnalysisRecord) => ({
      id: record.analysis_id,
      projectKey: record.project_key,
      projectName: record.project_name || '未知项目',
      analysisType: record.analysis_type || 'ai_analysis',
      status: convertStatus(record.status),
      aiService: record.ai_service,
      summary: record.results?.summary || getStatusSummary(record.status),
      createdAt: record.created_at,
      completedAt: record.updated_at
    }))
    
    pagination.value.total = data.total
    
    console.log(`成功加载${analysisResults.value.length}条分析结果数据`)
  } catch (error) {
    console.error('加载分析结果失败:', error)
    ElMessage.error('加载分析结果失败')
  } finally {
    loading.value = false
  }
}

// 状态转换函数，将后端状态转换为前端状态
const convertStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    'PENDING': 'processing',
    'IN_PROGRESS': 'processing',
    'COMPLETED': 'completed',
    'FAILURE': 'failed',
    'CANCELED': 'failed'
  }
  return statusMap[status] || status.toLowerCase()
}

// 根据状态获取摘要文本
const getStatusSummary = (status: string): string => {
  const summaryMap: Record<string, string> = {
    'PENDING': '等待分析...',
    'IN_PROGRESS': '正在分析中...',
    'FAILURE': '分析失败',
    'CANCELED': '分析已取消'
  }
  return summaryMap[status] || '未知状态'
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
}

const handleSizeChange = (size: number) => {
  pagination.value.size = size
  loadAnalysisResults()
}

const handleCurrentChange = (page: number) => {
  pagination.value.page = page
  loadAnalysisResults()
}

// 自动刷新相关方法
const startAutoRefresh = () => {
  if (autoRefresh.value && !refreshInterval.value) {
    console.log('启动自动刷新, 间隔:', refreshRate, 'ms')
    refreshInterval.value = window.setInterval(() => {
      console.log('自动刷新分析结果数据')
      loadAnalysisResults()
    }, refreshRate)
  }
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    console.log('停止自动刷新')
    window.clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

const toggleAutoRefresh = () => {
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const refreshData = () => {
  loadAnalysisResults()
}

// 组件卸载时清除定时器
onUnmounted(() => {
  stopAutoRefresh()
})

const triggerNewAnalysis = () => {
  ElMessage.info('新建分析功能正在开发中')
}

const viewDetail = async (row: any) => {
  try {
    loading.value = true
    console.log('查看分析详情:', row.id)
    
    // 获取分析详情数据
    const response = await analysisApi.getAnalysisResult(row.id)
    
    if (response.data) {
      // 导航到分析详情页面，并传递分析数据
      router.push({
        path: `/analysis/${row.id}`,
        query: { 
          from: 'analysis-list',
          projectName: row.projectName 
        }
      })
    } else {
      ElMessage.warning('未找到分析详情')
    }
  } catch (error) {
    console.error('获取分析详情失败:', error)
    ElMessage.error('获取分析详情失败')
  } finally {
    loading.value = false
  }
}

const downloadReport = async (row: any, format: 'json' | 'pdf' = 'json') => {
  try {
    loading.value = true
    console.log(`下载${format.toUpperCase()}格式分析报告:`, row.id)
    
    // 获取分析详情数据
    const response = await analysisApi.getAnalysisResult(row.id)
    console.log('分析结果数据:', response.data);
    
    if (response.data && response.data.results) {
      if (format === 'pdf') {
        try {
          // 确保响应数据符合AnalysisRecord类型
          // 修正可能缺失的字段，确保pdf生成不会失败
          const analysisRecord = {
            ...response.data,
            results: {
              ...response.data.results,
              // 确保bottlenecks和recommendations字段是数组
              bottlenecks: Array.isArray(response.data.results.bottlenecks) 
                ? response.data.results.bottlenecks 
                : [],
              recommendations: Array.isArray(response.data.results.recommendations) 
                ? response.data.results.recommendations 
                : []
            }
          };
          
          console.log('处理后的分析数据:', analysisRecord);
          
          // 生成PDF报告
          await generateAnalysisReportPDF(analysisRecord, row.projectName || '未知项目')
          ElMessage.success('PDF报告生成并下载成功')
        } catch (error) {
          console.error('生成PDF报告失败:', error);
          ElMessage.error(`PDF报告生成失败: ${error instanceof Error ? error.message : '未知错误'}`);
        }
      } else {
        // 导出JSON报告逻辑
        const reportData = {
          performance_score: response.data.results.performance_score,
          bottlenecks: response.data.results.bottlenecks,
          suggestions: response.data.results.recommendations ? response.data.results.recommendations.map((item: string, index: number) => ({
            priority: index < 1 ? 'high' : index < 3 ? 'medium' : 'low',
            title: item,
            description: item,
            category: 'general'
          })) : [],
          risks: {
            current_risks: [],
            potential_issues: [],
            recommendations: []
          },
          analysis_time: response.data.created_at
        }
        
        const blob = new Blob([JSON.stringify(reportData, null, 2)], {
          type: 'application/json'
        })
        
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `分析报告_${row.projectName || row.projectKey}_${row.id.substring(0, 8)}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        
        ElMessage.success('JSON报告导出成功')
      }
    } else {
      ElMessage.warning('分析报告数据不完整，无法下载')
    }
  } catch (error) {
    console.error('下载分析报告失败:', error)
    ElMessage.error('下载分析报告失败')
  } finally {
    loading.value = false
  }
}

const handleDownloadCommand = (row: any, command: 'json' | 'pdf') => {
  downloadReport(row, command)
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
    
    loading.value = true
    console.log('删除分析结果:', row.id)
    
    try {
      // 调用删除API
      await http.delete(`/v1/analysis/result/${row.id}`)
      
      ElMessage.success('删除成功')
      
      // 重新加载数据
      await loadAnalysisResults()
    } catch (error) {
      console.error('删除分析结果失败:', error)
      ElMessage.error('删除分析结果失败')
    } finally {
      loading.value = false
    }
  } catch {
    // 用户取消删除
    console.log('用户取消删除操作')
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
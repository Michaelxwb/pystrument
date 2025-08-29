<template>
  <div class="analysis-results">
    <div class="page-header">
      <div class="header-left">
        <span class="title">AI分析结果</span>
        <span class="subtitle">查看和管理所有AI分析报告</span>
      </div>
      <div class="header-actions">
        <el-tooltip content="刷新数据" placement="top">
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-tooltip>
        <el-button type="primary" @click="triggerNewAnalysis">
          <el-icon><Plus /></el-icon>
          新建分析
        </el-button>
      </div>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-title">
            <el-icon><Document /></el-icon>
            <span>分析列表</span>
          </div>
          <div class="card-actions">
            <el-switch
              v-model="autoRefresh"
              active-text="自动刷新"
              @change="toggleAutoRefresh"
            />
          </div>
        </div>
      </template>

      <!-- 筛选条件 -->
      <div class="filter-container">
        <el-form :model="filters" inline>
          <el-form-item label="项目:">
            <el-select 
              v-model="filters.projectKey" 
              placeholder="选择项目" 
              clearable 
              style="width: auto; min-width: 150px;"
              @change="handleFilterChange"
            >
              <el-option
                v-for="project in projects"
                :key="project.key"
                :label="project.name"
                :value="project.key"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="状态:">
            <el-select 
              v-model="filters.status" 
              placeholder="选择状态" 
              clearable 
              style="width: auto; min-width: 120px;"
              @change="handleFilterChange"
            >
              <el-option label="进行中" value="processing" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
            </el-select>
          </el-form-item>
          <el-form-item label="分析类型:">
            <el-select 
              v-model="filters.analysisType" 
              placeholder="选择类型" 
              clearable 
              style="width: auto; min-width: 120px;"
              @change="handleFilterChange"
            >
              <el-option label="AI分析" value="ai_analysis" />
              <el-option label="性能报告" value="performance_report" />
              <el-option label="趋势分析" value="trend_analysis" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="search">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="resetFilters">
              <el-icon><RefreshRight /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 分析结果表格 -->
      <el-table 
        :data="analysisResults" 
        style="width: 100%" 
        v-loading="loading"
        stripe
        border
        highlight-current-row
        :empty-text="'暂无分析数据'"
        :header-cell-style="{backgroundColor: '#f5f7fa', color: '#606266'}"
      >
        <el-table-column prop="projectName" label="项目" width="150" show-overflow-tooltip>
          <template #default="scope">
            <el-tooltip :content="scope.row.projectName" placement="top">
              <span>{{ scope.row.projectName }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="analysisType" label="分析类型" width="120">
          <template #default="scope">
            <el-tag size="small">{{ getAnalysisTypeText(scope.row.analysisType) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)" size="small" effect="dark">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="aiService" label="AI服务" width="100" />
        <el-table-column prop="summary" label="分析摘要" show-overflow-tooltip>
          <template #default="scope">
            <el-tooltip :content="scope.row.summary" placement="top">
              <span>{{ scope.row.summary || '暂无摘要' }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="160" sortable>
          <template #default="scope">
            <el-tooltip :content="formatFullDateTime(scope.row.createdAt)" placement="top">
              <span>{{ formatDateTime(scope.row.createdAt) }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="completedAt" label="完成时间" width="160" sortable>
          <template #default="scope">
            <template v-if="scope.row.status === 'completed' && scope.row.completedAt">
              <el-tooltip :content="formatFullDateTime(scope.row.completedAt)" placement="top">
                <span>{{ formatDateTime(scope.row.completedAt) }}</span>
              </el-tooltip>
            </template>
            <template v-else>
              <span class="text-muted">未完成</span>
            </template>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="viewDetail(scope.row)"
              :disabled="scope.row.status !== 'completed'"
              circle
            >
              <el-icon><View /></el-icon>
            </el-button>
            <el-dropdown @command="(cmd) => handleDownloadCommand(scope.row, cmd)" trigger="click">
              <el-button 
                type="success" 
                size="small" 
                :disabled="scope.row.status !== 'completed'"
                circle
              >
                <el-icon><Download /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="json">JSON格式</el-dropdown-item>
                  <el-dropdown-item command="pdf">PDF格式</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button 
              type="danger" 
              size="small" 
              @click="deleteAnalysis(scope.row)"
              circle
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          background
          small
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Refresh, 
  Search, 
  RefreshRight, 
  View, 
  Download, 
  Delete,
  Document
} from '@element-plus/icons-vue'
import { analysisApi } from '@/api/analysis'
import { projectApi } from '@/api/project'
import { http } from '@/utils/request'
import { generateAnalysisReportPDF } from '@/utils/reportGenerator'
import { formatDateTime, formatFullDateTime } from '@/utils/dateUtils'
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
  size: 10,
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
    const params = {
      page: pagination.value.page,
      size: pagination.value.size,
      status: filters.value.status || undefined,
      analysis_type: filters.value.analysisType || undefined
    }
    
    // 使用获取所有分析历史的方法
    const response = await analysisApi.getAllAnalysisHistory(params)
    
    analysisResults.value = response.data.records.map((item: any) => {
      // 状态映射：将后端返回的大写状态转换为前端所需的小写状态
      // 修复状态映射，确保处理所有可能的后端状态值
      const statusMap: Record<string, string> = {
        'PENDING': 'pending',
        'IN_PROGRESS': 'processing',
        'COMPLETED': 'completed',
        'SUCCESS': 'completed', // 添加对SUCCESS状态的处理
        'FAILURE': 'failed',
        'CANCELED': 'failed',
        'FAILED': 'failed' // 添加对FAILED状态的处理
      };
      
      // 确保正确提取analysis_id
      const analysisId = item.analysis_id || item.id || item._id;
      
      // 正确提取摘要信息
      let summaryText = '';
      if (item.results) {
        // 尝试从不同字段获取摘要信息
        if (item.results.summary) {
          summaryText = item.results.summary;
        } else if (item.results.bottleneck_analysis && item.results.bottleneck_analysis.length > 0) {
          // 如果没有摘要但有瓶颈分析，使用第一个瓶颈分析的描述作为摘要
          summaryText = `发现${item.results.bottleneck_analysis.length}个性能瓶颈，包括${item.results.bottleneck_analysis[0].type}问题`;
        } else if (item.results.optimization_suggestions && item.results.optimization_suggestions.length > 0) {
          // 如果没有摘要但有优化建议，使用第一个优化建议的标题作为摘要
          summaryText = `提供${item.results.optimization_suggestions.length}个优化建议，包括${item.results.optimization_suggestions[0].title}`;
        } else if (item.results.performance_score) {
          // 如果只有性能评分，使用评分作为摘要
          summaryText = `性能评分: ${item.results.performance_score}分`;
        }
      }
      
      return {
        id: analysisId,
        analysis_id: analysisId,  // 同时保留analysis_id字段
        ...item,
        projectName: item.project_name || item.projectKey || '未知项目',
        analysisType: item.analysis_type || 'ai_analysis',
        status: statusMap[item.status] || 'pending', // 使用状态映射
        aiService: item.ai_service || 'default',
        summary: summaryText || item.summary || '暂无摘要',
        createdAt: item.created_at || '',
        // 修复完成时间字段映射，使用updated_at作为completedAt的值
        completedAt: item.completed_at || item.updated_at || ''
      };
    })
    
    pagination.value.total = response.data.total
  } catch (error) {
    console.error('加载分析结果失败:', error)
    ElMessage.error('加载分析结果失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  // 筛选条件变化时自动触发搜索
  pagination.value.page = 1
  loadAnalysisResults()
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
  pagination.value.page = 1
  loadAnalysisResults()
}

const handleSizeChange = (size: number) => {
  pagination.value.size = size
  pagination.value.page = 1
  loadAnalysisResults()
}

const handleCurrentChange = (page: number) => {
  pagination.value.page = page
  loadAnalysisResults()
}

const startAutoRefresh = () => {
  if (refreshInterval.value) {
    stopAutoRefresh()
  }
  
  console.log('启动自动刷新，间隔:', refreshRate, 'ms')
  refreshInterval.value = window.setInterval(() => {
    console.log('自动刷新分析结果数据')
    loadAnalysisResults()
  }, refreshRate)
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
  ElMessage.success('数据刷新成功')
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
    // 确保使用正确的分析ID
    const analysisId = row.analysis_id || row.id || row._id;
    console.log('查看分析详情:', analysisId)
    
    if (!analysisId) {
      ElMessage.error('分析ID无效')
      return
    }
    
    // 获取分析详情数据
    const response = await analysisApi.getAnalysisResult(analysisId)
    
    if (response.data) {
      // 导航到分析详情页面，并传递分析数据
      router.push({
        path: `/analysis/${analysisId}`,
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
    // 确保使用正确的分析ID
    const analysisId = row.analysis_id || row.id || row._id;
    console.log(`下载${format.toUpperCase()}格式分析报告:`, analysisId)
    
    if (!analysisId) {
      ElMessage.error('分析ID无效')
      return
    }
    
    // 获取分析详情数据
    const response = await analysisApi.getAnalysisResult(analysisId)
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
              // 确保bottleneck_analysis和optimization_suggestions字段是数组
              bottleneck_analysis: Array.isArray(response.data.results.bottleneck_analysis) 
                ? response.data.results.bottleneck_analysis 
                : [],
              optimization_suggestions: Array.isArray(response.data.results.optimization_suggestions) 
                ? response.data.results.optimization_suggestions 
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
        // 使用后端原始字段名称保持一致性
        const reportData = {
          performance_score: response.data.results.performance_score,
          bottleneck_analysis: response.data.results.bottleneck_analysis || [],
          optimization_suggestions: response.data.results.optimization_suggestions || [],
          risk_assessment: response.data.results.risk_assessment || {
            current_risks: [],
            potential_issues: [],
            recommendations: []
          },
          summary: response.data.results.summary || '',
          analysis_time: response.data.created_at
        }
        
        const blob = new Blob([JSON.stringify(reportData, null, 2)], {
          type: 'application/json'
        })
        
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `分析报告_${row.projectName || row.projectKey}_${analysisId.substring(0, 8)}.json`
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
    // 确保使用正确的分析ID
    const analysisId = row.analysis_id || row.id || row._id;
    console.log('删除分析结果:', analysisId)
    
    if (!analysisId) {
      ElMessage.error('分析ID无效')
      loading.value = false
      return
    }
    
    try {
      // 调用删除API
      await http.delete(`/v1/analysis/result/${analysisId}`)
      
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
    loading.value = false
  }
}

// 辅助方法
const getAnalysisTypeText = (type: string) => {
  switch (type) {
    case 'ai_analysis': return 'AI分析'
    case 'performance_report': return '性能报告'
    case 'trend_analysis': return '趋势分析'
    default: return '未知类型'
  }
}

const getStatusTagType = (status: string) => {
  switch (status) {
    case 'pending': return 'info'
    case 'processing': return 'warning'
    case 'completed': return 'success'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'pending': return '待处理'
    case 'processing': return '处理中'
    case 'completed': return '已完成'
    case 'failed': return '失败'
    default: return '未知'
  }
}
</script>

<style lang="scss" scoped>
.analysis-results {
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
      align-items: center;
      gap: 16px;
    }
  }
  
  .filter-container {
    margin-bottom: 20px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
    
    .el-form {
      margin-bottom: 0;
      
      .el-form-item {
        margin-bottom: 0;
        margin-right: 15px;
      }
    }
  }
  
  .pagination-wrapper {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
}
</style>
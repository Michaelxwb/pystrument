<template>
  <div class="ai-analysis">
    <div class="page-header">
      <div class="header-left">
        <el-button
          type="text"
          @click="goBack"
          style="padding: 0; margin-right: 16px;"
        >
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h2>AI性能分析报告</h2>
        <span v-if="projectName" class="project-name">{{ projectName }}</span>
      </div>
      <div class="header-actions">
        <el-button
          v-if="!analysisData"
          type="primary"
          @click="triggerAnalysis"
          :loading="analyzing"
        >
          <el-icon><MagicStick /></el-icon>
          开始分析
        </el-button>
        <el-dropdown v-else @command="handleExportCommand" trigger="click">
          <el-button type="success">
            <el-icon><Download /></el-icon>
            导出报告
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="json">JSON格式</el-dropdown-item>
              <el-dropdown-item command="pdf">PDF格式</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 分析进行中 -->
    <div v-else-if="analyzing" class="analyzing-container">
      <el-card>
        <div class="analyzing-content">
          <el-icon class="analyzing-icon"><Loading /></el-icon>
          <h3>AI正在分析性能数据...</h3>
          <p>预计需要 1-2 分钟，请耐心等待</p>
          <el-progress
            :percentage="analyzeProgress"
            :format="formatProgress"
            style="margin-top: 20px;"
          />
        </div>
      </el-card>
    </div>

    <!-- 分析结果 -->
    <div v-else-if="analysisData" class="analysis-results">
      <!-- 性能评分卡片 -->
      <div class="score-section">
        <el-card>
          <div class="score-content">
            <div class="score-main">
              <div class="score-value">{{ analysisData.performance_score }}</div>
              <div class="score-label">性能评分</div>
              <div class="score-level" :class="getScoreLevel(analysisData.performance_score)">
                {{ getScoreLevelText(analysisData.performance_score) }}
              </div>
            </div>
            <div class="score-chart">
              <div ref="scoreChartRef" style="width: 200px; height: 200px;"></div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 瓶颈分析 -->
      <div class="bottleneck-section">
        <el-card>
          <template #header>
            <div class="section-header">
              <el-icon><Warning /></el-icon>
              <span>性能瓶颈分析</span>
              <el-tag :type="getBottleneckSeverityType()" size="small">
                发现 {{ analysisData.bottleneck_analysis?.length || 0 }} 个瓶颈
              </el-tag>
            </div>
          </template>
          
          <div v-if="!analysisData.bottleneck_analysis?.length" class="no-bottlenecks">
            <el-icon><SuccessFilled /></el-icon>
            <p>恭喜！未发现明显的性能瓶颈</p>
          </div>
          
          <div v-else class="bottleneck-list">
            <div
              v-for="(bottleneck, index) in analysisData.bottleneck_analysis"
              :key="index"
              class="bottleneck-item"
            >
              <div class="bottleneck-header">
                <el-tag
                  :type="getSeverityTagType(bottleneck.severity)"
                  size="small"
                >
                  {{ getSeverityText(bottleneck.severity) }}
                </el-tag>
                <span class="bottleneck-type">{{ getBottleneckTypeText(bottleneck.type) }}</span>
                <span class="bottleneck-impact">影响程度: {{ (bottleneck.impact * 100).toFixed(1) }}%</span>
              </div>
              <div class="bottleneck-description">
                {{ bottleneck.description }}
              </div>
              <div v-if="bottleneck.function" class="bottleneck-function">
                相关函数: <code>{{ bottleneck.function }}</code>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 优化建议 -->
      <div class="optimization-section">
        <el-card>
          <template #header>
            <div class="section-header">
              <el-icon><Bulb /></el-icon>
              <span>优化建议</span>
              <el-tag type="primary" size="small">
                {{ analysisData.optimization_suggestions?.length || 0 }} 条建议
              </el-tag>
            </div>
          </template>
          
          <div v-if="!analysisData.optimization_suggestions?.length" class="no-suggestions">
            <el-icon><InfoFilled /></el-icon>
            <p>当前性能表现良好，暂无特殊优化建议</p>
          </div>
          
          <div v-else class="suggestions-list">
            <el-collapse v-model="activeSuggestions">
              <el-collapse-item
                v-for="(suggestion, index) in analysisData.optimization_suggestions"
                :key="index"
                :name="index"
              >
                <template #title>
                  <div class="suggestion-title">
                    <el-tag
                      :type="getPriorityTagType(suggestion.priority)"
                      size="small"
                    >
                      {{ getPriorityText(suggestion.priority) }}
                    </el-tag>
                    <span>{{ suggestion.title }}</span>
                    <span class="suggestion-category">{{ getCategoryText(suggestion.category) }}</span>
                  </div>
                </template>
                
                <div class="suggestion-content">
                  <div class="suggestion-description">
                    {{ suggestion.description }}
                  </div>
                  
                  <div v-if="suggestion.code_example" class="suggestion-code">
                    <h4>代码示例:</h4>
                    <el-input
                      v-model="suggestion.code_example"
                      type="textarea"
                      :rows="6"
                      readonly
                      class="code-textarea"
                    />
                  </div>
                  
                  <div v-if="suggestion.expected_improvement" class="suggestion-improvement">
                    <el-tag type="success" size="small">
                      预期效果: {{ suggestion.expected_improvement }}
                    </el-tag>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-card>
      </div>

      <!-- 风险评估 -->
      <div class="risk-section">
        <el-card>
          <template #header>
            <div class="section-header">
              <el-icon><Shield /></el-icon>
              <span>风险评估</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="risk-category">
                <h4>当前风险</h4>
                <div v-if="!analysisData.risk_assessment?.current_risks?.length" class="no-risks">
                  <el-icon color="#67c23a"><SuccessFilled /></el-icon>
                  <span>暂无明显风险</span>
                </div>
                <ul v-else class="risk-list">
                  <li
                    v-for="(risk, index) in analysisData.risk_assessment.current_risks"
                    :key="index"
                    class="risk-item current-risk"
                  >
                    {{ risk }}
                  </li>
                </ul>
              </div>
            </el-col>
            
            <el-col :span="8">
              <div class="risk-category">
                <h4>潜在问题</h4>
                <div v-if="!analysisData.risk_assessment?.potential_issues?.length" class="no-risks">
                  <el-icon color="#67c23a"><SuccessFilled /></el-icon>
                  <span>暂无潜在问题</span>
                </div>
                <ul v-else class="risk-list">
                  <li
                    v-for="(issue, index) in analysisData.risk_assessment.potential_issues"
                    :key="index"
                    class="risk-item potential-issue"
                  >
                    {{ issue }}
                  </li>
                </ul>
              </div>
            </el-col>
            
            <el-col :span="8">
              <div class="risk-category">
                <h4>建议措施</h4>
                <div v-if="!analysisData.risk_assessment?.recommendations?.length" class="no-risks">
                  <el-icon color="#909399"><InfoFilled /></el-icon>
                  <span>暂无特殊建议</span>
                </div>
                <ul v-else class="risk-list">
                  <li
                    v-for="(recommendation, index) in analysisData.risk_assessment.recommendations"
                    :key="index"
                    class="risk-item recommendation"
                  >
                    {{ recommendation }}
                  </li>
                </ul>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </div>

      <!-- 分析元信息 -->
      <div class="metadata-section">
        <el-card>
          <template #header>
            <span>分析信息</span>
          </template>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="分析时间">
              {{ formatDateTime(analysisRecord?.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="完成时间">
              {{ formatDateTime(analysisRecord?.completed_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="AI服务">
              {{ analysisRecord?.ai_service || 'default' }}
            </el-descriptions-item>
            <el-descriptions-item label="分析状态">
              <el-tag
                :type="getStatusTagType(analysisRecord?.status)"
                size="small"
              >
                {{ getStatusText(analysisRecord?.status) }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <el-card>
        <div class="error-content">
          <el-icon class="error-icon"><Close /></el-icon>
          <h3>分析失败</h3>
          <p>{{ error }}</p>
          <el-button type="primary" @click="retryAnalysis">重试分析</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  MagicStick,
  Download,
  Loading,
  Warning,
  MagicStick as Bulb,
  WarnTriangleFilled as Shield,
  SuccessFilled,
  InfoFilled,
  Close
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { analysisApi } from '@/api/analysis'
import { projectApi } from '@/api/project'
import type { AnalysisRecord, AnalysisResults } from '@/types/analysis'
import { generateAnalysisReportPDF } from '@/utils/reportGenerator'

// 定义组件名称
defineOptions({
  name: 'AIAnalysis'
})

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const analyzing = ref(false)
const analyzeProgress = ref(0)
const error = ref('')
const analysisData = ref<any | null>(null)
const analysisRecord = ref<AnalysisRecord | null>(null)
const activeSuggestions = ref<number[]>([])
const projectName = ref('')

// 图表引用
const scoreChartRef = ref<HTMLElement>()
let scoreChart: echarts.ECharts | null = null

// 获取路由参数
const performanceRecordId = computed(() => route.params.id as string)
const fromAnalysisList = computed(() => route.query.from === 'analysis-list')

// 方法
const loadAnalysisData = async () => {
  loading.value = true
  try {
    // 从路由查询参数获取项目名称
    if (route.query.projectName) {
      projectName.value = route.query.projectName as string
    }
    
    // 如果是从分析列表页面跳转过来，直接获取分析结果
    if (fromAnalysisList.value) {
      const response = await analysisApi.getAnalysisResult(performanceRecordId.value)
      
      if (response.data) {
        analysisRecord.value = response.data
        
        // 处理分析结果，确保数据格式一致
        if (response.data.results) {
          analysisData.value = {
            performance_score: response.data.results.performance_score,
            bottleneck_analysis: response.data.results.bottlenecks || [],
            optimization_suggestions: response.data.results.recommendations ? response.data.results.recommendations.map((item: string, index: number) => ({
              priority: index < 1 ? 'high' : index < 3 ? 'medium' : 'low',
              title: item,
              description: item,
              category: 'general'
            })) : [],
            risk_assessment: {
              current_risks: [],
              potential_issues: [],
              recommendations: []
            },
            summary: response.data.results.summary
          }
        }
        
        // 如果有项目信息，更新项目名称
        if (response.data.project_key && !projectName.value) {
          try {
            const projectResponse = await projectApi.getProjectDetail(response.data.project_key)
            if (projectResponse.data) {
              projectName.value = projectResponse.data.name
            }
          } catch (err) {
            console.log('获取项目信息失败', err)
          }
        }
        
        if (analysisData.value) {
          await nextTick()
          initScoreChart()
        }
      }
    } else {
      // 查找已存在的分析记录
      try {
        // 构造分析ID并尝试获取结果
        const analysisId = performanceRecordId.value
        if (analysisId.startsWith('analysis_')) {
          const response = await analysisApi.getAnalysisResult(analysisId)
          
          if (response.data) {
            analysisRecord.value = response.data
            analysisData.value = response.data.results || null
            
            // 如果有项目信息，更新项目名称
            if (response.data.project_key && !projectName.value) {
              try {
                const projectResponse = await projectApi.getProjectDetail(response.data.project_key)
                if (projectResponse.data) {
                  projectName.value = projectResponse.data.name
                }
              } catch (err) {
                console.log('获取项目信息失败', err)
              }
            }
            
            if (analysisData.value) {
              await nextTick()
              initScoreChart()
            }
          }
        }
      } catch (err) {
        console.log('未找到现有分析结果，可能需要触发新分析')
      }
    }
  } catch (error) {
    console.error('加载分析数据失败:', error)
  } finally {
    loading.value = false
  }
}

const triggerAnalysis = async () => {
  analyzing.value = true
  analyzeProgress.value = 0
  error.value = ''
  
  try {
    const response = await analysisApi.triggerAnalysis(performanceRecordId.value, {
      ai_service: 'default',
      priority: 'normal'
    })
    
    const taskId = response.data.task_id
    
    // 轮询任务状态
    const pollStatus = async () => {
      try {
        const statusResponse = await analysisApi.getTaskStatus(taskId)
        const status = statusResponse.data
        
        if (status.progress) {
          analyzeProgress.value = status.progress
        }
        
        if (status.status === 'SUCCESS') {
          analyzing.value = false
          ElMessage.success('AI分析完成')
          // 获取分析结果
          if (status.analysis_id) {
            const resultResponse = await analysisApi.getAnalysisResult(status.analysis_id)
            if (resultResponse.data) {
              analysisRecord.value = resultResponse.data
              
              // 处理分析结果，确保数据格式一致
              if (resultResponse.data.results) {
                analysisData.value = {
                  performance_score: resultResponse.data.results.performance_score,
                  bottleneck_analysis: resultResponse.data.results.bottlenecks || [],
                  optimization_suggestions: resultResponse.data.results.recommendations ? resultResponse.data.results.recommendations.map((item: string, index: number) => ({
                    priority: index < 1 ? 'high' : index < 3 ? 'medium' : 'low',
                    title: item,
                    description: item,
                    category: 'general'
                  })) : [],
                  risk_assessment: {
                    current_risks: [],
                    potential_issues: [],
                    recommendations: []
                  },
                  summary: resultResponse.data.results.summary
                }
              }
              
              if (analysisData.value) {
                await nextTick()
                initScoreChart()
              }
            }
          }
        } else if (status.status === 'FAILURE' || status.status === 'CANCELED') {
          analyzing.value = false
          error.value = status.error || '分析失败'
          ElMessage.error('AI分析失败')
        } else {
          // 继续轮询
          setTimeout(pollStatus, 2000) // 2秒后再检查
        }
      } catch (error) {
        console.error('检查分析状态失败:', error)
        analyzing.value = false
        error.value = '检查分析状态失败'
        ElMessage.error('检查分析状态失败')
      }
    }
    
    setTimeout(pollStatus, 2000)
  } catch (error) {
    console.error('触发分析失败:', error)
    analyzing.value = false
    error.value = '触发分析失败'
    ElMessage.error('触发AI分析失败')
  }
}

const retryAnalysis = () => {
  error.value = ''
  triggerAnalysis()
}

const exportReport = (format: 'json' | 'pdf' = 'json') => {
  if (!analysisData.value || !analysisRecord.value) {
    ElMessage.warning('暂无分析数据可导出')
    return
  }
  
  try {
    if (format === 'pdf') {
      // 生成PDF报告
      generateAnalysisReportPDF(analysisRecord.value, projectName.value)
      ElMessage.success('PDF报告生成并下载成功')
    } else {
      // 导出JSON报告逻辑
      const reportData = {
        performance_score: analysisData.value?.performance_score,
        bottlenecks: analysisData.value?.bottleneck_analysis,
        suggestions: analysisData.value?.optimization_suggestions,
        risks: analysisData.value?.risk_assessment,
        analysis_time: analysisRecord.value?.created_at
      }
      
      const blob = new Blob([JSON.stringify(reportData, null, 2)], {
        type: 'application/json'
      })
      
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `performance-analysis-${performanceRecordId.value}.json`
      a.click()
      URL.revokeObjectURL(url)
      
      ElMessage.success('JSON报告导出成功')
    }
  } catch (error) {
    console.error('导出报告失败:', error)
    ElMessage.error('导出报告失败')
  }
}

const handleExportCommand = (command: 'json' | 'pdf') => {
  exportReport(command)
}

const initScoreChart = () => {
  if (!scoreChartRef.value || !analysisData.value) return
  
  scoreChart = echarts.init(scoreChartRef.value)
  
  const score = analysisData.value.performance_score
  
  const option = {
    series: [{
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      center: ['50%', '75%'],
      radius: '90%',
      min: 0,
      max: 100,
      splitNumber: 10,
      axisLine: {
        lineStyle: {
          width: 6,
          color: [
            [0.3, '#ff4d4f'],
            [0.7, '#faad14'],
            [1, '#52c41a']
          ]
        }
      },
      pointer: {
        icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
        length: '12%',
        width: 20,
        offsetCenter: [0, '-60%'],
        itemStyle: {
          color: 'auto'
        }
      },
      axisTick: {
        length: 12,
        lineStyle: {
          color: 'auto',
          width: 2
        }
      },
      splitLine: {
        length: 20,
        lineStyle: {
          color: 'auto',
          width: 5
        }
      },
      axisLabel: {
        color: '#464646',
        fontSize: 12
      },
      title: {
        offsetCenter: [0, '-20%'],
        fontSize: 14,
        color: '#464646'
      },
      detail: {
        fontSize: 18,
        offsetCenter: [0, '0%'],
        valueAnimation: true,
        formatter: function (value: number) {
          return Math.round(value) + ''
        },
        color: 'auto'
      },
      data: [{
        value: score,
        name: '性能评分'
      }]
    }]
  }
  
  scoreChart.setOption(option)
}

// 辅助方法
const formatProgress = (percentage: number) => {
  return `${percentage}%`
}

const getScoreLevel = (score: number) => {
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  if (score >= 40) return 'fair'
  return 'poor'
}

const getScoreLevelText = (score: number) => {
  if (score >= 80) return '优秀'
  if (score >= 60) return '良好'
  if (score >= 40) return '一般'
  return '较差'
}

const getBottleneckSeverityType = () => {
  const bottlenecks = analysisData.value?.bottleneck_analysis || []
  const hasHigh = bottlenecks.some(b => b.severity === 'high')
  const hasMedium = bottlenecks.some(b => b.severity === 'medium')
  
  if (hasHigh) return 'danger'
  if (hasMedium) return 'warning'
  return 'success'
}

const getSeverityTagType = (severity: string) => {
  const typeMap: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return typeMap[severity] || 'info'
}

const getSeverityText = (severity: string) => {
  const textMap: Record<string, string> = {
    high: '严重',
    medium: '中等',
    low: '轻微'
  }
  return textMap[severity] || severity
}

const getBottleneckTypeText = (type: string) => {
  const textMap: Record<string, string> = {
    database: '数据库瓶颈',
    computation: 'CPU计算瓶颈',
    io: 'I/O瓶颈',
    memory: '内存瓶颈',
    network: '网络瓶颈'
  }
  return textMap[type] || type
}

const getPriorityTagType = (priority: string) => {
  const typeMap: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return typeMap[priority] || 'info'
}

const getPriorityText = (priority: string) => {
  const textMap: Record<string, string> = {
    high: '高优先级',
    medium: '中优先级',
    low: '低优先级'
  }
  return textMap[priority] || priority
}

const getCategoryText = (category: string) => {
  const textMap: Record<string, string> = {
    database: '数据库优化',
    memory: '内存优化',
    computation: '计算优化',
    io: 'I/O优化',
    performance: '性能优化'
  }
  return textMap[category] || category
}

const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    completed: 'success',
    processing: 'warning',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    completed: '已完成',
    processing: '处理中',
    failed: '失败'
  }
  return textMap[status] || status
}

const formatDateTime = (dateString?: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 返回上一页
const goBack = () => {
  if (fromAnalysisList.value) {
    router.push('/analysis')
  } else {
    router.back()
  }
}

// 生命周期
onMounted(async () => {
  await loadAnalysisData()
})
</script>

<style scoped>
.ai-analysis {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-left h2 {
  margin: 0;
  color: #303133;
}

.page-header .project-name {
  margin-left: 12px;
  color: #909399;
  font-size: 16px;
}

.loading-container,
.analyzing-container,
.error-container {
  margin-top: 40px;
}

.analyzing-content,
.error-content {
  text-align: center;
  padding: 40px;
}

.analyzing-icon,
.error-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 16px;
}

.error-icon {
  color: #f56c6c;
}

.analysis-results > div {
  margin-bottom: 20px;
}

.score-section .score-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
}

.score-main {
  text-align: center;
}

.score-value {
  font-size: 48px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.score-label {
  font-size: 16px;
  color: #606266;
  margin-bottom: 8px;
}

.score-level {
  font-size: 14px;
  font-weight: bold;
  padding: 4px 12px;
  border-radius: 12px;
}

.score-level.excellent {
  background: #f0f9ff;
  color: #52c41a;
}

.score-level.good {
  background: #fff7e6;
  color: #faad14;
}

.score-level.fair {
  background: #fff2e8;
  color: #fa8c16;
}

.score-level.poor {
  background: #fff1f0;
  color: #ff4d4f;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.no-bottlenecks,
.no-suggestions,
.no-risks {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.no-bottlenecks .el-icon,
.no-risks .el-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.bottleneck-list .bottleneck-item {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 12px;
}

.bottleneck-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.bottleneck-type {
  font-weight: bold;
  color: #303133;
}

.bottleneck-impact {
  font-size: 12px;
  color: #909399;
}

.bottleneck-description {
  color: #606266;
  line-height: 1.5;
  margin-bottom: 8px;
}

.bottleneck-function {
  font-size: 12px;
  color: #909399;
}

.bottleneck-function code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
}

.suggestion-title {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.suggestion-category {
  font-size: 12px;
  color: #909399;
  margin-left: auto;
}

.suggestion-content {
  padding: 16px 0;
}

.suggestion-description {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 16px;
}

.suggestion-code {
  margin-bottom: 16px;
}

.suggestion-code h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #303133;
}

.code-textarea {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  background: #f8f9fa;
}

.suggestion-improvement {
  text-align: right;
}

.risk-category h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.risk-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.risk-item {
  padding: 8px 12px;
  margin-bottom: 8px;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.4;
}

.current-risk {
  background: #fef0f0;
  border-left: 4px solid #f56c6c;
  color: #f56c6c;
}

.potential-issue {
  background: #fdf6ec;
  border-left: 4px solid #e6a23c;
  color: #e6a23c;
}

.recommendation {
  background: #f0f9ff;
  border-left: 4px solid #409eff;
  color: #409eff;
}

.no-risks {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
}
</style>
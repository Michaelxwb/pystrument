<template>
  <div class="ai-analysis">
    <div class="page-header">
      <div class="header-left">
        <el-button
          type="text"
          @click="goBack"
          class="back-button"
        >
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div class="header-info">
          <span class="title">AI性能分析报告</span>
          <span v-if="projectName" class="project-name">{{ projectName }}</span>
        </div>
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
        <h3 class="section-title">性能评分 <el-tooltip content="基于多维度分析得出的综合性能评分" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
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
        <h3 class="section-title">性能瓶颈分析 <el-tooltip content="识别系统中的性能瓶颈和潜在问题" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
        <el-card>
          <template #header>
            <div class="section-header">
              <el-icon><Warning /></el-icon>
              <span>瓶颈详情</span>
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
        <h3 class="section-title">优化建议 <el-tooltip content="针对发现的问题提供的优化建议" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
        <el-card>
          <template #header>
            <div class="section-header">
              <el-icon><Lightning /></el-icon>
              <span>建议详情</span>
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
        <h3 class="section-title">风险评估 <el-tooltip content="系统当前存在的风险和潜在问题评估" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
        <el-card>
          <template #header>
            <div class="section-header">
              <el-icon><Lock /></el-icon>
              <span>风险详情</span>
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
        <h3 class="section-title">分析信息 <el-tooltip content="本次分析的基本信息" placement="top"><el-icon><QuestionFilled /></el-icon></el-tooltip></h3>
        <el-card>
          <template #header>
            <div class="section-header">
              <el-icon><InfoFilled /></el-icon>
              <span>基本信息</span>
            </div>
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
import { ref, reactive, onMounted, nextTick, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  MagicStick,
  Download,
  Loading,
  Warning,
  Lightning,
  Lock,
  SuccessFilled,
  InfoFilled,
  Close,
  QuestionFilled
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { analysisApi } from '@/api/analysis'
import { projectApi } from '@/api/project'
import type { AnalysisRecord, AnalysisResults } from '@/types/analysis'
import { generateAnalysisReportPDF } from '@/utils/reportGenerator'
import { formatDateTime } from '@/utils/dateUtils'

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
            bottleneck_analysis: response.data.results.bottleneck_analysis || [],
            optimization_suggestions: response.data.results.optimization_suggestions || [],
            risk_assessment: response.data.results.risk_assessment || {
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
        
        // 初始化评分图表
        await nextTick()
        initScoreChart()
      }
    } else {
      // 否则触发新的分析
      await triggerAnalysis()
    }
  } catch (err: any) {
    console.error('加载分析数据失败:', err)
    error.value = err.message || '加载分析数据失败'
    ElMessage.error('加载分析数据失败')
  } finally {
    loading.value = false
  }
}

// 触发分析
const triggerAnalysis = async () => {
  try {
    analyzing.value = true
    analyzeProgress.value = 0
    
    // 模拟进度更新
    const progressInterval = setInterval(() => {
      if (analyzeProgress.value < 90) {
        analyzeProgress.value += 5
      }
    }, 500)
    
    // 触发分析
    const response = await analysisApi.triggerAnalysis(performanceRecordId.value, {
      ai_service: 'default',
      priority: 'normal'
    })
    
    // 获取任务ID并轮询状态
    const taskId = response.data.task_id
    let taskCompleted = false
    
    while (!taskCompleted) {
      try {
        const statusResponse = await analysisApi.getTaskStatus(taskId)
        const status = statusResponse.data.status
        
        if (status === 'SUCCESS') {
          taskCompleted = true
          // 获取分析结果
          const resultResponse = await analysisApi.getAnalysisResult(performanceRecordId.value)
          analysisRecord.value = resultResponse.data
          
          // 处理分析结果
          if (resultResponse.data.results) {
            analysisData.value = {
              performance_score: resultResponse.data.results.performance_score,
              bottleneck_analysis: resultResponse.data.results.bottleneck_analysis || [],
              optimization_suggestions: resultResponse.data.results.optimization_suggestions || [],
              risk_assessment: resultResponse.data.results.risk_assessment || {
                current_risks: [],
                potential_issues: [],
                recommendations: []
              },
              summary: resultResponse.data.results.summary
            }
          }
          
          // 初始化评分图表
          await nextTick()
          initScoreChart()
          
          ElMessage.success('AI分析完成')
        } else if (status === 'FAILURE') {
          taskCompleted = true
          throw new Error('AI分析失败')
        } else if (status === 'IN_PROGRESS') {
          // 更新进度
          const progress = statusResponse.data.progress || 0
          analyzeProgress.value = Math.max(analyzeProgress.value, progress * 100)
        }
        
        // 等待一段时间再检查
        await new Promise(resolve => setTimeout(resolve, 2000))
      } catch (err) {
        taskCompleted = true
        throw err
      }
    }
    
    // 清除进度更新定时器
    clearInterval(progressInterval)
  } catch (err: any) {
    console.error('触发分析失败:', err)
    error.value = err.message || '触发分析失败'
    ElMessage.error('触发分析失败')
  } finally {
    analyzing.value = false
  }
}

// 重试分析
const retryAnalysis = () => {
  error.value = ''
  triggerAnalysis()
}

// 初始化评分图表
const initScoreChart = () => {
  if (!scoreChartRef.value || !analysisData.value) return
  
  // 销毁已存在的图表实例
  if (scoreChart) {
    scoreChart.dispose()
  }
  
  // 初始化图表
  scoreChart = echarts.init(scoreChartRef.value)
  
  // 计算评分等级
  const score = analysisData.value.performance_score
  let levelText = ''
  let levelColor = ''
  
  if (score >= 80) {
    levelText = '优秀'
    levelColor = '#52c41a'
  } else if (score >= 60) {
    levelText = '良好'
    levelColor = '#faad14'
  } else if (score >= 40) {
    levelText = '一般'
    levelColor = '#fa8c16'
  } else {
    levelText = '较差'
    levelColor = '#ff4d4f'
  }
  
  // 配置图表选项
  const option = {
    series: [
      {
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        min: 0,
        max: 100,
        splitNumber: 5,
        axisLine: {
          lineStyle: {
            width: 15,
            color: [
              [0.4, '#ff4d4f'],
              [0.6, '#fa8c16'],
              [0.8, '#faad14'],
              [1, '#52c41a']
            ]
          }
        },
        pointer: {
          icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
          length: '70%',
          width: 8,
          offsetCenter: [0, '-50%'],
          itemStyle: {
            color: 'auto'
          }
        },
        axisTick: {
          length: 8,
          lineStyle: {
            color: 'auto',
            width: 2
          }
        },
        splitLine: {
          length: 12,
          lineStyle: {
            color: 'auto',
            width: 3
          }
        },
        axisLabel: {
          color: '#666',
          fontSize: 12,
          distance: -40,
          formatter: function (value: number) {
            if (value === 0) return '0'
            if (value === 20) return '20'
            if (value === 40) return '40'
            if (value === 60) return '60'
            if (value === 80) return '80'
            if (value === 100) return '100'
            return ''
          }
        },
        title: {
          offsetCenter: [0, '20%'],
          fontSize: 16
        },
        detail: {
          fontSize: 32,
          offsetCenter: [0, '-20%'],
          valueAnimation: true,
          formatter: function (value: number) {
            return '{value|' + value.toFixed(0) + '}\n{unit|分}'
          },
          rich: {
            value: {
              fontSize: 32,
              fontWeight: 'bold',
              color: '#333'
            },
            unit: {
              fontSize: 14,
              color: '#999',
              padding: [0, 0, -10, 0]
            }
          }
        },
        data: [
          {
            value: score,
            name: levelText,
            title: {
              color: levelColor,
              fontSize: 16
            }
          }
        ]
      }
    ]
  }
  
  // 设置图表选项
  scoreChart.setOption(option)
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    scoreChart?.resize()
  })
}

// 导出命令处理
const handleExportCommand = async (command: 'json' | 'pdf') => {
  if (!analysisRecord.value) return
  
  try {
    if (command === 'pdf') {
      // 生成PDF报告
      await generateAnalysisReportPDF(analysisRecord.value, projectName.value || '未知项目')
      ElMessage.success('PDF报告生成并下载成功')
    } else {
      // 导出JSON报告
      const reportData = {
        performance_score: analysisData.value?.performance_score,
        bottlenecks: analysisData.value?.bottleneck_analysis,
        suggestions: analysisData.value?.optimization_suggestions,
        risks: analysisData.value?.risk_assessment,
        analysis_time: analysisRecord.value.created_at
      }
      
      const blob = new Blob([JSON.stringify(reportData, null, 2)], {
        type: 'application/json'
      })
      
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `AI分析报告_${projectName.value || '未知项目'}_${performanceRecordId.value.substring(0, 8)}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      ElMessage.success('JSON报告导出成功')
    }
  } catch (err) {
    console.error('导出报告失败:', err)
    ElMessage.error('导出报告失败')
  }
}

// 返回上一页
const goBack = () => {
  if (fromAnalysisList.value) {
    router.push('/analysis')
  } else {
    router.go(-1)
  }
}

// 格式化进度
const formatProgress = (percentage: number) => {
  return `${percentage.toFixed(0)}%`
}

// 获取评分等级
const getScoreLevel = (score: number) => {
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  if (score >= 40) return 'fair'
  return 'poor'
}

// 获取评分等级文本
const getScoreLevelText = (score: number) => {
  if (score >= 80) return '优秀'
  if (score >= 60) return '良好'
  if (score >= 40) return '一般'
  return '较差'
}

// 获取瓶颈严重程度类型
const getBottleneckSeverityType = () => {
  const bottlenecks = analysisData.value?.bottleneck_analysis || []
  if (bottlenecks.length === 0) return 'success'
  
  // 检查是否有高严重性瓶颈
  const hasHighSeverity = bottlenecks.some((b: any) => b.severity === 'high')
  if (hasHighSeverity) return 'danger'
  
  // 检查是否有中等严重性瓶颈
  const hasMediumSeverity = bottlenecks.some((b: any) => b.severity === 'medium')
  if (hasMediumSeverity) return 'warning'
  
  return 'info'
}

// 获取严重性标签类型
const getSeverityTagType = (severity: string) => {
  switch (severity) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'info'
    default: return 'info'
  }
}

// 获取严重性文本
const getSeverityText = (severity: string) => {
  switch (severity) {
    case 'high': return '高'
    case 'medium': return '中'
    case 'low': return '低'
    default: return '未知'
  }
}

// 获取瓶颈类型文本
const getBottleneckTypeText = (type: string) => {
  switch (type) {
    case 'database': return '数据库'
    case 'network': return '网络'
    case 'cpu': return 'CPU'
    case 'memory': return '内存'
    case 'io': return 'I/O'
    default: return type
  }
}

// 获取优先级标签类型
const getPriorityTagType = (priority: string) => {
  switch (priority) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'info'
    default: return 'info'
  }
}

// 获取优先级文本
const getPriorityText = (priority: string) => {
  switch (priority) {
    case 'high': return '高优先级'
    case 'medium': return '中优先级'
    case 'low': return '低优先级'
    default: return '未知优先级'
  }
}

// 获取分类文本
const getCategoryText = (category: string) => {
  switch (category) {
    case 'database': return '数据库优化'
    case 'network': return '网络优化'
    case 'cpu': return 'CPU优化'
    case 'memory': return '内存优化'
    case 'io': return 'I/O优化'
    case 'algorithm': return '算法优化'
    default: return '通用优化'
  }
}

// 获取状态标签类型
const getStatusTagType = (status?: string) => {
  switch (status) {
    case 'pending': return 'info'
    case 'processing': return 'warning'
    case 'completed': return 'success'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

// 获取状态文本
const getStatusText = (status?: string) => {
  switch (status) {
    case 'pending': return '待处理'
    case 'processing': return '处理中'
    case 'completed': return '已完成'
    case 'failed': return '失败'
    default: return '未知'
  }
}



// 组件卸载时清理
onUnmounted(() => {
  if (scoreChart) {
    scoreChart.dispose()
    scoreChart = null
  }
})

// 初始化
onMounted(() => {
  loadAnalysisData()
})
</script>

<style lang="scss" scoped>
.ai-analysis {
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
      
      .header-info {
        .title {
          font-size: 24px;
          font-weight: 600;
          color: #303133;
          margin-right: 16px;
        }
        
        .project-name {
          font-size: 16px;
          color: #909399;
        }
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
  
  .section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
    color: #303133;
  }
  
  .loading-container,
  .analyzing-container,
  .error-container {
    margin-top: 20px;
  }
  
  .analyzing-content,
  .error-content {
    text-align: center;
    padding: 40px;
  }
  
  .analyzing-icon,
  .error-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  
  .analyzing-icon {
    color: #409eff;
    animation: rotating 2s linear infinite;
  }
  
  .error-icon {
    color: #f56c6c;
  }
  
  @keyframes rotating {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
  
  .score-section {
    .score-content {
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
    transition: all 0.3s;
    
    &:hover {
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    }
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
    margin-left: auto;
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
}
</style>
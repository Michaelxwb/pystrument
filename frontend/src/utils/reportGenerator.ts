// PDF报告生成工具

import html2pdf from 'html2pdf.js'
import type { AnalysisRecord, AnalysisResults } from '@/types/analysis'

// PDF报告选项
const pdfOptions = {
  margin: 10,
  filename: 'analysis-report.pdf',
  image: { type: 'jpeg', quality: 0.98 },
  html2canvas: { scale: 2, useCORS: true },
  jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
}

/**
 * 生成分析报告PDF
 * @param analysisRecord 分析记录
 * @param projectName 项目名称
 */
export async function generateAnalysisReportPDF(analysisRecord: AnalysisRecord, projectName: string): Promise<void> {
  // 添加调试日志
  console.log('生成PDF报告，传入参数:', { analysisRecord, projectName });
  
  if (!analysisRecord) {
    console.error('分析数据不完整，无法生成报告: 缺少analysisRecord');
    throw new Error('分析数据不完整，无法生成报告')
  }
  
  // 如果results字段不存在，创建一个默认的空结果对象
  if (!analysisRecord.results) {
    console.warn('分析结果为空，将使用默认值');
    analysisRecord.results = {
      summary: '暂无分析摘要',
      performance_score: 0,
      bottlenecks: [],
      recommendations: [],
    };
  }
  
  const results = analysisRecord.results
  const reportFilename = `分析报告_${projectName || analysisRecord.project_key || '未知项目'}_${(analysisRecord.analysis_id || 'unknown').substring(0, 8)}.pdf`
  
  // 添加调试日志
  console.log('分析结果数据:', results);
  
  // 创建报告HTML内容
  const reportContent = createReportHTML(analysisRecord, projectName, results)
  
  // 添加调试日志
  console.log('生成的报告HTML内容长度:', reportContent.length);
  
  // 创建临时容器
  const container = document.createElement('div')
  container.innerHTML = reportContent
  container.style.position = 'absolute'
  container.style.left = '-9999px'
  container.style.width = '210mm' // A4宽度
  container.style.minHeight = '297mm' // A4高度
  container.style.padding = '10mm'
  container.style.backgroundColor = '#ffffff' // 确保背景为白色
  document.body.appendChild(container)
  
  // 添加调试日志
  console.log('临时容器创建成功，内容长度:', container.innerHTML.length);
  
  // 配置PDF选项
  const options = {
    ...pdfOptions,
    filename: reportFilename,
    html2canvas: {
      ...pdfOptions.html2canvas,
      logging: true, // 启用html2canvas的日志
      backgroundColor: '#ffffff', // 设置背景颜色为白色
    }
  }
  
  try {
    // 确保内容完全渲染后再生成PDF
    await new Promise(resolve => setTimeout(resolve, 500));
    
    console.log('开始生成PDF...');
    
    // 生成PDF
    const worker = html2pdf()
      .from(container)
      .set(options);
      
    console.log('配置PDF生成选项完成，准备保存...');
    await worker.save();
    
    console.log('PDF生成并保存成功');
  } catch (error) {
    console.error('生成PDF失败:', error);
    throw error;
  } finally {
    // 移除临时容器
    document.body.removeChild(container)
  }
}

/**
 * 创建报告HTML内容
 * @param record 分析记录
 * @param projectName 项目名称
 * @param results 分析结果
 */
function createReportHTML(record: AnalysisRecord, projectName: string, results: AnalysisResults): string {
  // 添加调试日志
  console.log('创建报告HTML，传入参数:', { record, projectName, results });
  
  // 确保bottlenecks和recommendations字段存在且为数组
  const bottlenecks = Array.isArray(results.bottlenecks) ? results.bottlenecks : [];
  const recommendations = Array.isArray(results.recommendations) ? results.recommendations : [];
  
  // 添加调试日志
  console.log('处理后的瓶颈和建议数据:', { bottlenecks, recommendations });
  
  // 使用后端返回的bottlenecks字段替代前端期望的bottleneck_analysis
  const bottlenecksHTML = createBottlenecksHTML(bottlenecks);
  // 使用后端返回的recommendations字段替代前端期望的optimization_suggestions
  const recommendationsHTML = createRecommendationsHTML(recommendations);
  
  // 添加调试日志
  console.log('生成的瓶颈和建议HTML:', { bottlenecksHTML, recommendationsHTML });
  
  return `
    <div class="analysis-report">
      <div class="report-header">
        <h1>AI性能分析报告</h1>
        <div class="report-meta">
          <div class="project-name">项目: ${projectName || record.project_key || '未知项目'}</div>
          <div class="report-date">生成时间: ${new Date().toLocaleString('zh-CN')}</div>
        </div>
      </div>
      
      <div class="report-summary">
        <h2>分析摘要</h2>
        <div class="summary-content">${results.summary || '无摘要信息'}</div>
        
        <div class="score-section">
          <div class="score-label">性能评分</div>
          <div class="score-value">${results.performance_score || 0}</div>
          <div class="score-level">${getScoreLevelText(results.performance_score || 0)}</div>
        </div>
      </div>
      
      <div class="bottlenecks-section">
        <h2>性能瓶颈分析</h2>
        ${bottlenecksHTML || '<div class="no-data">未发现明显的性能瓶颈</div>'}
      </div>
      
      <div class="recommendations-section">
        <h2>优化建议</h2>
        ${recommendationsHTML || '<div class="no-data">暂无优化建议</div>'}
      </div>
      
      <div class="report-footer">
        <div>报告ID: ${record.analysis_id || '未知ID'}</div>
        <div>分析服务: ${record.ai_service || '默认服务'}</div>
        <div>分析时间: ${formatDateTime(record.created_at)}</div>
      </div>
    </div>
    
    <style>
      .analysis-report {
        font-family: Arial, sans-serif;
        color: #333;
        line-height: 1.5;
        width: 100%;
      }
      
      .report-header {
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #409eff;
      }
      
      .report-header h1 {
        color: #409eff;
        margin: 0 0 10px 0;
        text-align: center;
      }
      
      .report-meta {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #666;
      }
      
      h2 {
        color: #409eff;
        margin: 20px 0 10px 0;
        padding-bottom: 5px;
        border-bottom: 1px solid #eee;
      }
      
      .summary-content {
        margin-bottom: 15px;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 4px;
      }
      
      .score-section {
        display: flex;
        align-items: center;
        margin: 15px 0;
        padding: 15px;
        background-color: #f0f9ff;
        border-radius: 8px;
      }
      
      .score-label {
        font-weight: bold;
        margin-right: 10px;
      }
      
      .score-value {
        font-size: 24px;
        font-weight: bold;
        color: #409eff;
        margin-right: 10px;
      }
      
      .score-level {
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 12px;
        font-weight: bold;
        background-color: #e1f3ff;
        color: #409eff;
      }
      
      .bottleneck-item, .recommendation-item {
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
        background-color: #f8f8f8;
      }
      
      .bottleneck-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;
      }
      
      .bottleneck-type {
        font-weight: bold;
      }
      
      .bottleneck-severity {
        font-size: 12px;
        padding: 2px 6px;
        border-radius: 10px;
      }
      
      .severity-high {
        background-color: #fef0f0;
        color: #f56c6c;
      }
      
      .severity-medium {
        background-color: #fdf6ec;
        color: #e6a23c;
      }
      
      .severity-low {
        background-color: #f0f9ff;
        color: #409eff;
      }
      
      .no-data {
        text-align: center;
        padding: 20px;
        color: #909399;
        font-style: italic;
      }
      
      .report-footer {
        margin-top: 30px;
        padding-top: 10px;
        border-top: 1px solid #eee;
        font-size: 11px;
        color: #999;
      }
      
      .bottleneck-description {
        margin: 10px 0;
        padding: 8px;
        background-color: #ffffff;
        border-radius: 4px;
      }
      
      .bottleneck-function {
        font-size: 12px;
        color: #666;
        margin: 5px 0;
      }
      
      .bottleneck-recommendations {
        font-size: 12px;
        color: #409eff;
        margin: 5px 0;
        padding: 5px;
        background-color: #f0f9ff;
        border-radius: 4px;
      }
    </style>
  `
}

/**
 * 创建瓶颈HTML内容
 */
function createBottlenecksHTML(bottlenecks: any[]): string {
  // 添加调试日志
  console.log('创建瓶颈HTML，传入数据:', bottlenecks);
  
  if (!bottlenecks || bottlenecks.length === 0) {
    return '<div class="no-data">未发现明显的性能瓶颈</div>'
  }
  
  const html = bottlenecks.map((bottleneck, index) => {
    // 添加调试日志
    console.log(`处理瓶颈 ${index}:`, bottleneck);
    
    return `
      <div class="bottleneck-item">
        <div class="bottleneck-header">
          <div class="bottleneck-type">${getBottleneckTypeText(bottleneck.type)}</div>
          <div class="bottleneck-severity severity-${bottleneck.severity || 'medium'}">${getSeverityText(bottleneck.severity)}</div>
        </div>
        <div class="bottleneck-description">${bottleneck.description || bottleneck.summary || '无描述信息'}</div>
        ${bottleneck.function ? `<div class="bottleneck-function">相关函数: ${bottleneck.function}</div>` : ''}
        ${bottleneck.recommendations && Array.isArray(bottleneck.recommendations) && bottleneck.recommendations.length > 0 ? 
          `<div class="bottleneck-recommendations">建议: ${bottleneck.recommendations.join(', ')}</div>` : ''}
      </div>
    `
  }).join('')
  
  // 添加调试日志
  console.log('生成的瓶颈HTML:', html);
  
  return html;
}

/**
 * 创建建议HTML内容
 */
function createRecommendationsHTML(recommendations: string[]): string {
  // 添加调试日志
  console.log('创建建议HTML，传入数据:', recommendations);
  
  if (!recommendations || recommendations.length === 0) {
    return '<div class="no-data">暂无优化建议</div>'
  }
  
  const html = recommendations.map((recommendation, index) => {
    // 添加调试日志
    console.log(`处理建议 ${index}:`, recommendation);
    
    return `
      <div class="recommendation-item">
        ${recommendation || '无建议内容'}
      </div>
    `
  }).join('')
  
  // 添加调试日志
  console.log('生成的建议HTML:', html);
  
  return html;
}

/**
 * 获取瓶颈类型文本
 */
function getBottleneckTypeText(type: string): string {
  const typeMap: Record<string, string> = {
    'database': '数据库瓶颈',
    'computation': 'CPU计算瓶颈',
    'io': 'I/O瓶颈',
    'memory': '内存瓶颈',
    'network': '网络瓶颈'
  }
  return typeMap[type] || (type || '未知类型')
}

/**
 * 获取严重程度文本
 */
function getSeverityText(severity: string): string {
  const textMap: Record<string, string> = {
    'high': '严重',
    'medium': '中等',
    'low': '轻微'
  }
  return textMap[severity] || (severity || '中等')
}

/**
 * 获取评分等级文本
 */
function getScoreLevelText(score: number): string {
  if (score >= 80) return '优秀'
  if (score >= 60) return '良好'
  if (score >= 40) return '一般'
  return '较差'
}

/**
 * 格式化日期时间
 */
function formatDateTime(dateString?: string): string {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleString('zh-CN')
  } catch (error) {
    console.error('日期格式化失败:', error);
    return dateString || '-'
  }
}

export default {
  generateAnalysisReportPDF
}
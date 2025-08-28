// PDF报告生成工具

import type { AnalysisRecord, AnalysisResults } from '@/types/analysis'
import jsPDF from 'jspdf'
import { formatDateTime } from '@/utils/dateUtils'

/**
 * 使用直接输出HTML的方式生成报告
 * @param analysisRecord 分析记录
 * @param projectName 项目名称
 */
export async function generateAnalysisReportPDF(analysisRecord: AnalysisRecord, projectName: string): Promise<void> {
  console.log('生成报告，传入参数:', { analysisRecord, projectName });
  
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
  const reportFilename = `分析报告_${projectName || analysisRecord.project_key || '未知项目'}_${(analysisRecord.analysis_id || 'unknown').substring(0, 8)}`
  
  // 创建报告HTML内容
  const reportContent = createReportHTML(analysisRecord, projectName, results)
  
  // 打开新窗口并写入报告内容
  const reportWindow = window.open('', '_blank');
  if (!reportWindow) {
    throw new Error('无法创建新窗口，请检查是否被浏览器拦截');
  }
  
  reportWindow.document.write(reportContent);
  reportWindow.document.title = reportFilename;
  reportWindow.document.close();
  
  // 延迟打印，等待内容完全加载
  setTimeout(() => {
    try {
      reportWindow.print();
    } catch (error) {
      console.error('打印失败:', error);
    }
  }, 1000);
}

/**
 * 创建报告HTML内容
 * @param record 分析记录
 * @param projectName 项目名称
 * @param results 分析结果
 */
function createReportHTML(record: AnalysisRecord, projectName: string, results: AnalysisResults): string {
  console.log('创建报告HTML，传入参数:', { record, projectName, results });
  
  // 确保bottlenecks和recommendations字段存在且为数组
  const bottlenecks = Array.isArray(results.bottlenecks) ? results.bottlenecks : [];
  const recommendations = Array.isArray(results.recommendations) ? results.recommendations : [];
  
  // 生成瓶颈和建议的HTML内容
  const bottlenecksHTML = createBottlenecksHTML(bottlenecks);
  const recommendationsHTML = createRecommendationsHTML(recommendations);
  
  // 创建完整的HTML文档，包含DOCTYPE和meta标签
  return `
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>AI性能分析报告</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          color: #333;
          line-height: 1.5;
          margin: 0;
          padding: 20px;
          background-color: #ffffff;
        }
        
        .analysis-report {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          border: 1px solid #eee;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .report-header {
          margin-bottom: 20px;
          padding-bottom: 10px;
          border-bottom: 2px solid #409eff;
          text-align: center;
        }
        
        .report-header h1 {
          color: #409eff;
          margin: 0 0 15px 0;
          font-size: 24px;
        }
        
        .report-meta {
          display: flex;
          justify-content: space-between;
          font-size: 12px;
          color: #666;
          margin-top: 10px;
        }
        
        h2 {
          color: #409eff;
          margin: 20px 0 10px 0;
          padding-bottom: 5px;
          border-bottom: 1px solid #eee;
          font-size: 18px;
        }
        
        .summary-content {
          margin-bottom: 15px;
          padding: 15px;
          background-color: #f8f9fa;
          border-radius: 6px;
          font-size: 14px;
        }
        
        .score-section {
          display: flex;
          align-items: center;
          margin: 20px 0;
          padding: 15px;
          background-color: #f0f9ff;
          border-radius: 8px;
          text-align: center;
        }
        
        .score-label {
          font-weight: bold;
          margin-right: 15px;
          font-size: 16px;
        }
        
        .score-value {
          font-size: 28px;
          font-weight: bold;
          color: #409eff;
          margin: 0 15px;
        }
        
        .score-level {
          padding: 5px 10px;
          border-radius: 15px;
          font-size: 14px;
          font-weight: bold;
          background-color: #e1f3ff;
          color: #409eff;
        }
        
        .bottleneck-item, .recommendation-item {
          padding: 15px;
          margin-bottom: 15px;
          border-radius: 8px;
          background-color: #f8f8f8;
          border-left: 4px solid #409eff;
        }
        
        .bottleneck-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 10px;
          align-items: center;
        }
        
        .bottleneck-type {
          font-weight: bold;
          font-size: 16px;
        }
        
        .bottleneck-severity {
          font-size: 12px;
          padding: 3px 8px;
          border-radius: 12px;
          font-weight: bold;
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
        
        .bottleneck-description {
          margin: 10px 0;
          padding: 10px;
          background-color: #ffffff;
          border-radius: 6px;
          font-size: 14px;
          line-height: 1.6;
          border: 1px solid #eee;
        }
        
        .bottleneck-function {
          font-size: 13px;
          color: #666;
          margin: 8px 0;
          font-family: monospace;
          background-color: #f5f5f5;
          padding: 5px 8px;
          border-radius: 4px;
          display: inline-block;
        }
        
        .bottleneck-recommendations {
          font-size: 13px;
          color: #409eff;
          margin: 8px 0;
          padding: 8px;
          background-color: #f0f9ff;
          border-radius: 6px;
          line-height: 1.5;
        }
        
        .no-data {
          text-align: center;
          padding: 30px;
          color: #909399;
          font-style: italic;
          background-color: #f9f9f9;
          border-radius: 8px;
          margin: 20px 0;
          font-size: 14px;
        }
        
        .report-footer {
          margin-top: 30px;
          padding-top: 15px;
          border-top: 1px solid #eee;
          font-size: 12px;
          color: #999;
          text-align: center;
        }
        
        .report-footer div {
          margin: 5px 0;
        }
        
        @media print {
          body {
            padding: 0;
            background: white;
          }
          
          .analysis-report {
            border: none;
            box-shadow: none;
            padding: 0;
            max-width: 100%;
          }
          
          @page {
            size: A4;
            margin: 1cm;
          }
        }
      </style>
    </head>
    <body>
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
            <div class="score-label">性能评分:</div>
            <div class="score-value">${results.performance_score || 0}</div>
            <div class="score-level">${getScoreLevelText(results.performance_score || 0)}</div>
          </div>
        </div>
        
        <div class="bottlenecks-section">
          <h2>性能瓶颈分析</h2>
          ${bottlenecksHTML}
        </div>
        
        <div class="recommendations-section">
          <h2>优化建议</h2>
          ${recommendationsHTML}
        </div>
        
        <div class="report-footer">
          <div>报告ID: ${record.analysis_id || '未知ID'}</div>
          <div>分析服务: ${record.ai_service || '默认服务'}</div>
          <div>分析时间: ${formatDateTime(record.created_at)}</div>
          <div>性能分析平台 © ${new Date().getFullYear()}</div>
        </div>
      </div>
    </body>
    </html>
  `
}

/**
 * 创建瓶颈HTML内容
 */
function createBottlenecksHTML(bottlenecks: any[]): string {
  console.log('创建瓶颈HTML，传入数据:', bottlenecks);
  
  if (!bottlenecks || bottlenecks.length === 0) {
    return '<div class="no-data">未发现明显的性能瓶颈</div>'
  }
  
  // 防止非法字符在HTML中导致问题
  const sanitizeText = (text: string): string => {
    if (!text) return '';
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  };
  
  const html = bottlenecks.map((bottleneck, index) => {
    console.log(`处理瓶颈 ${index}:`, bottleneck);
    
    const type = sanitizeText(bottleneck.type || '');
    const description = sanitizeText(bottleneck.description || bottleneck.summary || '无描述信息');
    const functionName = bottleneck.function ? sanitizeText(bottleneck.function) : '';
    
    let recommendationsHtml = '';
    if (bottleneck.recommendations && Array.isArray(bottleneck.recommendations) && bottleneck.recommendations.length > 0) {
      const sanitizedRecommendations = bottleneck.recommendations.map(sanitizeText).join(', ');
      recommendationsHtml = `<div class="bottleneck-recommendations">建议: ${sanitizedRecommendations}</div>`;
    }
    
    return `
      <div class="bottleneck-item">
        <div class="bottleneck-header">
          <div class="bottleneck-type">${getBottleneckTypeText(type)}</div>
          <div class="bottleneck-severity severity-${bottleneck.severity || 'medium'}">${getSeverityText(bottleneck.severity)}</div>
        </div>
        <div class="bottleneck-description">${description}</div>
        ${functionName ? `<div class="bottleneck-function">相关函数: ${functionName}</div>` : ''}
        ${recommendationsHtml}
      </div>
    `;
  }).join('');
  
  return html;
}

/**
 * 创建建议HTML内容
 */
function createRecommendationsHTML(recommendations: string[]): string {
  console.log('创建建议HTML，传入数据:', recommendations);
  
  if (!recommendations || recommendations.length === 0) {
    return '<div class="no-data">暂无优化建议</div>';
  }
  
  // 防止非法字符在HTML中导致问题
  const sanitizeText = (text: string): string => {
    if (!text) return '';
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  };
  
  const html = recommendations.map((recommendation, index) => {
    console.log(`处理建议 ${index}:`, recommendation);
    const sanitizedRecommendation = sanitizeText(recommendation || '无建议内容');
    
    return `
      <div class="recommendation-item">
        ${sanitizedRecommendation}
      </div>
    `;
  }).join('');
  
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

// 移除本地的formatDateTime函数，使用从dateUtils导入的函数

export default {
  generateAnalysisReportPDF
}
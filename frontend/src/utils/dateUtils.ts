/**
 * 日期时间工具函数
 * 用于处理时区转换和格式化
 */

/**
 * 将日期时间转换为东八区（北京时间）
 * @param dateString 日期字符串
 * @returns 转换后的Date对象
 */
export const toBeijingTime = (dateString?: string): Date => {
  if (!dateString) {
    return new Date();
  }
  
  try {
    // 创建Date对象
    const date = new Date(dateString);
    
    // 获取当前时区偏移（分钟）
    const timezoneOffset = date.getTimezoneOffset();
    
    // 东八区偏移量（分钟）
    const beijingOffset = -480; // UTC+8 = -480分钟
    
    // 计算时区差异并调整
    const offsetDiff = beijingOffset - timezoneOffset;
    const beijingTime = new Date(date.getTime() + offsetDiff * 60 * 1000);
    
    return beijingTime;
  } catch (error) {
    console.error('时间转换错误:', error);
    return new Date();
  }
}

/**
 * 格式化日期时间为简短格式（月/日 时:分）
 * @param dateString 日期字符串
 * @returns 格式化后的字符串
 */
export const formatDateTime = (dateString?: string): string => {
  if (!dateString) return '';
  
  try {
    const beijingTime = toBeijingTime(dateString);
    return beijingTime.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  } catch (error) {
    return dateString;
  }
}

/**
 * 格式化日期时间为完整格式（年-月-日 时:分:秒）
 * @param dateString 日期字符串
 * @returns 格式化后的字符串
 */
export const formatFullDateTime = (dateString?: string): string => {
  if (!dateString) return '';
  
  try {
    const beijingTime = toBeijingTime(dateString);
    return beijingTime.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  } catch (error) {
    return dateString;
  }
}

/**
 * 格式化日期（年-月-日）
 * @param dateString 日期字符串
 * @returns 格式化后的字符串
 */
export const formatDate = (dateString?: string): string => {
  if (!dateString) return '';
  
  try {
    const beijingTime = toBeijingTime(dateString);
    return beijingTime.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  } catch (error) {
    return dateString;
  }
}

export default {
  toBeijingTime,
  formatDateTime,
  formatFullDateTime,
  formatDate
}
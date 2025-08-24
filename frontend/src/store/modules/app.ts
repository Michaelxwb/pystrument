import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 状态
  const loading = ref(false)
  const theme = ref<'light' | 'dark'>('light')
  const sidebarCollapsed = ref(false)
  const deviceType = ref<'desktop' | 'tablet' | 'mobile'>('desktop')
  const locale = ref('zh-CN')
  
  // 计算属性
  const isDark = computed(() => theme.value === 'dark')
  const isMobile = computed(() => deviceType.value === 'mobile')
  
  // 方法
  const setLoading = (status: boolean) => {
    loading.value = status
  }
  
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    
    // 切换Element Plus主题
    const html = document.documentElement
    if (theme.value === 'dark') {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }
    
    // 保存到本地存储
    localStorage.setItem('theme', theme.value)
  }
  
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
    localStorage.setItem('sidebarCollapsed', String(sidebarCollapsed.value))
  }
  
  const setSidebarCollapsed = (collapsed: boolean) => {
    sidebarCollapsed.value = collapsed
    localStorage.setItem('sidebarCollapsed', String(collapsed))
  }
  
  const setDeviceType = (type: 'desktop' | 'tablet' | 'mobile') => {
    deviceType.value = type
    
    // 移动端自动收起侧边栏
    if (type === 'mobile') {
      setSidebarCollapsed(true)
    }
  }
  
  const setLocale = (newLocale: string) => {
    locale.value = newLocale
    localStorage.setItem('locale', newLocale)
  }
  
  const initApp = () => {
    // 初始化主题
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null
    if (savedTheme) {
      theme.value = savedTheme
      if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark')
      }
    }
    
    // 初始化侧边栏状态
    const savedSidebarState = localStorage.getItem('sidebarCollapsed')
    if (savedSidebarState) {
      sidebarCollapsed.value = savedSidebarState === 'true'
    }
    
    // 初始化语言
    const savedLocale = localStorage.getItem('locale')
    if (savedLocale) {
      locale.value = savedLocale
    }
    
    // 检测设备类型
    detectDeviceType()
    
    // 监听窗口大小变化
    window.addEventListener('resize', detectDeviceType)
  }
  
  const detectDeviceType = () => {
    const width = window.innerWidth
    if (width < 768) {
      setDeviceType('mobile')
    } else if (width < 1024) {
      setDeviceType('tablet')
    } else {
      setDeviceType('desktop')
    }
  }
  
  // 全局错误处理
  const handleError = (error: Error | string, context?: string) => {
    console.error(`[${context || 'App'}] Error:`, error)
    
    ElMessage({
      type: 'error',
      message: typeof error === 'string' ? error : error.message,
      duration: 5000
    })
  }
  
  // 全局成功提示
  const showSuccess = (message: string) => {
    ElMessage({
      type: 'success',
      message,
      duration: 3000
    })
  }
  
  // 全局警告提示
  const showWarning = (message: string) => {
    ElMessage({
      type: 'warning',
      message,
      duration: 4000
    })
  }
  
  // 全局信息提示
  const showInfo = (message: string) => {
    ElMessage({
      type: 'info',
      message,
      duration: 3000
    })
  }
  
  return {
    // 状态
    loading,
    theme,
    sidebarCollapsed,
    deviceType,
    locale,
    
    // 计算属性
    isDark,
    isMobile,
    
    // 方法
    setLoading,
    toggleTheme,
    toggleSidebar,
    setSidebarCollapsed,
    setDeviceType,
    setLocale,
    initApp,
    detectDeviceType,
    handleError,
    showSuccess,
    showWarning,
    showInfo
  }
})
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// 布局组件
const Layout = () => import('@/components/layout/Layout.vue')

// 页面组件
const Dashboard = () => import('@/views/Dashboard.vue')
const ProjectManagement = () => import('@/views/ProjectManagement.vue')
const ProjectDetail = () => import('@/views/ProjectDetail.vue')
const PerformanceMonitor = () => import('@/views/PerformanceMonitor.vue')
const PerformanceDetail = () => import('@/views/PerformanceDetail.vue')
const AIAnalysis = () => import('@/views/AIAnalysis.vue')
const AnalysisResults = () => import('@/views/AnalysisResults.vue')
const Settings = () => import('@/views/Settings.vue')

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/',
    component: Layout,
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: {
          title: '仪表板',
          icon: 'Dashboard',
          keepAlive: true
        }
      },
      {
        path: 'projects',
        name: 'Projects',
        component: ProjectManagement,
        meta: {
          title: '项目管理',
          icon: 'Collection',
          keepAlive: true
        }
      },
      {
        path: 'projects/:projectKey',
        name: 'ProjectDetail',
        component: ProjectDetail,
        props: true,
        meta: {
          title: '项目详情',
          activeMenu: '/projects'
        }
      },
      {
        path: 'performance',
        name: 'Performance',
        component: PerformanceMonitor,
        meta: {
          title: '性能监控',
          icon: 'Monitor',
          keepAlive: true
        }
      },
      {
        path: 'performance/:traceId',
        name: 'PerformanceDetail',
        component: PerformanceDetail,
        props: true,
        meta: {
          title: '性能详情',
          activeMenu: '/performance'
        }
      },
      {
        path: 'analysis',
        name: 'Analysis',
        component: AnalysisResults,
        meta: {
          title: 'AI分析',
          icon: 'DataAnalysis',
          keepAlive: true
        }
      },
      {
        path: 'analysis/:id',
        name: 'AIAnalysis',
        component: AIAnalysis,
        props: true,
        meta: {
          title: 'AI分析详情',
          activeMenu: '/analysis'
        }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: Settings,
        meta: {
          title: '系统设置',
          icon: 'Setting'
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: {
      title: '页面不存在'
    }
  }
]

const router = createRouter({
  history: createWebHistory('/'),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 性能分析平台`
  }
  
  next()
})

router.afterEach(() => {
  // 路由切换后的处理
})

export default router
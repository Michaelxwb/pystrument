import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { projectApi } from '@/api/project'
import type { Project, ProjectCreate, ProjectUpdate } from '@/types/project'

export const useProjectStore = defineStore('project', () => {
  // 状态
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const pagination = ref({
    page: 1,
    size: 10
  })
  
  // 计算属性
  const activeProjects = computed(() => 
    projects.value.filter(p => p.status === 'active')
  )
  
  const archivedProjects = computed(() => 
    projects.value.filter(p => p.status === 'archived')
  )
  
  const projectOptions = computed(() => 
    activeProjects.value.map(p => ({
      label: p.name,
      value: p.project_key
    }))
  )
  
  // 方法
  const fetchProjects = async (params?: {
    page?: number
    size?: number
    status?: string
    framework?: string
  }) => {
    try {
      loading.value = true
      
      const queryParams = {
        page: params?.page || pagination.value.page,
        size: params?.size || pagination.value.size,
        ...(params?.status && { status: params.status }),
        ...(params?.framework && { framework: params.framework })
      }
      
      const response = await projectApi.getProjects(queryParams)
      
      if (response.code === 0) {
        projects.value = response.data.projects
        total.value = response.data.total
        pagination.value.page = response.data.page
        pagination.value.size = response.data.size
      }
      
      return response
    } catch (error) {
      console.error('获取项目列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  const fetchProjectDetail = async (projectKey: string) => {
    try {
      loading.value = true
      const response = await projectApi.getProjectDetail(projectKey)
      
      if (response.code === 0) {
        currentProject.value = response.data
      }
      
      return response
    } catch (error) {
      console.error('获取项目详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  const createProject = async (projectData: ProjectCreate) => {
    try {
      loading.value = true
      const response = await projectApi.createProject(projectData)
      
      if (response.code === 0) {
        // 刷新项目列表
        await fetchProjects()
      }
      
      return response
    } catch (error) {
      console.error('创建项目失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  const updateProject = async (projectKey: string, projectData: ProjectUpdate) => {
    try {
      loading.value = true
      const response = await projectApi.updateProject(projectKey, projectData)
      
      if (response.code === 0) {
        // 更新本地数据
        const index = projects.value.findIndex(p => p.project_key === projectKey)
        if (index !== -1) {
          projects.value[index] = { ...projects.value[index], ...response.data }
        }
        
        // 更新当前项目
        if (currentProject.value?.project_key === projectKey) {
          currentProject.value = { ...currentProject.value, ...response.data }
        }
      }
      
      return response
    } catch (error) {
      console.error('更新项目失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  const deleteProject = async (projectKey: string) => {
    try {
      loading.value = true
      const response = await projectApi.deleteProject(projectKey)
      
      if (response.code === 0) {
        // 从列表中移除
        const index = projects.value.findIndex(p => p.project_key === projectKey)
        if (index !== -1) {
          projects.value.splice(index, 1)
        }
        
        // 清除当前项目
        if (currentProject.value?.project_key === projectKey) {
          currentProject.value = null
        }
      }
      
      return response
    } catch (error) {
      console.error('删除项目失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  const fetchProjectStats = async (projectKey: string) => {
    try {
      const response = await projectApi.getProjectStats(projectKey)
      return response
    } catch (error) {
      console.error('获取项目统计失败:', error)
      throw error
    }
  }
  
  const setCurrentProject = (project: Project | null) => {
    currentProject.value = project
  }
  
  const clearProjects = () => {
    projects.value = []
    currentProject.value = null
    total.value = 0
    pagination.value = { page: 1, size: 10 }
  }
  
  const getProjectByKey = (projectKey: string) => {
    return projects.value.find(p => p.project_key === projectKey)
  }
  
  const updateProjectActivity = (projectKey: string, lastActivity: string) => {
    const project = projects.value.find(p => p.project_key === projectKey)
    if (project) {
      project.last_activity = lastActivity
    }
  }
  
  return {
    // 状态
    projects,
    currentProject,
    loading,
    total,
    pagination,
    
    // 计算属性
    activeProjects,
    archivedProjects,
    projectOptions,
    
    // 方法
    fetchProjects,
    fetchProjectDetail,
    createProject,
    updateProject,
    deleteProject,
    fetchProjectStats,
    setCurrentProject,
    clearProjects,
    getProjectByKey,
    updateProjectActivity
  }
})
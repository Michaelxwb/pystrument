import { http } from '@/utils/request'
import type { Project, ProjectCreate, ProjectUpdate, ProjectStats } from '@/types/project'

export const projectApi = {
  // 获取项目列表
  getProjects(params?: {
    page?: number
    size?: number
    status?: string
    framework?: string
  }) {
    return http.get<{
      projects: Project[]
      total: number
      page: number
      size: number
      pages: number
    }>('/v1/projects', params)
  },
  
  // 获取项目详情
  getProjectDetail(projectKey: string) {
    return http.get<Project>(`/v1/projects/${projectKey}`)
  },
  
  // 创建项目
  createProject(data: ProjectCreate) {
    return http.post<Project>('/v1/projects', data)
  },
  
  // 更新项目
  updateProject(projectKey: string, data: ProjectUpdate) {
    return http.put<Project>(`/v1/projects/${projectKey}`, data)
  },
  
  // 删除项目
  deleteProject(projectKey: string) {
    return http.delete(`/v1/projects/${projectKey}`)
  },
  
  // 获取项目统计
  getProjectStats(projectKey: string) {
    return http.get<ProjectStats>(`/v1/projects/${projectKey}/stats`)
  }
}
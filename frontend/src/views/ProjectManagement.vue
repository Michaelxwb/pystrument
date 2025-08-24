<template>
  <div class="project-management">
    <div class="page-header">
      <h2>项目管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建项目
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-section">
      <el-form :model="filters" inline>
        <el-form-item label="项目名称">
          <el-input
            v-model="filters.name"
            placeholder="请输入项目名称"
            @keyup.enter="loadProjects"
            clearable
          />
        </el-form-item>
        <el-form-item label="框架类型">
          <el-select
            v-model="filters.framework"
            placeholder="请选择框架"
            clearable
          >
            <el-option label="Flask" value="flask" />
            <el-option label="Django" value="django" />
            <el-option label="FastAPI" value="fastapi" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filters.status"
            placeholder="请选择状态"
            clearable
          >
            <el-option label="活跃" value="active" />
            <el-option label="暂停" value="paused" />
            <el-option label="已删除" value="deleted" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadProjects">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 项目列表 -->
    <div class="project-list">
      <el-table
        v-loading="loading"
        :data="projects"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="项目名称" min-width="150">
          <template #default="{ row }">
            <div class="project-name">
              <el-link
                @click="viewProject(row)"
                type="primary"
                :underline="false"
              >
                {{ row.name }}
              </el-link>
              <el-tag
                v-if="row.status === 'active'"
                type="success"
                size="small"
                class="status-tag"
              >
                活跃
              </el-tag>
              <el-tag
                v-else-if="row.status === 'paused'"
                type="warning"
                size="small"
                class="status-tag"
              >
                暂停
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="framework" label="框架" width="100">
          <template #default="{ row }">
            <el-tag :type="getFrameworkTagType(row.framework)" size="small">
              {{ row.framework }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="description" label="描述" min-width="200" />
        
        <el-table-column label="性能统计" width="150">
          <template #default="{ row }">
            <div class="performance-stats">
              <div>今日请求: {{ row.stats?.today_requests || 0 }}</div>
              <div>平均响应: {{ row.stats?.avg_response_time || 0 }}ms</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="viewProject(row)"
            >
              查看
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="editProject(row)"
            >
              编辑
            </el-button>
            <el-popconfirm
              title="确定要删除这个项目吗？"
              @confirm="deleteProject(row)"
            >
              <template #reference>
                <el-button
                  type="danger"
                  size="small"
                >
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadProjects"
        @current-change="loadProjects"
      />
    </div>

    <!-- 创建/编辑项目对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingProject ? '编辑项目' : '创建项目'"
      width="600px"
    >
      <el-form
        ref="projectFormRef"
        :model="projectForm"
        :rules="projectFormRules"
        label-width="100px"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input
            v-model="projectForm.name"
            placeholder="请输入项目名称"
          />
        </el-form-item>
        
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="projectForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
        
        <el-form-item label="框架类型" prop="framework">
          <el-select
            v-model="projectForm.framework"
            placeholder="请选择框架类型"
            style="width: 100%"
          >
            <el-option label="Flask" value="flask" />
            <el-option label="Django" value="django" />
            <el-option label="FastAPI" value="fastapi" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="项目URL" prop="base_url">
          <el-input
            v-model="projectForm.base_url"
            placeholder="https://api.yourproject.com"
          />
        </el-form-item>
        
        <el-form-item label="采样率" prop="sampling_rate">
          <el-slider
            v-model="projectForm.sampling_rate"
            :min="1"
            :max="100"
            :step="1"
            show-stops
            show-input
          />
          <div class="form-tip">设置性能数据采样率（1-100%）</div>
        </el-form-item>
        
        <el-form-item label="AI分析" prop="enable_ai_analysis">
          <el-switch
            v-model="projectForm.enable_ai_analysis"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="submitProject"
        >
          {{ editingProject ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { projectApi } from '@/api/project'
import type { Project, ProjectCreate, ProjectUpdate } from '@/types/project'

// 定义组件名称
defineOptions({
  name: 'ProjectManagement'
})

// Vue Router
const router = useRouter()

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const editingProject = ref<Project | null>(null)
const projects = ref<Project[]>([])

// 筛选条件
const filters = reactive({
  name: '',
  framework: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 项目表单
const projectForm = reactive<ProjectCreate>({
  name: '',
  description: '',
  framework: 'flask',
  base_url: '',
  sampling_rate: 10,
  enable_ai_analysis: true
})

// 表单验证规则
const projectFormRules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '描述不能超过200个字符', trigger: 'blur' }
  ],
  framework: [
    { required: true, message: '请选择框架类型', trigger: 'change' }
  ],
  base_url: [
    { type: 'url', message: '请输入正确的URL格式', trigger: 'blur' }
  ]
}

const projectFormRef = ref()

// 方法
const loadProjects = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...filters
    }
    
    const response = await projectApi.getProjects(params)
    
    projects.value = response.data.projects
    pagination.total = response.data.total
    pagination.page = response.data.page
    pagination.size = response.data.size
  } catch (error) {
    ElMessage.error('加载项目列表失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.name = ''
  filters.framework = ''
  filters.status = ''
  pagination.page = 1
  loadProjects()
}

const viewProject = (project: Project) => {
  // 跳转到项目详情页
  router.push(`/projects/${project.project_key}`)
}

const editProject = (project: Project) => {
  editingProject.value = project
  Object.assign(projectForm, {
    name: project.name,
    description: project.description,
    framework: project.framework,
    base_url: project.base_url,
    sampling_rate: project.config?.sampling_rate || 10,
    enable_ai_analysis: project.config?.enable_ai_analysis ?? true
  })
  showCreateDialog.value = true
}

const submitProject = async () => {
  if (!projectFormRef.value) return
  
  try {
    await projectFormRef.value.validate()
    submitting.value = true
    
    if (editingProject.value) {
      // 更新项目
      await projectApi.updateProject(editingProject.value.project_key, projectForm as ProjectUpdate)
      ElMessage.success('项目更新成功')
    } else {
      // 创建项目
      await projectApi.createProject(projectForm)
      ElMessage.success('项目创建成功')
    }
    
    showCreateDialog.value = false
    resetForm()
    loadProjects()
  } catch (error) {
    if (error !== false) { // 排除表单验证失败的情况
      ElMessage.error(editingProject.value ? '项目更新失败' : '项目创建失败')
    }
  } finally {
    submitting.value = false
  }
}

const deleteProject = async (project: Project) => {
  try {
    await projectApi.deleteProject(project.project_key)
    ElMessage.success('项目删除成功')
    loadProjects()
  } catch (error) {
    ElMessage.error('项目删除失败')
  }
}

const resetForm = () => {
  editingProject.value = null
  Object.assign(projectForm, {
    name: '',
    description: '',
    framework: 'flask',
    base_url: '',
    sampling_rate: 10,
    enable_ai_analysis: true
  })
  projectFormRef.value?.resetFields()
}

const getFrameworkTagType = (framework: string) => {
  const typeMap: Record<string, string> = {
    flask: 'success',
    django: 'primary',
    fastapi: 'warning',
    other: 'info'
  }
  return typeMap[framework] || 'info'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.project-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.filter-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.project-list {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.project-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-tag {
  margin-left: 8px;
}

.performance-stats {
  font-size: 12px;
  color: #606266;
}

.performance-stats div {
  margin-bottom: 2px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
<template>
  <div class="error-404">
    <div class="error-container">
      <div class="error-code">404</div>
      <div class="error-message">页面不存在</div>
      <div class="error-description">
        抱歉，您访问的页面不存在或已被删除
      </div>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">
          <el-icon><HomeFilled /></el-icon>
          返回首页
        </el-button>
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回上页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

// 定义组件名称
defineOptions({
  name: 'NotFound'
})

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style lang="scss" scoped>
.error-404 {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  
  .error-container {
    text-align: center;
    color: white;
    
    .error-code {
      font-size: 120px;
      font-weight: bold;
      margin-bottom: 20px;
      opacity: 0.8;
    }
    
    .error-message {
      font-size: 32px;
      margin-bottom: 16px;
    }
    
    .error-description {
      font-size: 16px;
      margin-bottom: 40px;
      opacity: 0.8;
    }
    
    .error-actions {
      display: flex;
      gap: 16px;
      justify-content: center;
    }
  }
}
</style>
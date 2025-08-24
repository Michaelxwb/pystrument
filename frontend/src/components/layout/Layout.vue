<template>
  <div class="layout-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside :width="sidebarWidth" class="sidebar-container">
        <div class="logo-container">
          <h2>性能分析平台</h2>
        </div>
        <el-menu
          :default-active="$route.path"
          class="sidebar-menu"
          router
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/dashboard">
            <el-icon><Dashboard /></el-icon>
            <span>仪表板</span>
          </el-menu-item>
          <el-menu-item index="/projects">
            <el-icon><Collection /></el-icon>
            <span>项目管理</span>
          </el-menu-item>
          <el-menu-item index="/performance">
            <el-icon><Monitor /></el-icon>
            <span>性能监控</span>
          </el-menu-item>
          <el-menu-item index="/analysis">
            <el-icon><DataAnalysis /></el-icon>
            <span>AI分析</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区域 -->
      <el-container>
        <!-- 顶部导航栏 -->
        <el-header class="navbar">
          <div class="navbar-left">
            <el-button
              type="text"
              @click="toggleSidebar"
              class="sidebar-toggle"
            >
              <el-icon><Expand /></el-icon>
            </el-button>
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item v-if="$route.meta.title">
                {{ $route.meta.title }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="navbar-right">
            <el-dropdown>
              <span class="el-dropdown-link">
                <el-avatar :size="30" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
                <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>个人中心</el-dropdown-item>
                  <el-dropdown-item>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <!-- 主内容 -->
        <el-main class="app-main">
          <router-view v-slot="{ Component, route }">
            <transition name="fade-transform" mode="out-in">
              <component :is="Component" :key="route.fullPath" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const sidebarWidth = ref('200px')

const toggleSidebar = () => {
  sidebarWidth.value = sidebarWidth.value === '200px' ? '64px' : '200px'
}
</script>

<style lang="scss" scoped>
.layout-container {
  height: 100vh;
  
  .el-container {
    height: 100%;
  }
}

.sidebar-container {
  background: #304156;
  min-height: 100vh;
  transition: width 0.28s;
  
  .logo-container {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #2b3a4b;
    
    h2 {
      color: #ffffff;
      font-size: 16px;
      margin: 0;
    }
  }
  
  .sidebar-menu {
    border: none;
    height: calc(100vh - 60px);
    overflow: auto;
    
    .el-menu-item {
      height: 50px;
      line-height: 50px;
      
      &.is-active {
        background-color: #409EFF !important;
      }
    }
  }
}

.navbar {
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
  
  .navbar-left {
    display: flex;
    align-items: center;
    
    .sidebar-toggle {
      margin-right: 20px;
      
      .el-icon {
        font-size: 18px;
      }
    }
  }
  
  .navbar-right {
    .el-dropdown-link {
      display: flex;
      align-items: center;
      cursor: pointer;
      
      .el-avatar {
        margin-right: 8px;
      }
    }
  }
}

.app-main {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

// 页面切换动画
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
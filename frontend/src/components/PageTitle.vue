<template>
  <div class="page-title">
    <h1 class="main-title">{{ title }}</h1>
    <p class="sub-title" v-if="subtitle">{{ subtitle }}</p>
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  }
})
</script>

<style lang="scss" scoped>
.page-title {
  margin-bottom: 24px;
  
  .main-title {
    margin: 0 0 8px 0;
    color: #303133;
    font-size: 24px;
    font-weight: 600;
  }
  
  .sub-title {
    margin: 0;
    color: #909399;
    font-size: 14px;
  }
}
</style>
<template>
  <div class="layout">
    <!-- 顶部导航栏 -->
    <BackstageHeader />
    <!-- 主体部分：左侧侧边栏 + 右侧内容区域 -->
    <div class="main-content">
      <BackstageAside />
      <div class="content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import BackstageHeader from '../components/BackstageHeader.vue'
import BackstageAside from '../components/BackstageAside.vue'
</script>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: #fff;
}
.main-content {
  display: flex;
  flex: 1;
  background: #fff;
}
.content {
  flex: 1;
  padding: 16px;
  overflow: auto;
  min-height: 0;
  background: #fff;
}
</style>
<style>
html, body, #app {
  height: 100%;
  overflow: hidden;
}
</style> 
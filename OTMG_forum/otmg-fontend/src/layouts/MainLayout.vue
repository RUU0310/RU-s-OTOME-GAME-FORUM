<template>
  <div class="main-layout">
    <MainHeader 
      @search-change="handleSearchChange"
    />
    <div class="main-content">
      <router-view 
        :searchText="searchText"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MainHeader from '../components/MainHeader.vue'

// 搜索状态
const searchText = ref('')

// 处理MainHeader的事件
const handleSearchChange = (text) => {
  searchText.value = text
}
</script>

<style scoped>
.main-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}
.main-content {
  flex: 1;
  overflow: auto;
  background: #f8f9fa;
  min-height: 0;
}
</style>

<style>
html, body, #app {
  height: 100%;
  overflow: hidden;
}
</style>

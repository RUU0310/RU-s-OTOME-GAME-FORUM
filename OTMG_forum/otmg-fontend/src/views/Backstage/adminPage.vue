<template>
  <div class="admin-info-container">
    <div style="display: flex; align-items: center; margin-bottom: 32px;">
      <img :src="user.avatar || defaultAvatar" class="admin-avatar" alt="头像" />
      <div style="margin-left: 24px;">
        <h2>{{ user.nickname || user.username }}</h2>
        <el-tag type="success" v-if="user.role === 'admin'">管理员</el-tag>
        <el-tag v-else-if="user.role === 'publisher'" type="warning">发行商</el-tag>
        <el-tag v-else>普通用户</el-tag>
      </div>
    </div>
    <el-descriptions title="基本信息" :column="1">
      <el-descriptions-item label="用户名">{{ user.username }}</el-descriptions-item>
      <el-descriptions-item label="昵称">{{ user.nickname }}</el-descriptions-item>
      <el-descriptions-item label="手机号">{{ user.phone }}</el-descriptions-item>
      <el-descriptions-item label="邮箱">{{ user.email }}</el-descriptions-item>
      <el-descriptions-item label="简介">{{ user.bio }}</el-descriptions-item>
      <el-descriptions-item label="角色">
        <span v-if="user.role === 'admin'">管理员</span>
        <span v-else-if="user.role === 'publisher'">发行商</span>
        <span v-else>普通用户</span>
      </el-descriptions-item>
    </el-descriptions>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const user = ref({})
const defaultAvatar = '/src/assets/logo.png'
onMounted(async () => {
  const localUser = JSON.parse(localStorage.getItem('user') || 'null')
  if (!localUser) {
    window.location.href = '/login'
    return
  }
  try {
    const res = await axios.get(`http://localhost:5000/users/${localUser.user_id}`)
    user.value = res.data
  } catch {
    user.value = localUser
  }
})
</script>
<style scoped>
.admin-info-container {
  max-width: 600px;
  margin: 40px auto 0 auto;
  padding: 0 24px;
}
.admin-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  background: #f0f0f0;
}
</style>

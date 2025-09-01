<script setup>
import { ref, onMounted } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const username = ref('')
const avatar = ref('')
const defaultAvatar = '/src/assets/logo.png' // 可替换为你的默认头像

const goToPage = (path) => {
  router.push(path)
}

const handleLogout = () => {
  localStorage.removeItem('user')
  router.push('/login')
}

onMounted(async () => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (!user) {
    router.push('/login')
    return
  }
  try {
    // 调用后端接口获取用户详细信息
    const res = await axios.get(`http://localhost:5000/users/${user.user_id}`)
    if (res.data && res.data.user_id) {
      username.value = res.data.nickname || res.data.username || '用户'
      avatar.value = res.data.avatar || defaultAvatar
    } else {
      username.value = user.nickname || user.username || '用户'
      avatar.value = user.avatar || defaultAvatar
    }
  } catch (e) {
    // 如果接口失败，回退到本地信息
    username.value = user.nickname || user.username || '用户'
    avatar.value = user.avatar || defaultAvatar
  }
})
</script>

<template>
  <div style="height: 50px; border-bottom: 1px solid #ccc; display: flex; align-items: center; background: #fff;">
    <div style="width: 150px; text-align: center; font-weight: bold; color: dodgerblue;">后台管理</div>
    <div style="flex: 1;"></div>
    <div style="width: 160px;">
      <el-dropdown>
        <span class="el-dropdown-link">
          <img :src="avatar" class="header-avatar" alt="头像" />
          {{ username }}
          <el-icon class="el-icon--right">
            <arrow-down />
          </el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="goToPage('/backstage/adminPage')">个人信息</el-dropdown-item>
            <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<style scoped>
.el-dropdown-link:focus {
  outline: none;
}
.el-dropdown-link {
  cursor: pointer;
  color: var(--el-color-primary);
  display: flex;
  align-items: center;
}
.header-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 8px;
  background: #f0f0f0;
}
</style> 
<template>
  <div class="sidebar">
    <el-menu default-active="1" class="el-menu-vertical-demo">
      <el-menu-item index="1" @click="goToPage('/backstage/games')">游戏管理</el-menu-item>
      <el-menu-item index="1.5" @click="goToPage('/backstage/game-audit')" :class="{'has-pending-audit': hasPendingAudit}">
        游戏审核
        <span v-if="hasPendingAudit" class="red-dot"></span>
      </el-menu-item>
      <el-menu-item index="2" @click="goToPage('/backstage/characters')">游戏角色</el-menu-item>
      <el-menu-item index="3" @click="goToPage('/backstage/users')" :class="{'has-upgrade-pending': hasUpgradePending}">
        用户管理
        <span v-if="hasUpgradePending" class="red-dot"></span>
      </el-menu-item>
      <el-menu-item index="4" @click="goToPage('/backstage/groups')">小组管理</el-menu-item>
      <el-menu-item index="5" @click="goToPage('/backstage/posts')">帖子管理</el-menu-item>
      <el-menu-item index="6" @click="goToPage('/backstage/group-buys')">拼团管理</el-menu-item>
      <el-menu-item index="7" @click="goToPage('/backstage/tags')">标签管理</el-menu-item>
      <el-menu-item index="8" @click="goToPage('/backstage/character-tags')">角色标签管理</el-menu-item>
      <!-- 可继续添加更多菜单项 -->
    </el-menu>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
const router = useRouter()
const goToPage = (path) => {
  router.push(path)
}
const hasUpgradePending = ref(false)
const hasPendingAudit = ref(false)

function setUpgradePending(val) {
  hasUpgradePending.value = !!val
}

function setPendingAudit(val) {
  hasPendingAudit.value = !!val
}

function eventHandler(e) {
  if (e && e.detail !== undefined) setUpgradePending(e.detail)
}

function auditEventHandler(e) {
  if (e && e.detail !== undefined) setPendingAudit(e.detail)
}

onMounted(() => {
  window.addEventListener('set-user-upgrade-pending', eventHandler)
  window.addEventListener('set-pending-audit', auditEventHandler)
  
  // 主动请求一次，保证红点及时
  axios.get('http://localhost:5000/users').then(res => {
    if (Array.isArray(res.data)) {
      setUpgradePending(res.data.some(u => u.upgrade_status === 'pending'))
    }
  })
  
  // 检查待审核游戏
  axios.get('http://localhost:5000/games/audit?status=pending').then(res => {
    if (res.data.status === 'success') {
      setPendingAudit(res.data.results.length > 0)
    }
  })
})

onUnmounted(() => {
  window.removeEventListener('set-user-upgrade-pending', eventHandler)
  window.removeEventListener('set-pending-audit', auditEventHandler)
})
</script>

<style scoped>
.sidebar {
  width: 200px;
  height: calc(100vh - 50px);
  background-color: #fff;
  border-right: 1px solid #ccc;
  overflow-y: auto;
}
.el-menu-vertical-demo {
  width: 100%;
}
.has-upgrade-pending,
.has-pending-audit {
  position: relative;
}
.red-dot {
  position: absolute;
  top: 16px;
  right: 18px;
  width: 10px;
  height: 10px;
  background: #ff4d4f;
  border-radius: 50%;
  box-shadow: 0 0 6px #ff4d4f;
  z-index: 2;
}
</style> 
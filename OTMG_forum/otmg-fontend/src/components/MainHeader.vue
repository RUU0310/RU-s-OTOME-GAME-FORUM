<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const username = ref('未登录')
const avatar = ref('')
const defaultAvatar = '/src/assets/logo.png'
const userId = ref(null)
const userRole = ref(null)
const showHeaderDot = ref(false)

// 搜索相关
const searchText = ref('')

// 判断是否在游戏一览页面
const isGamesOverview = computed(() => {
  return route.path === '/games-overview'
})

// 定义事件
const emit = defineEmits(['search-change'])

const goToPage = (path) => {
  if (!userId.value) return
  router.push(path)
}

const handleLogout = () => {
  localStorage.removeItem('user')
  router.push('/login')
}

// 搜索处理函数
const handleSearchChange = () => {
  emit('search-change', searchText.value)
}

function setHeaderDot(val) { showHeaderDot.value = !!val }
function eventHandler(e) { if (e && e.detail !== undefined) setHeaderDot(e.detail) }

let headerDotTimer = null
async function refreshHeaderDot() {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (!user) return
  try {
    const reqRes = await axios.get(`http://localhost:5000/api/group-buy/group-buys/requests?leader_id=${user.user_id}`)
    const hasPendingRequest = reqRes.data && reqRes.data.success && reqRes.data.data && reqRes.data.data.some(r => r.status === 'pending')
    const msgRes = await axios.get(`http://localhost:5000/api/messages/?user_id=${user.user_id}`)
    const hasUnreadMsg = msgRes.data && msgRes.data.success && msgRes.data.data && msgRes.data.data.some(m => !m.is_read)
    showHeaderDot.value = hasPendingRequest || hasUnreadMsg
  } catch {}
}

onMounted(async () => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (!user) {
    username.value = '未登录'
    avatar.value = defaultAvatar
    userId.value = null
    userRole.value = null
    return
  }
  userId.value = user.user_id
  userRole.value = user.role
  try {
    const res = await axios.get(`http://localhost:5000/users/${user.user_id}`)
    if (res.data && res.data.user_id) {
      username.value = res.data.nickname || res.data.username || '用户'
      avatar.value = res.data.avatar || defaultAvatar
      userRole.value = res.data.role
    } else {
      username.value = user.nickname || user.username || '用户'
      avatar.value = user.avatar || defaultAvatar
      userRole.value = user.role
    }
    // 主动请求消息和拼团申请状态，决定是否显示感叹号
    await refreshHeaderDot()
  } catch (e) {
    username.value = user.nickname || user.username || '用户'
    avatar.value = user.avatar || defaultAvatar
    userRole.value = user.role
  }
  await refreshHeaderDot()
  headerDotTimer = setInterval(refreshHeaderDot, 5000)
  window.addEventListener('set-header-notification-dot', eventHandler)
})

onUnmounted(() => {
  window.removeEventListener('set-header-notification-dot', eventHandler)
  if (headerDotTimer) clearInterval(headerDotTimer)
})
</script>

<template>
  <div class="main-header">
    <!-- 装饰性星星 -->
    <div class="stars">
      <div class="star star-1">✨</div>
      <div class="star star-2">💫</div>
      <div class="star star-3">⭐</div>
      <div class="star star-4">✨</div>
    </div>

    <div class="main-header-left">
      <button class="heart-button pixel-text" @click="goToPage('/games-overview')">
        <span class="button-text">游戏一览</span>
      </button>
      <button class="heart-button pixel-text" style="margin-left: 16px;" @click="goToPage('/group-overview')">
        <span class="button-text">小组讨论</span>
      </button>
      <button class="heart-button pixel-text" style="margin-left: 16px;" @click="goToPage('/group-buy-overview')">
        <span class="button-text">周边拼团</span>
      </button>
      <button class="heart-button pixel-text" style="margin-left: 16px;" @click="goToPage('/fantasy-rating')">
        <span class="button-text">幻想时间</span>
      </button>
    </div>

    <div class="main-header-right">
      
      <el-dropdown>
        <span class="el-dropdown-link pixel-text">
          <div class="avatar-container">
            <img :src="avatar || defaultAvatar" class="header-avatar" alt="头像" />
            <!-- 发行商标识 - 头像右下角 -->
            <div v-if="userRole === 'publisher'" class="publisher-badge">
              <span class="publisher-icon">🎮</span>
            </div>
            <div class="avatar-decoration">💝</div>
            <div v-if="showHeaderDot" class="exclamation-badge">❗</div>
          </div>
          <span class="username-text">{{ username }}</span>
          <span class="heart-icon">💗</span>
          
        </span>
        <template #dropdown>
          <el-dropdown-menu class="kawaii-dropdown">
            <el-dropdown-item @click="goToPage('/user')" :disabled="!userId" class="pixel-text">
              <span class="menu-icon">🌸</span> 个人中心
            </el-dropdown-item>
            <el-dropdown-item @click="goToPage('/messages')" :disabled="!userId" class="pixel-text">
              <span class="menu-icon">🔔</span> 消息通知
            </el-dropdown-item>
            <el-dropdown-item @click="handleLogout" :disabled="!userId" class="pixel-text">
              <span class="menu-icon">👋</span> 退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 浮动爱心动画 -->
    <div class="floating-hearts">
      <div class="floating-heart heart-anim-1">💕</div>
      <div class="floating-heart heart-anim-2">💖</div>
      <div class="floating-heart heart-anim-3">💗</div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

.pixel-text {
  font-family: 'Press Start 2P', 'Microsoft YaHei', sans-serif;
  font-size: 12px;
}

.main-header {
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg,
  #ff9a9e 0%,
  #fecfef 25%,
  #fecfef 75%,
  #ff9a9e 100%);
  border-bottom: 3px solid #ff69b4;
  padding: 0 32px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(255, 105, 180, 0.3);
}

.main-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
      radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.3) 2px, transparent 2px),
      radial-gradient(circle at 80% 50%, rgba(255, 255, 255, 0.3) 1px, transparent 1px),
      radial-gradient(circle at 40% 20%, rgba(255, 255, 255, 0.2) 1px, transparent 1px);
  background-size: 30px 30px, 50px 50px, 40px 40px;
  pointer-events: none;
}

.stars {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.star {
  position: absolute;
  font-size: 16px;
  animation: twinkle 2s infinite ease-in-out;
}

.star-1 { top: 15px; left: 10%; animation-delay: 0s; }
.star-2 { top: 20px; right: 15%; animation-delay: 0.5s; }
.star-3 { bottom: 15px; left: 25%; animation-delay: 1s; }
.star-4 { bottom: 20px; right: 30%; animation-delay: 1.5s; }

@keyframes twinkle {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

.main-header-left {
  display: flex;
  align-items: center;
  z-index: 2;
}

.main-header-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
}

.site-title {
  color: #ff1493;
  font-size: 16px;
  font-weight: bold;
  animation: pulse 2s infinite ease-in-out;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.main-header-right {
  display: flex;
  align-items: center;
  z-index: 2;
  gap: 16px;
}


.heart-button {
  background: linear-gradient(45deg, #ff69b4, #ff1493);
  border: 3px solid #fff;
  border-radius: 25px;
  padding: 12px 20px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(255, 20, 147, 0.4);
  position: relative;
  overflow: hidden;
}

.heart-button::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transform: rotate(45deg);
  transition: all 0.6s;
  opacity: 0;
}

.heart-button:hover::before {
  animation: shine 0.6s ease-in-out;
}

.heart-button:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 20px rgba(255, 20, 147, 0.6);
}

.heart-button:active {
  transform: translateY(0) scale(0.98);
}

@keyframes shine {
  0% { left: -50%; opacity: 0; }
  50% { opacity: 1; }
  100% { left: 150%; opacity: 0; }
}

.heart {
  font-size: 16px;
  animation: heartBeat 1.5s infinite ease-in-out;
}

@keyframes heartBeat {
  0%, 100% { transform: scale(1); }
  25% { transform: scale(1.1); }
  50% { transform: scale(1); }
  75% { transform: scale(1.05); }
}

.button-text {
  color: white;
  font-weight: bold;
}

.el-dropdown-link:focus {
  outline: none;
}

.el-dropdown-link {
  cursor: pointer;
  color: #ff1493;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
  border: 2px solid #ff69b4;
}

.el-dropdown-link:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 105, 180, 0.3);
}

.avatar-container {
  position: relative;
  display: inline-block;
}

.header-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #ff69b4;
  background: #f0f0f0;
  transition: all 0.3s ease;
}

.avatar-decoration {
  position: absolute;
  top: -5px;
  right: -5px;
  font-size: 12px;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.username-text {
  color: #ff1493;
  font-weight: bold;
}

.heart-icon {
  font-size: 14px;
  animation: heartBeat 1.5s infinite ease-in-out;
}

.floating-hearts {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.floating-heart {
  position: absolute;
  font-size: 20px;
  opacity: 0.7;
}

.heart-anim-1 {
  top: 10px;
  left: 5%;
  animation: float 4s infinite ease-in-out;
  animation-delay: 0s;
}

.heart-anim-2 {
  top: 30px;
  right: 10%;
  animation: float 3s infinite ease-in-out;
  animation-delay: 1s;
}

.heart-anim-3 {
  bottom: 10px;
  left: 80%;
  animation: float 3.5s infinite ease-in-out;
  animation-delay: 2s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0.7;
  }
  50% {
    transform: translateY(-10px) rotate(5deg);
    opacity: 1;
  }
}

/* 下拉菜单样式 */
:deep(.kawaii-dropdown) {
  background: linear-gradient(135deg, #ffeef8, #fff0f5);
  border: 2px solid #ff69b4;
  border-radius: 15px;
  box-shadow: 0 8px 25px rgba(255, 105, 180, 0.3);
}

:deep(.kawaii-dropdown .el-dropdown-menu__item) {
  color: #ff1493;
  padding: 12px 20px;
  transition: all 0.3s ease;
  border-radius: 10px;
  margin: 4px;
}

:deep(.kawaii-dropdown .el-dropdown-menu__item:hover) {
  background: linear-gradient(45deg, #ff69b4, #ff1493);
  color: white;
  transform: translateX(5px);
}

.menu-icon {
  margin-right: 8px;
  font-size: 14px;
}

/* 发行商标识样式 */
.publisher-badge {
  position: absolute;
  bottom: -2px;
  right: -2px;
  background: #ffeb3b;
  border: 2px solid white;
  border-radius: 50%;
  width: 14px;
  height: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.publisher-icon {
  font-size: 8px;
  color: #333;
  line-height: 1;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .search-box {
    width: 160px;
  }
}

@media (max-width: 768px) {
  .main-header {
    padding: 0 16px;
    height: 70px;
  }

  .pixel-text {
    font-size: 10px;
  }

  .site-title {
    font-size: 12px;
  }

  .heart-button {
    padding: 8px 12px;
    font-size: 10px;
  }

  .header-avatar {
    width: 30px;
    height: 30px;
  }

  .publisher-badge {
    width: 12px;
    height: 12px;
    bottom: -1px;
    right: -1px;
  }

  .publisher-icon {
    font-size: 6px;
  }

  .search-section {
    display: none; /* 在移动端隐藏搜索区域 */
  }
  
  .main-header-right {
    gap: 8px;
  }
}

.exclamation-badge {
  position: absolute;
  top: -8px;
  left: -8px;
  color: #ff4d4f;
  font-size: 22px;
  font-weight: bold;
  background: none;
  border: none;
  box-shadow: none;
  z-index: 3;
  pointer-events: none;
}
</style>
<template>
  <div v-if="group" class="group-detail-container">
    <!-- 小组信息卡片 -->
    <div class="group-info-card">
      <div class="group-info-row">
        <div class="avatar-wrapper">
          <img :src="getFullImageUrl(group.avatar)" v-if="group.avatar" class="group-avatar" />
          <div v-else class="default-avatar">🌟</div>
        </div>
        <div class="group-info-main">
          <h2 class="group-name">
            <span v-if="group.is_official" class="official-badge">官方</span>
            {{ group.name }}
          </h2>
          <p class="group-description">{{ group.description }}</p>
          <div class="member-info">
            <span class="member-count">👥 {{ group.member_count }} 人</span>
            <button class="member-list-btn" @click="showMembers = true">查看成员</button>
            <button v-if="!isMember" class="join-btn" @click="joinGroup"> 加入小组</button>
            <button v-else class="leave-btn" @click="showLeaveConfirm = true"> 退出小组</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="category-section">
        <div class="category-btn-group">
          <button
              :class="['category-btn', selectedCategory === 'all' ? 'active' : '']"
              @click="selectedCategory = 'all'"
          >
            🌸 全部分类
          </button>
          <button
              v-for="cat in categories"
              :key="cat.category_id"
              :class="['category-btn', selectedCategory === cat.category_id ? 'active' : '']"
              @click="selectedCategory = cat.category_id"
          >
            {{ cat.name }}
          </button>
        </div>
      </div>
      <div v-if="isMember" class="post-section">
        <button class="create-post-btn" @click="goToPostCreate">✨ 发布帖子</button>
      </div>
    </div>

    <!-- 帖子列表 -->
    <div v-if="filteredPosts.length" class="posts-section">
      <div class="posts-container">
        <div v-for="post in filteredPosts" :key="post.post_id" class="post-card">
          <div class="post-content">
            <h4 class="post-title" @click="goToPostDetail(post.post_id)">{{ post.title }}</h4>
            <div class="post-meta">
              <span class="author">👤 {{ post.nickname || post.username || '未知用户' }}</span>
              <span v-if="post.category_name" class="category">🏷️ {{ post.category_name }}</span>
              <span class="time">🕒 {{ formatTime(post.created_at) }}</span>
              <span class="likes">💝 {{ post.like_count }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 暂无帖子 -->
    <div v-else class="empty-state">
      <div class="empty-icon">📄</div>
      <p class="empty-text">还没有帖子哦～</p>
      <p class="empty-subtitle">快来发布第一个帖子吧！</p>
    </div>

    <!-- 小组成员抽屉 -->
    <el-drawer v-model="showMembers" title="🌺 小组成员" direction="rtl" size="340px">
      <ul v-if="members.length" class="member-list">
        <li v-for="m in members" :key="m.user_id" class="member-item">
          <div class="member-avatar-wrapper">
            <img :src="getFullImageUrl(m.avatar)" class="member-avatar" v-if="m.avatar" />
            <div v-else class="default-member-avatar">🌸</div>
          </div>
          <div class="member-info">
            <span class="member-nickname">{{ m.nickname || m.username || '未知用户' }}</span>
          </div>
        </li>
      </ul>
      <div v-else class="empty-members">
        <div class="empty-icon">👥</div>
        <p>暂无成员</p>
      </div>
    </el-drawer>

    <!-- 退出小组确认弹窗 -->
    <el-dialog v-model="showLeaveConfirm" title="💔 确认退出" width="320px" :close-on-click-modal="false">
      <div class="leave-confirm-content">
        <p>确定要退出该小组吗？</p>
        <p class="leave-hint">退出后将无法查看小组内容</p>
      </div>
      <template #footer>
        <button class="cancel-btn" @click="showLeaveConfirm = false">取消</button>
        <button class="confirm-btn" @click="leaveGroup">确认退出</button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'

const API_BASE_URL = 'http://localhost:5000'
const route = useRoute()
const router = useRouter()
const group = ref(null)
const isMember = ref(false)
const user = JSON.parse(localStorage.getItem('user') || 'null')
const posts = ref([])
const categories = ref([])
const showMembers = ref(false)
const members = ref([])
const showLeaveConfirm = ref(false)

const fetchGroup = async () => {
  const res = await axios.get(`${API_BASE_URL}/groups/${route.params.id}`)
  group.value = res.data
}

const checkIsMember = async () => {
  if (!user) return
  const res = await axios.get(`${API_BASE_URL}/groups/${route.params.id}/members`)
  isMember.value = res.data.some(m => m.user_id === user.user_id)
}

const joinGroup = async () => {
  if (!user) return
  await axios.post(`${API_BASE_URL}/groups/${route.params.id}/join`, { user_id: user.user_id })
  isMember.value = true
  group.value.member_count += 1
}

const leaveGroup = async () => {
  if (!user) return
  showLeaveConfirm.value = false
  await axios.post(`${API_BASE_URL}/groups/${route.params.id}/leave`, { user_id: user.user_id })
  isMember.value = false
  group.value.member_count -= 1
}

const goToPostCreate = () => {
  router.push(`/group/${route.params.id}/post/create`)
}

const getFullImageUrl = (avatar) => {
  if (!avatar) return ''
  if (avatar.startsWith('http')) return avatar
  return `${API_BASE_URL}/static/${avatar}`
}

const fetchPosts = async () => {
  const res = await axios.get(`${API_BASE_URL}/groups/${route.params.id}/posts`)
  posts.value = res.data
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchCategories = async () => {
  const res = await axios.get(`${API_BASE_URL}/post-categories`)
  categories.value = res.data
}

const selectedCategory = ref('all')

const filteredPosts = computed(() => {
  if (selectedCategory.value === 'all') return posts.value
  return posts.value.filter(post => post.category_id === selectedCategory.value)
})

const fetchMembers = async () => {
  const res = await axios.get(`${API_BASE_URL}/groups/${route.params.id}/members`)
  if (res.data && res.data.length) {
    const userIds = res.data.map(m => m.user_id)
    const userRes = await axios.get(`${API_BASE_URL}/users`)
    const userMap = {}
    userRes.data.forEach(u => { userMap[u.user_id] = u })
    members.value = res.data.map(m => ({
      ...m,
      nickname: userMap[m.user_id]?.nickname,
      username: userMap[m.user_id]?.username,
      avatar: userMap[m.user_id]?.avatar
    }))
  } else {
    members.value = []
  }
}

watch(showMembers, (val) => {
  if (val) fetchMembers()
})

const goToPostDetail = (postId) => {
  router.push(`/post/${postId}`)
}

onMounted(async () => {
  await fetchGroup()
  await checkIsMember()
  await fetchPosts()
  await fetchCategories()
})

onBeforeUnmount(() => {
  // No need to clean up editor as it's handled by vue-quill
})
</script>

<style scoped>
.group-detail-container {
  min-height: 100vh;
  background: #fdf2f8;
  padding: 1.5rem 1rem;
  font-family: 'PingFang SC', 'Hiragino Sans GB', sans-serif;
}

/* 统一按钮基础样式 */
button {
  border: none;
  outline: none;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
  border-radius: 12px;
}

/* 小组信息卡片 */
.group-info-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 1.5rem;
  border: 2px solid #f8bbd9;
}

.group-info-row {
  display: flex;
  align-items: flex-start;
  gap: 2rem;
}

.avatar-wrapper {
  flex-shrink: 0;
}

.group-avatar {
  width: 100px;
  height: 100px;
  border-radius: 16px;
  object-fit: cover;
  border: 2px solid rgba(216, 27, 96, 0.2);
}

.default-avatar {
  width: 100px;
  height: 100px;
  border-radius: 16px;
  background: #f8bbd9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
  border: 2px solid rgba(216, 27, 96, 0.2);
}

.group-info-main {
  flex: 1;
}

.group-name {
  font-size: 1.8rem;
  font-weight: 600;
  color: #d81b60;
  margin: 0 0 0.8rem 0;
}

.group-description {
  color: #8e24aa;
  font-size: 1rem;
  line-height: 1.5;
  margin: 0 0 1rem 0;
}

.member-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.member-count {
  color: #8e24aa;
  font-size: 0.9rem;
  font-weight: 500;
}

.member-list-btn {
  padding: 0.4rem 0.8rem;
  font-size: 0.8rem;
  color: #d81b60;
  background: rgba(248, 187, 217, 0.3);
  border: 1px solid #f8bbd9;
  border-radius: 12px;
  font-weight: 500;
}

.member-list-btn:hover {
  background: #f8bbd9;
  color: white;
  transform: translateY(-1px);
}

.join-btn {
  background: #e91e63;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 0.4rem 0.8rem;
  font-size: 0.8rem;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(233, 30, 99, 0.2);
}

.join-btn:hover {
  background: #c2185b;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(233, 30, 99, 0.3);
}

.leave-btn {
  padding: 0.4rem 0.8rem;
  font-size: 0.8rem;
  color: white;
  background: #ba68c8;
  border: none;
  border-radius: 12px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(186, 104, 200, 0.2);
}

.leave-btn:hover {
  background: #9c27b0;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(186, 104, 200, 0.3);
}

/* 操作栏 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 16px;
  padding: 1.2rem 1.5rem;
  border: 1px solid rgba(248, 187, 217, 0.3);
  flex-wrap: wrap;
  gap: 1rem;
}

.category-btn-group {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.category-btn {
  background: rgba(255, 255, 255, 0.7);
  border: 2px solid #f8bbd9;
  border-radius: 16px;
  padding: 0.5rem 1rem;
  font-size: 0.8rem;
  color: #d81b60;
  font-weight: 500;
  white-space: nowrap;
}

.category-btn:hover {
  background: rgba(248, 187, 217, 0.3);
  transform: translateY(-2px);
}

.category-btn.active {
  background: #d81b60;
  color: white;
  box-shadow: 0 4px 15px rgba(216, 27, 96, 0.2);
}

.create-post-btn {
  background: #e91e63;
  color: white;
  border: none;
  border-radius: 16px;
  padding: 0.6rem 1.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  box-shadow: 0 3px 10px rgba(233, 30, 99, 0.2);
}

.create-post-btn:hover {
  background: #c2185b;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(233, 30, 99, 0.3);
}

/* 帖子区域 */
.posts-section {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(248, 187, 217, 0.3);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #d81b60;
  margin: 0;
}

.decoration {
  font-size: 1.1rem;
  opacity: 0.7;
}

.posts-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.post-card {
  background: rgba(248, 240, 255, 0.6);
  border-radius: 15px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(142, 36, 170, 0.1);
}

.post-card:hover {
  transform: translateX(10px);
  background: rgba(248, 240, 255, 0.9);
  box-shadow: 0 8px 25px rgba(142, 36, 170, 0.1);
}

.post-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #6a1b99;
  margin: 0 0 0.8rem 0;
  line-height: 1.4;
  cursor: pointer;
  transition: color 0.3s ease;
}

.post-title:hover {
  color: #d81b60;
}

.post-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.85rem;
  opacity: 0.8;
}

.post-meta span {
  color: #8e24aa;
}

.author {
  font-weight: 500;
}

.category {
  background: rgba(142, 36, 170, 0.1);
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
  color: #6a1b99 !important;
}

.time {
  color: #ba68c8 !important;
}

.likes {
  color: #d81b60 !important;
  font-weight: 500;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 3rem 2rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  border: 1px solid rgba(248, 187, 217, 0.3);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.6;
}

.empty-text {
  font-size: 1.1rem;
  color: #8e24aa;
  margin: 0 0 0.5rem 0;
  font-weight: 500;
}

.empty-subtitle {
  font-size: 0.9rem;
  color: #ba68c8;
  margin: 0;
  opacity: 0.8;
}

/* 成员列表 */
.member-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(248, 187, 217, 0.2);
}

.member-item:last-child {
  border-bottom: none;
}

.member-avatar-wrapper {
  flex-shrink: 0;
}

.member-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(216, 27, 96, 0.2);
}

.default-member-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f8bbd9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  color: white;
  border: 2px solid rgba(216, 27, 96, 0.2);
}

.member-info {
  flex: 1;
}

.member-nickname {
  font-size: 0.95rem;
  color: #6a1b99;
  font-weight: 500;
}

.empty-members {
  text-align: center;
  padding: 2rem;
  color: #8e24aa;
}

.empty-members .empty-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  opacity: 0.6;
}

/* 弹窗按钮 */
.cancel-btn {
  background: rgba(248, 187, 217, 0.3);
  color: #d81b60;
  border: 1px solid #f8bbd9;
  padding: 0.5rem 1.2rem;
  font-size: 0.9rem;
  font-weight: 500;
  margin-right: 0.8rem;
}

.cancel-btn:hover {
  background: #f8bbd9;
  color: white;
  transform: translateY(-1px);
}

.confirm-btn {
  background: #e53e3e;
  color: white;
  border: 1px solid #e53e3e;
  padding: 0.5rem 1.2rem;
  font-size: 0.9rem;
  font-weight: 500;
}

.confirm-btn:hover {
  background: #c53030;
  border-color: #c53030;
  transform: translateY(-1px);
}

/* 退出确认弹窗 */
.leave-confirm-content {
  text-align: center;
  padding: 1rem;
}

.leave-confirm-content p {
  margin: 0 0 0.5rem 0;
  color: #6a1b99;
}

.leave-hint {
  font-size: 0.9rem;
  color: #ba68c8 !important;
  opacity: 0.8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .group-detail-container {
    padding: 1rem 0.8rem;
  }

  .group-info-card {
    padding: 1.5rem;
  }

  .group-info-row {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
  }

  .action-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .category-btn-group {
    justify-content: center;
  }

  .posts-section {
    padding: 1.5rem;
  }

  .post-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
}

@media (max-width: 480px) {
  .group-avatar,
  .default-avatar {
    width: 80px;
    height: 80px;
  }

  .group-name {
    font-size: 1.5rem;
  }

  .member-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .category-btn-group {
    flex-direction: column;
    align-items: center;
  }

  .category-btn {
    width: 140px;
  }
}

.official-badge {
  color: #2196f3;
  font-weight: bold;
  margin-right: 4px;
}
</style>
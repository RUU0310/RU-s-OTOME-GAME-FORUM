<template>
  <div class="post-detail-container" v-if="post">
    <!-- 装饰性顶部边框 -->
    <div class="decorative-header">
      <div class="decorative-line"></div>
      <span class="decorative-icon">🌸</span>
      <div class="decorative-line"></div>
    </div>

    <div class="post-header-bar">
      <h2 class="post-title">{{ post.title }}</h2>
      <div style="display: flex; align-items: center; gap: 8px;">
        <div class="post-actions-bar" v-if="user && post.user_id === user.user_id">
          <button class="edit-btn" @click="goToEdit">编辑</button>
          <button class="delete-btn" @click="showDeleteConfirm = true">删除</button>
        </div>
      </div>
    </div>

    <div class="post-meta">
      <div class="author-info">
        <img 
          v-if="post.avatar" 
          :src="getFullImageUrl(post.avatar)" 
          class="author-avatar" 
          alt="头像"
        />
        <div v-else class="default-avatar">👤</div>
        <span class="author-name">{{ post.nickname || post.username || '未知用户' }}</span>
      </div>
      <span v-if="post.category_name" class="category-tag">🏷️ {{ post.category_name }}</span>
      <span class="post-time">{{ formatTime(post.created_at) }}</span>
    </div>

    <div class="post-content" v-html="post.content"></div>

    <div v-if="post.images && post.images.length" class="post-images">
      <img v-for="img in post.images" :key="img" :src="getFullImageUrl(img)" class="post-image" />
    </div>

    <div v-if="post.is_poll && post.poll_options && post.poll_options.length" class="poll-section">
      <div class="poll-header">
        <h4 class="poll-title">投票</h4>
        <div class="poll-decoration">✨</div>
      </div>
      
      <div v-if="!pollExpired">
        <div v-if="!hasVoted">
          <div v-for="opt in post.poll_options" :key="opt.option_id" class="poll-option" :class="{selected: selectedOptions.includes(opt.option_id)}" @click="selectOption(opt.option_id)">
            <span class="option-text">{{ opt.text }}</span>
            <span class="vote-count">{{ opt.vote_count }}票</span>
          </div>
          <button class="vote-btn" @click="submitVote" :disabled="selectedOptions.length === 0">投票</button>
        </div>
        <div v-else>
          <div v-for="opt in post.poll_options" :key="opt.option_id" class="poll-option" :class="{voted: votedOptions.includes(opt.option_id)}">
            <span class="option-text">{{ opt.text }}</span>
            <span class="vote-count">{{ opt.vote_count }}票</span>
          </div>
          <div class="voted-tip">你已投票</div>
        </div>
      </div>
      <div v-else>
        <div v-for="opt in post.poll_options" :key="opt.option_id" class="poll-option">
          <span class="option-text">{{ opt.text }}</span>
          <span class="vote-count">{{ opt.vote_count }}票</span>
        </div>
        <div class="voted-tip">⏰ 投票已截止</div>
      </div>
      <div v-if="post.poll_deadline" class="poll-deadline">⏰ 截止时间：{{ formatTime(post.poll_deadline) }}</div>
      
      <!-- 饼图展示 -->
      <div v-if="showPieChart" class="poll-pie-chart">
        <Pie :data="pieData" :options="pieOptions" />
      </div>
    </div>

      <div class="post-actions-top">
        <button
          :class="['action-btn', 'favorite-btn', { active: isFavorite }]"
          @click="toggleFavorite"
        >
          {{ isFavorite ? '💖 已收藏' : '🤍 收藏' }}
        </button>
        <button
          :class="['action-btn', 'like-btn', { active: post.liked }]"
          @click="togglePostLike"
        >
          {{ post.liked ? '💖' : '🤍' }} {{ post.like_count }}
        </button>
      </div>

    <!-- 评论区 -->
    <div class="comments-section">
      <div class="section-header">
        <h3 class="section-title">💬 评论区</h3>
  
      </div>

      <CommentItem
        v-for="comment in comments"
        :key="comment.id"
        :comment="comment"
        :depth="0"
        :replyToId="replyToId"
        :replyContent="replyContent"
        :likeComment="likeComment"
        :submitReply="submitReply"
        :formatTime="formatTime"
        :isMyComment="isMyComment"
        :editMap="editMap"
        :editContentMap="editContentMap"
        :startEdit="startEdit"
        :saveEdit="saveEdit"
        :cancelEdit="cancelEdit"
        :deleteComment="deleteComment"
        @update:replyToId="val => replyToId = val"
        @update:replyContent="val => replyContent = val"
      />

      <div class="comment-input-section">
        <el-input 
          v-model="newComment" 
          placeholder="💭 写下你的评论..." 
          class="comment-input"
        />
        <button class="submit-comment-btn" @click="submitComment">发送</button>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <el-dialog v-model="showDeleteConfirm" title="💔 确认删除" width="320px" :close-on-click-modal="false">
      <div class="delete-confirm-content">
        <p>确定要删除该帖子吗？</p>
        <p class="delete-hint">删除后不可恢复</p>
      </div>
      <template #footer>
        <button class="cancel-btn" @click="showDeleteConfirm = false">取消</button>
        <button class="confirm-delete-btn" @click="deletePost">确认删除</button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { ElMessage } from 'element-plus'
import CommentItem from '@/components/CommentItem.vue'

ChartJS.register(ArcElement, Tooltip, Legend)

const API_BASE_URL = 'http://localhost:5000'
const route = useRoute()
const router = useRouter()
const post = ref(null)
const user = JSON.parse(localStorage.getItem('user') || 'null')
const hasVoted = ref(false)
const votedOptions = ref([])
const selectedOptions = ref([])
const showDeleteConfirm = ref(false)
const comments = ref([])
const newComment = ref('')
const replyToId = ref(null)
const replyContent = ref('')
const isFavorite = ref(false)
const editMap = ref({})
const editContentMap = ref({})

const getFullImageUrl = (img) => {
  if (!img) return ''
  if (img.startsWith('http')) return img
  return `${API_BASE_URL}/static/${img}`
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })
}

const pollExpired = computed(() => {
  if (!post.value || !post.value.poll_deadline) return false
  return new Date(post.value.poll_deadline) < new Date()
})

const showPieChart = computed(() => {
  if (!post.value || !post.value.is_poll || !post.value.poll_options || post.value.poll_options.length === 0) return false
  return hasVoted.value || pollExpired.value
})

const pieColors = [
  '#ffb6d5', // 粉
  '#cdb7f6', // 紫
  '#aeefff', // 浅蓝
  '#ffe6a7', // 浅黄
  '#ffd6e0', // 淡粉
  '#e0c3fc', // 淡紫
  '#b5ead7', // 薄荷绿
  '#f7cac9', // 浅粉
  '#f3c6f1', // 浅紫
  '#b5d0ff'  // 浅蓝紫
]

const pieData = computed(() => {
  if (!showPieChart.value) return { labels: [], datasets: [] }
  return {
    labels: post.value.poll_options.map(opt => opt.text),
    datasets: [
      {
        data: post.value.poll_options.map(opt => opt.vote_count),
        backgroundColor: pieColors,
        borderColor: '#fff',
        borderWidth: 1
      }
    ]
  }
})

const pieOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right',
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          const label = context.label || ''
          const value = context.parsed || 0
          const total = context.chart._metasets[context.datasetIndex].total
          const percent = total ? ((value / total) * 100).toFixed(1) : 0
          return `${label}: ${value}票 (${percent}%)`
        }
      }
    }
  }
}

const fetchPost = async () => {
  const params = user ? { user_id: user.user_id } : {}
  const res = await axios.get(`${API_BASE_URL}/posts/${route.params.id}`, { params })
  post.value = res.data
  if (user && post.value.is_poll) {
    // 查询用户是否已投票
    const voteRes = await axios.get(`${API_BASE_URL}/posts/${route.params.id}/user-votes/${user.user_id}`)
    votedOptions.value = voteRes.data.voted_option_ids || []
    hasVoted.value = votedOptions.value.length > 0
  }
}

const selectOption = (optionId) => {
  if (post.value.poll_type === 'single') {
    selectedOptions.value = [optionId]
  } else {
    if (selectedOptions.value.includes(optionId)) {
      selectedOptions.value = selectedOptions.value.filter(id => id !== optionId)
    } else {
      selectedOptions.value.push(optionId)
    }
  }
}

const submitVote = async () => {
  if (!user) return
  try {
    if (post.value.poll_type === 'single') {
      await axios.post(`${API_BASE_URL}/poll-options/${selectedOptions.value[0]}/vote`, { user_id: user.user_id })
    } else {
      for (const optionId of selectedOptions.value) {
        await axios.post(`${API_BASE_URL}/poll-options/${optionId}/vote`, { user_id: user.user_id })
      }
    }
    await fetchPost()
    selectedOptions.value = []
  } catch (e) {
    alert(e.response?.data?.message || '投票失败')
  }
}

const goToEdit = () => {
  router.push(`/post/${post.value.post_id}/edit`)
}

const deletePost = async () => {
  try {
    await axios.delete(`${API_BASE_URL}/posts/${post.value.post_id}`)
    ElMessage.success('删除成功')
    showDeleteConfirm.value = false
    router.back()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '删除失败')
  }
}

const fetchComments = async () => {
  const params = user ? { user_id: user.user_id } : {}
  const res = await axios.get(`${API_BASE_URL}/posts/${route.params.id}/comments`, { params })
  comments.value = res.data
}

const submitComment = async () => {
  if (!user) return ElMessage.warning('请先登录')
  if (!newComment.value.trim()) return ElMessage.warning('请输入评论内容')
  await axios.post(`${API_BASE_URL}/posts/${route.params.id}/comments`, {
    user_id: user.user_id,
    content: newComment.value
  })
  newComment.value = ''
  fetchComments()
}

const submitReply = async (parentId) => {
  if (!user) return ElMessage.warning('请先登录')
  if (!replyContent.value.trim()) return ElMessage.warning('请输入回复内容')
  await axios.post(`${API_BASE_URL}/posts/${route.params.id}/comments`, {
    user_id: user.user_id,
    content: replyContent.value,
    parent_id: parentId
  })
  replyContent.value = ''
  replyToId.value = null
  fetchComments()
}

const isMyComment = (c) => {
  return user && c.user_id === user.user_id
}

const startEdit = (c) => {
  editMap.value[c.id] = true
  editContentMap.value[c.id] = c.content
}

const saveEdit = async (c) => {
  if (!user) return ElMessage.warning('请先登录')
  const content = editContentMap.value[c.id]
  if (!content || !content.trim()) return ElMessage.warning('内容不能为空')
  await axios.put(`${API_BASE_URL}/posts/${route.params.id}/comments/${c.id}`, {
    user_id: user.user_id,
    content: content.trim()
  })
  editMap.value[c.id] = false
  fetchComments()
}

const cancelEdit = (c) => {
  editMap.value[c.id] = false
}

const deleteComment = async (c) => {
  if (!user) return ElMessage.warning('请先登录')
  if (!confirm('确定要删除这条评论吗？')) return
  await axios.put(`${API_BASE_URL}/posts/${route.params.id}/comments/${c.id}`, {
    user_id: user.user_id,
    content: '[该评论已被删除]'
  })
  fetchComments()
}

const likeComment = async (comment) => {
  if (!user) return ElMessage.warning('请先登录')
  if (comment.liked) {
    await axios.delete(`${API_BASE_URL}/comments/${comment.id}/like`, { params: { user_id: user.user_id } })
  } else {
    await axios.post(`${API_BASE_URL}/comments/${comment.id}/like`, { user_id: user.user_id })
  }
  fetchComments()
}

const fetchFavorite = async () => {
  if (!user) return
  const res = await axios.get(`${API_BASE_URL}/posts/${route.params.id}/favorite`, { params: { user_id: user.user_id } })
  isFavorite.value = res.data.is_favorite
}

const toggleFavorite = async () => {
  if (!user) return ElMessage.warning('请先登录')
  if (isFavorite.value) {
    await axios.delete(`${API_BASE_URL}/posts/${route.params.id}/favorite`, { params: { user_id: user.user_id } })
    isFavorite.value = false
  } else {
    await axios.post(`${API_BASE_URL}/posts/${route.params.id}/favorite`, { user_id: user.user_id })
    isFavorite.value = true
  }
}

const togglePostLike = async () => {
  if (!user) return ElMessage.warning('请先登录')
  if (post.value.liked) {
    await axios.delete(`${API_BASE_URL}/posts/${route.params.id}/like`, { params: { user_id: user.user_id } })
  } else {
    await axios.post(`${API_BASE_URL}/posts/${route.params.id}/like`, { user_id: user.user_id })
  }
  await fetchPost()
}

onMounted(() => {
  fetchPost()
  fetchComments()
  fetchFavorite()
})
</script>

<style scoped>
.post-detail-container {
  max-width: 800px;
  margin: 8px auto 40px auto;
  padding: 12px 24px 32px 24px;
  position: relative;
}

.post-detail-container::before {
  content: '✨ ♡ ✨';
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  color: rgba(236, 72, 153, 0.4);
  font-size: 12px;
  letter-spacing: 8px;
}

.decorative-header {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  gap: 15px;
}

.decorative-line {
  height: 1px;
  background: linear-gradient(90deg, transparent, #f472b6, transparent);
  flex: 1;
  max-width: 100px;
}

.decorative-icon {
  color: #ec4899;
  font-size: 16px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-3px); }
}

.post-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
  margin-top: 0;
}

.post-title {
  margin-bottom: 0;
  color: #be185d;
  font-size: 1.5rem;
  font-weight: 600;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 14px;
  color: #8b5a6b;
  margin-bottom: 20px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #d63384;
  font-weight: 500;
}

.author-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(236, 72, 153, 0.2);
}

.default-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(236, 72, 153, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  border: 2px solid rgba(236, 72, 153, 0.2);
}

.author-name {
  color: #d63384;
  font-weight: 500;
}

.category-tag {
  background: rgba(236, 72, 153, 0.1);
  color: #be185d;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 12px;
  border: 1px solid rgba(236, 72, 153, 0.2);
}

.post-time {
  color: #9d7b8a;
}

.post-content {
  margin-bottom: 20px;
  color: #6d4c57;
  line-height: 1.7;
}

.post-images {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
  max-width: 100%;
  width: 100%;
}

.post-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  border: 2px solid rgba(236, 72, 153, 0.2);
  box-shadow: 0 2px 8px rgba(236, 72, 153, 0.1);
  transition: transform 0.3s ease;
  max-width: 100%;
  max-height: 100%;
}

.post-image:hover {
  transform: scale(1.05);
}

.poll-section {
  margin-top: 20px;
  padding: 20px;
  border: 1px solid rgba(236, 72, 153, 0.2);
  border-radius: 15px;
}

.poll-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(236, 72, 153, 0.1);
}

.poll-title {
  margin-bottom: 0;
  color: #be185d;
  font-size: 1.1rem;
  font-weight: 600;
}

.poll-decoration {
  font-size: 14px;
  color: #ec4899;
  animation: sparkle 2s ease-in-out infinite;
}

@keyframes sparkle {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}

.poll-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border: 1px solid rgba(236, 72, 153, 0.2);
  border-radius: 10px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.poll-option:hover {
  background: rgba(236, 72, 153, 0.05);
  border-color: #ec4899;
  transform: translateX(5px);
}

.poll-option.selected {
  border-color: #ec4899;
  background: rgba(236, 72, 153, 0.1);
  box-shadow: 0 2px 8px rgba(236, 72, 153, 0.15);
}

.poll-option.voted {
  border-color: #be185d;
  background: rgba(190, 24, 93, 0.1);
}

.option-text {
  color: #6d4c57;
  font-size: 15px;
  font-weight: 500;
}

.vote-count {
  font-size: 13px;
  color: #9d7b8a;
  font-weight: 500;
}

.vote-btn {
  margin-top: 15px;
  padding: 10px 24px;
  background: #ec4899;
  color: #fff;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(236, 72, 153, 0.2);
}

.vote-btn:hover:not(:disabled) {
  background: #be185d;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(236, 72, 153, 0.3);
}

.vote-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  box-shadow: none;
}

.voted-tip {
  color: #be185d;
  margin-top: 15px;
  font-size: 14px;
  font-weight: 500;
  text-align: center;
  padding: 10px;
  background: rgba(236, 72, 153, 0.1);
  border-radius: 8px;
}

.poll-pie-chart {
  margin-top: 24px;
  padding: 16px;
  min-height: 320px;
  border: 1px solid rgba(236, 72, 153, 0.1);
  border-radius: 12px;
}

.poll-deadline {
  color: #9d7b8a;
  font-size: 13px;
  margin-top: 12px;
  text-align: center;
  padding: 8px;
  background: rgba(236, 72, 153, 0.05);
  border-radius: 8px;
}

.post-actions-bar {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-bottom: 10px;
}

.edit-btn, .delete-btn {
  padding: 6px 16px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.edit-btn {
  background: rgba(236, 72, 153, 0.1);
  color: #be185d;
  border: 1px solid rgba(236, 72, 153, 0.3);
}

.edit-btn:hover {
  background: #ec4899;
  color: #fff;
  transform: translateY(-1px);
}

.delete-btn {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.delete-btn:hover {
  background: #dc2626;
  color: #fff;
  transform: translateY(-1px);
}

.comments-section {
  margin-top: 30px;
  padding: 24px;
  border: 1px solid rgba(236, 72, 153, 0.2);
  border-radius: 15px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(236, 72, 153, 0.1);
}

.section-title {
  margin-bottom: 0;
  color: #be185d;
  font-size: 1.2rem;
  font-weight: 600;
}

.section-decoration {
  font-size: 14px;
  color: #ec4899;
  animation: sparkle 2s ease-in-out infinite;
}

.post-actions-top {
  display: flex;
  gap: 16px;
  margin-top: 32px;
  margin-bottom: 20px;
  justify-content: flex-start;
}

.action-btn {
  font-size: 15px;
  border-radius: 20px;
  padding: 10px 24px;
  background: rgba(255, 255, 255, 0.8);
  color: #be185d;
  border: 2px solid rgba(236, 72, 153, 0.3);
  box-shadow: 0 2px 8px rgba(236, 72, 153, 0.1);
  transition: all 0.3s ease;
  font-weight: 500;
  cursor: pointer;
}

.action-btn:hover {
  background: #ec4899;
  color: #fff;
  border-color: #ec4899;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(236, 72, 153, 0.2);
}

.action-btn.active {
  background: #ec4899;
  color: #fff;
  border-color: #ec4899;
}

.comment-input-section {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.comment-input {
  flex: 1;
}

.submit-comment-btn {
  padding: 10px 20px;
  background: #ec4899;
  color: #fff;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(236, 72, 153, 0.2);
}

.submit-comment-btn:hover {
  background: #be185d;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(236, 72, 153, 0.3);
}

.delete-confirm-content {
  text-align: center;
  padding: 10px;
}

.delete-confirm-content p {
  margin: 0 0 8px 0;
  color: #6d4c57;
}

.delete-hint {
  color: #be185d;
  font-size: 13px;
  opacity: 0.8;
}

.cancel-btn, .confirm-delete-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.cancel-btn {
  background: rgba(236, 72, 153, 0.1);
  color: #be185d;
  border: 1px solid rgba(236, 72, 153, 0.3);
}

.cancel-btn:hover {
  background: rgba(236, 72, 153, 0.2);
}

.confirm-delete-btn {
  background: #dc2626;
  color: #fff;
  border: 1px solid #dc2626;
}

.confirm-delete-btn:hover {
  background: #b91c1c;
}
</style> 
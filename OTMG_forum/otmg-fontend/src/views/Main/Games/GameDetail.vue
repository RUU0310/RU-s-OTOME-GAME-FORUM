<template>
  <div class="game-detail-bk-container" v-if="game">
    <div class="game-detail-bk-header">
      <el-image
          v-if="game.image_url"
          :src="getFullImageUrl(game.image_url)"
          fit="cover"
          class="game-detail-bk-image"
          :alt="game.name"
      />
      <div class="game-detail-bk-title">
        <h1 class="game-title">
          <span v-if="game.is_official" class="official-badge">官方</span>
          {{ game.name }}
        </h1>
        <div class="game-detail-bk-meta">
          <span>地区：{{ game.region }}</span>
          <span>发行公司：{{ game.publisher }}</span>
          <span>发行日期：{{ game.release_date }}</span>
          <span>
            <el-link v-if="game.purchase_link" :href="game.purchase_link" target="_blank" type="primary">购买链接</el-link>
            <span v-else>无购买链接</span>
          </span>
        </div>
        <div class="game-detail-bk-user">
          <el-radio-group v-model="userStatus" @change="onStatusChange">
            <el-radio-button label="wish">想玩</el-radio-button>
            <el-radio-button label="playing">在玩</el-radio-button>
            <el-radio-button label="played">玩过</el-radio-button>
          </el-radio-group>
          <el-button 
            v-if="userStatus" 
            size="small" 
            type="info" 
            @click="clearStatus" 
            class="clear-status-btn"
          >
            取消状态
          </el-button>
          <span class="game-detail-bk-user-label">我的评分：</span>
          <el-rate v-model="userRating" :max="5" allow-half @change="onRatingChange" />
          <el-button v-if="userRating > 0" size="small" type="info" @click="clearRating" class="clear-rating-btn">清除评分</el-button>
          <span v-if="userRating" class="game-detail-bk-user-score">{{ (userRating * 2).toFixed(1) }}/10</span>
        </div>
        <div class="game-detail-bk-stats">
          <span>想玩 {{ stats.wish }} 人</span>
          <span>在玩 {{ stats.playing }} 人</span>
          <span>玩过 {{ stats.played }} 人</span>
          <span class="game-detail-bk-avg-label">全局评分：</span>
          <el-rate v-model="avgRatingStar" :max="5" disabled allow-half />
          <span v-if="stats.avg_rating">{{ (stats.avg_rating * 2).toFixed(1) }}/10 ({{ stats.rating_count }}人)</span>
          <span v-else>暂无评分</span>
        </div>
      </div>
    </div>
    <div class="game-detail-bk-content">
      <div class="game-detail-bk-section section-fixed-width">
        <h2>简介</h2>
        <div class="game-detail-bk-desc">{{ game.description }}</div>
      </div>
    </div>
    <div class="game-detail-bk-section section-fixed-width">
      <h2>角色列表</h2>
      <div v-if="characters.length === 0" style="color: #aaa; margin-bottom: 12px;">暂无角色</div>
      <div v-else class="character-carousel">
        <button class="carousel-btn left" @click="prevPage" :disabled="characterPage === 1">&#8592;</button>
        <div class="character-list">
          <div v-for="c in pagedCharacters" :key="c.id" class="character-card">
            <img v-if="c.avatar" :src="getFullImageUrl(c.avatar)" class="character-img" />
            <div class="character-info">
              <div class="character-title">
                <span class="character-name">{{ c.name }}</span>
                <span class="character-type">[{{ c.role_type || '可攻略' }}]</span>
              </div>
              <div class="character-cv">CV: {{ c.cv }}</div>
              <div class="character-desc">{{ c.description }}</div>
              <div v-if="c.extra_info && Object.keys(c.extra_info).length" class="character-extra">
                <span v-for="(v, k) in c.extra_info" :key="k" class="character-extra-item">{{ k }}: {{ v }}</span>
              </div>
            </div>
          </div>
        </div>
        <button class="carousel-btn right" @click="nextPage" :disabled="characterPage === totalCharacterPages">&#8594;</button>
      </div>
      <div v-if="characters.length > pageSize" class="carousel-indicator">
        <span v-for="n in totalCharacterPages" :key="n" :class="['dot', {active: n === characterPage}]" @click="goToPage(n)"></span>
      </div>
    </div>
    <div class="game-detail-bk-section game-detail-bk-comments section-fixed-width">
      <h2>评论区</h2>
      <div class="comment-input-area">
        <el-input
            v-model="commentContent"
            type="textarea"
            :rows="2"
            maxlength="300"
            show-word-limit
            placeholder="说点什么..."
            class="comment-input"
        />
        <el-button type="primary" @click="submitComment" :disabled="!commentContent.trim()">发表评论</el-button>
      </div>
      <div v-if="comments.length === 0" class="comment-empty">暂无评论</div>
      <div v-else class="comment-list">
        <div v-for="c in (showAllComments ? comments : topComments)" :key="c.id" class="comment-item">
          <div class="avatar-container">
          <img :src="c.avatar || defaultAvatar" class="comment-avatar" />
            <!-- 发行商标识 - 头像右下角 -->
            <div v-if="c.user_role === 'publisher'" class="publisher-badge">
              <span class="publisher-icon">🎮</span>
            </div>
          </div>
          <div class="comment-main">
            <div class="comment-header">
              <span class="comment-nickname">{{ c.nickname || '用户' }}</span>
              <span class="comment-time">{{ formatChinaTime(c.created_at) }}</span>
              <el-button
                  class="comment-like-btn"
                  size="small"
                  type="text"
                  @click="likeComment(c)"
                  :icon="Promotion"
                  :class="{ liked: c.liked }"
              >
                <span class="comment-like-count">{{ c.like_count || 0 }}</span>
              </el-button>
              <span v-if="c.user_rating" class="comment-user-rating">
                <el-rate :model-value="c.user_rating" :max="5" disabled allow-half style="font-size: 1em; vertical-align: middle;" />
                <span class="comment-user-rating-score">{{ (c.user_rating * 2).toFixed(1) }}/10</span>
              </span>
              <template v-if="isMyComment(c)">
                <el-button v-if="!editMap[c.id]" size="small" type="text" @click="editMap[c.id]=true">编辑</el-button>
                <el-button size="small" type="text" @click="deleteComment(c)">删除</el-button>
              </template>
            </div>
            <div class="comment-content" v-if="!editMap[c.id]">{{ c.content }}</div>
            <div v-else class="comment-edit-area">
              <el-input v-model="editContentMap[c.id]" type="textarea" :rows="2" maxlength="300" show-word-limit />
              <el-button size="small" type="primary" @click="saveEditComment(c)">保存</el-button>
              <el-button size="small" @click="cancelEditComment(c)">取消</el-button>
            </div>
          </div>
        </div>
        <div v-if="comments.length > 5 && !showAllComments" style="text-align:center;margin:10px 0;">
          <el-button type="primary" size="small" @click="showAllComments = true">全部评论</el-button>
        </div>
        <div v-if="showAllComments && comments.length > 5" style="text-align:center;margin:10px 0;">
          <el-button size="small" @click="showAllComments = false">只看热门</el-button>
        </div>
      </div>
    </div>
    <div v-if="loading" class="loading"><el-spinner /> 加载中...</div>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Promotion } from '@element-plus/icons-vue'

const route = useRoute()
const game = ref(null)
const loading = ref(false)
const error = ref('')
const API_BASE_URL = 'http://localhost:5000'

const userStatus = ref('')
const userRating = ref(0)
const stats = ref({ wish: 0, playing: 0, played: 0, avg_rating: null, rating_count: 0 })
const avgRatingStar = ref(0)
const comments = ref([])
const commentContent = ref('')
const defaultAvatar = '/src/assets/logo.png'
const editMap = ref({})
const editContentMap = ref({})
const characters = ref([])
const pageSize = 1
const characterPage = ref(1)
const totalCharacterPages = computed(() => Math.ceil(characters.value.length / pageSize))
const pagedCharacters = computed(() => {
  const start = (characterPage.value - 1) * pageSize
  return characters.value.slice(start, start + pageSize)
})
const showAllComments = ref(false)

const topComments = computed(() => {
  // 按点赞数降序排列，取前5条
  return [...comments.value].sort((a, b) => (b.like_count || 0) - (a.like_count || 0)).slice(0, 5)
})

function getFullImageUrl(url) {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return API_BASE_URL + url
}

const getGameDetail = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await axios.get(`${API_BASE_URL}/games/${route.params.id}`)
    if (res.data.status === 'success') {
      game.value = res.data.result || res.data
    } else {
      error.value = res.data.message || '未找到游戏信息'
    }
  } catch (e) {
    error.value = '请求失败'
  } finally {
    loading.value = false
  }
}

const getUserGameStatus = async () => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (!user) return
  const res = await axios.get(`${API_BASE_URL}/games/${route.params.id}/user_status`, { params: { user_id: user.user_id } })
  if (res.data.status === 'success' && res.data.result) {
    userStatus.value = res.data.result.status || ''
    userRating.value = res.data.result.rating || 0
  } else {
    userStatus.value = ''
    userRating.value = 0
  }
}

const getGameStats = async () => {
  const res = await axios.get(`${API_BASE_URL}/games/${route.params.id}/stats`)
  if (res.data.status === 'success' && res.data.result) {
    stats.value = res.data.result
    avgRatingStar.value = stats.value.avg_rating ? stats.value.avg_rating : 0
  }
}

const getComments = async () => {
  const res = await axios.get(`${API_BASE_URL}/games/${route.params.id}/comments`)
  if (res.data.status === 'success') {
    comments.value = res.data.results
    for (const c of comments.value) {
      editContentMap.value[c.id] = c.content
    }
  }
}

const onStatusChange = async () => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (!user) return
  
  // 如果状态为空，则取消状态
  const status = userStatus.value || null
  
  await axios.post(`${API_BASE_URL}/games/${route.params.id}/user_status`, {
    user_id: user.user_id,
    status: status
  })
  getGameStats()
}

const onRatingChange = async () => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (!user) return
  await axios.post(`${API_BASE_URL}/games/${route.params.id}/user_status`, {
    user_id: user.user_id,
    rating: userRating.value
  })
  getGameStats()
  getComments()
}

const submitComment = async () => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (!user) {
    ElMessage.error('请先登录')
    return
  }
  if (!commentContent.value.trim()) return
  await axios.post(`${API_BASE_URL}/games/${route.params.id}/comments`, {
    user_id: user.user_id,
    content: commentContent.value.trim()
  })
  commentContent.value = ''
  getComments()
}

const likeComment = async (c) => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (!user) {
    ElMessage.error('请先登录')
    return
  }
  await axios.post(`${API_BASE_URL}/games/${route.params.id}/comments/${c.id}/like`, {
    user_id: user.user_id
  })
  getComments()
}

const clearStatus = () => {
  userStatus.value = ''
  onStatusChange()
}

const clearRating = () => {
  userRating.value = 0
  onRatingChange()
}

function isMyComment(c) {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  return user && user.user_id === c.user_id
}

const saveEditComment = async (c) => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (!user) return
  const content = editContentMap.value[c.id]
  if (!content || !content.trim()) {
    ElMessage.error('内容不能为空')
    return
  }
  await axios.put(`${API_BASE_URL}/games/${route.params.id}/comments/${c.id}`, {
    user_id: user.user_id,
    content: content.trim()
  })
  editMap.value[c.id] = false
  getComments()
}

const cancelEditComment = (c) => {
  editMap.value[c.id] = false
}

const deleteComment = async (c) => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (!user) return
  if (!window.confirm('确定要删除这条评论吗？')) return
  await axios.delete(`${API_BASE_URL}/games/${route.params.id}/comments/${c.id}`, {
    params: { user_id: user.user_id }
  })
  getComments()
}

const getCharacters = async () => {
  const res = await axios.get(`${API_BASE_URL}/games/${route.params.id}/characters`)
  if (res.data.status === 'success') {
    characters.value = res.data.results
  }
}

function prevPage() {
  if (characterPage.value > 1) characterPage.value--
}

function nextPage() {
  if (characterPage.value < totalCharacterPages.value) characterPage.value++
}

function goToPage(n) {
  characterPage.value = n
}

function formatChinaTime(time) {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })
}

onMounted(() => {
  getGameDetail()
  getUserGameStatus()
  getGameStats()
  getComments()
  getCharacters()
})

watch(() => route.params.id, () => {
  getGameDetail()
  getUserGameStatus()
  getGameStats()
  getComments()
  getCharacters()
})

watch(characters, () => { characterPage.value = 1 })
</script>

<style scoped>
/* 让背景色占满整个屏幕 */
body, html {
  min-height: 100vh;
  margin: 0;
  padding: 0;
  background: linear-gradient(135deg, #fdf2f8 0%, #fce7f3 50%, #fdf4ff 100%) !important;
}

.game-detail-bk-container {
  padding: 40px 16px 32px 16px;
  min-height: 100vh;
  background: transparent;
  max-width: 900px;
  margin: 0 auto;
  position: relative;
}

/* 添加飘动的小装饰元素 */
.game-detail-bk-container::after {
  content: '✨ ♡ ✨ ♡ ✨ ♡ ✨ ♡ ✨';
  position: fixed;
  top: 5%;
  left: 0;
  right: 0;
  text-align: center;
  color: rgba(236, 72, 153, 0.4);
  font-size: 14px;
  letter-spacing: 20px;
  animation: float 6s ease-in-out infinite;
  pointer-events: none;
  z-index: 1;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); opacity: 0.6; }
  50% { transform: translateY(-10px); opacity: 0.8; }
}

.game-detail-bk-header {
  display: flex;
  align-items: flex-start;
  gap: 32px;
  margin-bottom: 32px;
  position: relative;
}

.game-detail-bk-image {
  width: 220px;
  height: 300px;
  object-fit: cover;
  border-radius: 20px;
  background: linear-gradient(135deg, #fdf2f8, #fce7f3);
  box-shadow:
      0 8px 32px rgba(236, 72, 153, 0.2),
      0 0 0 1px rgba(236, 72, 153, 0.15);
  border: 3px solid rgba(255, 255, 255, 0.8);
  position: relative;
  overflow: hidden;
}

.game-detail-bk-image::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%);
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
  100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.game-detail-bk-title {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.game-detail-bk-title h1 {
  font-size: 2.2rem;
  font-weight: bold;
  margin: 0 0 18px 0;
  background: linear-gradient(135deg, #be185d, #ec4899, #f472b6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.game-detail-bk-title h1::after {
  content: '♡';
  position: absolute;
  right: -30px;
  top: -5px;
  color: rgba(236, 72, 153, 0.4);
  font-size: 0.6em;
  animation: heartbeat 2s ease-in-out infinite;
}

@keyframes heartbeat {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

.game-detail-bk-meta {
  color: #8b5a6b;
  font-size: 1.08rem;
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin-bottom: 8px;
}

.game-detail-bk-user {
  margin: 18px 0 8px 0;
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 20px;
  border: 2px solid rgba(255, 192, 203, 0.3);
  backdrop-filter: blur(10px);
}

.game-detail-bk-user-label {
  margin-left: 12px;
  color: #b06b7a;
  font-weight: 500;
}

.game-detail-bk-user-score {
  margin-left: 8px;
  color: #ff6b9d;
  font-weight: bold;
  text-shadow: 0 1px 2px rgba(255, 107, 157, 0.3);
}

.game-detail-bk-stats {
  margin: 8px 0 0 0;
  color: #9d7b8a;
  font-size: 1.02rem;
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
  padding: 12px 16px;
  background: rgba(255, 240, 245, 0.6);
  border-radius: 15px;
  border: 1px solid rgba(255, 192, 203, 0.2);
}

.game-detail-bk-avg-label {
  margin-left: 18px;
  color: #8b5a6b;
  font-weight: 500;
}

.game-detail-bk-content {
  display: flex;
  gap: 40px;
  flex-wrap: wrap;
}

.game-detail-bk-section {
  flex: 1 1 320px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 25px;
  padding: 30px 32px 24px 32px;
  margin-bottom: 24px;
  box-shadow:
      0 8px 32px rgba(255, 182, 193, 0.2),
      0 0 0 1px rgba(255, 255, 255, 0.3);
  border: 2px solid rgba(255, 240, 245, 0.8);
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}

.game-detail-bk-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #f472b6, #f9a8d4, #fce7f3);
}

.game-detail-bk-section h2 {
  font-size: 1.3rem;
  font-weight: bold;
  margin-bottom: 20px;
  color: #d63384;
  position: relative;
  padding-left: 25px
}

.game-detail-bk-section h2::before {
  content: '✿';
  position: absolute;
  left: 0;
  color: #ec4899;
  font-size: 1.1em;
}

.game-detail-bk-desc {
  font-size: 1.05rem;
  color: #6d4c57;
  line-height: 1.8;
  white-space: pre-line;
  padding: 15px;
  background: rgba(255, 248, 250, 0.8);
  border-radius: 15px;
}

.game-detail-bk-comments {
  min-width: 320px;
  max-width: 600px;
}

.comment-input-area {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 18px;
  padding: 20px;
  background: rgba(255, 248, 250, 0.6);
  border-radius: 20px;
  border: 2px dashed rgba(255, 192, 203, 0.4);
}

.comment-input {
  flex: 1;
}

.comment-list {
  margin-top: 8px;
}

.comment-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 18px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  border: 1px solid rgba(255, 228, 225, 0.6);
  transition: all 0.3s ease;
}

.comment-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 182, 193, 0.25);
}

.avatar-container {
  position: relative;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  background: linear-gradient(135deg, #fdf2f8, #fce7f3);
  border: 3px solid rgba(236, 72, 153, 0.2);
  box-shadow: 0 4px 15px rgba(236, 72, 153, 0.15);
}

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

.comment-main {
  flex: 1;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}

.comment-nickname {
  font-weight: bold;
  color: #d63384;
}

.comment-time {
  color: #b06b7a;
  font-size: 0.95rem;
}

.comment-content {
  font-size: 1.05rem;
  color: #6d4c57;
  line-height: 1.7;
  word-break: break-all;
  padding: 8px 12px;
  background: rgba(255, 248, 250, 0.5);
  border-radius: 12px;
}

.comment-empty {
  color: #b06b7a;
  text-align: center;
  margin: 18px 0;
  padding: 30px;
  background: rgba(255, 248, 250, 0.5);
  border-radius: 20px;
  border: 2px dashed rgba(255, 192, 203, 0.3);
}

.loading, .error {
  text-align: center;
  color: #b06b7a;
  margin-top: 40px;
  font-size: 1.1rem;
}

.error {
  color: #dc3545;
  background: rgba(220, 53, 69, 0.1);
  padding: 15px;
  border-radius: 15px;
}

.comment-like-btn {
  margin-left: 10px;
  color: #b06b7a;
  display: flex;
  align-items: center;
  font-size: 1.1rem;
  padding: 4px 8px;
  transition: all 0.3s ease;
  border-radius: 12px;
}

.comment-like-btn:hover {
  background: rgba(255, 182, 193, 0.2);
}

.comment-like-btn.liked {
  color: #ff6b9d;
  background: rgba(255, 107, 157, 0.15);
}

.comment-like-count {
  margin-left: 2px;
  font-size: 1rem;
}

.comment-user-rating {
  margin-left: 12px;
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 4px 8px;
  background: rgba(255, 107, 157, 0.1);
  border-radius: 12px;
}

.comment-user-rating-score {
  color: #ff6b9d;
  font-size: 0.98em;
  margin-left: 2px;
  font-weight: 600;
}

.clear-status-btn {
  margin-left: 8px;
  padding: 4px 12px;
  font-size: 0.95em;
  border-radius: 12px;
  background: rgba(255, 182, 193, 0.2);
  border-color: rgba(255, 182, 193, 0.4);
}

.clear-rating-btn {
  margin-left: 8px;
  padding: 4px 12px;
  font-size: 0.95em;
  border-radius: 12px;
  background: rgba(255, 182, 193, 0.2);
  border-color: rgba(255, 182, 193, 0.4);
}

.section-fixed-width {
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.comment-edit-area {
  margin-top: 6px;
  display: flex;
  gap: 8px;
  align-items: flex-start;
  padding: 15px;
  background: rgba(255, 248, 250, 0.8);
  border-radius: 15px;
}

.character-carousel {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}

.carousel-btn {
  background: linear-gradient(135deg, #ffb6c1, #ffc0cb);
  border: 2px solid rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  width: 42px;
  height: 42px;
  font-size: 1.4em;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(255, 182, 193, 0.3);
}

.carousel-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(255, 182, 193, 0.4);
}

.carousel-btn:disabled {
  background: linear-gradient(135deg, #f0f0f0, #e0e0e0);
  color: #ccc;
  border-color: #f0f0f0;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.character-list {
  display: flex;
  flex-wrap: nowrap;
  gap: 24px;
  margin-bottom: 0;
}

.character-card {
  display: flex;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(255, 182, 193, 0.15);
  padding: 24px;
  min-width: 520px;
  max-width: 700px;
  align-items: flex-start;
  gap: 20px;
  border: 1px solid rgba(255, 192, 203, 0.2);
  transition: all 0.3s ease;
}

.character-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 182, 193, 0.25);
}

.character-img {
  width: 160px;
  height: 160px;
  object-fit: contain;
  background: #fef7ff;
  border-radius: 12px;
  display: block;
  border: 2px solid rgba(255, 192, 203, 0.3);
  box-shadow: 0 2px 8px rgba(255, 182, 193, 0.15);
  transition: all 0.3s ease;
}

.character-img:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(255, 182, 193, 0.25);
}

.carousel-indicator {
  text-align: center;
  margin-top: 15px;
}

.dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255, 182, 193, 0.3);
  margin: 0 5px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid rgba(255, 255, 255, 0.8);
}

.dot:hover {
  background: rgba(255, 182, 193, 0.6);
  transform: scale(1.2);
}

.dot.active {
  background: linear-gradient(135deg, #ff6b9d, #ffb6c1);
  transform: scale(1.3);
  box-shadow: 0 3px 10px rgba(255, 107, 157, 0.4);
}

.character-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.character-title {
  font-weight: bold;
  font-size: 1.15em;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.character-name {
  color: #d63384;
  font-weight: bold;
}

.character-type {
  color: #ff6b9d;
  font-size: 0.9em;
  background: rgba(255, 107, 157, 0.1);
  padding: 2px 8px;
  border-radius: 8px;
  border: 1px solid rgba(255, 107, 157, 0.2);
}

.character-cv {
  color: #b06b7a;
  font-size: 0.98em;
  font-weight: 500;
}

.character-desc {
  color: #6d4c57;
  font-size: 0.98em;
  margin-top: 5px;
  line-height: 1.6;
  padding: 8px 12px;
  background: rgba(255, 248, 250, 0.5);
  border-radius: 8px;
}

.character-extra {
  margin-top: 8px;
  color: #9d7b8a;
  font-size: 0.95em;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.character-extra-item {
  background: rgba(255, 240, 245, 0.6);
  border-radius: 8px;
  padding: 4px 10px;
  border: 1px solid rgba(255, 192, 203, 0.2);
  font-size: 0.9em;
  transition: all 0.3s ease;
}

.character-extra-item:hover {
  background: rgba(255, 182, 193, 0.15);
  transform: translateY(-1px);
}

/* 自定义Element Plus组件样式 */
:deep(.el-radio-button__inner) {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(255, 192, 203, 0.4);
  color: #d63384;
  border-radius: 0 !important;
  transition: all 0.3s ease;
}

:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: #ec4899;
  border-color: #ec4899;
  color: white;
  box-shadow: 0 2px 6px rgba(236, 72, 153, 0.25);
}

:deep(.el-rate__icon) {
  color: #f472b6;
}

:deep(.el-rate__icon.hover) {
  color: #ec4899;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #ec4899, #f472b6);
  border-color: #ec4899;
  border-radius: 15px;
  transition: all 0.3s ease;
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #be185d, #ec4899);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(236, 72, 153, 0.3);
}

:deep(.el-button--info) {
  background: rgba(236, 72, 153, 0.15);
  border-color: rgba(236, 72, 153, 0.3);
  color: #be185d;
  border-radius: 12px;
}

:deep(.el-textarea__inner) {
  border-radius: 15px;
  border-color: rgba(236, 72, 153, 0.3);
  background: rgba(255, 255, 255, 0.9);
}

:deep(.el-textarea__inner:focus) {
  border-color: #ec4899;
  box-shadow: 0 0 0 2px rgba(236, 72, 153, 0.15);
}

:deep(.el-link--primary) {
  color: #ec4899;
}

:deep(.el-link--primary:hover) {
  color: #be185d;
}

.official-badge {
  background: linear-gradient(45deg, #be185d, #ec4899);
  color: white;
  font-size: 1rem;
  padding: 4px 8px;
  border-radius: 10px;
  font-weight: bold;
  box-shadow: 0 3px 6px rgba(190, 24, 93, 0.25);
  animation: officialGlow 2s ease-in-out infinite alternate;
  white-space: nowrap;
  -webkit-background-clip: initial;
  -webkit-text-fill-color: initial;
  background-clip: initial;
}

@keyframes officialGlow {
  0% {
    box-shadow: 0 3px 6px rgba(190, 24, 93, 0.25);
  }
  100% {
    box-shadow: 0 3px 10px rgba(190, 24, 93, 0.4), 0 0 15px rgba(190, 24, 93, 0.15);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .game-detail-bk-container {
    padding: 24px 12px;
  }

  .game-detail-bk-header {
    flex-direction: column;
    gap: 20px;
  }

  .game-detail-bk-image {
    width: 180px;
    height: 240px;
  }

  .game-detail-bk-title h1 {
    font-size: 1.8rem;
    gap: 8px;
  }

  .official-badge {
    font-size: 0.8rem;
    padding: 3px 6px;
  }

  .game-detail-bk-meta {
    font-size: 0.95rem;
    gap: 16px;
  }

  .game-detail-bk-user {
    gap: 12px;
    padding: 12px 16px;
  }

  .game-detail-bk-stats {
    gap: 12px;
    padding: 10px 12px;
  }

  .game-detail-bk-section {
    padding: 20px 24px;
  }

  .character-card {
    min-width: 300px;
    padding: 20px 24px;
    gap: 16px;
  }

  .character-img {
    width: 120px;
    height: 120px;
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
}
</style>

<style>
body, html {
  min-height: 100vh;
  margin: 0;
  padding: 0;
  background: linear-gradient(135deg, #fdf2f8 0%, #fce7f3 50%, #fdf4ff 100%) !important;
}
</style>
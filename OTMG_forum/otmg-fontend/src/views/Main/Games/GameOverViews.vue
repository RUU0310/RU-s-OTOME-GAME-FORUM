<template>
  <div class="game-overview-container">
    <el-row :gutter="24">
      <!-- 左侧：游戏一览 -->
      <el-col :xs="24" :sm="24" :md="18" :lg="18">
        <el-row :gutter="12">
          <el-col v-for="game in filteredGames" :key="game.game_id" :xs="24" :sm="12" :md="6" :lg="6">
            <el-card shadow="hover" class="game-card" @click="goToDetail(game.game_id)" style="cursor:pointer;">
              <div class="card-decoration">
                <span class="corner-heart top-left">💕</span>
                <span class="corner-heart top-right">🌸</span>
              </div>
              <el-image
                  v-if="game.image_url"
                  :src="getFullImageUrl(game.image_url)"
                  fit="cover"
                  class="game-image"
                  :alt="game.name"
              />
              <div class="game-info">
                <h3 class="game-title">
                  <span v-if="game.is_official" class="official-badge">官方</span>
                  {{ game.name }}
                </h3>
                <div class="game-meta">
                  <span>地区：{{ game.region }}</span>
                  <span>发行：{{ game.publisher }}</span>
                </div>
                <div class="game-meta">
                  <span>发行日期：{{ game.release_date }}</span>
                </div>
                <div class="game-meta game-rating-meta">
                  <el-rate v-if="gameStats[game.game_id]" :model-value="gameStats[game.game_id].avg_rating || 0" :max="5" disabled allow-half />
                  <span v-if="gameStats[game.game_id] && gameStats[game.game_id].avg_rating">{{ (gameStats[game.game_id].avg_rating * 2).toFixed(1) }}/10</span>
                  <span v-else>暂无评分</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <div v-if="loading" class="loading">
          <el-spinner class="cute-spinner" />
          <span class="loading-text">加载中...</span>
        </div>
        <div v-if="!loading && filteredGames.length === 0" class="empty">
          <div class="empty-icon">🎮💭</div>
          <div>{{ searchText ? '没有找到相关游戏' : '暂无游戏信息' }}</div>
        </div>
        <!-- 添加游戏对话框 -->
        <el-dialog v-model="showAddGameDialog" title="添加新游戏" width="500px" @close="resetAddGameForm">
          <el-form :model="addGameForm" :rules="addGameRules" ref="addGameFormRef" label-width="90px" status-icon>
            <el-form-item label="游戏名称" prop="name">
              <el-input v-model="addGameForm.name" autocomplete="off" />
            </el-form-item>
            <el-form-item label="封面图" prop="image_url">
              <div class="image-upload-container">
                <el-upload
                  class="image-uploader"
                  :action="`${API_BASE_URL}/upload`"
                  :show-file-list="false"
                  :on-success="handleImageSuccess"
                  :on-error="handleImageError"
                  :before-upload="beforeImageUpload"
                  accept="image/*"
                >
                  <div v-if="addGameForm.image_url" class="image-preview">
                    <el-image :src="getFullImageUrl(addGameForm.image_url)" fit="cover" />
                    <div class="image-overlay">
                      <span>点击更换图片</span>
                    </div>
                  </div>
                  <div v-else class="upload-placeholder">
                    <div class="upload-icon">📷</div>
                    <div class="upload-text">点击上传封面图</div>
                    <div class="upload-hint">支持 JPG、PNG、GIF、WebP 格式</div>
                  </div>
                </el-upload>
                <div v-if="addGameForm.image_url" class="image-actions">
                  <el-button size="small" type="danger" @click="removeImage">删除图片</el-button>
                </div>
              </div>
            </el-form-item>
            <el-form-item label="简介" prop="description">
              <el-input type="textarea" v-model="addGameForm.description" :rows="3" />
            </el-form-item>
            <el-form-item label="地区" prop="region">
              <el-select v-model="addGameForm.region" placeholder="请选择地区">
                <el-option label="日本" value="日本" />
                <el-option label="欧美" value="欧美" />
                <el-option label="国产" value="国产" />
                <el-option label="韩国" value="韩国" />
              </el-select>
            </el-form-item>
            <el-form-item label="发行公司" prop="publisher">
              <el-input v-model="addGameForm.publisher" />
            </el-form-item>
            <el-form-item label="发行日期" prop="release_date">
              <el-date-picker v-model="addGameForm.release_date" type="date" placeholder="选择发行日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
            </el-form-item>
            <el-form-item label="购买链接" prop="purchase_link">
              <el-input v-model="addGameForm.purchase_link" />
            </el-form-item>
            <el-form-item label="官方游戏" prop="is_official">
              <el-switch v-model="addGameForm.is_official" />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="showAddGameDialog = false">取消</el-button>
            <el-button type="primary" :loading="addGameLoading" @click="onAddGameSubmit">提交</el-button>
          </template>
        </el-dialog>
      </el-col>
      <!-- 右侧：排行榜 -->
      <el-col :xs="24" :sm="24" :md="6" :lg="6">
        <div class="rank-section">
          <!-- 搜索和添加游戏按钮 -->
          <div class="search-filter-section" style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 18px;">
            <!-- 第一行：搜索框和添加按钮 -->
            <div style="display: flex; align-items: center; gap: 10px;">
              <div class="search-box">
                <input
                  v-model="searchTextInput"
                  placeholder="🔍 搜索游戏..."
                  class="search-input"
                  @input="onSearchInput"
                />
              </div>
              <el-button @click="showAddGameDialog = true" class="add-game-btn">
                <span style="margin-right: 6px;">➕</span>添加游戏
              </el-button>
            </div>
            <!-- 第二行：筛选和排序 -->
            <div style="display: flex; align-items: center; gap: 10px;">
              <el-select v-model="sortType" size="small" style="width: 90px;" @change="onSortChange">
                <el-option label="默认排序" value="default" />
                <el-option label="最新" value="time" />
              </el-select>
              <el-select v-model="regionFilter" size="small" style="width: 90px;" clearable placeholder="地区">
                <el-option label="全部地区" value="" />
                <el-option label="日本" value="日本" />
                <el-option label="欧美" value="欧美" />
                <el-option label="国产" value="国产" />
                <el-option label="韩国" value="韩国" />
              </el-select>
              <el-select v-model="publisherFilter" size="small" style="width: 90px;" clearable placeholder="发行商">
                <el-option label="全部发行" value="" />
                <el-option v-for="pub in publisherOptions" :key="pub" :label="pub" :value="pub" />
              </el-select>
            </div>
          </div>
          <el-tabs v-model="rankTab" stretch>
            <el-tab-pane label="评分榜" name="score">
              <div v-for="(game, idx) in scoreRankList" :key="game.game_id" class="rank-item">
                <span class="rank-index">{{ idx + 1 }}</span>
                <el-image :src="getFullImageUrl(game.image_url)" class="rank-img" fit="cover" />
                <div class="rank-info">
                  <div class="rank-title">{{ game.name }}</div>
                  <div class="rank-meta">均分：{{ (gameStats[game.game_id]?.avg_rating * 2).toFixed(1) || '--' }}/10</div>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="热度榜" name="hot">
              <div v-for="(game, idx) in hotRankList" :key="game.game_id" class="rank-item">
                <span class="rank-index">{{ idx + 1 }}</span>
                <el-image :src="getFullImageUrl(game.image_url)" class="rank-img" fit="cover" />
                <div class="rank-info">
                  <div class="rank-title">{{ game.name }}</div>
                  <div class="rank-meta">在玩人数：{{ gameStats[game.game_id]?.playing || 0 }}</div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { ElRate } from 'element-plus'
import { ElMessage } from 'element-plus'
import { ElDatePicker } from 'element-plus'

const router = useRouter()

const games = ref([])
const loading = ref(false)
const API_BASE_URL = 'http://localhost:5000'
const gameStats = ref({})

// 搜索参数 - 从MainHeader接收
const searchText = ref('')

// 定义props来接收MainHeader的参数
const props = defineProps({
  searchText: {
    type: String,
    default: ''
  }
})

// 监听props变化
watch(() => props.searchText, (newVal) => {
  searchText.value = newVal
})

function getFullImageUrl(url) {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return API_BASE_URL + url
}

const getGames = async () => {
  loading.value = true
  try {
    const res = await axios.get(`${API_BASE_URL}/games?status=approved`)
    if (res.data.status === 'success') {
      games.value = res.data.results
    } else {
      games.value = []
    }
  } catch (e) {
    games.value = []
  } finally {
    loading.value = false
  }
}

const getAllGameStats = async () => {
  const statsMap = {}
  await Promise.all(games.value.map(async (g) => {
    try {
      const res = await axios.get(`${API_BASE_URL}/games/${g.game_id}/stats`)
      if (res.data.status === 'success' && res.data.result) {
        statsMap[g.game_id] = res.data.result
      }
    } catch {}
  }))
  gameStats.value = statsMap
}

function goToDetail(id) {
  router.push(`/games/${id}`)
}

const sortType = ref('default')
const regionFilter = ref('')
const publisherFilter = ref('')
const publisherOptions = computed(() => {
  // 从所有游戏中提取唯一发行商
  const set = new Set()
  games.value.forEach(g => { if (g.publisher) set.add(g.publisher) })
  return Array.from(set)
})

function onSortChange() {
  // 触发排序时重新计算 filteredGames
  searchText.value = searchTextInput.value // 保证搜索和排序联动
}

// 过滤游戏列表
const filteredGames = computed(() => {
  let result = games.value

  // 搜索过滤
  if (searchText.value) {
    result = result.filter(game => 
      game.name && game.name.toLowerCase().includes(searchText.value.toLowerCase())
    )
  }
  // 地区筛选
  if (regionFilter.value) {
    result = result.filter(game => game.region === regionFilter.value)
  }
  // 发行商筛选
  if (publisherFilter.value) {
    result = result.filter(game => game.publisher === publisherFilter.value)
  }

  // 排序
  if (sortType.value === 'time') {
    result = [...result].sort((a, b) => {
      if (!a.release_date) return 1
      if (!b.release_date) return -1
      return new Date(b.release_date) - new Date(a.release_date)
    })
  }

  return result
})

const showAddGameDialog = ref(false)
const addGameForm = ref({
  name: '',
  image_url: '',
  description: '',
  region: '',
  publisher: '',
  release_date: '',
  purchase_link: '',
  is_official: false
})
const addGameLoading = ref(false)
const addGameRules = {
  name: [{ required: true, message: '请输入游戏名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入简介', trigger: 'blur' }],
  region: [{ required: true, message: '请选择地区', trigger: 'change' }],
  publisher: [{ required: true, message: '请输入发行公司', trigger: 'blur' }],
  release_date: [{ required: true, message: '请选择发行日期', trigger: 'change' }]
}
const addGameFormRef = ref()

// 搜索输入框与props解耦
const searchTextInput = ref('')
watch(() => props.searchText, (newVal) => {
  searchTextInput.value = newVal
})
function onSearchInput() {
  searchText.value = searchTextInput.value
}

async function onAddGameSubmit() {
  await addGameFormRef.value.validate()
  addGameLoading.value = true
  try {
    const res = await axios.post(`${API_BASE_URL}/games`, addGameForm.value)
    if (res.data.status === 'success') {
      showAddGameDialog.value = false
      addGameForm.value = { name: '', image_url: '', description: '', region: '', publisher: '', release_date: '', purchase_link: '', is_official: false }
      await getGames()
      ElMessage.success('游戏已提交，等待管理员审核')
      
      // 触发审核红点提示
      window.dispatchEvent(new CustomEvent('set-pending-audit', { detail: true }))
    } else {
      ElMessage.error(res.data.message || '添加失败')
    }
  } catch (e) {
    ElMessage.error('添加失败')
  } finally {
    addGameLoading.value = false
  }
}

function resetAddGameForm() {
  addGameForm.value = { name: '', image_url: '', description: '', region: '', publisher: '', release_date: '', purchase_link: '', is_official: false }
}

// 图片上传相关方法
function beforeImageUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

function handleImageSuccess(response) {
  if (response.status === 'success') {
    addGameForm.value.image_url = response.file_url
    ElMessage.success('图片上传成功!')
  } else {
    ElMessage.error(response.message || '图片上传失败!')
  }
}

function handleImageError() {
  ElMessage.error('图片上传失败!')
}

function removeImage() {
  addGameForm.value.image_url = ''
}

const rankTab = ref('score')

const scoreRankList = computed(() => {
  // 按评分降序，取前10
  return games.value
    .filter(g => gameStats.value[g.game_id] && gameStats.value[g.game_id].avg_rating)
    .sort((a, b) => (gameStats.value[b.game_id].avg_rating || 0) - (gameStats.value[a.game_id].avg_rating || 0))
    .slice(0, 7)
})
const hotRankList = computed(() => {
  // 按在玩人数降序，取前10
  return games.value
    .filter(g => gameStats.value[g.game_id])
    .sort((a, b) => (gameStats.value[b.game_id].playing || 0) - (gameStats.value[a.game_id].playing || 0))
    .slice(0, 10)
})

onMounted(async () => {
  await getGames()
  await getAllGameStats()
})

watch(games, () => {
  getAllGameStats()
})
</script>

<style scoped>
.game-overview-container {
  padding: 16px 16px;
  min-height: 100vh;
  background: linear-gradient(135deg, #fef7f0 0%, #fdf2f8 50%, #f0f9ff 100%);
  position: relative;
  display: flex;
  flex-direction: column;
}

/* 让el-row高度自适应，左右两栏顶部对齐 */
.game-overview-container > .el-row {
  align-items: flex-start;
}

/* 添加背景装饰点 */
.game-overview-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
      radial-gradient(circle at 20% 20%, rgba(252, 165, 165, 0.1) 2px, transparent 2px),
      radial-gradient(circle at 80% 80%, rgba(251, 207, 232, 0.1) 2px, transparent 2px),
      radial-gradient(circle at 60% 40%, rgba(196, 181, 253, 0.1) 1px, transparent 1px);
  background-size: 60px 60px, 80px 80px, 40px 40px;
  pointer-events: none;
}

.game-card {
  margin-bottom: 16px;
  border-radius: 14px;
  overflow: hidden;
  transition: all 0.2s;
  height: 380px;
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid #f3e8ee;
  box-shadow: 0 2px 8px rgba(251, 207, 232, 0.10);
  padding: 0;
}

.game-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(251, 207, 232, 0.3);
  border-color: #f9a8d4;
}

.card-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
}

.corner-heart {
  position: absolute;
  font-size: 14px;
  opacity: 0.7;
  animation: gentle-float 3s ease-in-out infinite;
}

.top-left {
  top: 12px;
  left: 12px;
  animation-delay: 0s;
}

.top-right {
  top: 12px;
  right: 12px;
  animation-delay: 1.5s;
}

@keyframes gentle-float {
  0%, 100% {
    transform: translateY(0px);
    opacity: 0.7;
  }
  50% {
    transform: translateY(-3px);
    opacity: 1;
  }
}

.game-image {
  width: 100%;
  height: 250px;
  object-fit: cover;
  border-radius: 12px 12px 0 0;
  margin-bottom: 0;
  border-bottom: 1px solid #f3e8ee;
}

.game-info {
  padding: 10px 10px 14px 10px;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.game-title {
  font-size: 1rem;
  font-weight: bold;
  margin: 0 0 4px 0;
  color: #be185d;
  text-shadow: none;
  display: flex;
  align-items: center;
  gap: 4px;
}

.official-badge {
  background: linear-gradient(45deg, #ec4899, #f472b6);
  color: white;
  font-size: 0.8rem;
  padding: 2px 6px;
  border-radius: 8px;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(236, 72, 153, 0.3);
  animation: officialGlow 2s ease-in-out infinite alternate;
  white-space: nowrap;
}

@keyframes officialGlow {
  0% {
    box-shadow: 0 2px 4px rgba(236, 72, 153, 0.3);
  }
  100% {
    box-shadow: 0 2px 8px rgba(236, 72, 153, 0.5), 0 0 12px rgba(236, 72, 153, 0.2);
  }
}

.game-meta {
  font-size: 0.78rem;
  color: #be7c7c;
  margin-bottom: 2px;
  gap: 6px;
}

.game-rating-meta {
  align-items: center;
  gap: 8px;
  display: flex;
  margin-bottom: 8px;
}

/* 自定义评分星星颜色 */
:deep(.el-rate__item) {
  color: #f8d7da;
}

:deep(.el-rate__item.is-active) {
  color: #f472b6;
}

.loading {
  text-align: center;
  color: #be7c7c;
  margin-top: 40px;
  font-size: 1.1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.cute-spinner {
  color: #f472b6;
}

.loading-text {
  color: #be7c7c;
  font-weight: 500;
}

.empty {
  text-align: center;
  color: #be7c7c;
  margin-top: 40px;
  font-size: 1.1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.empty-icon {
  font-size: 2.5rem;
  opacity: 0.8;
}

.rank-section {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(251, 207, 232, 0.10);
  padding: 18px 12px 12px 12px;
  margin-top: 0;
}
.rank-item {
  display: flex;
  align-items: center;
  margin-bottom: 14px;
  gap: 10px;
}
.rank-index {
  font-size: 1.2rem;
  font-weight: bold;
  color: #e91e63;
  width: 24px;
  text-align: center;
}
.rank-img {
  width: 40px;
  height: 56px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid #f3e8ee;
}
.rank-info {
  flex: 1;
  min-width: 0;
}
.rank-title {
  font-size: 0.98rem;
  font-weight: bold;
  color: #be185d;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rank-meta {
  font-size: 0.82rem;
  color: #be7c7c;
}
/* 搜索区域 */
.search-section {
  display: flex;
  align-items: center;
  z-index: 2;
}

.search-box {
  position: relative;
  width: 200px;
}

.search-input {
  width: 100%;
  padding: 0.5rem 1rem;
  border: 2px solid #ff69b4;
  border-radius: 20px;
  font-size: 0.85rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  color: #333;
  outline: none;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.search-input:focus {
  border-color: #ff1493;
  box-shadow: 0 0 15px rgba(255, 20, 147, 0.2);
}

.search-input::placeholder {
  color: #ff69b4;
  opacity: 0.7;
}

/* 添加游戏按钮淡粉色 */
.add-game-btn {
  background: linear-gradient(45deg, #ffd6e0, #ffe4f0);
  color: #d63384;
  border: none;
  border-radius: 20px;
  font-weight: bold;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(255,182,213,0.13);
}
.add-game-btn:hover {
  background: linear-gradient(45deg, #ffb6d5, #ffb6d5);
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255,182,213,0.18);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-filter-section {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .search-box {
    width: 100%;
    min-width: auto;
  }
  
  .filter-controls {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .filter-select {
    min-width: 70px;
  }
}

/* 图片上传组件样式 */
.image-upload-container {
  width: 100%;
}

.image-uploader {
  width: 100%;
}

.image-uploader :deep(.el-upload) {
  width: 100%;
  display: block;
}

.image-preview {
  position: relative;
  width: 100%;
  height: 200px;
  border-radius: 12px;
  overflow: hidden;
  border: 2px dashed #f472b6;
  cursor: pointer;
  transition: all 0.3s ease;
}

.image-preview:hover {
  border-color: #ec4899;
  transform: scale(1.02);
}

.image-preview .el-image {
  width: 100%;
  height: 100%;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(236, 72, 153, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  color: white;
  font-weight: bold;
}

.image-preview:hover .image-overlay {
  opacity: 1;
}

.upload-placeholder {
  width: 100%;
  height: 200px;
  border: 2px dashed #f472b6;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #fef7f0 0%, #fdf2f8 50%);
}

.upload-placeholder:hover {
  border-color: #ec4899;
  background: linear-gradient(135deg, #fdf2f8 0%, #fce7f3 50%);
  transform: translateY(-2px);
}

.upload-icon {
  font-size: 2.5rem;
  margin-bottom: 8px;
  opacity: 0.8;
}

.upload-text {
  font-size: 1rem;
  font-weight: bold;
  color: #be185d;
  margin-bottom: 4px;
}

.upload-hint {
  font-size: 0.8rem;
  color: #be7c7c;
  text-align: center;
}

.image-actions {
  margin-top: 8px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .game-overview-container {
    padding: 24px 12px;
  }

  .corner-heart {
    font-size: 12px;
  }

  .game-title {
    font-size: 1rem;
    gap: 6px;
  }

  .official-badge {
    font-size: 0.7rem;
    padding: 1px 4px;
  }

  .game-card {
    height: 210px;
  }
  .game-image {
    height: 110px;
  }
  .game-info {
    padding-bottom: 6px;
  }
  
  .image-preview,
  .upload-placeholder {
    height: 150px;
  }
  
  .upload-icon {
    font-size: 2rem;
  }
  
  .upload-text {
    font-size: 0.9rem;
  }
  
  .upload-hint {
    font-size: 0.75rem;
  }
}
</style>
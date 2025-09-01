<template>
  <div class="fantasy-rating">
    <div class="search-bar">
      <div class="search-box">
        <input
          v-model="searchGameName"
          @input="onSearchInput"
          @keyup.enter="onSearchEnter"
          placeholder="🔍 搜索游戏名称..."
          class="search-input"
        />
        <button v-if="searchGameName" @click="clearSearch" class="clear-btn">✕</button>
      </div>
    </div>
    <div v-if="characters.length" class="card-container">
      <div class="character-card">
        <div class="card-content">
          <img :src="currentCharacter.avatar" alt="avatar" class="character-avatar" />
          <div class="info-section">
            <div class="game-name">{{ currentCharacter.game_name }}</div>
            <div class="character-name">{{ currentCharacter.name }}</div>
            <div class="character-info">{{ currentCharacter.cv }}</div>
            <div class="character-info">{{ currentCharacter.description }}</div>
            <div class="score-row">
              <span>外貌：</span>
              <el-rate
                v-model="currentCharacter.appearance_star"
                :max="5"
                :allow-half="false"
                allow-clear
                show-score
                @change="score => submitRating(currentCharacter, 'appearance_score', score * 2)"
              >
                <template #score>
                  <span>{{ (currentCharacter.appearance_star * 2).toFixed(1) }}分</span>
                </template>
              </el-rate>
              <span style="flex:1"></span>
              <el-button class="square-clear-btn" @click="clearSingleRating(currentCharacter, 'appearance')">✕</el-button>
            </div>
            <div class="score-row">
              <span>性格：</span>
              <el-rate
                v-model="currentCharacter.personality_star"
                :max="5"
                :allow-half="false"
                allow-clear
                show-score
                @change="score => submitRating(currentCharacter, 'personality_score', score * 2)"
              >
                <template #score>
                  <span>{{ (currentCharacter.personality_star * 2).toFixed(1) }}分</span>
                </template>
              </el-rate>
              <span style="flex:1"></span>
              <el-button class="square-clear-btn" @click="clearSingleRating(currentCharacter, 'personality')">✕</el-button>
            </div>
          </div>
        </div>
        <div class="card-actions">
          <el-button @click="prevCharacter" :disabled="currentIndex === 0">上一位</el-button>
          <el-button @click="nextCharacter" :disabled="currentIndex === characters.length - 1" style="margin-left: 16px;">下一位</el-button>
        </div>
      </div>
    </div>
    <div v-else style="text-align:center;color:#aaa;padding:40px;">暂无可攻略角色</div>
    <div class="report-btn-bar">
      <el-button type="primary" class="pink-girly-btn" @click="generateReport">生成喜好报告</el-button>
    </div>
    <el-dialog v-model="reportDialogVisible" title="我的乙女喜好报告" width="500px">
      <div v-html="reportHtml"></div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useRouter } from 'vue-router'

const loading = ref(false)
const characters = ref([])
const allCharacters = ref([])
const games = ref([])
const selectedGameId = ref('')
const user = JSON.parse(localStorage.getItem('user') || 'null')
const currentIndex = ref(0)
const currentCharacter = computed(() => characters.value[currentIndex.value] || {})
const searchGameName = ref('')
const reportDialogVisible = ref(false)
const reportHtml = ref('')
const router = useRouter()

async function loadGames() {
  try {
    const res = await axios.get('http://localhost:5000/games')
    if (res.data.status === 'success') {
      games.value = res.data.results
    }
  } catch {}
}

async function loadCharacters() {
  loading.value = true
  try {
    const res = await axios.get('http://localhost:5000/api/game-character/list')
    if (res.data.success) {
      let all = res.data.data.filter(c => c.role_type === '可攻略')
      if (user) {
        const ratingRes = await axios.get(`http://localhost:5000/api/game-character/ratings/user?user_id=${user.user_id}`)
        if (ratingRes.data.success) {
          const ratingMap = {}
          ratingRes.data.data.forEach(r => {
            ratingMap[r.character_id] = r
          })
          all.forEach(c => {
            if (ratingMap[c.id]) {
              c.appearance_star = ratingMap[c.id].appearance_score ? ratingMap[c.id].appearance_score / 2 : 0
              c.personality_star = ratingMap[c.id].personality_score ? ratingMap[c.id].personality_score / 2 : 0
            } else {
              c.appearance_star = 0
              c.personality_star = 0
            }
          })
        } else {
          all.forEach(c => {
            c.appearance_star = 0
            c.personality_star = 0
          })
        }
      } else {
        all.forEach(c => {
          c.appearance_star = 0
          c.personality_star = 0
        })
      }
      allCharacters.value = all
      filterByGame()
    }
  } catch (e) {
    ElMessage.error('加载角色失败')
  } finally {
    loading.value = false
  }
}

function filterByGame() {
  if (!selectedGameId.value) {
    characters.value = allCharacters.value
  } else {
    characters.value = allCharacters.value.filter(c => c.game_id === selectedGameId.value)
  }
  currentIndex.value = 0
}

async function submitRating(row, type, score) {
  if (!user) {
    ElMessage.error('请先登录')
    return
  }
  try {
    await axios.post('http://localhost:5000/api/game-character/ratings', {
      user_id: user.user_id,
      character_id: row.id,
      [type]: score
    })
    ElMessage.success('评分已提交')
  } catch (e) {
    ElMessage.error('提交失败')
  }
}

function prevCharacter() {
  if (currentIndex.value > 0) currentIndex.value--
}
function nextCharacter() {
  if (currentIndex.value < characters.value.length - 1) currentIndex.value++
}

function querySearchGames(queryString, cb) {
  const results = games.value
    .filter(g => g.name.toLowerCase().includes(queryString.toLowerCase()))
    .map(g => ({ value: g.name, game_id: g.game_id }))
  cb(results)
}

function onGameSelect(item) {
  selectedGameId.value = item.game_id
  filterByGame()
}

watch(searchGameName, (val) => {
  if (!val) {
    selectedGameId.value = ''
    filterByGame()
  }
})

function clearRating(row) {
  row.appearance_star = 0
  row.personality_star = 0
  submitRating(row, 'appearance_score', 0)
  submitRating(row, 'personality_score', 0)
}

function clearSingleRating(row, type) {
  if (type === 'appearance') {
    row.appearance_star = 0
    submitRating(row, 'appearance_score', 0)
  } else if (type === 'personality') {
    row.personality_star = 0
    submitRating(row, 'personality_score', 0)
  }
}

function generateReport() {
  router.push('/preference-report')
}

function onSearchInput() {
  if (!searchGameName.value) {
    selectedGameId.value = ''
    filterByGame()
  }
}

function onSearchEnter() {
  const val = searchGameName.value.trim().toLowerCase()
  if (!val) {
    selectedGameId.value = ''
    filterByGame()
    return
  }
  const found = games.value.find(g => g.name.toLowerCase().includes(val))
  if (found) {
    selectedGameId.value = found.game_id
    filterByGame()
  }
}

function clearSearch() {
  searchGameName.value = ''
  selectedGameId.value = ''
  filterByGame()
}

onMounted(() => {
  loadGames()
  loadCharacters()
})
</script>

<style scoped>
.fantasy-rating {
  max-width: none;
  width: 100%;
  padding: 40px 0 80px 0;
  position: relative;
  background: linear-gradient(135deg, #ffeef8 0%, #fff0f5 50%, #f8f0ff 100%);
  min-height: 100vh;
}
.search-bar {
  margin-bottom: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.search-box {
  position: relative;
  width: 260px;
}
.search-input {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 2px solid #f8bbd9;
  border-radius: 20px;
  font-size: 0.9rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  color: #333;
  outline: none;
  transition: all 0.3s ease;
  box-sizing: border-box;
}
.search-input:focus {
  border-color: #d63384;
  box-shadow: 0 0 15px rgba(216, 27, 96, 0.15);
}
.search-input::placeholder {
  color: #ba68c8;
  opacity: 0.7;
}
.clear-btn {
  position: absolute;
  right: 0.8rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #d63384;
  cursor: pointer;
  font-size: 1rem;
  opacity: 0.7;
  transition: opacity 0.3s ease;
}
.clear-btn:hover {
  opacity: 1;
}
.report-btn-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 32px;
  display: flex;
  justify-content: center;
  z-index: 10;
  pointer-events: none;
}
.report-btn-bar .pink-girly-btn {
  pointer-events: auto;
}
.card-container {
  display: flex;
  justify-content: center;
}
.character-card {
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 6px 24px rgba(255, 105, 180, 0.15);
  padding: 40px 32px;
  width: 1000px;
  height: 420px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.card-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  width: 100%;
  height: 260px;
}
.character-avatar {
  width: 180px;
  height: 260px;
  border-radius: 16px;
  object-fit: contain;
  background: #f8bbd0;
  margin-right: 32px;
  box-shadow: 0 4px 16px #f8bbd0;
}
.info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  min-width: 0;
  max-width: 700px;
}
.game-name {
  color: #1890ff;
  font-size: 15px;
  font-weight: bold;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.character-name {
  font-size: 20px;
  font-weight: bold;
  color: #d63384;
  margin-bottom: 4px;
}
.character-info {
  color: #888;
  font-size: 14px;
  margin-bottom: 4px;
  text-align: left;
  max-width: 100%;
  white-space: normal;
  overflow: visible;
  text-overflow: initial;
}
.score-row {
  display: flex;
  align-items: center;
  margin: 10px 0 0 0;
  gap: 8px;
}
.card-actions {
  margin-top: 18px;
  display: flex;
  justify-content: center;
  gap: 16px;
}
.pink-girly-btn {
  background: linear-gradient(90deg, #ffb6d5 0%, #ffd6ec 100%);
  color: #d63384;
  border: none;
  border-radius: 16px;
  font-size: 13px;
  font-family: 'Smiley Sans', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-weight: 500;
  padding: 4px 16px;
  margin-left: 8px;
  box-shadow: none;
  transition: none;
}
.pink-girly-btn:hover {
  background: linear-gradient(90deg, #ffb6d5 0%, #ffd6ec 100%);
  color: #d63384;
  box-shadow: none;
  transform: none;
}
.square-clear-btn {
  width: 24px;
  height: 24px;
  min-width: 24px;
  min-height: 24px;
  max-width: 24px;
  max-height: 24px;
  padding: 0;
  margin-left: 24px;
  background: #ffd6ec;
  color: #d63384;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-family: inherit;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: none;
  transition: background 0.2s, color 0.2s;
}
.square-clear-btn:hover {
  background: #ffb6d5;
  color: #fff;
}
</style> 
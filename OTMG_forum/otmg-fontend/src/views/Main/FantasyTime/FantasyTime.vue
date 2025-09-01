<template>
  <div class="fantasy-time">
    <div class="header">
      <p>基于你的偏好数据，为你生成理想形象和AI对话</p>
    </div>

    <div class="content">
      <!-- 理想形象展示 -->
      <div class="ideal-character-section">
        <h2>🎭 你的理想形象</h2>
        <div class="character-card">
          <div class="character-avatar">
            <div v-if="isGeneratingImage" class="image-loading">
              <span>🎨</span>
              <div class="loading-text">生成中...</div>
            </div>
            <img 
              v-else-if="idealCharacterImage" 
              :src="idealCharacterImage" 
              class="ideal-character-img" 
              alt="理想形象"
              @click="showImageDialog = true"
            />
            <div v-else class="avatar-placeholder">
              <span>👤</span>
            </div>
          </div>
          <div class="character-info">
            <h3>{{ idealCharacter.name }}</h3>
            <div class="character-traits">
              <span v-if="idealCharacter.hair" class="trait-tag">{{ idealCharacter.hair }}发</span>
              <span v-if="idealCharacter.eye" class="trait-tag">{{ idealCharacter.eye }}瞳</span>
              <span v-if="idealCharacter.glass" class="trait-tag">{{ idealCharacter.glass }}</span>
              <span v-if="idealCharacter.aura" class="trait-tag">{{ idealCharacter.aura }}</span>
              <span v-if="idealCharacter.age" class="trait-tag">{{ idealCharacter.age }}</span>
            </div>
            <div class="character-personality">
              <p v-if="idealCharacter.baseChar">性格：{{ idealCharacter.baseChar }}</p>
              <p v-if="idealCharacter.tone">语气：{{ idealCharacter.tone }}</p>
              <p v-if="idealCharacter.world">世界观：{{ idealCharacter.world }}</p>
            </div>
           
          </div>
        </div>
      </div>

      <!-- AI对话区域 -->
      <div class="chat-section">
        <h2>💬 与理想形象对话</h2>
        <div class="chat-container">
          <div class="chat-messages" ref="chatMessages">
            <div v-for="(message, index) in messages" :key="index" 
                 :class="['message', message.type]">
              <div class="message-content">
                <div class="message-avatar">
                  <div v-if="message.type === 'ai' && isGeneratingImage" class="ai-avatar-loading">
                    <span>🎨</span>
                  </div>
                  <img 
                    v-else-if="message.type === 'ai' && idealCharacterImage && !isGeneratingImage" 
                    :src="idealCharacterImage" 
                    class="ai-avatar-img" 
                    alt="理想形象"
                    @click="showImageDialog = true"
                  />
                  <span v-else-if="message.type === 'ai'">🤖</span>
                  <img 
                    v-else-if="currentUser?.avatar && !userAvatarError" 
                    :src="getFullAvatarUrl(currentUser.avatar)" 
                    class="user-avatar-img" 
                    alt="用户头像"
                    @error="handleAvatarError"
                  />
                  <span v-else class="user-avatar-icon">💕</span>
                </div>
                <div class="message-text">{{ message.text }}</div>
              </div>
              <div class="message-time">{{ message.time }}</div>
            </div>
          </div>
          
          <div class="chat-input">
            <el-input
              v-model="inputMessage"
              placeholder="输入你想说的话..."
              @keyup.enter="sendMessage"
              :disabled="isGenerating"
            />
            <el-button 
              type="primary" 
              @click="sendMessage" 
              :loading="isGenerating"
              :disabled="!inputMessage.trim()"
            >
              发送
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片大图对话框 -->
    <el-dialog 
      v-model="showImageDialog" 
      width="600px" 
      :show-close="true"
      :show-header="false"
      center
    >
      <div class="image-dialog-content">
        <img 
          v-if="idealCharacterImage" 
          :src="idealCharacterImage" 
          class="large-character-img" 
          alt="理想形象大图"
        />
        <div v-else class="no-image-placeholder">
          <span>暂无图片</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const idealCharacter = ref({
  name: '理想中的Ta',
  hair: '',
  eye: '',
  glass: '',
  aura: '',
  age: '',
  baseChar: '',
  tone: '',
  world: ''
})

const messages = ref([])
const inputMessage = ref('')
const isGenerating = ref(false)
const chatMessages = ref(null)
const currentUser = ref(null)
const defaultAvatar = '/src/assets/logo.png'
const userAvatarError = ref(false)
const idealCharacterImage = ref('')
const isGeneratingImage = ref(false)
const ratingStats = ref({
  appearanceCount: 0,
  personalityCount: 0
})
const showImageDialog = ref(false)
const chatHistory = ref([])

// 获取完整的头像URL
function getFullAvatarUrl(avatar) {
  if (!avatar) return defaultAvatar
  if (avatar.startsWith('http')) return avatar
  return `http://localhost:5000${avatar}`
}

// 处理头像加载错误
function handleAvatarError() {
  userAvatarError.value = true
}

// 生成理想形象图片
async function generateIdealCharacterImage() {
  if (isGeneratingImage.value) return
  
  const traits = {
    hair: idealCharacter.value.hair,
    eyes: idealCharacter.value.eye,
    glasses: idealCharacter.value.glass,
    aura: idealCharacter.value.aura,
    age: idealCharacter.value.age
  }
  
  // 检查是否有足够的特征来生成图片
  const hasTraits = Object.values(traits).some(trait => trait)
  if (!hasTraits) {
    console.log('没有足够的特征来生成理想形象图片')
    return
  }
  
  isGeneratingImage.value = true
  
  try {
    const response = await axios.post('http://localhost:5000/api/generate-ideal-character', {
      traits: traits
    })
    
    if (response.data.success) {
      idealCharacterImage.value = response.data.image_data
      console.log('理想形象图片生成成功，AI头像已更新')
    } else {
      console.error('生成理想形象图片失败:', response.data.message)
    }
  } catch (error) {
    console.error('生成理想形象图片请求失败:', error)
  } finally {
    isGeneratingImage.value = false
  }
}

// 获取用户偏好数据
async function loadUserPreferences() {
  try {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user) {
      ElMessage.warning('请先登录')
      return
    }

    // 获取当前用户详细信息
    try {
      const userRes = await axios.get(`http://localhost:5000/users/${user.user_id}`)
      if (userRes.data && userRes.data.user_id) {
        currentUser.value = userRes.data
      } else {
        currentUser.value = user
      }
    } catch (e) {
      currentUser.value = user
    }

    // 获取角色评分数据
    const charRes = await axios.get('http://localhost:5000/api/game-character/list')
    if (!charRes.data.success) throw new Error('角色获取失败')
    
    let all = charRes.data.data.filter(c => c.role_type === '可攻略')
    
    // 获取用户评分
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

    const rated = all.filter(c => c.appearance_star > 0 || c.personality_star > 0)
    if (!rated.length) {
      ElMessage.warning('暂无评分数据，无法生成理想形象')
      return
    }

    // 计算评分统计
    const appearanceCount = rated.filter(c => c.appearance_star > 0).length
    const personalityCount = rated.filter(c => c.personality_star > 0).length
    ratingStats.value = { appearanceCount, personalityCount }
    
    console.log(`评分统计: 外貌评分${appearanceCount}个角色，性格评分${personalityCount}个角色`)

    // 统计标签偏好
    const ratedIds = rated.map(c => c.id)
    const tagScoreMap = {}
    const characterTagsMap = {}
    
    const tagReqs = ratedIds.map(id =>
      axios.get(`http://localhost:5000/api/character-tags?character_id=${id}`)
    )
    const resArr = await Promise.all(tagReqs)
    resArr.forEach((res, idx) => {
      if (res.data.status === 'success') {
        characterTagsMap[ratedIds[idx]] = res.data.results
      }
    })

    // 使用固定的标签分类，与PreferenceReport.vue保持一致
    const appearanceTags = ["发色", "瞳色", "眼镜配饰", "整体气质", "年龄特征"]
    const personalityTags = ["基础性格", "语气", "世界观倾向"]

    console.log('使用的标签分类:', { appearanceTags, personalityTags })

    rated.forEach(c => {
      // 外貌标签分数
      if (c.appearance_star > 0) {
        (characterTagsMap[c.id] || []).forEach(ct => {
          const tag = ct.tag
          if (!tag) return
          const values = (ct.value || '').split(',')
          values.forEach(val => {
            if (!val) return
            if (!tagScoreMap[tag.name]) tagScoreMap[tag.name] = {}
            if (!tagScoreMap[tag.name][val]) tagScoreMap[tag.name][val] = 0
            // 外貌相关标签
            if (appearanceTags.includes(tag.name)) {
              tagScoreMap[tag.name][val] += c.appearance_star
              console.log(`  - 外貌标签 "${tag.name}": "${val}" += ${c.appearance_star}`)
            }
          })
        })
      }
      // 性格标签分数
      if (c.personality_star > 0) {
        (characterTagsMap[c.id] || []).forEach(ct => {
          const tag = ct.tag
          if (!tag) return
          const values = (ct.value || '').split(',')
          values.forEach(val => {
            if (!val) return
            if (!tagScoreMap[tag.name]) tagScoreMap[tag.name] = {}
            if (!tagScoreMap[tag.name][val]) tagScoreMap[tag.name][val] = 0
            // 性格相关标签
            if (personalityTags.includes(tag.name)) {
              tagScoreMap[tag.name][val] += c.personality_star
              console.log(`  - 性格标签 "${tag.name}": "${val}" += ${c.personality_star}`)
            }
          })
        })
      }
    })

    // 生成理想形象
    const tagFavMap = {}
    for (const tagName in tagScoreMap) {
      const valueMap = tagScoreMap[tagName]
      let best = null, bestScore = -1
      for (const val in valueMap) {
        if (valueMap[val] > bestScore) {
          bestScore = valueMap[val]
          best = val
        }
      }
      if (best && bestScore > 0) { // 只选择有分数的标签
        tagFavMap[tagName] = { value: best, score: bestScore }
        console.log(`标签 ${tagName}: 选择 ${best} (分数: ${bestScore})`)
      }
    }

    console.log('评分统计详情:', {
      appearanceTags,
      personalityTags,
      tagScoreMap,
      tagFavMap
    })

    idealCharacter.value = {
      name: '理想中的Ta',
      hair: tagFavMap['发色']?.value || '',
      eye: tagFavMap['瞳色']?.value || '',
      glass: tagFavMap['眼镜配饰']?.value || '',
      aura: tagFavMap['整体气质']?.value || '',
      age: tagFavMap['年龄特征']?.value || '',
      baseChar: tagFavMap['基础性格']?.value || '',
      tone: tagFavMap['语气']?.value || '',
      world: tagFavMap['世界观倾向']?.value || ''
    }

    // 添加欢迎消息
    addMessage('ai', generateWelcomeMessage())

    // 生成理想形象图片
    await generateIdealCharacterImage()

  } catch (error) {
    console.error('加载用户偏好失败:', error)
    ElMessage.error('加载用户偏好失败: ' + (error.message || '未知错误'))
  }
}

function generateWelcomeMessage() {
  const { hair, eye, glass, aura, age, baseChar, tone, world } = idealCharacter.value
  let message = '你好！我是基于你的偏好生成的理想形象。'
  
  // 外貌特征描述
  const appearanceTraits = []
  if (hair) appearanceTraits.push(`${hair}发`)
  if (eye) appearanceTraits.push(`${eye}瞳`)
  if (glass) appearanceTraits.push(glass)
  if (aura) appearanceTraits.push(`${aura}气质`)
  if (age) appearanceTraits.push(age)
  
  if (appearanceTraits.length > 0) {
    message += `我有着${appearanceTraits.join('、')}的外貌特征，`
  }
  
  // 性格特征描述
  const personalityTraits = []
  if (baseChar) personalityTraits.push(`${baseChar}的性格`)
  if (tone) personalityTraits.push(`${tone}的语气`)
  if (world) personalityTraits.push(`${world}的世界观`)
  
  if (personalityTraits.length > 0) {
    message += `以及${personalityTraits.join('、')}。`
  }
  
  message += '有什么想和我聊的吗？'
  return message
}

function addMessage(type, text) {
  const now = new Date()
  const time = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  const msg = {
    type,
    text,
    time,
    id: Date.now() + Math.random()
  }
  messages.value.push(msg)
  // 新增：同步到chatHistory
  if (type === 'user') {
    chatHistory.value.push({ role: 'user', content: text })
  } else if (type === 'ai') {
    chatHistory.value.push({ role: 'assistant', content: text })
  }
  // 滚动到底部
  nextTick(() => {
    if (chatMessages.value) {
      chatMessages.value.scrollTop = chatMessages.value.scrollHeight
    }
  })
}

async function sendMessage() {
  if (!inputMessage.value.trim() || isGenerating.value) return
  const userMessage = inputMessage.value.trim()
  addMessage('user', userMessage)
  inputMessage.value = ''
  isGenerating.value = true
  try {
    // 新增：发送完整历史
    const response = await axios.post('http://localhost:5000/api/fantasy-chat', {
      messages: chatHistory.value,
      character_traits: idealCharacter.value
    })
    if (response.data.success) {
      addMessage('ai', response.data.reply)
    } else {
      addMessage('ai', '抱歉，我现在有点累，稍后再和你聊天吧~')
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    addMessage('ai', '网络连接出现问题，请稍后再试~')
  } finally {
    isGenerating.value = false
  }
}

onMounted(() => {
  loadUserPreferences()
  // 新增：初始化历史和欢迎消息
  chatHistory.value.length = 0
})
</script>

<style scoped>
.fantasy-time {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.header h1 {
  color: #d63384;
  font-size: 32px;
  margin-bottom: 8px;
  font-weight: bold;
}

.header p {
  color: #666;
  font-size: 16px;
}

.content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
}

.ideal-character-section,
.chat-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(214, 51, 132, 0.1);
}

.ideal-character-section h2,
.chat-section h2 {
  color: #d63384;
  margin-bottom: 20px;
  font-size: 20px;
  font-weight: bold;
}

.character-card {
  display: flex;
  gap: 20px;
  align-items: center;
}

.character-avatar {
  flex-shrink: 0;
}

.avatar-placeholder {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #ffb6d5 0%, #ffd6ec 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
}

.image-loading {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #ffb6d5 0%, #ffd6ec 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.loading-text {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #d63384;
}

.ideal-character-img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #ffb6d5;
  box-shadow: 0 4px 12px rgba(214, 51, 132, 0.2);
  transition: all 0.3s ease;
}

.ideal-character-img:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(214, 51, 132, 0.3);
  cursor: pointer;
}

.character-info h3 {
  color: #d63384;
  margin-bottom: 12px;
  font-size: 18px;
}

.character-traits {
  margin-bottom: 12px;
}

.trait-tag {
  display: inline-block;
  background: #fce7f3;
  color: #d63384;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-right: 8px;
  margin-bottom: 4px;
}

.character-personality p {
  margin: 4px 0;
  color: #666;
  font-size: 14px;
}

.character-stats {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.character-stats p {
  margin: 4px 0;
  color: #888;
  font-size: 12px;
  font-style: italic;
}

.chat-container {
  height: 500px;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #fafafa;
  border-radius: 12px;
  margin-bottom: 16px;
}

.message {
  margin-bottom: 16px;
  animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.message.user .message-content {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  background: #fce7f3;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  overflow: hidden;
  position: relative;
}

.message.ai .message-avatar {
  background: #e0f2fe;
}

.message.user .message-avatar {
  background: #ffb6d5;
}

.user-avatar-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.ai-avatar-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e0f2fe;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.ai-avatar-img:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  cursor: pointer;
}

.ai-avatar-loading {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.05);
  }
}

.user-avatar-icon {
  font-size: 16px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.message-text {
  background: white;
  padding: 12px 16px;
  border-radius: 16px;
  max-width: 70%;
  word-wrap: break-word;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message.ai .message-text {
  background: #e0f2fe;
}

.message.user .message-text {
  background: #ffb6d5;
  color: white;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  margin-left: 44px;
}

.message.user .message-time {
  margin-left: 0;
  margin-right: 44px;
  text-align: right;
}

.chat-input {
  display: flex;
  gap: 12px;
  align-items: center;
}

.chat-input .el-input {
  flex: 1;
}

.chat-input .el-input :deep(.el-input__wrapper) {
  border-radius: 20px;
  border: 2px solid #fce7f3;
  box-shadow: none;
}

.chat-input .el-input :deep(.el-input__wrapper:hover) {
  border-color: #ffb6d5;
}

.chat-input .el-input :deep(.el-input__wrapper.is-focus) {
  border-color: #d63384;
  box-shadow: 0 0 0 2px rgba(214, 51, 132, 0.1);
}

.chat-input .el-button {
  background: linear-gradient(90deg, #d63384 0%, #e91e63 100%);
  border: none;
  border-radius: 20px;
  padding: 12px 24px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.chat-input .el-button:hover {
  background: linear-gradient(90deg, #c2255c 0%, #d81b60 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(214, 51, 132, 0.3);
}

@media (max-width: 768px) {
  .content {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .character-card {
    flex-direction: column;
    text-align: center;
  }
}

/* 图片对话框样式 */
.image-dialog-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.large-character-img {
  max-width: 100%;
  max-height: 500px;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(214, 51, 132, 0.2);
  object-fit: contain;
  transition: all 0.3s ease;
}

.large-character-img:hover {
  transform: scale(1.02);
  box-shadow: 0 12px 32px rgba(214, 51, 132, 0.3);
}

.no-image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 300px;
  background: linear-gradient(135deg, #fce7f3 0%, #f8bbd0 100%);
  border-radius: 16px;
  color: #d63384;
  font-size: 18px;
  font-weight: 500;
}
</style> 
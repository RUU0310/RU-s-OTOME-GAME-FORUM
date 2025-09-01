<template>
  <div class="user-page-bk-container" v-if="user">
    <h2>个人中心</h2>
    
 

    <!-- 个人信息卡片 -->
    <div class="user-info-card">
      <!-- 用户基本信息 -->
      <div class="user-info-bk-header">
        <el-upload
          class="avatar-uploader"
          action="http://localhost:5000/upload"
          :show-file-list="false"
          :on-success="handleAvatarSuccess"
          name="file"
          :disabled="!editMode"
        >
          <el-image
            v-if="form.avatar"
            :src="form.avatar"
            class="user-avatar-bk"
            fit="cover"
          />
          <el-icon v-else><Plus /></el-icon>
        </el-upload>
        <div class="user-info-bk-title">
          <div class="user-info-bk-username">{{ form.username }}</div>
          <div class="user-info-bk-nickname">{{ form.nickname }}</div>
        </div>
        <el-button v-if="!editMode" type="primary" @click="editMode = true" class="girly-btn girly-btn--small">
          编辑
        </el-button>
      </div>

      <!-- 用户表单 -->
      <el-form :model="form" label-width="90px" class="user-form-bk" :rules="rules" ref="formRef" :disabled="!editMode">
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" :disabled="!editMode" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" :disabled="!editMode" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" :disabled="!editMode" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input type="textarea" v-model="form.bio" rows="2" :disabled="!editMode" />
        </el-form-item>
        <el-form-item v-if="editMode">
          <el-button type="primary" @click="onSubmit">保存</el-button>
          <el-button @click="onCancel">取消</el-button>
          <el-button type="warning" @click="showPwdDialog = true">修改密码</el-button>
        </el-form-item>
      </el-form>

      <!-- 升级身份按钮 -->
      <div v-if="user && user.role === 'user'" class="upgrade-section">
        <!-- 未申请状态 -->
        <div v-if="!user.upgrade_status || user.upgrade_status === 'none'" class="upgrade-state">
          <el-button type="success" @click="showUpgradeDialog = true" class="upgrade-button girly-btn">
            <span class="btn-icon">🚀</span>
            申请成为发行商
          </el-button>
        </div>
        
        <!-- 待审核状态 -->
        <div v-else-if="user.upgrade_status === 'pending'" class="upgrade-state pending">
          <div class="pending-badge">
            <span class="pending-icon">⏳</span>
            <span class="pending-text">申请审核中</span>
          </div>
          <p class="pending-message">您的升级申请已提交，请等待管理员审核</p>
          <p class="pending-time" v-if="user.upgrade_request_time">
            申请时间：{{ formatRequestTime(user.upgrade_request_time) }}
          </p>
        </div>
        
        <!-- 被拒绝状态 -->
        <div v-else-if="user.upgrade_status === 'rejected'" class="upgrade-state rejected">
          <div class="rejected-badge">
            <span class="rejected-icon">❌</span>
            <span class="rejected-text">申请被拒绝</span>
          </div>
          <p class="rejected-message">很抱歉，您的升级申请未能通过审核</p>
          <el-button type="primary" @click="showUpgradeDialog = true" class="retry-button">
            <span class="retry-icon">🔄</span>
            重新申请
          </el-button>
        </div>
      </div>

      <!-- 发行商功能区域 -->
      <div v-if="user && user.role === 'publisher'" class="publisher-section girly-publisher-section">
        <div class="publisher-badge girly-badge">
          <span class="developer-icon">🎀</span>
          <span class="developer-text">发行商</span>
        </div>
        <div class="publisher-actions">
          <el-button class="girly-btn" @click="openPublishGameDialog">
            <span class="btn-icon">🌸</span>
            发行游戏
          </el-button>
        </div>
      </div>
    </div>

       <!-- 我发行的游戏 -->
       <div class="my-published-games-section">
      <h3>我发行的游戏</h3>
      <div class="game-list">
        <div v-for="game in myPublishedGames" :key="game.game_id" class="game-item" @click="goToGameDetail(game.game_id)">
          <el-image :src="game.image_url" class="game-cover" fit="cover" />
          <div class="game-info">
            <h4>
              <span v-if="game.is_official" class="official-badge">[官方]</span>
              {{ game.name }}
            </h4>
            <p class="game-publisher">{{ game.publisher }}</p>
          </div>
          <div class="game-actions">
            <el-button size="small" type="primary" @click.stop="editPublishedGame(game)">编辑</el-button>
            <el-button size="small" type="danger" @click.stop="deletePublishedGame(game)">删除</el-button>
          </div>
        </div>
        <div v-if="myPublishedGames.length === 0" class="empty-state">
          <p>还没有发行的游戏</p>
        </div>
      </div>
    </div>

    <!-- 游戏状态展示 -->
    <div class="game-status-section">
      <h3>我的游戏</h3>
      <div class="game-status-tabs">
        <el-tabs v-model="activeTab" @tab-click="handleTabClick">
          <el-tab-pane label="想玩" name="wish">
            <div class="game-list">
              <div v-for="game in wishGames" :key="game.game_id" class="game-item" @click="goToGameDetail(game.game_id)">
                <el-image :src="game.image_url" class="game-cover" fit="cover" />
                <div class="game-info">
                  <h4>
                    <span v-if="game.is_official" class="official-badge">[官方]</span>
                    {{ game.name }}
                  </h4>
                  <p class="game-publisher">{{ game.publisher }}</p>
                </div>
              </div>
              <div v-if="wishGames.length === 0" class="empty-state">
                <p>还没有想玩的游戏</p>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="在玩" name="playing">
            <div class="game-list">
              <div v-for="game in playingGames" :key="game.game_id" class="game-item" @click="goToGameDetail(game.game_id)">
                <el-image :src="game.image_url" class="game-cover" fit="cover" />
                <div class="game-info">
                  <h4>
                    <span v-if="game.is_official" class="official-badge">[官方]</span>
                    {{ game.name }}
                  </h4>
                  <p class="game-publisher">{{ game.publisher }}</p>
                </div>
              </div>
              <div v-if="playingGames.length === 0" class="empty-state">
                <p>还没有在玩的游戏</p>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="玩过" name="played">
            <div class="game-list">
              <div v-for="game in playedGames" :key="game.game_id" class="game-item" @click="goToGameDetail(game.game_id)">
                <el-image :src="game.image_url" class="game-cover" fit="cover" />
                <div class="game-info">
                  <h4>
                    <span v-if="game.is_official" class="official-badge">[官方]</span>
                    {{ game.name }}
                  </h4>
                  <p class="game-publisher">{{ game.publisher }}</p>
                </div>
              </div>
              <div v-if="playedGames.length === 0" class="empty-state">
                <p>还没有玩过的游戏</p>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- 收藏帖子展示 -->
    <div class="favorite-posts-section">
      <h3>我的收藏</h3>
      <div v-if="favoritePosts.length" class="posts-container">
        <div v-for="post in favoritePosts" :key="post.post_id" class="post-card" @click="goToPostDetail(post.post_id)">
          <div class="post-content">
            <h4 class="post-title">{{ post.title }}</h4>
            <div class="post-meta">
              <span class="author">👤 {{ post.nickname || post.username || '未知用户' }}</span>
              <span v-if="post.group_name" class="group">🏠 {{ post.group_name }}</span>
              <span v-if="post.category_name" class="category">🏷️ {{ post.category_name }}</span>
              <span class="time">🕒 {{ formatTime(post.created_at) }}</span>
              <span class="likes">💝 {{ post.like_count }}</span>
              <span class="favorite-time">⭐ {{ formatTime(post.favorite_time) }}</span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <p>还没有收藏的帖子</p>
      </div>
    </div>

    <!-- 我的拼团展示 -->
    <div class="my-group-buys-section">
      <h3>我的拼团</h3>
      <div v-if="myGroupBuys.length" class="group-buys-container">
        <div v-for="gb in myGroupBuys" :key="gb.group_buy_id" class="group-buy-card" @click="goToGroupBuyDetail(gb.group_buy_id)">
          <el-image :src="gb.product?.image" class="group-buy-cover" fit="cover" />
          <div class="group-buy-info">
            <h4 class="group-buy-title">{{ gb.title }}</h4>
            <div class="group-buy-meta">
              <span class="status">{{ gb.status === 'recruiting' ? '招募中' : gb.status === 'full' ? '已满员' : gb.status === 'completed' ? '已完成' : gb.status }}</span>
              <span class="deadline" v-if="gb.deadline">截止：{{ formatTime(gb.deadline) }}</span>
              <span class="created">创建：{{ formatTime(gb.created_at) }}</span>
              <span class="member-count">人数：{{ gb.member_count }}/{{ gb.total_max_count }}</span>
            </div>
            <div class="group-buy-product">商品：{{ gb.product?.name }}</div>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <p>还没有发起的拼团</p>
      </div>
    </div>

    <!-- 我参与的拼团展示 -->
    <div class="my-group-buys-section">
      <h3>我参与的拼团</h3>
      <div v-if="joinedGroupBuys.length" class="group-buys-container">
        <div v-for="gb in joinedGroupBuys" :key="gb.group_buy_id" class="group-buy-card" @click="goToGroupBuyDetail(gb.group_buy_id)">
          <el-image :src="gb.product?.image" class="group-buy-cover" fit="cover" />
          <div class="group-buy-info">
            <h4 class="group-buy-title">{{ gb.title }}</h4>
            <div class="group-buy-meta">
              <span class="status">{{ gb.status === 'recruiting' ? '招募中' : gb.status === 'full' ? '已满员' : gb.status === 'completed' ? '已完成' : gb.status }}</span>
              <span class="deadline" v-if="gb.deadline">截止：{{ formatTime(gb.deadline) }}</span>
              <span class="created">创建：{{ formatTime(gb.created_at) }}</span>
              <span class="member-count">人数：{{ gb.member_count }}/{{ gb.total_max_count }}</span>
            </div>
            <div class="group-buy-product">商品：{{ gb.product?.name }}</div>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <p>还没有参与的拼团</p>
      </div>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="showPwdDialog" title="修改密码" width="400px">
      <el-form :model="pwdForm" label-width="90px" :rules="pwdRules" ref="pwdFormRef">
        <el-form-item label="新密码" prop="password">
          <el-input v-model="pwdForm.password" type="password" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm">
          <el-input v-model="pwdForm.confirm" type="password" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPwdDialog = false">取消</el-button>
        <el-button type="primary" @click="onPwdSubmit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 升级身份对话框 -->
    <el-dialog v-model="showUpgradeDialog" width="800px" :show-close="true" :close-on-click-modal="false">
      <div class="upgrade-dialog-content">
        <div class="upgrade-info">
          <h4>申请成为发行商/个人开发者身份</h4>
          <p>您将获得：</p>
          <ul>
            <li>✨ 特殊的发行商标识</li>
            <li>🎯 发布官方游戏的权利</li>
            <li>🌟 社区中的特殊地位</li>
          </ul>
          <div class="upgrade-process">
            <h5>申请流程：</h5>
            <ol>
              <li>提交申请</li>
              <li>管理员审核（1-3个工作日）</li>
              <li>审核通过后自动升级</li>
            </ol>
          </div>
          <p class="upgrade-note">注意：申请提交后请耐心等待审核结果</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="showUpgradeDialog = false">取消</el-button>
        <el-button type="success" @click="onUpgradeSubmit">提交申请</el-button>
      </template>
    </el-dialog>

    <!-- 发行游戏对话框 -->
    <el-dialog v-model="showPublishGameDialog" width="50%" @close="resetPublishGameForm">
      <el-form
        ref="publishGameFormRef"
        :model="publishGameForm"
        status-icon
        label-width="120px"
        class="publish-game-form"
        :rules="publishGameRules"
      >
        <el-form-item label="游戏名称" prop="name">
          <el-input v-model="publishGameForm.name" autocomplete="off"/>
        </el-form-item>
        <el-form-item label="封面图" prop="image_url">
          <el-upload
            class="avatar-uploader"
            action="http://localhost:5000/upload"
            :show-file-list="false"
            :on-success="handleGameImageSuccess"
            :before-upload="beforeUpload"
            name="file"
            :headers="{}"
          >
            <img v-if="publishGameForm.image_url" :src="publishGameForm.image_url" class="game-cover-preview" />
            <el-icon v-else><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="游戏简介" prop="description">
          <el-input type="textarea" v-model="publishGameForm.description" autocomplete="off" :rows="3"/>
        </el-form-item>
        <el-form-item label="地区" prop="region">
          <el-select v-model="publishGameForm.region" placeholder="请选择地区">
            <el-option label="日本" value="日本"/>
            <el-option label="欧美" value="欧美"/>
            <el-option label="国产" value="国产"/>
            <el-option label="韩国" value="韩国"/>
          </el-select>
        </el-form-item>
        <el-form-item label="发行公司" prop="publisher">
          <el-input v-model="publishGameForm.publisher" autocomplete="off"/>
        </el-form-item>
        <el-form-item label="发行日期" prop="release_date">
          <el-date-picker
            v-model="publishGameForm.release_date"
            type="date"
            placeholder="选择发行日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="购买链接" prop="purchase_link">
          <el-input v-model="publishGameForm.purchase_link" autocomplete="off"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPublishGameDialog = false">取消</el-button>
        <el-button type="primary" @click="onPublishGameSubmit" :loading="publishing">发行游戏</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { Plus } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const user = ref(null)
const form = reactive({
  username: '',
  nickname: '',
  phone: '',
  email: '',
  avatar: '',
  bio: ''
})
const rules = {
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }]
}
const formRef = ref()
const showPwdDialog = ref(false)
const pwdForm = reactive({ password: '', confirm: '' })
const pwdFormRef = ref()
const pwdRules = {
  password: [{ required: true, message: '请输入新密码', trigger: 'blur' }],
  confirm: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: (rule, value) => value === pwdForm.password, message: '两次输入不一致', trigger: 'blur' }
  ]
}
const editMode = ref(false)
const activeTab = ref('wish')
const wishGames = ref([])
const playingGames = ref([])
const playedGames = ref([])
const favoritePosts = ref([])
const showUpgradeDialog = ref(false)
const showPublishGameDialog = ref(false)
const publishing = ref(false)
const publishGameForm = reactive({
  name: '',
  image_url: '',
  description: '',
  region: '',
  publisher: '',
  release_date: '',
  purchase_link: ''
})
const publishGameFormRef = ref()
const myPublishedGames = ref([])

// 发行游戏表单验证规则
const publishGameRules = {
  name: [{ required: true, message: '请输入游戏名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入游戏简介', trigger: 'blur' }],
  region: [{ required: true, message: '请选择地区', trigger: 'change' }],
  publisher: [{ required: true, message: '请输入发行公司', trigger: 'blur' }],
  release_date: [{ required: true, message: '请选择发行日期', trigger: 'change' }]
}

// 新增：我的拼团
const myGroupBuys = ref([])
const joinedGroupBuys = ref([])

const getUserInfo = async () => {
  const localUser = JSON.parse(localStorage.getItem('user') || 'null')
  if (!localUser) return
  try {
    const res = await axios.get(`http://localhost:5000/users/${localUser.user_id}`)
    if (res.data && res.data.user_id) {
      user.value = res.data
      Object.assign(form, res.data)
      await getGameStatus()
      await getFavoritePosts()
    }
  } catch (e) {
    ElMessage.error('获取用户信息失败')
  }
}

function handleAvatarSuccess(res) {
  if (res.status === 'success' && res.file_url) {
    form.avatar = 'http://localhost:5000' + res.file_url
  }
}

function onCancel() {
  if (user.value) Object.assign(form, user.value)
  editMode.value = false
}

async function onSubmit() {
  try {
    await axios.put(`http://localhost:5000/users/${user.value.user_id}`, form)
    ElMessage.success('保存成功')
    getUserInfo()
    editMode.value = false
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

async function onPwdSubmit() {
  if (!pwdForm.password || pwdForm.password !== pwdForm.confirm) {
    ElMessage.error('两次输入不一致')
    return
  }
  try {
    await axios.put(`http://localhost:5000/users/${user.value.user_id}`, { password: pwdForm.password })
    ElMessage.success('密码修改成功')
    showPwdDialog.value = false
    pwdForm.password = ''
    pwdForm.confirm = ''
  } catch (e) {
    ElMessage.error('密码修改失败')
  }
}

async function getGameStatus() {
  try {
    const res = await axios.get(`http://localhost:5000/users/${user.value.user_id}/game-status`)
    if (res.data && res.data.game_status) {
      const gameStatus = res.data.game_status
      wishGames.value = gameStatus.wish
      playingGames.value = gameStatus.playing
      playedGames.value = gameStatus.played
    }
  } catch (e) {
    ElMessage.error('获取游戏状态失败')
  }
}

async function getFavoritePosts() {
  try {
    const res = await axios.get(`http://localhost:5000/users/${user.value.user_id}/favorite-posts`)
    if (res.data && res.data.status === 'success') {
      favoritePosts.value = res.data.favorite_posts
    }
  } catch (e) {
    ElMessage.error('获取收藏帖子失败')
  }
}

function handleTabClick(tab) {
  activeTab.value = tab.name
}

function formatTime(time) {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function changeGameStatus(gameId, newStatus) {
  try {
    await axios.post(`http://localhost:5000/games/${gameId}/user_status`, {
      user_id: user.value.user_id,
      status: newStatus
    })
    ElMessage.success('状态更新成功')
    await getGameStatus()
  } catch (e) {
    ElMessage.error('状态更新失败')
  }
}

async function removeGameStatus(gameId) {
  try {
    await axios.post(`http://localhost:5000/games/${gameId}/user_status`, {
      user_id: user.value.user_id,
      status: null
    })
    ElMessage.success('移除成功')
    await getGameStatus()
  } catch (e) {
    ElMessage.error('移除失败')
  }
}

function goToGameDetail(gameId) {
  router.push(`/games/${gameId}`)
}

function goToPostDetail(postId) {
  router.push(`/post/${postId}`)
}

async function onUpgradeSubmit() {
  try {
    const res = await axios.post(`http://localhost:5000/users/${user.value.user_id}/upgrade`)
    if (res.data.status === 'success') {
      ElMessage.success(res.data.message || '申请提交成功，请等待审核')
      // 更新本地存储的用户信息
      const localUser = JSON.parse(localStorage.getItem('user') || '{}')
      localUser.upgrade_status = 'pending'
      localUser.upgrade_request_time = res.data.upgrade_request_time
      localStorage.setItem('user', JSON.stringify(localUser))
      // 重新获取用户信息
      await getUserInfo()
      showUpgradeDialog.value = false
    }
  } catch (e) {
    if (e.response && e.response.data && e.response.data.message) {
      ElMessage.error(e.response.data.message)
    } else {
      ElMessage.error('申请提交失败')
    }
  }
}

// 格式化申请时间
function formatRequestTime(timeString) {
  if (!timeString) return ''
  try {
    const date = new Date(timeString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return timeString
  }
}

function handleGameImageSuccess(res) {
  if (res.status === 'success' && res.file_url) {
    publishGameForm.image_url = 'http://localhost:5000' + res.file_url
  }
}

function beforeUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('请上传图片格式文件')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

async function onPublishGameSubmit() {
  try {
    await publishGameFormRef.value.validate()
    publishing.value = true
    const gameData = { ...publishGameForm }
    gameData.is_official = true
    if (publishGameForm.game_id) {
      // 编辑
      const res = await axios.put(`http://localhost:5000/games/${publishGameForm.game_id}`, gameData)
      if (res.data.status === 'success') {
        ElMessage.success('游戏修改成功')
        showPublishGameDialog.value = false
        publishing.value = false
        resetPublishGameForm()
        await getMyPublishedGames()
        await getGameStatus()
      }
    } else {
      // 新增
      const res = await axios.post(`http://localhost:5000/games`, gameData)
      if (res.data.status === 'success') {
        ElMessage.success('游戏发布成功')
        showPublishGameDialog.value = false
        publishing.value = false
        resetPublishGameForm()
        await getMyPublishedGames()
        await getGameStatus()
      }
    }
  } catch (e) {
    if (e.message) {
      ElMessage.error(e.message)
    } else {
      ElMessage.error('操作失败')
    }
    publishing.value = false
  }
}

function resetPublishGameForm() {
  Object.assign(publishGameForm, {
    name: '',
    image_url: '',
    description: '',
    region: '',
    publisher: '',
    release_date: '',
    purchase_link: '',
    game_id: undefined
  })
}

async function getMyGroupBuys() {
  try {
    const localUser = JSON.parse(localStorage.getItem('user') || 'null')
    if (!localUser) return
    const res = await axios.get(`http://localhost:5000/api/group-buy/users/${localUser.user_id}/my-group-buys`)
    if (res.data && res.data.success) {
      myGroupBuys.value = res.data.data
    }
  } catch (e) {
    ElMessage.error('获取我的拼团失败')
  }
}

async function getJoinedGroupBuys() {
  try {
    const localUser = JSON.parse(localStorage.getItem('user') || 'null')
    if (!localUser) return
    const res = await axios.get(`http://localhost:5000/api/group-buy/users/${localUser.user_id}/joined-group-buys`)
    if (res.data && res.data.success) {
      joinedGroupBuys.value = res.data.data
    }
  } catch (e) {
    ElMessage.error('获取我参与的拼团失败')
  }
}

function goToGroupBuyDetail(groupBuyId) {
  router.push(`/group-buy/${groupBuyId}`)
}

// 打开发行游戏对话框时，自动填充发行公司
function openPublishGameDialog() {
  // 优先用nickname，没有则用username
  publishGameForm.publisher = user.value?.nickname || user.value?.username || ''
  showPublishGameDialog.value = true
}

async function getMyPublishedGames() {
  try {
    // 先获取所有游戏，前端筛选
    const res = await axios.get('http://localhost:5000/games')
    if (res.data && res.data.status === 'success') {
      const games = res.data.results || []
      // 以nickname优先，没有则用username
      const publisherName = user.value?.nickname || user.value?.username || ''
      myPublishedGames.value = games.filter(g => g.publisher === publisherName)
    }
  } catch (e) {
    ElMessage.error('获取我发行的游戏失败')
  }
}

function editPublishedGame(game) {
  Object.assign(publishGameForm, {
    name: game.name,
    image_url: game.image_url,
    description: game.description,
    region: game.region,
    publisher: game.publisher,
    release_date: game.release_date,
    purchase_link: game.purchase_link
  })
  publishGameForm.game_id = game.game_id // 标记为编辑
  showPublishGameDialog.value = true
}

async function deletePublishedGame(game) {
  try {
    await ElMessageBox.confirm('确定要删除该游戏吗？', '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    const res = await axios.delete(`http://localhost:5000/games/${game.game_id}`)
    if (res.data && res.data.status === 'success') {
      ElMessage.success('删除成功')
      await getMyPublishedGames()
      await getGameStatus()
    } else {
      ElMessage.error(res.data.message || '删除失败')
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => {
  getUserInfo()
  getMyGroupBuys()
  getJoinedGroupBuys()
  getMyPublishedGames()
})
</script>

<style scoped>
.user-page-bk-container {
  max-width: 800px;
  margin: 30px auto;
  padding: 0px 32px 40px 32px;
}

.user-page-bk-container h2 {
  text-align: center;
  color: #e91e63;
  font-size: 2rem;
  margin-top: 0;
  margin-bottom: 32px;
  letter-spacing: 2px;
}

.user-info-card {
  padding: 32px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(233, 30, 99, 0.2);
  margin-bottom: 32px;
}

.user-info-bk-header {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 40px;
  padding: 24px;
  border-radius: 16px;
  background: rgba(255, 182, 193, 0.05);
  border: 1px solid rgba(255, 182, 193, 0.2);
}

.user-avatar-bk {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  background: linear-gradient(135deg, #ffb6c1, #ffc0cb);
  box-shadow: 0 8px 24px rgba(233, 30, 99, 0.2);
  border: 4px solid rgba(255, 255, 255, 0.8);
  transition: transform 0.3s ease;
}

.user-avatar-bk:hover {
  transform: scale(1.05);
}

.user-info-bk-title {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.user-info-bk-username {
  font-size: 0.9rem;
  color: #ff8fa3;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.user-info-bk-nickname {
  font-size: 1.8rem;
  font-weight: bold;
  color: #e91e63;
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.user-form-bk {
  padding: 0;
  margin-bottom: 32px;
}

.user-form-bk :deep(.el-button) {
  border-radius: 20px;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.user-form-bk :deep(.el-button--primary) {
  background: linear-gradient(135deg, #e91e63, #ff6b9d);
  border: none;
  box-shadow: 0 4px 16px rgba(233, 30, 99, 0.3);
}

.user-form-bk :deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(233, 30, 99, 0.4);
}

.user-form-bk :deep(.el-button--default) {
  background: linear-gradient(135deg, #ff8fa3, #ffb6c1);
  border: none;
  color: white;
  box-shadow: 0 4px 16px rgba(255, 143, 163, 0.3);
}

.user-form-bk :deep(.el-button--default:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 143, 163, 0.4);
}

.user-form-bk :deep(.el-button--warning) {
  background: linear-gradient(135deg, #ff9800, #ffb74d);
  border: none;
  color: white;
  box-shadow: 0 4px 16px rgba(255, 152, 0, 0.3);
}

.user-form-bk :deep(.el-button--warning:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 152, 0, 0.4);
}

.game-status-section {
  margin-top: 32px;
  padding: 32px;
}

.game-status-section h3 {
  color: #e91e63;
  margin-bottom: 24px;
  font-size: 1.5rem;
  font-weight: bold;
  text-align: center;
  letter-spacing: 2px;
}

.game-status-tabs {
  margin-top: 24px;
}

.game-status-tabs :deep(.el-tabs__header) {
  margin-bottom: 24px;
}

.game-status-tabs :deep(.el-tabs__nav-wrap::after) {
  background: rgba(255, 182, 193, 0.3);
}

.game-status-tabs :deep(.el-tabs__item) {
  color: #ff8fa3;
  font-weight: bold;
  font-size: 1rem;
  letter-spacing: 1px;
  transition: all 0.3s ease;
}

.game-status-tabs :deep(.el-tabs__item.is-active) {
  color: #e91e63;
}

.game-status-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(135deg, #e91e63, #ff6b9d);
  height: 3px;
  border-radius: 2px;
}

.game-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 24px;
  margin-top: 24px;
}

.game-item {
  padding: 16px;
  transition: all 0.3s ease;
  border: 2px solid rgba(255, 182, 193, 0.2);
  cursor: pointer;
  border-radius: 16px;
}

.game-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(233, 30, 99, 0.15);
  border-color: rgba(233, 30, 99, 0.4);
}

.game-cover {
  width: 100%;
  height: 140px;
  border-radius: 12px;
  margin-bottom: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.game-item:hover .game-cover {
  transform: scale(1.02);
}

.game-info h4 {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  font-weight: bold;
  color: #e91e63;
  line-height: 1.4;
  letter-spacing: 0.5px;
}

.game-publisher {
  font-size: 0.9rem;
  color: #ff8fa3;
  margin: 0;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #ff8fa3;
  grid-column: 1 / -1;
}

.empty-state p {
  font-size: 1.1rem;
  margin: 0;
  letter-spacing: 1px;
}

/* 升级身份相关样式 */
.upgrade-section {
  margin: 32px 0;
  text-align: center;
  padding: 24px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(255, 182, 193, 0.1) 0%, rgba(255, 192, 203, 0.05) 100%);
  border: 2px solid rgba(255, 182, 193, 0.3);
  position: relative;
  overflow: hidden;
}

.upgrade-section::before {
  content: '✨';
  position: absolute;
  top: 10px;
  left: 10px;
  font-size: 1.2rem;
  opacity: 0.6;
  animation: sparkle 2s infinite ease-in-out;
}

.upgrade-section::after {
  content: '🌸';
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 1.2rem;
  opacity: 0.6;
  animation: sparkle 2s infinite ease-in-out 1s;
}

@keyframes sparkle {
  0%, 100% { transform: scale(1) rotate(0deg); opacity: 0.6; }
  50% { transform: scale(1.2) rotate(180deg); opacity: 1; }
}

.upgrade-state {
  padding: 24px;
  border-radius: 16px;
  position: relative;
}

.upgrade-state.pending {
  background: linear-gradient(135deg, rgba(255, 248, 225, 0.9) 0%, rgba(255, 236, 179, 0.8) 100%);
  border: 2px solid rgba(255, 193, 7, 0.4);
  box-shadow: 0 4px 16px rgba(255, 193, 7, 0.2);
}

.upgrade-state.rejected {
  background: linear-gradient(135deg, rgba(255, 242, 240, 0.9) 0%, rgba(255, 204, 199, 0.8) 100%);
  border: 2px solid rgba(244, 67, 54, 0.4);
  box-shadow: 0 4px 16px rgba(244, 67, 54, 0.2);
}

.pending-badge {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(45deg, #ffc107, #ffd54f);
  color: white;
  padding: 12px 20px;
  border-radius: 25px;
  font-weight: bold;
  margin-bottom: 16px;
  box-shadow: 0 6px 20px rgba(255, 193, 7, 0.3);
  animation: gentle-pulse 3s infinite ease-in-out;
  letter-spacing: 1px;
  position: relative;
}

.pending-badge::before {
  content: '✨';
  position: absolute;
  left: -8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.8rem;
  animation: twinkle 1.5s infinite ease-in-out;
}

.rejected-badge {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(45deg, #f44336, #ef5350);
  color: white;
  padding: 12px 20px;
  border-radius: 25px;
  font-weight: bold;
  margin-bottom: 16px;
  box-shadow: 0 6px 20px rgba(244, 67, 54, 0.3);
  letter-spacing: 1px;
  position: relative;
}

.rejected-badge::before {
  content: '💔';
  position: absolute;
  left: -8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.8rem;
  animation: heartbeat 1.5s infinite ease-in-out;
}

.pending-icon, .rejected-icon {
  margin-right: 10px;
  font-size: 1.3rem;
}

.pending-text, .rejected-text {
  font-size: 1.1rem;
}

.pending-message, .rejected-message {
  color: #666;
  margin: 12px 0;
  font-size: 1rem;
  line-height: 1.6;
  font-weight: 300;
}

.pending-time {
  color: #999;
  font-size: 0.9rem;
  margin: 12px 0;
  font-weight: 300;
}

.retry-button {
  background: linear-gradient(45deg, #e91e63, #ff6b9d);
  border: none;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 25px;
  box-shadow: 0 6px 20px rgba(233, 30, 99, 0.3);
  transition: all 0.3s ease;
  margin-top: 16px;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
}

.retry-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.retry-button:hover::before {
  left: 100%;
}

.retry-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(233, 30, 99, 0.4);
}

.retry-icon {
  margin-right: 8px;
  font-size: 1.1rem;
}

.upgrade-button.girly-btn {
  background: #ffb6d5 !important;
  color: #fff !important;
  border: none !important;
  border-radius: 40px !important;
  font-size: 22px !important;
  font-weight: bold;
  box-shadow: 0 2px 8px #ffd6ec !important;
  padding: 18px 48px !important;
  letter-spacing: 2px;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  transition: all 0.2s;
}
.upgrade-button.girly-btn .btn-icon {
  font-size: 1.5em;
}
.upgrade-button.girly-btn:hover {
  background: #b5d0ff !important;
  color: #fff !important;
  box-shadow: 0 4px 16px #b5d0ff !important;
  transform: translateY(-2px) scale(1.04);
}

/* 发行商功能区域样式 */
.publisher-section {
  margin-top: 32px;
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 24px;
  border-radius: 16px;
  background: rgba(255, 182, 193, 0.05);
  border: 1px solid rgba(255, 182, 193, 0.2);
}

.publisher-badge {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(45deg, #2196f3, #42a5f5);
  color: white;
  padding: 12px 20px;
  border-radius: 25px;
  font-weight: bold;
  box-shadow: 0 6px 20px rgba(33, 150, 243, 0.3);
  animation: gentle-pulse 3s infinite ease-in-out;
  letter-spacing: 1px;
}

.publisher-actions {
  display: flex;
  gap: 16px;
}

.publish-game-button {
  background: linear-gradient(45deg, #4caf50, #66bb6a);
  border: none;
  padding: 14px 28px;
  font-size: 1rem;
  font-weight: bold;
  border-radius: 25px;
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3);
  transition: all 0.3s ease;
  letter-spacing: 1px;
}

.publish-game-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(76, 175, 80, 0.4);
}

.publish-icon {
  margin-right: 8px;
  font-size: 1.2rem;
}

/* 对话框样式 */
:deep(.el-dialog) {
  border-radius: 20px;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  background: transparent !important;
  padding: 0 !important;
  border-bottom: none !important;
}

:deep(.el-dialog__title) {
  color: #e91e63;
  font-weight: bold;
  letter-spacing: 1px;
}

:deep(.el-dialog__body) {
  padding: 32px;
  background: white;
}

:deep(.el-dialog__footer) {
  padding: 24px 32px;
  background: white;
  border-top: 1px solid rgba(255, 182, 193, 0.3);
}

/* 升级身份弹窗特殊样式 */
:deep(.el-dialog) {
  border-radius: 24px;
  box-shadow: 0 12px 40px rgba(233, 30, 99, 0.2);
}

:deep(.el-dialog .el-dialog__body) {
  padding: 40px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 248, 255, 0.9) 100%);
}

:deep(.el-dialog .el-dialog__footer) {
  padding: 24px 40px;
  background: rgba(255, 255, 255, 0.95);
  border-top: 2px solid rgba(255, 182, 193, 0.3);
}

.upgrade-dialog-content {
  text-align: center;
  padding: 20px 0;
}

.upgrade-info h4 {
  color: #e91e63;
  margin-bottom: 24px;
  font-size: 1.6rem;
  font-weight: bold;
  letter-spacing: 1px;
  text-align: center;
}

.upgrade-info p {
  color: #666;
  margin-bottom: 10px;
  line-height: 1.4;
  font-size: 1rem;
}

.upgrade-info ul {
  text-align: left;
  margin: 12px 0;
  padding-left: 32px;
  list-style: none;
}

.upgrade-info li {
  color: #666;
  margin-bottom: 6px;
  line-height: 1.3;
  font-size: 0.98rem;
  position: relative;
  padding-left: 8px;
}

.upgrade-process {
  background: linear-gradient(135deg, rgba(255, 182, 193, 0.1) 0%, rgba(255, 192, 203, 0.05) 100%);
  border-radius: 16px;
  padding: 16px;
  margin: 14px 0;
  text-align: left;
  border: 2px solid rgba(255, 182, 193, 0.3);
  position: relative;
}

.upgrade-process h5 {
  color: #e91e63;
  margin-bottom: 8px;
  font-size: 1.08rem;
  font-weight: bold;
  letter-spacing: 1px;
}

.upgrade-process ol {
  margin: 0;
  padding-left: 20px;
}

.upgrade-process li {
  color: #666;
  margin-bottom: 4px;
  line-height: 1.3;
  font-size: 0.98rem;
  position: relative;
}

.upgrade-note {
  color: #ff9800 !important;
  font-weight: bold;
  font-size: 0.98rem;
  letter-spacing: 0.5px;
  background: rgba(255, 152, 0, 0.1);
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 152, 0, 0.3);
  margin-top: 12px;
}

.game-cover-preview {
  width: 100%;
  height: 140px;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.avatar-uploader {
  border: 2px dashed rgba(255, 182, 193, 0.5);
  border-radius: 12px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  background: white;
}

.avatar-uploader:hover {
  border-color: #e91e63;
  background: #f8f9fa;
  transform: scale(1.02);
}

.avatar-uploader .el-icon {
  font-size: 32px;
  color: #ff8fa3;
  width: 100%;
  height: 140px;
  text-align: center;
  line-height: 140px;
  transition: color 0.3s ease;
}

.avatar-uploader:hover .el-icon {
  color: #e91e63;
}

/* 收藏帖子区域样式 */
.favorite-posts-section {
  margin-top: 32px;
  padding: 32px;
}

.favorite-posts-section h3 {
  color: #e91e63;
  margin-bottom: 24px;
  font-size: 1.5rem;
  font-weight: bold;
  text-align: center;
  letter-spacing: 2px;
}

.posts-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.post-card {
  padding: 16px;
  transition: all 0.3s ease;
  border: 2px solid rgba(255, 182, 193, 0.2);
  cursor: pointer;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.8);
}

.post-card:hover {
  transform: translateX(10px);
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 8px 25px rgba(233, 30, 99, 0.15);
  border-color: rgba(233, 30, 99, 0.4);
}

.post-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.post-title {
  font-size: 1.1rem;
  font-weight: bold;
  color: #e91e63;
  line-height: 1.4;
  letter-spacing: 0.5px;
  margin: 0;
  cursor: pointer;
  transition: color 0.3s ease;
}

.post-title:hover {
  color: #c2185b;
}

.post-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 0.85rem;
  opacity: 0.8;
}

.post-meta span {
  color: #ff8fa3;
}

.author {
  font-weight: 500;
}

.group {
  background: rgba(255, 182, 193, 0.1);
  padding: 2px 8px;
  border-radius: 10px;
  color: #e91e63 !important;
}

.category {
  background: rgba(255, 182, 193, 0.1);
  padding: 2px 8px;
  border-radius: 10px;
  color: #e91e63 !important;
}

.time {
  color: #ba68c8 !important;
}

.likes {
  color: #e91e63 !important;
  font-weight: 500;
}

.favorite-time {
  color: #ff9800 !important;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-page-bk-container {
    margin: 20px;
    padding: 24px 20px;
  }
  
  .user-info-card {
    padding: 24px;
  }
  
  .user-info-bk-header {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .game-list {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 16px;
  }
  
  .game-cover {
    height: 120px;
  }
  
  .game-info h4 {
    font-size: 1rem;
  }
  
  .publisher-section {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .publisher-actions {
    justify-content: center;
  }

  .publish-game-button {
    width: 100%;
    max-width: 240px;
  }
  
  .upgrade-button, .retry-button {
    width: 100%;
    max-width: 240px;
  }
  
  .post-meta {
    flex-direction: column;
    gap: 6px;
  }
}

@keyframes twinkle {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
}

.publish-game-form {
  padding: 24px;
}

/* 新增：我的拼团 */
.my-group-buys-section {
  margin-top: 32px;
  padding: 32px;
}
.my-group-buys-section h3 {
  color: #e91e63;
  margin-bottom: 24px;
  font-size: 1.5rem;
  font-weight: bold;
  text-align: center;
  letter-spacing: 2px;
}
.group-buys-container {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}
.group-buy-card {
  display: flex;
  flex-direction: row;
  align-items: center;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(233, 30, 99, 0.08);
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid rgba(255, 182, 193, 0.2);
  min-width: 320px;
  max-width: 480px;
  width: 100%;
}
.group-buy-card:hover {
  box-shadow: 0 8px 32px rgba(233, 30, 99, 0.15);
  border-color: #e91e63;
  background: #fff0f6;
}
.group-buy-cover {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  margin-right: 20px;
  object-fit: cover;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.group-buy-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.group-buy-title {
  font-size: 1.1rem;
  font-weight: bold;
  color: #e91e63;
  margin: 0;
}
.group-buy-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 0.95rem;
  opacity: 0.8;
}
.group-buy-meta .status {
  color: #4caf50;
  font-weight: 500;
}
.group-buy-meta .deadline {
  color: #ff9800;
}
.group-buy-meta .created {
  color: #ba68c8;
}
.group-buy-meta .member-count {
  color: #e91e63;
  font-weight: 500;
}
.group-buy-product {
  color: #ff8fa3;
  font-size: 0.95rem;
  margin-top: 4px;
}
@media (max-width: 768px) {
  .my-group-buys-section {
    padding: 20px 10px;
  }
  .group-buys-container {
    flex-direction: column;
    gap: 12px;
  }
  .group-buy-card {
    min-width: 0;
    max-width: 100%;
    flex-direction: column;
    align-items: flex-start;
    padding: 12px;
  }
  .group-buy-cover {
    margin-right: 0;
    margin-bottom: 10px;
    width: 100%;
    height: 120px;
  }
}

.girly-publisher-section {
  background: #fff7fa !important;
  border: 2px solid #ffb6d5 !important;
  box-shadow: 0 4px 16px #ffd6ec;
}
.girly-badge {
  background: #ffb6d5 !important;
  color: #fff !important;
  box-shadow: 0 2px 8px #ffd6ec !important;
  border-radius: 40px !important;
  font-size: 1.1rem;
  padding: 14px 32px !important;
}
.girly-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 16px 40px;
  font-size: 20px;
  font-weight: bold;
  color: #fff;
  background: #ffb6d5;
  border: none;
  border-radius: 40px;
  box-shadow: 0 2px 8px #ffd6ec;
  transition: all 0.2s;
  letter-spacing: 2px;
  cursor: pointer;
  position: relative;
}
.girly-btn .btn-icon {
  font-size: 1.4em;
}
.girly-btn:hover {
  background: #b5d0ff;
  box-shadow: 0 4px 16px #b5d0ff;
  transform: translateY(-2px) scale(1.04);
}

.girly-btn--small {
  padding: 6px 22px;
  font-size: 15px;
  border-radius: 24px;
}

.official-badge {
  color: #2196f3;
  font-weight: bold;
  margin-right: 4px;
}

.my-published-games-section {
  margin-top: 32px;
  padding: 32px;
}
.my-published-games-section h3 {
  color: #e91e63;
  margin-bottom: 24px;
  font-size: 1.5rem;
  font-weight: bold;
  text-align: center;
  letter-spacing: 2px;
}
</style>
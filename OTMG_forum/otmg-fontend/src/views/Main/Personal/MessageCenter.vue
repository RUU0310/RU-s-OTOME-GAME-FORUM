<template>
  <div class="message-center">
    <h2>消息中心</h2>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="拼团申请审核" name="review">
        <el-table :data="requests" v-loading="loadingRequests" style="margin-top:24px;">
      <el-table-column label="拼团标题" prop="group_buy_title" />
      <el-table-column label="申请人" prop="nickname">
        <template #default="{ row }">
          {{ row.nickname || row.username }}
              <span v-if="cancelledOrders[row.user_id] !== undefined" style="color:#faad14;font-size:12px;margin-left:4px;">
                （跑单{{ cancelledOrders[row.user_id] }}次）
              </span>
        </template>
      </el-table-column>
      <el-table-column label="角色" prop="character_name" />
      <el-table-column label="份数" prop="count" />
      <el-table-column label="留言" prop="message" />
      <el-table-column label="申请时间" prop="created_at" />
      <el-table-column label="操作">
        <template #default="{ row }">
              <div class="action-row">
          <el-button v-if="row.status === 'pending'" type="success" size="small" @click="reviewRequest(row.id, true)">同意</el-button>
          <el-button v-if="row.status === 'pending'" type="danger" size="small" @click="reviewRequest(row.id, false)">拒绝</el-button>
          <span v-else-if="row.status === 'approved'" style="color:#67C23A;">已同意</span>
          <span v-else-if="row.status === 'rejected'" style="color:#F56C6C;">已拒绝</span>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="消息通知" name="notification">
        <el-table :data="messages" v-loading="loadingMessages" style="margin-top:24px;">
          <el-table-column label="内容" prop="content" />
          <el-table-column label="时间" prop="created_at" />
          <el-table-column label="状态">
            <template #default="{ row }">
              <span v-if="!row.is_read" style="color:#ff1493;">未读</span>
              <span v-else style="color:#aaa;">已读</span>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template #default="{ row }">
              <el-button v-if="!row.is_read" size="small" @click="markRead(row.id)">标为已读</el-button>
        </template>
      </el-table-column>
    </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const activeTab = ref('review')

// 拼团申请审核相关
const loadingRequests = ref(false)
const requests = ref([])
const user = JSON.parse(localStorage.getItem('user') || 'null')
const cancelledOrders = ref({})

async function fetchCancelledOrders(userIds) {
  const promises = userIds.map(uid =>
    axios.get(`http://localhost:5000/api/messages/user/${uid}/cancelled-orders`).then(res => {
      if (res.data.success) return [uid, res.data.cancelled_orders]
      return [uid, 0]
    }).catch(() => [uid, 0])
  )
  const results = await Promise.all(promises)
  results.forEach(([uid, count]) => {
    cancelledOrders.value[uid] = count
  })
}

async function loadRequests() {
  if (!user) return
  loadingRequests.value = true
  try {
    const res = await axios.get(`http://localhost:5000/api/group-buy/group-buys/requests?leader_id=${user.user_id}`)
    if (res.data.success) {
      requests.value = res.data.data
      // 批量获取所有申请人的跑单次数
      const userIds = [...new Set(res.data.data.map(r => r.user_id))]
      await fetchCancelledOrders(userIds)
    }
  } catch (e) {
    ElMessage.error('加载消息失败')
  } finally {
    loadingRequests.value = false
    syncHeaderDot()
  }
}

async function reviewRequest(id, approve) {
  if (!user) return
  loadingRequests.value = true
  try {
    const res = await axios.post(`http://localhost:5000/api/group-buy/group-buys/requests/${id}/review`, {
      reviewer_id: user.user_id,
      approve
    })
    if (res.data.success) {
      ElMessage.success('操作成功')
      await loadRequests()
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    loadingRequests.value = false
    syncHeaderDot()
  }
}

// 消息通知相关
const loadingMessages = ref(false)
const messages = ref([])
let timer = null

async function fetchMessages() {
  if (!user) return
  loadingMessages.value = true
  try {
    const res = await axios.get(`http://localhost:5000/api/messages/?user_id=${user.user_id}`)
    if (res.data.success) {
      messages.value = res.data.data
    }
  } finally {
    loadingMessages.value = false
    syncHeaderDot()
  }
}

async function markRead(id) {
  try {
    await axios.post(`http://localhost:5000/api/messages/${id}/read`)
    fetchMessages()
    syncHeaderDot()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

function syncHeaderDot() {
  const hasPendingRequest = requests.value.some(r => r.status === 'pending')
  const hasUnreadMsg = messages.value.some(m => !m.is_read)
  window.dispatchEvent(new CustomEvent('set-header-notification-dot', { detail: hasPendingRequest || hasUnreadMsg }))
}

// 监听 activeTab 变化，切换时刷新数据
watch(activeTab, (tab) => {
  if (tab === 'review') {
    loadRequests()
  } else if (tab === 'notification') {
    fetchMessages()
  }
})

onMounted(() => {
  loadRequests()
  fetchMessages()
})
onUnmounted(() => {
  // 不再需要定时器，移除
})
</script>

<style scoped>
.message-center {
  max-width: 900px;
  margin: 40px auto;
}
.action-row {
  display: flex;
  gap: 8px;
  align-items: center;
}
h2 {
  color: #ff1493;
  margin-bottom: 18px;
}
</style> 
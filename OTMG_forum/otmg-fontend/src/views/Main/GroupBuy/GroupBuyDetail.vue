<template>
  <div class="group-buy-detail">
    <div class="detail-header">
      <el-button @click="$router.back()" class="back-button">
        <span class="back-icon">←</span>
        返回
      </el-button>
      <h1 class="detail-title">拼团详情</h1>
      <el-button
        v-if="groupBuy && groupBuy.leader && groupBuy.leader.user_id == user.user_id && groupBuy.status !== 'completed'"
        type="success"
        @click="markAsCompleted"
        style="margin-left:auto;"
      >设为已完成</el-button>
      <el-select v-if="groupBuy && groupBuy.leader && groupBuy.leader.user_id == user.user_id"
                 v-model="editStatus"
                 style="margin-left: 16px; width: 120px;">
        <el-option label="招募中" value="recruiting" />
        <el-option label="已满员" value="full" />
        <el-option label="已完成" value="completed" />
      </el-select>
      <el-button v-if="groupBuy && groupBuy.leader && groupBuy.leader.user_id == user.user_id"
                 type="primary"
                 @click="updateStatus"
                 style="margin-left: 8px;">
        修改状态
      </el-button>
    </div>
    
    <div class="detail-content" v-loading="loading">
      <div v-if="groupBuy" class="detail-card">
        <h2>{{ groupBuy.title }}</h2>
        <p class="detail-description">{{ groupBuy.description }}</p>
        <p class="detail-status">状态：{{ getStatusText(groupBuy.status) }}</p>
        <div v-if="groupBuy.product" class="product-info" style="display:flex;align-items:center;gap:28px;margin-top:18px;">
          <img :src="groupBuy.product.image" alt="商品图片" style="width:160px;height:160px;object-fit:cover;border-radius:16px;box-shadow:0 2px 12px #f8bbd0;">
          <div>
            <div style="font-weight:bold;font-size:22px;color:#d63384;">{{ groupBuy.product.name }}</div>
            <div style="color:#888;margin-top:8px;font-size:15px;">{{ groupBuy.product.description }}</div>
          </div>
        </div>
        <div class="groupbuy-info" style="margin-top:18px;display:flex;flex-wrap:wrap;gap:32px 48px;align-items:center;">
          <div>
            <b>团长：</b>
            {{ groupBuy.leader?.nickname || groupBuy.leader?.username || '未知' }}
            <span v-if="leaderStats !== null" style="color:#faad14;font-size:13px;margin-left:6px;">
              （成功开团{{ leaderStats }}次）
            </span>
          </div>
          <div><b>联系方式：</b>{{ groupBuy.contact_info || '无' }}</div>
          <div><b>均价：</b><span style="color:#ff1493;font-weight:bold;">{{ groupBuy.average_price }} 元</span></div>
          <div><b>截止时间：</b>{{ groupBuy.deadline ? groupBuy.deadline.replace('T', ' ').slice(0, 16) : '无' }}</div>
          
        </div>
      </div>
      
      <div v-else class="empty-state">
        <p>拼团不存在或已被删除</p>
      </div>
      
      <div v-if="groupBuy && groupBuy.characters && groupBuy.characters.length" class="character-list">
        <h3>角色价格</h3>
        <el-table :data="groupBuy.characters" border style="width: 100%; margin-top: 12px;">
          <el-table-column label="角色" prop="name">
            <template #default="{ row }">
              <img :src="row.image" alt="" style="width:32px;height:32px;border-radius:50%;margin-right:8px;">
              {{ row.name }}
              <el-tag v-if="row.is_popular" type="danger" size="small" style="margin-left:6px;">热门</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="调价" prop="price_adjustment">
            <template #default="{ row }">
              <span :style="{ color: row.price_adjustment > 0 ? '#67C23A' : (row.price_adjustment < 0 ? '#F56C6C' : '#333') }">
                {{ row.price_adjustment > 0 ? '+' : '' }}{{ row.price_adjustment }} 元
              </span>
            </template>
          </el-table-column>
          <el-table-column label="可拼团个数" prop="max_count">
            <template #default="{ row }">
              <span>{{ row.max_count }}</span>
              <span style="color:#888;margin-left:8px;">(剩余{{ row.max_count - row.joined_count }}份)</span>
            </template>
          </el-table-column>
          <el-table-column label="最终价格">
            <template #default="{ row }">
              <b style="color:#ff1493;">
                {{ calcFinalPrice(row) }} 元
              </b>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template #default="{ row }">
              <template v-if="groupBuy.status !== 'completed'">
                <el-button
                  v-if="row.max_count > row.joined_count"
                  type="primary"
                  size="small"
                  @click="openRequestDialog(row)"
                >申请拼团</el-button>
                <el-input-number
                  v-if="getUserJoinedCount(row.character_id) > 0"
                  v-model="cancelCounts[row.character_id]"
                  :min="1"
                  :max="getUserJoinedCount(row.character_id)"
                  size="small"
                  style="width: 80px; margin-left: 8px; margin-right: 8px;"
                />
                <el-button
                  v-if="getUserJoinedCount(row.character_id) > 0"
                  type="danger"
                  size="small"
                  @click="cancelGroupBuy(row.character_id, cancelCounts[row.character_id] || 1)"
                >取消</el-button>
                <span v-if="row.max_count <= row.joined_count && getUserJoinedCount(row.character_id) === 0" style="color:#aaa;">已满</span>
              </template>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
    <el-dialog v-model="showRequestDialog" title="申请拼团" width="400px">
      <el-form :model="requestForm">
        <el-form-item label="申请份数">
          <el-input-number v-model="requestForm.count" :min="1" :max="requestForm.maxCount" />
        </el-form-item>
        <el-form-item label="留言">
          <el-input v-model="requestForm.message" type="textarea" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRequestDialog = false">取消</el-button>
        <el-button type="primary" @click="submitRequest" :loading="loading">提交申请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const loading = ref(false)
const groupBuy = ref(null)
const user = JSON.parse(localStorage.getItem('user') || 'null')
const joinCounts = ref({})
const cancelCounts = ref({})
const editStatus = ref('')
const leaderStats = ref(null)
const showRequestDialog = ref(false)
const requestForm = ref({ character_id: null, count: 1, maxCount: 1, message: '' })

// 获取拼团详情
const loadGroupBuyDetail = async () => {
  loading.value = true
  try {
    const response = await axios.get(`http://localhost:5000/api/group-buy/group-buys/${route.params.id}`)
    if (response.data.success) {
      groupBuy.value = response.data.data
      // 初始化每个角色的默认份数为1
      if (groupBuy.value.characters) {
        groupBuy.value.characters.forEach(c => {
          joinCounts.value[c.character_id] = 1
          cancelCounts.value[c.character_id] = 1
        })
      }
    }
  } catch (error) {
    ElMessage.error('获取拼团详情失败')
    console.error('Error loading group buy detail:', error)
  } finally {
    loading.value = false
  }
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'recruiting': '招募中',
    'full': '已满员',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || '招募中'
}

const calcFinalPrice = (row) => {
  if (!groupBuy.value) return '';
  const avg = Number(groupBuy.value.average_price) || 0;
  const adj = Number(row.price_adjustment) || 0;
  return (avg + adj).toFixed(2);
}

// 判断当前用户是否已参与该角色
function hasJoined(character_id) {
  if (!groupBuy.value || !user) return false
  // 假设后端只允许一个角色参与，前端只需判断是否有该用户参与该拼团即可
  // 如需支持多角色参与，可扩展
  if (!groupBuy.value.characters) return false
  // 这里需要后端返回当前用户参与的角色，或前端请求成员列表。简化处理：只要有一条记录即可
  // 这里假设后端只允许一个角色参与
  // 实际可根据业务调整
  return groupBuy.value.characters.some(c => c.joined_users && c.joined_users.includes(user.user_id) && c.character_id === character_id)
}

// 参与拼团
async function joinGroupBuy(character_id, count = 1) {
  if (!user) {
    ElMessage.error('请先登录')
    return
  }
  try {
    loading.value = true
    const res = await axios.post(`http://localhost:5000/api/group-buy/group-buys/${groupBuy.value.group_buy_id}/join`, {
      user_id: user.user_id,
      character_id,
      count
    })
    if (res.data.success) {
      ElMessage.success('参与成功')
      await loadGroupBuyDetail()
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (e) {
    ElMessage.error('参与失败')
  } finally {
    loading.value = false
  }
}

function getUserJoinedCount(character_id) {
  if (!groupBuy.value || !user) return 0
  if (!groupBuy.value.members) return 0
  return groupBuy.value.members.filter(m => m.user_id === user.user_id && m.character_id === character_id).length
}

async function cancelGroupBuy(character_id, count = 1) {
  if (!user) {
    ElMessage.error('请先登录')
    return
  }
  try {
    loading.value = true
    const res = await axios.post(`http://localhost:5000/api/group-buy/group-buys/${groupBuy.value.group_buy_id}/cancel`, {
      user_id: user.user_id,
      character_id,
      count
    })
    if (res.data.success) {
      ElMessage.success('取消成功')
      await loadGroupBuyDetail()
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (e) {
    ElMessage.error('取消失败')
  } finally {
    loading.value = false
  }
}

async function markAsCompleted() {
  try {
    loading.value = true
    const res = await axios.patch(`http://localhost:5000/api/group-buy/group-buys/${groupBuy.value.group_buy_id}`, {
      user_id: user.user_id,
      status: 'completed'
    })
    if (res.data.success) {
      ElMessage.success('已设为已完成')
      await loadGroupBuyDetail()
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    loading.value = false
  }
}

watch(() => groupBuy.value, (val) => {
  if (val) editStatus.value = val.status
})

async function updateStatus() {
  try {
    loading.value = true
    const res = await axios.patch(`http://localhost:5000/api/group-buy/group-buys/${groupBuy.value.group_buy_id}`, {
      user_id: user.user_id,
      status: editStatus.value
    })
    if (res.data.success) {
      ElMessage.success('状态已更新')
      await loadGroupBuyDetail()
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    loading.value = false
  }
}

async function loadLeaderStats() {
  if (groupBuy.value && groupBuy.value.leader) {
    try {
      const res = await axios.get(`http://localhost:5000/api/group-buy/user-group-buy-stats/${groupBuy.value.leader.user_id}`)
      leaderStats.value = res.data.successful_groups || 0
    } catch {
      leaderStats.value = 0
    }
  }
}

watch(() => groupBuy.value && groupBuy.value.leader, () => {
  loadLeaderStats()
})

function openRequestDialog(row) {
  requestForm.value.character_id = row.character_id
  requestForm.value.count = 1
  requestForm.value.maxCount = row.max_count - row.joined_count
  requestForm.value.message = ''
  showRequestDialog.value = true
}

async function submitRequest() {
  if (!user) {
    ElMessage.error('请先登录')
    return
  }
  try {
    loading.value = true
    const res = await axios.post(`http://localhost:5000/api/group-buy/group-buys/${groupBuy.value.group_buy_id}/request`, {
      user_id: user.user_id,
      character_id: requestForm.value.character_id,
      count: requestForm.value.count,
      message: requestForm.value.message
    })
    if (res.data.success) {
      ElMessage.success('申请已提交，等待团长审核')
      showRequestDialog.value = false
      await loadGroupBuyDetail()
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (e) {
    ElMessage.error('申请失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadGroupBuyDetail()
})
</script>

<style scoped>
.group-buy-detail {
  padding: 24px;
  min-height: 100vh;
  background: linear-gradient(135deg, #ffeef8 0%, #fff0f5 100%);
}

.detail-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
}

.back-button {
  background: #ffd6e0;
  color: #d63384;
  border: none;
  border-radius: 20px;
  font-weight: bold;
  padding: 8px 16px;
  box-shadow: 0 2px 8px rgba(255,182,213,0.13);
  transition: all 0.2s;
}
.back-button:hover {
  background: #ffb6d5;
  color: #fff;
}

.back-icon {
  margin-right: 4px;
}

.detail-title {
  color: #ff1493;
  font-size: 24px;
  font-weight: bold;
  margin: 0;
}

.detail-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(255, 105, 180, 0.1);
}

.detail-card h2 {
  color: #333;
  margin-bottom: 12px;
}

.detail-description {
  color: #666;
  margin-bottom: 16px;
}

.detail-status {
  color: #ff1493;
  font-weight: bold;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 40px;
}

.character-list {
  margin-top: 24px;
}

.character-list h3 {
  color: #333;
  margin-bottom: 12px;
}

.el-button[type="success"], .el-button.el-button--success {
  background: #ffd6e0 !important;
  color: #d63384 !important;
  border: none !important;
  border-radius: 20px !important;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(255,182,213,0.13);
  transition: all 0.2s;
}
.el-button[type="success"]:hover, .el-button.el-button--success:hover {
  background: #ffb6d5 !important;
  color: #fff !important;
}

.el-button[type="primary"], .el-button.el-button--primary {
  background: linear-gradient(45deg, #ffb6d5, #ff69b4) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 20px !important;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(255,182,213,0.13);
  transition: all 0.2s;
}
.el-button[type="primary"]:hover, .el-button.el-button--primary:hover {
  background: linear-gradient(45deg, #ff69b4, #ffb6d5) !important;
  color: #fff !important;
}

.el-button[type="danger"], .el-button.el-button--danger {
  background: #f8bbd9 !important;
  color: #d63384 !important;
  border: none !important;
  border-radius: 20px !important;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(255,182,213,0.13);
  transition: all 0.2s;
}
.el-button[type="danger"]:hover, .el-button.el-button--danger:hover {
  background: #ffb6d5 !important;
  color: #fff !important;
}

.el-input-number, .el-input__inner {
  border-radius: 12px !important;
}

.el-select {
  border-radius: 20px !important;
}

.el-dialog__footer .el-button {
  margin-left: 8px;
}
</style> 
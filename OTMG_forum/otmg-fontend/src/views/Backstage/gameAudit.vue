<template>
  <div class="game-audit-container">
    <!-- 统计和搜索 -->
    <div class="header">
      <div class="header-stats">
        <el-tag type="warning" size="large">待审核: {{ pendingCount }}</el-tag>
        <el-tag type="success" size="large">已通过: {{ approvedCount }}</el-tag>
        <el-tag type="danger" size="large">已拒绝: {{ rejectedCount }}</el-tag>
      </div>
      
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索游戏名称、发行商..."
          style="width: 300px; margin-right: 10px;"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 筛选标签页 -->
    <div class="filter-section">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="待审核" name="pending">
          <template #label>
            <span>待审核 <el-badge :value="pendingCount" class="tab-badge" /></span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="已通过" name="approved">
          <template #label>
            <span>已通过 <el-badge :value="approvedCount" class="tab-badge" /></span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="已拒绝" name="rejected">
          <template #label>
            <span>已拒绝 <el-badge :value="rejectedCount" class="tab-badge" /></span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 游戏列表 -->
    <el-table :data="filteredGames" style="width: 100%" v-loading="loading">
      <el-table-column prop="game_id" label="ID" width="80"></el-table-column>
      <el-table-column label="游戏封面" width="100">
        <template #default="scope">
          <el-image
            :src="scope.row.image_url"
            style="width: 60px; height: 80px;"
            fit="cover"
            :preview-src-list="[scope.row.image_url]"
          >
            <template #error>
              <div class="image-slot">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="游戏名称" min-width="150"></el-table-column>
      <el-table-column prop="publisher" label="发行商" width="120"></el-table-column>
      <el-table-column prop="region" label="地区" width="80"></el-table-column>
      <el-table-column prop="release_date" label="发行日期" width="120"></el-table-column>
      <el-table-column label="官方" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.is_official ? 'success' : 'info'">
            {{ scope.row.is_official ? '官方' : '非官方' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="提交时间" width="160"></el-table-column>
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip></el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="viewGame(scope.row)">查看</el-button>
          <el-button 
            v-if="scope.row.status === 'pending'" 
            size="small" 
            type="success" 
            @click="approveGame(scope.row)"
          >
            通过
          </el-button>
          <el-button 
            v-if="scope.row.status === 'pending'" 
            size="small" 
            type="danger" 
            @click="rejectGame(scope.row)"
          >
            拒绝
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[4, 8, 12, 20]"
        :total="totalGames"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 查看游戏详情对话框 -->
    <el-dialog
      v-model="showViewDialog"
      title="游戏详情"
      width="600px"
    >
      <div v-if="selectedGame" class="game-detail">
        <div class="detail-row">
          <label>游戏名称:</label>
          <span>{{ selectedGame.name }}</span>
        </div>
        <div class="detail-row">
          <label>游戏封面:</label>
          <el-image
            v-if="selectedGame.image_url"
            :src="selectedGame.image_url"
            style="width: 100px; height: 140px;"
            fit="cover"
          />
        </div>
        <div class="detail-row">
          <label>发行商:</label>
          <span>{{ selectedGame.publisher }}</span>
        </div>
        <div class="detail-row">
          <label>地区:</label>
          <span>{{ selectedGame.region }}</span>
        </div>
        <div class="detail-row">
          <label>发行日期:</label>
          <span>{{ selectedGame.release_date }}</span>
        </div>
        <div class="detail-row">
          <label>官方状态:</label>
          <el-tag :type="selectedGame.is_official ? 'success' : 'info'">
            {{ selectedGame.is_official ? '官方' : '非官方' }}
          </el-tag>
        </div>
        <div class="detail-row">
          <label>购买链接:</label>
          <a v-if="selectedGame.purchase_link" :href="selectedGame.purchase_link" target="_blank">
            {{ selectedGame.purchase_link }}
          </a>
          <span v-else>无</span>
        </div>
        <div class="detail-row">
          <label>游戏描述:</label>
          <div class="description-text">{{ selectedGame.description }}</div>
        </div>
        <div class="detail-row">
          <label>提交时间:</label>
          <span>{{ selectedGame.created_at }}</span>
        </div>
        <div class="detail-row">
          <label>审核状态:</label>
          <el-tag :type="getStatusType(selectedGame.status)">
            {{ getStatusText(selectedGame.status) }}
          </el-tag>
        </div>
      </div>
      <template #footer>
        <el-button @click="showViewDialog = false">关闭</el-button>
        <el-button 
          v-if="selectedGame && selectedGame.status === 'pending'" 
          type="success" 
          @click="approveGame(selectedGame)"
        >
          通过审核
        </el-button>
        <el-button 
          v-if="selectedGame && selectedGame.status === 'pending'" 
          type="danger" 
          @click="rejectGame(selectedGame)"
        >
          拒绝审核
        </el-button>
      </template>
    </el-dialog>

    <!-- 拒绝原因对话框 -->
    <el-dialog
      v-model="showRejectDialog"
      title="拒绝审核"
      width="400px"
    >
      <el-form :model="rejectForm" label-width="80px">
        <el-form-item label="拒绝原因">
          <el-input
            v-model="rejectForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入拒绝原因..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRejectDialog = false">取消</el-button>
        <el-button type="danger" @click="confirmReject">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Picture } from '@element-plus/icons-vue'
import axios from 'axios'

// 响应式数据
const games = ref([])
const loading = ref(false)
const activeTab = ref('pending')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(4)
const totalGames = ref(0)
const showViewDialog = ref(false)
const showRejectDialog = ref(false)
const selectedGame = ref(null)

// 统计数据
const pendingCount = ref(0)
const approvedCount = ref(0)
const rejectedCount = ref(0)

// 拒绝表单
const rejectForm = reactive({
  reason: ''
})

// 计算属性 - 过滤后的游戏列表
const filteredGames = computed(() => {
  let result = games.value

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(game => 
      game.name.toLowerCase().includes(keyword) ||
      game.publisher.toLowerCase().includes(keyword)
    )
  }

  // 分页处理
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return result.slice(start, end)
})

// 获取游戏列表
const fetchGames = async (status = 'pending') => {
  loading.value = true
  try {
    const response = await axios.get(`http://localhost:5000/games/audit?status=${status}`)
    if (response.data.status === 'success') {
      games.value = response.data.results
      // 计算过滤后的总数（用于分页）
      let filteredResult = games.value
      if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase()
        filteredResult = games.value.filter(game => 
          game.name.toLowerCase().includes(keyword) ||
          game.publisher.toLowerCase().includes(keyword)
        )
      }
      totalGames.value = filteredResult.length
    }
  } catch (error) {
    ElMessage.error('获取游戏列表失败')
    console.error('Error fetching games:', error)
  } finally {
    loading.value = false
  }
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const [pendingRes, approvedRes, rejectedRes] = await Promise.all([
      axios.get('http://localhost:5000/games/audit?status=pending'),
      axios.get('http://localhost:5000/games/audit?status=approved'),
      axios.get('http://localhost:5000/games/audit?status=rejected')
    ])
    
    pendingCount.value = pendingRes.data.status === 'success' ? pendingRes.data.results.length : 0
    approvedCount.value = approvedRes.data.status === 'success' ? approvedRes.data.results.length : 0
    rejectedCount.value = rejectedRes.data.status === 'success' ? rejectedRes.data.results.length : 0
  } catch (error) {
    console.error('Error fetching stats:', error)
  }
}

// 标签页切换
const handleTabChange = (tabName) => {
  activeTab.value = tabName
  fetchGames(tabName)
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  // 重新计算过滤后的总数
  let filteredResult = games.value
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filteredResult = games.value.filter(game => 
      game.name.toLowerCase().includes(keyword) ||
      game.publisher.toLowerCase().includes(keyword)
    )
  }
  totalGames.value = filteredResult.length
}

// 刷新数据
const refreshData = () => {
  fetchGames(activeTab.value)
  fetchStats()
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

// 查看游戏详情
const viewGame = (game) => {
  selectedGame.value = game
  showViewDialog.value = true
}

// 通过审核
const approveGame = async (game) => {
  try {
    await ElMessageBox.confirm(
      `确定要通过游戏"${game.name}"的审核吗？`,
      '确认通过',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'success',
      }
    )
    
    const response = await axios.put(`http://localhost:5000/games/${game.game_id}/audit`, {
      status: 'approved'
    })
    
    if (response.data.status === 'success') {
      ElMessage.success('审核通过')
      showViewDialog.value = false
      await refreshData()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
      console.error('Error approving game:', error)
    }
  }
}

// 拒绝审核
const rejectGame = (game) => {
  selectedGame.value = game
  rejectForm.reason = ''
  showRejectDialog.value = true
}

// 确认拒绝
const confirmReject = async () => {
  if (!rejectForm.reason.trim()) {
    ElMessage.warning('请输入拒绝原因')
    return
  }
  
  try {
    const response = await axios.put(`http://localhost:5000/games/${selectedGame.value.game_id}/audit`, {
      status: 'rejected',
      reason: rejectForm.reason
    })
    
    if (response.data.status === 'success') {
      ElMessage.success('已拒绝审核')
      showRejectDialog.value = false
      showViewDialog.value = false
      await refreshData()
    }
  } catch (error) {
    ElMessage.error('操作失败')
    console.error('Error rejecting game:', error)
  }
}

// 获取状态类型
const getStatusType = (status) => {
  switch (status) {
    case 'pending': return 'warning'
    case 'approved': return 'success'
    case 'rejected': return 'danger'
    default: return 'info'
  }
}

// 获取状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'pending': return '待审核'
    case 'approved': return '已通过'
    case 'rejected': return '已拒绝'
    default: return '未知'
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchGames('pending')
  fetchStats()
})
</script>

<style scoped>
.game-audit-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  color: #303133;
}

.header-stats {
  display: flex;
  gap: 10px;
}

.filter-section {
  margin-bottom: 20px;
}

.search-bar {
  display: flex;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
}

.game-detail {
  padding: 10px 0;
}

.detail-row {
  display: flex;
  margin-bottom: 15px;
  align-items: flex-start;
}

.detail-row label {
  font-weight: bold;
  width: 100px;
  color: #606266;
  flex-shrink: 0;
}

.detail-row span {
  color: #303133;
}

.description-text {
  max-height: 100px;
  overflow-y: auto;
  line-height: 1.5;
  color: #606266;
}

.tab-badge {
  margin-left: 5px;
}
</style>

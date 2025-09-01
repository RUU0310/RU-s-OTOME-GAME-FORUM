<template>
  <div style="height: 100%; width: 100%;">
    <div v-if="debugMode" style="background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px;">
      <h4>调试信息:</h4>
      <p>用户数量: {{ users.length }}</p>
      <p>最后请求时间: {{ lastRequestTime }}</p>
      <p>最后响应: {{ lastResponse }}</p>
    </div>
    <div style="margin-bottom: 20px;">
      <el-button type="primary" @click="showAddDialog" size="small">添加用户</el-button>
      <el-button @click="refreshData" size="small">刷新数据</el-button>
      <el-button @click="toggleDebug" size="small">{{ debugMode ? '关闭' : '开启' }}调试</el-button>
      <el-button type="warning" @click="showUpgradeRequests" size="small">升级申请 ({{ pendingUpgradeCount }})</el-button>
    </div>
    <el-table
      :data="users.slice((currentPage - 1) * pageSize, currentPage * pageSize)"
      stripe
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column label="用户ID" prop="user_id" width="90"/>
      <el-table-column label="用户名" prop="username" width="110"/>
      <el-table-column label="昵称" prop="nickname" width="100"/>
      <el-table-column label="手机号" prop="phone" width="110"/>
      <el-table-column label="邮箱" prop="email" width="160"/>
      <el-table-column label="头像" width="80">
        <template #default="scope">
          <img v-if="scope.row.avatar" :src="getFullImageUrl(scope.row.avatar)" style="width: 48px; height: 48px; object-fit: cover; border-radius: 50%;" />
          <span v-else>无头像</span>
        </template>
      </el-table-column>
      <el-table-column label="简介" prop="bio" width="180" show-overflow-tooltip/>
      <el-table-column label="角色" prop="role" width="70"/>
      <el-table-column label="升级状态" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.upgrade_status === 'pending'" type="warning" size="small">待审核</el-tag>
          <el-tag v-else-if="scope.row.upgrade_status === 'approved'" type="success" size="small">已通过</el-tag>
          <el-tag v-else-if="scope.row.upgrade_status === 'rejected'" type="danger" size="small">已拒绝</el-tag>
          <el-tag v-else type="info" size="small">无申请</el-tag>
        </template>
      </el-table-column>
      <el-table-column align="right" label="操作" width="200px">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.$index, scope.row)">删除</el-button>
          <el-button 
            v-if="scope.row.upgrade_status === 'pending'" 
            size="small" 
            type="warning" 
            @click="handleReviewUpgrade(scope.row)"
          >
            审核
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination-container">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="users.length"
        layout="total, prev, pager, next, jumper"
        @current-change="handlePageChange"
      />
    </div>
  </div>
  <!-- 添加用户弹窗 -->
  <el-dialog
    title="添加用户"
    v-model="add_dialog_visible"
    width="40%"
    :before-close="handleClose"
  >
    <el-form
      ref="ruleFormRef"
      :model="user_form"
      status-icon
      label-width="120px"
      class="demo-ruleForm"
    >
      <el-form-item label="用户名" prop="username">
        <el-input v-model="user_form.username" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="user_form.password" type="password" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="昵称" prop="nickname">
        <el-input v-model="user_form.nickname" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="手机号" prop="phone">
        <el-input v-model="user_form.phone" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="user_form.email" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="头像" prop="avatar">
        <el-upload
          class="avatar-uploader"
          action="http://localhost:5000/upload"
          :show-file-list="false"
          :on-success="handleUploadSuccess"
          :before-upload="beforeUpload"
          name="file"
          :headers="{}"
        >
          <img v-if="user_form.avatar" :src="user_form.avatar" class="avatar" style="width: 60px; height: 60px; object-fit: cover; border-radius: 50%;" />
          <el-icon v-else><Plus /></el-icon>
        </el-upload>
      </el-form-item>
      <el-form-item label="简介" prop="bio">
        <el-input type="textarea" v-model="user_form.bio" autocomplete="off" :rows="2"/>
      </el-form-item>
      <el-form-item label="角色" prop="role">
        <el-select v-model="user_form.role" placeholder="请选择角色">
          <el-option label="普通用户" value="user"/>
          <el-option label="管理员" value="admin"/>
          <el-option label="发行商" value="publisher"/>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm(ruleFormRef)" :loading="submitting">提交</el-button>
        <el-button @click="resetForm(ruleFormRef)">重置</el-button>
      </el-form-item>
    </el-form>
  </el-dialog>
  <!-- 编辑用户弹窗 -->
  <el-dialog
    title="编辑用户"
    v-model="edit_dialog_visible"
    width="40%"
    :before-close="handleClose"
  >
    <el-form
      ref="editFormRef"
      :model="user_form"
      status-icon
      label-width="120px"
      class="demo-ruleForm"
    >
      <el-form-item label="用户名" prop="username">
        <el-input v-model="user_form.username" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="user_form.password" type="password" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="昵称" prop="nickname">
        <el-input v-model="user_form.nickname" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="手机号" prop="phone">
        <el-input v-model="user_form.phone" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="user_form.email" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="头像" prop="avatar">
        <el-upload
          class="avatar-uploader"
          action="http://localhost:5000/upload"
          :show-file-list="false"
          :on-success="handleUploadSuccess"
          :before-upload="beforeUpload"
          name="file"
          :headers="{}"
        >
          <img v-if="user_form.avatar" :src="user_form.avatar" class="avatar" style="width: 60px; height: 60px; object-fit: cover; border-radius: 50%;" />
          <el-icon v-else><Plus /></el-icon>
        </el-upload>
      </el-form-item>
      <el-form-item label="简介" prop="bio">
        <el-input type="textarea" v-model="user_form.bio" autocomplete="off" :rows="2"/>
      </el-form-item>
      <el-form-item label="角色" prop="role">
        <el-select v-model="user_form.role" placeholder="请选择角色">
          <el-option label="普通用户" value="user"/>
          <el-option label="管理员" value="admin"/>
          <el-option label="发行商" value="publisher"/>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitEditForm(editFormRef)" :loading="submitting">提交</el-button>
        <el-button @click="resetForm(editFormRef)">重置</el-button>
      </el-form-item>
    </el-form>
  </el-dialog>
  
  <!-- 升级申请审核对话框 -->
  <el-dialog
    title="审核升级申请"
    v-model="upgradeReviewDialogVisible"
    width="50%"
    :before-close="handleClose"
  >
    <div v-if="currentUpgradeRequest" class="upgrade-review-content">
      <div class="user-info-section">
        <h4>申请人信息</h4>
        <div class="user-info-grid">
          <div class="info-item">
            <label>用户名：</label>
            <span>{{ currentUpgradeRequest.username }}</span>
          </div>
          <div class="info-item">
            <label>昵称：</label>
            <span>{{ currentUpgradeRequest.nickname }}</span>
          </div>
          <div class="info-item">
            <label>手机号：</label>
            <span>{{ currentUpgradeRequest.phone || '未填写' }}</span>
          </div>
          <div class="info-item">
            <label>邮箱：</label>
            <span>{{ currentUpgradeRequest.email || '未填写' }}</span>
          </div>
          <div class="info-item">
            <label>申请时间：</label>
            <span>{{ formatRequestTime(currentUpgradeRequest.upgrade_request_time) }}</span>
          </div>
        </div>
        <div class="user-bio" v-if="currentUpgradeRequest.bio">
          <label>个人简介：</label>
          <p>{{ currentUpgradeRequest.bio }}</p>
        </div>
      </div>
      
      <div class="review-actions">
        <h4>审核操作</h4>
        <div class="action-buttons">
          <el-button type="success" @click="approveUpgrade" :loading="reviewing">
            <span class="action-icon">✅</span>
            通过申请
          </el-button>
          <el-button type="danger" @click="rejectUpgrade" :loading="reviewing">
            <span class="action-icon">❌</span>
            拒绝申请
          </el-button>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import axios from 'axios'
import {reactive, ref, onMounted} from "vue";
import {ElMessageBox, ElMessage} from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
const API_BASE_URL = 'http://localhost:5000'
const users = reactive([])
const loading = ref(false)
const submitting = ref(false)
const debugMode = ref(false)
const lastRequestTime = ref('')
const lastResponse = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// 升级申请审核相关
const pendingUpgradeCount = ref(0)
const upgradeReviewDialogVisible = ref(false)
const currentUpgradeRequest = ref(null)
const reviewing = ref(false)

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})
api.interceptors.request.use(
  config => {
    lastRequestTime.value = new Date().toLocaleTimeString()
    return config
  },
  error => Promise.reject(error)
)
api.interceptors.response.use(
  response => {
    lastResponse.value = `${response.status} - ${response.data?.message || 'success'}`
    return response
  },
  error => {
    lastResponse.value = `错误: ${error.message}`
    ElMessage.error(`请求失败: ${error.message}`)
    return Promise.reject(error)
  }
)
const getUsers = async () => {
  try {
    loading.value = true
    const res = await api.get('/users')
    if (Array.isArray(res.data)) {
      users.splice(0, users.length)
      users.push(...res.data)
      getPendingUpgradeCount()
      // 新增：同步侧边栏红点
      const hasPending = users.some(user => user.upgrade_status === 'pending')
      window.dispatchEvent(new CustomEvent('set-user-upgrade-pending', { detail: hasPending }))
      ElMessage.success(`获取到 ${users.length} 个用户的数据`)
    } else {
      throw new Error(res.data.message || '获取数据失败')
    }
  } catch (error) {
    ElMessage.error('获取数据失败，请检查后端服务')
  } finally {
    loading.value = false
  }
}
const refreshData = () => { getUsers() }

// 新增：后台管理页面一进入就同步红点
function syncUpgradePendingRedDot() {
  api.get('/users').then(res => {
    if (Array.isArray(res.data)) {
      const hasPending = res.data.some(user => user.upgrade_status === 'pending')
      window.dispatchEvent(new CustomEvent('set-user-upgrade-pending', { detail: hasPending }))
    }
  })
}

onMounted(() => {
  syncUpgradePendingRedDot()
  getUsers()
})

const handleDelete = async (index, scope) => {
  try {
    await ElMessageBox.confirm('确定要删除这个用户吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    const res = await api.delete(`/users/${scope.user_id}`)
    if (res.data.msg === '删除成功') {
      ElMessage.success('删除成功')
      await getUsers()
    } else {
      throw new Error(res.data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}
const add_dialog_visible = ref(false)
const ruleFormRef = ref()
const emptyUserForm = {
  user_id: '',
  username: '',
  password: '',
  nickname: '',
  phone: '',
  email: '',
  avatar: '',
  bio: '',
  role: 'user',
}
const user_form = reactive({ ...emptyUserForm })
const submitForm = async (formEl) => {
  try {
    submitting.value = true
    const res = await api.post('/users', user_form)
    if (res.data.user_id) {
      ElMessage.success('添加成功')
      add_dialog_visible.value = false
      formEl.resetFields()
      await getUsers()
    } else {
      throw new Error(res.data.message || res.data.msg || '添加失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || error.message || '添加失败')
  } finally {
    submitting.value = false
  }
}
const resetForm = (formEl) => {
  Object.assign(user_form, emptyUserForm)
  formEl.resetFields()
}
const handleClose = (done) => {
  ElMessageBox.confirm('确认关闭？')
    .then(() => { done() })
    .catch(() => {})
}
const editFormRef = ref()
const edit_dialog_visible = ref(false)
const handleEdit = (index, scope) => {
  for (let key in user_form) user_form[key] = scope[key]
  edit_dialog_visible.value = true
}
const submitEditForm = async (formEl) => {
  try {
    submitting.value = true
    const res = await api.put(`/users/${user_form.user_id}`, user_form)
    if (res.data.msg === '更新成功') {
      ElMessage.success('修改成功')
      formEl.resetFields()
      edit_dialog_visible.value = false
      await getUsers()
    } else {
      throw new Error(res.data.message || res.data.msg || '修改失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || error.message || '修改失败')
  } finally {
    submitting.value = false
  }
}
const toggleDebug = () => { debugMode.value = !debugMode.value }
const handleUploadSuccess = (response) => {
  if (response.status === 'success') {
    user_form.avatar = 'http://localhost:5000' + response.file_url
    ElMessage.success('头像上传成功')
  } else {
    ElMessage.error(response.message || '头像上传失败')
  }
}
const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}
const handlePageChange = (page) => { currentPage.value = page }
const showAddDialog = () => {
  Object.assign(user_form, emptyUserForm)
  add_dialog_visible.value = true
}
function getFullImageUrl(url) {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return API_BASE_URL + url
}

// 升级申请审核相关函数
const getPendingUpgradeCount = () => {
  pendingUpgradeCount.value = users.filter(user => user.upgrade_status === 'pending').length
}

const showUpgradeRequests = () => {
  const pendingUsers = users.filter(user => user.upgrade_status === 'pending')
  if (pendingUsers.length === 0) {
    ElMessage.info('暂无待审核的升级申请')
    return
  }
  // 显示第一个待审核的申请
  currentUpgradeRequest.value = pendingUsers[0]
  upgradeReviewDialogVisible.value = true
}

const handleReviewUpgrade = (user) => {
  currentUpgradeRequest.value = user
  upgradeReviewDialogVisible.value = true
}

const approveUpgrade = async () => {
  try {
    reviewing.value = true
    const res = await api.post(`/users/${currentUpgradeRequest.value.user_id}/upgrade-review`, {
      action: 'approve'
    })
    if (res.data.status === 'success') {
      ElMessage.success('申请已通过')
      upgradeReviewDialogVisible.value = false
      await getUsers()
      getPendingUpgradeCount()
    } else {
      throw new Error(res.data.message || '审核失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || error.message || '审核失败')
  } finally {
    reviewing.value = false
  }
}

const rejectUpgrade = async () => {
  try {
    reviewing.value = true
    const res = await api.post(`/users/${currentUpgradeRequest.value.user_id}/upgrade-review`, {
      action: 'reject'
    })
    if (res.data.status === 'success') {
      ElMessage.success('申请已拒绝')
      upgradeReviewDialogVisible.value = false
      await getUsers()
      getPendingUpgradeCount()
    } else {
      throw new Error(res.data.message || '审核失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || error.message || '审核失败')
  } finally {
    reviewing.value = false
  }
}

const formatRequestTime = (timeString) => {
  if (!timeString) return '未知时间'
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
</script>

<style scoped>
.el-table { width: 100%; }
.pagination-container { margin-top: 20px; text-align: right; }
.avatar-uploader .avatar { width: 60px; height: 60px; display: block; border-radius: 50%; }

/* 升级申请审核样式 */
.upgrade-review-content {
  padding: 20px 0;
}

.user-info-section {
  margin-bottom: 30px;
}

.user-info-section h4 {
  color: #409eff;
  margin-bottom: 16px;
  font-size: 1.1rem;
  border-bottom: 2px solid #e6f7ff;
  padding-bottom: 8px;
}

.user-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.info-item label {
  font-weight: bold;
  color: #666;
  margin-right: 8px;
  min-width: 80px;
}

.info-item span {
  color: #333;
  flex: 1;
}

.user-bio {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 12px;
  border-left: 3px solid #67c23a;
}

.user-bio label {
  font-weight: bold;
  color: #666;
  display: block;
  margin-bottom: 8px;
}

.user-bio p {
  color: #333;
  margin: 0;
  line-height: 1.5;
}

.review-actions {
  border-top: 1px solid #e9ecef;
  padding-top: 20px;
}

.review-actions h4 {
  color: #e6a23c;
  margin-bottom: 16px;
  font-size: 1.1rem;
}

.action-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.action-buttons .el-button {
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: bold;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.action-buttons .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.action-icon {
  margin-right: 8px;
  font-size: 1.1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-info-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons .el-button {
    width: 100%;
  }
}
</style>

<template>
  <div style="height: 100%; width: 100%;">
    <div style="margin-bottom: 20px;">
      <el-button type="primary" @click="showAddDialog" size="small">添加小组</el-button>
      <el-button @click="refreshData" size="small">刷新数据</el-button>
    </div>
    <el-table
      :data="groups.slice((currentPage - 1) * pageSize, currentPage * pageSize)"
      stripe
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column label="小组ID" prop="group_id" width="80"/>
      <el-table-column label="游戏ID" prop="game_id" width="80"/>
      <el-table-column label="小组名" prop="name" width="180"/>
      <el-table-column label="头像" width="80">
        <template #default="scope">
          <img v-if="scope.row.avatar" :src="getFullImageUrl(scope.row.avatar)" style="width: 48px; height: 48px; object-fit: cover;" />
          <span v-else>无头像</span>
        </template>
      </el-table-column>
      <el-table-column label="简介" prop="description" width="340" show-overflow-tooltip/>
      <el-table-column label="成员数" prop="member_count" width="100"/>
      <el-table-column align="right" label="操作" width="200px">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.$index, scope.row)">删除</el-button>
          <el-button size="small" type="info" @click="showMembers(scope.row.group_id)">成员</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination-container">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="groups.length"
        layout="total, prev, pager, next, jumper"
        @current-change="handlePageChange"
      />
    </div>
  </div>
  <!-- 添加小组弹窗 -->
  <el-dialog
    title="添加小组"
    v-model="add_dialog_visible"
    width="40%"
    :before-close="handleClose"
  >
    <el-form
      ref="ruleFormRef"
      :model="group_form"
      status-icon
      label-width="120px"
      class="demo-ruleForm"
    >
      <el-form-item label="游戏ID" prop="game_id">
        <el-input v-model="group_form.game_id" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="小组名" prop="name">
        <el-input v-model="group_form.name" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="简介" prop="description">
        <el-input type="textarea" v-model="group_form.description" autocomplete="off" :rows="2"/>
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
          <img v-if="group_form.avatar" :src="group_form.avatar" class="avatar" style="width: 48px; height: 48px; object-fit: cover;" />
          <el-icon v-else><Plus /></el-icon>
        </el-upload>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm(ruleFormRef)" :loading="submitting">提交</el-button>
        <el-button @click="resetForm(ruleFormRef)">重置</el-button>
      </el-form-item>
    </el-form>
  </el-dialog>
  <!-- 编辑小组弹窗 -->
  <el-dialog
    title="编辑小组"
    v-model="edit_dialog_visible"
    width="40%"
    :before-close="handleClose"
  >
    <el-form
      ref="editFormRef"
      :model="group_form"
      status-icon
      label-width="120px"
      class="demo-ruleForm"
    >
      <el-form-item label="游戏ID" prop="game_id">
        <el-input v-model="group_form.game_id" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="小组名" prop="name">
        <el-input v-model="group_form.name" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="简介" prop="description">
        <el-input type="textarea" v-model="group_form.description" autocomplete="off" :rows="2"/>
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
          <img v-if="group_form.avatar" :src="group_form.avatar" class="avatar" style="width: 48px; height: 48px; object-fit: cover;" />
          <el-icon v-else><Plus /></el-icon>
        </el-upload>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitEditForm(editFormRef)" :loading="submitting">提交</el-button>
        <el-button @click="resetForm(editFormRef)">重置</el-button>
      </el-form-item>
    </el-form>
  </el-dialog>
  <!-- 小组成员弹窗 -->
  <el-dialog
    title="小组成员"
    v-model="members_dialog_visible"
    width="40%"
  >
    <el-table :data="members" style="width:100%">
      <el-table-column label="用户ID" prop="user_id" width="120"/>
      <el-table-column label="加入时间" prop="joined_at" width="180"/>
    </el-table>
  </el-dialog>
</template>

<script setup>
import axios from 'axios'
import {reactive, ref, onMounted} from "vue";
import {ElMessageBox, ElMessage} from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
const API_BASE_URL = 'http://localhost:5000'
const groups = reactive([])
const loading = ref(false)
const submitting = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})
const getGroups = async () => {
  try {
    loading.value = true
    const res = await api.get('/groups')
    if (Array.isArray(res.data)) {
      groups.splice(0, groups.length)
      groups.push(...res.data)
      ElMessage.success(`获取到 ${groups.length} 个小组的数据`)
    } else {
      throw new Error(res.data.message || '获取数据失败')
    }
  } catch (error) {
    ElMessage.error('获取数据失败，请检查后端服务')
  } finally {
    loading.value = false
  }
}
const refreshData = () => { getGroups() }
onMounted(() => { getGroups() })
const handleDelete = async (index, scope) => {
  try {
    await ElMessageBox.confirm('确定要删除这个小组吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    const res = await api.delete(`/groups/${scope.group_id}`)
    if (res.data.status === 'success') {
      ElMessage.success('删除成功')
      await getGroups()
    } else {
      throw new Error(res.data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}
const add_dialog_visible = ref(false)
const ruleFormRef = ref()
const emptyGroupForm = {
  group_id: '',
  game_id: '',
  name: '',
  description: '',
  avatar: ''
}
const group_form = reactive({ ...emptyGroupForm })
const submitForm = async (formEl) => {
  try {
    submitting.value = true
    const res = await api.post('/groups', group_form)
    if (res.data.group_id) {
      ElMessage.success('添加成功')
      add_dialog_visible.value = false
      formEl.resetFields()
      await getGroups()
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
  Object.assign(group_form, emptyGroupForm)
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
  for (let key in group_form) group_form[key] = scope[key]
  edit_dialog_visible.value = true
}
const submitEditForm = async (formEl) => {
  try {
    submitting.value = true
    const res = await api.put(`/groups/${group_form.group_id}`, group_form)
    if (res.data.status === 'success') {
      ElMessage.success('修改成功')
      formEl.resetFields()
      edit_dialog_visible.value = false
      await getGroups()
    } else {
      throw new Error(res.data.message || res.data.msg || '修改失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || error.message || '修改失败')
  } finally {
    submitting.value = false
  }
}
const handlePageChange = (page) => { currentPage.value = page }
const showAddDialog = () => {
  Object.assign(group_form, emptyGroupForm)
  add_dialog_visible.value = true
}
const members_dialog_visible = ref(false)
const members = ref([])
const showMembers = async (group_id) => {
  const res = await api.get(`/groups/${group_id}/members`)
  members.value = res.data
  members_dialog_visible.value = true
}
function getFullImageUrl(url) {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return API_BASE_URL + url
}
const handleUploadSuccess = (response) => {
  if (response.status === 'success') {
    group_form.avatar = 'http://localhost:5000' + response.file_url
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
</script>

<style scoped>
.el-table { width: 100%; }
.pagination-container { margin-top: 20px; text-align: right; }
</style>

<template>
  <div style="height: 100%; width: 100%;">
    <!-- 调试信息 -->
    <div v-if="debugMode" style="background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px;">
      <h4>调试信息:</h4>
      <p>角色数量: {{ characters.length }}</p>
      <p>最后请求时间: {{ lastRequestTime }}</p>
      <p>最后响应: {{ lastResponse }}</p>
    </div>
    <div style="margin-bottom: 20px; display: flex; align-items: center; gap: 16px;">
      <el-select v-model="game_id" placeholder="请选择游戏" style="width: 220px;">
        <el-option v-for="g in games" :key="g.game_id" :label="g.name" :value="g.game_id" />
      </el-select>
      <el-button type="primary" @click="showAddDialog" size="small">添加角色</el-button>
      <el-button @click="refreshData" size="small">刷新数据</el-button>
      <el-button @click="toggleDebug" size="small">{{ debugMode ? '关闭' : '开启' }}调试</el-button>
    </div>
    <el-table
      :data="characters.slice((currentPage - 1) * pageSize, currentPage * pageSize)"
      stripe
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column label="角色ID" prop="id" width="90"/>
      <el-table-column label="所属游戏" width="120">
        <template #default="scope">
          {{ getGameName(scope.row.game_id) }}
        </template>
      </el-table-column>
      <el-table-column label="角色名" prop="name" width="100"/>
      <el-table-column label="CV" prop="cv" width="90"/>
      <el-table-column label="角色类型" prop="role_type" width="80">
        <template #default="scope">
          {{ scope.row.role_type || '可攻略' }}
        </template>
      </el-table-column>
      <el-table-column label="图片" width="80">
        <template #default="scope">
          <img v-if="scope.row.avatar" :src="getFullImageUrl(scope.row.avatar)" style="width: 48px; height: 48px; object-fit: cover;" />
          <span v-else>无图片</span>
        </template>
      </el-table-column>
      <el-table-column label="简介" prop="description" width="160" show-overflow-tooltip/>
      <el-table-column label="extra_info" width="120">
        <template #default="scope">
          <div v-if="scope.row.extra_info && Object.keys(scope.row.extra_info).length">
            <div v-for="(v, k) in scope.row.extra_info" :key="k">{{ k }}: {{ v }}</div>
          </div>
          <span v-else>无</span>
        </template>
      </el-table-column>
      <el-table-column align="right" label="操作" width="200px">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.$index, scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination-container">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="characters.length"
        layout="total, prev, pager, next, jumper"
        @current-change="handlePageChange"
      />
    </div>
    <!-- 添加角色弹窗 -->
    <el-dialog
      title="添加角色"
      v-model="add_dialog_visible"
      width="40%"
      :before-close="handleClose"
    >
      <el-form
        ref="ruleFormRef"
        :model="character_form"
        status-icon
        label-width="120px"
        class="demo-ruleForm"
      >
        <el-form-item label="角色名" prop="name">
          <el-input v-model="character_form.name" autocomplete="off"/>
        </el-form-item>
        <el-form-item label="CV" prop="cv">
          <el-input v-model="character_form.cv" autocomplete="off"/>
        </el-form-item>
        <el-form-item label="角色类型" prop="role_type">
          <el-select v-model="character_form.role_type" placeholder="请选择类型" style="width: 180px;">
            <el-option label="女主" value="女主" />
            <el-option label="可攻略" value="可攻略" />
            <el-option label="不可攻略" value="不可攻略" />
          </el-select>
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
            <img v-if="character_form.avatar" :src="character_form.avatar" class="avatar" style="width: 60px; height: 60px; object-fit: cover;" />
            <el-icon v-else><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="简介" prop="description">
          <el-input type="textarea" v-model="character_form.description" autocomplete="off" :rows="2"/>
        </el-form-item>
        <el-form-item label="extra_info">
          <div v-for="(item, idx) in extraInfoList" :key="idx" style="display: flex; align-items: center; margin-bottom: 4px;">
            <el-input v-model="item.key" placeholder="键" style="width: 40%; margin-right: 8px;" />
            <el-input v-model="item.value" placeholder="值" style="width: 40%; margin-right: 8px;" />
            <button
              v-if="extraInfoList.length > 1"
              @click.prevent="removeExtraInfo(idx)"
              style="width: 28px; height: 28px; border-radius: 50%; border: 1px solid #dcdfe6; background: #fff; color: #f56c6c; font-size: 18px; margin-right: 4px; cursor: pointer; display: flex; align-items: center; justify-content: center;"
              title="删除"
              type="button"
            >-</button>
            <button
              v-if="idx === extraInfoList.length - 1"
              @click.prevent="addExtraInfo"
              style="width: 28px; height: 28px; border-radius: 50%; border: 1px solid #dcdfe6; background: #fff; color: #409eff; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center;"
              title="添加"
              type="button"
            >+</button>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm(ruleFormRef)" :loading="submitting">提交</el-button>
          <el-button @click="resetForm(ruleFormRef)">重置</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
    <!-- 编辑角色弹窗 -->
    <el-dialog
      title="编辑角色"
      v-model="edit_dialog_visible"
      width="40%"
      :before-close="handleClose"
    >
      <el-form
        ref="editFormRef"
        :model="character_form"
        status-icon
        label-width="120px"
        class="demo-ruleForm"
      >
        <el-form-item label="角色名" prop="name">
          <el-input v-model="character_form.name" autocomplete="off"/>
        </el-form-item>
        <el-form-item label="CV" prop="cv">
          <el-input v-model="character_form.cv" autocomplete="off"/>
        </el-form-item>
        <el-form-item label="角色类型" prop="role_type">
          <el-select v-model="character_form.role_type" placeholder="请选择类型" style="width: 180px;">
            <el-option label="女主" value="女主" />
            <el-option label="可攻略" value="可攻略" />
            <el-option label="不可攻略" value="不可攻略" />
          </el-select>
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
            <img v-if="character_form.avatar" :src="character_form.avatar" class="avatar" style="width: 60px; height: 60px; object-fit: cover;" />
            <el-icon v-else><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="简介" prop="description">
          <el-input type="textarea" v-model="character_form.description" autocomplete="off" :rows="2"/>
        </el-form-item>
        <el-form-item label="extra_info">
          <div v-for="(item, idx) in editExtraInfoList" :key="'edit-' + idx" style="display: flex; align-items: center; margin-bottom: 4px;">
            <el-input v-model="item.key" placeholder="键" style="width: 40%; margin-right: 8px;" />
            <el-input v-model="item.value" placeholder="值" style="width: 40%; margin-right: 8px;" />
            <button
              v-if="editExtraInfoList.length > 1"
              @click.prevent="removeEditExtraInfo(idx)"
              style="width: 28px; height: 28px; border-radius: 50%; border: 1px solid #dcdfe6; background: #fff; color: #f56c6c; font-size: 18px; margin-right: 4px; cursor: pointer; display: flex; align-items: center; justify-content: center;"
              title="删除"
              type="button"
            >-</button>
            <button
              v-if="idx === editExtraInfoList.length - 1"
              @click.prevent="addEditExtraInfo"
              style="width: 28px; height: 28px; border-radius: 50%; border: 1px solid #dcdfe6; background: #fff; color: #409eff; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center;"
              title="添加"
              type="button"
            >+</button>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitEditForm(editFormRef)" :loading="submitting">提交</el-button>
          <el-button @click="resetForm(editFormRef)">重置</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>
<script setup>
import axios from 'axios'
import {reactive, ref, onMounted, watch} from "vue";
import {ElMessageBox, ElMessage} from 'element-plus'
import { Plus, Minus } from '@element-plus/icons-vue'

const API_BASE_URL = 'http://localhost:5000'
const game_id = ref(1) // TODO: 可根据实际业务选择游戏ID
const characters = reactive([])
const loading = ref(false)
const submitting = ref(false)
const debugMode = ref(false)
const lastRequestTime = ref('')
const lastResponse = ref('')
const currentPage = ref(1)
const pageSize = ref(3)
const games = reactive([])
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
const getCharacters = async () => {
  try {
    loading.value = true
    const res = await api.get(`/games/${game_id.value}/characters`)
    if (res.data.status === 'success') {
      characters.splice(0, characters.length)
      characters.push(...res.data.results)
      ElMessage.success(`获取到 ${characters.length} 个角色的数据`)
    } else {
      throw new Error(res.data.message || '获取数据失败')
    }
  } catch (error) {
    ElMessage.error('获取数据失败，请检查后端服务')
  } finally {
    loading.value = false
  }
}
const refreshData = () => { getCharacters() }
const getGames = async () => {
  try {
    const res = await api.get('/games')
    if (res.data.status === 'success') {
      games.splice(0, games.length)
      games.push(...res.data.results)
      if (games.length && !game_id.value) game_id.value = games[0].game_id
    }
  } catch {}
}
onMounted(() => {
  getGames()
  // getCharacters() 移到watch
})
watch(game_id, (val, oldVal) => {
  if (val && val !== oldVal) getCharacters()
})
const handleDelete = async (index, scope) => {
  try {
    await ElMessageBox.confirm('确定要删除这个角色吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    const res = await api.delete(`/characters/${scope.id}`)
    if (res.data.status === 'success') {
      ElMessage.success('删除成功')
      await getCharacters()
    } else {
      throw new Error(res.data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}
const add_dialog_visible = ref(false)
const ruleFormRef = ref()
const emptyCharacterForm = {
  name: '',
  cv: '',
  avatar: '',
  description: '',
  extra_info: {},
  id: '',
  role_type: '可攻略',
}
const character_form = reactive({ ...emptyCharacterForm })
const extraInfoList = ref([{ key: '', value: '' }])
const submitForm = async (formEl) => {
  try {
    submitting.value = true
    character_form.extra_info = listToObj(extraInfoList.value)
    const res = await api.post(`/games/${game_id.value}/characters`, character_form)
    if (res.data.status === 'success') {
      ElMessage.success('添加成功')
      add_dialog_visible.value = false
      formEl.resetFields()
      await getCharacters()
    } else {
      throw new Error(res.data.message || '添加失败')
    }
  } catch (error) {
    ElMessage.error('添加失败')
  } finally {
    submitting.value = false
  }
}
const resetForm = (formEl) => {
  Object.assign(character_form, emptyCharacterForm)
  extraInfoList.value = [{ key: '', value: '' }]
  formEl.resetFields()
}
const handleClose = (done) => {
  ElMessageBox.confirm('确认关闭？')
    .then(() => { done() })
    .catch(() => {})
}
const editExtraInfoList = ref([{ key: '', value: '' }])
const edit_dialog_visible = ref(false)
const handleEdit = (index, scope) => {
  for (let key in character_form) character_form[key] = scope[key]
  editExtraInfoList.value = objToList(scope.extra_info)
  if (editExtraInfoList.value.length === 0) editExtraInfoList.value = [{ key: '', value: '' }]
  edit_dialog_visible.value = true
}
function addEditExtraInfo() {
  editExtraInfoList.value.push({ key: '', value: '' })
}
function removeEditExtraInfo(idx) {
  if (editExtraInfoList.value.length > 1) {
    editExtraInfoList.value.splice(idx, 1)
  }
}
const submitEditForm = async (formEl) => {
  try {
    submitting.value = true
    character_form.extra_info = listToObj(editExtraInfoList.value)
    const res = await api.put(`/characters/${character_form.id}`, character_form)
    if (res.data.status === 'success') {
      ElMessage.success('修改成功')
      if (formEl && formEl.resetFields) formEl.resetFields()
      edit_dialog_visible.value = false
      await getCharacters()
    } else {
      throw new Error(res.data.message || '修改失败')
    }
  } catch (error) {
    if (!error.message?.includes('修改成功')) {
      ElMessage.error(error.message || '修改失败')
    }
  } finally {
    submitting.value = false
  }
}
const toggleDebug = () => { debugMode.value = !debugMode.value }
const handleUploadSuccess = (response) => {
  if (response.status === 'success') {
    character_form.avatar = 'http://localhost:5000' + response.file_url
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
  Object.assign(character_form, emptyCharacterForm)
  extraInfoList.value = [{ key: '', value: '' }]
  add_dialog_visible.value = true
}
function getFullImageUrl(url) {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return API_BASE_URL + url
}
function addExtraInfo() {
  extraInfoList.value.push({ key: '', value: '' })
}
function removeExtraInfo(idx) {
  if (extraInfoList.value.length > 1) {
    extraInfoList.value.splice(idx, 1)
  }
}
function listToObj(list) {
  const obj = {}
  list.forEach(item => {
    if (item.key) obj[item.key] = item.value
  })
  return obj
}
function objToList(obj) {
  if (!obj) return []
  return Object.entries(obj).map(([key, value]) => ({ key, value }))
}
function getGameName(game_id) {
  const g = games.find(g => g.game_id === game_id)
  return g ? g.name : '未知'
}
</script>
<style scoped>
.el-table { width: 100%; }
.pagination-container { margin-top: 20px; text-align: right; }
.avatar-uploader .avatar { width: 60px; height: 60px; display: block; }
</style>

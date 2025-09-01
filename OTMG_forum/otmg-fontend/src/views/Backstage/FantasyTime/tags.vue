<template>
  <div style="height: 100%; width: 100%;">
    <div v-if="debugMode" style="background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px;">
      <h4>调试信息:</h4>
      <p>标签数量: {{ tags.length }}</p>
      <p>最后请求时间: {{ lastRequestTime }}</p>
      <p>最后响应: {{ lastResponse }}</p>
    </div>
    <div style="margin-bottom: 20px;">
      <el-button type="primary" @click="showAddDialog" size="small">添加标签</el-button>
      <el-button @click="refreshData" size="small">刷新数据</el-button>
      <el-button @click="toggleDebug" size="small">{{ debugMode ? '关闭' : '开启' }}调试</el-button>
    </div>
    <el-table :data="tags.slice((currentPage - 1) * pageSize, currentPage * pageSize)" stripe style="width: 100%" v-loading="loading">
      <el-table-column label="标签ID" prop="id" width="80"/>
      <el-table-column label="标签名" prop="name" width="120"/>
      <el-table-column label="类型" prop="type" width="100"/>
      <el-table-column label="分类" prop="category" width="100"/>
      <el-table-column label="可选项" prop="options" width="180" show-overflow-tooltip/>
      <el-table-column label="多选" width="60">
        <template #default="scope">
          <el-switch v-model="scope.row.is_multiple" disabled />
        </template>
      </el-table-column>
      <el-table-column label="描述" prop="description" width="160" show-overflow-tooltip/>
      <el-table-column label="启用" width="60">
        <template #default="scope">
          <el-switch v-model="scope.row.is_active" disabled />
        </template>
      </el-table-column>
      <el-table-column align="right" label="操作" width="160px">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.$index, scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination-container">
      <el-pagination :current-page="currentPage" :page-size="pageSize" :total="tags.length" layout="total, prev, pager, next, jumper" @current-change="handlePageChange" />
    </div>
  </div>
  <!-- 添加标签弹窗 -->
  <el-dialog title="添加标签" v-model="add_dialog_visible" width="40%" :before-close="handleClose">
    <el-form ref="ruleFormRef" :model="tag_form" status-icon label-width="120px" class="demo-ruleForm">
      <el-form-item label="标签名" prop="name">
        <el-input v-model="tag_form.name" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="类型" prop="type">
        <el-select v-model="tag_form.type" placeholder="请选择类型" @change="onTypeChange">
          <el-option label="外貌" value="appearance" />
          <el-option label="性格" value="personality" />
        </el-select>
      </el-form-item>
      <el-form-item label="分类" prop="category">
        <el-input v-model="tag_form.category" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="可选项" prop="options">
        <el-input v-model="tag_form.options" autocomplete="off" placeholder="用逗号分隔"/>
      </el-form-item>
      <el-form-item label="多选" prop="is_multiple">
        <el-switch v-model="tag_form.is_multiple"/>
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input v-model="tag_form.description" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="启用" prop="is_active">
        <el-switch v-model="tag_form.is_active"/>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm(ruleFormRef)" :loading="submitting">提交</el-button>
        <el-button @click="resetForm(ruleFormRef)">重置</el-button>
      </el-form-item>
    </el-form>
  </el-dialog>
  <!-- 编辑标签弹窗 -->
  <el-dialog title="编辑标签" v-model="edit_dialog_visible" width="40%" :before-close="handleClose">
    <el-form ref="editFormRef" :model="tag_form" status-icon label-width="120px" class="demo-ruleForm">
      <el-form-item label="标签名" prop="name">
        <el-input v-model="tag_form.name" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="类型" prop="type">
        <el-select v-model="tag_form.type" placeholder="请选择类型" @change="onTypeChange">
          <el-option label="外貌" value="appearance" />
          <el-option label="性格" value="personality" />
        </el-select>
      </el-form-item>
      <el-form-item label="分类" prop="category">
        <el-input v-model="tag_form.category" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="可选项" prop="options">
        <el-input v-model="tag_form.options" autocomplete="off" placeholder="用逗号分隔"/>
      </el-form-item>
      <el-form-item label="多选" prop="is_multiple">
        <el-switch v-model="tag_form.is_multiple"/>
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input v-model="tag_form.description" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="启用" prop="is_active">
        <el-switch v-model="tag_form.is_active"/>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitEditForm(editFormRef)" :loading="submitting">提交</el-button>
        <el-button @click="resetForm(editFormRef)">重置</el-button>
      </el-form-item>
    </el-form>
  </el-dialog>
</template>

<script setup>
import axios from 'axios'
import {reactive, ref, onMounted} from "vue";
import {ElMessageBox, ElMessage} from 'element-plus'
const API_BASE_URL = 'http://localhost:5000'
const tags = reactive([])
const loading = ref(false)
const submitting = ref(false)
const debugMode = ref(false)
const lastRequestTime = ref('')
const lastResponse = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
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
const getTags = async () => {
  try {
    loading.value = true
    const res = await api.get('/api/tags')
    if (res.data.status === 'success') {
      tags.splice(0, tags.length)
      tags.push(...res.data.results)
      ElMessage.success(`获取到 ${tags.length} 个标签的数据`)
    } else {
      throw new Error(res.data.message || '获取数据失败')
    }
  } catch (error) {
    ElMessage.error('获取数据失败，请检查后端服务')
  } finally {
    loading.value = false
  }
}
const refreshData = () => { getTags() }
onMounted(() => { getTags() })
const handleDelete = async (index, scope) => {
  try {
    await ElMessageBox.confirm('确定要删除这个标签吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await api.delete(`/api/tags/${scope.id}`)
    ElMessage.success('删除成功')
    await getTags()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}
const add_dialog_visible = ref(false)
const ruleFormRef = ref()
const emptyTagForm = {
  id: '',
  name: '',
  type: '',
  category: '',
  options: '',
  is_multiple: false,
  description: '',
  is_active: true,
}
const tag_form = reactive({ ...emptyTagForm })
const submitForm = async (formEl) => {
  try {
    submitting.value = true
    const res = await api.post('/api/tags', tag_form)
    if (res.data.status === 'success') {
      ElMessage.success('添加成功')
      add_dialog_visible.value = false
      formEl.resetFields()
      await getTags()
    } else {
      throw new Error(res.data.message || '添加失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || error.message || '添加失败')
  } finally {
    submitting.value = false
  }
}
const resetForm = (formEl) => {
  Object.assign(tag_form, emptyTagForm)
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
  for (let key in tag_form) tag_form[key] = scope[key]
  edit_dialog_visible.value = true
}
const submitEditForm = async (formEl) => {
  try {
    submitting.value = true
    const res = await api.put(`/api/tags/${tag_form.id}`, tag_form)
    if (res.data.status === 'success') {
      ElMessage.success('修改成功')
      formEl.resetFields()
      edit_dialog_visible.value = false
      await getTags()
    } else {
      throw new Error(res.data.message || '修改失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || error.message || '修改失败')
  } finally {
    submitting.value = false
  }
}
const toggleDebug = () => { debugMode.value = !debugMode.value }
const handlePageChange = (page) => { currentPage.value = page }
const showAddDialog = () => {
  Object.assign(tag_form, emptyTagForm)
  add_dialog_visible.value = true
}
function onTypeChange(val) {
  if (val === 'appearance') tag_form.category = '外貌'
  else if (val === 'personality') tag_form.category = '性格'
  else tag_form.category = ''
}
</script>

<style scoped>
.el-table { width: 100%; }
.pagination-container { margin-top: 20px; text-align: right; }
</style> 
<template>
  <div style="height: 100%; width: 100%;">
    <div v-if="debugMode" style="background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px;">
      <h4>调试信息:</h4>
      <p>角色标签数量: {{ characterTags.length }}</p>
      <p>最后请求时间: {{ lastRequestTime }}</p>
      <p>最后响应: {{ lastResponse }}</p>
    </div>
    <div style="margin-bottom: 20px;">
      <el-button type="primary" @click="showAddDialog" size="small">添加角色标签</el-button>
      <el-button @click="refreshData" size="small">刷新数据</el-button>
      <el-button @click="toggleDebug" size="small">{{ debugMode ? '关闭' : '开启' }}调试</el-button>
    </div>
    <el-table :data="characterTags.slice((currentPage - 1) * pageSize, currentPage * pageSize)" stripe style="width: 100%" v-loading="loading">
      <el-table-column label="ID" prop="id" width="80"/>
      <el-table-column label="角色ID" prop="character_id" width="90"/>
      <el-table-column label="角色名" width="120">
        <template #default="scope">
          {{ scope.row.character?.name || '' }}
        </template>
      </el-table-column>
      <el-table-column label="标签名" width="120">
        <template #default="scope">
          {{ scope.row.tag?.name || '' }}
        </template>
      </el-table-column>
      <el-table-column label="标签值" prop="value" width="120"/>
      <el-table-column align="right" label="操作" width="160px">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.$index, scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination-container">
      <el-pagination :current-page="currentPage" :page-size="pageSize" :total="characterTags.length" layout="total, prev, pager, next, jumper" @current-change="handlePageChange" />
    </div>
  </div>
  <!-- 添加角色标签弹窗（批量模式） -->
  <el-dialog title="批量添加角色标签" v-model="add_dialog_visible" width="40%" :before-close="handleClose">
    <el-form ref="ruleFormRef" :model="ct_form" status-icon label-width="120px" class="demo-ruleForm">
      <el-form-item label="游戏" prop="game_id">
        <el-select
          v-model="selectedGameId"
          filterable
          remote
          reserve-keyword
          placeholder="输入游戏名搜索"
          :remote-method="searchGames"
          :loading="gameLoading"
          style="width: 100%"
        >
          <el-option
            v-for="g in gameOptions"
            :key="g.game_id"
            :label="g.name"
            :value="g.game_id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="角色" prop="character_id">
        <el-select
          v-model="ct_form.character_id"
          filterable
          placeholder="请选择角色"
          :disabled="!selectedGameId"
        >
          <el-option
            v-for="item in characterOptions"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
      </el-form-item>
      <template v-for="tag in tagOptions" :key="tag.id">
        <el-form-item :label="tag.name">
          <el-select
            v-model="batchTagValues[tag.id]"
            :multiple="tag.is_multiple"
            filterable
            :placeholder="`请选择${tag.name}`"
            :disabled="!ct_form.character_id || !tag.options"
          >
            <el-option
              v-for="opt in (tag.options ? tag.options.split(',') : [])"
              :key="opt"
              :label="opt"
              :value="opt"
            />
          </el-select>
        </el-form-item>
      </template>
      <el-form-item>
        <el-button type="primary" @click="submitBatchTags" :loading="submitting">提交</el-button>
        <el-button @click="resetForm(ruleFormRef.value)">重置</el-button>
      </el-form-item>
    </el-form>
  </el-dialog>
  <!-- 编辑角色标签弹窗 -->
  <el-dialog title="编辑角色标签" v-model="edit_dialog_visible" width="40%" :before-close="handleClose">
    <el-form ref="editFormRef" :model="ct_form" status-icon label-width="120px" class="demo-ruleForm">
      <el-form-item label="游戏" prop="game_id">
        <el-select
          v-model="selectedGameId"
          filterable
          remote
          reserve-keyword
          placeholder="输入游戏名搜索"
          :remote-method="searchGames"
          :loading="gameLoading"
          style="width: 100%"
        >
          <el-option
            v-for="g in gameOptions"
            :key="g.game_id"
            :label="g.name"
            :value="g.game_id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="角色" prop="character_id">
        <el-select
          v-model="ct_form.character_id"
          filterable
          placeholder="请选择角色"
          :disabled="!selectedGameId"
        >
          <el-option
            v-for="item in characterOptions"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="标签" prop="tag_id">
        <el-select v-model="ct_form.tag_id" placeholder="请选择标签" @change="onTagChange" disabled>
          <el-option
            v-for="tag in tagOptions"
            :key="tag.id"
            :label="tag.name"
            :value="tag.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="标签值" prop="value">
        <el-select
          v-if="selectedTag && tagOptionList.length && selectedTag.is_multiple"
          v-model="ct_form.value"
          multiple
          filterable
          placeholder="请选择标签值"
        >
          <el-option
            v-for="opt in tagOptionList"
            :key="opt"
            :label="opt"
            :value="opt"
          />
        </el-select>
        <el-select
          v-else-if="selectedTag && tagOptionList.length"
          v-model="ct_form.value"
          filterable
          placeholder="请选择标签值"
        >
          <el-option
            v-for="opt in tagOptionList"
            :key="opt"
            :label="opt"
            :value="opt"
          />
        </el-select>
        <el-input v-else v-model="ct_form.value" placeholder="请输入标签值" disabled/>
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
import {reactive, ref, onMounted, watch} from "vue";
import {ElMessageBox, ElMessage} from 'element-plus'
const API_BASE_URL = 'http://localhost:5000'
const characterTags = reactive([])
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
const getCharacterTags = async () => {
  try {
    loading.value = true
    const res = await api.get('/api/character-tags')
    if (res.data.status === 'success') {
      characterTags.splice(0, characterTags.length)
      characterTags.push(...res.data.results)
      ElMessage.success(`获取到 ${characterTags.length} 个角色标签的数据`)
    } else {
      throw new Error(res.data.message || '获取数据失败')
    }
  } catch (error) {
    ElMessage.error('获取数据失败，请检查后端服务')
  } finally {
    loading.value = false
  }
}
const refreshData = () => { getCharacterTags() }
onMounted(() => { getCharacterTags() })
const handleDelete = async (index, scope) => {
  try {
    await ElMessageBox.confirm('确定要删除这个角色标签吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await api.delete(`/api/character-tags/${scope.id}`)
    ElMessage.success('删除成功')
    await getCharacterTags()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}
const add_dialog_visible = ref(false)
const ruleFormRef = ref()
const emptyCTForm = {
  id: '',
  character_id: '',
  tag_id: '',
  value: '',
}
const ct_form = reactive({ ...emptyCTForm })
const batchTagValues = reactive({})
const submitBatchTags = async () => {
  try {
    submitting.value = true
    const records = []
    for (const tag of tagOptions.value) {
      const val = batchTagValues[tag.id]
      if (val && val.length > 0) {
        records.push({
          character_id: ct_form.character_id,
          tag_id: tag.id,
          value: Array.isArray(val) ? val.join(',') : val
        })
      }
    }
    if (!ct_form.character_id || records.length === 0) {
      ElMessage.warning('请选择角色并至少选择一个标签值')
      submitting.value = false
      return
    }
    const res = await api.post('/api/character-tags/batch', { records })
    if (res.data.status === 'success') {
      ElMessage.success('批量添加成功')
      add_dialog_visible.value = false
      resetForm(ruleFormRef.value)
      await getCharacterTags()
    } else {
      throw new Error(res.data.message || '批量添加失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || error.message || '批量添加失败')
  } finally {
    submitting.value = false
  }
}
const resetForm = (formEl) => {
  Object.assign(ct_form, emptyCTForm)
  for (const key in batchTagValues) batchTagValues[key] = undefined
  if (formEl && typeof formEl.resetFields === 'function') {
    formEl.resetFields()
  }
}
const handleClose = (done) => {
  ElMessageBox.confirm('确认关闭？')
    .then(() => { done() })
    .catch(() => {})
}
const editFormRef = ref()
const edit_dialog_visible = ref(false)
const handleEdit = (index, scope) => {
  for (let key in ct_form) ct_form[key] = scope[key]
  const tag = tagOptions.value.find(t => t.id === scope.tag_id)
  if (tag && tag.is_multiple && typeof ct_form.value === 'string') {
    ct_form.value = ct_form.value.split(',')
  }
  edit_dialog_visible.value = true
}
const submitEditForm = async (formEl) => {
  try {
    submitting.value = true
    const res = await api.put(`/api/character-tags/${ct_form.id}`, ct_form)
    if (res.data.status === 'success') {
      ElMessage.success('修改成功')
      formEl.resetFields()
      edit_dialog_visible.value = false
      await getCharacterTags()
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
  Object.assign(ct_form, emptyCTForm)
  add_dialog_visible.value = true
}
const tagOptions = ref([])
const characterOptions = ref([])
const characterLoading = ref(false)
const selectedTag = ref(null)
const tagOptionList = ref([])
const gameOptions = ref([])
const selectedGameId = ref('')
const gameLoading = ref(false)

const getTags = async () => {
  const res = await api.get('/api/tags')
  if (res.data.status === 'success') tagOptions.value = res.data.results
}

const searchGames = async (query) => {
  gameLoading.value = true
  const res = await api.get('/games')
  if (res.data.status === 'success') {
    gameOptions.value = res.data.results.filter(g => g.name.includes(query))
  }
  gameLoading.value = false
}

watch(selectedGameId, async (val) => {
  if (!val) {
    characterOptions.value = []
    return
  }
  characterLoading.value = true
  const res = await api.get(`/games/${val}/characters`)
  if (res.data.status === 'success') {
    characterOptions.value = res.data.results.filter(c => {
      if (c.role_type !== '可攻略') return false
      if (!ct_form.tag_id) return true
      return !characterTags.some(t => t.character_id === c.id && t.tag_id === ct_form.tag_id)
    })
  }
  characterLoading.value = false
})

const onTagChange = (tagId) => {
  selectedTag.value = tagOptions.value.find(t => t.id === tagId)
  tagOptionList.value = selectedTag.value?.options?.split(',') || []
  // 清空标签值
  ct_form.value = selectedTag.value?.is_multiple ? [] : ''
}

// 标签变化时自动联动标签值（新建和编辑都能用）
watch(() => ct_form.tag_id, (tagId) => {
  onTagChange(tagId)
})

onMounted(() => {
  getCharacterTags()
  getTags()
})
</script>

<style scoped>
.el-table { width: 100%; }
.pagination-container { margin-top: 20px; text-align: right; }
</style> 
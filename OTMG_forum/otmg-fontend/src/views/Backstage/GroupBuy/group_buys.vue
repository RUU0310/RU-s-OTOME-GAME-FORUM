<template>
  <div style="height: 100%; width: 100%;">
    <div style="margin-bottom: 20px;">
      <el-button type="primary" @click="showAddDialog" size="small">添加拼团</el-button>
      <el-button @click="refreshData" size="small">刷新数据</el-button>
    </div>
    <el-table
      :data="groupBuys.slice((currentPage - 1) * pageSize, currentPage * pageSize)"
      stripe
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column label="拼团ID" prop="group_buy_id" width="80"/>
      <el-table-column label="标题" prop="title" width="180"/>
      <el-table-column label="商品" width="180">
        <template #default="scope">
          <span v-if="scope.row.product">{{ scope.row.product.name }}</span>
          <span v-else>无</span>
        </template>
      </el-table-column>
      <el-table-column label="团长" width="120">
        <template #default="scope">
          <span v-if="scope.row.leader">{{ scope.row.leader.nickname || scope.row.leader.username }}</span>
          <span v-else>无</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" prop="status" width="100"/>
      <el-table-column label="截止时间" prop="deadline" width="160"/>
      <el-table-column label="成员数" prop="member_count" width="100"/>
      <el-table-column align="right" label="操作" width="180px">
        <template #default="scope">
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination-container">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="groupBuys.length"
        layout="total, prev, pager, next, jumper"
        @current-change="handlePageChange"
      />
    </div>
    <!-- 添加拼团弹窗 -->
    <el-dialog
      title="添加拼团"
      v-model="addDialogVisible"
      width="40%"
      :before-close="handleClose"
    >
      <el-form
        ref="addFormRef"
        :model="addForm"
        status-icon
        label-width="120px"
        class="demo-ruleForm"
      >
        <el-form-item label="商品ID" prop="product_id">
          <el-input v-model="addForm.product_id" autocomplete="off"/>
        </el-form-item>
        <el-form-item label="团长ID" prop="leader_id">
          <el-input v-model="addForm.leader_id" autocomplete="off"/>
        </el-form-item>
        <el-form-item label="标题" prop="title">
          <el-input v-model="addForm.title" autocomplete="off"/>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input type="textarea" v-model="addForm.description" autocomplete="off" :rows="2"/>
        </el-form-item>
        <el-form-item label="联系方式" prop="contact_info">
          <el-input v-model="addForm.contact_info" autocomplete="off"/>
        </el-form-item>
        <el-form-item label="均价" prop="average_price">
          <el-input v-model="addForm.average_price" autocomplete="off"/>
        </el-form-item>
        <el-form-item label="截止时间" prop="deadline">
          <el-date-picker v-model="addForm.deadline" type="datetime" placeholder="选择日期时间" style="width: 100%;" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitAddForm(addFormRef)" :loading="submitting">提交</el-button>
          <el-button @click="resetAddForm(addFormRef)">重置</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
import axios from 'axios'
import {reactive, ref, onMounted} from "vue";
import {ElMessageBox, ElMessage} from 'element-plus'
const API_BASE_URL = 'http://localhost:5000'
const groupBuys = reactive([])
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
const getGroupBuys = async () => {
  try {
    loading.value = true
    const res = await api.get('/api/group-buy/group-buys')
    if (res.data.success && Array.isArray(res.data.data)) {
      groupBuys.splice(0, groupBuys.length)
      groupBuys.push(...res.data.data)
      ElMessage.success(`获取到 ${groupBuys.length} 个拼团数据`)
    } else {
      throw new Error(res.data.message || '获取数据失败')
    }
  } catch (error) {
    ElMessage.error('获取数据失败，请检查后端服务')
  } finally {
    loading.value = false
  }
}
const refreshData = () => { getGroupBuys() }
onMounted(() => { getGroupBuys() })
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个拼团吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    const res = await api.delete(`/api/group-buy/group-buys/${row.group_buy_id}`)
    if (res.data.success) {
      ElMessage.success('删除成功')
      await getGroupBuys()
    } else {
      throw new Error(res.data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}
const addDialogVisible = ref(false)
const addFormRef = ref()
const emptyAddForm = {
  product_id: '',
  leader_id: '',
  title: '',
  description: '',
  contact_info: '',
  average_price: '',
  deadline: ''
}
const addForm = reactive({ ...emptyAddForm })
const submitAddForm = async (formEl) => {
  try {
    submitting.value = true
    // 转换截止时间为ISO字符串
    const payload = { ...addForm }
    if (payload.deadline) {
      payload.deadline = new Date(payload.deadline).toISOString()
    }
    const res = await api.post('/api/group-buy/group-buys', payload)
    if (res.data.success) {
      ElMessage.success('添加成功')
      addDialogVisible.value = false
      resetAddForm(formEl)
      await getGroupBuys()
    } else {
      throw new Error(res.data.message || res.data.msg || '添加失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || error.message || '添加失败')
  } finally {
    submitting.value = false
  }
}
const resetAddForm = (formEl) => {
  Object.assign(addForm, emptyAddForm)
  formEl?.resetFields && formEl.resetFields()
}
const handleClose = (done) => {
  ElMessageBox.confirm('确认关闭？')
    .then(() => { done() })
    .catch(() => {})
}
const handlePageChange = (page) => { currentPage.value = page }
const showAddDialog = () => {
  Object.assign(addForm, emptyAddForm)
  addDialogVisible.value = true
}
</script>

<style scoped>
.el-table { width: 100%; }
.pagination-container { margin-top: 20px; text-align: right; }
</style> 
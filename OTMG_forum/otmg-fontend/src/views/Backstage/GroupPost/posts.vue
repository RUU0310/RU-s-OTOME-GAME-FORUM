<template>
  <div style="height: 100%; width: 100%;">
    <div style="margin-bottom: 20px;">
      <el-button @click="refreshData" size="small">刷新数据</el-button>
    </div>
    <el-table
      :data="posts.slice((currentPage - 1) * pageSize, currentPage * pageSize)"
      stripe
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column label="帖子ID" prop="post_id" width="90"/>
      <el-table-column label="小组ID" prop="group_id" width="90"/>
      <el-table-column label="所属小组" prop="group_name" width="160">
        <template #default="scope">
          {{ scope.row.group_name || '' }}
        </template>
      </el-table-column>
      <el-table-column label="标题" prop="title" width="180"/>
      <el-table-column label="作者" width="120">
        <template #default="scope">
          {{ scope.row.nickname || scope.row.username || scope.row.user_id }}
        </template>
      </el-table-column>
      <el-table-column label="分类" prop="category_name" width="100"/>
      <el-table-column label="创建时间" prop="created_at" width="160"/>
      <el-table-column label="点赞数" prop="like_count" width="80"/>
      <el-table-column label="操作" align="right" width="120px">
        <template #default="scope">
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination-container">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="posts.length"
        layout="total, prev, pager, next, jumper"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import {reactive, ref, onMounted} from "vue";
import {ElMessageBox, ElMessage} from 'element-plus'
const API_BASE_URL = 'http://localhost:5000'
const posts = reactive([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})
const getAllPosts = async () => {
  try {
    loading.value = true
    // 获取所有小组
    const groupsRes = await api.get('/groups')
    if (!Array.isArray(groupsRes.data)) throw new Error('获取小组失败')
    const allPosts = []
    // 并发获取每个小组的帖子
    await Promise.all(groupsRes.data.map(async (g) => {
      const res = await api.get(`/groups/${g.group_id}/posts`)
      if (Array.isArray(res.data)) {
        allPosts.push(...res.data)
      }
    }))
    posts.splice(0, posts.length)
    posts.push(...allPosts)
    ElMessage.success(`获取到 ${posts.length} 个帖子`)
  } catch (error) {
    ElMessage.error('获取帖子失败，请检查后端服务')
  } finally {
    loading.value = false
  }
}
const refreshData = () => { getAllPosts() }
onMounted(() => { getAllPosts() })
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个帖子吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    const res = await api.delete(`/posts/${row.post_id}`)
    if (res.data.status === 'success') {
      ElMessage.success('删除成功')
      await getAllPosts()
    } else {
      throw new Error(res.data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}
const handlePageChange = (page) => { currentPage.value = page }
</script>

<style scoped>
.el-table { width: 100%; }
.pagination-container { margin-top: 20px; text-align: right; }
</style> 
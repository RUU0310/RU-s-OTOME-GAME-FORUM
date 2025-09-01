<template>
    <div style="height: 100%; width: 100%;">
  
      <!-- 调试信息 -->
      <div v-if="debugMode" style="background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px;">
        <h4>调试信息:</h4>
        <p>游戏数量: {{ games.length }}</p>
        <p>最后请求时间: {{ lastRequestTime }}</p>
        <p>最后响应: {{ lastResponse }}</p>
      </div>
  
      <div style="margin-bottom: 20px;">
        <el-button type="primary" @click="showAddDialog" size="small">添加游戏</el-button>
        <el-button @click="refreshData" size="small">刷新数据</el-button>
        <el-button @click="toggleDebug" size="small">{{ debugMode ? '关闭' : '开启' }}调试</el-button>
      </div>
  
      <!-- 数据表格 -->
      <el-table
        :data="games.slice((currentPage - 1) * pageSize, currentPage * pageSize)"
        stripe
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column label="游戏ID" prop="game_id" width="90"/>
        <el-table-column label="游戏名称" prop="name" width="130"/>
        <el-table-column label="封面图" width="100">
          <template #default="scope">
            <img v-if="scope.row.image_url" :src="getFullImageUrl(scope.row.image_url)" style="width: 70px; height: 50px; object-fit: cover;" />
            <span v-else>无图片</span>
          </template>
        </el-table-column>
        <el-table-column label="游戏简介" prop="description" width="220" show-overflow-tooltip/>
        <el-table-column label="地区" prop="region" width="70"/>
        <el-table-column label="发行公司" prop="publisher" width="100"/>
        <el-table-column label="发行日期" prop="release_date" width="100"/>
        <el-table-column label="购买链接" width="90">
          <template #default="scope">
            <el-link v-if="scope.row.purchase_link" :href="scope.row.purchase_link" target="_blank" type="primary">购买</el-link>
            <span v-else>无链接</span>
          </template>
        </el-table-column>
        <el-table-column align="right" label="操作" width="250px">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.$index, scope.row)">
              编辑
            </el-button>
            <el-button
                size="small"
                type="danger"
                @click="handleDelete(scope.$index, scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
  
      <!-- 分页器 -->
      <div class="pagination-container">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :total="games.length"
          layout="total, prev, pager, next, jumper"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  
    <!-- 添加游戏页面 -->
    <el-dialog
        title="添加游戏"
        v-model="add_dialog_visible"
        width="40%"
        :before-close="handleClose"
    >
      <el-form
          ref="ruleFormRef"
          :model="game_form"
          status-icon
          label-width="120px"
          class="demo-ruleForm"
      >
        <el-form-item label="游戏名称" prop="name">
          <el-input v-model="game_form.name" autocomplete="off"/>
        </el-form-item>
        <el-form-item label="封面图" prop="image_url">
          <el-upload
            class="avatar-uploader"
            action="http://localhost:5000/upload"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :before-upload="beforeUpload"
            name="file"
            :headers="{}"
          >
            <img v-if="game_form.image_url" :src="game_form.image_url" class="avatar" style="width: 80px; height: 60px; object-fit: cover;" />
            <el-icon v-else><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="游戏简介" prop="description">
          <el-input type="textarea" v-model="game_form.description" autocomplete="off" :rows="3"/>
        </el-form-item>
        <el-form-item label="地区" prop="region">
          <el-select v-model="game_form.region" placeholder="请选择地区">
            <el-option label="日本" value="日本"/>
            <el-option label="欧美" value="欧美"/>
            <el-option label="国产" value="国产"/>
            <el-option label="韩国" value="韩国"/>
          </el-select>
        </el-form-item>
        <el-form-item label="发行公司" prop="publisher">
          <el-input v-model="game_form.publisher" autocomplete="off"/>
        </el-form-item>
        <el-form-item label="发行日期" prop="release_date">
          <el-date-picker
              v-model="game_form.release_date"
              type="date"
              placeholder="选择发行日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="购买链接" prop="purchase_link">
          <el-input v-model="game_form.purchase_link" autocomplete="off"/>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm(ruleFormRef)" :loading="submitting">提交</el-button>
          <el-button @click="resetForm(ruleFormRef)">重置</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  
    <!-- 编辑游戏页面 -->
    <el-dialog
        title="编辑游戏"
        v-model="edit_dialog_visible"
        width="40%"
        :before-close="handleClose"
    >
      <el-form
          ref="editFormRef"
          :model="game_form"
          status-icon
          label-width="120px"
          class="demo-ruleForm"
      >
        <el-form-item label="游戏名称" prop="name">
          <el-input v-model="game_form.name" autocomplete="off"/>
        </el-form-item>
        <el-form-item label="封面图" prop="image_url">
          <el-upload
            class="avatar-uploader"
            action="http://localhost:5000/upload"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :before-upload="beforeUpload"
            name="file"
            :headers="{}"
          >
            <img v-if="game_form.image_url" :src="game_form.image_url" class="avatar" style="width: 80px; height: 60px; object-fit: cover;" />
            <el-icon v-else><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="游戏简介" prop="description">
          <el-input type="textarea" v-model="game_form.description" autocomplete="off" :rows="3"/>
        </el-form-item>
        <el-form-item label="地区" prop="region">
          <el-select v-model="game_form.region" placeholder="请选择地区">
            <el-option label="日本" value="日本"/>
            <el-option label="欧美" value="欧美"/>
            <el-option label="国产" value="国产"/>
            <el-option label="韩国" value="韩国"/>
          </el-select>
        </el-form-item>
        <el-form-item label="发行公司" prop="publisher">
          <el-input v-model="game_form.publisher" autocomplete="off"/>
        </el-form-item>
        <el-form-item label="发行日期" prop="release_date">
          <el-date-picker
              v-model="game_form.release_date"
              type="date"
              placeholder="选择发行日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="购买链接" prop="purchase_link">
          <el-input v-model="game_form.purchase_link" autocomplete="off"/>
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
  import { Plus } from '@element-plus/icons-vue'
  
  // 基础配置
  const API_BASE_URL = 'http://localhost:5000'
  
  // 响应式数据
  const games = reactive([])
  const loading = ref(false)
  const submitting = ref(false)
  const debugMode = ref(false)
  const lastRequestTime = ref('')
  const lastResponse = ref('')
  const currentPage = ref(1)
  const pageSize = ref(8)
  
  // 创建axios实例，添加拦截器
  const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json'
    }
  })
  
  // 请求拦截器
  api.interceptors.request.use(
      config => {
        lastRequestTime.value = new Date().toLocaleTimeString()
        console.log('发送请求:', config.method.toUpperCase(), config.url, config.data)
        return config
      },
      error => {
        console.error('请求错误:', error)
        return Promise.reject(error)
      }
  )
  
  // 响应拦截器
  api.interceptors.response.use(
      response => {
        lastResponse.value = `${response.status} - ${response.data?.message || 'success'}`
        console.log('收到响应:', response.data)
        return response
      },
      error => {
        console.error('响应错误:', error)
        lastResponse.value = `错误: ${error.message}`
        ElMessage.error(`请求失败: ${error.message}`)
        return Promise.reject(error)
      }
  )
  
  // 获取游戏数据
  const getGames = async () => {
    try {
      loading.value = true
      const res = await api.get('/games')
  
      if (res.data.status === 'success') {
        games.splice(0, games.length)
        games.push(...res.data.results)
        console.log(`更新数据成功，共 ${games.length} 个游戏`)
        ElMessage.success(`获取到 ${games.length} 个游戏的数据`)
      } else {
        throw new Error(res.data.message || '获取数据失败')
      }
    } catch (error) {
      console.error('获取游戏数据失败:', error)
      ElMessage.error('获取数据失败，请检查后端服务')
    } finally {
      loading.value = false
    }
  }
  
  // 刷新数据
  const refreshData = () => {
    console.log('手动刷新数据')
    getGames()
  }
  
  // 页面渲染之后加载数据
  onMounted(() => {
    console.log('组件挂载，开始获取数据')
    getGames()
  })
  
  // 删除数据
  const handleDelete = async (index, scope) => {
    try {
      await ElMessageBox.confirm('确定要删除这个游戏吗？', '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      })
  
      const res = await api.delete(`/games/${scope.game_id}`)
  
      if (res.data.status === 'success') {
        ElMessage.success('删除成功')
        await getGames() // 重新获取数据
      } else {
        throw new Error(res.data.message || '删除失败')
      }
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除失败:', error)
        ElMessage.error('删除失败')
      }
    }
  }
  
  /*表单添加*/
  const add_dialog_visible = ref(false)
  const ruleFormRef = ref()
  const emptyGameForm = {
    name: "",
    image_url: "",
    description: "",
    region: "",
    publisher: "",
    release_date: "",
    purchase_link: "",
    game_id: "",
  }
  const game_form = reactive(emptyGameForm)
  
  // 表单提交事件
  const submitForm = async (formEl) => {
    try {
      submitting.value = true
      console.log('提交添加表单:', game_form)
  
      const res = await api.post('/games', game_form)
  
      if (res.data.status === 'success') {
        ElMessage.success('添加成功')
        add_dialog_visible.value = false
        formEl.resetFields()
        await getGames() // 重新获取数据
      } else {
        throw new Error(res.data.message || '添加失败')
      }
    } catch (error) {
      console.error('添加失败:', error)
      ElMessage.error('添加失败')
    } finally {
      submitting.value = false
    }
  }
  
  // 重置表单
  const resetForm = (formEl) => {
    Object.assign(game_form, emptyGameForm)
    formEl.resetFields()
  }
  
  // 关闭弹窗前确认
  const handleClose = (done) => {
    ElMessageBox.confirm('确认关闭？')
        .then(() => {
          done()
        })
        .catch(() => {
          // 用户取消
        })
  }
  
  /*编辑表单*/
  const editFormRef = ref()
  const edit_dialog_visible = ref(false)
  
  const handleEdit = (index, scope) => {
    console.log('编辑游戏:', scope)
    // 深拷贝数据到表单
    for (let key in scope) {
      game_form[key] = scope[key]
    }
    edit_dialog_visible.value = true
  }
  
  // 编辑提交按钮
  const submitEditForm = async (formEl) => {
    try {
      submitting.value = true
      console.log('提交编辑表单:', game_form)
  
      const res = await api.put(`/games/${game_form.game_id}`, game_form)
  
      if (res.data.status === 'success') {
        ElMessage.success('修改成功')
        formEl.resetFields()
        edit_dialog_visible.value = false
        await getGames() // 重新获取数据
      } else {
        throw new Error(res.data.message || '修改失败')
      }
    } catch (error) {
      console.error('修改失败:', error)
      ElMessage.error('修改失败')
    } finally {
      submitting.value = false
    }
  }
  
  // 切换调试模式
  const toggleDebug = () => {
    debugMode.value = !debugMode.value
  }
  
  // 上传成功回调
  const handleUploadSuccess = (response) => {
    if (response.status === 'success') {
      game_form.image_url = 'http://localhost:5000' + response.file_url
      ElMessage.success('图片上传成功')
    } else {
      ElMessage.error(response.message || '图片上传失败')
    }
  }
  
  // 上传前校验（可选）
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
  
  // 处理分页变化
  const handlePageChange = (page) => {
    currentPage.value = page
  }
  
  const showAddDialog = () => {
    Object.assign(game_form, emptyGameForm); // 重置为初始值
    add_dialog_visible.value = true;
  };
  
  function getFullImageUrl(url) {
    if (!url) return '';
    if (url.startsWith('http')) return url;
    return API_BASE_URL + url;
  }
  </script>
  
  <style scoped>
  .el-table {
    width: 100%;
  }
  .pagination-container {
    margin-top: 20px;
    text-align: right;
  }
  .avatar-uploader .avatar {
    width: 80px;
    height: 60px;
    display: block;
  }
  </style>
<template>
  <div class="group-buy-overview">
    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="filter-section">
        <el-select v-model="statusFilter" placeholder="选择状态" @change="loadGroupBuys" class="filter-select">
          <el-option label="全部" value="" />
          <el-option label="招募中" value="recruiting" />
          <el-option label="已满员" value="full" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        <div class="search-box">
          <input
            v-model="searchQuery"
            @keyup="onSearchInputKeyup"
            placeholder="🔍 搜索拼团/商品..."
            class="search-input"
          />
          <button v-if="searchQuery" @click="clearSearch" class="clear-btn">✕</button>
        </div>
      </div>
      
      <div class="action-buttons">
        <el-button 
          type="success" 
          @click="showCreateProductDialog = true" 
          class="create-product-button"
          :disabled="!currentUser"
        >
          <span class="button-icon">🛍️</span>
          创建商品
        </el-button>
        
        <el-button 
          type="primary" 
          @click="showCreateDialog = true" 
          class="create-button"
          :disabled="!currentUser"
        >
          <span class="button-icon">✨</span>
          创建拼团
        </el-button>
      </div>
    </div>

    <!-- 拼团列表 -->
    <div class="group-buy-list" v-loading="loading">
      <div v-if="filteredGroupBuys.length === 0" class="empty-state">
        <div class="empty-icon">🎭</div>
        <p class="empty-text">暂无拼团，快来创建第一个拼团吧！</p>
      </div>
      
      <div v-else class="group-buy-grid">
        <div 
          v-for="groupBuy in filteredGroupBuys" 
          :key="groupBuy.group_buy_id" 
          class="group-buy-card"
          @click="goToDetail(groupBuy.group_buy_id)"
        >
          <!-- 商品图片 -->
          <div class="product-image">
            <img 
              :src="groupBuy.product?.image || '/src/assets/logo.png'" 
              :alt="groupBuy.product?.name"
              class="product-img"
            />
            <div class="status-badge" :class="getStatusClass(groupBuy.status)">
              {{ getStatusText(groupBuy.status) }}
            </div>
          </div>

          <!-- 拼团信息 -->
          <div class="group-buy-info">
            <h3 class="group-title">{{ groupBuy.title }}</h3>
            <p class="product-name">{{ groupBuy.product?.name }}</p>
            
            <div class="price-info">
              <span class="price-label">均价：</span>
              <span class="price-value">¥{{ groupBuy.average_price }}</span>
            </div>

            <div class="member-info">
              <span class="member-count">{{ groupBuy.total_max_count - (groupBuy.member_count || 0) }}</span>
              <span class="member-label">份可拼团</span>
            </div>

            <div class="leader-info">
              <span class="leader-label">团长：</span>
              <span class="leader-name">
                {{ groupBuy.leader?.nickname || groupBuy.leader?.username }}
                <span v-if="leaderStatsMap[groupBuy.leader?.user_id] !== undefined" style="color:#faad14;font-size:13px;margin-left:4px;">
                  （成功开团{{ leaderStatsMap[groupBuy.leader?.user_id] }}次）
                </span>
              </span>
            </div>

            <div class="time-info">
              <span class="time-label">截止：</span>
              <span class="time-value">{{ formatDeadline(groupBuy.deadline) }}</span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="card-actions">
            <el-button 
              type="primary" 
              size="small" 
              @click.stop="goToDetail(groupBuy.group_buy_id)"
              class="detail-button"
            >
              查看详情
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建拼团对话框 -->
    <el-dialog 
      v-model="showCreateDialog" 
      title="创建拼团" 
      width="600px"
      class="create-dialog"
    >
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="选择商品" prop="product_id">
          <el-select v-model="createForm.product_id" placeholder="请选择商品" @change="onProductChange">
            <el-option 
              v-for="product in products" 
              :key="product.product_id" 
              :label="product.name" 
              :value="product.product_id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="拼团标题" prop="title">
          <el-input v-model="createForm.title" placeholder="请输入拼团标题" />
        </el-form-item>

        <el-form-item label="拼团描述" prop="description">
          <el-input 
            v-model="createForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入拼团描述"
          />
        </el-form-item>

        <el-form-item label="联系方式" prop="contact_info">
          <el-input v-model="createForm.contact_info" placeholder="请输入联系方式" />
        </el-form-item>

        <el-form-item label="拼团均价" prop="average_price">
          <el-input-number v-model="createForm.average_price" :step="1" min="0" style="width: 100%;" placeholder="请输入拼团均价" />
        </el-form-item>

        <el-form-item label="截止时间" prop="deadline">
          <el-date-picker
            v-model="createForm.deadline"
            type="datetime"
            placeholder="选择截止时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
            :disabled-date="disabledDate"
            :disabled-time="disabledTime"
          />
        </el-form-item>

        <div v-if="selectedProduct && selectedProduct.characters && selectedProduct.characters.length">
          <h4 style="margin: 12px 0 8px 0; color: #ff1493;">角色调价与可拼团个数</h4>
          <div v-for="(character, idx) in selectedProduct.characters" :key="character.character_id" style="margin-bottom: 10px;display:flex;align-items:center;gap:16px;">
            <span style="display:inline-block;width:90px;">{{ character.name }}
              <el-tag v-if="character.is_popular" type="danger" size="small" style="margin-left:6px;">热门</el-tag>
            </span>
            <el-input-number v-model="createForm.character_adjustments[idx].price_adjustment" :step="1" style="width: 120px;" placeholder="调价" />
            <span style="margin-left:8px;color:#888;">元</span>
            <el-input-number v-model="createForm.character_adjustments[idx].max_count" :min="0" :step="1" style="width: 120px; margin-left:24px;" placeholder="可拼团个数" />
            <span style="margin-left:8px;color:#888;">份</span>
          </div>
        </div>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="createGroupBuy" :loading="creating">
            创建拼团
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 创建商品对话框 -->
    <el-dialog 
      v-model="showCreateProductDialog" 
      title="创建商品" 
      width="800px"
      class="create-product-dialog"
    >
      <el-form :model="productForm" :rules="productRules" ref="productFormRef" label-width="100px">
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="productForm.name" placeholder="请输入商品名称" />
        </el-form-item>

        <el-form-item label="商品描述" prop="description">
          <el-input 
            v-model="productForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入商品描述"
          />
        </el-form-item>

        <el-form-item label="商品图片" prop="image">
          <el-upload
            class="image-upload"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :show-file-list="false"
            :on-success="handleImageSuccess"
            :on-error="handleImageError"
            :before-upload="beforeImageUpload"
            accept="image/*"
            name="file"
          >
            <div v-if="productForm.image" class="image-preview">
              <img :src="productForm.image" class="preview-img" />
              <div class="image-overlay">
                <span class="upload-text">点击更换图片</span>
              </div>
            </div>
            <div v-else class="upload-placeholder">
              <span class="upload-text">上传图片</span>
            </div>
          </el-upload>
        </el-form-item>

        <!-- 角色管理 -->
        <el-form-item label="角色管理">
          <div class="characters-section">
            <div class="characters-header">
              <h4>角色列表</h4>
              <el-button 
                type="primary" 
                size="small" 
                @click="addCharacter"
                :disabled="productForm.characters.length >= maxCharacterCount"
              >
                添加角色
              </el-button>
            </div>
            
            <div class="characters-list-vertical">
              <div 
                v-for="(character, index) in productForm.characters" 
                :key="index" 
                class="character-item-vertical"
                style="max-width: 520px; min-width: 350px; margin: 0 auto; position: relative;"
              >
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="removeCharacter(index)"
                  class="remove-character-btn-vertical"
                  style="position:absolute;top:12px;right:12px;z-index:2;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;"
                >
                  <span style="font-size:20px;">×</span>
                </el-button>
                <el-form-item :label="`角色${index + 1}`" :prop="`characters.${index}.name`" :rules="characterRules.name">
                  <el-input v-model="character.name" placeholder="角色名称" />
                </el-form-item>
                <el-form-item label="角色图片" :prop="`characters.${index}.image`" :rules="characterRules.image">
                  <el-upload
                    class="character-image-upload"
                    :action="uploadUrl"
                    :headers="uploadHeaders"
                    :show-file-list="false"
                    :on-success="(res) => handleCharacterImageSuccess(res, index)"
                    :on-error="handleImageError"
                    :before-upload="beforeImageUpload"
                    accept="image/*"
                    name="file"
                  >
                    <div v-if="character.image" class="character-image-preview">
                      <img :src="character.image" class="character-preview-img" />
                      <div class="image-overlay">
                        <span class="upload-text">更换</span>
                      </div>
                    </div>
                    <div v-else class="character-upload-placeholder">
                      <span class="upload-text">上传图片</span>
                    </div>
                  </el-upload>
                </el-form-item>
                <el-form-item label="热门角色">
                  <el-switch v-model="character.is_popular" />
                </el-form-item>
              </div>
            </div>
            
            <div v-if="productForm.characters.length === 0" class="no-characters">
              <p>请添加角色</p>
            </div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateProductDialog = false">取消</el-button>
          <el-button type="primary" @click="createProduct" :loading="creatingProduct">
            创建商品
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const creating = ref(false)
const creatingProduct = ref(false)
const showCreateDialog = ref(false)
const showCreateProductDialog = ref(false)
const statusFilter = ref('')
const groupBuys = ref([])
const products = ref([])
const selectedProduct = ref(null)
const maxCharacterCount = 20
const leaderStatsMap = ref({})
const searchQuery = ref('')

// 当前用户
const currentUser = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  return user
})

// 创建表单
const createForm = ref({
  product_id: '',
  title: '',
  description: '',
  contact_info: '',
  average_price: null,
  deadline: '',
  character_adjustments: []
})

const createFormRef = ref()

// 商品表单
const productForm = ref({
  name: '',
  description: '',
  image: '',
  characters: []
})

const productFormRef = ref()

// 上传相关
const uploadUrl = 'http://localhost:5000/upload'
const IMAGE_PREFIX = 'http://localhost:5000'
const uploadHeaders = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  return user ? { 'Authorization': `Bearer ${user.token}` } : {}
})

// 角色验证规则
const characterRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 1, max: 50, message: '角色名称长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  image: [
    { required: true, message: '请上传角色图片', trigger: 'change' }
  ]
}

// 表单验证规则
const createRules = {
  product_id: [
    { required: true, message: '请选择商品', trigger: 'change' }
  ],
  title: [
    { required: true, message: '请输入拼团标题', trigger: 'blur' },
    { min: 2, max: 50, message: '标题长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '描述不能超过 500 个字符', trigger: 'blur' }
  ],
  contact_info: [
    { required: true, message: '请输入联系方式', trigger: 'blur' }
  ],
  average_price: [
    { required: true, message: '请输入拼团均价', trigger: 'blur' },
    { type: 'number', min: 0, message: '均价必须大于0', trigger: 'blur' }
  ],
  deadline: [
    { required: true, message: '请选择截止时间', trigger: 'change' }
  ]
}

// 商品表单验证规则
const productRules = {
  name: [
    { required: true, message: '请输入商品名称', trigger: 'blur' },
    { min: 2, max: 100, message: '商品名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 1000, message: '描述不能超过 1000 个字符', trigger: 'blur' }
  ],
  image: [
    { required: true, message: '请上传商品图片', trigger: 'change' }
  ]
}

// 获取拼团列表
const loadGroupBuys = async () => {
  loading.value = true
  try {
    const response = await axios.get(`http://localhost:5000/api/group-buy/group-buys?status=${statusFilter.value}`)
    if (response.data.success) {
      groupBuys.value = response.data.data
    }
  } catch (error) {
    ElMessage.error('获取拼团列表失败')
  } finally {
    loading.value = false
  }
}

// 获取商品列表
const loadProducts = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/group-buy/products')
    if (response.data.success) {
      products.value = response.data.data
    }
  } catch (error) {
    ElMessage.error('获取商品列表失败')
  }
}

// 商品选择变化
const onProductChange = () => {
  selectedProduct.value = products.value.find(p => p.product_id === createForm.value.product_id)
  if (selectedProduct.value && selectedProduct.value.characters) {
    createForm.value.character_adjustments = selectedProduct.value.characters.map(c => ({
      character_id: c.character_id,
      price_adjustment: 0,
      max_count: 1
    }))
  } else {
    createForm.value.character_adjustments = []
  }
}

// 创建拼团
const createGroupBuy = async () => {
  if (!currentUser.value) {
    ElMessage.error('请先登录')
    return
  }

  try {
    await createFormRef.value.validate()
  } catch (error) {
    return
  }

  creating.value = true
  try {
    const groupBuyData = {
      ...createForm.value,
      leader_id: currentUser.value.user_id,
      character_adjustments: createForm.value.character_adjustments.map(adj => ({
        character_id: adj.character_id,
        price_adjustment: adj.price_adjustment,
        max_count: adj.max_count
      }))
    }

    const response = await axios.post('http://localhost:5000/api/group-buy/group-buys', groupBuyData)
    
    if (response.data.success) {
      ElMessage.success('拼团创建成功！')
      showCreateDialog.value = false
      resetCreateForm()
      loadGroupBuys()
    } else {
      ElMessage.error(response.data.message || '创建失败')
    }
  } catch (error) {
    ElMessage.error('创建拼团失败')
  } finally {
    creating.value = false
  }
}

// 重置创建表单
const resetCreateForm = () => {
  createForm.value = {
    product_id: '',
    title: '',
    description: '',
    contact_info: '',
    average_price: null,
    deadline: '',
    character_adjustments: []
  }
  selectedProduct.value = null
  createFormRef.value?.resetFields()
}

// 创建商品
const createProduct = async () => {
  if (!currentUser.value) {
    ElMessage.error('请先登录')
    return
  }

  try {
    await productFormRef.value.validate()
  } catch (error) {
    return
  }

  // 验证角色数量
  if (productForm.value.characters.length === 0) {
    ElMessage.error('请至少添加一个角色')
    return
  }

  // 验证所有角色信息
  for (let i = 0; i < productForm.value.characters.length; i++) {
    const character = productForm.value.characters[i]
    if (!character.name || !character.image) {
      ElMessage.error(`请完善角色${i + 1}的信息`)
      return
    }
  }

  creatingProduct.value = true
  try {
    const productData = {
      name: productForm.value.name,
      description: productForm.value.description,
      image: productForm.value.image,
      characters: productForm.value.characters.map(c => ({
        name: c.name,
        image: c.image,
        is_popular: c.is_popular
      }))
    }

    const productResponse = await axios.post('http://localhost:5000/api/group-buy/products', productData)
    
    if (productResponse.data.success) {
      ElMessage.success('商品和角色创建成功！')
      showCreateProductDialog.value = false
      resetProductForm()
      loadProducts() // 重新加载商品列表
    } else {
      ElMessage.error(productResponse.data.message || '创建失败')
    }
  } catch (error) {
    ElMessage.error('创建商品失败')
  } finally {
    creatingProduct.value = false
  }
}

// 重置商品表单
const resetProductForm = () => {
  productForm.value = {
    name: '',
    description: '',
    image: '',
    characters: []
  }
  productFormRef.value?.resetFields()
}

// 图片上传相关方法
const handleImageSuccess = (response) => {
  if (response.status === 'success') {
    productForm.value.image = IMAGE_PREFIX + response.file_url
    ElMessage.success('图片上传成功')
  } else {
    ElMessage.error(response.message || '图片上传失败')
  }
}

const handleCharacterImageSuccess = (response, index) => {
  if (response.status === 'success') {
    productForm.value.characters[index].image = IMAGE_PREFIX + response.file_url
    ElMessage.success('角色图片上传成功')
  } else {
    ElMessage.error(response.message || '角色图片上传失败')
  }
}

const handleImageError = () => {
  ElMessage.error('图片上传失败')
}

const beforeImageUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

// 角色管理相关方法
const addCharacter = () => {
  if (productForm.value.characters.length < maxCharacterCount) {
    productForm.value.characters.push({
      name: '',
      image: '',
      is_popular: false
    })
  }
}

const removeCharacter = (index) => {
  productForm.value.characters.splice(index, 1)
}

// 跳转到详情页
const goToDetail = (id) => {
  router.push(`/group-buy/${id}`)
}

// 获取状态样式类
const getStatusClass = (status) => {
  const statusMap = {
    'recruiting': 'status-recruiting',
    'full': 'status-full',
    'completed': 'status-completed',
    'cancelled': 'status-cancelled'
  }
  return statusMap[status] || 'status-recruiting'
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

// 格式化截止时间
const formatDeadline = (deadline) => {
  if (!deadline) return '无截止时间'
  const date = new Date(deadline)
  return date.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })
}

// 禁用过去的日期
const disabledDate = (time) => {
  return time.getTime() < Date.now() - 8.64e7
}

// 禁用时间（可选）
const disabledTime = () => {
  return {}
}

async function loadLeaderStatsForList() {
  // 收集所有团长id
  const ids = Array.from(new Set(groupBuys.value.map(gb => gb.leader?.user_id).filter(Boolean)))
  const statsMap = {}
  await Promise.all(ids.map(async (id) => {
    try {
      const res = await axios.get(`http://localhost:5000/api/group-buy/user-group-buy-stats/${id}`)
      statsMap[id] = res.data.successful_groups || 0
    } catch {
      statsMap[id] = 0
    }
  }))
  leaderStatsMap.value = statsMap
}

watch(groupBuys, () => {
  loadLeaderStatsForList()
})

// 页面加载
onMounted(() => {
  loadGroupBuys()
  loadProducts()
})

// 搜索功能
const filteredGroupBuys = computed(() => {
  if (!searchQuery.value.trim()) return groupBuys.value
  const q = searchQuery.value.trim().toLowerCase()
  return groupBuys.value.filter(gb =>
    (gb.title && gb.title.toLowerCase().includes(q)) ||
    (gb.product && gb.product.name && gb.product.name.toLowerCase().includes(q))
  )
})

function onSearchInputKeyup(e) {
  if (e.key === 'Enter') {
    // 触发过滤，实际已响应式
  }
}

function clearSearch() {
  searchQuery.value = ''
}
</script>

<style scoped>
.group-buy-overview {
  padding: 24px;
  min-height: 100vh;
  background: linear-gradient(135deg, #ffeef8 0%, #fff0f5 100%);
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(255, 105, 180, 0.1);
  gap: 16px;
}

.filter-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-box {
  position: relative;
  width: 220px;
}

.search-input {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 2px solid #f8bbd9;
  border-radius: 20px;
  font-size: 0.9rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  color: #333;
  outline: none;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.search-input:focus {
  border-color: #d63384;
  box-shadow: 0 0 15px rgba(216, 27, 96, 0.15);
}

.search-input::placeholder {
  color: #ba68c8;
  opacity: 0.7;
}

.clear-btn {
  position: absolute;
  right: 0.8rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #d63384;
  cursor: pointer;
  font-size: 1rem;
  opacity: 0.7;
  transition: opacity 0.3s ease;
}

.clear-btn:hover {
  opacity: 1;
}

.create-product-button {
  background: #ffd6e0;
  color: #d63384;
  border: none;
  border-radius: 25px;
  padding: 12px 24px;
  font-weight: bold;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(255,182,213,0.13);
}

.create-product-button:hover {
  background: #ffb6d5;
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255,182,213,0.18);
}

.create-button {
  background: linear-gradient(45deg, #ffb6d5, #ff69b4);
  color: #fff;
  border: none;
  border-radius: 25px;
  padding: 12px 24px;
  font-weight: bold;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(255,182,213,0.13);
}

.create-button:hover {
  background: linear-gradient(45deg, #ff69b4, #ffb6d5);
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255,182,213,0.18);
}

.button-icon {
  margin-right: 8px;
}

.group-buy-list {
  min-height: 400px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 16px;
  margin: 0;
}

.group-buy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.group-buy-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(255, 105, 180, 0.15);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.group-buy-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(255, 105, 180, 0.25);
}

.product-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.product-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.group-buy-card:hover .product-img {
  transform: scale(1.05);
}

.status-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.status-recruiting {
  background: linear-gradient(45deg, #ffb6d5, #ff69b4);
}

.status-full {
  background: #ffd6e0;
  color: #d63384;
}

.status-completed {
  background: #e0c3fc;
  color: #a259c4;
}

.status-cancelled {
  background: #f8bbd9;
  color: #d63384;
}

.group-buy-info {
  padding: 20px;
}

.group-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.product-name {
  color: #666;
  font-size: 14px;
  margin: 0 0 12px 0;
}

.price-info {
  margin-bottom: 8px;
}

.price-label {
  color: #999;
  font-size: 14px;
}

.price-value {
  color: #ff1493;
  font-weight: bold;
  font-size: 16px;
}

.member-info {
  margin-bottom: 8px;
}

.member-count {
  color: #1890ff;
  font-weight: bold;
  font-size: 16px;
}

.member-label {
  color: #999;
  font-size: 14px;
}

.leader-info {
  margin-bottom: 8px;
}

.leader-label {
  color: #999;
  font-size: 14px;
}

.leader-name {
  color: #333;
  font-weight: bold;
  font-size: 14px;
}

.time-info {
  margin-bottom: 16px;
}

.time-label {
  color: #999;
  font-size: 14px;
}

.time-value {
  color: #666;
  font-size: 14px;
}

.card-actions {
  padding: 0 20px 20px;
}

.detail-button {
  width: 100%;
  background: #ffd6e0;
  color: #d63384;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(255,182,213,0.13);
}

.detail-button:hover {
  background: #ffb6d5;
  color: #fff;
}

/* 对话框样式 */
:deep(.create-dialog .el-dialog__header) {
  background: linear-gradient(135deg, #ffeef8, #fff0f5);
  border-bottom: 2px solid #ff69b4;
}

:deep(.create-dialog .el-dialog__title) {
  color: #ff1493;
  font-weight: bold;
}

:deep(.create-product-dialog .el-dialog__header) {
  background: linear-gradient(135deg, #f6ffed, #f0f9ff);
  border-bottom: 2px solid #52c41a;
}

:deep(.create-product-dialog .el-dialog__title) {
  color: #52c41a;
  font-weight: bold;
}

.product-preview {
  margin-top: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #ff69b4;
}

.product-preview h4 {
  color: #ff1493;
  margin: 0 0 12px 0;
}

.preview-content {
  display: flex;
  gap: 16px;
}

.preview-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  border: 2px solid #ff69b4;
}

.preview-info p {
  margin: 4px 0;
  font-size: 14px;
  color: #666;
}

.preview-info strong {
  color: #333;
}

/* 图片上传样式 */
.image-upload {
  width: 100%;
}

.image-preview {
  position: relative;
  width: 200px;
  height: 150px;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.image-preview:hover {
  border-color: #ff69b4;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-preview:hover .image-overlay {
  opacity: 1;
}

.upload-placeholder {
  width: 200px;
  height: 150px;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-placeholder:hover {
  border-color: #ff69b4;
  background: #fff0f5;
}

.upload-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.upload-text {
  color: #666;
  font-size: 14px;
}

/* 角色管理样式 */
.characters-section {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
}

.characters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.characters-header h4 {
  color: #333;
  margin: 0;
}

.characters-list-vertical {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.character-item-vertical {
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 16px;
  position: relative;
}

.remove-character-btn-vertical {
  position: absolute;
  top: 8px;
  right: 8px;
  height: 32px;
}

.no-characters {
  text-align: center;
  color: #999;
  padding: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .group-buy-overview {
    padding: 16px;
  }

  .action-bar {
    flex-direction: column;
    gap: 16px;
  }

  .action-buttons {
    flex-direction: column;
    width: 100%;
  }

  .create-product-button,
  .create-button {
    width: 100%;
  }

  .group-buy-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .image-preview,
  .upload-placeholder {
    width: 100%;
    height: 120px;
  }
}
</style>

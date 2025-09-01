.group-card.my-group {
background: linear-gradient(135deg, rgba(255, 240, 245, 0.9), rgba(248, 240, 255, 0.9));
}<template>
  <div class="group-overview-container">
    <!-- 顶部导航栏 -->
    <div class="top-bar">
      <div class="tabs-container">
        <button
            :class="['tab-btn', { active: activeTab === 'all' }]"
            @click="activeTab = 'all'"
        >
           全部小组
        </button>
        <button
            :class="['tab-btn', { active: activeTab === 'mine' }]"
            @click="activeTab = 'mine'"
        >
          我的小组
        </button>
      </div>

      <!-- 搜索框 -->
      <div v-if="activeTab === 'all'" class="search-section">
        <div class="search-box">
          <input
              v-model="searchText"
              placeholder="🔍 搜索小组名称..."
              class="search-input"
          />
          <button v-if="searchText" @click="searchText = ''" class="clear-btn">✕</button>
        </div>
      </div>
    </div>

    <!-- 全部小组页面 -->
    <div v-if="activeTab === 'all'" class="tab-content">

      <!-- 小组卡片网格 -->
      <div class="groups-grid">
        <div
            v-for="group in filteredGroups"
            :key="group.group_id"
            class="group-card"
            @click="goToGroupDetail(group.group_id)"
        >
          <div class="card-inner">
            <div class="avatar-section">
              <div class="avatar-wrapper">
                <img
                    v-if="group.avatar"
                    :src="getFullImageUrl(group.avatar)"
                    class="group-avatar"
                    :alt="group.name"
                />
                <div v-else class="default-avatar">🌟</div>
              </div>
            </div>
            <div class="info-section">
              <h3 class="group-name">
                <span v-if="group.is_official" class="official-badge">官方</span>
                {{ group.name }}
              </h3>
              <div class="member-info">
                <span class="member-count">👥 {{ group.member_count }} 人</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 我的小组页面 -->
    <div v-if="activeTab === 'mine'" class="tab-content">
      <div class="groups-grid">
        <div
            v-for="group in myGroups"
            :key="group.group_id"
            class="group-card"
            @click="goToGroupDetail(group.group_id)"
        >
          <div class="card-inner">
            <div class="avatar-section">
              <div class="avatar-wrapper">
                <img
                    v-if="group.avatar"
                    :src="getFullImageUrl(group.avatar)"
                    class="group-avatar"
                    :alt="group.name"
                />
                <div v-else class="default-avatar">🌟</div>
              </div>
            </div>
            <div class="info-section">
              <h3 class="group-name">
                <span v-if="group.is_official" class="official-badge">官方</span>
                {{ group.name }}
              </h3>
              <div class="member-info">
                <span class="member-count">👥 {{ group.member_count }} 人</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 热门帖子区域 -->
      <div v-if="hotPosts.length" class="hot-posts-section">
    
        <div class="posts-container">
          <div
              v-for="post in hotPosts"
              :key="post.post_id"
              class="post-card"
              @click="goToPostDetail(post.post_id)"
          >
            <div class="post-content">
              <h4 class="post-title">{{ post.title }}</h4>
              <div class="post-meta">
                <span class="author">👤 {{ post.nickname || post.username || '未知用户' }}</span>
                <span v-if="post.category_name" class="category">🏷️ {{ post.category_name }}</span>
                <span class="time">🕒 {{ formatTime(post.created_at) }}</span>
                <span class="likes">💝 {{ post.like_count }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const API_BASE_URL = 'http://localhost:5000'
const allGroups = ref([])
const myGroups = ref([])
const activeTab = ref('all')
const searchText = ref('')
const router = useRouter()
const hotPosts = ref([])

function getFullImageUrl(url) {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return API_BASE_URL + url
}

const fetchAllGroups = async () => {
  const res = await axios.get(API_BASE_URL + '/groups')
  allGroups.value = res.data
}

const fetchMyGroups = async () => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (!user) {
    myGroups.value = []
    return
  }
  const res = await axios.get(API_BASE_URL + `/users/${user.user_id}/groups`)
  myGroups.value = res.data
}

const filteredGroups = computed(() => {
  if (!searchText.value) return allGroups.value
  return allGroups.value.filter(g => g.name && g.name.includes(searchText.value))
})

function goToGroupDetail(groupId) {
  router.push({ name: 'GroupDetail', params: { id: groupId } })
}

function goToPostDetail(postId) {
  router.push(`/post/${postId}`)
}

const fetchHotPosts = async () => {
  if (!myGroups.value.length) {
    hotPosts.value = []
    return
  }
  const group_ids = myGroups.value.map(g => g.group_id)
  const res = await axios.post(API_BASE_URL + '/groups/hot-posts', { group_ids })
  hotPosts.value = res.data
}

function formatTime(time) {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchAllGroups()
  fetchMyGroups()
  fetchHotPosts()
})

watch(myGroups, fetchHotPosts, { immediate: true })
</script>

<style scoped>
.group-overview-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #ffeef8 0%, #fff0f5 50%, #f8f0ff 100%);
  padding: 1.5rem 1rem;
  font-family: 'PingFang SC', 'Hiragino Sans GB', sans-serif;
}

/* 顶部导航栏 */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
  flex-wrap: wrap;
}

/* 标签页 */
.tabs-container {
  display: flex;
  gap: 0.8rem;
  flex-shrink: 0;
}

.tab-btn {
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid #f8bbd9;
  border-radius: 15px;
  padding: 0.4rem 1rem;
  font-size: 0.85rem;
  color: #c2185b;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  font-weight: 500;
  white-space: nowrap;
}

.tab-btn:hover {
  background: rgba(248, 187, 217, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(194, 24, 91, 0.1);
}

.tab-btn.active {
  background: #ba68c8;
  color: white;
  box-shadow: 0 4px 15px rgba(233, 30, 99, 0.15);
}

/* 搜索区域 */
.search-section {
  flex: 1;
  max-width: 280px;
  min-width: 200px;
}

.search-box {
  position: relative;
  width: 100%;
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
  border-color: #d81b60;
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
  color: #d81b60;
  cursor: pointer;
  font-size: 1rem;
  opacity: 0.7;
  transition: opacity 0.3s ease;
}

.clear-btn:hover {
  opacity: 1;
}

/* 小组网格 */
.groups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.2rem;
  margin-bottom: 2.5rem;
}

.group-card {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(248, 187, 217, 0.3);
}

.group-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 30px rgba(216, 27, 96, 0.15);
  border-color: #f8bbd9;
}

.group-card.my-group {
  background: linear-gradient(135deg, rgba(255, 240, 245, 0.9), rgba(248, 240, 255, 0.9));
}

.card-inner {
  padding: 1.5rem;
  text-align: center;
}

.avatar-section {
  margin-bottom: 1rem;
}

.avatar-wrapper {
  display: inline-block;
  position: relative;
}

.group-avatar {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  object-fit: cover;
  border: 2px solid rgba(216, 27, 96, 0.2);
  transition: all 0.3s ease;
}

.group-card:hover .group-avatar {
  border-color: #d81b60;
  transform: scale(1.05);
}

.default-avatar {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f8bbd9, #e1bee7);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  border: 2px solid rgba(216, 27, 96, 0.2);
}

.group-name {
  font-size: 1rem;
  font-weight: 600;
  color: #d81b60;
  margin: 0 0 0.4rem 0;
  line-height: 1.3;
}

.member-info {
  color: #8e24aa;
  font-size: 0.8rem;
  opacity: 0.8;
}

/* 热门帖子区域 */
.hot-posts-section {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  padding: 2rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(248, 187, 217, 0.3);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #d81b60;
  margin: 0;
}

.decoration {
  font-size: 1.2rem;
  opacity: 0.7;
}

.posts-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.post-card {
  background: rgba(248, 240, 255, 0.6);
  border-radius: 15px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(142, 36, 170, 0.1);
}

.post-card:hover {
  transform: translateX(10px);
  background: rgba(248, 240, 255, 0.9);
  box-shadow: 0 8px 25px rgba(142, 36, 170, 0.1);
}

.post-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #6a1b99;
  margin: 0 0 0.8rem 0;
  line-height: 1.4;
}

.post-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.85rem;
  opacity: 0.8;
}

.post-meta span {
  color: #8e24aa;
}

.author {
  font-weight: 500;
}

.category {
  background: rgba(142, 36, 170, 0.1);
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
  color: #6a1b99 !important;
}

.time {
  color: #ba68c8 !important;
}

.likes {
  color: #d81b60 !important;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .group-overview-container {
    padding: 1.2rem 0.8rem;
  }

  .top-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .tabs-container {
    justify-content: center;
  }

  .search-section {
    max-width: none;
    width: 100%;
  }

  .groups-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }

  .post-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
}

@media (max-width: 480px) {
  .groups-grid {
    grid-template-columns: 1fr;
  }

  .hot-posts-section {
    padding: 1.5rem;
  }

  .tabs-container {
    flex-direction: column;
    align-items: center;
  }

  .tab-btn {
    width: 160px;
  }

  .search-section {
    order: 2;
  }

  .tabs-container {
    order: 1;
  }
}

.official-badge {
  color: #2196f3;
  font-weight: bold;
  margin-right: 4px;
}
</style>
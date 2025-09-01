<template>
  <div class="post-create-main">
    <el-input
      v-model="postTitle"
      placeholder="请输入帖子标题"
      style="margin-bottom: 16px;"
      maxlength="200"
      show-word-limit
    />
    <el-select
      v-model="selectedCategory"
      placeholder="选择分类（可选）"
      clearable
      style="width: 220px; margin-bottom: 16px;"
    >
      <el-option
        v-for="category in categories"
        :key="category.category_id"
        :label="category.name"
        :value="category.category_id"
      />
    </el-select>
    <div style="margin-bottom: 16px;">
      <el-radio-group v-model="postType">
        <el-radio label="normal">普通帖子</el-radio>
        <el-radio label="poll">投票帖</el-radio>
      </el-radio-group>
    </div>
    <div v-if="postType === 'poll'" class="poll-settings">
      <div style="margin-bottom: 12px;">
        <el-radio-group v-model="pollType">
          <el-radio label="single">单选投票</el-radio>
          <el-radio label="multi">多选投票</el-radio>
        </el-radio-group>
      </div>
      <div style="margin-bottom: 12px;">
        <label>投票选项：</label>
        <div v-for="(option, index) in pollOptions" :key="index" style="margin-bottom: 8px; display: flex; align-items: center;">
          <el-input
            v-model="pollOptions[index]"
            :placeholder="`选项 ${index + 1}`"
            style="flex: 1; margin-right: 8px;"
          />
          <el-button
            v-if="pollOptions.length > 2"
            type="danger"
            size="small"
            @click="removePollOption(index)"
          >删除</el-button>
        </div>
        <el-button type="primary" size="small" @click="addPollOption">添加选项</el-button>
      </div>
      <div style="margin-bottom: 12px;">
        <label>投票截止时间（可选）：</label>
        <el-date-picker
          v-model="pollDeadline"
          type="datetime"
          placeholder="选择截止时间"
          format="YYYY-MM-DD HH:mm:ss"
          value-format="YYYY-MM-DDTHH:mm:ss"
          style="margin-left: 8px;"
        />
      </div>
    </div>
    <QuillEditor
      v-model:content="quillContent"
      contentType="html"
      style="height: 350px; margin-bottom: 32px; width: 100%;"
      :options="editorOption"
    />
    <div class="post-btn-row">
      <el-button type="primary" @click="submitPost" size="large">发布</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { QuillEditor, Quill } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import BlotFormatter from 'quill-blot-formatter'
Quill.register('modules/blotFormatter', BlotFormatter)
import { ImageDrop } from 'quill-image-drop-module'
Quill.register('modules/imageDrop', ImageDrop)
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const user = JSON.parse(localStorage.getItem('user') || 'null')
const API_BASE_URL = 'http://localhost:5000'

// 发帖相关数据
const postTitle = ref('')
const postType = ref('normal')
const selectedCategory = ref(null)
const pollType = ref('single')
const pollOptions = ref(['', ''])
const pollDeadline = ref(null)
const quillContent = ref('')
const categories = ref([])

const editorOption = {
  modules: {
    toolbar: [
      [{ header: [1, 2, 3, 4, 5, 6] }],
      [{ size: ['small', false, 'large', 'huge'] }],
      ['bold', 'italic', 'underline', 'strike'],
      ['blockquote', 'code-block'],
      [{ header: 1 }, { header: 2 }],
      [{ list: 'ordered' }, { list: 'bullet' }],
      [{ script: 'sub' }, { script: 'super' }],
      [{ indent: '-1' }, { indent: '+1' }],
      [{ direction: 'rtl' }],
      [{ color: [] }, { background: [] }],
      [{ font: [] }],
      [{ align: [] }],
      ['clean'],
      ['image', 'link', 'video']
    ],
    imageDrop: true,
    blotFormatter: {}
  },
  theme: 'snow',
  placeholder: '请输入帖子内容'
}

const addPollOption = () => {
  pollOptions.value.push('')
}
const removePollOption = (index) => {
  pollOptions.value.splice(index, 1)
}

const fetchCategories = async () => {
  const res = await axios.get(`${API_BASE_URL}/post-categories`)
  categories.value = res.data
}

onMounted(() => {
  fetchCategories()
})

const submitPost = async () => {
  if (!user) {
    ElMessage.warning('请先登录')
    return
  }
  if (!postTitle.value.trim()) {
    ElMessage.warning('请填写标题')
    return
  }
  const content = quillContent.value
  if (!content || content === '<p><br></p>') {
    ElMessage.warning('请填写内容')
    return
  }
  // 投票帖验证
  if (postType.value === 'poll') {
    const validOptions = pollOptions.value.filter(opt => opt.trim())
    if (validOptions.length < 2) {
      ElMessage.warning('投票至少需要2个选项')
      return
    }
  }
  try {
    const group_id = route.params.id || route.params.group_id || route.query.group_id
    const postData = {
      user_id: user.user_id,
      title: postTitle.value.trim(),
      content: content,
      category_id: selectedCategory.value,
      is_poll: postType.value === 'poll',
      poll_type: pollType.value,
      poll_deadline: pollDeadline.value,
      poll_options: postType.value === 'poll' ? pollOptions.value.filter(opt => opt.trim()) : null
    }
    await axios.post(`${API_BASE_URL}/groups/${group_id}/posts`, postData)
    ElMessage.success('发布成功')
    router.push(`/group/${group_id}`)
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '发布失败')
  }
}
</script>

<style scoped>
.post-create-main {
  max-width: 900px;
  margin: 40px auto 0 auto;
  padding: 32px 24px 48px 24px;
  min-height: 80vh;
}
.poll-settings {
  background: #fafbfc;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  border: 1px solid #e0e0e0;
  max-width: 100%;
}
.post-btn-row {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style> 
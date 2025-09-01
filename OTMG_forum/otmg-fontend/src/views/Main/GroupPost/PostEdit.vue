<template>
  <div class="post-edit-main" v-if="post">
    <h2 class="edit-title">编辑帖子</h2>
    <el-input
      v-model="form.title"
      placeholder="请输入帖子标题"
      style="margin-bottom: 16px;"
      maxlength="200"
      show-word-limit
    />
    <el-select
      v-model="form.category_id"
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
      <el-radio-group v-model="form.type">
        <el-radio label="normal">普通帖子</el-radio>
        <el-radio label="poll">投票帖</el-radio>
      </el-radio-group>
    </div>
    <div v-if="form.type === 'poll'" class="poll-settings">
      <div style="margin-bottom: 12px;">
        <el-radio-group v-model="form.poll_type">
          <el-radio label="single">单选投票</el-radio>
          <el-radio label="multi">多选投票</el-radio>
        </el-radio-group>
      </div>
      <div style="margin-bottom: 12px;">
        <label>投票选项：</label>
        <div v-for="(option, index) in form.poll_options" :key="index" style="margin-bottom: 8px; display: flex; align-items: center;">
          <el-input
            v-model="form.poll_options[index]"
            :placeholder="`选项 ${index + 1}`"
            style="flex: 1; margin-right: 8px;"
          />
          <el-button
            v-if="form.poll_options.length > 2"
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
          v-model="form.poll_deadline"
          type="datetime"
          placeholder="选择截止时间"
          format="YYYY-MM-DD HH:mm:ss"
          value-format="YYYY-MM-DDTHH:mm:ss"
          style="margin-left: 8px;"
        />
      </div>
    </div>
    <QuillEditor
      v-model:content="form.content"
      contentType="html"
      style="height: 350px; margin-bottom: 32px; width: 100%;"
      :options="editorOption"
    />
    <div class="post-btn-row">
      <el-button type="primary" @click="submitEdit" size="large">保存</el-button>
      <el-button @click="goBack" size="large">取消</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { QuillEditor, Quill } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import BlotFormatter from 'quill-blot-formatter'
Quill.register('modules/blotFormatter', BlotFormatter)
import { ImageDrop } from 'quill-image-drop-module'
Quill.register('modules/imageDrop', ImageDrop)

const API_BASE_URL = 'http://localhost:5000'
const route = useRoute()
const router = useRouter()
const post = ref(null)
const categories = ref([])
const form = ref({
  title: '',
  content: '',
  category_id: null,
  imagesStr: '',
  type: 'normal',
  poll_type: 'single',
  poll_options: ['', ''],
  poll_deadline: null
})

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
  form.value.poll_options.push('')
}
const removePollOption = (index) => {
  form.value.poll_options.splice(index, 1)
}

const fetchPost = async () => {
  const res = await axios.get(`${API_BASE_URL}/posts/${route.params.id}`)
  post.value = res.data
  form.value.title = post.value.title
  form.value.content = post.value.content
  form.value.category_id = post.value.category_id
  form.value.imagesStr = post.value.images && post.value.images.length ? post.value.images.join(',') : ''
  if (post.value.is_poll) {
    form.value.type = 'poll'
    form.value.poll_type = post.value.poll_type || 'single'
    form.value.poll_options = post.value.poll_options ? post.value.poll_options.map(opt => opt.text) : ['', '']
    form.value.poll_deadline = post.value.poll_deadline
  } else {
    form.value.type = 'normal'
    form.value.poll_type = 'single'
    form.value.poll_options = ['', '']
    form.value.poll_deadline = null
  }
}

const fetchCategories = async () => {
  const res = await axios.get(`${API_BASE_URL}/post-categories`)
  categories.value = res.data
}

const submitEdit = async () => {
  if (!form.value.title.trim()) {
    ElMessage.warning('请填写标题')
    return
  }
  const content = form.value.content
  if (!content || content === '<p><br></p>') {
    ElMessage.warning('请填写内容')
    return
  }
  if (form.value.type === 'poll') {
    const validOptions = form.value.poll_options.filter(opt => opt.trim())
    if (validOptions.length < 2) {
      ElMessage.warning('投票至少需要2个选项')
      return
    }
  }
  try {
    await axios.put(`${API_BASE_URL}/posts/${route.params.id}`, {
      title: form.value.title,
      content: form.value.content,
      category_id: form.value.category_id,
      images: form.value.imagesStr ? form.value.imagesStr.split(',').map(s => s.trim()) : [],
      is_poll: form.value.type === 'poll',
      poll_type: form.value.poll_type,
      poll_deadline: form.value.poll_deadline,
      poll_options: form.value.type === 'poll' ? form.value.poll_options.filter(opt => opt.trim()) : null
    })
    ElMessage.success('保存成功')
    router.push(`/post/${route.params.id}`)
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '保存失败')
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchPost()
  fetchCategories()
})
</script>

<style scoped>
.post-edit-main {
  max-width: 900px;
  margin: 16px auto 0 auto;
  padding: 18px 24px 48px 24px;
  min-height: 80vh;
  /* background: #fff; */
  /* border-radius: 10px; */
  /* box-shadow: 0 2px 8px rgba(0,0,0,0.04); */
}
.edit-title {
  color: #d63384;
  margin-bottom: 24px;
  font-size: 22px;
  text-align: center;
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
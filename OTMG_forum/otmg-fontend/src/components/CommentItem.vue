<template>
  <div class="comment-item" :class="{ child: depth > 0 }">
    <div class="comment-header">
      <div class="comment-user-info">
        <div class="avatar-wrapper">
          <img 
            v-if="comment.avatar" 
            :src="getFullImageUrl(comment.avatar)" 
            class="comment-avatar" 
            alt="头像"
          />
          <div v-else class="comment-default-avatar">👤</div>
          <div v-if="comment.role === 'publisher'" class="publisher-badge-comment">
            <span class="publisher-icon-comment">🎮</span>
          </div>
        </div>
        <span class="comment-nickname">{{ comment.nickname }}</span>
      </div>
      <div class="comment-meta">
        <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
        <span
          class="comment-like"
          :class="{ liked: comment.liked }"
          @click="likeComment(comment)"
        >❤{{ comment.like_count }}</span>
        <span class="comment-reply" @click="$emit('update:replyToId', comment.id)">回复</span>
        <template v-if="isMyComment(comment)">
          <span v-if="!editMap[comment.id]" class="comment-edit" @click="startEdit(comment)">编辑</span>
          <span class="comment-delete" @click="deleteComment(comment)">删除</span>
        </template>
      </div>
    </div>
    <div v-if="editMap[comment.id]" class="comment-edit-area">
      <el-input v-model="editContentMap[comment.id]" type="textarea" :rows="2" maxlength="300" show-word-limit />
      <el-button size="small" type="primary" @click="saveEdit(comment)">保存</el-button>
      <el-button size="small" @click="cancelEdit(comment)">取消</el-button>
    </div>
    <div v-else class="comment-content">{{ comment.content }}</div>
    <div v-if="replyToId === comment.id" class="reply-box">
      <el-input :model-value="replyContent" @update:model-value="val => $emit('update:replyContent', val)" placeholder="回复内容..." />
      <el-button @click="submitReply(comment.id)" size="small">回复</el-button>
    </div>
    <div v-if="comment.children && comment.children.length" class="comment-children">
      <CommentItem
        v-for="child in comment.children"
        :key="child.id"
        :comment="child"
        :depth="depth + 1"
        :replyToId="replyToId"
        :replyContent="replyContent"
        :likeComment="likeComment"
        :submitReply="submitReply"
        :formatTime="formatTime"
        :isMyComment="isMyComment"
        :editMap="editMap"
        :editContentMap="editContentMap"
        :startEdit="startEdit"
        :saveEdit="saveEdit"
        :cancelEdit="cancelEdit"
        :deleteComment="deleteComment"
        @update:replyToId="$emit('update:replyToId', $event)"
        @update:replyContent="$emit('update:replyContent', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import CommentItem from './CommentItem.vue'

const API_BASE_URL = 'http://localhost:5000'

const props = defineProps({
  comment: Object,
  depth: { type: Number, default: 0 },
  replyToId: Number,
  replyContent: String,
  likeComment: Function,
  submitReply: Function,
  formatTime: Function,
  isMyComment: Function,
  editMap: Object,
  editContentMap: Object,
  startEdit: Function,
  saveEdit: Function,
  cancelEdit: Function,
  deleteComment: Function
})

const getFullImageUrl = (img) => {
  if (!img) return ''
  if (img.startsWith('http')) return img
  return `${API_BASE_URL}/static/${img}`
}

defineEmits(['update:replyToId', 'update:replyContent'])
</script>

<style scoped>
.comment-item {
  margin-bottom: 18px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.comment-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.comment-user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
}

.comment-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid rgba(236, 72, 153, 0.2);
}

.comment-default-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(236, 72, 153, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  border: 1px solid rgba(236, 72, 153, 0.2);
}
.child {
  background: #f8f9fa;
  border-radius: 6px;
  margin-top: 8px;
  padding: 10px 12px;
  border: 1px solid #f0f0f0;
}
.comment-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #888;
}
.comment-nickname {
  color: #d63384;
  font-weight: bold;
}
.comment-time {
  color: #aaa;
}
.comment-like, .comment-reply {
  cursor: pointer;
  color: #1976d2;
}
.comment-like:hover, .comment-reply:hover {
  text-decoration: underline;
}
.comment-like.liked {
  color: #ff6b9d;
  font-weight: bold;
}
.comment-edit, .comment-delete {
  cursor: pointer;
  color: #e57373;
  margin-left: 8px;
  font-size: 13px;
}
.comment-edit:hover, .comment-delete:hover {
  text-decoration: underline;
  color: #d63384;
}
.comment-content {
  margin: 6px 0 0 0;
  color: #333;
  font-size: 15px;
}
.reply-box {
  margin: 8px 0 0 0;
  display: flex;
  gap: 8px;
}
.comment-children {
  margin-left: 24px;
}
.comment-edit-area {
  margin-top: 6px;
  display: flex;
  gap: 8px;
  align-items: flex-start;
  padding: 10px;
  background: #fff6fa;
  border-radius: 8px;
}
/* 发行商标识（评论区头像右下角） */
.publisher-badge-comment {
  position: absolute;
  bottom: -2px;
  right: -2px;
  background: #ffeb3b;
  border: 2px solid white;
  border-radius: 50%;
  width: 12px;
  height: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}
.publisher-icon-comment {
  font-size: 7px;
  color: #333;
  line-height: 1;
}
</style> 
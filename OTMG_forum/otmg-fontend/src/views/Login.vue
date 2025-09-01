<template>
  <div class="login-container">
    <!-- 背景图片层 -->
    <div class="background-image"></div>
    
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="floating-heart heart-1">💕</div>
      <div class="floating-heart heart-2">💖</div>
      <div class="floating-heart heart-3">💝</div>
      <div class="floating-heart heart-4">💗</div>
      <div class="floating-heart heart-5">💓</div>
      <div class="floating-flower flower-1">🌸</div>
      <div class="floating-flower flower-2">🌺</div>
      <div class="floating-flower flower-3">🌷</div>
      <div class="floating-flower flower-4">🌹</div>
    </div>

    <!-- 登录框周围装饰 -->
    <div class="form-decoration">
      <div class="glow-orb orb-1"></div>
      <div class="glow-orb orb-2"></div>
      <div class="glow-orb orb-3"></div>
      <div class="floating-particle particle-1">✨</div>
      <div class="floating-particle particle-2">💫</div>
      <div class="floating-particle particle-3">⭐</div>
    </div>

    <div class="form-container">
    
      <!-- 登录表单 -->
      <el-form :model="loginForm" class="login-form" @keyup.enter="handleLogin" label-width="80px">
        <h2 class="form-title">
          ❤  欢迎回家  ❤
        </h2>
        <el-form-item label="用户名">
          <el-input 
            v-model="loginForm.username" 
            autocomplete="off"
            class="romantic-input"
            placeholder="请输入你的用户名"
          >
            <template #prefix>
              <span class="input-icon">👤</span>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            autocomplete="off"
            class="romantic-input"
            placeholder="请输入你的密码"
          >
            <template #prefix>
              <span class="input-icon">🔒</span>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleLogin" 
            :loading="loading" 
            class="login-btn"
          >
            登录
          </el-button>
        </el-form-item>
        
        <div class="register-link">
          <span class="register-text">还没有账号？</span>
          <el-button 
            type="text" 
            @click="showRegisterDialog = true"
            class="register-btn"
          >
            立即注册
          </el-button>
        </div>
        
        <el-alert v-if="errorMsg" :title="errorMsg" type="error" show-icon style="margin-top: 10px;" />
      </el-form>
    </div>

    <!-- 注册弹窗 -->
    <el-dialog
      v-model="showRegisterDialog"
      title=""
      width="420px"
      :show-close="true"
      class="register-dialog"
      :close-on-click-modal="false"
    >
      <el-form 
        :model="registerForm" 
        :rules="registerRules" 
        ref="registerFormRef" 
        class="register-form"
        @keyup.enter="handleRegister"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="registerForm.username" 
            autocomplete="off"
            class="romantic-input"
            placeholder="3-20个字符"
          >
            <template #prefix>
              <span class="input-icon">👤</span>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="registerForm.password" 
            type="password" 
            autocomplete="off"
            class="romantic-input"
            placeholder="至少6个字符"
          >
            <template #prefix>
              <span class="input-icon">🔒</span>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password" 
            autocomplete="off"
            class="romantic-input"
            placeholder="再次输入密码"
          >
            <template #prefix>
              <span class="input-icon">🔐</span>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input 
            v-model="registerForm.nickname" 
            autocomplete="off"
            class="romantic-input"
            placeholder="你的可爱昵称"
          >
            <template #prefix>
              <span class="input-icon">🎀</span>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="registerForm.email" 
            autocomplete="off"
            class="romantic-input"
            placeholder="your.email@example.com"
          >
            <template #prefix>
              <span class="input-icon">📧</span>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input 
            v-model="registerForm.phone" 
            autocomplete="off"
            class="romantic-input"
            placeholder="13800138000"
          >
            <template #prefix>
              <span class="input-icon">📱</span>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleRegister" 
            :loading="loading" 
            class="register-submit-btn"
          >
            注册
          </el-button>
        </el-form-item>
        <el-alert v-if="errorMsg" :title="errorMsg" type="error" show-icon style="margin-top: 10px;" />
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const showRegisterDialog = ref(false)
const loading = ref(false)
const errorMsg = ref('')

// 登录表单
const loginForm = ref({ username: '', password: '' })

// 注册表单
const registerForm = ref({ 
  username: '', 
  password: '', 
  confirmPassword: '', 
  nickname: '', 
  email: '', 
  phone: '' 
})

const registerFormRef = ref()


const handleLogin = async () => {
  errorMsg.value = ''
  if (!loginForm.value.username || !loginForm.value.password) {
    errorMsg.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  try {
    const res = await axios.post('http://localhost:5000/users/login', loginForm.value, { withCredentials: true })
    if (res.data.status === 'success') {
      localStorage.setItem('user', JSON.stringify(res.data))
      ElMessage.success('登录成功 ')
      if (res.data.role === 'admin') {
        router.push('/backstage/games')
      } else {
        router.push('/games-overview')
      }
    } else {
      errorMsg.value = res.data.message || '登录失败'
    }
  } catch (e) {
    errorMsg.value = e.response?.data?.message || '登录失败'
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  errorMsg.value = ''
  
  // 验证表单
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validate()
  } catch (error) {
    return
  }
  
  loading.value = true
  try {
    const registerData = {
      username: registerForm.value.username,
      password: registerForm.value.password,
      nickname: registerForm.value.nickname,
      email: registerForm.value.email,
      phone: registerForm.value.phone
    }
    
    const res = await axios.post('http://localhost:5000/users/register', registerData, { withCredentials: true })
    if (res.data.status === 'success') {
      localStorage.setItem('user', JSON.stringify(res.data))
      ElMessage.success('注册成功！欢迎加入')
      showRegisterDialog.value = false
      if (res.data.role === 'admin') {
        router.push('/backstage/games')
      } else {
        router.push('/games-overview')
      }
    } else {
      errorMsg.value = res.data.message || '注册失败'
    }
  } catch (e) {
    errorMsg.value = e.response?.data?.message || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  height: 100vh;
  background: #f5f5f5;
  position: relative;
  overflow: hidden;
  padding-left: 120px;
}

/* 背景图片层 */
.background-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(rgba(255, 182, 193, 0.2), rgba(255, 192, 203, 0.1)), 
              url('@/assets/login-bcg.png') center/cover no-repeat;
  opacity: 0.9;
  z-index: 0;
}

/* 背景装饰动画 */
.bg-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.floating-heart, .floating-flower {
  position: absolute;
  font-size: 24px;
  animation: float 6s ease-in-out infinite;
  opacity: 0.6;
}

.heart-1 { top: 10%; left: 10%; animation-delay: 0s; }
.heart-2 { top: 20%; right: 15%; animation-delay: 1s; }
.heart-3 { bottom: 30%; left: 20%; animation-delay: 2s; }
.heart-4 { bottom: 20%; right: 10%; animation-delay: 3s; }
.heart-5 { top: 50%; left: 5%; animation-delay: 4s; }

.flower-1 { top: 15%; left: 80%; animation-delay: 0.5s; }
.flower-2 { bottom: 40%; right: 25%; animation-delay: 1.5s; }
.flower-3 { top: 70%; right: 5%; animation-delay: 2.5s; }
.flower-4 { bottom: 10%; left: 70%; animation-delay: 3.5s; }

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(10deg); }
}

@keyframes gentleGlow {
  0% { 
    box-shadow: 
      0 8px 32px rgba(255, 182, 193, 0.3),
      0 0 60px rgba(255, 107, 157, 0.2),
      inset 0 1px 0 rgba(255, 255, 255, 0.4);
  }
}

@keyframes borderGlow {
  0% { 
    background: linear-gradient(45deg, 
      rgba(255, 107, 157, 0.3), 
      rgba(255, 182, 193, 0.2), 
      rgba(196, 69, 105, 0.3));
  }
}

@keyframes floatAround {
  0%, 100% { 
    transform: translateY(-50%) translateX(0px) scale(1);
    opacity: 0.6;
  }
}

.form-container {
  width: 480px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 25px;
  box-shadow: 
    0 8px 32px rgba(255, 182, 193, 0.3),
    0 0 60px rgba(255, 107, 157, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(25px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
  position: relative;
  z-index: 2;
  animation: gentleGlow 4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.form-container::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, 
    rgba(255, 107, 157, 0.3), 
    rgba(255, 182, 193, 0.2), 
    rgba(196, 69, 105, 0.3));
  border-radius: 27px;
  z-index: -1;
  animation: borderGlow 5s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.form-container::after {
  content: '';
  position: absolute;
  top: 50%;
  left: -30px;
  width: 20px;
  height: 20px;
  background: radial-gradient(circle, rgba(255, 107, 157, 0.6), transparent);
  border-radius: 50%;
  animation: floatAround 6s ease-in-out infinite;
  z-index: 1;
}

/* 登录框周围装饰 */
.form-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.glow-orb {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 107, 157, 0.4), transparent);
  animation: orbFloat 8s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.orb-1 {
  width: 40px;
  height: 40px;
  top: 20%;
  left: -20px;
  animation-delay: 0s;
}

.orb-2 {
  width: 30px;
  height: 30px;
  top: 60%;
  right: -15px;
  animation-delay: 2s;
}

.orb-3 {
  width: 25px;
  height: 25px;
  bottom: 20%;
  left: -10px;
  animation-delay: 4s;
}

.floating-particle {
  position: absolute;
  font-size: 16px;
  animation: particleFloat 6s cubic-bezier(0.4, 0, 0.2, 1) infinite;
  opacity: 0.7;
}

.particle-1 {
  top: 15%;
  right: -30px;
  animation-delay: 1s;
}

.particle-2 {
  top: 45%;
  left: -25px;
  animation-delay: 3s;
}

.particle-3 {
  bottom: 30%;
  right: -20px;
  animation-delay: 5s;
}

@keyframes orbFloat {
  0% { 
    transform: translateY(0px) scale(1);
    opacity: 0.4;
  }
  25% { 
    transform: translateY(-8px) scale(1.05);
    opacity: 0.5;
  }
  50% { 
    transform: translateY(-20px) scale(1.2);
    opacity: 0.7;
  }
  75% { 
    transform: translateY(-12px) scale(1.1);
    opacity: 0.6;
  }
  100% { 
    transform: translateY(0px) scale(1);
    opacity: 0.4;
  }
}

@keyframes particleFloat {
  0% { 
    transform: translateY(0px) rotate(0deg);
    opacity: 0.7;
  }
  20% { 
    transform: translateY(-8px) rotate(45deg);
    opacity: 0.8;
  }
  40% { 
    transform: translateY(-15px) rotate(90deg);
    opacity: 1;
  }
  60% { 
    transform: translateY(-10px) rotate(135deg);
    opacity: 0.9;
  }
  80% { 
    transform: translateY(-18px) rotate(225deg);
    opacity: 0.85;
  }
  100% { 
    transform: translateY(0px) rotate(360deg);
    opacity: 0.7;
  }
}

.form-header {
  background: linear-gradient(135deg, #ff6b9d, #c44569);
  padding: 30px;
  text-align: center;
  color: white;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 48px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.site-title {
  font-size: 28px;
  font-weight: bold;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.site-subtitle {
  font-size: 16px;
  margin: 0;
  opacity: 0.9;
}

.login-form {
  padding: 40px;
  padding-top: 60px;
}

.form-title {
  text-align: center;
  margin-bottom: 30px;
  color: #c44569;
  font-size: 24px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.title-icon {
  font-size: 20px;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.romantic-input :deep(.el-input__wrapper) {
  border-radius: 18px;
  border: 1px solid rgba(255, 182, 193, 0.6);
  background: rgba(255, 255, 255, 0.7);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.romantic-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(255, 107, 157, 0.8);
  box-shadow: 0 0 12px rgba(255, 107, 157, 0.2);
  background: rgba(255, 255, 255, 0.8);
}

.romantic-input :deep(.el-input__wrapper.is-focus) {
  border-color: rgba(196, 69, 105, 0.8);
  box-shadow: 0 0 16px rgba(196, 69, 105, 0.3);
  background: rgba(255, 255, 255, 0.9);
}

.input-icon {
  font-size: 16px;
  color: #ff6b9d;
}

.login-btn {
  width: 100%;
  height: 50px;
  border-radius: 25px;
  background: linear-gradient(135deg, rgba(255, 107, 157, 0.9), rgba(196, 69, 105, 0.9));
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 18px;
  font-weight: bold;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(255, 107, 157, 0.3);
  backdrop-filter: blur(10px);
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 107, 157, 0.4);
  background: linear-gradient(135deg, rgba(255, 107, 157, 1), rgba(196, 69, 105, 1));
}

.btn-icon {
  font-size: 16px;
  animation: heartBeat 1.5s ease-in-out infinite;
}

@keyframes heartBeat {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

.register-link {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ffb6c1;
}

.register-text {
  color: #666;
  font-size: 14px;
}

.register-btn {
  color: rgba(255, 107, 157, 0.9);
  font-weight: bold;
  font-size: 14px;
  margin-left: 5px;
  transition: all 0.3s ease;
  text-shadow: 0 1px 2px rgba(255, 107, 157, 0.3);
}

.register-btn:hover {
  color: rgba(196, 69, 105, 1);
  transform: scale(1.05);
  text-shadow: 0 2px 4px rgba(196, 69, 105, 0.4);
}

.sparkle {
  margin-left: 5px;
  animation: sparkle 1.5s ease-in-out infinite;
}

@keyframes sparkle {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.2); }
}

/* 注册弹窗样式 */
.register-dialog :deep(.el-dialog) {
  width: 420px !important;
  max-width: 95vw;
}

.register-dialog :deep(.el-dialog__header) {
  display: none !important;
  height: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
  border: none !important;
}

.register-dialog :deep(.el-dialog__title) {
  color: white;
}

.register-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: white;
  font-size: 20px;
}

.register-form {
  max-width: 340px;
  margin: 0 auto;
  padding: 16px 16px 32px 16px;
}

.register-form :deep(.el-form-item) {
  margin-top: 10px;
  margin-bottom: 0;
}

.register-form :deep(.el-form-item:first-child) {
  margin-top: 0;
}

.register-submit-btn {
  width: 100%;
  height: 50px;
  border-radius: 25px;
  background: linear-gradient(135deg, rgba(255, 107, 157, 0.9), rgba(196, 69, 105, 0.9));
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 18px;
  font-weight: bold;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(255, 107, 157, 0.3);
  backdrop-filter: blur(10px);
}

.register-submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 107, 157, 0.4);
  background: linear-gradient(135deg, rgba(255, 107, 157, 1), rgba(196, 69, 105, 1));
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    justify-content: center;
    padding-left: 20px;
    padding-right: 20px;
  }
  
  .form-container {
    width: 90%;
    max-width: 480px;
  }
}

@media (max-width: 480px) {
  .login-container {
    padding-left: 10px;
    padding-right: 10px;
  }
  
  .form-container {
    width: 95%;
  }
  
  .login-form {
    padding: 30px 20px;
  }
  
  .register-form {
    padding: 20px;
  }
  
  .site-title {
    font-size: 24px;
  }
  
  .form-title {
    font-size: 20px;
  }
}

.register-dialog :deep(.el-dialog__body) {
  padding-top: 10px !important;
}
</style>

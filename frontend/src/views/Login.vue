<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>智能面试提升系统</h2>
          <p>用户登录</p>
        </div>
      </template>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            style="width: 100%"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>

        <el-form-item>
          <div class="login-footer">
            <span>还没有账号？</span>
            <el-link type="primary" @click="goToRegister">立即注册</el-link>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        console.log('[Login] 开始登录请求')
        const success = await userStore.loginAction(loginForm)
        console.log('[Login] loginAction 返回结果:', success)
        console.log('[Login] 当前 token:', userStore.token)
        console.log('[Login] 当前 isLogin:', userStore.isLogin)
        if (success) {
          ElMessage.success('登录成功')
          console.log('[Login] 准备跳转到 /dashboard')
          await router.push('/dashboard')
          console.log('[Login] 跳转完成')
        } else {
          ElMessage.error('登录失败，请检查用户名或密码')
        }
      } catch (error) {
        console.error('登录失败:', error)
        ElMessage.error(error.response?.data?.detail || '登录失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }
  })
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-size: 200% 200%;
  animation: gradientShift 15s ease infinite;
  position: relative;
  overflow: hidden;
}

@keyframes gradientShift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

/* 背景装饰元素 */
.login-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.login-card {
  width: 400px;
  border-radius: var(--radius-xl);
  border: none;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  animation: cardEnter 0.6s ease-out;
  position: relative;
  z-index: 1;
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

:deep(.el-card__header) {
  padding: var(--spacing-xl) var(--spacing-xl) var(--spacing-lg);
  border-bottom: none;
  background: linear-gradient(180deg, rgba(102, 126, 234, 0.05) 0%, transparent 100%);
}

:deep(.el-card__body) {
  padding: var(--spacing-lg) var(--spacing-xl) var(--spacing-xl);
}

.card-header {
  text-align: center;
  position: relative;
}

.card-header::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 4px;
  background: linear-gradient(90deg, var(--primary-color), #764ba2);
  border-radius: var(--radius-round);
}

.card-header h2 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--text-primary);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  background: linear-gradient(135deg, var(--primary-color) 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.card-header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
}

/* 表单样式 */
:deep(.el-form) {
  padding: var(--spacing-md) 0;
}

:deep(.el-form-item) {
  margin-bottom: var(--spacing-lg);
}

:deep(.el-form-item:last-child) {
  margin-bottom: 0;
}

:deep(.el-form-item__label) {
  color: var(--text-regular);
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
}

:deep(.el-input__wrapper) {
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) var(--spacing-md);
  box-shadow: 0 0 0 1px var(--border-color-light) inset;
  transition: all var(--transition-fast);
  background: var(--bg-color-light);
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--primary-color-light) inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px var(--primary-color) inset;
  background: var(--card-bg);
}

:deep(.el-input__inner) {
  font-size: var(--font-size-base);
  color: var(--text-primary);
}

:deep(.el-input__prefix-inner) {
  color: var(--text-secondary);
}

/* 按钮样式 */
:deep(.el-button) {
  height: 44px;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  border-radius: var(--radius-md);
  border: none;
  background: linear-gradient(135deg, var(--primary-color) 0%, #764ba2 100%);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: all var(--transition-base);
}

:deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

:deep(.el-button:active) {
  transform: translateY(0);
}

:deep(.el-button.is-loading) {
  opacity: 0.8;
}

/* 底部链接 */
.login-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.login-footer span {
  color: var(--text-regular);
}

:deep(.el-link) {
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
}

:deep(.el-link__inner) {
  color: var(--primary-color);
}

:deep(.el-link:hover .el-link__inner) {
  color: var(--primary-dark);
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-card {
    width: 90%;
    margin: var(--spacing-md);
  }

  :deep(.el-card__header),
  :deep(.el-card__body) {
    padding: var(--spacing-lg);
  }

  .card-header h2 {
    font-size: var(--font-size-xl);
  }
}

/* 添加浮动动画 */
@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.login-card {
  animation: cardEnter 0.6s ease-out, float 6s ease-in-out infinite 0.6s;
}

/* 输入框图标动画 */
:deep(.el-input__prefix-inner .el-icon) {
  transition: transform var(--transition-fast);
}

:deep(.el-input__wrapper:focus-within .el-input__prefix-inner .el-icon) {
  transform: scale(1.2);
  color: var(--primary-color);
}
</style>
<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <h2>智能面试提升系统</h2>
          <p>用户注册</p>
        </div>
      </template>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱"
            prefix-icon="Message"
          />
        </el-form-item>

        <el-form-item label="姓名" prop="full_name">
          <el-input
            v-model="registerForm.full_name"
            placeholder="请输入姓名"
            prefix-icon="UserFilled"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            style="width: 100%"
            :loading="loading"
            @click="handleRegister"
          >
            注册
          </el-button>
        </el-form-item>

        <el-form-item>
          <div class="register-footer">
            <span>已有账号？</span>
            <el-link type="primary" @click="goToLogin">立即登录</el-link>
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

const registerFormRef = ref(null)
const loading = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
  full_name: '',
  password: '',
  confirmPassword: ''
})

const validatePassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validatePassword, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const { confirmPassword, ...data } = registerForm
        const success = await userStore.registerAction(data)
        if (success) {
          ElMessage.success('注册成功，请登录')
          router.push('/login')
        }
      } catch (error) {
        console.error('注册失败:', error)
      } finally {
        loading.value = false
      }
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-size: 200% 200%;
  animation: gradientShift 15s ease infinite;
  position: relative;
  overflow: hidden;
  padding: var(--spacing-md);
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
.register-container::before {
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

.register-card {
  width: 450px;
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
  margin-bottom: var(--spacing-md);
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
.register-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.register-footer span {
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
  .register-card {
    width: 100%;
    margin: 0;
  }

  :deep(.el-card__header),
  :deep(.el-card__body) {
    padding: var(--spacing-lg);
  }

  .card-header h2 {
    font-size: var(--font-size-xl);
  }

  :deep(.el-form-item) {
    margin-bottom: var(--spacing-sm);
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

.register-card {
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

/* 滚动条样式 */
:deep(.el-card__body)::-webkit-scrollbar {
  width: 6px;
}

:deep(.el-card__body)::-webkit-scrollbar-track {
  background: var(--bg-color-light);
  border-radius: var(--radius-round);
}

:deep(.el-card__body)::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: var(--radius-round);
}

:deep(.el-card__body)::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}
</style>
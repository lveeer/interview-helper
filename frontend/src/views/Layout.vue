<template>
  <el-container class="layout-container">
    <!-- 移动端遮罩层 -->
    <div
      v-if="isMobileMenuOpen"
      class="mobile-overlay"
      @click="closeMobileMenu"
    ></div>

    <!-- 侧边栏 -->
    <el-aside
      width="220px"
      :class="{ 'mobile-open': isMobileMenuOpen }"
    >
      <div class="logo">
        <svg class="logo-icon" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#409EFF;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#667EEA;stop-opacity:1" />
            </linearGradient>
            <linearGradient id="logoGradient2" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#667EEA;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#764BA2;stop-opacity:1" />
            </linearGradient>
          </defs>
          <!-- 外圆环 -->
          <circle cx="32" cy="32" r="28" stroke="url(#logoGradient)" stroke-width="2" fill="none" opacity="0.3"/>
          <circle cx="32" cy="32" r="24" stroke="url(#logoGradient)" stroke-width="1.5" fill="none" opacity="0.5"/>
          <!-- 中心图标 - 智能AI -->
          <circle cx="32" cy="32" r="16" fill="url(#logoGradient)"/>
          <!-- AI芯片图案 -->
          <rect x="26" y="26" width="12" height="12" rx="2" fill="white" opacity="0.9"/>
          <circle cx="29" cy="29" r="1.5" fill="#409EFF"/>
          <circle cx="35" cy="29" r="1.5" fill="#409EFF"/>
          <path d="M29 34 Q32 36 35 34" stroke="#409EFF" stroke-width="1.5" stroke-linecap="round" fill="none"/>
          <!-- 连接线 -->
          <line x1="32" y1="16" x2="32" y2="10" stroke="url(#logoGradient2)" stroke-width="2" stroke-linecap="round"/>
          <line x1="32" y1="48" x2="32" y2="54" stroke="url(#logoGradient2)" stroke-width="2" stroke-linecap="round"/>
          <line x1="16" y1="32" x2="10" y2="32" stroke="url(#logoGradient2)" stroke-width="2" stroke-linecap="round"/>
          <line x1="48" y1="32" x2="54" y2="32" stroke="url(#logoGradient2)" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <div class="logo-text">
          <span class="logo-title">智能面试提升系统</span>
          <span class="logo-subtitle">AI</span>
        </div>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        @select="closeMobileMenu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/resume">
          <el-icon><Document /></el-icon>
          <span>简历管理</span>
        </el-menu-item>
        <el-menu-item index="/job-match">
          <el-icon><TrendCharts /></el-icon>
          <span>岗位匹配</span>
        </el-menu-item>
        <el-menu-item index="/interview">
          <el-icon><ChatDotRound /></el-icon>
          <span>模拟面试</span>
        </el-menu-item>
        <el-menu-item index="/knowledge">
          <el-icon><Reading /></el-icon>
          <span>知识库</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container class="main-container">
      <el-header>
        <div class="header-content">
          <!-- 汉堡菜单按钮（移动端） -->
          <div class="hamburger" @click="toggleMobileMenu">
            <el-icon><Menu /></el-icon>
          </div>

          <div class="breadcrumb">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item v-if="currentRoute.meta.title">
                {{ currentRoute.meta.title }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>

          <div class="user-info">
            <el-dropdown @command="handleCommand">
              <span class="el-dropdown-link">
                <el-icon><User /></el-icon>
                {{ userStore.username }}
                <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>

      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 移动端菜单状态
const isMobileMenuOpen = ref(false)
const isMobile = ref(false)

// 检测是否为移动端
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

// 切换移动端菜单
const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

// 关闭移动端菜单
const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

// 监听窗口大小变化
const handleResize = () => {
  checkMobile()
  if (!isMobile.value) {
    isMobileMenuOpen.value = false
  }
}

const activeMenu = computed(() => route.path)
const currentRoute = computed(() => route)

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch {
      // 用户取消
    }
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏样式 */
.el-aside {
  background: linear-gradient(180deg, var(--sidebar-bg) 0%, var(--sidebar-bg-dark) 100%);
  overflow-x: hidden;
  transition: all var(--transition-base);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: var(--z-index-sticky);
}

/* 主容器样式 */
.main-container {
  margin-left: 20px;
}

/* Logo区域 */
.logo {
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e293b 0%, #304156 50%, #1e293b 100%);
  border-bottom: 1px solid rgba(64, 158, 255, 0.3);
  position: relative;
  overflow: hidden;
  padding: 0 var(--spacing-md);
  gap: var(--spacing-md);
}

.logo::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg,
    rgba(64, 158, 255, 0.25) 0%,
    rgba(102, 126, 234, 0.2) 25%,
    rgba(118, 75, 162, 0.25) 50%,
    rgba(102, 126, 234, 0.2) 75%,
    rgba(64, 158, 255, 0.25) 100%);
  opacity: 1;
  transition: opacity var(--transition-base);
  animation: gradientShift 6s ease-in-out infinite;
}

.logo:hover::before {
  opacity: 0.85;
}

@keyframes gradientShift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.logo-icon {
  width: 36px;
  height: 36px;
  position: relative;
  z-index: 1;
  filter: drop-shadow(0 2px 4px rgba(64, 158, 255, 0.3));
  transition: transform var(--transition-base);
}

.logo:hover .logo-icon {
  transform: scale(1.1) rotate(5deg);
}

.logo-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  position: relative;
  z-index: 1;
  line-height: 1.2;
}

.logo-title {
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 1.5px;
  background: linear-gradient(135deg, #ffffff 0%, #e8f4ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-subtitle {
  font-size: 14px;
  font-weight: 700;
  color: #409EFF;
  letter-spacing: 4px;
  margin-top: 4px;
}

/* 菜单样式 */
:deep(.el-menu) {
  border: none;
  background: transparent;
}

:deep(.el-menu-item) {
  margin: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
  color: var(--sidebar-text);
  position: relative;
  overflow: hidden;
}

:deep(.el-menu-item::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 0;
  background: var(--primary-color);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  transition: height var(--transition-base);
}

:deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.1);
  color: var(--sidebar-text-hover);
  transform: translateX(4px);
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(64, 158, 255, 0.2) 0%, transparent 100%);
  color: var(--primary-color);
  font-weight: var(--font-weight-medium);
}

:deep(.el-menu-item.is-active::before) {
  height: 70%;
}

:deep(.el-menu-item .el-icon) {
  font-size: 18px;
  transition: transform var(--transition-base);
}

:deep(.el-menu-item:hover .el-icon) {
  transform: scale(1.1);
}

:deep(.el-menu-item span) {
  margin-left: var(--spacing-sm);
}

/* 头部样式 */
.el-header {
  background: var(--header-bg);
  border-bottom: 1px solid var(--header-border);
  display: flex;
  align-items: center;
  padding: 0 var(--spacing-lg);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: var(--z-index-sticky);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

/* 面包屑样式 */
.breadcrumb {
  flex: 1;
}

:deep(.el-breadcrumb) {
  font-size: var(--font-size-sm);
}

:deep(.el-breadcrumb__item) {
  display: flex;
  align-items: center;
}

:deep(.el-breadcrumb__inner) {
  color: var(--text-secondary);
  font-weight: var(--font-weight-normal);
  transition: color var(--transition-fast);
}

:deep(.el-breadcrumb__inner:hover) {
  color: var(--primary-color);
}

:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: var(--text-primary);
  font-weight: var(--font-weight-medium);
}

:deep(.el-breadcrumb__separator) {
  color: var(--text-placeholder);
  margin: 0 var(--spacing-xs);
}

/* 用户信息区域 */
.user-info {
  cursor: pointer;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  margin-left: var(--spacing-lg);
}

.user-info:hover {
  background: var(--bg-color);
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--text-primary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  transition: color var(--transition-fast);
}

.el-dropdown-link:hover {
  color: var(--primary-color);
}

.el-dropdown-link .el-icon:first-child {
  font-size: 20px;
  color: var(--primary-color);
}

.el-dropdown-link .el-icon--right {
  font-size: 14px;
  color: var(--text-secondary);
  transition: transform var(--transition-fast);
}

.user-info:hover .el-dropdown-link .el-icon--right {
  transform: rotate(180deg);
}

/* 下拉菜单样式 */
:deep(.el-dropdown-menu) {
  border: 1px solid var(--border-color-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: var(--spacing-xs);
}

:deep(.el-dropdown-menu__item) {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  color: var(--text-regular);
}

:deep(.el-dropdown-menu__item:hover) {
  background: var(--bg-color);
  color: var(--primary-color);
  transform: translateX(2px);
}

/* 主内容区域 */
.el-main {
  background: var(--bg-color);
  padding: var(--spacing-lg) var(--spacing-xl);
  overflow-y: auto;
  position: relative;
  min-height: calc(100vh - var(--header-height));
}

/* 确保主内容区的第一个元素有上边距 */
.el-main > *:first-child {
  margin-top: 0;
}

/* 确保主内容区的最后一个元素有下边距 */
.el-main > *:last-child {
  margin-bottom: 0;
}

/* 滚动条样式优化 */
.el-main::-webkit-scrollbar {
  width: 6px;
}

.el-main::-webkit-scrollbar-track {
  background: transparent;
}

.el-main::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: var(--radius-round);
}

.el-main::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .el-aside {
    position: fixed;
    left: -220px;
    top: 0;
    bottom: 0;
    z-index: var(--z-index-modal);
  }

  .el-aside.mobile-open {
    left: 0;
  }

  .el-header {
    padding: 0 var(--spacing-md);
  }

  .logo-title {
    font-size: 13px;
  }

  .logo-subtitle {
    font-size: 9px;
  }

  .logo-icon {
    width: 32px;
    height: 32px;
  }

  .el-dropdown-link span {
    display: none;
  }

  .el-main {
    padding: var(--spacing-md);
  }
}

/* 移动端遮罩层 */
.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--bg-color-overlay);
  z-index: var(--z-index-modal-backdrop);
  opacity: 0;
  visibility: hidden;
  transition: all var(--transition-base);
}

.mobile-overlay.show {
  opacity: 1;
  visibility: visible;
}

/* 汉堡菜单按钮（移动端） */
.hamburger {
  display: none;
  cursor: pointer;
  padding: var(--spacing-sm);
  margin-right: var(--spacing-md);
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}

.hamburger:hover {
  background: var(--bg-color);
}

.hamburger .el-icon {
  font-size: 24px;
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .hamburger {
    display: flex;
    align-items: center;
  }
}

/* 页面过渡动画 */
.page-enter-active,
.page-leave-active {
  transition: all var(--transition-base);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
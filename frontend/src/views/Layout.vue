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
        background-color="#ffffff"
        text-color="#606266"
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
        <el-menu-item index="/resume-optimize">
          <el-icon><MagicStick /></el-icon>
          <span>简历优化</span>
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
        <el-menu-item index="/llm-config">
          <el-icon><Setting /></el-icon>
          <span>LLM 配置</span>
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

          <div class="header-right">
            <!-- 黑暗模式切换 -->
            <div class="theme-toggle">
              <el-tooltip :content="themeStore.isDark ? '切换到亮色模式' : '切换到黑暗模式'" placement="bottom">
                <el-button
                  type="text"
                  @click="themeStore.toggleTheme"
                  class="theme-btn"
                >
                  <el-icon>
                    <Sunny v-if="themeStore.isDark" />
                    <Moon v-else />
                  </el-icon>
                </el-button>
              </el-tooltip>
            </div>

            <!-- 通知铃铛 -->
            <div class="notification-wrapper">
              <el-badge :value="unreadCount" :hidden="unreadCount === 0" :max="99">
                <el-button
                  type="text"
                  :icon="Bell"
                  @click="drawerVisible = true"
                  class="notification-btn"
                >
                  通知
                </el-button>
              </el-badge>
            </div>

            <!-- 用户信息 -->
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
        </div>
      </el-header>

      <el-main>
        <router-view />
      </el-main>
    </el-container>

    <!-- 通知抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      title="通知历史"
      size="480px"
      :destroy-on-close="true"
    >
      <template #header>
        <div class="drawer-header">
          <span class="drawer-title">通知历史</span>
          <el-button
            type="primary"
            link
            @click="handleMarkAllAsRead"
            :disabled="unreadCount === 0"
          >
            全部标为已读
          </el-button>
        </div>
      </template>

      <div v-if="historyNotifications.length === 0" class="empty-notifications">
        <el-empty description="暂无通知" />
      </div>

      <div v-else class="notifications-list">
        <div
          v-for="item in historyNotifications"
          :key="item.id"
          class="notification-item"
          :class="{ unread: item.status !== 'read' }"
          @click="handleNotificationClick(item)"
        >
          <div class="notification-content">
            <div class="notification-header">
              <el-tag :type="getNotificationTypeColor(item.notification_type)" size="small">
                {{ getTaskTypeName(item.task_type) }}
              </el-tag>
              <span class="notification-time">
                {{ formatTime(item.created_at) }}
              </span>
            </div>
            <div class="notification-title">{{ item.task_title }}</div>
            <div class="notification-message">{{ item.message }}</div>
            <div v-if="item.error" class="notification-error">{{ item.error }}</div>
          </div>
          <div class="notification-actions">
            <el-button
              v-if="item.redirect_url"
              type="primary"
              link
              size="small"
              @click.stop="handleRedirect(item)"
            >
              查看
            </el-button>
            <el-button
              type="danger"
              link
              size="small"
              @click.stop="handleDeleteNotification(item.id)"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>
    </el-drawer>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  HomeFilled,
  Document,
  MagicStick,
  TrendCharts,
  ChatDotRound,
  Reading,
  Setting,
  Menu,
  User,
  ArrowDown,
  Bell,
  Sunny,
  Moon
} from '@element-plus/icons-vue'
import notificationManager from '@/utils/notification'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()

// 移动端菜单状态
const isMobileMenuOpen = ref(false)
const isMobile = ref(false)

// 通知相关状态
const drawerVisible = ref(false)
const unreadCount = ref(0)
const historyNotifications = ref([])

// 初始化通知管理器
const initNotifications = () => {
  if (!userStore.isLogin || !userStore.userInfo?.id) {
    return
  }

  console.log('[Layout] 初始化通知系统')

  // 设置 router 实例
  notificationManager.setRouter(router)

  // 连接 WebSocket
  notificationManager.connect(userStore.userInfo.id, userStore.token)

  // 注册事件监听器
  notificationManager.on('history_loaded', (notifications) => {
    historyNotifications.value = notifications
    unreadCount.value = notificationManager.unreadCount
  })

  notificationManager.on('notification_updated', (notifications) => {
    historyNotifications.value = notifications
    unreadCount.value = notificationManager.unreadCount
  })

  notificationManager.on('unread_count_updated', (count) => {
    unreadCount.value = count
  })

  notificationManager.on('task_status', (data) => {
    if (data.status === 'completed' || data.status === 'failed') {
      loadHistoryNotifications()
    }
  })

  // 加载历史通知
  loadHistoryNotifications()
}

// 加载历史通知
const loadHistoryNotifications = async () => {
  await notificationManager.loadHistoryNotifications(userStore.token)
  historyNotifications.value = notificationManager.historyNotifications
  unreadCount.value = notificationManager.unreadCount
}

// 标记通知为已读
const handleMarkAsRead = async (notificationId) => {
  await notificationManager.markAsRead(notificationId, userStore.token)
  loadHistoryNotifications()
}

// 标记所有通知为已读
const handleMarkAllAsRead = async () => {
  await notificationManager.markAllAsRead(userStore.token)
  loadHistoryNotifications()
}

// 删除通知
const handleDeleteNotification = async (notificationId) => {
  try {
    await ElMessageBox.confirm('确定要删除这条通知吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await notificationManager.deleteNotification(notificationId, userStore.token)
    loadHistoryNotifications()
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

// 处理跳转
const handleRedirect = (item) => {
  if (item.redirect_url) {
    handleMarkAsRead(item.id)
    // 使用 Vue Router 跳转，避免页面重新加载
    if (item.redirect_url.startsWith('http')) {
      // 外部链接才使用 window.location.href
      window.location.href = item.redirect_url
    } else {
      // 内部路由使用 router.push
      router.push(item.redirect_url)
    }
  }
}

// 点击通知项
const handleNotificationClick = (item) => {
  if (item.status !== 'read') {
    handleMarkAsRead(item.id)
  }
}

// 获取通知类型颜色
const getNotificationTypeColor = (type) => {
  return notificationManager.getNotificationTypeColor(type)
}

// 获取任务类型名称
const getTaskTypeName = (type) => {
  return notificationManager.getTaskTypeName(type)
}

// 格式化时间
const formatTime = (time) => {
  return new Date(time).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

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
      notificationManager.disconnect()
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
  initNotifications()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  notificationManager.disconnect()
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏样式 */
.el-aside {
  background: var(--bg-color-white);
  overflow-x: hidden;
  transition: all var(--transition-base);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: var(--z-index-sticky);
  border-right: 1px solid var(--border-color-light);
}

/* 主容器样式 */
.main-container {
}

/* Logo区域 */
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #ffffff 100%);
  border-bottom: 1px solid var(--border-color-light);
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
  color: var(--text-primary);
  letter-spacing: 1px;
  background: linear-gradient(135deg, var(--text-primary) 0%, var(--primary-color) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
}

.logo-subtitle {
  font-size: 14px;
  font-weight: 700;
  color: var(--primary-color);
  letter-spacing: 4px;
  margin-top: 4px;
}

/* 菜单样式 */
:deep(.el-menu) {
  border: none;
  background: transparent;
}

:deep(.el-menu-item) {
  margin: 0;
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
  color: var(--text-primary);
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
  background: rgba(64, 158, 255, 0.1);
  color: var(--primary-color);
  transform: translateX(4px);
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(64, 158, 255, 0.15) 0%, transparent 100%);
  color: var(--primary-color);
  font-weight: var(--font-weight-medium);
}

:deep(.el-menu-item.is-active::before) {
  height: 70%;
}

:deep(.el-menu-item.is-active .el-icon) {
  color: var(--primary-color);
}

:deep(.el-menu-item:hover .el-icon) {
  transform: scale(1.1);
  color: var(--primary-color);
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

/* 通知相关样式 */
.header-right {
  display: flex;
  align-items: center;
  gap: 25px;
}

/* 黑暗模式切换按钮 */
.theme-toggle {
  display: flex;
  align-items: center;
}

.theme-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  color: var(--text-primary);
  transition: all var(--transition-fast);
}

.theme-btn:hover {
  background: var(--bg-color);
  color: var(--primary-color);
  transform: rotate(15deg);
}

.theme-btn .el-icon {
  font-size: 20px;
  transition: transform var(--transition-base);
}

.notification-wrapper {
  display: flex;
  align-items: center;
  position: relative;
}

.notification-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  color: var(--text-primary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-fast);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-md);
}

.notification-btn:hover {
  color: var(--primary-color);
  background: var(--bg-color);
}

.notification-btn .el-icon {
  font-size: 20px;
}

:deep(.el-badge__content) {
  transform: translateY(-50%) translateX(50%);
  box-shadow: var(--shadow-sm);
}

/* 抽屉样式 */
.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--border-color-light);
  margin-bottom: var(--spacing-md);
}

.drawer-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.drawer-header .el-button {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  padding: var(--spacing-xs) var(--spacing-sm);
}

.drawer-header .el-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-notifications {
  padding: var(--spacing-xxl) 0;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.empty-notifications :deep(.el-empty) {
  padding: 0;
}

.empty-notifications :deep(.el-empty__image) {
  width: 120px;
  height: 120px;
}

.empty-notifications :deep(.el-empty__description) {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-md);
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 4px 0;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.notifications-list::-webkit-scrollbar {
  width: 6px;
}

.notifications-list::-webkit-scrollbar-track {
  background: transparent;
}

.notifications-list::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: var(--radius-round);
  transition: background var(--transition-fast);
}

.notifications-list::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

.notification-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px;
  background: var(--bg-color-white);
  border: 1px solid var(--border-color-light);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  gap: 12px;
  box-shadow: var(--shadow-xs);
}

.notification-item.unread {
  background: linear-gradient(135deg, #f0f7ff 0%, #e8f4ff 100%);
  border-left: 3px solid var(--primary-color);
  border-color: var(--primary-color);
  box-shadow: var(--shadow-sm);
}

.notification-item:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
  border-color: var(--primary-color);
}

.notification-content {
  flex: 1;
  min-width: 0;
  padding-right: 8px;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  flex-wrap: wrap;
  gap: 6px;
}

.notification-header :deep(.el-tag) {
  font-weight: var(--font-weight-medium);
  border: none;
  padding: 2px 8px;
  height: 22px;
  line-height: 1;
}

.notification-time {
  font-size: var(--font-size-xs);
  color: var(--text-placeholder);
  white-space: nowrap;
  padding-left: 8px;
}

.notification-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
  margin-bottom: 12px;
  word-break: break-word;
  line-height: 1.5;
}

.notification-item.unread .notification-title {
  font-weight: var(--font-weight-semibold);
  color: var(--primary-color);
}

.notification-message {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-bottom: 0;
  line-height: 1.6;
  word-break: break-word;
  padding-top: 4px;
}

.notification-error {
  font-size: var(--font-size-sm);
  color: var(--color-danger);
  margin-top: var(--spacing-sm);
  padding: var(--spacing-sm);
  background: rgba(245, 108, 108, 0.1);
  border: 1px solid rgba(245, 108, 108, 0.2);
  border-radius: var(--radius-sm);
  line-height: 1.5;
}

.notification-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-left: 8px;
  flex-shrink: 0;
  align-items: flex-end;
}

.notification-actions .el-button {
  min-width: 60px;
  text-align: right;
  padding: 4px 8px;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-fast);
  height: auto;
  line-height: 1.4;
}

.notification-actions .el-button:hover {
  transform: scale(1.05);
}

/* 抽屉内部滚动条 */
:deep(.el-drawer__body) {
  padding: var(--spacing-lg);
  overflow-y: auto;
}

:deep(.el-drawer__body)::-webkit-scrollbar {
  width: 6px;
}

:deep(.el-drawer__body)::-webkit-scrollbar-track {
  background: transparent;
}

:deep(.el-drawer__body)::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: var(--radius-round);
  transition: background var(--transition-fast);
}

:deep(.el-drawer__body)::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* 抽屉头部样式优化 */
:deep(.el-drawer__header) {
  margin-bottom: 0;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--border-color-light);
}

:deep(.el-drawer__title) {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

/* 抽屉整体样式 */
:deep(.el-drawer) {
  border-radius: 0;
}

:deep(.el-drawer__header) {
  margin-bottom: 0;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--border-color-light);
  background: var(--bg-color-white);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-right {
    gap: var(--spacing-sm);
  }

  .notification-btn span {
    display: none;
  }

  .notification-btn .el-icon {
    font-size: 20px;
  }

  :deep(.el-drawer) {
    width: 100% !important;
  }

  :deep(.el-drawer__body) {
    padding: var(--spacing-md);
  }

  .notification-item {
    flex-direction: column;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
  }

  .notification-content {
    padding-right: 0;
    width: 100%;
  }

  .notification-header {
    align-items: flex-start;
  }

  .notification-actions {
    flex-direction: row;
    margin-left: 0;
    width: 100%;
    align-items: center;
    justify-content: flex-end;
    padding-top: var(--spacing-sm);
    border-top: 1px solid var(--border-color-light);
    gap: var(--spacing-sm);
  }

  .notification-actions .el-button {
    flex: 0 0 auto;
    padding: var(--spacing-xs) var(--spacing-md);
  }

  .notifications-list {
    max-height: calc(100vh - 250px);
  }
}
</style>
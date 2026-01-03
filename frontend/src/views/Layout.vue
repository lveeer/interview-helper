<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <div class="logo">
        <h3>智能面试系统</h3>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
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

    <el-container>
      <el-header>
        <div class="header-content">
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
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

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
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-aside {
  background-color: #304156;
  overflow-x: hidden;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  background-color: #2b2f3a;
  color: #fff;
}

.logo h3 {
  margin: 0;
  font-size: 18px;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.breadcrumb {
  flex: 1;
}

.user-info {
  cursor: pointer;
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  gap: 5px;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
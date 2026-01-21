import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页' }
      },
      {
        path: '/resume',
        name: 'Resume',
        component: () => import('@/views/Resume.vue'),
        meta: { title: '简历管理' }
      },
      {
        path: '/resume-optimize',
        name: 'ResumeOptimize',
        component: () => import('@/views/ResumeOptimize.vue'),
        meta: { title: '简历优化' }
      },
      {
        path: '/job-match',
        name: 'JobMatch',
        component: () => import('@/views/JobMatch.vue'),
        meta: { title: '岗位匹配' }
      },
      {
        path: '/interview',
        name: 'Interview',
        component: () => import('@/views/Interview.vue'),
        meta: { title: '模拟面试' }
      },
      {
        path: '/interview/:id',
        name: 'InterviewRoom',
        component: () => import('@/views/InterviewRoom.vue'),
        meta: { title: '面试房间' }
      },
      {
        path: '/knowledge',
        name: 'Knowledge',
        component: () => import('@/views/Knowledge.vue'),
        meta: { title: '知识库' }
      },
      {
        path: '/report/:id',
        name: 'Report',
        component: () => import('@/views/Report.vue'),
        meta: { title: '评估报告' }
      },
      {
        path: '/interview-record/:id',
        name: 'InterviewRecord',
        component: () => import('@/views/InterviewRecord.vue'),
        meta: { title: '面试对话记录' }
      },
      {
        path: '/llm-config',
        name: 'LLMConfig',
        component: () => import('@/views/LLMConfig.vue'),
        meta: { title: 'LLM 配置' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  // 设置页面标题
  document.title = to.meta.title || '智能面试提升系统'

  // 检查是否需要登录
  if (to.meta.requiresAuth && !userStore.isLogin) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && userStore.isLogin) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
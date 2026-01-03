import { defineStore } from 'pinia'
import { login, register, getUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('user') || 'null')
  }),

  getters: {
    isLogin: (state) => !!state.token,
    username: (state) => state.userInfo?.username || '',
    email: (state) => state.userInfo?.email || ''
  },

  actions: {
    // 登录
    async loginAction(loginForm) {
      console.log('[UserStore] 开始登录')
      const formData = new URLSearchParams()
      formData.append('username', loginForm.username)
      formData.append('password', loginForm.password)

      const res = await login(formData)
      console.log('[UserStore] 登录响应:', res)
      if (res.code === 200) {
        this.token = res.data.access_token
        localStorage.setItem('token', res.data.access_token)
        console.log('[UserStore] Token 已保存:', this.token)
        // 尝试获取用户信息，但不影响登录结果
        try {
          console.log('[UserStore] 开始获取用户信息')
          await this.getUserInfoAction()
          console.log('[UserStore] 用户信息获取成功')
        } catch (error) {
          console.error('[UserStore] 获取用户信息失败:', error)
        }
        console.log('[UserStore] 登录成功，返回 true')
        return true
      }
      console.log('[UserStore] 登录失败，返回 false')
      return false
    },

    // 注册
    async registerAction(registerForm) {
      const res = await register(registerForm)
      if (res.code === 201) {
        this.userInfo = res.data
        localStorage.setItem('user', JSON.stringify(res.data))
        return true
      }
      return false
    },

    // 获取用户信息
    async getUserInfoAction() {
      const res = await getUserInfo()
      if (res.code === 200) {
        this.userInfo = res.data
        localStorage.setItem('user', JSON.stringify(res.data))
        return true
      }
      return false
    },

    // 登出
    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
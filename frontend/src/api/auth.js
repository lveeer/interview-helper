import request from '@/utils/request'

// 用户注册
export const register = (data) => {
  return request({
    url: '/auth/register',
    method: 'post',
    data
  })
}

// 用户登录
export const login = (data) => {
  return request({
    url: '/auth/login',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

// 获取当前用户信息
export const getUserInfo = () => {
  return request({
    url: '/auth/me',
    method: 'get'
  })
}
import request from '@/utils/request'

// 开始游戏
export const startGame = (data) => {
  return request({
    url: '/game/resume-finder/start',
    method: 'post',
    data
  })
}

// 提交答案
export const submitAnswer = (data) => {
  return request({
    url: '/game/resume-finder/submit',
    method: 'post',
    data
  })
}

// 使用提示
export const useHint = (data) => {
  return request({
    url: '/game/resume-finder/hint',
    method: 'post',
    data
  })
}

// 完成游戏
export const completeGame = (data) => {
  return request({
    url: '/game/resume-finder/complete',
    method: 'post',
    data
  })
}

// 获取用户统计
export const getUserStats = () => {
  return request({
    url: '/game/resume-finder/stats',
    method: 'get'
  })
}

// 获取排行榜
export const getLeaderboard = (params) => {
  return request({
    url: '/game/resume-finder/leaderboard',
    method: 'get',
    params
  })
}

// 获取成就列表
export const getAchievements = () => {
  return request({
    url: '/game/resume-finder/achievements',
    method: 'get'
  })
}

// 获取错误类型列表
export const getErrorTypes = () => {
  return request({
    url: '/game/resume-finder/error-types',
    method: 'get'
  })
}
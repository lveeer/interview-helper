import request from '@/utils/request'

// 创建面试
export const createInterview = (data) => {
  return request({
    url: '/interview/create',
    method: 'post',
    data,
    timeout: 30000 // 30秒超时
  })
}

// 获取面试列表
export const getInterviewList = () => {
  return request({
    url: '/interview',
    method: 'get'
  })
}

// 获取面试详情
export const getInterviewDetail = (id) => {
  return request({
    url: `/interview/${id}`,
    method: 'get'
  })
}

// 获取面试对话记录
export const getInterviewRecord = (id) => {
  return request({
    url: `/interview/${id}/record`,
    method: 'get'
  })
}
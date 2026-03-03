import request from '@/utils/request'

// ===== 岗位管理 API =====

// 创建岗位
export const createJob = (data) => {
  return request({
    url: '/jobs',
    method: 'post',
    data
  })
}

// 获取岗位列表
export const getJobList = () => {
  return request({
    url: '/jobs',
    method: 'get'
  })
}

// 获取岗位详情
export const getJobDetail = (id) => {
  return request({
    url: `/jobs/${id}`,
    method: 'get'
  })
}

// 更新岗位
export const updateJob = (id, data) => {
  return request({
    url: `/jobs/${id}`,
    method: 'put',
    data
  })
}

// 删除岗位
export const deleteJob = (id) => {
  return request({
    url: `/jobs/${id}`,
    method: 'delete'
  })
}

// ===== 岗位面试关联 API =====

// 针对岗位创建面试
export const createJobInterview = (jobId, data) => {
  return request({
    url: `/jobs/${jobId}/interviews`,
    method: 'post',
    data,
    timeout: 30000
  })
}

// 获取岗位的历史面试记录
export const getJobInterviews = (jobId) => {
  return request({
    url: `/jobs/${jobId}/interviews`,
    method: 'get'
  })
}

// ===== 岗位匹配 API（原有功能）=====

// 岗位匹配分析
export const matchJob = (data) => {
  return request({
    url: '/jobs/match',
    method: 'post',
    data
  })
}

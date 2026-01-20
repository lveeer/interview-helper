import request from '@/utils/request'

// 上传简历
export const uploadResume = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/resume/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取简历列表
export const getResumeList = () => {
  return request({
    url: '/resume',
    method: 'get'
  })
}

// 获取简历详情
export const getResumeDetail = (id) => {
  return request({
    url: `/resume/${id}`,
    method: 'get'
  })
}

// 删除简历
export const deleteResume = (id) => {
  return request({
    url: `/resume/${id}`,
    method: 'delete'
  })
}

// 分析简历
export const analyzeResume = (id, jd = null, forceRefresh = false) => {
  const params = {}
  if (jd) params.jd = jd
  if (forceRefresh) params.force_refresh = true

  return request({
    url: `/resume/${id}/analyze`,
    method: 'post',
    params: Object.keys(params).length > 0 ? params : undefined,
    timeout: 45000
  })
}

// 获取优化建议
export const getOptimizationSuggestions = (id, jd = null, forceRefresh = false) => {
  const params = {}
  if (jd) params.jd = jd
  if (forceRefresh) params.force_refresh = true

  return request({
    url: `/resume/${id}/suggestions`,
    method: 'get',
    params: Object.keys(params).length > 0 ? params : undefined
  })
}

// 应用优化建议
export const applyOptimization = (id, suggestions) => {
  return request({
    url: `/resume/${id}/optimize`,
    method: 'post',
    data: { suggestions }
  })
}

// 获取优化历史
export const getOptimizationHistory = (id) => {
  return request({
    url: `/resume/${id}/optimization-history`,
    method: 'get'
  })
}

// 导出优化后的简历
export const exportOptimizedResume = (id, format = 'pdf') => {
  return request({
    url: `/resume/${id}/export`,
    method: 'get',
    params: { format },
    responseType: 'blob'
  })
}

// 比较简历版本
export const compareResumeVersions = (id, version1, version2) => {
  return request({
    url: `/resume/${id}/compare`,
    method: 'get',
    params: { version1, version2 }
  })
}

// 恢复到历史版本
export const restoreResumeVersion = (id, version) => {
  return request({
    url: `/resume/${id}/restore`,
    method: 'post',
    data: { version }
  })
}

// 重新解析简历
export const reparseResume = (id) => {
  return request({
    url: `/resume/${id}/reparse`,
    method: 'post',
    timeout: 60000
  })
}
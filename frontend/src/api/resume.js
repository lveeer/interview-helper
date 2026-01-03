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
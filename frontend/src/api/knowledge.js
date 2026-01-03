import request from '@/utils/request'

// 上传知识库文档
export const uploadKnowledge = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/knowledge/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取知识库文档列表
export const getKnowledgeList = () => {
  return request({
    url: '/knowledge',
    method: 'get'
  })
}

// 查询知识库
export const queryKnowledge = (data) => {
  return request({
    url: '/knowledge/query',
    method: 'post',
    data
  })
}

// 删除知识库文档
export const deleteKnowledge = (id) => {
  return request({
    url: `/knowledge/${id}`,
    method: 'delete'
  })
}
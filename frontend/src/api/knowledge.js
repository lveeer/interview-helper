import request from '@/utils/request'

// 分段策略选项
export const CHUNK_STRATEGY_OPTIONS = [
  { value: 'semantic', label: '语义分段', description: '按段落和语义边界分割（通用场景）' },
  { value: 'parent_child', label: '父子分段', description: '保证上下文完整性（推荐面试场景）' },
  { value: 'recursive', label: '递归分段', description: '灵活的分隔符控制（适合技术文档）' }
]

// 上传知识库文档
export const uploadKnowledge = (file, chunkStrategy = 'semantic') => {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: `/knowledge/upload?chunk_strategy=${chunkStrategy}`,
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

// 获取文档预览内容
export const getDocumentPreview = (id) => {
  return request({
    url: `/knowledge/${id}/preview`,
    method: 'get'
  })
}

// 更新文档分类
export const updateDocumentCategory = (id, category) => {
  return request({
    url: `/knowledge/${id}/category`,
    method: 'put',
    data: { category }
  })
}

// 获取查询历史
export const getQueryHistory = () => {
  return request({
    url: '/knowledge/query/history',
    method: 'get'
  })
}

// 清空查询历史
export const clearQueryHistory = () => {
  return request({
    url: '/knowledge/query/history',
    method: 'delete'
  })
}

// 更新文档分段策略
export const updateChunkStrategy = (docId, chunkStrategy) => {
  return request({
    url: `/knowledge/${docId}/chunk-strategy`,
    method: 'put',
    data: { chunk_strategy: chunkStrategy }
  })
}
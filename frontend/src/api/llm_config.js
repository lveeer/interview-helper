import request from '@/utils/request'

// 获取支持的提供商列表
export const getProviders = () => {
  return request({
    url: '/llm-config/providers',
    method: 'get'
  })
}

// 测试 LLM 连接
export const testConnection = (data) => {
  return request({
    url: '/llm-config/test-connection',
    method: 'post',
    data
  })
}

// 获取当前用户配置
export const getMyConfig = () => {
  return request({
    url: '/llm-config/',
    method: 'get'
  })
}

// 创建 LLM 配置
export const createConfig = (data) => {
  return request({
    url: '/llm-config/',
    method: 'post',
    data
  })
}

// 更新 LLM 配置
export const updateConfig = (data) => {
  return request({
    url: '/llm-config/',
    method: 'put',
    data
  })
}

// 删除 LLM 配置
export const deleteConfig = () => {
  return request({
    url: '/llm-config/',
    method: 'delete'
  })
}
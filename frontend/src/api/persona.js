import request from '@/utils/request'

/**
 * 获取所有人设列表
 * @returns {Promise} 返回人设列表
 */
export function getPersonas() {
  return request({
    url: '/personas',
    method: 'get'
  })
}

/**
 * 获取默认人设
 * @returns {Promise} 返回默认人设信息
 */
export function getDefaultPersona() {
  return request({
    url: '/personas/default',
    method: 'get'
  })
}

/**
 * 获取人设详情
 * @param {number} id - 人设ID
 * @returns {Promise} 返回人设详情
 */
export function getPersona(id) {
  return request({
    url: `/personas/${id}`,
    method: 'get'
  })
}

/**
 * 创建自定义人设
 * @param {Object} data - 人设数据
 * @param {string} data.name - 人设名称
 * @param {string} data.description - 人设描述
 * @param {string} data.tone - 语气风格
 * @param {string} data.focus - 关注重点
 * @returns {Promise} 返回创建的人设
 */
export function createPersona(data) {
  return request({
    url: '/personas',
    method: 'post',
    data
  })
}

/**
 * 更新自定义人设
 * @param {number} id - 人设ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 返回更新后的人设
 */
export function updatePersona(id, data) {
  return request({
    url: `/personas/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除自定义人设
 * @param {number} id - 人设ID
 * @returns {Promise} 返回删除结果
 */
export function deletePersona(id) {
  return request({
    url: `/personas/${id}`,
    method: 'delete'
  })
}
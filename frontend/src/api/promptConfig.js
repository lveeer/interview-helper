import request from '@/utils/request'

// ===== 配置分类常量 =====
export const CONFIG_CATEGORIES = [
  { value: 'interview', label: '面试' },
  { value: 'resume', label: '简历' },
  { value: 'evaluation', label: '评估' },
  { value: 'rag', label: 'RAG' },
  { value: 'game', label: '游戏' },
  { value: 'other', label: '其他' }
]

// ===== A/B 测试状态常量 =====
export const AB_TEST_STATUS = {
  DRAFT: 'draft',
  RUNNING: 'running',
  PAUSED: 'paused',
  COMPLETED: 'completed',
  ARCHIVED: 'archived'
}

export const AB_TEST_STATUS_LABELS = {
  draft: '草稿',
  running: '运行中',
  paused: '已暂停',
  completed: '已完成',
  archived: '已归档'
}

// ===== Prompt 配置管理 =====

/**
 * 创建 Prompt 配置
 * @param {Object} data - 配置数据
 * @param {string} data.name - 配置名称（唯一标识）
 * @param {string} data.display_name - 显示名称
 * @param {string} data.description - 配置描述
 * @param {string} data.category - 分类
 * @param {string} data.tags - 标签（逗号分隔）
 * @param {boolean} data.is_active - 是否启用
 * @param {string} data.initial_content - 初始版本内容
 * @param {string} data.initial_version - 初始版本号
 */
export const createConfig = (data) => {
  return request({
    url: '/prompt-config',
    method: 'post',
    data
  })
}

/**
 * 获取配置列表
 * @param {Object} params - 查询参数
 * @param {string} params.category - 分类过滤
 * @param {boolean} params.is_active - 是否启用过滤
 * @param {string} params.search - 搜索关键词
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 */
export const getConfigList = (params = {}) => {
  return request({
    url: '/prompt-config',
    method: 'get',
    params
  })
}

/**
 * 获取配置详情
 * @param {number} configId - 配置 ID
 */
export const getConfigDetail = (configId) => {
  return request({
    url: `/prompt-config/${configId}`,
    method: 'get'
  })
}

/**
 * 更新配置
 * @param {number} configId - 配置 ID
 * @param {Object} data - 更新数据
 */
export const updateConfig = (configId, data) => {
  return request({
    url: `/prompt-config/${configId}`,
    method: 'put',
    data
  })
}

/**
 * 删除配置
 * @param {number} configId - 配置 ID
 */
export const deleteConfig = (configId) => {
  return request({
    url: `/prompt-config/${configId}`,
    method: 'delete'
  })
}

/**
 * 设置激活版本
 * @param {number} configId - 配置 ID
 * @param {number} versionId - 版本 ID
 */
export const activateVersion = (configId, versionId) => {
  return request({
    url: `/prompt-config/${configId}/activate-version`,
    method: 'post',
    data: { version_id: versionId }
  })
}

// ===== 版本管理 =====

/**
 * 创建版本
 * @param {number} configId - 配置 ID
 * @param {Object} data - 版本数据
 * @param {string} data.version - 版本号
 * @param {string} data.content - Prompt 内容
 * @param {string} data.change_log - 变更日志
 */
export const createVersion = (configId, data) => {
  return request({
    url: `/prompt-config/${configId}/versions`,
    method: 'post',
    data
  })
}

/**
 * 获取版本列表
 * @param {number} configId - 配置 ID
 * @param {boolean} includeUnpublished - 是否包含未发布版本
 */
export const getVersionList = (configId, includeUnpublished = true) => {
  return request({
    url: `/prompt-config/${configId}/versions`,
    method: 'get',
    params: { include_unpublished: includeUnpublished }
  })
}

/**
 * 获取版本详情
 * @param {number} versionId - 版本 ID
 */
export const getVersionDetail = (versionId) => {
  return request({
    url: `/prompt-config/versions/${versionId}`,
    method: 'get'
  })
}

/**
 * 更新版本（仅未发布版本可更新）
 * @param {number} versionId - 版本 ID
 * @param {Object} data - 更新数据
 */
export const updateVersion = (versionId, data) => {
  return request({
    url: `/prompt-config/versions/${versionId}`,
    method: 'put',
    data
  })
}

/**
 * 发布版本
 * @param {number} versionId - 版本 ID
 */
export const publishVersion = (versionId) => {
  return request({
    url: `/prompt-config/versions/${versionId}/publish`,
    method: 'post'
  })
}

/**
 * 删除版本（仅未发布版本可删除）
 * @param {number} versionId - 版本 ID
 */
export const deleteVersion = (versionId) => {
  return request({
    url: `/prompt-config/versions/${versionId}`,
    method: 'delete'
  })
}

// ===== A/B 测试管理 =====

/**
 * 创建 A/B 测试
 * @param {number} configId - 配置 ID
 * @param {Object} data - 测试数据
 * @param {string} data.name - 测试名称
 * @param {string} data.description - 测试描述
 * @param {number} data.control_version_id - 对照组版本 ID
 * @param {number} data.experiment_version_id - 实验组版本 ID
 * @param {number} data.traffic_ratio - 实验组流量比例 (0-1)
 * @param {string} data.start_time - 开始时间
 * @param {string} data.end_time - 结束时间
 */
export const createABTest = (configId, data) => {
  return request({
    url: `/prompt-config/${configId}/ab-tests`,
    method: 'post',
    data
  })
}

/**
 * 获取 A/B 测试列表
 * @param {number} configId - 配置 ID
 * @param {Object} params - 查询参数
 */
export const getABTestList = (configId, params = {}) => {
  return request({
    url: `/prompt-config/${configId}/ab-tests`,
    method: 'get',
    params
  })
}

/**
 * 获取 A/B 测试详情
 * @param {number} testId - 测试 ID
 */
export const getABTestDetail = (testId) => {
  return request({
    url: `/prompt-config/ab-tests/${testId}`,
    method: 'get'
  })
}

/**
 * 更新 A/B 测试（仅草稿状态可更新）
 * @param {number} testId - 测试 ID
 * @param {Object} data - 更新数据
 */
export const updateABTest = (testId, data) => {
  return request({
    url: `/prompt-config/ab-tests/${testId}`,
    method: 'put',
    data
  })
}

/**
 * 变更 A/B 测试状态
 * @param {number} testId - 测试 ID
 * @param {string} status - 目标状态
 */
export const changeABTestStatus = (testId, status) => {
  return request({
    url: `/prompt-config/ab-tests/${testId}/status`,
    method: 'post',
    data: { status }
  })
}

/**
 * 激活 A/B 测试
 * @param {number} configId - 配置 ID
 * @param {number} abTestId - A/B 测试 ID
 */
export const activateABTest = (configId, abTestId) => {
  return request({
    url: `/prompt-config/${configId}/activate-ab-test`,
    method: 'post',
    data: { ab_test_id: abTestId }
  })
}

/**
 * 停用 A/B 测试
 * @param {number} configId - 配置 ID
 */
export const deactivateABTest = (configId) => {
  return request({
    url: `/prompt-config/${configId}/deactivate-ab-test`,
    method: 'post'
  })
}

/**
 * 删除 A/B 测试（仅草稿状态可删除）
 * @param {number} testId - 测试 ID
 */
export const deleteABTest = (testId) => {
  return request({
    url: `/prompt-config/ab-tests/${testId}`,
    method: 'delete'
  })
}

// ===== A/B 测试结果 =====

/**
 * 记录测试结果
 * @param {number} testId - 测试 ID
 * @param {Object} data - 结果数据
 * @param {string} data.variant - 变体类型 (control/experiment)
 * @param {string} data.session_id - 会话 ID
 * @param {string} data.metrics - 指标数据（JSON 字符串）
 * @param {number} data.score - 评分
 * @param {string} data.feedback - 反馈信息
 */
export const recordABTestResult = (testId, data) => {
  return request({
    url: `/prompt-config/ab-tests/${testId}/results`,
    method: 'post',
    data
  })
}

/**
 * 获取测试统计
 * @param {number} testId - 测试 ID
 */
export const getABTestStatistics = (testId) => {
  return request({
    url: `/prompt-config/ab-tests/${testId}/statistics`,
    method: 'get'
  })
}

// ===== Prompt 获取 =====

/**
 * 获取生效的 Prompt（自动处理 A/B 测试分流）
 * @param {string} configName - 配置名称
 * @param {Object} params - 查询参数
 * @param {number} params.user_id - 用户 ID（用于一致性分流）
 * @param {string} params.session_id - 会话 ID（用于一致性分流）
 */
export const resolvePrompt = (configName, params = {}) => {
  return request({
    url: `/prompt-config/resolve/${configName}`,
    method: 'get',
    params
  })
}

// ===== 初始化 =====

/**
 * 从文件系统初始化 Prompt 配置
 */
export const initFromFiles = () => {
  return request({
    url: '/prompt-config/init-from-files',
    method: 'post'
  })
}

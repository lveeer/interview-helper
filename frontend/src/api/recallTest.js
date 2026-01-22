import request from '@/utils/request'

// 创建召回测试用例
export const createTestCase = (data) => {
  return request({
    url: '/knowledge/recall-test/cases',
    method: 'post',
    data
  })
}

// 获取召回测试用例列表
export const getTestCases = () => {
  return request({
    url: '/knowledge/recall-test/cases',
    method: 'get'
  })
}

// 删除召回测试用例
export const deleteTestCase = (id) => {
  return request({
    url: `/knowledge/recall-test/cases/${id}`,
    method: 'delete'
  })
}

// 执行召回测试
export const runRecallTest = (data) => {
  return request({
    url: '/knowledge/recall-test/run',
    method: 'post',
    data
  })
}

// 获取召回测试结果
export const getTestResults = (testCaseId) => {
  return request({
    url: '/knowledge/recall-test/results',
    method: 'get',
    params: testCaseId ? { test_case_id: testCaseId } : undefined
  })
}

// 获取召回测试汇总统计
export const getTestSummary = (testCaseId) => {
  return request({
    url: '/knowledge/recall-test/summary',
    method: 'get',
    params: testCaseId ? { test_case_id: testCaseId } : undefined
  })
}
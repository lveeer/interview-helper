import request from '@/utils/request'

/**
 * 获取用户统计数据
 */
export const getDashboardStatistics = () => {
  return request({
    url: '/statistics/dashboard',
    method: 'get'
  })
}
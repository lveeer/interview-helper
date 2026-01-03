import request from '@/utils/request'

// 岗位匹配分析
export const matchJob = (data) => {
  return request({
    url: '/job/match',
    method: 'post',
    data
  })
}
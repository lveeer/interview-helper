import request from '@/utils/request'

// 获取面试评估报告
export const getInterviewReport = (interviewId) => {
  return request({
    url: `/evaluation/report/${interviewId}`,
    method: 'get'
  })
}
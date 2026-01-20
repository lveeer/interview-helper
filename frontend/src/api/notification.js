import request from '@/utils/request'

/**
 * 获取通知列表
 * @param {Object} params - 查询参数
 * @param {number} params.skip - 跳过数量
 * @param {number} params.limit - 限制数量
 * @param {boolean} params.unreadOnly - 是否只获取未读
 * @returns {Promise}
 */
export function getNotifications(params = {}) {
  return request({
    url: '/task/notifications',
    method: 'get',
    params: {
      skip: params.skip || 0,
      limit: params.limit || 20,
      unread_only: params.unreadOnly || false
    }
  })
}

/**
 * 标记通知为已读
 * @param {number} notificationId - 通知 ID
 * @returns {Promise}
 */
export function markNotificationAsRead(notificationId) {
  return request({
    url: `/task/notifications/${notificationId}/read`,
    method: 'put'
  })
}

/**
 * 标记所有通知为已读
 * @returns {Promise}
 */
export function markAllNotificationsAsRead() {
  return request({
    url: '/task/notifications/read-all',
    method: 'put'
  })
}

/**
 * 删除通知
 * @param {number} notificationId - 通知 ID
 * @returns {Promise}
 */
export function deleteNotification(notificationId) {
  return request({
    url: `/task/notifications/${notificationId}`,
    method: 'delete'
  })
}

/**
 * 获取未读通知数量
 * @returns {Promise}
 */
export function getUnreadCount() {
  return request({
    url: '/task/notifications/unread-count',
    method: 'get'
  })
}
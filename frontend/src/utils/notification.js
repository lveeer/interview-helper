import { ElMessage, ElNotification } from 'element-plus'

/**
 * 通知管理器类
 * 处理 WebSocket 连接、通知接收和显示
 */
class NotificationManager {
  constructor() {
    this.ws = null
    this.notifications = []
    this.historyNotifications = []
    this.unreadCount = 0
    this.listeners = []
    this.heartbeatInterval = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 5000
    this.router = null
  }

  /**
   * 设置 Vue Router 实例
   * @param {Object} router - Vue Router 实例
   */
  setRouter(router) {
    this.router = router
  }

  /**
   * 连接 WebSocket
   * @param {number} userId - 用户 ID
   * @param {string} token - JWT token
   */
  connect(userId, token) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('[NotificationManager] WebSocket 已连接')
      return
    }

    const wsUrl = `ws://localhost:8000/api/task/ws/task/${userId}?token=${token}`
    console.log('[NotificationManager] 正在连接 WebSocket:', wsUrl)

    try {
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('[NotificationManager] WebSocket 连接已建立')
        this.reconnectAttempts = 0
        this.emit('connected')
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.handleNotification(data)
        } catch (error) {
          console.error('[NotificationManager] 解析消息失败:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('[NotificationManager] WebSocket 错误:', error)
        this.emit('error', error)
      }

      this.ws.onclose = () => {
        console.log('[NotificationManager] WebSocket 连接已关闭')
        this.emit('disconnected')
        this.clearHeartbeat()
        this.autoReconnect(userId, token)
      }

      // 启动心跳机制
      this.startHeartbeat()
    } catch (error) {
      console.error('[NotificationManager] 创建 WebSocket 失败:', error)
      this.autoReconnect(userId, token)
    }
  }

  /**
   * 自动重连
   * @param {number} userId - 用户 ID
   * @param {string} token - JWT token
   */
  autoReconnect(userId, token) {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[NotificationManager] 达到最大重连次数，停止重连')
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectDelay * this.reconnectAttempts

    console.log(`[NotificationManager] ${delay / 1000}秒后尝试第 ${this.reconnectAttempts} 次重连...`)

    setTimeout(() => {
      this.connect(userId, token)
    }, delay)
  }

  /**
   * 启动心跳机制
   */
  startHeartbeat() {
    this.clearHeartbeat()
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }))
        console.log('[NotificationManager] 发送心跳')
      }
    }, 30000)
  }

  /**
   * 清除心跳
   */
  clearHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  /**
   * 处理通知消息
   * @param {Object} data - 通知数据
   */
  handleNotification(data) {
    console.log('[NotificationManager] 收到通知:', data)

    switch (data.type) {
      case 'connected':
        this.emit('connected', data)
        break

      case 'active_tasks':
        this.emit('active_tasks', data.tasks)
        break

      case 'task_status':
        // 添加到通知列表
        this.notifications.unshift({
          id: Date.now(),
          ...data,
          timestamp: new Date()
        })

        // 根据状态显示不同通知
        if (data.status === 'completed') {
          this.showTaskCompletedNotification(data)
        } else if (data.status === 'failed') {
          this.showTaskFailedNotification(data)
        } else if (data.status === 'processing') {
          this.showTaskProcessingNotification(data)
        }

        this.emit('task_status', data)
        break

      case 'pong':
        console.log('[NotificationManager] 收到心跳响应')
        break

      default:
        console.warn('[NotificationManager] 未知通知类型:', data.type)
    }
  }

  /**
   * 显示任务完成通知
   * @param {Object} data - 任务数据
   */
  showTaskCompletedNotification(data) {
    const key = `task_${data.task_id}`

    ElNotification({
      title: '任务完成',
      message: this.buildNotificationMessage(data),
      type: 'success',
      duration: 5000,
      dangerouslyUseHTMLString: true,
      onClick: () => this.handleRedirect(data),
      position: 'top-right'
    })
  }

  /**
   * 显示任务失败通知
   * @param {Object} data - 任务数据
   */
  showTaskFailedNotification(data) {
    ElNotification({
      title: '任务失败',
      message: this.buildNotificationMessage(data),
      type: 'error',
      duration: 5000,
      dangerouslyUseHTMLString: true,
      position: 'top-right'
    })
  }

  /**
   * 显示任务处理中通知
   * @param {Object} data - 任务数据
   */
  showTaskProcessingNotification(data) {
    ElMessage({
      message: `${this.getTaskTypeName(data.task_type)} - ${data.message || '任务处理中...'}`,
      type: 'info',
      duration: 3000
    })
  }

  /**
   * 构建通知消息内容
   * @param {Object} data - 任务数据
   * @returns {string} - 消息内容
   */
  buildNotificationMessage(data) {
    let message = ''

    if (data.message) {
      message += `<div style="font-weight: bold; margin-bottom: 8px;">${data.message}</div>`
    }

    if (data.result && typeof data.result === 'object') {
      message += '<div style="font-size: 12px; color: #666;">'
      Object.entries(data.result).forEach(([key, value]) => {
        message += `<div>${key}: ${value}</div>`
      })
      message += '</div>'
    }

    if (data.error) {
      message += `<div style="font-size: 12px; color: #f56c6c; margin-top: 8px;">${data.error}</div>`
    }

    return message
  }

  /**
   * 处理跳转
   * @param {Object} data - 任务数据
   */
  handleRedirect(data) {
    if (data.redirect_url) {
      console.log('[NotificationManager] 跳转到:', data.redirect_url)

      // 判断是外部链接还是内部路由
      if (data.redirect_url.startsWith('http://') || data.redirect_url.startsWith('https://')) {
        // 外部链接使用 window.location.href
        window.location.href = data.redirect_url
      } else {
        // 内部路由使用 Vue Router
        if (this.router) {
          this.router.push(data.redirect_url)
        } else {
          console.warn('[NotificationManager] Router 未设置，使用 window.location.href')
          window.location.href = data.redirect_url
        }
      }
    }
  }

  /**
   * 加载历史通知
   * @param {string} token - JWT token
   * @param {Object} params - 查询参数
   */
  async loadHistoryNotifications(token, params = {}) {
    try {
      const queryString = new URLSearchParams({
        skip: params.skip || 0,
        limit: params.limit || 20,
        unread_only: params.unreadOnly || false
      }).toString()

      const response = await fetch(`http://localhost:8000/api/task/notifications?${queryString}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      const result = await response.json()

      if (result.code === 200) {
        this.historyNotifications = result.data.notifications
        this.unreadCount = result.data.notifications.filter(n => n.status !== 'read').length
        this.emit('history_loaded', this.historyNotifications)
        console.log('[NotificationManager] 历史通知加载成功:', this.historyNotifications.length)
      }
    } catch (error) {
      console.error('[NotificationManager] 加载历史通知失败:', error)
      this.emit('error', error)
    }
  }

  /**
   * 标记通知为已读
   * @param {number} notificationId - 通知 ID
   * @param {string} token - JWT token
   */
  async markAsRead(notificationId, token) {
    try {
      const response = await fetch(
        `http://localhost:8000/api/task/notifications/${notificationId}/read`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )

      if (response.ok) {
        // 更新本地状态
        const notification = this.historyNotifications.find(n => n.id === notificationId)
        if (notification) {
          notification.status = 'read'
          this.unreadCount = Math.max(0, this.unreadCount - 1)
          this.emit('notification_updated', this.historyNotifications)
        }
        console.log('[NotificationManager] 标记已读成功:', notificationId)
      }
    } catch (error) {
      console.error('[NotificationManager] 标记已读失败:', error)
      this.emit('error', error)
    }
  }

  /**
   * 标记所有通知为已读
   * @param {string} token - JWT token
   */
  async markAllAsRead(token) {
    try {
      const response = await fetch(
        'http://localhost:8000/api/task/notifications/read-all',
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )

      if (response.ok) {
        this.historyNotifications.forEach(n => n.status = 'read')
        this.unreadCount = 0
        this.emit('notification_updated', this.historyNotifications)
        console.log('[NotificationManager] 标记全部已读成功')
      }
    } catch (error) {
      console.error('[NotificationManager] 标记全部已读失败:', error)
      this.emit('error', error)
    }
  }

  /**
   * 删除通知
   * @param {number} notificationId - 通知 ID
   * @param {string} token - JWT token
   */
  async deleteNotification(notificationId, token) {
    try {
      const response = await fetch(
        `http://localhost:8000/api/task/notifications/${notificationId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )

      if (response.ok) {
        this.historyNotifications = this.historyNotifications.filter(n => n.id !== notificationId)
        this.emit('notification_updated', this.historyNotifications)
        console.log('[NotificationManager] 删除通知成功:', notificationId)
      }
    } catch (error) {
      console.error('[NotificationManager] 删除通知失败:', error)
      this.emit('error', error)
    }
  }

  /**
   * 获取未读数量
   * @param {string} token - JWT token
   */
  async getUnreadCount(token) {
    try {
      const response = await fetch(
        'http://localhost:8000/api/task/notifications/unread-count',
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )

      const result = await response.json()

      if (result.code === 200) {
        this.unreadCount = result.data.unread_count
        this.emit('unread_count_updated', this.unreadCount)
        return this.unreadCount
      }
    } catch (error) {
      console.error('[NotificationManager] 获取未读数量失败:', error)
      this.emit('error', error)
    }
    return 0
  }

  /**
   * 获取通知类型标签颜色
   * @param {string} type - 通知类型
   * @returns {string} - Element Plus 标签类型
   */
  getNotificationTypeColor(type) {
    const colors = {
      success: 'success',
      error: 'danger',
      warning: 'warning',
      info: 'info'
    }
    return colors[type] || 'info'
  }

  /**
   * 获取任务类型显示名称
   * @param {string} type - 任务类型
   * @returns {string} - 显示名称
   */
  getTaskTypeName(type) {
    const names = {
      interview_generation: '面试问题生成',
      resume_upload: '简历上传',
      resume_parse: '简历解析',
      resume_optimize: '简历优化',
      knowledge_upload: '知识库上传',
      evaluation_generate: '评估报告生成',
      job_match: '岗位匹配分析'
    }
    return names[type] || type
  }

  /**
   * 注册事件监听器
   * @param {string} event - 事件名称
   * @param {Function} callback - 回调函数
   */
  on(event, callback) {
    this.listeners.push({ event, callback })
  }

  /**
   * 移除事件监听器
   * @param {string} event - 事件名称
   * @param {Function} callback - 回调函数
   */
  off(event, callback) {
    this.listeners = this.listeners.filter(
      l => !(l.event === event && l.callback === callback)
    )
  }

  /**
   * 触发事件
   * @param {string} event - 事件名称
   * @param {*} data - 事件数据
   */
  emit(event, data) {
    this.listeners
      .filter(l => l.event === event)
      .forEach(l => {
        try {
          l.callback(data)
        } catch (error) {
          console.error(`[NotificationManager] 事件回调错误 (${event}):`, error)
        }
      })
  }

  /**
   * 断开连接
   */
  disconnect() {
    console.log('[NotificationManager] 断开 WebSocket 连接')
    this.clearHeartbeat()
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.reconnectAttempts = 0
  }
}

// 导出单例实例
export const notificationManager = new NotificationManager()

export default notificationManager
/**
 * WebSocket 心跳客户端类
 * 支持自动重连、心跳检测、消息队列缓冲
 */
class WebSocketClient {
  constructor(options = {}) {
    this.url = options.url || ''
    this.heartbeatInterval = options.heartbeatInterval || 30000 // 心跳间隔，默认30秒
    this.reconnectInterval = options.reconnectInterval || 1000 // 重连间隔，默认1秒
    this.maxReconnectAttempts = options.maxReconnectAttempts || 5 // 最大重连次数
    this.reconnectAttempts = 0 // 当前重连次数
    this.heartbeatTimer = null // 心跳定时器
    this.reconnectTimer = null // 重连定时器
    this.messageQueue = [] // 消息队列
    this.isManualClose = false // 是否手动关闭
    this.latency = 0 // 网络延迟
    this.lastHeartbeatTime = null // 上次心跳时间

    // 事件回调
    this.onOpen = options.onOpen || (() => {})
    this.onMessage = options.onMessage || (() => {})
    this.onError = options.onError || (() => {})
    this.onClose = options.onClose || (() => {})
    this.onReconnect = options.onReconnect || (() => {})
    this.onStatusChange = options.onStatusChange || (() => {})

    this.ws = null
    this.status = 'disconnected' // connected, connecting, disconnected, reconnecting
  }

  /**
   * 连接 WebSocket
   */
  connect() {
    if (this.status === 'connected' || this.status === 'connecting') {
      return
    }

    this.status = 'connecting'
    this.onStatusChange(this.status)

    try {
      this.ws = new WebSocket(this.url)
      this._setupEventListeners()
    } catch (error) {
      this._handleError(error)
    }
  }

  /**
   * 设置 WebSocket 事件监听
   */
  _setupEventListeners() {
    this.ws.onopen = () => {
      this.status = 'connected'
      this.reconnectAttempts = 0
      this.onStatusChange(this.status)
      this.onOpen()
      this._startHeartbeat()
      this._flushMessageQueue()
    }

    this.ws.onmessage = (event) => {
      const data = event.data

      // 处理心跳响应
      if (data === 'pong') {
        this.latency = Date.now() - this.lastHeartbeatTime
        return
      }

      this.onMessage(data)
    }

    this.ws.onerror = (error) => {
      this._handleError(error)
    }

    this.ws.onclose = (event) => {
      this._handleClose(event)
    }
  }

  /**
   * 处理错误
   */
  _handleError(error) {
    console.error('WebSocket 错误:', error)
    this.status = 'disconnected'
    this.onStatusChange(this.status)
    this.onError(error)
  }

  /**
   * 处理连接关闭
   */
  _handleClose(event) {
    this.status = 'disconnected'
    this.onStatusChange(this.status)
    this._stopHeartbeat()

    // 如果不是手动关闭，尝试重连
    if (!this.isManualClose) {
      this._attemptReconnect()
    }

    this.onClose(event)
  }

  /**
   * 尝试重连
   */
  _attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('WebSocket 重连失败，已达到最大重连次数')
      return
    }

    this.reconnectAttempts++
    this.status = 'reconnecting'
    this.onStatusChange(this.status)
    this.onReconnect(this.reconnectAttempts)

    // 指数退避重连
    const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1)

    this.reconnectTimer = setTimeout(() => {
      console.log(`WebSocket 尝试第 ${this.reconnectAttempts} 次重连...`)
      this.connect()
    }, delay)
  }

  /**
   * 发送消息
   * @param {string|Object} message - 消息内容
   */
  send(message) {
    if (typeof message === 'object') {
      message = JSON.stringify(message)
    }

    if (this.status === 'connected' && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(message)
    } else {
      // 连接未建立，将消息加入队列
      this.messageQueue.push(message)
      console.log('WebSocket 未连接，消息已加入队列')
    }
  }

  /**
   * 刷新消息队列
   */
  _flushMessageQueue() {
    while (this.messageQueue.length > 0 && this.status === 'connected') {
      const message = this.messageQueue.shift()
      this.ws.send(message)
    }
  }

  /**
   * 开始心跳
   */
  _startHeartbeat() {
    this._stopHeartbeat()
    this.heartbeatTimer = setInterval(() => {
      if (this.status === 'connected') {
        this.lastHeartbeatTime = Date.now()
        this.ws.send('ping')
      }
    }, this.heartbeatInterval)
  }

  /**
   * 停止心跳
   */
  _stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  /**
   * 手动重连
   */
  reconnect() {
    this._stopHeartbeat()
    this.reconnectAttempts = 0
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    this.connect()
  }

  /**
   * 关闭连接
   */
  close() {
    this.isManualClose = true
    this._stopHeartbeat()
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    if (this.ws) {
      this.ws.close()
    }
    this.messageQueue = []
  }

  /**
   * 获取连接状态
   * @returns {string} 连接状态
   */
  getStatus() {
    return this.status
  }

  /**
   * 获取网络延迟
   * @returns {number} 延迟（毫秒）
   */
  getLatency() {
    return this.latency
  }

  /**
   * 获取重连次数
   * @returns {number} 重连次数
   */
  getReconnectAttempts() {
    return this.reconnectAttempts
  }
}

export default WebSocketClient
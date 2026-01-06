<template>
  <div class="interview-room">
    <div class="interview-container">
      <!-- macOS 风格窗口头部 -->
      <div class="interview-header">
        <div class="header-left">
          <div class="window-controls">
            <div class="window-control close"></div>
            <div class="window-control minimize"></div>
            <div class="window-control maximize"></div>
          </div>
          <div class="title-text">
            <h1>AI 模拟面试</h1>
          </div>
        </div>
        <button class="end-button" @click="handleEnd">
          结束
        </button>
      </div>

      <!-- 聊天区域 -->
      <div class="chat-container" ref="chatContainer">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.role]"
        >
          <div class="message-avatar">
            <div class="avatar-wrapper" :class="message.role">
              <el-icon v-if="message.role === 'interviewer'"><User /></el-icon>
              <el-icon v-else><UserFilled /></el-icon>
            </div>
          </div>
          <div class="message-content">
            <div class="message-role">
              {{ message.role === 'interviewer' ? '面试官' : '你' }}
            </div>
            <div class="message-text">{{ message.content }}</div>
          </div>
        </div>

        <!-- 打字指示器 -->
        <div v-if="isTyping" class="message interviewer">
          <div class="message-avatar">
            <div class="avatar-wrapper interviewer">
              <el-icon><User /></el-icon>
            </div>
          </div>
          <div class="message-content">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <div class="input-wrapper">
          <textarea
            v-model="userAnswer"
            class="input-field"
            :rows="3"
            placeholder="输入你的回答..."
            :disabled="isTyping"
            @keyup.ctrl.enter="sendAnswer"
          ></textarea>
          <div class="input-actions">
            <button
              class="send-button"
              :class="{ loading: isTyping }"
              :disabled="isTyping || !userAnswer.trim()"
              @click="sendAnswer"
            >
              <el-icon v-if="!isTyping"><Promotion /></el-icon>
              <span>{{ isTyping ? '思考中...' : '发送' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, UserFilled, Promotion } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const interviewId = route.params.id
const messages = ref([])
const userAnswer = ref('')
const isTyping = ref(false)
const chatContainer = ref(null)
let websocket = null
const isEnding = ref(false) // 标记是否正在结束面试

onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (websocket) {
    websocket.close()
  }
})

const connectWebSocket = () => {
  const wsUrl = `ws://localhost:8000/api/interview/ws/${interviewId}`
  websocket = new WebSocket(wsUrl)

  websocket.onopen = () => {
    console.log('WebSocket 连接成功')
  }

  websocket.onmessage = (event) => {
    console.log('收到 WebSocket 消息:', event.data)
    const data = JSON.parse(event.data)
    console.log('解析后的数据:', data)

    if (data.type === 'question' || data.type === 'followup') {
      isTyping.value = false
      messages.value.push({
        role: 'interviewer',
        content: data.data.question
      })
      scrollToBottom()
    } else if (data.type === 'end') {
      console.log('收到结束消息，准备跳转')
      isTyping.value = false
      ElMessage.success('面试已完成，报告生成中，请稍后在面试列表查看')
      setTimeout(() => {
        router.push('/interview')
      }, 2000)
    } else {
      console.log('未处理的消息类型:', data.type)
    }
  }

  websocket.onerror = (error) => {
    console.error('WebSocket 错误:', error)
    ElMessage.error('连接错误，请刷新页面重试')
  }

  websocket.onclose = () => {
    console.log('WebSocket 连接关闭')
    // 如果是用户主动结束面试导致的连接关闭，显示成功消息并跳转
    if (isEnding.value) {
      ElMessage.success('面试已完成，报告生成中，请稍后在面试列表查看')
      setTimeout(() => {
        router.push('/interview')
      }, 2000)
    }
  }
}

const sendAnswer = async () => {
  if (!userAnswer.value.trim()) {
    ElMessage.warning('请输入回答')
    return
  }

  const answer = userAnswer.value.trim()
  messages.value.push({
    role: 'candidate',
    content: answer
  })
  userAnswer.value = ''
  scrollToBottom()

  isTyping.value = true

  if (websocket && websocket.readyState === WebSocket.OPEN) {
    websocket.send(JSON.stringify({
      type: 'answer',
      answer: answer,
      answer_type: 'text'
    }))
  } else {
    ElMessage.error('连接已断开，请刷新页面')
  }
}

const handleEnd = async () => {
  try {
    await ElMessageBox.confirm('确定要结束面试吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 禁用按钮防止重复点击
    const endButton = document.querySelector('.end-button')
    if (endButton) {
      endButton.disabled = true
      endButton.textContent = '结束中...'
    }

    ElMessage.info('正在结束面试...')

    // 尝试发送结束消息
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.send(JSON.stringify({ type: 'end' }))
    }

    // 直接关闭 WebSocket 连接
    if (websocket) {
      websocket.close()
    }

    // 显示成功消息并跳转
    ElMessage.success('面试已完成，报告生成中，请稍后在面试列表查看')
    setTimeout(() => {
      router.push('/interview')
    }, 2000)
  } catch {
    // 用户取消
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}
</script>

<style scoped>
/* ===== 主容器 - macOS 风格 ===== */
.interview-room {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f5f7;
  padding: 20px;
  box-sizing: border-box;
}

.interview-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

/* ===== 顶部工具栏 - macOS 风格 ===== */
.interview-header {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.window-controls {
  display: flex;
  gap: 8px;
}

.window-control {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  transition: opacity 0.15s ease;
}

.window-control.close {
  background: #FF5F57;
}

.window-control.minimize {
  background: #FEBC2E;
}

.window-control.maximize {
  background: #28C840;
}

.title-text h1 {
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
  margin: 0;
  letter-spacing: -0.01em;
}

.end-button {
  padding: 6px 12px;
  background: #FF3B30;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.end-button:hover {
  background: #FF453A;
}

.end-button:active {
  opacity: 0.8;
}

/* ===== 聊天容器 ===== */
.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #ffffff;
  scroll-behavior: smooth;
}

.chat-container::-webkit-scrollbar {
  width: 8px;
}

.chat-container::-webkit-scrollbar-track {
  background: transparent;
}

.chat-container::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* ===== 消息样式 ===== */
.message {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  animation: messageFadeIn 0.2s ease-out;
}

.message:last-child {
  margin-bottom: 0;
}

@keyframes messageFadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.interviewer {
  flex-direction: row;
}

.message.candidate {
  flex-direction: row-reverse;
}

/* ===== 头像样式 ===== */
.message-avatar {
  flex-shrink: 0;
}

.avatar-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  transition: all 0.15s ease;
}

.avatar-wrapper.interviewer {
  background: #007AFF;
}

.avatar-wrapper.candidate {
  background: #34C759;
}

/* ===== 消息内容 ===== */
.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
}

.message-role {
  font-size: 12px;
  color: #86868b;
  margin-bottom: 4px;
  font-weight: 500;
  padding: 0 4px;
}

.message.interviewer .message-role {
  text-align: left;
}

.message.candidate .message-role {
  text-align: right;
}

/* ===== 消息气泡 ===== */
.message-text {
  background: #f5f5f7;
  padding: 12px 16px;
  border-radius: 18px;
  line-height: 1.5;
  color: #1d1d1f;
  font-size: 15px;
  font-weight: 400;
  letter-spacing: -0.01em;
}

.message.interviewer .message-text {
  border-top-left-radius: 4px;
}

.message.candidate .message-text {
  background: #007AFF;
  color: white;
  border-top-right-radius: 4px;
}

/* ===== 打字指示器 ===== */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: #f5f5f7;
  border-radius: 18px;
  border-top-left-radius: 4px;
  width: fit-content;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #86868b;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

/* ===== 输入区域 ===== */
.input-area {
  padding: 16px;
  background: #ffffff;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-field {
  width: 100%;
  padding: 12px 16px;
  font-size: 15px;
  line-height: 1.5;
  color: #1d1d1f;
  background: #f5f5f7;
  border: 1px solid transparent;
  border-radius: 10px;
  resize: none;
  transition: all 0.15s ease;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', sans-serif;
  outline: none;
}

.input-field::placeholder {
  color: #86868b;
}

.input-field:hover {
  background: #ebebeb;
}

.input-field:focus {
  background: #ffffff;
  border-color: #007AFF;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.input-field:disabled {
  background: #f5f5f7;
  cursor: not-allowed;
  opacity: 0.6;
}

/* ===== 输入操作按钮 ===== */
.input-actions {
  display: flex;
  justify-content: flex-end;
}

.send-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #007AFF;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  min-width: 80px;
  justify-content: center;
}

.send-button:hover:not(:disabled) {
  background: #0056CC;
}

.send-button:active:not(:disabled) {
  opacity: 0.8;
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #007AFF;
}

.send-button.loading {
  background: #86868b;
  cursor: wait;
}

.send-button .el-icon {
  font-size: 14px;
}

/* ===== 响应式设计 ===== */
@media (max-width: 768px) {
  .interview-room {
    padding: 12px;
  }

  .interview-header {
    padding: 10px 12px;
  }

  .chat-container {
    padding: 16px;
  }

  .message {
    margin-bottom: 20px;
  }

  .avatar-wrapper {
    width: 36px;
    height: 36px;
    font-size: 18px;
  }

  .message-content {
    max-width: 80%;
  }

  .message-text {
    padding: 10px 14px;
    font-size: 14px;
  }

  .input-area {
    padding: 12px;
  }

  .input-field {
    font-size: 14px;
    padding: 10px 14px;
  }

  .send-button {
    width: 100%;
    padding: 10px 16px;
  }
}

/* ===== 深色模式 ===== */
@media (prefers-color-scheme: dark) {
  .interview-room {
    background: #1c1c1e;
  }

  .interview-container {
    background: #2c2c2e;
    border-color: rgba(255, 255, 255, 0.1);
  }

  .interview-header {
    background: rgba(44, 44, 46, 0.8);
    border-bottom-color: rgba(255, 255, 255, 0.1);
  }

  .title-text h1 {
    color: #f5f5f7;
  }

  .chat-container {
    background: #2c2c2e;
  }

  .chat-container::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
  }

  .chat-container::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.3);
  }

  .message-role {
    color: #98989d;
  }

  .message-text {
    background: #3a3a3c;
    color: #f5f5f7;
  }

  .message.candidate .message-text {
    background: #0A84FF;
  }

  .typing-indicator {
    background: #3a3a3c;
  }

  .typing-indicator span {
    background: #98989d;
  }

  .input-area {
    background: #2c2c2e;
    border-top-color: rgba(255, 255, 255, 0.1);
  }

  .input-field {
    background: #3a3a3c;
    color: #f5f5f7;
  }

  .input-field::placeholder {
    color: #98989d;
  }

  .input-field:hover {
    background: #48484a;
  }

  .input-field:focus {
    background: #3a3a3c;
    border-color: #0A84FF;
    box-shadow: 0 0 0 3px rgba(10, 132, 255, 0.2);
  }
}
</style>
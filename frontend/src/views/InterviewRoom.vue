<template>
  <div class="interview-room">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>AI 模拟面试</span>
          <el-button type="danger" @click="handleEnd">
            <el-icon><Close /></el-icon>
            结束面试
          </el-button>
        </div>
      </template>

      <div class="chat-container" ref="chatContainer">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.role]"
        >
          <div class="message-avatar">
            <el-icon v-if="message.role === 'interviewer'"><User /></el-icon>
            <el-icon v-else><UserFilled /></el-icon>
          </div>
          <div class="message-content">
            <div class="message-role">
              {{ message.role === 'interviewer' ? '面试官' : '你' }}
            </div>
            <div class="message-text">{{ message.content }}</div>
          </div>
        </div>

        <div v-if="isTyping" class="message interviewer">
          <div class="message-avatar">
            <el-icon><User /></el-icon>
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

      <div class="input-area">
        <el-input
          v-model="userAnswer"
          type="textarea"
          :rows="3"
          placeholder="请输入你的回答..."
          :disabled="isTyping"
          @keyup.ctrl.enter="sendAnswer"
        />
        <div class="input-actions">
          <el-button type="primary" :loading="isTyping" @click="sendAnswer">
            发送 (Ctrl+Enter)
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()

const interviewId = route.params.id
const messages = ref([])
const userAnswer = ref('')
const isTyping = ref(false)
const chatContainer = ref(null)
let websocket = null

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
    const data = JSON.parse(event.data)

    if (data.type === 'question' || data.type === 'followup') {
      isTyping.value = false
      messages.value.push({
        role: 'interviewer',
        content: data.data.question
      })
      scrollToBottom()
    } else if (data.type === 'end') {
      isTyping.value = false
      ElMessage.success('面试已完成，报告生成中，请稍后在面试列表查看')
      setTimeout(() => {
        router.push('/interview')
      }, 2000)
    }
  }

  websocket.onerror = (error) => {
    console.error('WebSocket 错误:', error)
    ElMessage.error('连接错误，请刷新页面重试')
  }

  websocket.onclose = () => {
    console.log('WebSocket 连接关闭')
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

    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.send(JSON.stringify({ type: 'end' }))
    }
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
.interview-room {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.el-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: none;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

:deep(.el-card__header) {
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid var(--border-color-light);
  background: linear-gradient(180deg, var(--bg-color-light) 0%, transparent 100%);
}

:deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.card-header span::before {
  content: '💬';
  font-size: 20px;
}

/* 聊天容器 */
.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg) var(--spacing-xl);
  background: linear-gradient(180deg, var(--bg-color) 0%, var(--bg-color-light) 100%);
  scroll-behavior: smooth;
}

/* 消息样式 */
.message {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
  animation: messageSlideIn 0.3s ease-out;
}

.message:last-child {
  margin-bottom: 0;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
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

/* 头像样式 */
.message-avatar {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-round);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  font-size: 20px;
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-fast);
}

.message:hover .message-avatar {
  transform: scale(1.1);
}

.message.interviewer .message-avatar {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
}

.message.candidate .message-avatar {
  background: linear-gradient(135deg, var(--success-color) 0%, #5daf34 100%);
}

/* 消息内容 */
.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
}

.message-role {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  margin-bottom: var(--spacing-xs);
  font-weight: var(--font-weight-medium);
  padding: 0 var(--spacing-xs);
}

.message.interviewer .message-role {
  text-align: left;
}

.message.candidate .message-role {
  text-align: right;
}

/* 消息气泡 */
.message-text {
  background: var(--card-bg);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  line-height: 1.6;
  color: var(--text-primary);
  font-size: var(--font-size-base);
  position: relative;
  transition: all var(--transition-fast);
}

.message-text:hover {
  box-shadow: var(--shadow-md);
}

.message.interviewer .message-text {
  border-top-left-radius: var(--radius-xs);
  background: linear-gradient(135deg, #ffffff 0%, #f5f7fa 100%);
}

.message.candidate .message-text {
  border-top-right-radius: var(--radius-xs);
  background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary-color) 100%);
  color: #ffffff;
}

/* 打字指示器 */
.typing-indicator {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  background: linear-gradient(135deg, #ffffff 0%, #f5f7fa 100%);
  border-radius: var(--radius-lg);
  border-top-left-radius: var(--radius-xs);
  box-shadow: var(--shadow-sm);
  width: fit-content;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-round);
  background: var(--primary-color);
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
    transform: translateY(-10px);
    opacity: 1;
  }
}

/* 输入区域 */
.input-area {
  border-top: 1px solid var(--border-color-light);
  padding: var(--spacing-lg) var(--spacing-xl);
  background: var(--bg-color-light);
}

:deep(.el-textarea__inner) {
  border-radius: var(--radius-md);
  border: 2px solid var(--border-color-light);
  padding: var(--spacing-md);
  font-size: var(--font-size-base);
  line-height: 1.6;
  resize: none;
  transition: all var(--transition-fast);
  background: var(--card-bg);
}

:deep(.el-textarea__inner:hover) {
  border-color: var(--primary-color-light);
}

:deep(.el-textarea__inner:focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

:deep(.el-textarea__inner::placeholder) {
  color: var(--text-placeholder);
}

/* 输入操作按钮 */
.input-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: var(--spacing-md);
  gap: var(--spacing-md);
}

.input-actions .el-button {
  height: 40px;
  padding: 0 var(--spacing-lg);
  border-radius: var(--radius-md);
  font-weight: var(--font-weight-semibold);
  border: none;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: all var(--transition-base);
}

.input-actions .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}

.input-actions .el-button:active {
  transform: translateY(0);
}

.input-actions .el-button.is-loading {
  opacity: 0.8;
}

/* 结束按钮 */
.card-header .el-button {
  height: 36px;
  padding: 0 var(--spacing-md);
  border-radius: var(--radius-md);
  font-weight: var(--font-weight-medium);
  border: none;
  background: linear-gradient(135deg, var(--danger-color) 0%, #d95e5e 100%);
  box-shadow: 0 4px 12px rgba(245, 108, 108, 0.3);
  transition: all var(--transition-base);
}

.card-header .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(245, 108, 108, 0.4);
}

/* 滚动条样式 */
.chat-container::-webkit-scrollbar {
  width: 6px;
}

.chat-container::-webkit-scrollbar-track {
  background: transparent;
}

.chat-container::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: var(--radius-round);
  transition: background var(--transition-fast);
}

.chat-container::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  :deep(.el-card__header) {
    padding: var(--spacing-md);
  }

  .card-header span {
    font-size: var(--font-size-base);
  }

  .chat-container {
    padding: var(--spacing-md);
  }

  .message {
    margin-bottom: var(--spacing-lg);
  }

  .message-avatar {
    width: 36px;
    height: 36px;
    font-size: 16px;
  }

  .message-content {
    max-width: 80%;
  }

  .message-text {
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: var(--font-size-sm);
  }

  .input-area {
    padding: var(--spacing-md);
  }

  :deep(.el-textarea__inner) {
    font-size: var(--font-size-sm);
  }

  .input-actions .el-button {
    height: 36px;
    padding: 0 var(--spacing-md);
    font-size: var(--font-size-sm);
  }
}

/* 消息进入动画延迟 */
.message:nth-child(1) { animation-delay: 0.05s; }
.message:nth-child(2) { animation-delay: 0.1s; }
.message:nth-child(3) { animation-delay: 0.15s; }
.message:nth-child(4) { animation-delay: 0.2s; }
.message:nth-child(5) { animation-delay: 0.25s; }
</style>
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
.chat-container {
  height: 500px;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 4px;
  margin-bottom: 20px;
}

.message {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.message.interviewer {
  flex-direction: row;
}

.message.candidate {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #409EFF;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.message.candidate .message-avatar {
  background-color: #67C23A;
}

.message-content {
  max-width: 70%;
}

.message-role {
  font-size: 12px;
  color: #999;
  margin-bottom: 5px;
}

.message-text {
  background-color: #fff;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  line-height: 1.6;
}

.message.interviewer .message-text {
  border-top-left-radius: 0;
}

.message.candidate .message-text {
  border-top-right-radius: 0;
}

.typing-indicator {
  display: flex;
  gap: 5px;
  padding: 12px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #999;
  animation: typing 1.4s infinite;
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
  }
  30% {
    transform: translateY(-10px);
  }
}

.input-area {
  border-top: 1px solid #e4e7ed;
  padding-top: 20px;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
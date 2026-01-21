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
            <div class="voice-controls">
              <!-- 语音输入按钮 -->
              <button
                class="voice-button"
                :class="{ recording: isRecording }"
                :disabled="isTyping || !speechSupported.recognition"
                @click="toggleVoiceInput"
                :title="isRecording ? '停止录音' : '开始语音输入'"
              >
                <el-icon>
                  <component :is="isRecording ? 'Microphone' : 'Microphone'" />
                </el-icon>
                <span v-if="isRecording">录音中...</span>
              </button>

              <!-- 语音输出开关 -->
              <button
                class="voice-button"
                :class="{ active: voiceOutputEnabled }"
                :disabled="!speechSupported.synthesis"
                @click="toggleVoiceOutput"
                :title="voiceOutputEnabled ? '关闭语音输出' : '开启语音输出'"
              >
                <el-icon><Headset /></el-icon>
                <span>{{ voiceOutputEnabled ? '语音开' : '语音关' }}</span>
              </button>
            </div>
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
import { User, UserFilled, Promotion, Microphone, Headset } from '@element-plus/icons-vue'
import speechService from '@/utils/speech'

const route = useRoute()
const router = useRouter()

const interviewId = route.params.id
const messages = ref([])
const userAnswer = ref('')
const isTyping = ref(false)
const chatContainer = ref(null)
let websocket = null
const isEnding = ref(false) // 标记是否正在结束面试

// 语音相关状态
const speechSupported = speechService.checkSupport()
const isRecording = ref(false) // 是否正在录音
const voiceOutputEnabled = ref(false) // 是否启用语音输出
const interimTranscript = ref('') // 临时识别结果

onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (websocket) {
    websocket.close()
  }
  // 清理语音资源
  speechService.destroy()
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
      const question = data.data.question
      messages.value.push({
        role: 'interviewer',
        content: question
      })
      scrollToBottom()

      // 自动播放面试官问题的语音
      speakText(question)
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

// ===== 语音功能 =====

/**
 * 切换语音输入
 */
const toggleVoiceInput = async () => {
  if (!speechSupported.recognition) {
    ElMessage.error('您的浏览器不支持语音识别功能')
    return
  }

  if (isRecording.value) {
    // 停止录音
    stopVoiceInput()
  } else {
    // 开始录音
    try {
      await speechService.initRecognition({
        lang: 'zh-CN',
        continuous: false,
        interimResults: true
      })

      isRecording.value = true
      interimTranscript.value = ''
      ElMessage.info('开始录音，请说出你的回答...')

      speechService.startRecognition({
        onStart: () => {
          console.log('语音识别已启动')
        },
        onResult: (text) => {
          // 最终识别结果
          userAnswer.value = text
          interimTranscript.value = ''
          stopVoiceInput()
        },
        onInterim: (text) => {
          // 临时识别结果
          interimTranscript.value = text
          userAnswer.value = text
        },
        onEnd: () => {
          if (isRecording.value) {
            stopVoiceInput()
          }
        },
        onError: (error) => {
          console.error('语音识别错误:', error)
          ElMessage.error('语音识别失败: ' + error)
          stopVoiceInput()
        }
      })
    } catch (error) {
      console.error('初始化语音识别失败:', error)
      ElMessage.error('无法启动语音识别')
      isRecording.value = false
    }
  }
}

/**
 * 停止语音输入
 */
const stopVoiceInput = () => {
  if (isRecording.value) {
    speechService.stopRecognition()
    isRecording.value = false
    interimTranscript.value = ''
  }
}

/**
 * 切换语音输出
 */
const toggleVoiceOutput = () => {
  if (!speechSupported.synthesis) {
    ElMessage.error('您的浏览器不支持语音合成功能')
    return
  }

  voiceOutputEnabled.value = !voiceOutputEnabled.value
  ElMessage.success(voiceOutputEnabled.value ? '语音输出已开启' : '语音输出已关闭')
}

/**
 * 播放语音
 * @param {string} text - 要播放的文本
 */
const speakText = (text) => {
  if (!voiceOutputEnabled.value || !text || !speechSupported.synthesis) {
    return
  }

  try {
    speechService.speak(text, {
      lang: 'zh-CN',
      rate: 1,
      pitch: 1,
      volume: 1
    }).catch(error => {
      console.error('语音播放失败:', error)
    })
  } catch (error) {
    console.error('语音播放错误:', error)
  }
}
</script>

<style scoped>
/* ===== 主容器 - macOS 风格 ===== */
.interview-room {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-color);
  padding: 20px;
  box-sizing: border-box;
}

.interview-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-color-white);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  border: 1px solid var(--border-color-light);
}

/* ===== 顶部工具栏 - macOS 风格 ===== */
.interview-header {
  padding: 12px 16px;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-color-light);
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
  cursor: pointer;
  transition: all 0.2s;
}

.window-control.close {
  background: var(--danger-color);
}

.window-control.minimize {
  background: var(--warning-color);
}

.window-control.maximize {
  background: var(--success-color);
}

.title-text h1 {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: -0.01em;
}

.end-button {
  padding: 6px 12px;
  background: var(--danger-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.end-button:hover {
  background: #ff453a;
}

.end-button:active {
  opacity: 0.8;
}

/* ===== 聊天容器 ===== */
.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: var(--bg-color-white);
  scroll-behavior: smooth;
}

.chat-container::-webkit-scrollbar {
  width: 8px;
}

.chat-container::-webkit-scrollbar-track {
  background: transparent;
}

.chat-container::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
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
  background: var(--primary-color);
}

.avatar-wrapper.candidate {
  background: var(--success-color);
}

/* ===== 消息内容 ===== */
.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
}

.message-role {
  font-size: 12px;
  color: var(--text-secondary);
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
  background: var(--bg-color-light);
  padding: 12px 16px;
  border-radius: 18px;
  line-height: 1.5;
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 400;
  letter-spacing: -0.01em;
}

.message.interviewer .message-text {
  border-top-left-radius: 4px;
}

.message.candidate .message-text {
  background: var(--primary-color);
  color: white;
  border-top-right-radius: 4px;
}

/* ===== 打字指示器 ===== */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: var(--bg-color-light);
  border-radius: 18px;
  border-top-left-radius: 4px;
  width: fit-content;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-secondary);
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
  background: var(--bg-color-white);
  border-top: 1px solid var(--border-color-light);
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
  color: var(--text-primary);
  background: var(--bg-color-light);
  border: 1px solid transparent;
  border-radius: 10px;
  resize: none;
  transition: all 0.15s ease;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', sans-serif;
  outline: none;
}

.input-field::placeholder {
  color: var(--text-secondary);
}

.input-field:hover {
  background: var(--border-color-light);
}

.input-field:focus {
  background: var(--bg-color-white);
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.input-field:disabled {
  background: var(--bg-color-light);
  cursor: not-allowed;
  opacity: 0.6;
}

/* ===== 输入操作按钮 ===== */
.input-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* ===== 语音控制按钮 ===== */
.voice-controls {
  display: flex;
  gap: 8px;
}

.voice-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--bg-color-light);
  color: var(--text-primary);
  border: 1px solid var(--border-color-light);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.voice-button:hover:not(:disabled) {
  background: var(--border-color-light);
  border-color: var(--border-color);
}

.voice-button:active:not(:disabled) {
  opacity: 0.8;
}

.voice-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.voice-button.recording {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
  animation: recordingPulse 1.5s infinite;
}

.voice-button.active {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

@keyframes recordingPulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.voice-button .el-icon {
  font-size: 14px;
}

.voice-button span {
  font-size: 12px;
}

.send-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--primary-color);
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
  background: var(--primary-dark);
}

.send-button:active:not(:disabled) {
  opacity: 0.8;
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--primary-color);
}

.send-button.loading {
  background: var(--text-secondary);
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

  .voice-controls {
    flex: 1;
  }

  .voice-button {
    flex: 1;
    justify-content: center;
  }
}
</style>
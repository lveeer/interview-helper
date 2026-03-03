<template>
  <div class="video-interview-room">
    <!-- 视频布局区域 -->
    <div class="video-layout">
      <!-- 主视频区域 - AI 面试官 -->
      <div class="main-video-area">
        <div class="ai-interviewer-video">
          <!-- Lottie 动画容器 -->
          <div class="ai-avatar-container" ref="avatarContainer">
            <div 
              ref="lottieContainer" 
              class="lottie-animation"
              :class="{ 'is-speaking': isSpeaking }"
            ></div>
            <!-- 等待状态叠加层 -->
            <div v-if="!isSpeaking && !isTyping" class="idle-overlay">
              <div class="idle-pulse"></div>
            </div>
          </div>
          <div class="ai-name">AI 面试官</div>
          <div class="ai-status">
            <span v-if="isSpeaking" class="status-speaking">正在提问</span>
            <span v-else-if="isTyping" class="status-thinking">思考中...</span>
            <span v-else class="status-waiting">等待回答</span>
          </div>
        </div>
        
        <!-- 当前问题显示 -->
        <div v-if="currentQuestion" class="current-question-overlay">
          <div class="question-content">
            <QuestionDifficultyBadge
              v-if="currentQuestion.difficulty"
              :difficulty="currentQuestion.difficulty"
            />
            <FollowupTypeBadge
              v-if="currentQuestion.followup_type"
              :type="currentQuestion.followup_type"
              :count="currentQuestion.followup_count"
              :max-count="currentQuestion.max_followup_count"
            />
            <p>{{ currentQuestion.content }}</p>
          </div>
        </div>
      </div>

      <!-- 小视频窗口 - 用户自己 -->
      <div class="self-video-container">
        <video
          ref="localVideo"
          class="self-video"
          autoplay
          muted
          playsinline
        ></video>
        <div v-if="!cameraEnabled" class="video-off-overlay">
          <el-icon class="video-off-icon"><VideoCamera /></el-icon>
          <span>{{ hasMediaDevice ? '摄像头已关闭' : '摄像头不可用' }}</span>
        </div>
        <div class="self-video-name">
          <el-icon v-if="!micEnabled"><Mute /></el-icon>
          <span>{{ micEnabled ? '我' : (hasMediaDevice ? '已静音' : '麦克风不可用') }}</span>
        </div>
      </div>
    </div>

    <!-- 底部控制栏 -->
    <div class="control-bar">
      <div class="control-left">
        <ConnectionStatus
          :status="connectionStatus"
          :latency="connectionLatency"
          :reconnect-attempts="reconnectAttempts"
          @reconnect="handleReconnect"
        />
      </div>
      
      <div class="control-center">
        <!-- 麦克风控制 -->
        <button
          class="control-button"
          :class="{ active: !micEnabled }"
          @click="toggleMic"
          :title="micEnabled ? '关闭麦克风' : '开启麦克风'"
        >
          <el-icon>
            <component :is="micEnabled ? 'Microphone' : 'Mute'" />
          </el-icon>
        </button>

        <!-- 摄像头控制 -->
        <button
          class="control-button"
          :class="{ active: !cameraEnabled }"
          @click="toggleCamera"
          :title="cameraEnabled ? '关闭摄像头' : '开启摄像头'"
        >
          <el-icon>
            <component :is="cameraEnabled ? 'VideoCamera' : 'VideoCameraFilled'" />
          </el-icon>
        </button>

        <!-- 语音输出控制 -->
        <button
          class="control-button"
          :class="{ active: voiceOutputEnabled }"
          @click="toggleVoiceOutput"
          :title="voiceOutputEnabled ? '关闭语音播放' : '开启语音播放'"
        >
          <el-icon><Headset /></el-icon>
        </button>

        <!-- 结束面试 -->
        <button class="control-button end" @click="handleEnd" :disabled="isEnding">
          <el-icon><SwitchButton /></el-icon>
        </button>
      </div>

      <div class="control-right">
        <span class="interview-duration">{{ formattedDuration }}</span>
      </div>
    </div>

    <!-- 回答输入面板（可折叠） -->
    <div class="answer-panel" :class="{ expanded: isAnswerPanelExpanded }">
      <div class="panel-header" @click="isAnswerPanelExpanded = !isAnswerPanelExpanded">
        <span>回答面板</span>
        <el-icon><component :is="isAnswerPanelExpanded ? 'ArrowDown' : 'ArrowUp'" /></el-icon>
      </div>
      <div class="panel-content" v-show="isAnswerPanelExpanded">
        <div class="chat-messages" ref="chatContainer">
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message-item', message.role]"
          >
            <span class="message-role">{{ message.role === 'interviewer' ? '面试官' : '你' }}</span>
            <span class="message-text">{{ message.content }}</span>
          </div>
          <div v-if="isTyping" class="typing-hint">
            <el-icon class="loading-icon"><Loading /></el-icon>
            <span>面试官正在思考...</span>
          </div>
        </div>
        <div class="input-row">
          <textarea
            v-model="userAnswer"
            class="answer-input"
            :rows="2"
            placeholder="输入你的回答..."
            :disabled="isTyping"
            @keyup.ctrl.enter="sendAnswer"
          ></textarea>
          <div class="input-actions">
            <button
              class="voice-input-btn"
              :class="{ recording: isRecording }"
              :disabled="isTyping"
              @click="toggleVoiceInput"
            >
              <el-icon><Microphone /></el-icon>
            </button>
            <button
              class="send-btn"
              :disabled="isTyping || !userAnswer.trim()"
              @click="sendAnswer"
            >
              <el-icon><Promotion /></el-icon>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Microphone, Mute, VideoCamera, VideoCameraFilled, 
  Headset, SwitchButton, ArrowUp, ArrowDown, Loading, Promotion 
} from '@element-plus/icons-vue'
import lottie from 'lottie-web'
import speechService from '@/utils/speech'
import WebSocketClient from '@/utils/websocket'
import ConnectionStatus from '@/components/ConnectionStatus.vue'
import QuestionDifficultyBadge from '@/components/QuestionDifficultyBadge.vue'
import FollowupTypeBadge from '@/components/FollowupTypeBadge.vue'

const route = useRoute()
const router = useRouter()

const interviewId = route.params.id
const messages = ref([])
const userAnswer = ref('')
const isTyping = ref(false)
const chatContainer = ref(null)
let wsClient = null
const isEnding = ref(false)

// Lottie 动画相关
const lottieContainer = ref(null)
const avatarContainer = ref(null)
let lottieAnimation = null
const isSpeaking = ref(false)

// 动画 URL
const SPEAKING_ANIMATION_URL = 'https://assets2.lottiefiles.com/packages/lf20_vatpKHGdo4.json'

// WebSocket 连接状态
const connectionStatus = ref('disconnected')
const connectionLatency = ref(0)
const reconnectAttempts = ref(0)

// 视频相关状态
const localVideo = ref(null)
let mediaStream = null
const cameraEnabled = ref(true)
const micEnabled = ref(true)
const hasMediaDevice = ref(true) // 标记设备是否可用

// 当前显示的问题
const currentQuestion = ref(null)

// 面试时长
const interviewStartTime = ref(Date.now())
const elapsedSeconds = ref(0)
let durationTimer = null

// 答面板展开状态
const isAnswerPanelExpanded = ref(true)

// 语音相关状态
const speechSupported = speechService.checkSupport()
const isRecording = ref(false)
const voiceOutputEnabled = ref(true) // 视频模式默认开启语音输出

const formattedDuration = computed(() => {
  const minutes = Math.floor(elapsedSeconds.value / 60)
  const seconds = elapsedSeconds.value % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

onMounted(async () => {
  // 启动时长计时器
  durationTimer = setInterval(() => {
    elapsedSeconds.value = Math.floor((Date.now() - interviewStartTime.value) / 1000)
  }, 1000)

  // 初始化 Lottie 动画
  initLottieAnimation()

  // 初始化摄像头和麦克风
  await initMediaDevices()
  
  // 连接 WebSocket
  connectWebSocket()
})

onUnmounted(() => {
  // 清理计时器
  if (durationTimer) {
    clearInterval(durationTimer)
  }
  
  // 关闭 WebSocket
  if (wsClient) {
    wsClient.close()
  }
  
  // 关闭媒体流
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
  }
  
  // 清理 Lottie 动画
  if (lottieAnimation) {
    lottieAnimation.destroy()
  }
  
  // 清理语音资源
  speechService.destroy()
})

/**
 * 初始化 Lottie 动画
 */
const initLottieAnimation = () => {
  if (!lottieContainer.value) return
  
  lottieAnimation = lottie.loadAnimation({
    container: lottieContainer.value,
    renderer: 'svg',
    loop: true,
    autoplay: false,
    path: SPEAKING_ANIMATION_URL
  })
  
  lottieAnimation.addEventListener('DOMLoaded', () => {
    console.log('Lottie 动画加载完成')
  })
  
  lottieAnimation.addEventListener('error', (error) => {
    console.error('Lottie 动画加载失败:', error)
  })
}

/**
 * 播放说话动画
 */
const playSpeakingAnimation = () => {
  if (lottieAnimation) {
    isSpeaking.value = true
    lottieAnimation.play()
  }
}

/**
 * 停止说话动画
 */
const stopSpeakingAnimation = () => {
  if (lottieAnimation) {
    isSpeaking.value = false
    lottieAnimation.stop()
  }
}

/**
 * 初始化摄像头和麦克风
 */
const initMediaDevices = async () => {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true
    })
    
    if (localVideo.value) {
      localVideo.value.srcObject = mediaStream
    }
    
    hasMediaDevice.value = true
    ElMessage.success('摄像头和麦克风已开启')
  } catch (error) {
    console.warn('获取媒体设备失败:', error)
    
    // 获取失败，设置为黑屏模式
    hasMediaDevice.value = false
    cameraEnabled.value = false
    micEnabled.value = false
    
    // 显示友好的提示
    ElMessage.warning('视频面试将以黑屏模式进行，你仍可通过文字回答问题')
  }
}

/**
 * 切换麦克风
 */
const toggleMic = () => {
  if (!hasMediaDevice.value) {
    ElMessage.warning('麦克风不可用')
    return
  }
  if (mediaStream) {
    const audioTrack = mediaStream.getAudioTracks()[0]
    if (audioTrack) {
      audioTrack.enabled = !audioTrack.enabled
      micEnabled.value = audioTrack.enabled
      ElMessage.success(micEnabled.value ? '麦克风已开启' : '麦克风已关闭')
    }
  }
}

/**
 * 切换摄像头
 */
const toggleCamera = async () => {
  if (!hasMediaDevice.value) {
    ElMessage.warning('摄像头不可用')
    return
  }
  if (mediaStream) {
    const videoTrack = mediaStream.getVideoTracks()[0]
    if (videoTrack) {
      videoTrack.enabled = !videoTrack.enabled
      cameraEnabled.value = videoTrack.enabled
      ElMessage.success(cameraEnabled.value ? '摄像头已开启' : '摄像头已关闭')
    }
  }
}

/**
 * 连接 WebSocket
 */
const connectWebSocket = () => {
  const wsUrl = `ws://localhost:8000/api/interview/ws/${interviewId}`

  wsClient = new WebSocketClient({
    url: wsUrl,
    heartbeatInterval: 30000,
    reconnectInterval: 1000,
    maxReconnectAttempts: 5,
    onOpen: () => {
      console.log('WebSocket 连接成功')
    },
    onMessage: (data) => {
      const messageData = JSON.parse(data)

      if (messageData.type === 'question' || messageData.type === 'followup') {
        isTyping.value = false
        const question = messageData.data.question
        const message = {
          role: 'interviewer',
          content: question
        }

        if (messageData.data.difficulty) {
          message.difficulty = messageData.data.difficulty
        }
        if (messageData.data.followup_type) {
          message.followup_type = messageData.data.followup_type
          message.followup_count = messageData.data.followup_count || 0
          message.max_followup_count = messageData.data.max_followup_count || 3
        }

        messages.value.push(message)
        
        // 更新当前显示的问题
        currentQuestion.value = message
        
        scrollToBottom()

        // 自动播放面试官问题的语音
        speakText(question)
      } else if (messageData.type === 'end') {
        isTyping.value = false
        handleInterviewEnd()
      }
    },
    onError: (error) => {
      console.error('WebSocket 错误:', error)
      ElMessage.error('连接错误，请刷新页面重试')
    },
    onClose: () => {
      if (isEnding.value) {
        handleInterviewEnd()
      }
    },
    onReconnect: (attempts) => {
      console.log(`WebSocket 重连尝试 ${attempts}`)
    },
    onStatusChange: (status) => {
      connectionStatus.value = status
      connectionLatency.value = wsClient.getLatency()
      reconnectAttempts.value = wsClient.getReconnectAttempts()
    }
  })

  wsClient.connect()
}

/**
 * 发送回答
 */
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
  
  // 清空当前问题
  currentQuestion.value = null
  userAnswer.value = ''
  scrollToBottom()

  isTyping.value = true

  if (wsClient && wsClient.getStatus() === 'connected') {
    wsClient.send(JSON.stringify({
      type: 'answer',
      answer: answer,
      answer_type: 'text'
    }))
  } else {
    ElMessage.error('连接已断开，请刷新页面')
  }
}

/**
 * 结束面试
 */
const handleEnd = async () => {
  try {
    await ElMessageBox.confirm('确定要结束面试吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    isEnding.value = true
    ElMessage.info('正在结束面试...')

    // 发送结束消息
    if (wsClient && wsClient.getStatus() === 'connected') {
      wsClient.send(JSON.stringify({ type: 'end' }))
    }

    // 关闭 WebSocket
    if (wsClient) {
      wsClient.close()
    }

    handleInterviewEnd()
  } catch {
    // 用户取消
  }
}

/**
 * 处理面试结束
 */
const handleInterviewEnd = () => {
  // 关闭媒体流
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
  }
  
  ElMessage.success('面试已完成，报告生成中，请稍后在面试列表查看')
  setTimeout(() => {
    router.push('/interview')
  }, 2000)
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

// ===== 语音功能 =====

const toggleVoiceInput = async () => {
  if (!speechSupported.recognition) {
    ElMessage.error('您的浏览器不支持语音识别功能')
    return
  }

  if (isRecording.value) {
    stopVoiceInput()
  } else {
    try {
      await speechService.initRecognition({
        lang: 'zh-CN',
        continuous: false,
        interimResults: true
      })

      isRecording.value = true
      ElMessage.info('开始录音，请说出你的回答...')

      speechService.startRecognition({
        onStart: () => {
          console.log('语音识别已启动')
        },
        onResult: (text) => {
          userAnswer.value = text
          stopVoiceInput()
        },
        onInterim: (text) => {
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

const stopVoiceInput = () => {
  if (isRecording.value) {
    speechService.stopRecognition()
    isRecording.value = false
  }
}

const toggleVoiceOutput = () => {
  if (!speechSupported.synthesis) {
    ElMessage.error('您的浏览器不支持语音合成功能')
    return
  }

  voiceOutputEnabled.value = !voiceOutputEnabled.value
  ElMessage.success(voiceOutputEnabled.value ? '语音播放已开启' : '语音播放已关闭')
}

const speakText = (text) => {
  if (!voiceOutputEnabled.value || !text || !speechSupported.synthesis) {
    return
  }

  // 先停止之前的语音和动画
  speechService.stopSpeaking()
  stopSpeakingAnimation()

  try {
    // 使用浏览器原生 SpeechSynthesis 以便更好地控制动画
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'zh-CN'
    utterance.rate = 1
    utterance.pitch = 1
    utterance.volume = 1

    // 尝试获取中文语音
    const voices = window.speechSynthesis.getVoices()
    const chineseVoice = voices.find(voice => voice.lang.includes('zh'))
    if (chineseVoice) {
      utterance.voice = chineseVoice
    }

    utterance.onstart = () => {
      console.log('开始播放语音')
      playSpeakingAnimation()
    }

    utterance.onend = () => {
      console.log('语音播放完成')
      stopSpeakingAnimation()
    }

    utterance.onerror = (event) => {
      console.error('语音合成错误:', event.error)
      stopSpeakingAnimation()
    }

    window.speechSynthesis.speak(utterance)
  } catch (error) {
    console.error('语音播放错误:', error)
    stopSpeakingAnimation()
  }
}

const handleReconnect = () => {
  if (wsClient) {
    wsClient.reconnect()
  }
}
</script>

<style scoped>
.video-interview-room {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #1a1a2e;
  color: white;
  overflow: hidden;
}

/* ===== 视频布局 ===== */
.video-layout {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

/* ===== 主视频区域 - AI 面试官 ===== */
.main-video-area {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-interviewer-video {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.ai-avatar-container {
  position: relative;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
  overflow: hidden;
}

.lottie-animation {
  width: 100%;
  height: 100%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.lottie-animation.is-speaking {
  opacity: 1;
}

/* 等待状态叠加层 */
.idle-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.idle-pulse {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  animation: pulse 2s infinite ease-in-out;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.4;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
}

.ai-name {
  font-size: 18px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.ai-status {
  font-size: 14px;
  padding: 6px 16px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.status-speaking {
  color: #4ade80;
}

.status-thinking {
  color: #fbbf24;
}

.status-waiting {
  color: rgba(255, 255, 255, 0.6);
}

/* 移除旧的 speaking-indicator 样式 */
.speaking-indicator {
  display: none;
}

@keyframes speaking {
  0%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  50% {
    transform: translateY(-8px);
    opacity: 1;
  }
}

/* ===== 当前问题叠加层 ===== */
.current-question-overlay {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 40px);
  max-width: 800px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.question-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.question-content p {
  margin: 0;
  font-size: 16px;
  line-height: 1.6;
  color: white;
}

/* ===== 小视频窗口 - 用户自己 ===== */
.self-video-container {
  position: absolute;
  bottom: 20px;
  right: 20px;
  width: 200px;
  height: 150px;
  border-radius: 12px;
  overflow: hidden;
  background: #2d2d44;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.self-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1);
}

.video-off-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #2d2d44;
}

.video-off-icon {
  font-size: 32px;
  color: rgba(255, 255, 255, 0.5);
}

.video-off-overlay span {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.self-video-name {
  position: absolute;
  bottom: 8px;
  left: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 4px;
  font-size: 12px;
}

/* ===== 底部控制栏 ===== */
.control-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

.control-left {
  min-width: 150px;
}

.control-center {
  display: flex;
  align-items: center;
  gap: 12px;
}

.control-right {
  min-width: 150px;
  text-align: right;
}

.interview-duration {
  font-size: 18px;
  font-weight: 600;
  font-family: 'SF Mono', 'Consolas', monospace;
  color: rgba(255, 255, 255, 0.9);
}

.control-button {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.control-button:hover {
  background: rgba(255, 255, 255, 0.25);
}

.control-button:active {
  transform: scale(0.95);
}

.control-button.active {
  background: #ff4757;
}

.control-button.end {
  background: #ff4757;
  width: 56px;
  height: 56px;
}

.control-button.end:hover {
  background: #ff6b7a;
}

.control-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-button .el-icon {
  font-size: 22px;
}

/* ===== 回答输入面板 ===== */
.answer-panel {
  position: absolute;
  bottom: 80px;
  left: 20px;
  right: 240px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.answer-panel.expanded {
  max-height: 300px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.05);
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.panel-header:hover {
  background: rgba(255, 255, 255, 0.1);
}

.panel-content {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-messages {
  max-height: 120px;
  overflow-y: auto;
  padding: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.chat-messages::-webkit-scrollbar {
  width: 4px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.message-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 13px;
}

.message-item:last-child {
  margin-bottom: 0;
}

.message-item.candidate {
  flex-direction: row-reverse;
}

.message-role {
  color: rgba(255, 255, 255, 0.5);
  font-size: 11px;
  flex-shrink: 0;
}

.message-text {
  background: rgba(255, 255, 255, 0.1);
  padding: 6px 10px;
  border-radius: 8px;
  line-height: 1.4;
}

.message-item.interviewer .message-text {
  background: rgba(102, 126, 234, 0.3);
}

.message-item.candidate .message-text {
  background: rgba(0, 200, 83, 0.3);
}

.typing-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.input-row {
  display: flex;
  gap: 8px;
}

.answer-input {
  flex: 1;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: white;
  font-size: 14px;
  line-height: 1.4;
  resize: none;
  outline: none;
  transition: border-color 0.2s;
}

.answer-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.answer-input:focus {
  border-color: rgba(102, 126, 234, 0.5);
}

.answer-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.voice-input-btn,
.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.voice-input-btn:hover:not(:disabled),
.send-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.25);
}

.voice-input-btn:disabled,
.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.voice-input-btn.recording {
  background: #ff4757;
  animation: recordingPulse 1s infinite;
}

@keyframes recordingPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.send-btn {
  background: #667eea;
}

.send-btn:hover:not(:disabled) {
  background: #7c8ff5;
}

/* ===== 响应式设计 ===== */
@media (max-width: 768px) {
  .self-video-container {
    width: 120px;
    height: 90px;
    bottom: 70px;
    right: 10px;
  }

  .answer-panel {
    left: 10px;
    right: 130px;
    bottom: 70px;
  }

  .control-bar {
    padding: 12px 16px;
  }

  .control-button {
    width: 40px;
    height: 40px;
  }

  .control-button.end {
    width: 48px;
    height: 48px;
  }

  .control-button .el-icon {
    font-size: 18px;
  }

  .ai-avatar {
    width: 80px;
    height: 80px;
  }

  .avatar-icon {
    font-size: 36px;
  }
}
</style>

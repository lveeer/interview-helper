<template>
  <div class="video-interview-room" :class="{ 'sidebar-open': isSidebarOpen }">
    <!-- 背景动画 -->
    <div class="bg-animation">
      <div class="bg-orb"></div>
      <div class="bg-orb"></div>
      <div class="bg-orb"></div>
    </div>

    <!-- 顶部栏 -->
    <header class="top-bar">
      <div class="meeting-info">
        <span class="meeting-title">{{ meetingTitle }}</span>
        <span class="meeting-id">会议号：{{ interviewId }}</span>
        <div class="meeting-status">
          <div v-if="isRecording" class="recording-indicator">
            <span class="recording-dot"></span>
            <span>录制中</span>
          </div>
        </div>
      </div>
      <div class="meeting-status">
        <span class="duration">{{ formattedDuration }}</span>
      </div>
      <div class="top-actions">
        <button class="top-btn" @click="showSettingsPanel = true" title="设置">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        </button>
        <button class="top-btn" @click="copyMeetingLink" title="邀请">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="8.5" cy="7" r="4"/>
            <line x1="20" y1="8" x2="20" y2="14"/>
            <line x1="23" y1="11" x2="17" y2="11"/>
          </svg>
        </button>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="video-grid">
        <!-- AI面试官视频 -->
        <div class="video-container" :class="{ speaking: isAISpeaking }">
          <div class="video-simulation">
            <!-- Lottie 动画 -->
            <div ref="lottieContainer" class="ai-avatar-lottie" :class="{ visible: isAISpeaking }"></div>
            
            <!-- 等待状态头像 -->
            <div v-if="!isAISpeaking" class="video-placeholder">
              <div class="avatar interviewer">AI</div>
              <span class="participant-name">AI面试官</span>
            </div>
            
            <!-- 音量波形 -->
            <div v-if="isAISpeaking" class="video-wave">
              <div class="video-wave-bar" style="--wave-height: 25px; animation-delay: 0s;"></div>
              <div class="video-wave-bar" style="--wave-height: 35px; animation-delay: 0.1s;"></div>
              <div class="video-wave-bar" style="--wave-height: 20px; animation-delay: 0.2s;"></div>
              <div class="video-wave-bar" style="--wave-height: 40px; animation-delay: 0.3s;"></div>
              <div class="video-wave-bar" style="--wave-height: 30px; animation-delay: 0.4s;"></div>
              <div class="video-wave-bar" style="--wave-height: 25px; animation-delay: 0.5s;"></div>
              <div class="video-wave-bar" style="--wave-height: 35px; animation-delay: 0.6s;"></div>
              <div class="video-wave-bar" style="--wave-height: 20px; animation-delay: 0.7s;"></div>
            </div>
          </div>
          
          <div class="video-label">
            <span>AI面试官</span>
            <div class="mic-status unmuted">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" y1="19" x2="12" y2="23"/>
                <line x1="8" y1="23" x2="16" y2="23"/>
              </svg>
              <div v-if="isAISpeaking" class="volume-wave">
                <div class="volume-bar"></div>
                <div class="volume-bar"></div>
                <div class="volume-bar"></div>
                <div class="volume-bar"></div>
              </div>
            </div>
          </div>
          
          <!-- 当前问题悬浮显示 -->
          <div v-if="currentQuestion && subtitleEnabled" class="question-toast">
            <div class="toast-content">
              <div class="toast-header">
                <QuestionDifficultyBadge v-if="currentQuestion.difficulty" :difficulty="currentQuestion.difficulty" />
                <FollowupTypeBadge v-if="currentQuestion.followup_type" :type="currentQuestion.followup_type" :count="currentQuestion.followup_count" :max-count="currentQuestion.max_followup_count" />
              </div>
              <p class="toast-text">{{ currentQuestion.content }}</p>
            </div>
          </div>
        </div>

        <!-- 候选人视频（自己） -->
        <div class="video-container" :class="{ speaking: isUserSpeaking && micEnabled }">
          <div class="video-simulation">
            <!-- 实际视频 -->
            <video
              ref="localVideo"
              class="self-video-full"
              autoplay
              muted
              playsinline
              v-show="cameraEnabled"
            ></video>
            
            <!-- 视频关闭状态 -->
            <div v-if="!cameraEnabled" class="video-placeholder">
              <div class="avatar candidate">我</div>
              <span class="participant-name">我</span>
            </div>
          </div>
          
          <div class="video-label">
            <span>我</span>
            <div class="mic-status" :class="micEnabled ? 'unmuted' : 'muted'">
              <svg v-if="micEnabled" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" y1="19" x2="12" y2="23"/>
                <line x1="8" y1="23" x2="16" y2="23"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <line x1="1" y1="1" x2="23" y2="23"/>
                <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"/>
                <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"/>
                <line x1="12" y1="19" x2="12" y2="23"/>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 底部控制栏 - 腾讯会议风格 -->
    <footer class="control-bar">
      <div class="ctrl-btn-group">
        <!-- 静音按钮 -->
        <button class="ctrl-btn" :class="micEnabled ? 'active' : 'danger'" @click="toggleMic">
          <div class="ctrl-icon-box">
            <svg v-if="micEnabled" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
              <line x1="12" y1="19" x2="12" y2="23"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="1" y1="1" x2="23" y2="23"/>
              <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"/>
              <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"/>
              <line x1="12" y1="19" x2="12" y2="23"/>
            </svg>
          </div>
          <span class="ctrl-label">{{ micEnabled ? '静音' : '解除静音' }}</span>
        </button>

        <!-- 视频按钮 -->
        <button class="ctrl-btn" :class="cameraEnabled ? 'active' : 'danger'" @click="toggleCamera">
          <div class="ctrl-icon-box">
            <svg v-if="cameraEnabled" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 7l-7 5 7 5V7z"/>
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M16 16v1a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h2m5.66 0H14a2 2 0 0 1 2 2v3.34l1 1L23 7v10"/>
              <line x1="1" y1="1" x2="23" y2="23"/>
            </svg>
          </div>
          <span class="ctrl-label">{{ cameraEnabled ? '停止视频' : '开启视频' }}</span>
        </button>

        <!-- 共享屏幕按钮 -->
        <button class="ctrl-btn" :class="isScreenSharing ? 'active' : 'default'" @click="toggleScreenShare">
          <div class="ctrl-icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
              <line x1="8" y1="21" x2="16" y2="21"/>
              <line x1="12" y1="17" x2="12" y2="21"/>
            </svg>
          </div>
          <span class="ctrl-label">{{ isScreenSharing ? '停止共享' : '共享屏幕' }}</span>
        </button>

        <!-- 成员按钮 -->
        <button class="ctrl-btn default" :class="(isSidebarOpen && activeTab === 'member') ? 'active' : ''" @click="toggleMembers">
          <div class="ctrl-icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <span class="ctrl-label">成员</span>
        </button>

        <!-- 聊天按钮 -->
        <button class="ctrl-btn default" :class="(isSidebarOpen && activeTab === 'chat') ? 'active' : ''" @click="toggleChat">
          <div class="ctrl-icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            <span v-if="unreadCount > 0" class="ctrl-badge">{{ unreadCount }}</span>
          </div>
          <span class="ctrl-label">聊天</span>
        </button>

        <!-- 字幕开关 -->
        <button class="ctrl-btn" :class="subtitleEnabled ? 'active' : 'default'" @click="toggleSubtitle">
          <div class="ctrl-icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="4" width="20" height="16" rx="2"/>
              <path d="M6 12h4"/>
              <path d="M6 16h8"/>
              <path d="M14 12h4"/>
            </svg>
          </div>
          <span class="ctrl-label">{{ subtitleEnabled ? '关闭字幕' : '开启字幕' }}</span>
        </button>
      </div>

      <!-- 离开按钮 -->
      <button class="ctrl-btn leave-btn" @click="showLeaveModal = true">
        <div class="ctrl-icon-box">离开会议</div>
      </button>
    </footer>

    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ open: isSidebarOpen }">
      <div class="sidebar-tabs">
        <button class="sidebar-tab" :class="{ active: activeTab === 'member' }" @click="switchTab('member')">
          成员
          <span class="tab-badge">{{ participantCount }}</span>
        </button>
        <button class="sidebar-tab" :class="{ active: activeTab === 'chat' }" @click="switchTab('chat')">
          聊天
          <span v-if="unreadCount > 0" class="tab-badge">{{ unreadCount }}</span>
        </button>
      </div>
      
      <div class="sidebar-content">
        <!-- 成员列表 -->
        <div class="participant-list" v-show="activeTab === 'member'">
          <div class="participant-item" :class="{ speaking: isAISpeaking }">
            <div class="participant-avatar interviewer">AI</div>
            <div class="participant-info">
              <div class="participant-name-text">AI面试官</div>
              <div class="participant-role">主持人</div>
            </div>
            <div class="participant-actions">
              <button class="participant-action-btn" :class="{ muted: !isAISpeaking }">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                  <line x1="12" y1="19" x2="12" y2="23"/>
                </svg>
              </button>
              <button class="participant-action-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <path d="M23 7l-7 5 7 5V7z"/>
                  <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                </svg>
              </button>
            </div>
          </div>
          
          <div class="participant-item" :class="{ speaking: isUserSpeaking && micEnabled }">
            <div class="participant-avatar candidate">我</div>
            <div class="participant-info">
              <div class="participant-name-text">我</div>
              <div class="participant-role">参会者</div>
            </div>
            <div class="participant-actions">
              <button class="participant-action-btn" :class="{ muted: !micEnabled }">
                <svg v-if="micEnabled" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                  <line x1="12" y1="19" x2="12" y2="23"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <line x1="1" y1="1" x2="23" y2="23"/>
                  <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"/>
                  <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"/>
                  <line x1="12" y1="19" x2="12" y2="23"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
        
        <!-- 聊天面板 -->
        <div class="chat-panel" v-show="activeTab === 'chat'">
          <div class="chat-messages" ref="chatContainer">
            <div
              v-for="(message, index) in messages"
              :key="index"
              class="chat-message"
            >
              <div class="chat-sender">{{ message.role === 'interviewer' ? 'AI面试官' : '我' }}</div>
              <div class="chat-text">{{ message.content }}</div>
            </div>
            <div v-if="isTyping" class="chat-message">
              <div class="chat-sender">AI面试官</div>
              <div class="chat-text typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
          <div class="chat-input-area">
            <div class="chat-input-wrapper">
              <input 
                type="text" 
                class="chat-input" 
                v-model="userAnswer"
                placeholder="发送消息给所有人"
                @keypress.enter="sendMessage"
                :disabled="isTyping"
              >
              <button class="chat-send-btn" @click="sendMessage" :disabled="isTyping || !userAnswer.trim()">发送</button>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- 设置面板 -->
    <div class="settings-overlay" :class="{ open: showSettingsPanel }" @click="showSettingsPanel = false"></div>
    <div class="settings-panel" :class="{ open: showSettingsPanel }">
      <div class="settings-title">
        <span>设置</span>
        <button class="settings-close" @click="showSettingsPanel = false">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
      <div class="setting-item">
        <span class="setting-label">麦克风</span>
        <select class="setting-select" v-model="selectedMic">
          <option value="">默认麦克风</option>
          <option v-for="device in audioDevices" :key="device.deviceId" :value="device.deviceId">
            {{ device.label || '麦克风' }}
          </option>
        </select>
      </div>
      <div class="setting-item">
        <span class="setting-label">扬声器</span>
        <select class="setting-select" v-model="selectedSpeaker">
          <option value="">默认扬声器</option>
          <option v-for="device in speakerDevices" :key="device.deviceId" :value="device.deviceId">
            {{ device.label || '扬声器' }}
          </option>
        </select>
      </div>
      <div class="setting-item">
        <span class="setting-label">摄像头</span>
        <select class="setting-select" v-model="selectedCamera">
          <option value="">默认摄像头</option>
          <option v-for="device in videoDevices" :key="device.deviceId" :value="device.deviceId">
            {{ device.label || '摄像头' }}
          </option>
        </select>
      </div>
      <div class="setting-item">
        <span class="setting-label">语音播放</span>
        <select class="setting-select" v-model="voiceOutputEnabled">
          <option :value="true">开启</option>
          <option :value="false">关闭</option>
        </select>
      </div>
    </div>

    <!-- 离开确认弹窗 -->
    <div class="settings-overlay" :class="{ open: showLeaveModal }"></div>
    <div class="leave-modal" :class="{ open: showLeaveModal }">
      <div class="leave-modal-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="28" height="28">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
      </div>
      <div class="leave-modal-title">确定离开会议？</div>
      <div class="leave-modal-desc">离开后需要重新加入会议</div>
      <div class="leave-modal-actions">
        <button class="leave-modal-btn cancel" @click="showLeaveModal = false">取消</button>
        <button class="leave-modal-btn confirm" @click="handleEnd" :disabled="isEnding">
          {{ isEnding ? '离开中...' : '离开会议' }}
        </button>
      </div>
    </div>

    <!-- 连接状态指示器 -->
    <ConnectionStatus
      v-if="connectionStatus !== 'connected'"
      :status="connectionStatus"
      :latency="connectionLatency"
      :reconnect-attempts="reconnectAttempts"
      @reconnect="handleReconnect"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import lottie from 'lottie-web'
import speechService from '@/utils/speech'
import WebSocketClient from '@/utils/websocket'
import ConnectionStatus from '@/components/ConnectionStatus.vue'
import QuestionDifficultyBadge from '@/components/QuestionDifficultyBadge.vue'
import FollowupTypeBadge from '@/components/FollowupTypeBadge.vue'

const route = useRoute()
const router = useRouter()

const interviewId = route.params.id || '888 666 521'
const meetingTitle = ref('AI面试房间')
const messages = ref([])
const userAnswer = ref('')
const isTyping = ref(false)
const chatContainer = ref(null)
let wsClient = null
const isEnding = ref(false)

// Lottie 动画相关
const lottieContainer = ref(null)
let lottieAnimation = null
const isAISpeaking = ref(false)
const isUserSpeaking = ref(false)

// 动画 URL
const SPEAKING_ANIMATION_URL = 'https://assets2.lottiefiles.com/packages/lf20_vatpKHGdo4.json'

// WebSocket 连接状态
const connectionStatus = ref('disconnected')
const connectionLatency = ref(0)
const reconnectAttempts = ref(0)

// 视频相关状态
const localVideo = ref(null)
let mediaStream = null
let screenStream = null
const cameraEnabled = ref(true)
const micEnabled = ref(true)
const hasMediaDevice = ref(true)

// 设备选择
const audioDevices = ref([])
const videoDevices = ref([])
const speakerDevices = ref([])
const selectedMic = ref('')
const selectedCamera = ref('')
const selectedSpeaker = ref('')

// 当前显示的问题
const currentQuestion = ref(null)

// 面试时长
const interviewStartTime = ref(Date.now())
const elapsedSeconds = ref(0)
let durationTimer = null

// 面板状态
const isSidebarOpen = ref(false)
const activeTab = ref('member')
const showSettingsPanel = ref(false)
const showLeaveModal = ref(false)
const isScreenSharing = ref(false)
const isRecording = ref(false)
const subtitleEnabled = ref(true)

// 语音相关状态
const speechSupported = speechService.checkSupport()
const isRecordingVoice = ref(false)
const voiceOutputEnabled = ref(true)

// 未读消息计数
const unreadCount = ref(0)

// 参与者数量
const participantCount = ref(2)

const formattedDuration = computed(() => {
  const hours = Math.floor(elapsedSeconds.value / 3600)
  const minutes = Math.floor((elapsedSeconds.value % 3600) / 60)
  const seconds = elapsedSeconds.value % 60
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

onMounted(async () => {
  durationTimer = setInterval(() => {
    elapsedSeconds.value = Math.floor((Date.now() - interviewStartTime.value) / 1000)
  }, 1000)

  initLottieAnimation()
  await initMediaDevices()
  await enumerateDevices()
  connectWebSocket()
})

onUnmounted(() => {
  if (durationTimer) clearInterval(durationTimer)
  if (wsClient) wsClient.close()
  if (mediaStream) mediaStream.getTracks().forEach(track => track.stop())
  if (screenStream) screenStream.getTracks().forEach(track => track.stop())
  if (lottieAnimation) lottieAnimation.destroy()
  speechService.destroy()
})

const initLottieAnimation = () => {
  if (!lottieContainer.value) return
  
  lottieAnimation = lottie.loadAnimation({
    container: lottieContainer.value,
    renderer: 'svg',
    loop: true,
    autoplay: false,
    path: SPEAKING_ANIMATION_URL
  })
}

const playSpeakingAnimation = () => {
  if (lottieAnimation) {
    isAISpeaking.value = true
    lottieAnimation.play()
  }
}

const stopSpeakingAnimation = () => {
  if (lottieAnimation) {
    isAISpeaking.value = false
    lottieAnimation.stop()
  }
}

const enumerateDevices = async () => {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices()
    audioDevices.value = devices.filter(d => d.kind === 'audioinput')
    videoDevices.value = devices.filter(d => d.kind === 'videoinput')
    speakerDevices.value = devices.filter(d => d.kind === 'audiooutput')
  } catch (error) {
    console.warn('枚举设备失败:', error)
  }
}

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
    
    // 监听音频轨道来检测用户是否在说话
    const audioTrack = mediaStream.getAudioTracks()[0]
    if (audioTrack) {
      const audioContext = new AudioContext()
      const analyser = audioContext.createAnalyser()
      const source = audioContext.createMediaStreamSource(mediaStream)
      source.connect(analyser)
      analyser.fftSize = 256
      
      const dataArray = new Uint8Array(analyser.frequencyBinCount)
      
      const checkAudioLevel = () => {
        if (!mediaStream) return
        analyser.getByteFrequencyData(dataArray)
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length
        isUserSpeaking.value = average > 30
        requestAnimationFrame(checkAudioLevel)
      }
      
      checkAudioLevel()
    }
  } catch (error) {
    console.warn('获取媒体设备失败:', error)
    hasMediaDevice.value = false
    cameraEnabled.value = false
    micEnabled.value = false
    ElMessage.warning('视频面试将以黑屏模式进行，你仍可通过文字回答问题')
  }
}

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

const toggleCamera = () => {
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

const toggleScreenShare = async () => {
  if (isScreenSharing.value) {
    if (screenStream) {
      screenStream.getTracks().forEach(track => track.stop())
      screenStream = null
    }
    isScreenSharing.value = false
    ElMessage.success('屏幕共享已停止')
  } else {
    try {
      screenStream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: false
      })
      
      screenStream.getVideoTracks()[0].onended = () => {
        isScreenSharing.value = false
        screenStream = null
      }
      
      isScreenSharing.value = true
      ElMessage.success('屏幕共享已开始')
    } catch (error) {
      console.warn('屏幕共享失败:', error)
      ElMessage.warning('无法启动屏幕共享')
    }
  }
}

const toggleChat = () => {
  if (!isSidebarOpen.value || activeTab.value !== 'chat') {
    activeTab.value = 'chat'
    if (!isSidebarOpen.value) isSidebarOpen.value = true
    unreadCount.value = 0
    nextTick(() => scrollToBottom())
  } else {
    isSidebarOpen.value = false
  }
}

const toggleMembers = () => {
  if (!isSidebarOpen.value || activeTab.value !== 'member') {
    activeTab.value = 'member'
    if (!isSidebarOpen.value) isSidebarOpen.value = true
  } else {
    isSidebarOpen.value = false
  }
}

const toggleSubtitle = () => {
  subtitleEnabled.value = !subtitleEnabled.value
  ElMessage.success(subtitleEnabled.value ? '字幕已开启' : '字幕已关闭')
}

const switchTab = (tab) => {
  activeTab.value = tab
  if (tab === 'chat') {
    unreadCount.value = 0
    nextTick(() => scrollToBottom())
  }
}

const copyMeetingLink = () => {
  const link = window.location.href
  navigator.clipboard.writeText(link).then(() => {
    ElMessage.success('会议链接已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

const connectWebSocket = () => {
  const wsUrl = `ws://localhost:8000/api/interview/ws/${interviewId}`

  wsClient = new WebSocketClient({
    url: wsUrl,
    heartbeatInterval: 30000,
    reconnectInterval: 1000,
    maxReconnectAttempts: 5,
    onOpen: () => {
      console.log('WebSocket 连接成功')
      connectionStatus.value = 'connected'
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
        currentQuestion.value = message
        
        if (!isSidebarOpen.value || activeTab.value !== 'chat') {
          unreadCount.value++
        }
        
        scrollToBottom()
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
      reconnectAttempts.value = attempts
    },
    onStatusChange: (status) => {
      connectionStatus.value = status
      connectionLatency.value = wsClient.getLatency()
    }
  })

  wsClient.connect()
}

const sendMessage = () => {
  if (!userAnswer.value.trim()) return

  const answer = userAnswer.value.trim()
  messages.value.push({
    role: 'candidate',
    content: answer
  })
  
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

const handleEnd = () => {
  isEnding.value = true
  showLeaveModal.value = false
  ElMessage.info('正在结束面试...')

  if (wsClient && wsClient.getStatus() === 'connected') {
    wsClient.send(JSON.stringify({ type: 'end' }))
  }

  if (wsClient) wsClient.close()
  handleInterviewEnd()
}

const handleInterviewEnd = () => {
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
  }
  if (screenStream) {
    screenStream.getTracks().forEach(track => track.stop())
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

const speakText = (text) => {
  if (!voiceOutputEnabled.value || !text || !speechSupported.synthesis) return

  speechService.stopSpeaking()
  stopSpeakingAnimation()

  try {
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'zh-CN'
    utterance.rate = 1
    utterance.pitch = 1
    utterance.volume = 1

    const voices = window.speechSynthesis.getVoices()
    const chineseVoice = voices.find(voice => voice.lang.includes('zh'))
    if (chineseVoice) utterance.voice = chineseVoice

    utterance.onstart = () => playSpeakingAnimation()
    utterance.onend = () => stopSpeakingAnimation()
    utterance.onerror = () => stopSpeakingAnimation()

    window.speechSynthesis.speak(utterance)
  } catch (error) {
    console.error('语音播放错误:', error)
    stopSpeakingAnimation()
  }
}

const handleReconnect = () => {
  if (wsClient) wsClient.reconnect()
}
</script>

<style scoped>
/* ===== 腾讯会议风格 ===== */
:root {
  --primary-color: #00A4FF; /* 腾讯会议标准蓝 */
  --danger-color: #F53F3F; /* 警示红 */
  --bg-dark: #18181F; /* 深色背景 */
  --bg-panel: #1E1E26;
  --bg-input: #26262E;
  --text-main: #F2F3F5;
  --text-sub: #A5A6AB;
  --border-color: #2E2E38;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.video-interview-room {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background: #1a1d24;
  color: #fff;
  min-height: 100vh;
  overflow: hidden;
  position: relative;
}

/* 动态背景 */
.bg-animation {
  position: fixed;
  inset: 0;
  z-index: -1;
  overflow: hidden;
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
  animation: orbFloat 20s ease-in-out infinite;
}

.bg-orb:nth-child(1) {
  width: 400px;
  height: 400px;
  background: #00d4a4;
  top: -200px;
  left: -100px;
}

.bg-orb:nth-child(2) {
  width: 300px;
  height: 300px;
  background: #4a9eff;
  bottom: -150px;
  right: -50px;
  animation-delay: -7s;
}

.bg-orb:nth-child(3) {
  width: 250px;
  height: 250px;
  background: #f56c6c;
  top: 50%;
  right: 20%;
  animation-delay: -14s;
}

@keyframes orbFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(30px, -30px) scale(1.05); }
  50% { transform: translate(-20px, 20px) scale(0.95); }
  75% { transform: translate(20px, 30px) scale(1.02); }
}

/* 顶部栏 */
.top-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: linear-gradient(180deg, #252a34 0%, #1e222a 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  z-index: 100;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.meeting-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.meeting-title {
  font-size: 16px;
  font-weight: 500;
  color: #fff;
}

.meeting-id {
  font-size: 13px;
  color: #8a919f;
  background: rgba(255,255,255,0.08);
  padding: 4px 10px;
  border-radius: 4px;
}

.meeting-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.recording-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #f56c6c;
  font-size: 13px;
}

.recording-dot {
  width: 8px;
  height: 8px;
  background: #f56c6c;
  border-radius: 50%;
  animation: recordingPulse 1.5s ease-in-out infinite;
}

@keyframes recordingPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

.duration {
  font-size: 15px;
  font-weight: 500;
  color: #e8eaed;
  font-variant-numeric: tabular-nums;
}

.top-actions {
  display: flex;
  gap: 12px;
}

.top-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(255,255,255,0.08);
  border-radius: 8px;
  color: #c4c8d1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.top-btn:hover {
  background: rgba(255,255,255,0.15);
  color: #fff;
  transform: translateY(-1px);
}

.top-btn svg {
  width: 20px;
  height: 20px;
}

/* 主内容区 */
.main-content {
  padding-top: 56px;
  padding-bottom: 110px;
  height: 100vh;
  display: flex;
  transition: margin-right 0.3s ease;
}

.video-interview-room.sidebar-open .main-content {
  margin-right: 320px;
}

/* 视频网格 */
.video-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 20px;
  align-content: center;
}

.video-container {
  position: relative;
  aspect-ratio: 16/9;
  background: linear-gradient(145deg, #2a2f3a 0%, #1e222b 100%);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.video-container.speaking {
  box-shadow: 0 0 0 3px #00d4a4, 0 0 20px rgba(0, 212, 164, 0.3);
}

.video-container.speaking::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 12px;
  border: 2px solid #00d4a4;
  animation: speakingPulse 2s ease-in-out infinite;
  pointer-events: none;
  z-index: 2;
}

@keyframes speakingPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.video-simulation {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(145deg, #2d323d 0%, #22262e 100%);
  position: relative;
}

.video-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 500;
  margin-bottom: 12px;
}

.avatar.interviewer {
  background: linear-gradient(135deg, #00d4a4 0%, #00a880 100%);
  color: #fff;
}

.avatar.candidate {
  background: linear-gradient(135deg, #4a9eff 0%, #2d7dd2 100%);
  color: #fff;
}

.participant-name {
  font-size: 15px;
  font-weight: 500;
  color: #e8eaed;
}

/* Lottie 动画 */
.ai-avatar-lottie {
  position: absolute;
  width: 1000px;
  height: 1000px;
  opacity: 0;
  transition: opacity 0.3s;
}

.ai-avatar-lottie.visible {
  opacity: 1;
}

/* 实际视频 */
.self-video-full {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1);
}

.video-label {
  position: absolute;
  bottom: 12px;
  left: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(8px);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  z-index: 3;
}

.mic-status {
  display: flex;
  align-items: center;
}

.mic-status.muted {
  color: #f56c6c;
}

.mic-status.unmuted {
  color: #00d4a4;
}

/* 音量波形 */
.volume-wave {
  display: flex;
  align-items: center;
  gap: 2px;
  height: 16px;
  margin-left: 4px;
}

.volume-bar {
  width: 3px;
  background: #00d4a4;
  border-radius: 2px;
  animation: volumeWave 0.5s ease-in-out infinite;
}

.volume-bar:nth-child(1) { animation-delay: 0s; height: 6px; }
.volume-bar:nth-child(2) { animation-delay: 0.1s; height: 10px; }
.volume-bar:nth-child(3) { animation-delay: 0.2s; height: 14px; }
.volume-bar:nth-child(4) { animation-delay: 0.3s; height: 8px; }

@keyframes volumeWave {
  0%, 100% { transform: scaleY(0.5); }
  50% { transform: scaleY(1); }
}

/* 视频波形动画 */
.video-wave {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 4px;
  padding-bottom: 20px;
}

.video-wave-bar {
  width: 4px;
  background: linear-gradient(to top, #00d4a4, rgba(0,212,164,0.2));
  border-radius: 2px;
  animation: videoWave 1.2s ease-in-out infinite;
}

@keyframes videoWave {
  0%, 100% { height: 10px; }
  50% { height: var(--wave-height, 30px); }
}

/* 问题 Toast */
.question-toast {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  max-width: 80%;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  padding: 16px 20px;
  animation: slideUp 0.3s ease-out;
  border: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 10;
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

.toast-header {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.toast-text {
  margin: 0;
  font-size: 15px;
  line-height: 1.6;
  color: #ffffff;
}

/* 底部控制栏 - 腾讯会议风格 */
.control-bar {
  height: 90px;
  min-height: 90px;
  background: #1A1A22;
  border-top: 1px solid var(--border-color, #2E2E38);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 24px;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.ctrl-btn-group {
  display: flex;
  gap: 24px;
  margin: 0 32px;
}

/* 基础控制按钮样式 */
.ctrl-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 70px;
  height: 64px;
  border: none;
  background: transparent;
  cursor: pointer;
  position: relative;
}

.ctrl-icon-box {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  position: relative;
  background: #3A3A44; /* 默认背景 */
}

.ctrl-btn:hover .ctrl-icon-box {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.ctrl-label {
  font-size: 12px;
  color: var(--text-sub, #A5A6AB);
  user-select: none;
}

/* 状态逻辑 */
/* 开启状态 (麦克风/摄像头/共享) - 蓝色 */
.ctrl-btn.active .ctrl-icon-box {
  background: rgba(0, 164, 255, 0.15);
  border: 1px solid #00A4FF;
}

.ctrl-btn.active svg {
  stroke: #00A4FF;
}

/* 关闭状态 (麦克风/摄像头) - 红色 */
.ctrl-btn.danger .ctrl-icon-box {
  background: #F53F3F;
}

.ctrl-btn.danger .ctrl-label {
  color: #F53F3F;
}

/* 其他功能按钮 (成员/聊天) - 白色/灰色 */
.ctrl-btn.default .ctrl-icon-box {
  background: #2E2E38;
}

/* 离开会议按钮 */
.ctrl-btn.leave-btn {
  position: absolute;
  right: 24px;
  width: auto;
}

.leave-btn .ctrl-icon-box {
  width: auto;
  padding: 0 16px;
  background: #F53F3F;
  border: none;
  font-size: 14px;
  color: #fff;
}

/* 徽章 */
.ctrl-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: #F53F3F;
  color: #fff;
  font-size: 11px;
  font-weight: 500;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* SVG 通用 */
.ctrl-icon-box svg {
  width: 24px;
  height: 24px;
  stroke: #FFF;
  stroke-width: 2;
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

/* 侧边栏 */
.sidebar {
  position: fixed;
  top: 56px;
  right: -320px;
  bottom: 90px;
  width: 320px;
  background: #232730;
  border-left: 1px solid rgba(255,255,255,0.06);
  transition: right 0.3s ease;
  z-index: 90;
  display: flex;
  flex-direction: column;
}

.sidebar.open {
  right: 0;
}

.sidebar-tabs {
  display: flex;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.sidebar-tab {
  flex: 1;
  padding: 16px;
  border: none;
  background: transparent;
  color: #8a919f;
  font-size: 14px;
  cursor: pointer;
  position: relative;
  transition: color 0.2s;
}

.sidebar-tab:hover {
  color: #c4c8d1;
}

.sidebar-tab.active {
  color: #00d4a4;
}

.sidebar-tab.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 20px;
  right: 20px;
  height: 2px;
  background: #00d4a4;
  border-radius: 1px;
}

.tab-badge {
  background: #f56c6c;
  color: #fff;
  font-size: 11px;
  padding: 1px 5px;
  border-radius: 8px;
  margin-left: 6px;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
}

/* 参与者列表 */
.participant-list {
  padding: 12px;
}

.participant-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  transition: background 0.2s;
}

.participant-item:hover {
  background: rgba(255,255,255,0.05);
}

.participant-item.speaking {
  background: rgba(0, 212, 164, 0.1);
}

.participant-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 500;
}

.participant-avatar.interviewer {
  background: linear-gradient(135deg, #00d4a4 0%, #00a880 100%);
  color: #fff;
}

.participant-avatar.candidate {
  background: linear-gradient(135deg, #4a9eff 0%, #2d7dd2 100%);
  color: #fff;
}

.participant-info {
  flex: 1;
}

.participant-name-text {
  font-size: 14px;
  color: #e8eaed;
  margin-bottom: 2px;
}

.participant-role {
  font-size: 12px;
  color: #8a919f;
}

.participant-actions {
  display: flex;
  gap: 8px;
}

.participant-action-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255,255,255,0.08);
  border-radius: 6px;
  color: #8a919f;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.participant-action-btn:hover {
  background: rgba(255,255,255,0.15);
  color: #fff;
}

.participant-action-btn.muted {
  color: #f56c6c;
}

/* 聊天面板 */
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.chat-message {
  margin-bottom: 16px;
}

.chat-sender {
  font-size: 13px;
  color: #00d4a4;
  margin-bottom: 4px;
}

.chat-text {
  font-size: 14px;
  color: #e8eaed;
  background: rgba(255,255,255,0.06);
  padding: 10px 14px;
  border-radius: 8px;
  display: inline-block;
  max-width: 90%;
  word-wrap: break-word;
}

.chat-text.typing {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
}

.chat-text.typing span {
  width: 8px;
  height: 8px;
  background: rgba(255,255,255,0.5);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.chat-text.typing span:nth-child(1) { animation-delay: -0.32s; }
.chat-text.typing span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.chat-input-area {
  padding: 12px 16px;
  border-top: 1px solid rgba(255,255,255,0.06);
}

.chat-input-wrapper {
  display: flex;
  gap: 8px;
}

.chat-input {
  flex: 1;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 10px 14px;
  color: #e8eaed;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input:focus {
  border-color: #00d4a4;
}

.chat-send-btn {
  padding: 10px 18px;
  background: #00d4a4;
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.chat-send-btn:hover {
  background: #00e8b4;
  transform: translateY(-1px);
}

.chat-send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 设置面板 */
.settings-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 199;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s;
}

.settings-overlay.open {
  opacity: 1;
  visibility: visible;
}

.settings-panel {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0.95);
  background: #2a2f3a;
  border-radius: 16px;
  padding: 24px;
  width: 400px;
  max-width: 90vw;
  z-index: 200;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.settings-panel.open {
  opacity: 1;
  visibility: visible;
  transform: translate(-50%, -50%) scale(1);
}

.settings-title {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.settings-close {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255,255,255,0.08);
  border-radius: 8px;
  color: #8a919f;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.settings-close:hover {
  background: rgba(255,255,255,0.15);
  color: #fff;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.setting-label {
  font-size: 14px;
  color: #e8eaed;
}

.setting-select {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  padding: 8px 12px;
  color: #e8eaed;
  font-size: 14px;
  outline: none;
  min-width: 180px;
}

/* 离开确认弹窗 */
.leave-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0.95);
  background: #2a2f3a;
  border-radius: 16px;
  padding: 28px;
  width: 360px;
  text-align: center;
  z-index: 200;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.leave-modal.open {
  opacity: 1;
  visibility: visible;
  transform: translate(-50%, -50%) scale(1);
}

.leave-modal-icon {
  width: 56px;
  height: 56px;
  background: rgba(245, 108, 108, 0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: #f56c6c;
}

.leave-modal-title {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 8px;
}

.leave-modal-desc {
  font-size: 14px;
  color: #8a919f;
  margin-bottom: 24px;
}

.leave-modal-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.leave-modal-btn {
  padding: 10px 28px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.leave-modal-btn.cancel {
  background: rgba(255,255,255,0.1);
  color: #e8eaed;
}

.leave-modal-btn.cancel:hover {
  background: rgba(255,255,255,0.15);
}

.leave-modal-btn.confirm {
  background: #f56c6c;
  color: #fff;
}

.leave-modal-btn.confirm:hover {
  background: #f78989;
}

.leave-modal-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.25);
}

/* 响应式 */
@media (max-width: 768px) {
  .video-grid {
    grid-template-columns: 1fr;
    gap: 12px;
    padding: 12px;
  }

  .sidebar {
    width: 100%;
    right: -100%;
  }

  .video-interview-room.sidebar-open .main-content {
    margin-right: 0;
  }

  .control-bar {
    padding: 0 16px;
  }

  .ctrl-btn-group {
    gap: 12px;
    margin: 0;
  }

  .ctrl-btn {
    width: 56px;
  }

  .ctrl-btn.leave-btn {
    right: 16px;
  }
}
</style>
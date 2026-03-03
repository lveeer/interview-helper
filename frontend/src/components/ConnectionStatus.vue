<template>
  <div class="connection-status">
    <div class="status-indicator">
      <div :class="['status-dot', statusClass]"></div>
      <span class="status-text">{{ statusText }}</span>
    </div>

    <div v-if="status !== 'disconnected'" class="status-meta">
      <div v-if="latency > 0" class="meta-item">
        <el-icon><Timer /></el-icon>
        <span>{{ latency }}ms</span>
      </div>
      <div v-if="reconnectAttempts > 0" class="meta-item">
        <el-icon><Refresh /></el-icon>
        <span>重连 {{ reconnectAttempts }} 次</span>
      </div>
    </div>

    <el-button
      v-if="status === 'disconnected' || status === 'reconnecting'"
      type="primary"
      size="small"
      :icon="Refresh"
      :loading="status === 'reconnecting'"
      @click="handleReconnect"
    >
      {{ status === 'reconnecting' ? '重连中...' : '重新连接' }}
    </el-button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Refresh, Timer } from '@element-plus/icons-vue'

const props = defineProps({
  status: {
    type: String,
    default: 'disconnected',
    validator: (value) => ['connected', 'connecting', 'disconnected', 'reconnecting'].includes(value)
  },
  latency: {
    type: Number,
    default: 0
  },
  reconnectAttempts: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['reconnect'])

const statusClass = computed(() => {
  return {
    connected: 'status-connected',
    connecting: 'status-connecting',
    disconnected: 'status-disconnected',
    reconnecting: 'status-reconnecting'
  }[props.status]
})

const statusText = computed(() => {
  return {
    connected: '已连接',
    connecting: '连接中',
    disconnected: '已断开',
    reconnecting: '重连中'
  }[props.status]
})

const handleReconnect = () => {
  emit('reconnect')
}
</script>

<style scoped>
.connection-status {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 16px;
  background: var(--bg-color-light);
  border-radius: 8px;
  border: 1px solid var(--border-color-light);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-connected {
  background-color: var(--success-color);
  box-shadow: 0 0 8px rgba(82, 196, 26, 0.4);
}

.status-connecting {
  background-color: var(--warning-color);
  animation: pulse 1s infinite;
}

.status-disconnected {
  background-color: var(--danger-color);
  animation: none;
}

.status-reconnecting {
  background-color: var(--warning-color);
  animation: pulse 0.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.status-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.status-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-secondary);
}

.meta-item .el-icon {
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .connection-status {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .status-meta {
    flex-wrap: wrap;
  }
}
</style>
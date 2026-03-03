<template>
  <el-tag :type="tagType" :size="size" class="difficulty-badge">
    <span class="difficulty-icon">{{ icon }}</span>
    <span class="difficulty-text">{{ difficultyText }}</span>
    <span v-if="trend" :class="['trend-indicator', trend]">
      {{ trendIcon }}
    </span>
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  difficulty: {
    type: String,
    default: 'medium',
    validator: (value) => ['easy', 'medium', 'hard'].includes(value)
  },
  trend: {
    type: String,
    default: null,
    validator: (value) => value === null || ['up', 'down', 'same'].includes(value)
  },
  size: {
    type: String,
    default: 'default',
    validator: (value) => ['large', 'default', 'small'].includes(value)
  }
})

const tagType = computed(() => {
  return {
    easy: 'success',
    medium: 'warning',
    hard: 'danger'
  }[props.difficulty]
})

const difficultyText = computed(() => {
  return {
    easy: '简单',
    medium: '中等',
    hard: '困难'
  }[props.difficulty]
})

const icon = computed(() => {
  return {
    easy: '🟢',
    medium: '🟡',
    hard: '🔴'
  }[props.difficulty]
})

const trendIcon = computed(() => {
  return {
    up: '↑',
    down: '↓',
    same: '→'
  }[props.trend]
})
</script>

<style scoped>
.difficulty-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}

.difficulty-icon {
  font-size: 14px;
}

.difficulty-text {
  font-size: 13px;
}

.trend-indicator {
  font-size: 12px;
  font-weight: 600;
  margin-left: 2px;
}

.trend-indicator.up {
  color: var(--danger-color);
}

.trend-indicator.down {
  color: var(--success-color);
}

.trend-indicator.same {
  color: var(--text-secondary);
}
</style>
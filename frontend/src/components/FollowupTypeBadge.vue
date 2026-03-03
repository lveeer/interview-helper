<template>
  <div class="followup-badge">
    <el-tag :type="tagType" :size="size" class="followup-tag">
      <span class="followup-icon">{{ icon }}</span>
      <span class="followup-text">{{ typeText }}</span>
    </el-tag>
    <div v-if="showCount" class="followup-count">
      <span class="count-text">{{ count }}/{{ maxCount }}</span>
      <el-progress
        :percentage="progress"
        :show-text="false"
        :stroke-width="4"
        :color="progressColor"
        class="count-progress"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'deep',
    validator: (value) => ['deep', 'detail', 'case', 'comparison', 'extension', 'clarification'].includes(value)
  },
  count: {
    type: Number,
    default: 0
  },
  maxCount: {
    type: Number,
    default: 3
  },
  size: {
    type: String,
    default: 'default',
    validator: (value) => ['large', 'default', 'small'].includes(value)
  },
  showCount: {
    type: Boolean,
    default: true
  }
})

const tagType = computed(() => {
  return {
    deep: 'primary',
    detail: 'info',
    case: 'warning',
    comparison: 'danger',
    extension: 'success',
    clarification: ''
  }[props.type]
})

const typeText = computed(() => {
  return {
    deep: '深度追问',
    detail: '细节追问',
    case: '案例追问',
    comparison: '对比追问',
    extension: '扩展追问',
    clarification: '澄清追问'
  }[props.type]
})

const icon = computed(() => {
  return {
    deep: '🔍',
    detail: '📝',
    case: '💡',
    comparison: '⚖️',
    extension: '🌐',
    clarification: '❓'
  }[props.type]
})

const progress = computed(() => {
  return Math.round((props.count / props.maxCount) * 100)
})

const progressColor = computed(() => {
  if (progress.value >= 100) {
    return '#f5222d'
  } else if (progress.value >= 66) {
    return '#faad14'
  } else {
    return '#52c41a'
  }
})
</script>

<style scoped>
.followup-badge {
  display: inline-flex;
  flex-direction: column;
  gap: 4px;
}

.followup-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}

.followup-icon {
  font-size: 14px;
}

.followup-text {
  font-size: 13px;
}

.followup-count {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  background: var(--bg-color-light);
  border-radius: 4px;
}

.count-text {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
  white-space: nowrap;
}

.count-progress {
  width: 60px;
  min-width: 60px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .followup-count {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .count-progress {
    width: 100%;
    min-width: 0;
  }
}
</style>
<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: var(--primary-color);">
              <el-icon :size="30"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ resumeCount }}</div>
              <div class="stat-label">简历数量</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: var(--success-color);">
              <el-icon :size="30"><ChatDotRound /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ interviewCount }}</div>
              <div class="stat-label">面试次数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: var(--warning-color);">
              <el-icon :size="30"><Reading /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ knowledgeCount }}</div>
              <div class="stat-label">知识文档</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: var(--danger-color);">
              <el-icon :size="30"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ avgScore }}</div>
              <div class="stat-label">平均分数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mb-4">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <div class="ios-action-btn mac-blue" @click="goToResume">
              <el-icon class="ios-btn-icon"><Upload /></el-icon>
              <span class="ios-btn-label">上传简历</span>
            </div>
            <div class="ios-action-btn mac-green" @click="goToResumeOptimize">
              <el-icon class="ios-btn-icon"><MagicStick /></el-icon>
              <span class="ios-btn-label">简历优化</span>
            </div>
            <div class="ios-action-btn mac-teal" @click="goToInterview">
              <el-icon class="ios-btn-icon"><ChatDotRound /></el-icon>
              <span class="ios-btn-label">开始面试</span>
            </div>
            <div class="ios-action-btn mac-orange" @click="goToJobMatch">
              <el-icon class="ios-btn-icon"><TrendCharts /></el-icon>
              <span class="ios-btn-label">岗位匹配</span>
            </div>
            <div class="ios-action-btn mac-purple" @click="goToKnowledge">
              <el-icon class="ios-btn-icon"><Reading /></el-icon>
              <span class="ios-btn-label">知识库</span>
            </div>
            <div class="ios-action-btn mac-gray" @click="goToLLMConfig">
              <el-icon class="ios-btn-icon"><Setting /></el-icon>
              <span class="ios-btn-label">LLM 配置</span>
            </div>
            <div class="ios-action-btn mac-pink" @click="goToRecallTest">
              <el-icon class="ios-btn-icon"><DataAnalysis /></el-icon>
              <span class="ios-btn-label">召回测试</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近面试</span>
            </div>
          </template>
          <div v-if="recentInterviews.length > 0" class="recent-interviews">
            <div
              v-for="interview in recentInterviews"
              :key="interview.id"
              class="interview-item"
              @click="goToInterviewDetail(interview.id)"
            >
              <div class="interview-info">
                <div class="interview-title">{{ interview.job_description || '未命名面试' }}</div>
                <div class="interview-meta">
                  <span class="interview-time">{{ formatDate(interview.created_at) }}</span>
                  <el-tag
                    :type="interview.status === 'completed' ? 'success' : 'warning'"
                    size="small"
                  >
                    {{ interview.status === 'completed' ? '已完成' : '进行中' }}
                  </el-tag>
                </div>
              </div>
              <div class="interview-score">
                <div class="score-value">{{ interview.total_score }}</div>
                <div class="score-label">分</div>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无面试记录" /></el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboardStatistics } from '@/api/statistics'

const router = useRouter()

const resumeCount = ref(0)
const interviewCount = ref(0)
const knowledgeCount = ref(0)
const avgScore = ref(0)
const recentInterviews = ref([])

const loadData = async () => {
  try {
    const res = await getDashboardStatistics()

    if (res.code === 200) {
      resumeCount.value = res.data.resume_count || 0
      interviewCount.value = res.data.interview_count || 0
      knowledgeCount.value = res.data.knowledge_count || 0
      avgScore.value = res.data.avg_score || 0
      recentInterviews.value = res.data.recent_interviews || []
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const goToResume = () => router.push('/resume')
const goToResumeOptimize = () => router.push('/resume-optimize')
const goToInterview = () => router.push('/interview')
const goToJobMatch = () => router.push('/job-match')
const goToKnowledge = () => router.push('/knowledge')
const goToLLMConfig = () => router.push('/llm-config')
const goToRecallTest = () => router.push('/recall-test')

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    return '今天'
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  }
}

const goToInterviewDetail = (id) => {
  router.push(`/interview-record/${id}`)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard {
  animation: fadeIn var(--transition-base);
  position: relative;
  z-index: 1;
  padding-top: var(--spacing-md);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 确保所有内容可见 */
.dashboard > * {
  position: relative;
  z-index: 2;
}

/* 统计卡片样式 */
:deep(.el-row) {
  margin-bottom: var(--spacing-xl);
}

:deep(.el-row:last-child) {
  margin-bottom: 0;
}

:deep(.el-col) {
  margin-bottom: 0;
}

.stat-card {
  cursor: pointer;
  transition: all var(--transition-base);
  border: 1px solid var(--border-color-light);
  border-radius: var(--radius-lg);
  overflow: hidden;
  position: relative;
  background: var(--card-bg);
  z-index: 3;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent 0%, rgba(255, 255, 255, 0.1) 100%);
  opacity: 0;
  transition: opacity var(--transition-base);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-xl);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 24px;
  gap: var(--spacing-lg, 24px);
  position: relative;
  z-index: 4;
  padding: 8px 0;
}

.stat-icon {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  border-radius: var(--radius-lg, 12px);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 36px;
  transition: all 0.2s;
  transition: all var(--transition-base, 0.2s);
  position: relative;
  z-index: 4;
}

.stat-icon::after {
  content: '';
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  border-radius: var(--radius-lg);
  background: inherit;
  opacity: 0.3;
  filter: blur(8px);
  z-index: -1;
}

.stat-card:hover .stat-icon {
  transform: scale(1.1) rotate(5deg);
}

.stat-info {
  flex: 1;
  position: relative;
  z-index: 4;
}

.stat-value {
  font-size: 46px;
  font-size: var(--font-size-3xl, 46px);
  font-weight: 700;
  font-weight: var(--font-weight-bold, 700);
  color: #303133;
  color: var(--text-primary, #303133);
  margin-bottom: 8px;
  margin-bottom: var(--spacing-xs, 8px);
  line-height: 1.2;
}

.stat-label {
  font-size: 20px;
  font-size: var(--font-size-xl, 20px);
  color: #909399;
  color: var(--text-secondary, #909399);
  font-weight: 500;
  font-weight: var(--font-weight-medium, 500);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 卡片头部样式 */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 18px;
  font-size: var(--font-size-lg, 18px);
  font-weight: 600;
  font-weight: var(--font-weight-semibold, 600);
  color: #303133;
  color: var(--text-primary, #303133);
  padding: 0;
}

:deep(.el-card__header) {
  padding: 16px;
  padding: var(--spacing-lg, 16px);
  border-bottom: none;
  background: linear-gradient(180deg, #fafafa 0%, transparent 100%);
  background: linear-gradient(180deg, var(--bg-color-light, #fafafa) 0%, transparent 100%);
}

:deep(.el-card__body) {
  padding: 16px;
  padding: var(--spacing-lg, 16px);
  min-height: 100px;
}

/* 快速操作区域 - 苹果大卡片式设计 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 16px 0;
}

.ios-action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  height: 112px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease-out;
  position: relative;
  outline: none;
  -webkit-tap-highlight-color: transparent;
}

.ios-action-btn:hover {
  transform: translateY(-2px);
}

.ios-action-btn:active {
  transform: scale(0.98);
}

.ios-btn-icon {
  font-size: 32px;
  transition: all 0.2s ease-out;
  position: relative;
  z-index: 2;
}

.ios-btn-icon .el-icon {
  font-size: 32px;
  transition: transform 0.2s ease-out;
}

.ios-action-btn:hover .ios-btn-icon .el-icon {
  transform: scale(1.05);
}

.ios-btn-label {
  font-size: 14px;
  font-weight: 500;
  color: #FFFFFF;
  color: var(--text-white, #FFFFFF);
  text-align: center;
  position: relative;
  z-index: 2;
  letter-spacing: -0.005em;
  padding: 0 8px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.15);
}

/* 苹果大卡片式 - Apple 历年经典配色系统 */
/* 上传简历 - iOS 15+ Apple Blue */
.mac-blue {
  background: linear-gradient(135deg, #007AFF 0%, #0051D5 100%);
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.25);
}

.mac-blue .ios-btn-icon {
  color: #FFFFFF;
}

.mac-blue:hover {
  background: linear-gradient(135deg, #0066CC 0%, #0041AA 100%);
  box-shadow: 0 6px 24px rgba(0, 122, 255, 0.35);
}

/* 简历优化 - macOS Big Sur Green */
.mac-green {
  background: linear-gradient(135deg, #34C759 0%, #248A3D 100%);
  box-shadow: 0 4px 16px rgba(52, 199, 89, 0.25);
}

.mac-green .ios-btn-icon {
  color: #FFFFFF;
}

.mac-green:hover {
  background: linear-gradient(135deg, #2DB54E 0%, #1E6E32 100%);
  box-shadow: 0 6px 24px rgba(52, 199, 89, 0.35);
}

/* 开始面试 - iOS 7+ Teal/Cyan */
.mac-teal {
  background: linear-gradient(135deg, #32ADE6 0%, #007AFF 100%);
  box-shadow: 0 4px 16px rgba(50, 173, 230, 0.25);
}

.mac-teal .ios-btn-icon {
  color: #FFFFFF;
}

.mac-teal:hover {
  background: linear-gradient(135deg, #2A96C9 0%, #0066CC 100%);
  box-shadow: 0 6px 24px rgba(50, 173, 230, 0.35);
}

/* 岗位匹配 - iOS 13+ Orange */
.mac-orange {
  background: linear-gradient(135deg, #FF9500 0%, #FF6B00 100%);
  box-shadow: 0 4px 16px rgba(255, 149, 0, 0.25);
}

.mac-orange .ios-btn-icon {
  color: #FFFFFF;
}

.mac-orange:hover {
  background: linear-gradient(135deg, #E68600 0%, #E65C00 100%);
  box-shadow: 0 6px 24px rgba(255, 149, 0, 0.35);
}

/* 知识库 - iOS 8+ Purple */
.mac-purple {
  background: linear-gradient(135deg, #AF52DE 0%, #7C3AED 100%);
  box-shadow: 0 4px 16px rgba(175, 82, 222, 0.25);
}

.mac-purple .ios-btn-icon {
  color: #FFFFFF;
}

.mac-purple:hover {
  background: linear-gradient(135deg, #9E47C7 0%, #6B33D4 100%);
  box-shadow: 0 6px 24px rgba(175, 82, 222, 0.35);
}

/* LLM 配置 - macOS Monterey Indigo */
.mac-gray {
  background: linear-gradient(135deg, #5856D6 0%, #3634A3 100%);
  box-shadow: 0 4px 16px rgba(88, 86, 214, 0.25);
}

.mac-gray .ios-btn-icon {
  color: #FFFFFF;
}

.mac-gray:hover {
  background: linear-gradient(135deg, #4D4BBE 0%, #2E2C8F 100%);
  box-shadow: 0 6px 24px rgba(88, 86, 214, 0.35);
}

/* 召回测试 - iOS 15+ Pink */
.mac-pink {
  background: linear-gradient(135deg, #FF2D55 0%, #FF375F 100%);
  box-shadow: 0 4px 16px rgba(255, 45, 85, 0.25);
}

.mac-pink .ios-btn-icon {
  color: #FFFFFF;
}

.mac-pink:hover {
  background: linear-gradient(135deg, #E6264D 0%, #E63156 100%);
  box-shadow: 0 6px 24px rgba(255, 45, 85, 0.35);
}

/* 最近面试区域 */
:deep(.el-empty) {
  padding: 48px 0;
  padding: var(--spacing-xxl, 48px) 0;
}

:deep(.el-empty__description) {
  color: #909399;
  color: var(--text-secondary, #909399);
  margin-top: 16px;
  margin-top: var(--spacing-md, 16px);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  :deep(.el-col) {
    margin-bottom: var(--spacing-md);
  }

  .stat-content {
    gap: var(--spacing-md);
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    font-size: 24px;
  }

  .stat-value {
    font-size: var(--font-size-2xl);
  }

  .stat-label {
    font-size: var(--font-size-xs);
  }

  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .ios-action-btn {
    height: 96px;
    gap: 16px;
    border-radius: 12px;
  }

  .ios-btn-icon {
    font-size: 28px;
  }

  .ios-btn-icon .el-icon {
    font-size: 28px;
  }

  .ios-btn-label {
    font-size: 13px;
  }

  :deep(.el-card__header),
  :deep(.el-card__body) {
    padding: var(--spacing-md);
  }
}

/* 添加数字动画效果 */
.stat-value {
  display: inline-block;
}

@keyframes countUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-value.animate {
  animation: countUp 0.6s ease-out;
}

/* 卡片进入动画 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

:deep(.el-col) {
  animation: slideIn 0.5s ease-out backwards;
}

:deep(.el-col:nth-child(1)) { animation-delay: 0.1s; }
:deep(.el-col:nth-child(2)) { animation-delay: 0.2s; }
:deep(.el-col:nth-child(3)) { animation-delay: 0.3s; }
:deep(.el-col:nth-child(4)) { animation-delay: 0.4s; }


/* 最近面试列表样式 */
.recent-interviews {
  display: flex;
  flex-direction: column;
  gap: 12px;
  gap: var(--spacing-sm, 12px);
}

.interview-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  padding: var(--spacing-md, 16px);
  border-radius: 8px;
  border-radius: var(--radius-md, 8px);
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  background: linear-gradient(135deg, var(--bg-color-light, #fafafa) 0%, var(--bg-color, #f5f5f5) 100%);
  border: 1px solid var(--border-color-light);
  cursor: pointer;
  transition: all 0.2s;
  transition: all var(--transition-base, 0.2s);
  position: relative;
  overflow: hidden;
}

.interview-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent 0%, rgba(64, 158, 255, 0.05) 100%);
  opacity: 0;
  transition: opacity var(--transition-base);
}

.interview-item:hover {
  transform: translateX(4px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary-color, #409EFF);
}

.interview-item:hover::before {
  opacity: 1;
}

.interview-info {
  flex: 1;
  min-width: 0;
}

.interview-title {
  font-size: 15px;
  font-size: var(--font-size-base, 15px);
  font-weight: 600;
  font-weight: var(--font-weight-semibold, 600);
  color: #303133;
  color: var(--text-primary, #303133);
  margin-bottom: 8px;
  margin-bottom: var(--spacing-xs, 8px);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.interview-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  gap: var(--spacing-xs, 8px);
}

.interview-time {
  font-size: 13px;
  font-size: var(--font-size-sm, 13px);
  color: #909399;
  color: var(--text-secondary, #909399);
}

.interview-score {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-left: 16px;
  margin-left: var(--spacing-sm, 16px);
  padding: 8px 12px;
  padding: var(--spacing-xs) var(--spacing-sm);
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  border-radius: 6px;
  border-radius: var(--radius-sm, 6px);
  color: #fff;
  min-width: 60px;
  justify-content: center;
}

.score-value {
  font-size: 24px;
  font-size: var(--font-size-xl, 24px);
  font-weight: 700;
  font-weight: var(--font-weight-bold, 700);
  line-height: 1;
}

.score-label {
  font-size: 12px;
  font-size: var(--font-size-xs, 12px);
  opacity: 0.9;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .interview-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    gap: var(--spacing-sm, 12px);
  }

  .interview-meta {
    flex-wrap: wrap;
  }

  .interview-score {
    margin-left: 0;
    width: 100%;
  }
}

.mb-4 {
  margin-bottom: 20px;
}

</style>
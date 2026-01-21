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
            <el-button type="primary" @click="goToResume">
              <el-icon><Upload /></el-icon>
              上传简历
            </el-button>
            <el-button type="success" @click="goToResumeOptimize">
              <el-icon><MagicStick /></el-icon>
              简历优化
            </el-button>
            <el-button type="success" @click="goToInterview">
              <el-icon><ChatDotRound /></el-icon>
              开始面试
            </el-button>
            <el-button type="warning" @click="goToJobMatch">
              <el-icon><TrendCharts /></el-icon>
              岗位匹配
            </el-button>
            <el-button type="info" @click="goToKnowledge">
              <el-icon><Reading /></el-icon>
              知识库
            </el-button>
            <el-button type="primary" plain @click="goToLLMConfig">
              <el-icon><Setting /></el-icon>
              LLM 配置
            </el-button>
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

/* 快速操作区域 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  gap: var(--spacing-lg, 20px);
  padding: 16px 0;
}

.quick-actions .el-button {
  height: 100px;
  padding: 20px;
  padding: var(--spacing-lg, 20px);
  border-radius: 8px;
  border-radius: var(--radius-md, 8px);
  font-size: 14px;
  font-size: var(--font-size-base, 14px);
  font-weight: 500;
  font-weight: var(--font-weight-medium, 500);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  gap: var(--spacing-sm, 8px);
  transition: all 0.2s;
  transition: all var(--transition-base, 0.2s);
  border: 1px solid transparent;
  position: relative;
  overflow: hidden;
  min-width: 120px;
}

.quick-actions .el-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent 0%, rgba(255, 255, 255, 0.2) 100%);
  opacity: 0;
  transition: opacity var(--transition-base);
}

.quick-actions .el-button:hover::before {
  opacity: 1;
}

.quick-actions .el-button .el-icon {
  font-size: 24px;
  transition: transform var(--transition-base);
}

.quick-actions .el-button:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.quick-actions .el-button:hover .el-icon {
  transform: scale(1.2);
}

/* 按钮特定样式 */
.quick-actions .el-button--primary {
  background: linear-gradient(135deg, #409EFF 0%, #337ecc 100%);
  background: linear-gradient(135deg, var(--primary-color, #409EFF) 0%, var(--primary-dark, #337ecc) 100%);
  border-color: #409EFF;
  border-color: var(--primary-color, #409EFF);
}

.quick-actions .el-button--success {
  background: linear-gradient(135deg, #67C23A 0%, #5daf34 100%);
  background: linear-gradient(135deg, var(--success-color, #67C23A) 0%, #5daf34 100%);
  border-color: #67C23A;
  border-color: var(--success-color, #67C23A);
}

.quick-actions .el-button--warning {
  background: linear-gradient(135deg, #E6A23C 0%, #cf9236 100%);
  background: linear-gradient(135deg, var(--warning-color, #E6A23C) 0%, #cf9236 100%);
  border-color: #E6A23C;
  border-color: var(--warning-color, #E6A23C);
}

.quick-actions .el-button--info {
  background: linear-gradient(135deg, #909399 0%, #7a7e85 100%);
  background: linear-gradient(135deg, var(--info-color, #909399) 0%, #7a7e85 100%);
  border-color: #909399;
  border-color: var(--info-color, #909399);
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
    grid-template-columns: 1fr;
  }

  .quick-actions .el-button {
    flex-direction: row;
    justify-content: flex-start;
    padding: var(--spacing-sm) var(--spacing-md);
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
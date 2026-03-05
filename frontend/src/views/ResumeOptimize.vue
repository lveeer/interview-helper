<template>
  <div class="optimize-page">
    <!-- 选择简历区域 -->
    <div class="macos-window select-window">
      <div class="window-titlebar">
        <div class="window-title">
          <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <span>简历分析</span>
        </div>
      </div>

      <div class="window-content">
        <div class="select-section">
          <label class="select-label">选择简历</label>
          <div class="select-wrapper">
            <select v-model="selectedResumeId" @change="handleResumeChange" class="macos-select">
              <option value="" disabled>请选择要优化的简历</option>
              <option v-for="resume in resumeList" :key="resume.id" :value="resume.id">
                {{ resume.file_name }}
              </option>
            </select>
            <svg class="select-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </div>
        </div>

        <div class="jd-section">
          <div class="jd-header">
            <label class="jd-label">职位描述（JD）</label>
            <button v-if="jobDescription" class="clear-btn" @click="clearJD">清除</button>
          </div>
          <textarea
            v-model="jobDescription"
            class="jd-textarea"
            rows="8"
            placeholder="请输入职位描述（JD），系统将根据 JD 提供针对性的简历分析和优化建议..."
          ></textarea>
          <div class="jd-tip">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            <span>输入 JD 后，系统会根据职位要求提供更精准的分析和建议</span>
          </div>
        </div>

        <div class="analyze-actions">
          <button
            class="analyze-btn"
            :class="{ disabled: !selectedResumeId }"
            :disabled="!selectedResumeId || analyzing"
            @click="handleAnalyze"
          >
            <svg v-if="!analyzing" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
            <svg v-else class="spinning" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
            </svg>
            <span>{{ analyzing ? '分析中...' : '开始分析' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- AI 分析加载对话框 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="analyzing" class="modal-overlay dark">
          <div class="analyze-modal">
            <div class="analyze-animation">
              <div class="ai-ring ring-1"></div>
              <div class="ai-ring ring-2"></div>
              <div class="ai-ring ring-3"></div>
              <div class="ai-core">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2a10 10 0 1 0 10 10"></path>
                  <path d="M12 2v10l7-7"></path>
                </svg>
              </div>
            </div>

            <div class="analyze-info">
              <h3>AI 正在分析您的简历</h3>
              <p class="step-text">{{ currentAnalyzeStep }}</p>
            </div>

            <div class="analyze-progress">
              <div class="progress-track">
                <div class="progress-fill" :style="{ width: analyzeProgress + '%' }"></div>
              </div>
              <span class="progress-text">{{ analyzeProgress.toFixed(0) }}%</span>
            </div>

            <div class="analyze-steps">
              <div
                v-for="(step, index) in analyzeSteps"
                :key="index"
                class="step-item"
                :class="{ active: index === currentStepIndex, completed: index < currentStepIndex }"
              >
                <div class="step-indicator">
                  <svg v-if="index < currentStepIndex" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  <div v-else class="step-dot"></div>
                </div>
                <span>{{ step }}</span>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 分析结果 -->
    <div v-if="selectedResumeId && analysisResult" class="macos-window result-window">
      <div class="window-titlebar">
        <div class="window-title">简历分析报告</div>
        <div class="window-actions">
          <button class="action-btn secondary" @click="handleAnalyze" :disabled="analyzing">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="23 4 23 10 17 10"></polyline>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
            </svg>
            <span>重新分析</span>
          </button>
        </div>
      </div>

      <div class="window-content">
        <!-- 评分卡片 -->
        <div class="scores-section">
          <div class="main-score-card">
            <div class="score-circle">
              <svg viewBox="0 0 100 100">
                <circle class="score-bg" cx="50" cy="50" r="42" fill="none" stroke-width="8"/>
                <circle
                  class="score-fill"
                  cx="50" cy="50" r="42"
                  fill="none"
                  stroke-width="8"
                  :stroke-dasharray="264"
                  :stroke-dashoffset="264 - (264 * analysisResult.overall_score / 100)"
                  :style="{ stroke: getScoreColor(analysisResult.overall_score) }"
                />
              </svg>
              <div class="score-value">
                <span class="number">{{ analysisResult.overall_score }}</span>
                <span class="unit">分</span>
              </div>
            </div>
            <div class="score-label">综合评分</div>
          </div>

          <div class="sub-scores">
            <div class="sub-score-card">
              <div class="sub-header">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <span>内容完整性</span>
              </div>
              <div class="sub-progress">
                <div class="sub-track">
                  <div
                    class="sub-fill"
                    :style="{ width: analysisResult.content_score + '%', background: getScoreColor(analysisResult.content_score) }"
                  ></div>
                </div>
                <span class="sub-value">{{ analysisResult.content_score }}%</span>
              </div>
            </div>

            <div class="sub-score-card">
              <div class="sub-header">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                <span>专业匹配度</span>
              </div>
              <div class="sub-progress">
                <div class="sub-track">
                  <div
                    class="sub-fill"
                    :style="{ width: analysisResult.match_score + '%', background: getScoreColor(analysisResult.match_score) }"
                  ></div>
                </div>
                <span class="sub-value">{{ analysisResult.match_score }}%</span>
              </div>
            </div>

            <div class="sub-score-card">
              <div class="sub-header">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 20h9"></path>
                  <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
                </svg>
                <span>表达清晰度</span>
              </div>
              <div class="sub-progress">
                <div class="sub-track">
                  <div
                    class="sub-fill"
                    :style="{ width: analysisResult.clarity_score + '%', background: getScoreColor(analysisResult.clarity_score) }"
                  ></div>
                </div>
                <span class="sub-value">{{ analysisResult.clarity_score }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 优势与不足 -->
        <div class="analysis-cards">
          <div class="analysis-card strengths">
            <div class="card-header">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
              <h4>简历优势</h4>
            </div>
            <ul class="card-list">
              <li v-for="(strength, index) in analysisResult.strengths" :key="index">{{ strength }}</li>
            </ul>
          </div>

          <div class="analysis-card weaknesses">
            <div class="card-header">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              <h4>需要改进</h4>
            </div>
            <ul class="card-list">
              <li v-for="(weakness, index) in analysisResult.weaknesses" :key="index">{{ weakness }}</li>
            </ul>
          </div>
        </div>

        <!-- 详细分析折叠 -->
        <div class="detail-section">
          <div class="collapse-item" v-for="collapse in collapseItems" :key="collapse.name">
            <div class="collapse-header" @click="toggleCollapse(collapse.name)">
              <div class="collapse-title">
                <div class="collapse-icon" :class="collapse.iconClass">
                  <component :is="collapse.icon" />
                </div>
                <span>{{ collapse.title }}</span>
              </div>
              <svg class="collapse-arrow" :class="{ expanded: activeCollapses.includes(collapse.name) }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
            <Transition name="collapse">
              <div v-if="activeCollapses.includes(collapse.name)" class="collapse-content">
                <div v-if="collapse.data" class="analysis-detail">
                  <div class="status-badge" :class="collapse.data.status">
                    {{ collapse.data.status === 'good' ? '良好' : '需改进' }}
                  </div>
                  <div class="detail-info">
                    <p v-if="collapse.data.included" class="info-row">
                      <span class="label">已包含：</span>
                      <span class="value">{{ collapse.data.included.join(', ') || '无' }}</span>
                    </p>
                    <p v-if="collapse.data.missing" class="info-row">
                      <span class="label">缺失：</span>
                      <span class="value">{{ collapse.data.missing.join(', ') || '无' }}</span>
                    </p>
                    <p v-if="collapse.data.suggestions" class="info-row">
                      <span class="label">建议：</span>
                      <span class="value">{{ collapse.data.suggestions }}</span>
                    </p>
                    <p v-if="collapse.data.issues" class="info-row">
                      <span class="label">问题：</span>
                      <span class="value">{{ collapse.data.issues }}</span>
                    </p>
                    <p v-if="collapse.data.hard_skills" class="info-row">
                      <span class="label">硬技能：</span>
                      <span class="value">{{ collapse.data.hard_skills.join(', ') || '无' }}</span>
                    </p>
                    <p v-if="collapse.data.soft_skills" class="info-row">
                      <span class="label">软技能：</span>
                      <span class="value">{{ collapse.data.soft_skills.join(', ') || '无' }}</span>
                    </p>
                  </div>
                </div>
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </div>

    <!-- 优化建议 -->
    <div v-if="selectedResumeId && suggestions.length > 0" class="macos-window suggestions-window">
      <div class="window-titlebar">
        <div class="window-title">优化建议 ({{ suggestions.length }})</div>
        <div class="window-actions">
          <button class="action-btn ghost" @click="selectAllSuggestions">全选</button>
          <button class="action-btn ghost" @click="deselectAllSuggestions">取消全选</button>
          <button class="action-btn primary" @click="handleApplyOptimizations" :disabled="applying">
            <svg v-if="applying" class="spinning" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
            </svg>
            <span>应用选中建议</span>
          </button>
        </div>
      </div>

      <div class="window-content">
        <div class="suggestions-list">
          <div
            v-for="(suggestion, index) in suggestions"
            :key="index"
            class="suggestion-card"
            :class="{ selected: suggestion.selected }"
            @click="suggestion.selected = !suggestion.selected"
          >
            <div class="suggestion-check">
              <div class="checkbox" :class="{ checked: suggestion.selected }">
                <svg v-if="suggestion.selected" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </div>
            </div>

            <div class="suggestion-body">
              <div class="suggestion-header">
                <span class="priority-tag" :class="suggestion.priority">
                  {{ suggestion.priority === 'high' ? '重要' : suggestion.priority === 'medium' ? '中等' : '建议' }}
                </span>
                <span class="suggestion-title">{{ suggestion.title }}</span>
              </div>

              <p class="suggestion-desc">{{ suggestion.description }}</p>

              <div v-if="suggestion.before && suggestion.after" class="diff-section">
                <div class="diff-item before">
                  <span class="diff-label">原文</span>
                  <p>{{ suggestion.before }}</p>
                </div>
                <div class="diff-item after">
                  <span class="diff-label">建议</span>
                  <p>{{ suggestion.after }}</p>
                </div>
              </div>

              <div v-if="suggestion.reason" class="suggestion-reason">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="16" x2="12" y2="12"></line>
                  <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
                <span>原因：{{ suggestion.reason }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 优化历史 -->
    <div v-if="selectedResumeId && optimizationHistory.length > 0" class="macos-window history-window">
      <div class="window-titlebar">
        <div class="window-title">优化历史</div>
        <div class="window-actions">
          <button class="action-btn ghost" @click="loadOptimizationHistory">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="23 4 23 10 17 10"></polyline>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
            </svg>
            <span>刷新</span>
          </button>
        </div>
      </div>

      <div class="window-content">
        <div class="history-timeline">
          <div v-for="(history, index) in optimizationHistory" :key="index" class="history-item">
            <div class="history-dot"></div>
            <div class="history-card">
              <div class="history-header">
                <span class="history-title">{{ history.title }}</span>
                <span class="history-time">{{ formatDate(history.created_at) }}</span>
              </div>
              <p class="history-desc">{{ history.description }}</p>
              <div class="history-actions">
                <button class="history-btn" @click="handleCompare(history)">查看对比</button>
                <button class="history-btn primary" @click="handleRestore(history)">恢复此版本</button>
              </div>
            </div>
          </div>
        </div>

        <div class="export-section">
          <button class="export-btn" @click="handleExport('pdf')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            导出为 PDF
          </button>
          <button class="export-btn" @click="handleExport('docx')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            导出为 Word
          </button>
        </div>
      </div>
    </div>

    <!-- 对比对话框 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showCompareDialog" class="modal-overlay" @click.self="showCompareDialog = false">
          <div class="modal-container large">
            <div class="modal-titlebar">
              <span class="modal-title">版本对比</span>
            </div>
            <div class="modal-content">
              <div class="compare-grid">
                <div class="compare-pane">
                  <div class="pane-header">优化前</div>
                  <div class="pane-content">{{ compareData.before }}</div>
                </div>
                <div class="compare-pane">
                  <div class="pane-header">优化后</div>
                  <div class="pane-content">{{ compareData.after }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getResumeList,
  analyzeResume,
  getOptimizationSuggestions,
  applyOptimization,
  getOptimizationHistory,
  exportOptimizedResume,
  compareResumeVersions,
  restoreResumeVersion
} from '@/api/resume'

const selectedResumeId = ref(null)
const resumeList = ref([])
const analysisResult = ref(null)
const suggestions = ref([])
const optimizationHistory = ref([])
const analyzing = ref(false)
const applying = ref(false)
const showCompareDialog = ref(false)
const compareData = ref({ before: '', after: '' })
const jobDescription = ref('')
const activeCollapses = ref(['personal', 'education', 'experience', 'skills'])

// AI 分析动画相关
const analyzeProgress = ref(0)
const currentStepIndex = ref(0)
const currentAnalyzeStep = ref('')
const analyzeSteps = [
  '解析简历结构',
  '提取关键信息',
  '分析技能匹配度',
  '评估内容质量',
  '生成优化建议'
]
let analyzeTimer = null
let progressTimer = null

// 折叠面板配置
const collapseItems = computed(() => [
  {
    name: 'personal',
    title: '个人信息分析',
    icon: 'personal',
    iconClass: 'personal',
    data: analysisResult.value?.personal_analysis
  },
  {
    name: 'education',
    title: '教育背景分析',
    icon: 'education',
    iconClass: 'education',
    data: analysisResult.value?.education_analysis
  },
  {
    name: 'experience',
    title: '工作经历分析',
    icon: 'work',
    iconClass: 'work',
    data: analysisResult.value?.experience_analysis
  },
  {
    name: 'skills',
    title: '技能分析',
    icon: 'skills',
    iconClass: 'skills',
    data: analysisResult.value?.skills_analysis
  }
])

const toggleCollapse = (name) => {
  const index = activeCollapses.value.indexOf(name)
  if (index > -1) {
    activeCollapses.value.splice(index, 1)
  } else {
    activeCollapses.value.push(name)
  }
}

const loadResumeList = async () => {
  try {
    const res = await getResumeList()
    if (res.code === 200) {
      resumeList.value = res.data || []
    }
  } catch (error) {
    console.error('加载简历列表失败:', error)
    ElMessage.error('加载简历列表失败')
  }
}

const handleResumeChange = async (resumeId) => {
  if (resumeId) {
    analysisResult.value = null
    suggestions.value = []
    await loadOptimizationHistory()
  }
}

const handleAnalyze = async () => {
  if (!selectedResumeId.value) {
    ElMessage.warning('请先选择简历')
    return
  }

  analyzing.value = true
  analyzeProgress.value = 0
  currentStepIndex.value = 0
  currentAnalyzeStep.value = analyzeSteps[0]

  startAnalyzeAnimation()

  try {
    const forceRefresh = !!jobDescription.value
    const res = await analyzeResume(selectedResumeId.value, jobDescription.value, forceRefresh)
    if (res.code === 200) {
      analysisResult.value = res.data
      ElMessage.success(jobDescription.value ? '分析完成（已应用 JD 匹配）' : '分析完成')
    } else {
      ElMessage.error(res.message || '分析失败')
    }
  } catch (error) {
    console.error('分析失败:', error)
    analysisResult.value = getMockAnalysisResult()
    ElMessage.success('分析完成（演示数据）')
  } finally {
    stopAnalyzeAnimation()
    analyzing.value = false
  }
}

const startAnalyzeAnimation = () => {
  progressTimer = setInterval(() => {
    if (analyzeProgress.value < 95) {
      analyzeProgress.value += Math.random() * 3
      analyzeProgress.value = Math.round(analyzeProgress.value * 10) / 10
    }
  }, 300)

  analyzeTimer = setInterval(() => {
    if (currentStepIndex.value < analyzeSteps.length - 1) {
      currentStepIndex.value++
      currentAnalyzeStep.value = analyzeSteps[currentStepIndex.value]
    }
  }, 800)
}

const stopAnalyzeAnimation = () => {
  if (analyzeTimer) clearInterval(analyzeTimer)
  if (progressTimer) clearInterval(progressTimer)

  analyzeProgress.value = 100
  currentStepIndex.value = analyzeSteps.length - 1
  currentAnalyzeStep.value = '分析完成！'

  setTimeout(() => {
    analyzeProgress.value = 0
    currentStepIndex.value = 0
  }, 500)
}

const loadSuggestions = async () => {
  if (!selectedResumeId.value) return

  try {
    const forceRefresh = !!jobDescription.value
    const res = await getOptimizationSuggestions(selectedResumeId.value, jobDescription.value, forceRefresh)
    if (res.code === 200) {
      suggestions.value = (res.data || []).map(s => ({ ...s, selected: false }))
    }
  } catch (error) {
    console.error('加载优化建议失败:', error)
    suggestions.value = getMockSuggestions()
  }
}

const loadOptimizationHistory = async () => {
  if (!selectedResumeId.value) return

  try {
    const res = await getOptimizationHistory(selectedResumeId.value)
    if (res.code === 200) {
      optimizationHistory.value = res.data || []
    }
  } catch (error) {
    console.error('加载优化历史失败:', error)
    optimizationHistory.value = []
  }
}

const selectAllSuggestions = () => {
  suggestions.value.forEach(s => s.selected = true)
}

const deselectAllSuggestions = () => {
  suggestions.value.forEach(s => s.selected = false)
}

const handleApplyOptimizations = async () => {
  const selected = suggestions.value.filter(s => s.selected)
  if (selected.length === 0) {
    ElMessage.warning('请至少选择一条优化建议')
    return
  }

  applying.value = true
  try {
    const res = await applyOptimization(selectedResumeId.value, selected)
    if (res.code === 200) {
      ElMessage.success('优化应用成功')
      await loadOptimizationHistory()
      await handleAnalyze()
    } else {
      ElMessage.error(res.message || '应用优化失败')
    }
  } catch (error) {
    console.error('应用优化失败:', error)
    ElMessage.error('应用优化失败')
  } finally {
    applying.value = false
  }
}

const handleCompare = async (history) => {
  try {
    const res = await compareResumeVersions(
      selectedResumeId.value,
      history.version_before,
      history.version_after
    )
    if (res.code === 200) {
      compareData.value = res.data
      showCompareDialog.value = true
    }
  } catch (error) {
    console.error('对比失败:', error)
    ElMessage.error('对比失败')
  }
}

const handleRestore = async (history) => {
  try {
    await ElMessageBox.confirm(
      `确定要恢复到 ${formatDate(history.created_at)} 的版本吗？`,
      '确认恢复',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const res = await restoreResumeVersion(selectedResumeId.value, history.version)
    if (res.code === 200) {
      ElMessage.success('恢复成功')
      await loadOptimizationHistory()
      await handleAnalyze()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('恢复失败:', error)
      ElMessage.error('恢复失败')
    }
  }
}

const handleExport = async (format) => {
  if (!selectedResumeId.value) {
    ElMessage.warning('请先选择简历')
    return
  }

  try {
    const res = await exportOptimizedResume(selectedResumeId.value, format)
    const blob = new Blob([res], {
      type: format === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `optimized_resume.${format}`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

const getScoreColor = (score) => {
  if (score >= 80) return '#34c759'
  if (score >= 60) return '#ff9500'
  return '#ff3b30'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const clearJD = () => {
  jobDescription.value = ''
  ElMessage.info('已清除职位描述')
}

// Mock 数据
const getMockAnalysisResult = () => ({
  overall_score: 72,
  content_score: 75,
  match_score: 68,
  clarity_score: 74,
  strengths: [
    '工作经历描述详细，有具体的项目经验',
    '技能列表清晰，涵盖多个技术栈',
    '教育背景信息完整'
  ],
  weaknesses: [
    '缺少量化成果和数据支撑',
    '自我评价部分过于简单',
    '部分项目描述缺少技术细节'
  ],
  personal_analysis: {
    status: 'good',
    message: '个人信息完整',
    included: ['姓名', '联系方式', '邮箱'],
    missing: []
  },
  education_analysis: {
    status: 'good',
    message: '教育背景清晰',
    suggestions: '建议添加在校期间的重要课程或获奖经历'
  },
  experience_analysis: {
    status: 'warning',
    message: '工作经历描述需要优化',
    issues: '部分工作经历缺乏量化成果，项目描述不够具体',
    suggestions: '建议使用STAR法则描述项目经历，添加具体的数据和成果'
  },
  skills_analysis: {
    status: 'good',
    message: '技能描述清晰',
    hard_skills: ['JavaScript', 'Vue.js', 'Python', 'MySQL'],
    soft_skills: ['团队协作', '沟通能力', '问题解决'],
    suggestions: '建议添加技能熟练度等级'
  }
})

const getMockSuggestions = () => [
  {
    id: 1,
    priority: 'high',
    title: '添加量化成果',
    description: '在工作经历中添加具体的数字和成果，如"提升性能50%"、"管理10人团队"等',
    before: '负责项目开发，提升了系统性能',
    after: '负责核心模块开发，通过优化数据库查询和缓存策略，将系统响应时间从500ms降低到250ms，性能提升50%',
    reason: '量化成果能让HR更直观地了解你的能力和贡献',
    selected: false
  },
  {
    id: 2,
    priority: 'high',
    title: '优化项目描述',
    description: '使用STAR法则（情境-任务-行动-结果）重新组织项目经历',
    before: '参与了电商平台的开发',
    after: '在电商平台项目中（情境），负责用户模块开发（任务），使用Vue.js和Node.js构建了完整的用户注册登录功能（行动），支持日均10万+用户访问（结果）',
    reason: 'STAR法则能让项目经历更有条理，突出你的贡献和成果',
    selected: false
  },
  {
    id: 3,
    priority: 'medium',
    title: '丰富自我评价',
    description: '在自我评价中添加更多个人特质和职业目标',
    before: '吃苦耐劳，积极向上',
    after: '拥有5年前端开发经验，擅长Vue.js生态，对性能优化有深入研究。具备良好的团队协作能力，曾带领5人小组完成多个项目。目标是成为一名全栈开发工程师，持续学习新技术',
    reason: '详细的自我评价能展现你的职业规划和个人特色',
    selected: false
  }
]

onMounted(() => {
  loadResumeList()
})
</script>

<style scoped>
/* 页面容器 */
.optimize-page {
  padding: 24px;
  min-height: 100%;
  background: linear-gradient(180deg, #f5f5f7 0%, #ffffff 100%);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* macOS 窗口基础样式 */
.macos-window {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 12px;
  box-shadow: 
    0 0 0 1px rgba(0, 0, 0, 0.05),
    0 2px 8px rgba(0, 0, 0, 0.04),
    0 20px 40px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.window-titlebar {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(180deg, #f6f6f6 0%, #e8e8e8 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  user-select: none;
}

.window-controls {
  display: flex;
  gap: 8px;
  margin-right: 16px;
}

.control {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.15s ease;
}

.control.close {
  background: linear-gradient(180deg, #ff6058 0%, #e04038 100%);
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.12);
}

.control.minimize {
  background: linear-gradient(180deg, #ffbd2e 0%, #e5a020 100%);
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.12);
}

.control.maximize {
  background: linear-gradient(180deg, #28c840 0%, #20a830 100%);
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.12);
}

.window-title {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
}

.title-icon {
  width: 16px;
  height: 16px;
  color: #86868b;
}

.window-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-btn svg {
  width: 14px;
  height: 14px;
}

.action-btn.primary {
  background: linear-gradient(180deg, #007AFF 0%, #0066d6 100%);
  color: white;
}

.action-btn.primary:hover:not(:disabled) {
  background: linear-gradient(180deg, #0084ff 0%, #0070e6 100%);
}

.action-btn.secondary {
  background: rgba(0, 0, 0, 0.05);
  color: #1d1d1f;
}

.action-btn.secondary:hover {
  background: rgba(0, 0, 0, 0.08);
}

.action-btn.ghost {
  background: transparent;
  color: #86868b;
}

.action-btn.ghost:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #1d1d1f;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.window-content {
  padding: 20px;
}

/* 选择简历区域 */
.select-section {
  margin-bottom: 20px;
}

.select-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #86868b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.select-wrapper {
  position: relative;
}

.macos-select {
  width: 100%;
  padding: 10px 40px 10px 14px;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 14px;
  color: #1d1d1f;
  cursor: pointer;
  appearance: none;
  transition: all 0.15s ease;
}

.macos-select:hover {
  border-color: rgba(0, 0, 0, 0.2);
}

.macos-select:focus {
  outline: none;
  border-color: #007aff;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.select-arrow {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #86868b;
  pointer-events: none;
}

/* JD 区域 */
.jd-section {
  margin-bottom: 20px;
}

.jd-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.jd-label {
  font-size: 12px;
  font-weight: 600;
  color: #86868b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.clear-btn {
  padding: 4px 10px;
  background: transparent;
  border: none;
  color: #007aff;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.15s ease;
}

.clear-btn:hover {
  background: rgba(0, 122, 255, 0.1);
}

.jd-textarea {
  width: 100%;
  padding: 14px;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  color: #1d1d1f;
  resize: vertical;
  transition: all 0.15s ease;
  font-family: inherit;
}

.jd-textarea::placeholder {
  color: #86868b;
}

.jd-textarea:hover {
  border-color: rgba(0, 0, 0, 0.2);
}

.jd-textarea:focus {
  outline: none;
  border-color: #007aff;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.jd-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  padding: 10px 12px;
  background: rgba(0, 122, 255, 0.05);
  border-radius: 6px;
  font-size: 12px;
  color: #007aff;
}

.jd-tip svg {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

/* 分析按钮 */
.analyze-actions {
  text-align: center;
  padding-top: 10px;
}

.analyze-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 32px;
  background: linear-gradient(180deg, #007AFF 0%, #0066d6 100%);
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.3);
}

.analyze-btn:hover:not(.disabled) {
  background: linear-gradient(180deg, #0084ff 0%, #0070e6 100%);
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.4);
  transform: translateY(-1px);
}

.analyze-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.analyze-btn svg {
  width: 18px;
  height: 18px;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 分析模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-overlay.dark {
  background: rgba(0, 0, 0, 0.6);
}

.analyze-modal {
  width: 420px;
  padding: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  text-align: center;
  color: white;
}

.ai-ring {
  position: absolute;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  animation: rotate 3s linear infinite;
}

.ring-1 {
  width: 120px;
  height: 120px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-duration: 3s;
}

.ring-2 {
  width: 90px;
  height: 90px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-duration: 2s;
  animation-direction: reverse;
}

.ring-3 {
  width: 60px;
  height: 60px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-duration: 1.5s;
}

@keyframes rotate {
  0% { transform: translate(-50%, -50%) rotate(0deg); }
  100% { transform: translate(-50%, -50%) rotate(360deg); }
}

.ai-core {
  position: relative;
  width: 50px;
  height: 50px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse 2s ease-in-out infinite;
}

.ai-core svg {
  width: 24px;
  height: 24px;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.analyze-animation {
  position: relative;
  width: 140px;
  height: 140px;
  margin: 0 auto 30px;
}

.analyze-info h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 10px 0;
}

.step-text {
  font-size: 14px;
  opacity: 0.9;
  margin: 0;
}

.analyze-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 24px 0;
}

.progress-track {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: white;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  font-weight: 500;
  min-width: 40px;
}

.analyze-steps {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 24px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  opacity: 0.6;
  transition: all 0.3s ease;
}

.step-item.active {
  opacity: 1;
}

.step-item.completed {
  opacity: 0.8;
}

.step-indicator {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-indicator svg {
  width: 12px;
  height: 12px;
  color: #34c759;
}

.step-dot {
  width: 6px;
  height: 6px;
  background: currentColor;
  border-radius: 50%;
}

/* 评分区域 */
.scores-section {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
}

.main-score-card {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 32px;
  background: linear-gradient(135deg, rgba(0, 122, 255, 0.08) 0%, rgba(88, 86, 214, 0.08) 100%);
  border-radius: 16px;
}

.score-circle {
  position: relative;
  width: 120px;
  height: 120px;
  margin-bottom: 12px;
}

.score-circle svg {
  transform: rotate(-90deg);
}

.score-bg {
  stroke: rgba(0, 0, 0, 0.06);
}

.score-fill {
  stroke-linecap: round;
  transition: stroke-dashoffset 0.6s ease;
}

.score-value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.score-value .number {
  font-size: 32px;
  font-weight: 700;
  color: #1d1d1f;
}

.score-value .unit {
  font-size: 14px;
  color: #86868b;
  margin-left: 2px;
}

.score-label {
  font-size: 13px;
  font-weight: 500;
  color: #86868b;
}

.sub-scores {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sub-score-card {
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 10px;
}

.sub-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
}

.sub-header svg {
  width: 16px;
  height: 16px;
  color: #86868b;
}

.sub-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sub-track {
  flex: 1;
  height: 6px;
  background: rgba(0, 0, 0, 0.06);
  border-radius: 3px;
  overflow: hidden;
}

.sub-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}

.sub-value {
  font-size: 13px;
  font-weight: 600;
  color: #1d1d1f;
  min-width: 40px;
  text-align: right;
}

/* 分析卡片 */
.analysis-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.analysis-card {
  padding: 20px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.02);
}

.analysis-card.strengths {
  background: rgba(52, 199, 89, 0.06);
}

.analysis-card.weaknesses {
  background: rgba(255, 149, 0, 0.06);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.card-header svg {
  width: 20px;
  height: 20px;
}

.analysis-card.strengths .card-header svg {
  color: #34c759;
}

.analysis-card.weaknesses .card-header svg {
  color: #ff9500;
}

.card-header h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0;
}

.card-list {
  margin: 0;
  padding-left: 18px;
  list-style: disc;
}

.card-list li {
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 6px;
}

.analysis-card.strengths .card-list li {
  color: #2d8a4e;
}

.analysis-card.weaknesses .card-list li {
  color: #c67a00;
}

/* 详细分析折叠 */
.detail-section {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.collapse-item {
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.collapse-item:last-child {
  border-bottom: none;
}

.collapse-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: rgba(0, 0, 0, 0.02);
  cursor: pointer;
  transition: background 0.15s ease;
}

.collapse-header:hover {
  background: rgba(0, 0, 0, 0.04);
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  font-weight: 500;
  color: #1d1d1f;
}

.collapse-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
}

.collapse-icon.personal { background: rgba(0, 122, 255, 0.1); color: #007aff; }
.collapse-icon.education { background: rgba(88, 86, 214, 0.1); color: #5856d6; }
.collapse-icon.work { background: rgba(255, 149, 0, 0.1); color: #ff9500; }
.collapse-icon.skills { background: rgba(255, 59, 48, 0.1); color: #ff3b30; }

.collapse-icon svg {
  width: 16px;
  height: 16px;
}

.collapse-arrow {
  width: 18px;
  height: 18px;
  color: #86868b;
  transition: transform 0.2s ease;
}

.collapse-arrow.expanded {
  transform: rotate(180deg);
}

.collapse-content {
  padding: 20px;
  background: white;
}

.analysis-detail {
  display: flex;
  gap: 16px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  height: fit-content;
}

.status-badge.good {
  background: rgba(52, 199, 89, 0.1);
  color: #34c759;
}

.status-badge.warning {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.detail-info {
  flex: 1;
}

.info-row {
  margin-bottom: 8px;
  font-size: 13px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  font-weight: 500;
  color: #86868b;
}

.info-row .value {
  color: #1d1d1f;
}

/* 优化建议 */
.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 500px;
  overflow-y: auto;
}

.suggestion-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
  border: 2px solid transparent;
}

.suggestion-card:hover {
  background: rgba(0, 0, 0, 0.04);
}

.suggestion-card.selected {
  background: rgba(0, 122, 255, 0.05);
  border-color: rgba(0, 122, 255, 0.3);
}

.suggestion-check {
  flex-shrink: 0;
  padding-top: 2px;
}

.checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(0, 0, 0, 0.15);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.checkbox.checked {
  background: #007aff;
  border-color: #007aff;
}

.checkbox svg {
  width: 12px;
  height: 12px;
  color: white;
}

.suggestion-body {
  flex: 1;
}

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.priority-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.priority-tag.high {
  background: rgba(255, 59, 48, 0.1);
  color: #ff3b30;
}

.priority-tag.medium {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.priority-tag.low {
  background: rgba(142, 142, 147, 0.1);
  color: #8e8e93;
}

.suggestion-title {
  font-size: 14px;
  font-weight: 600;
  color: #1d1d1f;
}

.suggestion-desc {
  font-size: 13px;
  color: #424245;
  line-height: 1.5;
  margin: 0 0 12px 0;
}

.diff-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}

.diff-item {
  padding: 12px;
  border-radius: 8px;
  font-size: 12px;
}

.diff-item.before {
  background: rgba(255, 59, 48, 0.08);
}

.diff-item.after {
  background: rgba(0, 122, 255, 0.08);
}

.diff-label {
  font-weight: 600;
  margin-bottom: 6px;
  display: block;
}

.diff-item.before .diff-label { color: #ff3b30; }
.diff-item.after .diff-label { color: #007aff; }

.diff-item p {
  margin: 0;
  color: #424245;
  line-height: 1.5;
}

.suggestion-reason {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 12px;
  color: #86868b;
}

.suggestion-reason svg {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  margin-top: 1px;
}

/* 优化历史 */
.history-timeline {
  position: relative;
  padding-left: 24px;
}

.history-timeline::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: rgba(0, 0, 0, 0.06);
}

.history-item {
  position: relative;
  padding-bottom: 20px;
}

.history-item:last-child {
  padding-bottom: 0;
}

.history-dot {
  position: absolute;
  left: -20px;
  top: 6px;
  width: 10px;
  height: 10px;
  background: #007aff;
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.2);
}

.history-card {
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 10px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.history-title {
  font-size: 14px;
  font-weight: 600;
  color: #1d1d1f;
}

.history-time {
  font-size: 12px;
  color: #86868b;
}

.history-desc {
  font-size: 13px;
  color: #424245;
  margin: 0 0 12px 0;
}

.history-actions {
  display: flex;
  gap: 8px;
}

.history-btn {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  font-size: 12px;
  color: #1d1d1f;
  cursor: pointer;
  transition: all 0.15s ease;
}

.history-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}

.history-btn.primary {
  background: #007aff;
  border-color: #007aff;
  color: white;
}

.history-btn.primary:hover {
  background: #0066d6;
}

.export-section {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: transparent;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 13px;
  color: #1d1d1f;
  cursor: pointer;
  transition: all 0.15s ease;
}

.export-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.15);
}

.export-btn svg {
  width: 16px;
  height: 16px;
}

/* Modal 容器 */
.modal-container {
  width: 480px;
  max-height: 90vh;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px) saturate(180%);
  border-radius: 12px;
  box-shadow: 
    0 0 0 1px rgba(0, 0, 0, 0.1),
    0 24px 80px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-container.large {
  width: 800px;
}

.modal-titlebar {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(180deg, #f6f6f6 0%, #e8e8e8 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.modal-title {
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
}

.modal-content {
  padding: 24px;
  overflow-y: auto;
}

.compare-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.compare-pane {
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.pane-header {
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.04);
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.pane-content {
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
  font-size: 13px;
  line-height: 1.7;
  color: #424245;
  white-space: pre-wrap;
}

/* 过渡动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container,
.modal-enter-from .analyze-modal,
.modal-leave-to .analyze-modal {
  transform: scale(0.95) translateY(-10px);
}

.collapse-enter-active,
.collapse-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}

.collapse-enter-from,
.collapse-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

/* 滚动条 */
.suggestions-list::-webkit-scrollbar,
.pane-content::-webkit-scrollbar {
  width: 6px;
}

.suggestions-list::-webkit-scrollbar-track,
.pane-content::-webkit-scrollbar-track {
  background: transparent;
}

.suggestions-list::-webkit-scrollbar-thumb,
.pane-content::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
}
</style>

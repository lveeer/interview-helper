<template>
  <div class="resume-optimize">
    <!-- 简历选择区域 -->
    <el-card class="mb-4">
      <template #header>
        <div class="card-header">
          <span>选择简历</span>
        </div>
      </template>
      <el-select
        v-model="selectedResumeId"
        placeholder="请选择要优化的简历"
        style="width: 100%; margin-bottom: 15px;"
        @change="handleResumeChange"
      >
        <el-option
          v-for="resume in resumeList"
          :key="resume.id"
          :label="resume.file_name"
          :value="resume.id"
        />
      </el-select>

      <!-- JD 输入区域 -->
      <div class="jd-section">
        <div class="jd-header">
          <span class="jd-label">职位描述（JD）</span>
          <el-button
            v-if="jobDescription"
            type="text"
            size="small"
            @click="clearJD"
          >
            清除
          </el-button>
        </div>
        <el-input
          v-model="jobDescription"
          type="textarea"
          :rows="16"
          placeholder="请输入职位描述（JD），系统将根据 JD 提供针对性的简历分析和优化建议...&#10;&#10;例如：&#10;职位：前端开发工程师&#10;要求：&#10;- 3年以上 Vue.js 开发经验&#10;- 熟悉 TypeScript、ES6&#10;- 有大型项目经验优先&#10;- 良好的团队协作能力"
          class="jd-input"
        />
        <div class="jd-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>输入 JD 后，系统会根据职位要求提供更精准的分析和建议</span>
        </div>
      </div>

      <!-- 开始分析按钮 -->
      <div class="analyze-actions">
        <el-button
          type="primary"
          size="large"
          :disabled="!selectedResumeId"
          :loading="analyzing"
          @click="handleAnalyze"
        >
          <el-icon><Search /></el-icon>
          开始分析
        </el-button>
      </div>
    </el-card>

    <!-- AI 分析加载动画 -->
    <el-dialog
      v-model="analyzing"
      :show-close="false"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      width="600px"
      class="ai-analyze-dialog"
    >
      <div class="ai-analyze-container">
        <!-- AI 核心动画 -->
        <div class="ai-core">
          <div class="ai-ring ring-1"></div>
          <div class="ai-ring ring-2"></div>
          <div class="ai-ring ring-3"></div>
          <div class="ai-center">
            <el-icon class="ai-icon"><Search /></el-icon>
          </div>
        </div>

        <!-- 扫描线效果 -->
        <div class="scan-line"></div>

        <!-- 分析状态 -->
        <div class="analyze-status">
          <h3 class="status-title">AI 正在分析您的简历</h3>
          <p class="status-text">{{ currentAnalyzeStep }}</p>
        </div>

        <!-- 分析进度条 -->
        <div class="analyze-progress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: analyzeProgress + '%' }"></div>
          </div>
          <div class="progress-text">{{ analyzeProgress.toFixed(1) }}%</div>
        </div>

        <!-- 分析步骤 -->
        <div class="analyze-steps">
          <div
            v-for="(step, index) in analyzeSteps"
            :key="index"
            class="step-item"
            :class="{ active: index === currentStepIndex, completed: index < currentStepIndex }"
          >
            <div class="step-icon">
              <el-icon v-if="index < currentStepIndex"><Check /></el-icon>
              <div v-else class="step-dot"></div>
            </div>
            <span class="step-text">{{ step }}</span>
          </div>
        </div>

        <!-- 科技装饰 -->
        <div class="tech-decoration">
          <div class="tech-line line-1"></div>
          <div class="tech-line line-2"></div>
          <div class="tech-line line-3"></div>
          <div class="tech-line line-4"></div>
        </div>
      </div>
    </el-dialog>

    <!-- 简历分析结果 -->
    <el-card v-if="selectedResumeId && analysisResult" class="mb-4">
      <template #header>
        <div class="card-header">
          <span>简历分析报告</span>
          <el-button type="primary" @click="handleAnalyze" :loading="analyzing">
            <el-icon><Refresh /></el-icon>
            重新分析
          </el-button>
        </div>
      </template>

      <!-- 评分卡片 -->
      <el-row :gutter="20" class="mb-4">
        <el-col :span="6">
          <el-card shadow="hover" class="score-card">
            <div class="score-content">
              <el-progress
                type="circle"
                :percentage="analysisResult.overall_score"
                :color="getScoreColor(analysisResult.overall_score)"
                :width="120"
              />
              <div class="score-label">综合评分</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="18">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card shadow="hover" class="mini-score-card">
                <div class="mini-score-title">内容完整性</div>
                <el-progress
                  :percentage="analysisResult.content_score"
                  :color="getScoreColor(analysisResult.content_score)"
                />
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover" class="mini-score-card">
                <div class="mini-score-title">专业匹配度</div>
                <el-progress
                  :percentage="analysisResult.match_score"
                  :color="getScoreColor(analysisResult.match_score)"
                />
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover" class="mini-score-card">
                <div class="mini-score-title">表达清晰度</div>
                <el-progress
                  :percentage="analysisResult.clarity_score"
                  :color="getScoreColor(analysisResult.clarity_score)"
                />
              </el-card>
            </el-col>
          </el-row>
        </el-col>
      </el-row>

      <!-- 优势与不足 -->
      <el-row :gutter="20" class="mb-4">
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span class="highlight-title success">
                <el-icon><SuccessFilled /></el-icon>
                简历优势
              </span>
            </template>
            <ul class="strength-list">
              <li v-for="(strength, index) in analysisResult.strengths" :key="index">
                {{ strength }}
              </li>
            </ul>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span class="highlight-title warning">
                <el-icon><WarningFilled /></el-icon>
                需要改进
              </span>
            </template>
            <ul class="weakness-list">
              <li v-for="(weakness, index) in analysisResult.weaknesses" :key="index">
                {{ weakness }}
              </li>
            </ul>
          </el-card>
        </el-col>
      </el-row>

      <!-- 详细分析 -->
      <el-collapse v-model="activeCollapse" class="mb-4">
        <el-collapse-item title="个人信息分析" name="personal">
          <div v-if="analysisResult.personal_analysis">
            <el-alert
              v-if="analysisResult.personal_analysis.status === 'good'"
              title="个人信息完整"
              type="success"
              :closable="false"
              class="mb-2"
            />
            <el-alert
              v-else
              :title="analysisResult.personal_analysis.message"
              type="warning"
              :closable="false"
              class="mb-2"
            />
            <div class="analysis-detail">
              <p><strong>已包含：</strong>{{ analysisResult.personal_analysis.included.join(', ') || '无' }}</p>
              <p><strong>缺失：</strong>{{ analysisResult.personal_analysis.missing.join(', ') || '无' }}</p>
            </div>
          </div>
        </el-collapse-item>

        <el-collapse-item title="教育背景分析" name="education">
          <div v-if="analysisResult.education_analysis">
            <el-alert
              v-if="analysisResult.education_analysis.status === 'good'"
              title="教育背景清晰"
              type="success"
              :closable="false"
              class="mb-2"
            />
            <el-alert
              v-else
              :title="analysisResult.education_analysis.message"
              type="info"
              :closable="false"
              class="mb-2"
            />
            <div class="analysis-detail">
              <p><strong>建议：</strong>{{ analysisResult.education_analysis.suggestions }}</p>
            </div>
          </div>
        </el-collapse-item>

        <el-collapse-item title="工作经历分析" name="experience">
          <div v-if="analysisResult.experience_analysis">
            <el-alert
              v-if="analysisResult.experience_analysis.status === 'good'"
              title="工作经历描述充分"
              type="success"
              :closable="false"
              class="mb-2"
            />
            <el-alert
              v-else
              :title="analysisResult.experience_analysis.message"
              type="warning"
              :closable="false"
              class="mb-2"
            />
            <div class="analysis-detail">
              <p><strong>问题：</strong>{{ analysisResult.experience_analysis.issues }}</p>
              <p><strong>建议：</strong>{{ analysisResult.experience_analysis.suggestions }}</p>
            </div>
          </div>
        </el-collapse-item>

        <el-collapse-item title="技能分析" name="skills">
          <div v-if="analysisResult.skills_analysis">
            <el-alert
              v-if="analysisResult.skills_analysis.status === 'good'"
              title="技能描述清晰"
              type="success"
              :closable="false"
              class="mb-2"
            />
            <el-alert
              v-else
              :title="analysisResult.skills_analysis.message"
              type="info"
              :closable="false"
              class="mb-2"
            />
            <div class="analysis-detail">
              <p><strong>硬技能：</strong>{{ analysisResult.skills_analysis.hard_skills.join(', ') || '无' }}</p>
              <p><strong>软技能：</strong>{{ analysisResult.skills_analysis.soft_skills.join(', ') || '无' }}</p>
              <p><strong>建议：</strong>{{ analysisResult.skills_analysis.suggestions }}</p>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </el-card>

    <!-- 优化建议 -->
    <el-card v-if="selectedResumeId && suggestions.length > 0" class="mb-4">
      <template #header>
        <div class="card-header">
          <span>优化建议 ({{ suggestions.length }})</span>
          <div>
            <el-button @click="selectAllSuggestions">全选</el-button>
            <el-button @click="deselectAllSuggestions">取消全选</el-button>
            <el-button type="primary" @click="handleApplyOptimizations" :loading="applying">
              <el-icon><Check /></el-icon>
              应用选中建议
            </el-button>
          </div>
        </div>
      </template>

      <div class="suggestions-container">
        <div
          v-for="(suggestion, index) in suggestions"
          :key="index"
          class="suggestion-item"
          :class="{ selected: suggestion.selected }"
        >
          <el-checkbox v-model="suggestion.selected" class="suggestion-checkbox">
            <span class="suggestion-tag" :class="suggestion.priority">
              {{ suggestion.priority === 'high' ? '重要' : suggestion.priority === 'medium' ? '中等' : '建议' }}
            </span>
            <span class="suggestion-title">{{ suggestion.title }}</span>
          </el-checkbox>

          <div class="suggestion-content">
            <div class="suggestion-description">{{ suggestion.description }}</div>
            <div v-if="suggestion.before && suggestion.after" class="suggestion-diff">
              <div class="diff-section">
                <span class="diff-label">原文：</span>
                <div class="diff-content before">{{ suggestion.before }}</div>
              </div>
              <div class="diff-section">
                <span class="diff-label">建议：</span>
                <div class="diff-content after">{{ suggestion.after }}</div>
              </div>
            </div>
            <div v-if="suggestion.reason" class="suggestion-reason">
              <el-icon><InfoFilled /></el-icon>
              <span>原因：{{ suggestion.reason }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 优化历史 -->
    <el-card v-if="selectedResumeId && optimizationHistory.length > 0">
      <template #header>
        <div class="card-header">
          <span>优化历史</span>
          <el-button @click="loadOptimizationHistory">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-timeline>
        <el-timeline-item
          v-for="(history, index) in optimizationHistory"
          :key="index"
          :timestamp="formatDate(history.created_at)"
          :type="history.status === 'success' ? 'success' : 'info'"
        >
          <div class="history-item">
            <div class="history-title">{{ history.title }}</div>
            <div class="history-detail">{{ history.description }}</div>
            <div class="history-actions">
              <el-button size="small" @click="handleCompare(history)">
                查看对比
              </el-button>
              <el-button size="small" type="primary" @click="handleRestore(history)">
                恢复此版本
              </el-button>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>

      <!-- 导出按钮 -->
      <div class="export-section">
        <el-button type="primary" @click="handleExport('pdf')">
          <el-icon><Download /></el-icon>
          导出为 PDF
        </el-button>
        <el-button @click="handleExport('docx')">
          <el-icon><Download /></el-icon>
          导出为 Word
        </el-button>
      </div>
    </el-card>

    <!-- 对比对话框 -->
    <el-dialog v-model="showCompareDialog" title="版本对比" width="900px">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>优化前</span>
            </template>
            <div class="compare-content">{{ compareData.before }}</div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>优化后</span>
            </template>
            <div class="compare-content">{{ compareData.after }}</div>
          </el-card>
        </el-col>
      </el-row>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Check,
  Download,
  InfoFilled,
  SuccessFilled,
  WarningFilled,
  Search
} from '@element-plus/icons-vue'
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
const activeCollapse = ref(['personal', 'education', 'experience', 'skills'])
const showCompareDialog = ref(false)
const compareData = ref({ before: '', after: '' })
const jobDescription = ref('')

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
    // 清空之前的分析结果和建议
    analysisResult.value = null
    suggestions.value = []
    // 只加载优化历史
    await loadOptimizationHistory()
  }
}

const handleAnalyze = async () => {
  if (!selectedResumeId.value) {
    ElMessage.warning('请先选择简历')
    return
  }

  // 开始分析动画
  analyzing.value = true
  analyzeProgress.value = 0
  currentStepIndex.value = 0
  currentAnalyzeStep.value = analyzeSteps[0]

  // 启动进度动画
  startAnalyzeAnimation()

  try {
    // 当 JD 不为空时，强制刷新分析结果
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
    // Mock 数据用于演示
    analysisResult.value = getMockAnalysisResult()
    ElMessage.success('分析完成（演示数据）')
  } finally {
    // 停止动画，完成进度
    stopAnalyzeAnimation()
    analyzing.value = false
  }
}

const startAnalyzeAnimation = () => {
  // 进度条动画
  progressTimer = setInterval(() => {
    if (analyzeProgress.value < 95) {
      analyzeProgress.value += Math.random() * 3
      analyzeProgress.value = Math.round(analyzeProgress.value * 10) / 10
    }
  }, 300)

  // 步骤切换动画
  analyzeTimer = setInterval(() => {
    if (currentStepIndex.value < analyzeSteps.length - 1) {
      currentStepIndex.value++
      currentAnalyzeStep.value = analyzeSteps[currentStepIndex.value]
    }
  }, 800)
}

const stopAnalyzeAnimation = () => {
  // 清除定时器
  if (analyzeTimer) clearInterval(analyzeTimer)
  if (progressTimer) clearInterval(progressTimer)

  // 完成动画
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
    // 当 JD 不为空时，强制刷新优化建议
    const forceRefresh = !!jobDescription.value
    const res = await getOptimizationSuggestions(selectedResumeId.value, jobDescription.value, forceRefresh)
    if (res.code === 200) {
      suggestions.value = (res.data || []).map(s => ({ ...s, selected: false }))
    }
  } catch (error) {
    console.error('加载优化建议失败:', error)
    // Mock 数据用于演示
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
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
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
  },
  {
    id: 4,
    priority: 'medium',
    title: '添加技能熟练度',
    description: '为每个技能标注熟练度等级，如"精通"、"熟练"、"了解"',
    before: '技能：JavaScript, Vue.js, Python',
    after: '技能：JavaScript（精通）、Vue.js（熟练）、Python（了解）、MySQL（熟练）',
    reason: '技能熟练度能让HR快速了解你的技术能力分布',
    selected: false
  },
  {
    id: 5,
    priority: 'low',
    title: '优化排版格式',
    description: '统一字体、字号和间距，使简历更加整洁易读',
    before: '格式不统一，字号大小不一',
    after: '使用统一的字体（微软雅黑）、标题字号（16pt）、正文字号（12pt），段落间距1.5倍',
    reason: '良好的排版能提升简历的专业度和可读性',
    selected: false
  }
]

onMounted(() => {
  loadResumeList()
})
</script>

<style scoped>
.resume-optimize {
  padding: 20px;
}

.jd-section {
  margin-top: 15px;
}

.jd-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.jd-label {
  font-size: 14px;
  font-weight: bold;
  color: var(--text-primary);
}

.jd-input {
  margin-bottom: 10px;
}

.jd-tip {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: var(--text-secondary);
  background-color: var(--bg-color-light);
  padding: 8px 12px;
  border-radius: 4px;
}

.jd-tip .el-icon {
  margin-right: 5px;
  color: #409eff;
}

.analyze-actions {
  margin-top: 20px;
  text-align: center;
}

.analyze-actions .el-button {
  min-width: 160px;
}

.mb-4 {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-card {
  text-align: center;
}

.score-content {
  padding: 20px 0;
}

.score-label {
  margin-top: 15px;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.mini-score-card {
  padding: 15px;
}

.mini-score-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.highlight-title {
  display: flex;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.highlight-title.success {
  color: #67c23a;
}

.highlight-title.warning {
  color: #e6a23c;
}

.highlight-title .el-icon {
  margin-right: 8px;
}

.strength-list,
.weakness-list {
  margin: 0;
  padding-left: 20px;
}

.strength-list li {
  color: #67c23a;
  margin-bottom: 8px;
  line-height: 1.6;
}

.weakness-list li {
  color: #e6a23c;
  margin-bottom: 8px;
  line-height: 1.6;
}

.analysis-detail p {
  margin: 8px 0;
  color: #606266;
  line-height: 1.6;
}

.suggestions-container {
  max-height: 600px;
  overflow-y: auto;
}

.suggestion-item {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
  transition: all 0.3s;
}

.suggestion-item.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.suggestion-checkbox {
  margin-bottom: 10px;
}

.suggestion-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 12px;
  margin-right: 8px;
  color: white;
}

.suggestion-tag.high {
  background-color: #f56c6c;
}

.suggestion-tag.medium {
  background-color: #e6a23c;
}

.suggestion-tag.low {
  background-color: #909399;
}

.suggestion-title {
  font-weight: bold;
  font-size: 15px;
  color: #303133;
}

.suggestion-content {
  margin-left: 24px;
}

.suggestion-description {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 10px;
}

.suggestion-diff {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 10px;
}

.diff-section {
  margin-bottom: 8px;
}

.diff-label {
  font-weight: bold;
  font-size: 13px;
  color: #303133;
}

.diff-content {
  padding: 8px;
  border-radius: 3px;
  margin-top: 5px;
  font-size: 13px;
  line-height: 1.6;
}

.diff-content.before {
  background-color: #fef0f0;
  color: #f56c6c;
}

.diff-content.after {
  background-color: #f0f9ff;
  color: #409eff;
}

.suggestion-reason {
  display: flex;
  align-items: center;
  color: #909399;
  font-size: 13px;
}

.suggestion-reason .el-icon {
  margin-right: 5px;
}

.history-item {
  padding: 10px;
}

.history-title {
  font-weight: bold;
  font-size: 15px;
  color: #303133;
  margin-bottom: 5px;
}

.history-detail {
  color: #606266;
  font-size: 14px;
  margin-bottom: 10px;
  line-height: 1.6;
}

.history-actions {
  display: flex;
  gap: 10px;
}

.export-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #dcdfe6;
  text-align: center;
}

.compare-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
}

/* AI 分析动画样式 */
.ai-analyze-dialog :deep(.el-dialog__header) {
  display: none !important;
}

.ai-analyze-dialog :deep(.el-dialog) {
  background: transparent !important;
  box-shadow: none !important;
}

.ai-analyze-dialog :deep(.el-dialog__body) {
  padding: 40px !important;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border-radius: 12px !important;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3) !important;
}

.ai-analyze-dialog :deep(.el-overlay-dialog) {
  background: rgba(0, 0, 0, 0.5) !important;
}

.ai-analyze-container {
  position: relative;
  text-align: center;
  color: white !important;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  min-height: 400px;
  padding: 20px;
  border-radius: 12px;
}

/* AI 核心动画 */
.ai-core {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 0 auto 40px;
}

.ai-ring {
  position: absolute;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.6);
  animation: rotate 3s linear infinite;
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
}

.ring-1 {
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  animation-duration: 3s;
}

.ring-2 {
  width: 75%;
  height: 75%;
  top: 12.5%;
  left: 12.5%;
  animation-duration: 2s;
  animation-direction: reverse;
}

.ring-3 {
  width: 50%;
  height: 50%;
  top: 25%;
  left: 25%;
  animation-duration: 1.5s;
}

.ai-center {
  position: absolute;
  width: 80px;
  height: 80px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse 2s ease-in-out infinite;
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.4);
}

.ai-icon {
  font-size: 40px;
  color: white !important;
  animation: iconRotate 4s linear infinite;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.8));
}

@keyframes rotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
  50% { transform: translate(-50%, -50%) scale(1.1); opacity: 0.8; }
}

@keyframes iconRotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 扫描线效果 */
.scan-line {
  position: absolute;
  width: 100%;
  height: 3px;
  top: 0;
  left: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 1), transparent);
  animation: scan 2s linear infinite;
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.8);
}

@keyframes scan {
  0% { top: 0; opacity: 0; }
  50% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}

/* 分析状态 */
.analyze-status {
  margin-bottom: 30px;
}

.status-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  color: white !important;
}

.status-text {
  font-size: 16px;
  opacity: 0.9;
  animation: fadeInOut 1.5s ease-in-out infinite;
  color: white !important;
}

@keyframes fadeInOut {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* 进度条 */
.analyze-progress {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  gap: 15px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.3) !important;
  border-radius: 3px;
  overflow: hidden;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00c6fb 0%, #005bea 100%);
  border-radius: 3px;
  transition: width 0.3s ease;
  box-shadow: 0 0 15px rgba(0, 198, 251, 0.8);
}

.progress-text {
  font-size: 18px;
  font-weight: bold;
  min-width: 50px;
  color: white !important;
}

/* 分析步骤 */
.analyze-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
  text-align: left;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.step-item.active {
  background: rgba(255, 255, 255, 0.2) !important;
  animation: stepGlow 1.5s ease-in-out infinite;
  color: white !important;
}

.step-item.completed {
  opacity: 0.7;
  color: white !important;
}

.step-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-dot {
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  animation: dotPulse 1s ease-in-out infinite;
}

.step-item.active .step-dot {
  background: var(--primary-light) !important;
  box-shadow: 0 0 15px rgba(0, 198, 251, 1) !important;
}

.step-text {
  font-size: 14px;
  flex: 1;
  color: white !important;
}

@keyframes stepGlow {
  0%, 100% { box-shadow: 0 0 5px rgba(255, 255, 255, 0.3); }
  50% { box-shadow: 0 0 15px rgba(255, 255, 255, 0.6); }
}

@keyframes dotPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.3); }
}

/* 科技装饰 */
.tech-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
  overflow: hidden;
}

.tech-line {
  position: absolute;
  width: 2px;
  height: 100%;
  background: linear-gradient(180deg, transparent, rgba(255, 255, 255, 0.1), transparent);
}

.line-1 {
  left: 10%;
  animation: techMove 3s ease-in-out infinite;
}

.line-2 {
  left: 30%;
  animation: techMove 3s ease-in-out infinite 0.5s;
}

.line-3 {
  right: 30%;
  animation: techMove 3s ease-in-out infinite 1s;
}

.line-4 {
  right: 10%;
  animation: techMove 3s ease-in-out infinite 1.5s;
}

@keyframes techMove {
  0%, 100% { transform: translateY(-100%); opacity: 0; }
  50% { transform: translateY(100%); opacity: 0.3; }
}
</style>
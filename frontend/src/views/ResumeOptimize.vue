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
        style="width: 100%"
        @change="handleResumeChange"
      >
        <el-option
          v-for="resume in resumeList"
          :key="resume.id"
          :label="resume.file_name"
          :value="resume.id"
        />
      </el-select>
    </el-card>

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
  WarningFilled
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
    await handleAnalyze()
    await loadSuggestions()
    await loadOptimizationHistory()
  }
}

const handleAnalyze = async () => {
  if (!selectedResumeId.value) {
    ElMessage.warning('请先选择简历')
    return
  }

  analyzing.value = true
  try {
    const res = await analyzeResume(selectedResumeId.value)
    if (res.code === 200) {
      analysisResult.value = res.data
      ElMessage.success('分析完成')
    } else {
      ElMessage.error(res.message || '分析失败')
    }
  } catch (error) {
    console.error('分析失败:', error)
    // Mock 数据用于演示
    analysisResult.value = getMockAnalysisResult()
    ElMessage.success('分析完成（演示数据）')
  } finally {
    analyzing.value = false
  }
}

const loadSuggestions = async () => {
  if (!selectedResumeId.value) return

  try {
    const res = await getOptimizationSuggestions(selectedResumeId.value)
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
</style>
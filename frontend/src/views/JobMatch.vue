<template>
  <div class="match-page">
    <!-- 岗位匹配窗口 -->
    <div class="macos-window">
      <div class="window-titlebar">
        <div class="window-title">
          <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="8.5" cy="7" r="4"></circle>
            <line x1="20" y1="8" x2="20" y2="14"></line>
            <line x1="23" y1="11" x2="17" y2="11"></line>
          </svg>
          <span>岗位匹配分析</span>
        </div>
      </div>

      <div class="window-content">
        <div class="form-section">
          <!-- 选择简历 -->
          <div class="form-group">
            <label class="form-label">选择简历</label>
            <div class="select-wrapper">
              <select v-model="matchForm.resume_id" class="macos-select">
                <option value="" disabled>请选择简历</option>
                <option v-for="resume in resumeList" :key="resume.id" :value="resume.id">
                  {{ resume.file_name }}
                </option>
              </select>
              <svg class="select-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
          </div>

          <!-- 岗位描述 -->
          <div class="form-group">
            <label class="form-label">岗位描述</label>
            <textarea
              v-model="matchForm.job_description"
              class="macos-textarea"
              rows="10"
              placeholder="请输入目标岗位的职位描述（JD）..."
            ></textarea>
          </div>

          <!-- 操作按钮 -->
          <div class="form-actions">
            <button class="btn-secondary" @click="resetForm">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path>
                <path d="M3 3v5h5"></path>
              </svg>
              <span>重置</span>
            </button>
            <button class="btn-primary" :disabled="analyzing" @click="handleMatch">
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
    </div>

    <!-- 匹配结果 -->
    <Transition name="slide-fade">
      <div v-if="matchResult" class="macos-window result-window">
        <div class="window-titlebar">
          <div class="window-controls">
            <span class="control close"></span>
            <span class="control minimize"></span>
            <span class="control maximize"></span>
          </div>
          <div class="window-title">匹配结果</div>
        </div>

        <div class="window-content">
          <!-- 总体匹配度 -->
          <div class="score-section">
            <div class="main-score">
              <div class="score-ring">
                <svg viewBox="0 0 120 120">
                  <circle class="ring-bg" cx="60" cy="60" r="52" fill="none" stroke-width="10"/>
                  <circle
                    class="ring-fill"
                    cx="60" cy="60" r="52"
                    fill="none"
                    stroke-width="10"
                    :stroke-dasharray="327"
                    :stroke-dashoffset="327 - (327 * matchResult.match_score / 100)"
                    :style="{ stroke: getScoreColor(matchResult.match_score) }"
                  />
                </svg>
                <div class="score-display">
                  <span class="score-value">{{ matchResult.match_score }}</span>
                  <span class="score-unit">%</span>
                </div>
              </div>
              <div class="score-info">
                <h3>总体匹配度</h3>
                <p>{{ getMatchLevel(matchResult.match_score) }}</p>
              </div>
            </div>

            <div class="detail-scores">
              <div class="score-item">
                <div class="score-header">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                  </svg>
                  <span>关键词匹配</span>
                  <span class="score-percent">{{ matchResult.keyword_match }}%</span>
                </div>
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: matchResult.keyword_match + '%', background: getScoreColor(matchResult.keyword_match) }"
                  ></div>
                </div>
              </div>

              <div class="score-item">
                <div class="score-header">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 20h9"></path>
                    <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
                  </svg>
                  <span>技能匹配</span>
                  <span class="score-percent">{{ matchResult.skill_match }}%</span>
                </div>
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: matchResult.skill_match + '%', background: getScoreColor(matchResult.skill_match) }"
                  ></div>
                </div>
              </div>

              <div class="score-item">
                <div class="score-header">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                  </svg>
                  <span>项目相关性</span>
                  <span class="score-percent">{{ matchResult.project_relevance }}%</span>
                </div>
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: matchResult.project_relevance + '%', background: getScoreColor(matchResult.project_relevance) }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- 分析结果卡片 -->
          <div class="result-cards">
            <!-- 优势 -->
            <div class="result-card strengths">
              <div class="card-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
              </div>
              <h4>优势</h4>
              <ul>
                <li v-for="strength in matchResult.strengths" :key="strength">{{ strength }}</li>
              </ul>
            </div>

            <!-- 缺失技能 -->
            <div class="result-card missing">
              <div class="card-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="15" y1="9" x2="9" y2="15"></line>
                  <line x1="9" y1="9" x2="15" y2="15"></line>
                </svg>
              </div>
              <h4>缺失技能</h4>
              <div class="skill-tags">
                <span v-for="skill in matchResult.missing_skills" :key="skill" class="skill-tag">{{ skill }}</span>
              </div>
            </div>

            <!-- 优化建议 -->
            <div class="result-card suggestions">
              <div class="card-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="16" x2="12" y2="12"></line>
                  <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
              </div>
              <h4>优化建议</h4>
              <ul>
                <li v-for="suggestion in matchResult.suggestions" :key="suggestion">{{ suggestion }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getResumeList } from '@/api/resume'
import { matchJob } from '@/api/job'

const analyzing = ref(false)
const resumeList = ref([])
const matchResult = ref(null)

const matchForm = ref({
  resume_id: '',
  job_description: ''
})

const loadResumeList = async () => {
  try {
    const res = await getResumeList()
    if (res.code === 200) {
      resumeList.value = res.data || []
    }
  } catch (error) {
    console.error('加载简历列表失败:', error)
  }
}

const handleMatch = async () => {
  if (!matchForm.value.resume_id) {
    ElMessage.warning('请选择简历')
    return
  }

  if (!matchForm.value.job_description.trim()) {
    ElMessage.warning('请输入岗位描述')
    return
  }

  analyzing.value = true
  try {
    const res = await matchJob(matchForm.value)
    if (res.code === 200) {
      matchResult.value = res.data
      ElMessage.success('分析完成')
    }
  } catch (error) {
    console.error('分析失败:', error)
    // Mock 数据用于演示
    matchResult.value = {
      match_score: 75,
      keyword_match: 82,
      skill_match: 68,
      project_relevance: 78,
      strengths: [
        '具备 Vue.js 前端开发经验',
        '熟悉后端 Python 开发',
        '有完整的项目开发经历'
      ],
      missing_skills: ['React', 'TypeScript', 'Docker'],
      suggestions: [
        '建议补充 React 框架相关经验',
        '学习 TypeScript 提升代码质量',
        '了解容器化部署技术'
      ]
    }
    ElMessage.success('分析完成（演示数据）')
  } finally {
    analyzing.value = false
  }
}

const resetForm = () => {
  matchForm.value = {
    resume_id: '',
    job_description: ''
  }
  matchResult.value = null
}

const getScoreColor = (score) => {
  if (score >= 80) return '#34c759'
  if (score >= 60) return '#ff9500'
  return '#ff3b30'
}

const getMatchLevel = (score) => {
  if (score >= 80) return '匹配度较高，建议投递'
  if (score >= 60) return '匹配度中等，建议优化简历'
  return '匹配度较低，需要提升相关技能'
}

onMounted(() => {
  loadResumeList()
})
</script>

<style scoped>
/* 页面容器 */
.match-page {
  padding: 24px;
  min-height: 100%;
  background: linear-gradient(180deg, #f5f5f7 0%, #ffffff 100%);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* macOS 窗口样式 */
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

.window-content {
  padding: 24px;
}

/* 表单样式 */
.form-section {
  max-width: 800px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #86868b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}

.select-wrapper {
  position: relative;
}

.macos-select {
  width: 100%;
  padding: 12px 44px 12px 16px;
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
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #86868b;
  pointer-events: none;
}

.macos-textarea {
  width: 100%;
  padding: 16px;
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

.macos-textarea::placeholder {
  color: #86868b;
}

.macos-textarea:hover {
  border-color: rgba(0, 0, 0, 0.2);
}

.macos-textarea:focus {
  outline: none;
  border-color: #007aff;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 8px;
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #1d1d1f;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-secondary:hover {
  background: rgba(0, 0, 0, 0.08);
}

.btn-secondary svg {
  width: 16px;
  height: 16px;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
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

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(180deg, #0084ff 0%, #0070e6 100%);
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary svg {
  width: 16px;
  height: 16px;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 结果区域 */
.score-section {
  display: flex;
  gap: 32px;
  margin-bottom: 32px;
  padding: 24px;
  background: linear-gradient(135deg, rgba(0, 122, 255, 0.04) 0%, rgba(88, 86, 214, 0.04) 100%);
  border-radius: 16px;
}

.main-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.score-ring {
  position: relative;
  width: 140px;
  height: 140px;
  margin-bottom: 16px;
}

.score-ring svg {
  transform: rotate(-90deg);
}

.ring-bg {
  stroke: rgba(0, 0, 0, 0.06);
}

.ring-fill {
  stroke-linecap: round;
  transition: stroke-dashoffset 0.8s ease;
}

.score-display {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.score-value {
  font-size: 36px;
  font-weight: 700;
  color: #1d1d1f;
}

.score-unit {
  font-size: 18px;
  color: #86868b;
  margin-left: 2px;
}

.score-info {
  text-align: center;
}

.score-info h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 6px 0;
}

.score-info p {
  font-size: 13px;
  color: #86868b;
  margin: 0;
}

.detail-scores {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 20px;
}

.score-item {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 10px;
}

.score-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
}

.score-header svg {
  width: 16px;
  height: 16px;
  color: #86868b;
}

.score-percent {
  margin-left: auto;
  font-weight: 600;
  color: #1d1d1f;
}

.progress-bar {
  height: 6px;
  background: rgba(0, 0, 0, 0.06);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}

/* 结果卡片 */
.result-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.result-card {
  padding: 20px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.02);
}

.result-card.strengths {
  background: rgba(52, 199, 89, 0.06);
}

.result-card.missing {
  background: rgba(255, 59, 48, 0.06);
}

.result-card.suggestions {
  background: rgba(0, 122, 255, 0.06);
}

.card-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  margin-bottom: 14px;
}

.card-icon svg {
  width: 20px;
  height: 20px;
}

.result-card.strengths .card-icon {
  background: rgba(52, 199, 89, 0.15);
  color: #34c759;
}

.result-card.missing .card-icon {
  background: rgba(255, 59, 48, 0.15);
  color: #ff3b30;
}

.result-card.suggestions .card-icon {
  background: rgba(0, 122, 255, 0.15);
  color: #007aff;
}

.result-card h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 12px 0;
}

.result-card ul {
  margin: 0;
  padding-left: 18px;
  list-style: disc;
}

.result-card ul li {
  font-size: 13px;
  line-height: 1.7;
  color: #424245;
  margin-bottom: 6px;
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-tag {
  padding: 6px 12px;
  background: rgba(255, 59, 48, 0.1);
  border: 1px solid rgba(255, 59, 48, 0.2);
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  color: #ff3b30;
}

/* 过渡动画 */
.slide-fade-enter-active {
  transition: all 0.3s ease;
}

.slide-fade-leave-active {
  transition: all 0.2s ease;
}

.slide-fade-enter-from {
  transform: translateY(20px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

/* 响应式 */
@media (max-width: 900px) {
  .score-section {
    flex-direction: column;
    align-items: center;
  }

  .detail-scores {
    width: 100%;
  }

  .result-cards {
    grid-template-columns: 1fr;
  }
}
</style>

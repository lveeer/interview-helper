<template>
  <div class="resume-finder-game">
    <!-- 游戏开始界面 -->
    <div v-if="gameStatus === 'not-started'" class="game-start-screen">
      <el-card class="welcome-card">
        <template #header>
          <div class="card-header">
            <span>🎮 简历找茬挑战</span>
          </div>
        </template>
        
        <div class="game-description">
          <p>在简历中找出错误，学习简历优化技巧！</p>
          <ul>
            <li>🔍 找到错误：<span class="score-positive">+10分</span></li>
            <li>❌ 点错位置：<span class="score-negative">-5分</span></li>
            <li>💡 使用提示：<span class="score-negative">-3分</span></li>
          </ul>
        </div>

        <div class="difficulty-selection">
          <h3>选择难度</h3>
          <div class="difficulty-options">
            <div
              class="difficulty-card easy"
              :class="{ active: selectedDifficulty === 'easy' }"
              @click="selectDifficulty('easy')"
            >
              <div class="difficulty-icon">🌱</div>
              <div class="difficulty-name">简单</div>
              <div class="difficulty-info">3-5个错误 | 3分钟</div>
            </div>
            <div
              class="difficulty-card medium"
              :class="{ active: selectedDifficulty === 'medium' }"
              @click="selectDifficulty('medium')"
            >
              <div class="difficulty-icon">🌿</div>
              <div class="difficulty-name">中等</div>
              <div class="difficulty-info">5-8个错误 | 5分钟</div>
            </div>
            <div
              class="difficulty-card hard"
              :class="{ active: selectedDifficulty === 'hard' }"
              @click="selectDifficulty('hard')"
            >
              <div class="difficulty-icon">🌳</div>
              <div class="difficulty-name">困难</div>
              <div class="difficulty-info">8-12个错误 | 8分钟</div>
            </div>
          </div>
        </div>

        <el-button
          type="primary"
          size="large"
          class="start-btn"
          @click="startGame"
          :loading="loading"
        >
          开始挑战
        </el-button>
      </el-card>

      <!-- 用户统计 -->
      <el-card class="stats-card">
        <template #header>
          <div class="card-header">
            <span>📊 我的战绩</span>
          </div>
        </template>
        <div v-if="userStats" class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ userStats.total_games }}</div>
            <div class="stat-label">总场次</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ userStats.total_found }}</div>
            <div class="stat-label">找到错误</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ userStats.total_score }}</div>
            <div class="stat-label">总积分</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ (userStats.win_rate * 100).toFixed(0) }}%</div>
            <div class="stat-label">胜率</div>
          </div>
        </div>
        <el-skeleton v-else :rows="4" animated />
      </el-card>
    </div>

    <!-- 游戏进行中界面 -->
    <div v-else-if="gameStatus === 'playing'" class="game-playing-screen">
      <!-- 游戏顶部信息栏 -->
      <div class="game-header">
        <div class="game-info">
          <div class="info-item">
            <el-icon><Timer /></el-icon>
            <span>{{ formatTime(timeRemaining) }}</span>
          </div>
          <div class="info-item">
            <el-icon><Trophy /></el-icon>
            <span>{{ currentScore }}分</span>
          </div>
          <div class="info-item">
            <el-icon><CircleCheck /></el-icon>
            <span>{{ foundErrorsCount }}/{{ totalErrors }}</span>
          </div>
          <div class="info-item">
            <el-icon><InfoFilled /></el-icon>
            <span>{{ remainingHints }}次提示</span>
          </div>
        </div>
        <div class="game-actions">
          <el-button
            type="warning"
            :icon="InfoFilled"
            @click="getHint"
            :disabled="remainingHints <= 0"
          >
            提示 (-3分)
          </el-button>
          <el-button
            type="danger"
            @click="abandonGame"
          >
            放弃
          </el-button>
        </div>
      </div>

      <!-- 提示信息 -->
      <el-alert
        v-if="hintMessage"
        :title="hintMessage"
        type="info"
        :closable="true"
        @close="hintMessage = ''"
        class="hint-alert"
      />

      <!-- 简历展示区域 -->
      <div class="resume-container">
        <el-card class="resume-card">
          <div class="resume-content" @click="handleResumeClick">
            <!-- 个人信息 -->
            <div class="resume-section personal-info">
              <h3 class="section-title">个人信息</h3>
              <div class="info-grid">
                <div class="info-item" data-location="personal_info.name">
                  <label>姓名：</label>
                  <span>{{ resumeData.personal_info?.name }}</span>
                </div>
                <div class="info-item" data-location="personal_info.phone">
                  <label>电话：</label>
                  <span>{{ resumeData.personal_info?.phone }}</span>
                </div>
                <div class="info-item" data-location="personal_info.email">
                  <label>邮箱：</label>
                  <span>{{ resumeData.personal_info?.email }}</span>
                </div>
              </div>
            </div>

            <!-- 教育经历 -->
            <div class="resume-section education">
              <h3 class="section-title">教育经历</h3>
              <div
                v-for="(edu, index) in resumeData.education"
                :key="index"
                class="education-item"
                :data-location="`education[${index}]`"
              >
                <div class="education-header">
                  <span class="school">{{ edu.school }}</span>
                  <span class="time">{{ edu.time }}</span>
                </div>
                <div class="education-info">
                  <span class="major">{{ edu.major }}</span>
                  <span class="degree">{{ edu.degree }}</span>
                </div>
              </div>
            </div>

            <!-- 工作经历 -->
            <div class="resume-section experience">
              <h3 class="section-title">工作经历</h3>
              <div
                v-for="(exp, index) in resumeData.experience"
                :key="index"
                class="experience-item"
                :data-location="`experience[${index}]`"
              >
                <div class="experience-header">
                  <span class="company">{{ exp.company }}</span>
                  <span class="time">{{ exp.time }}</span>
                </div>
                <div class="position">{{ exp.position }}</div>
                <div
                  class="description"
                  :data-location="`experience[${index}].description`"
                >
                  {{ exp.description }}
                </div>
              </div>
            </div>

            <!-- 项目经历 -->
            <div class="resume-section projects" v-if="resumeData.projects">
              <h3 class="section-title">项目经历</h3>
              <div
                v-for="(proj, index) in resumeData.projects"
                :key="index"
                class="project-item"
                :data-location="`projects[${index}]`"
              >
                <div class="project-header">
                  <span class="project-name">{{ proj.name }}</span>
                  <span class="time">{{ proj.time }}</span>
                </div>
                <div class="project-role">{{ proj.role }}</div>
                <div
                  class="project-description"
                  :data-location="`projects[${index}].description`"
                >
                  {{ proj.description }}
                </div>
              </div>
            </div>

            <!-- 技能 -->
            <div class="resume-section skills">
              <h3 class="section-title">专业技能</h3>
              <div class="skills-list" data-location="skills">
                <el-tag
                  v-for="(skill, index) in resumeData.skills"
                  :key="index"
                  :data-location="`skills[${index}]`"
                >
                  {{ skill }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 游戏完成界面 -->
    <div v-else-if="gameStatus === 'completed'" class="game-completed-screen">
      <el-card class="result-card">
        <template #header>
          <div class="card-header">
            <span>🎉 游戏完成</span>
          </div>
        </template>

        <div class="result-content">
          <div class="score-display">
            <div class="score-value">{{ finalScore }}</div>
            <div class="score-label">最终得分</div>
          </div>

          <div class="result-stats">
            <div class="stat-row">
              <span class="stat-label">找到错误：</span>
              <span class="stat-value">{{ foundErrorsList.length }}个</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">遗漏错误：</span>
              <span class="stat-value error">{{ missedErrorsList.length }}个</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">用时：</span>
              <span class="stat-value">{{ formatTime(timeUsed) }}</span>
            </div>
          </div>

          <!-- 解锁的成就 -->
          <div v-if="achievementsUnlocked.length > 0" class="achievements-section">
            <h4>🏆 解锁成就</h4>
            <div class="achievements-list">
              <div
                v-for="achievement in achievementsUnlocked"
                :key="achievement.id"
                class="achievement-item"
              >
                <span class="achievement-icon">{{ achievement.icon }}</span>
                <span class="achievement-name">{{ achievement.name }}</span>
              </div>
            </div>
          </div>

          <!-- 错误详情 -->
          <div class="errors-detail">
            <h4>📋 错误详情</h4>
            <el-collapse>
              <el-collapse-item
                v-for="(error, index) in [...foundErrorsList, ...missedErrorsList]"
                :key="index"
                :title="`错误 ${index + 1}: ${getErrorTypeName(error.type)}`"
              >
                <div class="error-detail">
                  <p><strong>位置：</strong>{{ error.location }}</p>
                  <p><strong>问题：</strong>{{ error.hint }}</p>
                  <p><strong>正确写法：</strong>{{ error.correct_text }}</p>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>

        <div class="result-actions">
          <el-button type="primary" size="large" @click="restartGame">
            再来一局
          </el-button>
          <el-button size="large" @click="viewLeaderboard">
            查看排行榜
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Timer,
  Trophy,
  CircleCheck,
  InfoFilled
} from '@element-plus/icons-vue'
import {
  startGame as startGameAPI,
  submitAnswer as submitAnswerAPI,
  useHint as useHintAPI,
  completeGame as completeGameAPI,
  getUserStats
} from '@/api/game'

const router = useRouter()

// 游戏状态
const gameStatus = ref('not-started') // not-started, playing, completed
const loading = ref(false)
const selectedDifficulty = ref('medium')

// 游戏数据
const sessionId = ref(null)
const resumeData = ref({})
const totalErrors = ref(0)
const currentScore = ref(0)
const foundErrorsCount = ref(0)
const remainingHints = ref(3)
const timeLimit = ref(0)
const timeRemaining = ref(0)
const timeUsed = ref(0)

// 计时器
let timerInterval = null

// 提示信息
const hintMessage = ref('')

// 用户统计
const userStats = ref(null)

// 游戏结果
const finalScore = ref(0)
const foundErrorsList = ref([])
const missedErrorsList = ref([])
const achievementsUnlocked = ref([])

// 错误类型映射
const errorTypeMap = {
  format_inconsistency: '格式不一致',
  spacing_issue: '间距问题',
  font_mismatch: '字体混用',
  vague_description: '描述空洞',
  missing_quantification: '缺少量化成果',
  action_verb_weak: '动词力度弱',
  timeline_conflict: '时间线冲突',
  skill_experience_mismatch: '技能与经历不匹配',
  education_work_gap: '学历与工作年限矛盾',
  negative_language: '负面语言',
  over_claim: '过度夸大',
  discriminatory_terms: '歧视性词汇'
}

// 选择难度
const selectDifficulty = (difficulty) => {
  selectedDifficulty.value = difficulty
}

// 开始游戏
const startGame = async () => {
  loading.value = true
  try {
    const res = await startGameAPI({ difficulty: selectedDifficulty.value })
    if (res.code === 200) {
      sessionId.value = res.data.session_id
      resumeData.value = res.data.resume
      totalErrors.value = res.data.error_count
      timeLimit.value = res.data.time_limit
      timeRemaining.value = res.data.time_limit
      currentScore.value = 0
      foundErrorsCount.value = 0
      remainingHints.value = 3
      hintMessage.value = ''
      
      gameStatus.value = 'playing'
      startTimer()
    }
  } catch (error) {
    ElMessage.error('游戏启动失败')
  } finally {
    loading.value = false
  }
}

// 开始计时
const startTimer = () => {
  timerInterval = setInterval(() => {
    timeRemaining.value--
    if (timeRemaining.value <= 0) {
      clearInterval(timerInterval)
      completeGame()
    }
  }, 1000)
}

// 处理简历点击
const handleResumeClick = async (event) => {
  const target = event.target
  const location = target.dataset.location
  
  if (!location) return
  
  try {
    const res = await submitAnswerAPI({
      session_id: sessionId.value,
      location: location
    })
    
    if (res.code === 200) {
      if (res.data.is_correct) {
        currentScore.value = res.data.score
        foundErrorsCount.value = totalErrors.value - res.data.remaining_errors
        ElMessage.success({
          message: `找到错误！+10分`,
          duration: 2000
        })
        
        // 高亮显示错误位置
        target.classList.add('error-highlight')
        
        // 检查是否找到所有错误
        if (res.data.remaining_errors === 0) {
          setTimeout(() => {
            completeGame()
          }, 1500)
        }
      } else {
        currentScore.value = res.data.score
        ElMessage.error({
          message: '这里没有错误，-5分',
          duration: 2000
        })
      }
    }
  } catch (error) {
    console.error('提交答案失败:', error)
  }
}

// 获取提示
const getHint = async () => {
  try {
    const res = await useHintAPI({ session_id: sessionId.value })
    if (res.code === 200) {
      hintMessage.value = res.data.hint
      remainingHints.value = res.data.remaining_hints
      currentScore.value = res.data.score
    }
  } catch (error) {
    ElMessage.error('获取提示失败')
  }
}

// 放弃游戏
const abandonGame = async () => {
  try {
    await ElMessageBox.confirm('确定要放弃当前游戏吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    clearInterval(timerInterval)
    await completeGameAPI({ session_id: sessionId.value })
    gameStatus.value = 'not-started'
  } catch (error) {
    // 用户取消
  }
}

// 完成游戏
const completeGame = async () => {
  clearInterval(timerInterval)
  
  try {
    const res = await completeGameAPI({ session_id: sessionId.value })
    if (res.code === 200) {
      finalScore.value = res.data.final_score
      foundErrorsList.value = res.data.found_errors || []
      missedErrorsList.value = res.data.missed_errors || []
      timeUsed.value = res.data.time_used
      achievementsUnlocked.value = res.data.achievements_unlocked || []
      
      gameStatus.value = 'completed'
    }
  } catch (error) {
    ElMessage.error('游戏结算失败')
    gameStatus.value = 'not-started'
  }
}

// 重新开始
const restartGame = () => {
  gameStatus.value = 'not-started'
  selectedDifficulty.value = 'medium'
}

// 查看排行榜
const viewLeaderboard = () => {
  ElMessage.info('排行榜功能开发中...')
}

// 格式化时间
const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 获取错误类型名称
const getErrorTypeName = (type) => {
  return errorTypeMap[type] || type
}

// 加载用户统计
const loadUserStats = async () => {
  try {
    const res = await getUserStats()
    if (res.code === 200) {
      userStats.value = res.data
    }
  } catch (error) {
    console.error('加载用户统计失败:', error)
  }
}

onMounted(() => {
  loadUserStats()
})

onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
})
</script>

<style scoped>
.resume-finder-game {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 游戏开始界面 */
.game-start-screen {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.welcome-card {
  animation: fadeIn 0.5s ease-out;
}

.card-header {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.game-description {
  margin: 20px 0;
  padding: 16px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 8px;
}

.game-description p {
  font-size: 16px;
  color: #303133;
  margin-bottom: 12px;
  font-weight: 500;
}

.game-description ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.game-description li {
  padding: 8px 0;
  font-size: 14px;
  color: #606266;
}

.score-positive {
  color: #67c23a;
  font-weight: 600;
}

.score-negative {
  color: #f56c6c;
  font-weight: 600;
}

.difficulty-selection {
  margin: 24px 0;
}

.difficulty-selection h3 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 16px;
}

.difficulty-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.difficulty-card {
  padding: 20px;
  text-align: center;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
  background: #f5f7fa;
}

.difficulty-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.difficulty-card.active {
  border-color: #409EFF;
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
}

.difficulty-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.difficulty-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.difficulty-info {
  font-size: 12px;
  color: #909399;
}

.difficulty-card.easy .difficulty-icon { filter: hue-rotate(120deg); }
.difficulty-card.medium .difficulty-icon { filter: hue-rotate(60deg); }
.difficulty-card.hard .difficulty-icon { filter: hue-rotate(0deg); }

.start-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
  border: none;
  transition: all 0.3s;
}

.start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

/* 用户统计卡片 */
.stats-card {
  animation: fadeIn 0.5s ease-out 0.2s backwards;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #fafafa 100%);
  border-radius: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #409EFF;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 游戏进行中界面 */
.game-playing-screen {
  animation: fadeIn 0.5s ease-out;
}

.game-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
  border-radius: 12px;
  margin-bottom: 20px;
  color: #fff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.game-info {
  display: flex;
  align-items: center;
  gap: 24px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 16px;
  font-weight: 500;
}

.info-item .el-icon {
  font-size: 20px;
}

.game-actions {
  display: flex;
  gap: 12px;
}

.hint-alert {
  margin-bottom: 20px;
}

/* 简历展示区域 */
.resume-container {
  margin-bottom: 20px;
}

.resume-card {
  min-height: 600px;
}

.resume-content {
  padding: 20px;
}

.resume-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #409EFF;
}

/* 个人信息 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.info-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.info-item:hover {
  background: #ecf5ff;
  transform: scale(1.02);
}

.info-item label {
  font-weight: 500;
  color: #606266;
  margin-right: 8px;
}

/* 教育经历 */
.education-item {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.education-item:hover {
  background: #ecf5ff;
  transform: translateX(4px);
}

.education-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.school {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.time {
  font-size: 14px;
  color: #909399;
}

.education-info {
  display: flex;
  gap: 16px;
}

.major {
  font-size: 14px;
  color: #606266;
}

.degree {
  font-size: 14px;
  color: #909399;
}

/* 工作经历 */
.experience-item {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.experience-item:hover {
  background: #ecf5ff;
  transform: translateX(4px);
}

.experience-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.company {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.position {
  font-size: 14px;
  color: #409EFF;
  margin-bottom: 8px;
}

.description {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  padding: 8px;
  background: #fafafa;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.description:hover {
  background: #ecf5ff;
}

/* 项目经历 */
.project-item {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.project-item:hover {
  background: #ecf5ff;
  transform: translateX(4px);
}

.project-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.project-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.project-role {
  font-size: 14px;
  color: #409EFF;
  margin-bottom: 8px;
}

.project-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  padding: 8px;
  background: #fafafa;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.project-description:hover {
  background: #ecf5ff;
}

/* 技能 */
.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.skills-list:hover {
  background: #ecf5ff;
}

.skills-list .el-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.skills-list .el-tag:hover {
  transform: scale(1.05);
}

/* 错误高亮 */
.error-highlight {
  animation: errorPulse 0.5s ease-out;
  background: linear-gradient(135deg, #ffeb3b 0%, #ffc107 100%) !important;
  border: 2px solid #ff9800 !important;
  border-radius: 4px;
}

@keyframes errorPulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

/* 游戏完成界面 */
.game-completed-screen {
  animation: fadeIn 0.5s ease-out;
}

.result-card {
  max-width: 800px;
  margin: 0 auto;
}

.result-content {
  text-align: center;
}

.score-display {
  margin: 32px 0;
}

.score-value {
  font-size: 72px;
  font-weight: 700;
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.score-label {
  font-size: 18px;
  color: #909399;
  margin-top: 8px;
}

.result-stats {
  margin: 24px 0;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  font-size: 16px;
}

.stat-label {
  color: #606266;
}

.stat-value {
  font-weight: 600;
  color: #303133;
}

.stat-value.error {
  color: #f56c6c;
}

/* 成就区域 */
.achievements-section {
  margin: 24px 0;
  padding: 20px;
  background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%);
  border-radius: 8px;
}

.achievements-section h4 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 16px;
}

.achievements-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.achievement-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.achievement-icon {
  font-size: 24px;
}

.achievement-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

/* 错误详情 */
.errors-detail {
  margin: 24px 0;
  text-align: left;
}

.errors-detail h4 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 16px;
}

.error-detail {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.error-detail p {
  margin: 8px 0;
  font-size: 14px;
  color: #606266;
}

.error-detail strong {
  color: #303133;
}

/* 结果操作按钮 */
.result-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 32px;
}

.result-actions .el-button {
  min-width: 160px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
}

/* 动画 */
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

/* 响应式设计 */
@media (max-width: 768px) {
  .game-start-screen {
    grid-template-columns: 1fr;
  }

  .difficulty-options {
    grid-template-columns: 1fr;
  }

  .game-header {
    flex-direction: column;
    gap: 16px;
  }

  .game-info {
    flex-wrap: wrap;
    gap: 12px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .result-stats {
    padding: 16px;
  }

  .stat-row {
    flex-direction: column;
    gap: 4px;
    text-align: center;
  }

  .result-actions {
    flex-direction: column;
  }

  .result-actions .el-button {
    width: 100%;
  }
}
</style>
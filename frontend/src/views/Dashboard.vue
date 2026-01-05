<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #409EFF;">
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
            <div class="stat-icon" style="background-color: #67C23A;">
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
            <div class="stat-icon" style="background-color: #E6A23C;">
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
            <div class="stat-icon" style="background-color: #F56C6C;">
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

    <el-row :gutter="20" style="margin-top: 20px;">
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
          <el-empty description="暂无面试记录" />
        </el-card>
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

const loadData = async () => {
  try {
    const res = await getDashboardStatistics()

    if (res.code === 200) {
      resumeCount.value = res.data.resume_count || 0
      interviewCount.value = res.data.interview_count || 0
      knowledgeCount.value = res.data.knowledge_count || 0
      avgScore.value = res.data.avg_score || 0
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const goToResume = () => router.push('/resume')
const goToInterview = () => router.push('/interview')
const goToJobMatch = () => router.push('/job-match')
const goToKnowledge = () => router.push('/knowledge')

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.card-header {
  font-weight: bold;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.quick-actions .el-button {
  flex: 1;
  min-width: 120px;
}
</style>
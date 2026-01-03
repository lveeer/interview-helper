<template>
  <div class="report">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>面试评估报告</span>
          <el-button @click="goBack">
            <el-icon><Back /></el-icon>
            返回
          </el-button>
        </div>
      </template>

      <div v-if="reportData">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="score-card">
              <div class="score-title">总体评分</div>
              <div class="score-value">{{ reportData.total_score }}</div>
              <el-progress
                :percentage="reportData.total_score"
                :color="getScoreColor(reportData.total_score)"
                :stroke-width="20"
              />
            </div>
          </el-col>

          <el-col :span="12">
            <div class="feedback-card">
              <div class="feedback-title">总体评价</div>
              <div class="feedback-content">{{ reportData.overall_feedback }}</div>
            </div>
          </el-col>
        </el-row>

        <el-divider />

        <div class="section-title">
          <el-icon><Document /></el-icon>
          问题评估详情
        </div>

        <el-timeline>
          <el-timeline-item
            v-for="(evaluation, index) in reportData.question_evaluations"
            :key="index"
            :timestamp="`问题 ${index + 1}`"
            placement="top"
          >
            <el-card>
              <div class="question-text">{{ evaluation.question }}</div>
              <div class="question-score">
                <span>得分：</span>
                <el-tag :type="getScoreTagType(evaluation.score)">
                  {{ evaluation.score }}
                </el-tag>
              </div>
              <div class="evaluation-content">
                <div class="evaluation-item">
                  <strong>评价：</strong>{{ evaluation.feedback }}
                </div>
                <div class="evaluation-item">
                  <strong>优点：</strong>
                  <el-tag
                    v-for="strength in evaluation.strengths"
                    :key="strength"
                    type="success"
                    size="small"
                    style="margin-right: 5px; margin-bottom: 5px;"
                  >
                    {{ strength }}
                  </el-tag>
                </div>
                <div class="evaluation-item">
                  <strong>改进建议：</strong>
                  <el-tag
                    v-for="improvement in evaluation.improvements"
                    :key="improvement"
                    type="warning"
                    size="small"
                    style="margin-right: 5px; margin-bottom: 5px;"
                  >
                    {{ improvement }}
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>

        <el-divider />

        <div class="section-title">
          <el-icon><Reading /></el-icon>
          推荐学习资源
        </div>

        <el-row :gutter="20">
          <el-col
            v-for="(resource, index) in reportData.recommended_resources"
            :key="index"
            :span="8"
          >
            <el-card class="resource-card">
              <div class="resource-type">
                <el-tag>{{ resource.type }}</el-tag>
              </div>
              <div class="resource-title">{{ resource.title }}</div>
              <el-button
                v-if="resource.url"
                type="primary"
                size="small"
                style="margin-top: 10px;"
                @click="openResource(resource.url)"
              >
                查看资源
              </el-button>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <el-empty v-else description="暂无报告数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getInterviewReport } from '@/api/evaluation'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const reportData = ref(null)

const loadReport = async () => {
  loading.value = true
  try {
    const res = await getInterviewReport(route.params.id)
    if (res.code === 200) {
      reportData.value = res.data
    }
  } catch (error) {
    console.error('加载报告失败:', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/interview')
}

const openResource = (url) => {
  window.open(url, '_blank')
}

const getScoreColor = (score) => {
  if (score >= 80) return '#67C23A'
  if (score >= 60) return '#E6A23C'
  return '#F56C6C'
}

const getScoreTagType = (score) => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-card {
  text-align: center;
  padding: 20px;
}

.score-title {
  font-size: 16px;
  color: #666;
  margin-bottom: 10px;
}

.score-value {
  font-size: 48px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 20px;
}

.feedback-card {
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.feedback-title {
  font-size: 16px;
  color: #666;
  margin-bottom: 10px;
}

.feedback-content {
  font-size: 14px;
  line-height: 1.6;
  color: #333;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
}

.question-text {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
}

.question-score {
  margin-bottom: 15px;
  font-size: 14px;
}

.evaluation-content {
  margin-top: 15px;
}

.evaluation-item {
  margin-bottom: 10px;
  font-size: 14px;
}

.resource-card {
  text-align: center;
  height: 100%;
}

.resource-type {
  margin-bottom: 10px;
}

.resource-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 10px;
  min-height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
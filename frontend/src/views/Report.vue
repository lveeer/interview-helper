<template>
  <div class="report">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>面试评估报告</span>
          <div class="header-actions">
            <el-button
              type="primary"
              :loading="exportLoading"
              @click="exportToPDF"
            >
              <el-icon><Download /></el-icon>
              导出 PDF
            </el-button>
            <el-button @click="goBack">
              <el-icon><Back /></el-icon>
              返回
            </el-button>
          </div>
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
                <span class="score-text" :class="getScoreClass(evaluation.score)">
                  {{ evaluation.score }}
                </span>
              </div>
              <div class="evaluation-content">
                <div class="evaluation-item">
                  <strong>评价：</strong>{{ evaluation.feedback }}
                </div>
                <div class="evaluation-item">
                  <strong>优点：</strong>
                  <span
                    v-for="(strength, idx) in evaluation.strengths"
                    :key="idx"
                    class="tag-text tag-success"
                  >
                    {{ strength }}
                  </span>
                </div>
                <div class="evaluation-item">
                  <strong>改进建议：</strong>
                  <span
                    v-for="(improvement, idx) in evaluation.improvements"
                    :key="idx"
                    class="tag-text tag-warning"
                  >
                    {{ improvement }}
                  </span>
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
                <span class="tag-text tag-info">{{ resource.type }}</span>
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
import { ElMessage } from 'element-plus'
import html2pdf from 'html2pdf.js'
import { getInterviewReport } from '@/api/evaluation'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const exportLoading = ref(false)
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

const getScoreClass = (score) => {
  if (score >= 80) return 'score-high'
  if (score >= 60) return 'score-medium'
  return 'score-low'
}

const exportToPDF = async () => {
  if (!reportData.value) {
    ElMessage.warning('暂无报告数据，无法导出')
    return
  }

  try {
    exportLoading.value = true

    const element = document.querySelector('.report .el-card__body')
    if (!element) {
      ElMessage.error('未找到报告内容')
      return
    }

    const options = {
      margin: [10, 10, 10, 10],
      filename: `面试评估报告_${new Date().getTime()}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: {
        scale: 2,
        useCORS: true,
        logging: false,
        letterRendering: true,
        allowTaint: true,
        foreignObjectRendering: false,
        backgroundColor: '#ffffff',
        onclone: (clonedDoc) => {
          const clonedElement = clonedDoc.querySelector('.report .el-card__body')
          if (clonedElement) {
            clonedElement.style.width = '100%'
            clonedElement.style.minHeight = '100vh'
          }
        }
      },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
      pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
    }

    await html2pdf().set(options).from(element).save()
    ElMessage.success('PDF 导出成功')
  } catch (error) {
    console.error('PDF 导出失败:', error)
    ElMessage.error(`PDF 导出失败: ${error.message || '未知错误'}`)
  } finally {
    exportLoading.value = false
  }
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

.header-actions {
  display: flex;
  gap: 10px;
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

.score-text {
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 4px;
}

.score-text.score-high {
  color: #67C23A;
  background-color: #f0f9ff;
}

.score-text.score-medium {
  color: #E6A23C;
  background-color: #fdf6ec;
}

.score-text.score-low {
  color: #F56C6C;
  background-color: #fef0f0;
}

.tag-text {
  display: inline-block;
  padding: 2px 8px;
  margin-right: 5px;
  margin-bottom: 5px;
  border-radius: 4px;
  font-size: 12px;
}

.tag-success {
  color: #67C23A;
  background-color: #f0f9ff;
  border: 1px solid #e1f3d8;
}

.tag-warning {
  color: #E6A23C;
  background-color: #fdf6ec;
  border: 1px solid #faecd8;
}

.tag-info {
  color: #409EFF;
  background-color: #ecf5ff;
  border: 1px solid #d9ecff;
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

<style>
@media print {
  .el-tag {
    display: inline-block !important;
    visibility: visible !important;
  }

  .el-progress {
    visibility: visible !important;
  }

  .el-timeline-item__wrapper {
    visibility: visible !important;
  }
}
</style>
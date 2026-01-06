<template>
  <div class="interview-record">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
          <span>面试对话记录</span>
        </div>
      </template>

      <div v-loading="loading">
        <div v-if="recordData" class="record-content">
          <!-- 面试基本信息 -->
          <div class="interview-info">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="面试ID">{{ recordData.id }}</el-descriptions-item>
              <el-descriptions-item label="总分">
                <el-tag type="success" size="large">{{ recordData.total_score }}分</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getStatusType(recordData.status)">
                  {{ getStatusText(recordData.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="创建时间">
                {{ formatDate(recordData.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="岗位描述" :span="2">
                {{ recordData.job_description }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 问题列表 -->
          <div class="questions-section" v-if="recordData.questions && recordData.questions.length">
            <h3>问题列表</h3>
            <el-table :data="recordData.questions" size="small" border>
              <el-table-column prop="id" label="编号" width="100" />
              <el-table-column prop="question" label="问题内容" min-width="300" show-overflow-tooltip />
              <el-table-column prop="category" label="分类" width="120" />
              <el-table-column prop="difficulty" label="难度" width="100">
                <template #default="{ row }">
                  <el-tag :type="getDifficultyType(row.difficulty)" size="small">
                    {{ row.difficulty }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 对话记录 -->
          <div class="conversation-section">
            <h3>对话记录</h3>
            <div class="conversation-list">
              <div
                v-for="(item, index) in recordData.conversation"
                :key="index"
                :class="['conversation-item', item.role]"
              >
                <div class="message-wrapper">
                  <div class="message-header">
                    <div class="role-info">
                      <el-tag :type="item.role === 'interviewer' ? 'primary' : 'success'" size="small">
                        <el-icon v-if="item.role === 'interviewer'"><User /></el-icon>
                        <el-icon v-else><ChatDotRound /></el-icon>
                        {{ item.role === 'interviewer' ? '面试官' : '候选人' }}
                      </el-tag>
                      <el-tag v-if="item.type === 'followup'" type="warning" size="small" class="ml-2">
                        追问
                      </el-tag>
                      <template v-if="item.role === 'interviewer'">
                        <el-tag v-if="item.category" type="info" size="small" class="ml-2">
                          {{ item.category }}
                        </el-tag>
                        <el-tag v-if="item.difficulty" type="warning" size="small" class="ml-2">
                          {{ item.difficulty }}
                        </el-tag>
                      </template>
                    </div>
                    <span class="timestamp">{{ formatTime(item.timestamp) }}</span>
                  </div>
                  <div class="message-content">{{ item.content }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <el-empty v-else-if="!loading" description="暂无对话记录" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, User, ChatDotRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getInterviewRecord } from '@/api/interview'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const recordData = ref(null)

const loadRecord = async () => {
  const interviewId = route.params.id
  if (!interviewId) {
    ElMessage.error('面试ID不存在')
    goBack()
    return
  }

  loading.value = true
  try {
    const res = await getInterviewRecord(interviewId)
    if (res.code === 200) {
      recordData.value = res.data
    } else {
      ElMessage.error(res.message || '获取对话记录失败')
    }
  } catch (error) {
    console.error('加载对话记录失败:', error)
    ElMessage.error('加载对话记录失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/interview')
}

const getStatusText = (status) => {
  const statusMap = {
    pending: '待开始',
    in_progress: '进行中',
    analyzing: '分析中',
    completed: '已完成'
  }
  return statusMap[status] || status
}

const getStatusType = (status) => {
  const typeMap = {
    pending: 'info',
    in_progress: 'warning',
    analyzing: 'info',
    completed: 'success'
  }
  return typeMap[status] || ''
}

const getDifficultyType = (difficulty) => {
  const typeMap = {
    简单: 'success',
    中等: 'warning',
    困难: 'danger'
  }
  return typeMap[difficulty] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const formatTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleTimeString('zh-CN')
}

onMounted(() => {
  loadRecord()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.record-content {
  padding: 20px 0;
}

.interview-info {
  margin-bottom: 30px;
}

.questions-section {
  margin-bottom: 30px;
}

.questions-section h3 {
  margin-bottom: 15px;
  font-size: 18px;
  font-weight: 600;
}

.conversation-section h3 {
  margin-bottom: 15px;
  font-size: 18px;
  font-weight: 600;
}

.conversation-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.conversation-item {
  display: flex;
  flex-direction: column;
  max-width: 85%;
  transition: all 0.3s ease;
}

.conversation-item.interviewer {
  align-self: flex-start;
  margin-right: auto;
}

.conversation-item.candidate {
  align-self: flex-end;
  margin-left: auto;
}

.conversation-item .message-wrapper {
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.conversation-item:hover .message-wrapper {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.conversation-item.interviewer .message-wrapper {
  background: linear-gradient(135deg, #e8f4ff 0%, #f0f9ff 100%);
  border-left: 4px solid #409eff;
  border-top-left-radius: 2px;
}

.conversation-item.candidate .message-wrapper {
  background: linear-gradient(135deg, #f0fff4 0%, #f7fff7 100%);
  border-right: 4px solid #67c23a;
  border-top-right-radius: 2px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.conversation-item.candidate .message-header {
  flex-direction: row-reverse;
}

.role-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.timestamp {
  color: #909399;
  font-size: 12px;
  white-space: nowrap;
}

.message-content {
  padding: 8px 0;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 14px;
  color: #303133;
}

.question-id {
  margin-top: 10px;
  padding-top: 8px;
  font-size: 12px;
  color: #909399;
  border-top: 1px dashed rgba(0, 0, 0, 0.06);
}

.ml-2 {
  margin-left: 8px;
}
</style>
<template>
  <div class="job-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>岗位列表</span>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            添加岗位
          </el-button>
        </div>
      </template>

      <el-table :data="jobList" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="岗位名称" min-width="180" />
        <el-table-column prop="company" label="公司" width="150">
          <template #default="{ row }">
            {{ row.company || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="岗位描述" min-width="200">
          <template #default="{ row }">
            {{ truncateText(row.job_description, 100) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button type="success" size="small" @click="startInterview(row)">
              开始面试
            </el-button>
            <el-button type="primary" size="small" @click="viewHistory(row)">
              历史记录
            </el-button>
            <el-button type="info" size="small" @click="editJob(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑岗位对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingJob ? '编辑岗位' : '添加岗位'"
      width="600px"
    >
      <el-form :model="jobForm" label-width="80px">
        <el-form-item label="岗位名称" required>
          <el-input
            v-model="jobForm.title"
            placeholder="请输入岗位名称，如：前端开发工程师"
          />
        </el-form-item>
        <el-form-item label="公司名称">
          <el-input
            v-model="jobForm.company"
            placeholder="请输入公司名称（可选）"
          />
        </el-form-item>
        <el-form-item label="岗位描述" required>
          <el-input
            v-model="jobForm.job_description"
            type="textarea"
            :rows="6"
            placeholder="请输入岗位描述（JD），包括岗位职责、任职要求等"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ editingJob ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 开始面试对话框 -->
    <el-dialog
      v-model="showInterviewDialog"
      title="开始面试"
      width="600px"
    >
      <div class="interview-job-info">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="岗位名称">{{ selectedJob?.title }}</el-descriptions-item>
          <el-descriptions-item label="公司">{{ selectedJob?.company || '-' }}</el-descriptions-item>
          <el-descriptions-item label="岗位描述">
            <div class="jd-preview">{{ truncateText(selectedJob?.job_description, 200) }}</div>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <el-form :model="interviewForm" label-width="100px" class="interview-form">
        <el-form-item label="选择简历" required>
          <el-select
            v-model="interviewForm.resume_id"
            placeholder="请选择简历"
            style="width: 100%"
          >
            <el-option
              v-for="resume in resumeList"
              :key="resume.id"
              :label="resume.file_name"
              :value="resume.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="知识库文档">
          <el-select
            v-model="interviewForm.knowledge_doc_ids"
            placeholder="请选择知识库文档（可选）"
            style="width: 100%"
            multiple
            collapse-tags
            collapse-tags-tooltip
          >
            <el-option
              v-for="doc in knowledgeList"
              :key="doc.id"
              :label="doc.file_name"
              :value="doc.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="面试官人设">
          <el-select
            v-model="interviewForm.persona_id"
            placeholder="选择面试官风格（可选）"
            style="width: 100%"
          >
            <el-option
              v-for="persona in personaList"
              :key="persona.id"
              :label="persona.name"
              :value="persona.id"
            >
              <div class="persona-option">
                <span class="persona-name">{{ persona.name }}</span>
                <span class="persona-desc">{{ persona.description }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showInterviewDialog = false">取消</el-button>
        <el-button type="primary" :loading="creatingInterview" @click="handleCreateInterview">
          创建面试
        </el-button>
      </template>
    </el-dialog>

    <!-- 模式选择对话框 -->
    <el-dialog
      v-model="showModeDialog"
      title="选择面试模式"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="mode-options">
        <div
          class="mode-option"
          :class="{ active: selectedMode === 'normal' }"
          @click="selectedMode = 'normal'"
        >
          <el-icon class="mode-icon"><ChatLineSquare /></el-icon>
          <div class="mode-info">
            <h3>常规模式</h3>
            <p>文字对话形式进行面试，适合日常练习</p>
          </div>
        </div>
        <div
          class="mode-option"
          :class="{ active: selectedMode === 'video' }"
          @click="selectedMode = 'video'"
        >
          <el-icon class="mode-icon"><VideoCamera /></el-icon>
          <div class="mode-info">
            <h3>视频模式</h3>
            <p>开启摄像头和麦克风，模拟真实面试场景</p>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button size="large" @click="showModeDialog = false">取消</el-button>
        <el-button type="primary" size="large" @click="confirmStartInterview" :disabled="!selectedMode">
          开始面试
        </el-button>
      </template>
    </el-dialog>

    <!-- 历史面试记录对话框 -->
    <el-dialog
      v-model="showHistoryDialog"
      :title="`${selectedJob?.title || ''} - 历史面试记录`"
      width="800px"
    >
      <el-table :data="historyInterviews" v-loading="loadingHistory">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="简历" width="150">
          <template #default="{ row }">
            {{ getResumeName(row.resume_id) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="分数" width="80" />
        <el-table-column prop="created_at" label="面试时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              type="primary"
              size="small"
              @click="continueInterview(row)"
            >
              开始面试
            </el-button>
            <el-button
              v-if="row.status === 'in_progress'"
              type="warning"
              size="small"
              @click="continueInterview(row)"
            >
              继续面试
            </el-button>
            <el-button
              v-if="row.status === 'completed'"
              type="success"
              size="small"
              @click="viewReport(row)"
            >
              查看报告
            </el-button>
            <el-button
              v-if="row.status === 'completed'"
              type="info"
              size="small"
              @click="viewRecord(row)"
            >
              查看对话
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ChatLineSquare, VideoCamera } from '@element-plus/icons-vue'
import {
  getJobList,
  createJob,
  updateJob,
  deleteJob,
  createJobInterview,
  getJobInterviews
} from '@/api/job'
import { getResumeList } from '@/api/resume'
import { getKnowledgeList } from '@/api/knowledge'
import { getPersonas } from '@/api/persona'

const router = useRouter()

// 列表数据
const loading = ref(false)
const jobList = ref([])
const resumeList = ref([])
const knowledgeList = ref([])
const personaList = ref([])

// 创建/编辑岗位
const showCreateDialog = ref(false)
const editingJob = ref(null)
const submitting = ref(false)
const jobForm = ref({
  title: '',
  company: '',
  job_description: ''
})

// 开始面试
const showInterviewDialog = ref(false)
const selectedJob = ref(null)
const creatingInterview = ref(false)
const interviewForm = ref({
  resume_id: '',
  knowledge_doc_ids: [],
  persona_id: null
})

// 模式选择
const showModeDialog = ref(false)
const selectedMode = ref('normal')
const pendingInterview = ref(null)

// 历史记录
const showHistoryDialog = ref(false)
const loadingHistory = ref(false)
const historyInterviews = ref([])

// 加载岗位列表
const loadJobList = async () => {
  loading.value = true
  try {
    const res = await getJobList()
    if (res.code === 200) {
      jobList.value = res.data || []
    }
  } catch (error) {
    console.error('加载岗位列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载简历列表
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

// 加载知识库列表
const loadKnowledgeList = async () => {
  try {
    const res = await getKnowledgeList()
    if (res.code === 200) {
      knowledgeList.value = res.data || []
    }
  } catch (error) {
    console.error('加载知识库列表失败:', error)
  }
}

// 加载人设列表
const loadPersonaList = async () => {
  try {
    const res = await getPersonas()
    if (res.code === 200) {
      personaList.value = res.data || []
    }
  } catch (error) {
    console.error('加载人设列表失败:', error)
  }
}

// 创建/更新岗位
const handleSubmit = async () => {
  if (!jobForm.value.title.trim()) {
    ElMessage.warning('请输入岗位名称')
    return
  }
  if (!jobForm.value.job_description.trim()) {
    ElMessage.warning('请输入岗位描述')
    return
  }

  submitting.value = true
  try {
    let res
    if (editingJob.value) {
      res = await updateJob(editingJob.value.id, jobForm.value)
    } else {
      res = await createJob(jobForm.value)
    }

    if (res.code === 201 || res.code === 200) {
      ElMessage.success(editingJob.value ? '更新成功' : '创建成功')
      showCreateDialog.value = false
      resetJobForm()
      loadJobList()
    }
  } catch (error) {
    console.error('操作失败:', error)
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetJobForm = () => {
  editingJob.value = null
  jobForm.value = {
    title: '',
    company: '',
    job_description: ''
  }
}

// 编辑岗位
const editJob = (job) => {
  editingJob.value = job
  jobForm.value = {
    title: job.title,
    company: job.company || '',
    job_description: job.job_description
  }
  showCreateDialog.value = true
}

// 删除岗位
const handleDelete = async (job) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除岗位「${job.title}」吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const res = await deleteJob(job.id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      loadJobList()
    }
  } catch {
    // 用户取消
  }
}

// 开始面试
const startInterview = (job) => {
  selectedJob.value = job
  interviewForm.value = {
    resume_id: '',
    knowledge_doc_ids: [],
    persona_id: null
  }
  showInterviewDialog.value = true
}

// 创建面试
const handleCreateInterview = async () => {
  if (!interviewForm.value.resume_id) {
    ElMessage.warning('请选择简历')
    return
  }

  creatingInterview.value = true
  try {
    const res = await createJobInterview(selectedJob.value.id, interviewForm.value)
    if (res.code === 201) {
      ElMessage.success('面试创建成功')
      showInterviewDialog.value = false
      pendingInterview.value = res.data
      selectedMode.value = 'normal'
      showModeDialog.value = true
    }
  } catch (error) {
    console.error('创建面试失败:', error)
  } finally {
    creatingInterview.value = false
  }
}

// 确认开始面试
const confirmStartInterview = async () => {
  if (!selectedMode.value || !pendingInterview.value) return

  showModeDialog.value = false

  if (selectedMode.value === 'video') {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      })
      stream.getTracks().forEach(track => track.stop())
    } catch (error) {
      console.warn('获取媒体设备权限失败:', error)
      ElMessage.warning('未检测到摄像头或麦克风，视频面试将以黑屏模式进行')
    }
    router.push(`/video-interview/${pendingInterview.value.id}`)
  } else {
    router.push(`/interview/${pendingInterview.value.id}`)
  }
}

// 查看历史记录
const viewHistory = async (job) => {
  selectedJob.value = job
  loadingHistory.value = true
  showHistoryDialog.value = true

  try {
    const res = await getJobInterviews(job.id)
    if (res.code === 200) {
      historyInterviews.value = res.data || []
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
  } finally {
    loadingHistory.value = false
  }
}

// 获取简历名称
const getResumeName = (resumeId) => {
  const resume = resumeList.value.find(r => r.id === resumeId)
  return resume?.file_name || `简历 #${resumeId}`
}

// 继续面试
const continueInterview = (interview) => {
  showHistoryDialog.value = false
  router.push(`/interview/${interview.id}`)
}

// 查看报告
const viewReport = (interview) => {
  showHistoryDialog.value = false
  router.push(`/report/${interview.id}`)
}

// 查看对话
const viewRecord = (interview) => {
  showHistoryDialog.value = false
  router.push(`/interview-record/${interview.id}`)
}

// 状态相关
const getStatusText = (status) => {
  const statusMap = {
    pending: '待开始',
    initializing: '生成问题中',
    in_progress: '进行中',
    analyzing: '分析中',
    completed: '已完成'
  }
  return statusMap[status] || status
}

const getStatusType = (status) => {
  const typeMap = {
    pending: 'info',
    initializing: 'info',
    in_progress: 'warning',
    analyzing: 'info',
    completed: 'success'
  }
  return typeMap[status] || ''
}

// 格式化
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const truncateText = (text, maxLength) => {
  if (!text) return '-'
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

onMounted(() => {
  loadJobList()
  loadResumeList()
  loadKnowledgeList()
  loadPersonaList()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.interview-job-info {
  margin-bottom: 20px;
}

.jd-preview {
  max-height: 100px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.interview-form {
  margin-top: 20px;
}

.persona-option {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.persona-name {
  font-weight: 500;
  color: var(--text-primary);
}

.persona-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

.mode-options {
  display: flex;
  gap: 20px;
  padding: 10px 0;
}

.mode-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mode-option:hover {
  border-color: var(--primary-color);
  background-color: var(--hover-bg);
}

.mode-option.active {
  border-color: var(--primary-color);
  background-color: var(--primary-light);
}

.mode-icon {
  font-size: 48px;
  color: var(--primary-color);
  margin-bottom: 16px;
}

.mode-option.active .mode-icon {
  color: var(--primary-color);
}

.mode-info {
  text-align: center;
}

.mode-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: var(--text-primary);
}

.mode-info p {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}
</style>

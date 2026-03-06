<template>
  <div class="job-list-page">
    <!-- 岗位列表窗口 -->
    <div class="macos-window">
      <div class="window-titlebar">
        <div class="window-title">
          <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
            <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
          </svg>
          <span>岗位列表</span>
        </div>
        <div class="window-actions">
          <button class="action-btn primary" @click="showCreateDialog = true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            <span>添加岗位</span>
          </button>
        </div>
      </div>

      <div class="window-content">
        <div class="table-container" v-loading="loading">
          <table class="macos-table">
            <thead>
              <tr>
                <th class="col-id">ID</th>
                <th class="col-title">岗位名称</th>
                <th class="col-company">公司</th>
                <th class="col-desc">岗位描述</th>
                <th class="col-date">创建时间</th>
                <th class="col-actions">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="job in jobList" :key="job.id" class="table-row">
                <td class="col-id">
                  <span class="id-badge">{{ job.id }}</span>
                </td>
                <td class="col-title">
                  <span class="job-title">{{ job.title }}</span>
                </td>
                <td class="col-company">
                  <span class="company-name">{{ job.company || '-' }}</span>
                </td>
                <td class="col-desc">
                  <span class="desc-preview">{{ truncateText(job.job_description, 80) }}</span>
                </td>
                <td class="col-date">
                  <span class="date-text">{{ formatDate(job.created_at) }}</span>
                </td>
                <td class="col-actions">
                  <div class="action-group">
                    <button class="table-btn success" @click="startInterview(job)" title="开始面试">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                      </svg>
                    </button>
                    <button class="table-btn info" @click="viewHistory(job)" title="历史记录">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                      </svg>
                    </button>
                    <button class="table-btn warning" @click="editJob(job)" title="编辑">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                      </svg>
                    </button>
                    <button class="table-btn danger" @click="handleDelete(job)" title="删除">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="jobList.length === 0 && !loading">
                <td colspan="6" class="empty-cell">
                  <div class="empty-state">
                    <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                      <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                      <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                    </svg>
                    <p>暂无岗位，点击上方按钮添加</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 创建/编辑岗位对话框 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showCreateDialog" class="modal-overlay" @click.self="showCreateDialog = false">
          <div class="modal-container">
            <div class="modal-titlebar">
              <span class="modal-title">{{ editingJob ? '编辑岗位' : '添加岗位' }}</span>
            </div>
            <div class="modal-content">
              <div class="form-group">
                <label class="form-label required">岗位名称</label>
                <input
                  v-model="jobForm.title"
                  type="text"
                  class="macos-input"
                  placeholder="请输入岗位名称，如：前端开发工程师"
                />
              </div>
              <div class="form-group">
                <label class="form-label">公司名称</label>
                <input
                  v-model="jobForm.company"
                  type="text"
                  class="macos-input"
                  placeholder="请输入公司名称（可选）"
                />
              </div>
              <div class="form-group">
                <label class="form-label required">岗位描述</label>
                <textarea
                  v-model="jobForm.job_description"
                  class="macos-textarea"
                  rows="8"
                  placeholder="请输入岗位描述（JD），包括岗位职责、任职要求等"
                ></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-secondary" @click="showCreateDialog = false">取消</button>
              <button class="btn-primary" :disabled="submitting" @click="handleSubmit">
                {{ editingJob ? '保存' : '创建' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 开始面试对话框 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showInterviewDialog" class="modal-overlay" @click.self="showInterviewDialog = false">
          <div class="modal-container">
            <div class="modal-titlebar">
              <span class="modal-title">开始面试</span>
            </div>
            <div class="modal-content">
              <div class="job-preview">
                <div class="preview-item">
                  <span class="preview-label">岗位名称</span>
                  <span class="preview-value">{{ selectedJob?.title }}</span>
                </div>
                <div class="preview-item">
                  <span class="preview-label">公司</span>
                  <span class="preview-value">{{ selectedJob?.company || '-' }}</span>
                </div>
                <div class="preview-item">
                  <span class="preview-label">岗位描述</span>
                  <span class="preview-value desc">{{ truncateText(selectedJob?.job_description, 150) }}</span>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label required">选择简历</label>
                <div class="select-wrapper">
                  <select v-model="interviewForm.resume_id" class="macos-select">
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

              <div class="form-group">
                <label class="form-label">知识库文档</label>
                <div class="select-wrapper">
                  <select v-model="interviewForm.knowledge_doc_ids" class="macos-select" multiple>
                    <option v-for="doc in knowledgeList" :key="doc.id" :value="doc.id">
                      {{ doc.file_name }}
                    </option>
                  </select>
                  <svg class="select-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="6 9 12 15 18 9"></polyline>
                  </svg>
                </div>
                <span class="form-hint">可选择多个知识库文档辅助面试</span>
              </div>

              <div class="form-group">
                <label class="form-label">面试官人设</label>
                <div class="select-wrapper">
                  <select v-model="interviewForm.persona_id" class="macos-select">
                    <option :value="null">默认面试官</option>
                    <option v-for="persona in personaList" :key="persona.id" :value="persona.id">
                      {{ persona.name }} - {{ persona.description }}
                    </option>
                  </select>
                  <svg class="select-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="6 9 12 15 18 9"></polyline>
                  </svg>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-secondary" @click="showInterviewDialog = false">取消</button>
              <button class="btn-primary" :disabled="creatingInterview" @click="handleCreateInterview">
                创建面试
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 模式选择对话框 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showModeDialog" class="modal-overlay" @click.self="showModeDialog = false">
          <div class="modal-container mode-dialog">
            <div class="modal-titlebar">
              <div class="modal-controls">
                <span class="control close" @click="showModeDialog = false"></span>
                <span class="control minimize"></span>
                <span class="control maximize"></span>
              </div>
              <span class="modal-title">选择面试模式</span>
            </div>
            <div class="modal-content">
              <div class="mode-options">
                <div
                  class="mode-card"
                  :class="{ active: selectedMode === 'normal' }"
                  @click="selectedMode = 'normal'"
                >
                  <div class="mode-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                  </div>
                  <h4>常规模式</h4>
                  <p>文字对话形式进行面试，适合日常练习</p>
                </div>
                <div
                  class="mode-card"
                  :class="{ active: selectedMode === 'video' }"
                  @click="selectedMode = 'video'"
                >
                  <div class="mode-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polygon points="23 7 16 12 23 17 23 7"></polygon>
                      <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
                    </svg>
                  </div>
                  <h4>视频模式</h4>
                  <p>开启摄像头和麦克风，模拟真实面试场景</p>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-secondary" @click="showModeDialog = false">取消</button>
              <button class="btn-primary" :disabled="!selectedMode" @click="confirmStartInterview">
                开始面试
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 历史面试记录对话框 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showHistoryDialog" class="modal-overlay" @click.self="showHistoryDialog = false">
          <div class="modal-container large">
            <div class="modal-titlebar">
              <div class="modal-controls">
                <span class="control close" @click="showHistoryDialog = false"></span>
                <span class="control minimize"></span>
                <span class="control maximize"></span>
              </div>
              <span class="modal-title">{{ selectedJob?.title || '' }} - 历史面试记录</span>
            </div>
            <div class="modal-content">
              <table class="macos-table">
                <thead>
                  <tr>
                    <th class="col-id">ID</th>
                    <th class="col-resume">简历</th>
                    <th class="col-status">状态</th>
                    <th class="col-score">分数</th>
                    <th class="col-date">面试时间</th>
                    <th class="col-actions">操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="interview in historyInterviews" :key="interview.id" class="table-row">
                    <td class="col-id">
                      <span class="id-badge">{{ interview.id }}</span>
                    </td>
                    <td class="col-resume">
                      <span class="resume-name">{{ getResumeName(interview.resume_id) }}</span>
                    </td>
                    <td class="col-status">
                      <span class="status-tag" :class="interview.status">
                        {{ getStatusText(interview.status) }}
                      </span>
                    </td>
                    <td class="col-score">
                      <span class="score-text">{{ interview.total_score || '-' }}</span>
                    </td>
                    <td class="col-date">
                      <span class="date-text">{{ formatDate(interview.created_at) }}</span>
                    </td>
                    <td class="col-actions">
                      <div class="action-group">
                        <button
                          v-if="interview.status === 'pending'"
                          class="table-btn primary"
                          @click="continueInterview(interview)"
                          title="开始面试"
                        >
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="5 3 19 12 5 21 5 3"></polygon>
                          </svg>
                        </button>
                        <button
                          v-if="interview.status === 'in_progress'"
                          class="table-btn warning"
                          @click="continueInterview(interview)"
                          title="继续面试"
                        >
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="5 3 19 12 5 21 5 3"></polygon>
                          </svg>
                        </button>
                        <button
                          v-if="interview.status === 'completed'"
                          class="table-btn success"
                          @click="viewReport(interview)"
                          title="查看报告"
                        >
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                            <line x1="16" y1="13" x2="8" y2="13"></line>
                            <line x1="16" y1="17" x2="8" y2="17"></line>
                          </svg>
                        </button>
                        <button
                          v-if="interview.status === 'completed'"
                          class="table-btn info"
                          @click="viewRecord(interview)"
                          title="查看对话"
                        >
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="historyInterviews.length === 0 && !loadingHistory">
                    <td colspan="6" class="empty-cell">
                      <div class="empty-state">
                        <p>暂无面试记录</p>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
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

const loading = ref(false)
const jobList = ref([])
const resumeList = ref([])
const knowledgeList = ref([])
const personaList = ref([])

const showCreateDialog = ref(false)
const editingJob = ref(null)
const submitting = ref(false)
const jobForm = ref({
  title: '',
  company: '',
  job_description: ''
})

const showInterviewDialog = ref(false)
const selectedJob = ref(null)
const creatingInterview = ref(false)
const interviewForm = ref({
  resume_id: '',
  knowledge_doc_ids: [],
  persona_id: null
})

const showModeDialog = ref(false)
const selectedMode = ref('normal')
const pendingInterview = ref(null)

const showHistoryDialog = ref(false)
const loadingHistory = ref(false)
const historyInterviews = ref([])

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

const resetJobForm = () => {
  editingJob.value = null
  jobForm.value = {
    title: '',
    company: '',
    job_description: ''
  }
}

const editJob = (job) => {
  editingJob.value = job
  jobForm.value = {
    title: job.title,
    company: job.company || '',
    job_description: job.job_description
  }
  showCreateDialog.value = true
}

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

const startInterview = (job) => {
  selectedJob.value = job
  interviewForm.value = {
    resume_id: '',
    knowledge_doc_ids: [],
    persona_id: null
  }
  showInterviewDialog.value = true
}

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

const getResumeName = (resumeId) => {
  const resume = resumeList.value.find(r => r.id === resumeId)
  return resume?.file_name || `简历 #${resumeId}`
}

const continueInterview = (interview) => {
  showHistoryDialog.value = false
  router.push(`/interview/${interview.id}`)
}

const viewReport = (interview) => {
  showHistoryDialog.value = false
  router.push(`/report/${interview.id}`)
}

const viewRecord = (interview) => {
  showHistoryDialog.value = false
  router.push(`/interview-record/${interview.id}`)
}

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
/* 页面容器 */
.job-list-page {
  padding: 24px;
  min-height: 100%;
  background: linear-gradient(180deg, #f5f5f7 0%, #ffffff 100%);
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

.window-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
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

.action-btn.primary:hover {
  background: linear-gradient(180deg, #0084ff 0%, #0070e6 100%);
}

.window-content {
  padding: 0;
}

/* 表格样式 */
.table-container {
  overflow-x: auto;
}

.macos-table {
  width: 100%;
  border-collapse: collapse;
}

.macos-table thead {
  background: rgba(0, 0, 0, 0.02);
}

.macos-table th {
  padding: 10px 16px;
  font-size: 11px;
  font-weight: 600;
  color: #86868b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-align: left;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.macos-table td {
  padding: 14px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  vertical-align: middle;
}

.table-row {
  transition: background 0.15s ease;
}

.table-row:hover {
  background: rgba(0, 122, 255, 0.04);
}

.col-id { width: 60px; }
.col-company { width: 120px; }
.col-date { width: 160px; }
.col-actions { width: 160px; }

.id-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 22px;
  padding: 0 8px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #86868b;
}

.job-title {
  font-size: 14px;
  font-weight: 500;
  color: #1d1d1f;
}

.company-name {
  font-size: 13px;
  color: #424245;
}

.desc-preview {
  font-size: 12px;
  color: #86868b;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.date-text {
  font-size: 12px;
  color: #86868b;
}

.action-group {
  display: flex;
  gap: 4px;
}

.table-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 6px;
  background: transparent;
  cursor: pointer;
  transition: all 0.15s ease;
}

.table-btn svg {
  width: 14px;
  height: 14px;
}

.table-btn.success { color: #34c759; }
.table-btn.success:hover { background: rgba(52, 199, 89, 0.1); }

.table-btn.info { color: #007aff; }
.table-btn.info:hover { background: rgba(0, 122, 255, 0.1); }

.table-btn.warning { color: #ff9500; }
.table-btn.warning:hover { background: rgba(255, 149, 0, 0.1); }

.table-btn.danger { color: #ff3b30; }
.table-btn.danger:hover { background: rgba(255, 59, 48, 0.1); }

.table-btn.primary { color: #007aff; }
.table-btn.primary:hover { background: rgba(0, 122, 255, 0.1); }

/* 空状态 */
.empty-cell {
  padding: 60px 20px !important;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #86868b;
}

.empty-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 13px;
}

/* Modal 样式 */
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

.modal-container {
  width: 640px;
  max-width: 95vw;
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

.modal-container.mode-dialog {
  width: 560px;
}

.modal-titlebar {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(180deg, #f6f6f6 0%, #e8e8e8 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.modal-controls {
  display: flex;
  gap: 8px;
  margin-right: 16px;
}

.modal-title {
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
}

.modal-content {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  background: rgba(0, 0, 0, 0.02);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
}

/* 表单样式 */
.form-group {
  margin-bottom: 20px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #86868b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.form-label.required::after {
  content: '*';
  color: #ff3b30;
  margin-left: 4px;
}

.form-hint {
  display: block;
  margin-top: 6px;
  font-size: 11px;
  color: #86868b;
}

.macos-input {
  width: 100%;
  padding: 10px 14px;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 14px;
  color: #1d1d1f;
  transition: all 0.15s ease;
}

.macos-input::placeholder {
  color: #86868b;
}

.macos-input:hover {
  border-color: rgba(0, 0, 0, 0.2);
}

.macos-input:focus {
  outline: none;
  border-color: #007aff;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.macos-textarea {
  width: 100%;
  padding: 12px 14px;
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
  width: 14px;
  height: 14px;
  color: #86868b;
  pointer-events: none;
}

/* 按钮样式 */
.btn-secondary {
  padding: 8px 20px;
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-secondary:hover {
  background: rgba(0, 0, 0, 0.08);
}

.btn-primary {
  padding: 8px 20px;
  background: linear-gradient(180deg, #007AFF 0%, #0066d6 100%);
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: white;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(180deg, #0084ff 0%, #0070e6 100%);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 岗位预览 */
.job-preview {
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 10px;
  margin-bottom: 20px;
}

.preview-item {
  display: flex;
  margin-bottom: 12px;
}

.preview-item:last-child {
  margin-bottom: 0;
}

.preview-label {
  width: 80px;
  flex-shrink: 0;
  font-size: 12px;
  font-weight: 500;
  color: #86868b;
}

.preview-value {
  flex: 1;
  font-size: 13px;
  color: #1d1d1f;
}

.preview-value.desc {
  color: #424245;
  line-height: 1.5;
}

/* 模式选择 */
.mode-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.mode-card {
  padding: 24px;
  border: 2px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-card:hover {
  border-color: rgba(0, 122, 255, 0.3);
  background: rgba(0, 122, 255, 0.02);
}

.mode-card.active {
  border-color: #007aff;
  background: rgba(0, 122, 255, 0.05);
}

.mode-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 122, 255, 0.1);
  border-radius: 12px;
  color: #007aff;
}

.mode-icon svg {
  width: 24px;
  height: 24px;
}

.mode-card h4 {
  font-size: 15px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 8px 0;
}

.mode-card p {
  font-size: 12px;
  color: #86868b;
  margin: 0;
  line-height: 1.5;
}

/* 状态标签 */
.status-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.status-tag.pending {
  background: rgba(142, 142, 147, 0.1);
  color: #8e8e93;
}

.status-tag.in_progress {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.status-tag.completed {
  background: rgba(52, 199, 89, 0.1);
  color: #34c759;
}

.status-tag.initializing,
.status-tag.analyzing {
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
}

.score-text {
  font-size: 14px;
  font-weight: 600;
  color: #1d1d1f;
}

.resume-name {
  font-size: 13px;
  color: #424245;
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
.modal-leave-to .modal-container {
  transform: scale(0.95) translateY(-10px);
}
</style>
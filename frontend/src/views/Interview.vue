<template>
  <div class="interview-page">
    <!-- 面试列表窗口 -->
    <div class="macos-window">
      <div class="window-titlebar">
        <div class="window-title">
          <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M12 6v6l4 2"></path>
          </svg>
          <span>模拟面试</span>
        </div>
        <div class="window-actions">
          <button class="action-btn primary" @click="showCreateDialog = true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            <span>创建面试</span>
          </button>
        </div>
      </div>

      <div class="window-content">
        <div class="table-container" v-loading="loading">
          <table class="macos-table">
            <thead>
              <tr>
                <th class="col-id">ID</th>
                <th class="col-desc">岗位描述</th>
                <th class="col-status">状态</th>
                <th class="col-score">分数</th>
                <th class="col-date">创建时间</th>
                <th class="col-actions">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="interview in interviewList" :key="interview.id" class="table-row">
                <td class="col-id">
                  <span class="id-badge">{{ interview.id }}</span>
                </td>
                <td class="col-desc">
                  <span class="desc-preview">{{ truncateText(interview.job_description, 100) }}</span>
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
                      class="table-btn success"
                      @click="startInterview(interview)"
                      title="开始面试"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                      </svg>
                      <span class="btn-text">开始</span>
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
                      <span class="btn-text">继续</span>
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
                      <span class="btn-text">报告</span>
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
                      <span class="btn-text">对话</span>
                    </button>
                    <button
                      v-if="interview.status === 'analyzing'"
                      class="table-btn disabled"
                      disabled
                      title="报告生成中"
                    >
                      <svg class="spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <path d="M12 6v6l4 2"></path>
                      </svg>
                      <span class="btn-text">分析中</span>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="interviewList.length === 0 && !loading">
                <td colspan="6" class="empty-cell">
                  <div class="empty-state">
                    <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                      <circle cx="12" cy="12" r="10"></circle>
                      <path d="M12 6v6l4 2"></path>
                    </svg>
                    <p>暂无面试记录，点击上方按钮创建</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 创建面试对话框 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showCreateDialog" class="modal-overlay" @click.self="showCreateDialog = false">
          <div class="modal-container">
            <div class="modal-titlebar">
              <div class="modal-controls">
                <span class="control close" @click="showCreateDialog = false"></span>
                <span class="control minimize"></span>
                <span class="control maximize"></span>
              </div>
              <span class="modal-title">创建面试</span>
            </div>
            <div class="modal-content">
              <div class="form-group">
                <label class="form-label required">选择简历</label>
                <div class="select-wrapper">
                  <select v-model="createForm.resume_id" class="macos-select">
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
                <label class="form-label">选择岗位</label>
                <div class="select-wrapper">
                  <select v-model="createForm.job_id" class="macos-select">
                    <option :value="null">选择已有岗位（可选，与岗位描述二选一）</option>
                    <option v-for="job in jobList" :key="job.id" :value="job.id">
                      {{ job.title }} - {{ job.company || '未知公司' }}
                    </option>
                  </select>
                  <svg class="select-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="6 9 12 15 18 9"></polyline>
                  </svg>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">岗位描述</label>
                <textarea
                  v-model="createForm.job_description"
                  class="macos-textarea"
                  rows="4"
                  :placeholder="createForm.job_id ? '已选择岗位，此项可留空' : '请输入目标岗位的职位描述（JD）'"
                  :disabled="!!createForm.job_id"
                ></textarea>
              </div>

              <div class="form-group">
                <label class="form-label">知识库文档</label>
                <div class="multi-select-dropdown" :class="{ open: knowledgeDropdownOpen }" v-click-outside="closeKnowledgeDropdown">
                  <div class="multi-select-trigger" @click="knowledgeDropdownOpen = !knowledgeDropdownOpen">
                    <div class="selected-tags" v-if="selectedKnowledgeDocs.length > 0">
                      <span class="tag" v-for="doc in selectedKnowledgeDocs" :key="doc.id">
                        {{ doc.file_name }}
                        <button type="button" class="tag-remove" @click.stop="removeKnowledgeDoc(doc.id)">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                          </svg>
                        </button>
                      </span>
                    </div>
                    <span class="placeholder" v-else>请选择知识库文档（可多选）</span>
                    <svg class="dropdown-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="6 9 12 15 18 9"></polyline>
                    </svg>
                  </div>
                  <div class="multi-select-options" v-show="knowledgeDropdownOpen">
                    <div class="option-item" v-if="knowledgeList.length === 0">
                      暂无可选文档
                    </div>
                    <div
                      class="option-item"
                      v-for="doc in knowledgeList"
                      :key="doc.id"
                      :class="{ selected: isKnowledgeDocSelected(doc.id) }"
                      @click="toggleKnowledgeDoc(doc.id)"
                    >
                      <span class="option-checkbox">
                        <svg v-if="isKnowledgeDocSelected(doc.id)" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                          <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                      </span>
                      <span class="option-text">{{ doc.file_name }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">面试官人设</label>
                <div class="select-wrapper">
                  <select v-model="createForm.persona_id" class="macos-select">
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
              <button class="btn-secondary" @click="showCreateDialog = false">取消</button>
              <button class="btn-primary" :disabled="creating" @click="handleCreate">
                {{ creating ? '创建中...' : '创建面试' }}
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
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getInterviewList, createInterview } from '@/api/interview'
import { getResumeList } from '@/api/resume'
import { getKnowledgeList } from '@/api/knowledge'
import { getPersonas } from '@/api/persona'
import { getJobList } from '@/api/job'

const vClickOutside = {
  mounted(el, binding) {
    el._clickOutside = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value()
      }
    }
    document.addEventListener('click', el._clickOutside)
  },
  unmounted(el) {
    document.removeEventListener('click', el._clickOutside)
  }
}

const router = useRouter()
const loading = ref(false)
const creating = ref(false)
const showCreateDialog = ref(false)
const showModeDialog = ref(false)
const selectedMode = ref('normal')
const pendingInterview = ref(null)
const interviewList = ref([])
const resumeList = ref([])
const knowledgeList = ref([])
const personaList = ref([])
const jobList = ref([])

const createForm = ref({
  resume_id: '',
  job_id: null,
  job_description: '',
  knowledge_doc_ids: [],
  persona_id: null
})

const knowledgeDropdownOpen = ref(false)

const selectedKnowledgeDocs = computed(() => {
  return knowledgeList.value.filter(doc => createForm.value.knowledge_doc_ids.includes(doc.id))
})

const isKnowledgeDocSelected = (id) => {
  return createForm.value.knowledge_doc_ids.includes(id)
}

const toggleKnowledgeDoc = (id) => {
  const index = createForm.value.knowledge_doc_ids.indexOf(id)
  if (index === -1) {
    createForm.value.knowledge_doc_ids.push(id)
  } else {
    createForm.value.knowledge_doc_ids.splice(index, 1)
  }
}

const removeKnowledgeDoc = (id) => {
  const index = createForm.value.knowledge_doc_ids.indexOf(id)
  if (index !== -1) {
    createForm.value.knowledge_doc_ids.splice(index, 1)
  }
}

const closeKnowledgeDropdown = () => {
  knowledgeDropdownOpen.value = false
}

const loadInterviewList = async () => {
  loading.value = true
  try {
    const res = await getInterviewList()
    if (res.code === 200) {
      interviewList.value = res.data || []
    }
  } catch (error) {
    console.error('加载面试列表失败:', error)
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

const loadJobList = async () => {
  try {
    const res = await getJobList()
    if (res.code === 200) {
      jobList.value = res.data || []
    }
  } catch (error) {
    console.error('加载岗位列表失败:', error)
  }
}

const handleCreate = async () => {
  if (!createForm.value.resume_id) {
    ElMessage.warning('请选择简历')
    return
  }

  if (!createForm.value.job_id && !createForm.value.job_description.trim()) {
    ElMessage.warning('请选择岗位或输入岗位描述')
    return
  }

  creating.value = true
  try {
    const res = await createInterview(createForm.value)
    if (res.code === 201) {
      ElMessage.success('创建成功')
      showCreateDialog.value = false
      createForm.value = {
        resume_id: '',
        job_id: null,
        job_description: '',
        knowledge_doc_ids: [],
        persona_id: null
      }
      loadInterviewList()
    }
  } catch (error) {
    console.error('创建失败:', error)
  } finally {
    creating.value = false
  }
}

const startInterview = (interview) => {
  pendingInterview.value = interview
  selectedMode.value = 'normal'
  showModeDialog.value = true
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

const continueInterview = (interview) => {
  router.push(`/interview/${interview.id}`)
}

const viewReport = (interview) => {
  router.push(`/report/${interview.id}`)
}

const viewRecord = (interview) => {
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
  if (!text) return '暂无岗位描述'
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

onMounted(() => {
  loadInterviewList()
  loadResumeList()
  loadKnowledgeList()
  loadPersonaList()
  loadJobList()
})
</script>

<style scoped>
/* 页面容器 */
.interview-page {
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
.col-status { width: 100px; }
.col-score { width: 80px; }
.col-date { width: 160px; }
.col-actions { width: 140px; }

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

.desc-preview {
  font-size: 13px;
  color: #424245;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.date-text {
  font-size: 12px;
  color: #86868b;
}

.score-text {
  font-size: 14px;
  font-weight: 600;
  color: #1d1d1f;
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
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.status-tag.initializing,
.status-tag.analyzing {
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
}

.status-tag.in_progress {
  background: rgba(88, 86, 214, 0.1);
  color: #5856d6;
}

.status-tag.completed {
  background: rgba(52, 199, 89, 0.1);
  color: #34c759;
}

/* 操作按钮 */
.action-group {
  display: flex;
  gap: 8px;
}

.table-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  background: transparent;
  cursor: pointer;
  transition: all 0.15s ease;
  font-size: 13px;
  font-weight: 500;
}

.table-btn svg {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.table-btn .btn-text {
  white-space: nowrap;
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

.table-btn.disabled {
  color: #86868b;
  cursor: not-allowed;
}

.table-btn .spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

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

.select-wrapper {
  position: relative;
}

.macos-select {
  width: 100%;
  padding: 10px 32px 10px 12px;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 13px;
  color: #1d1d1f;
  appearance: none;
  cursor: pointer;
  transition: all 0.15s ease;
}

.macos-select:hover {
  background: rgba(0, 0, 0, 0.04);
}

.macos-select:focus {
  outline: none;
  border-color: #007aff;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.select-arrow {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 14px;
  height: 14px;
  color: #86868b;
  pointer-events: none;
}

.macos-textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 13px;
  color: #1d1d1f;
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
  transition: all 0.15s ease;
}

.macos-textarea:hover {
  background: rgba(0, 0, 0, 0.04);
}

.macos-textarea:focus {
  outline: none;
  border-color: #007aff;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.macos-textarea:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.macos-select[multiple] {
  height: auto;
  min-height: 80px;
  padding-right: 12px;
}

.macos-select[multiple] option {
  padding: 8px;
  border-radius: 4px;
}

/* 多选下拉框样式 */
.multi-select-dropdown {
  position: relative;
  width: 100%;
}

.multi-select-trigger {
  display: flex;
  align-items: center;
  min-height: 40px;
  padding: 6px 32px 6px 12px;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
  flex-wrap: wrap;
  gap: 6px;
}

.multi-select-dropdown.open .multi-select-trigger {
  border-color: #007aff;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.multi-select-trigger:hover {
  background: rgba(0, 0, 0, 0.04);
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  flex: 1;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: rgba(0, 122, 255, 0.1);
  border-radius: 6px;
  font-size: 12px;
  color: #007aff;
  max-width: 180px;
}

.tag {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  color: #007aff;
  opacity: 0.7;
  transition: opacity 0.15s;
  flex-shrink: 0;
}

.tag-remove:hover {
  opacity: 1;
}

.tag-remove svg {
  width: 10px;
  height: 10px;
}

.placeholder {
  color: #86868b;
  font-size: 13px;
}

.dropdown-arrow {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 14px;
  height: 14px;
  color: #86868b;
  pointer-events: none;
  transition: transform 0.15s ease;
}

.multi-select-dropdown.open .dropdown-arrow {
  transform: translateY(-50%) rotate(180deg);
}

.multi-select-options {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  max-height: 240px;
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  z-index: 100;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  cursor: pointer;
  transition: background 0.1s ease;
}

.option-item:hover {
  background: rgba(0, 122, 255, 0.04);
}

.option-item.selected {
  background: rgba(0, 122, 255, 0.08);
}

.option-checkbox {
  width: 18px;
  height: 18px;
  border: 1.5px solid rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.option-item.selected .option-checkbox {
  background: #007aff;
  border-color: #007aff;
}

.option-checkbox svg {
  width: 12px;
  height: 12px;
  color: white;
}

.option-text {
  font-size: 13px;
  color: #1d1d1f;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 按钮样式 */
.btn-primary {
  padding: 10px 20px;
  background: linear-gradient(180deg, #007AFF 0%, #0066d6 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-primary:hover {
  background: linear-gradient(180deg, #0084ff 0%, #0070e6 100%);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.04);
  color: #1d1d1f;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-secondary:hover {
  background: rgba(0, 0, 0, 0.08);
}

/* 模式选择卡片 */
.mode-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.mode-card {
  position: relative;
  padding: 24px 20px;
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
  border-color: #007AFF;
  background: rgba(0, 122, 255, 0.04);
}

.mode-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 12px;
  color: #86868b;
  transition: color 0.2s ease;
}

.mode-card.active .mode-icon {
  color: #007AFF;
}

.mode-icon svg {
  width: 100%;
  height: 100%;
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

/* Modal 动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}

/* 响应式 */
@media (max-width: 768px) {
  .interview-page {
    padding: 16px;
  }

  .modal-container {
    width: 95% !important;
  }

  .mode-options {
    grid-template-columns: 1fr;
  }
}
</style>
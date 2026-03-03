<template>
  <div class="interview">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>模拟面试</span>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            创建面试
          </el-button>
        </div>
      </template>

      <el-table :data="interviewList" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="job_description" label="岗位描述" min-width="200">
          <template #default="{ row }">
            {{ truncateText(row.job_description, 150) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="分数" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              type="primary"
              size="small"
              @click="startInterview(row)"
            >
              开始面试
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
            <el-button
              v-else-if="row.status === 'analyzing'"
              type="info"
              size="small"
              disabled
            >
              报告生成中...
            </el-button>
            <el-button
              v-if="row.status === 'in_progress'"
              type="warning"
              size="small"
              @click="continueInterview(row)"
            >
              继续面试
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建面试对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建面试" width="700px" class="create-interview-dialog">
      <el-form :model="createForm" label-width="90px">
        <el-form-item label="选择简历" required>
          <el-select
            v-model="createForm.resume_id"
            placeholder="请选择简历"
            style="width: 100%"
            size="large"
          >
            <el-option
              v-for="resume in resumeList"
              :key="resume.id"
              :label="resume.file_name"
              :value="resume.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="选择岗位">
          <el-select
            v-model="createForm.job_id"
            placeholder="选择已有岗位（可选，与岗位描述二选一）"
            style="width: 100%"
            size="large"
            clearable
          >
            <el-option
              v-for="job in jobList"
              :key="job.id"
              :label="job.title"
              :value="job.id"
            >
              <div class="job-option">
                <span class="job-title">{{ job.title }}</span>
                <span class="job-company">{{ job.company }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="岗位描述">
          <el-input
            v-model="createForm.job_description"
            type="textarea"
            :rows="4"
            :placeholder="createForm.job_id ? '已选择岗位，此项可留空' : '请输入目标岗位的职位描述（JD），例如：岗位职责、任职要求等'"
            :disabled="!!createForm.job_id"
            size="large"
          />
        </el-form-item>

        <el-form-item label="知识库文档">
          <el-select
            v-model="createForm.knowledge_doc_ids"
            placeholder="请选择知识库文档（可选）"
            style="width: 100%"
            multiple
            collapse-tags
            collapse-tags-tooltip
            size="large"
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
            v-model="createForm.persona_id"
            placeholder="选择面试官风格"
            style="width: 100%"
            size="large"
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
        <el-button size="large" @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" size="large" :loading="creating" @click="handleCreate">
          创建面试
        </el-button>
      </template>
    </el-dialog>

    <!-- 模式选择对话框 -->
    <el-dialog
      v-model="showModeDialog"
      title="选择面试模式"
      width="500px"
      class="mode-select-dialog"
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, VideoCamera, ChatLineSquare } from '@element-plus/icons-vue'
import { getInterviewList, createInterview } from '@/api/interview'
import { getResumeList } from '@/api/resume'
import { getKnowledgeList } from '@/api/knowledge'
import { getPersonas } from '@/api/persona'
import { getJobList } from '@/api/job'

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

  // 必须选择岗位或手动输入岗位描述
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
    // 视频模式：尝试请求权限，但不阻止进入
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: true, 
        audio: true 
      })
      // 权限获取成功，关闭流（进入页面后会重新获取）
      stream.getTracks().forEach(track => track.stop())
    } catch (error) {
      console.warn('获取媒体设备权限失败:', error)
      // 提示但不阻止进入
      ElMessage.warning('未检测到摄像头或麦克风，视频面试将以黑屏模式进行')
    }
    router.push(`/video-interview/${pendingInterview.value.id}`)
  } else {
    // 常规模式：直接跳转到普通面试房间
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
  loadInterviewList()
  loadResumeList()
  loadKnowledgeList()
  loadPersonaList()
  loadJobList()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.job-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.job-title {
  font-weight: 500;
  color: var(--text-primary);
}

.job-company {
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
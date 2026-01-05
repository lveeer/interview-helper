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
        <el-table-column prop="job_description" label="岗位描述" min-width="200" show-overflow-tooltip />
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
    <el-dialog v-model="showCreateDialog" title="创建面试" width="600px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="选择简历">
          <el-select
            v-model="createForm.resume_id"
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

        <el-form-item label="岗位描述">
          <el-input
            v-model="createForm.job_description"
            type="textarea"
            :rows="8"
            placeholder="请输入目标岗位的职位描述（JD）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getInterviewList, createInterview } from '@/api/interview'
import { getResumeList } from '@/api/resume'

const router = useRouter()
const loading = ref(false)
const creating = ref(false)
const showCreateDialog = ref(false)
const interviewList = ref([])
const resumeList = ref([])

const createForm = ref({
  resume_id: '',
  job_description: ''
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

const handleCreate = async () => {
  if (!createForm.value.resume_id) {
    ElMessage.warning('请选择简历')
    return
  }

  if (!createForm.value.job_description.trim()) {
    ElMessage.warning('请输入岗位描述')
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
        job_description: ''
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
  router.push(`/interview/${interview.id}`)
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

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadInterviewList()
  loadResumeList()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
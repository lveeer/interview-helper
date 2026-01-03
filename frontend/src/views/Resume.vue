<template>
  <div class="resume">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>简历管理</span>
          <el-button type="primary" @click="showUploadDialog = true">
            <el-icon><Upload /></el-icon>
            上传简历
          </el-button>
        </div>
      </template>

      <el-table :data="resumeList" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="file_name" label="文件名" />
        <el-table-column prop="file_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag>{{ row.file_type.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewResume(row)">
              查看
            </el-button>
            <el-button type="danger" size="small" @click="deleteResume(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 上传对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传简历" width="500px">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept=".pdf,.docx,.doc"
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 PDF、DOCX、DOC 格式，文件大小不超过 10MB
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">
          上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 简历详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="简历详情" width="800px">
      <el-descriptions v-if="currentResume" :column="2" border>
        <el-descriptions-item label="文件名">
          {{ currentResume.file_name }}
        </el-descriptions-item>
        <el-descriptions-item label="文件类型">
          {{ currentResume.file_type.toUpperCase() }}
        </el-descriptions-item>
        <el-descriptions-item v-if="currentResume.personal_info" label="姓名">
          {{ JSON.parse(currentResume.personal_info).name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item v-if="currentResume.personal_info" label="邮箱">
          {{ JSON.parse(currentResume.personal_info).email || '-' }}
        </el-descriptions-item>
        <el-descriptions-item v-if="currentResume.skills" label="技能" :span="2">
          <el-tag
            v-for="skill in JSON.parse(currentResume.skills)"
            :key="skill"
            style="margin-right: 5px; margin-bottom: 5px;"
          >
            {{ skill }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getResumeList, uploadResume, deleteResume as deleteResumeApi } from '@/api/resume'

const loading = ref(false)
const uploading = ref(false)
const showUploadDialog = ref(false)
const showDetailDialog = ref(false)
const uploadRef = ref(null)
const resumeList = ref([])
const currentResume = ref(null)
const selectedFile = ref(null)

const loadResumeList = async () => {
  loading.value = true
  try {
    const res = await getResumeList()
    if (res.code === 200) {
      resumeList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载简历列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const handleUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  uploading.value = true
  try {
    const res = await uploadResume(selectedFile.value)
    if (res.code === 201) {
      ElMessage.success('上传成功')
      showUploadDialog.value = false
      selectedFile.value = null
      uploadRef.value?.clearFiles()
      loadResumeList()
    }
  } catch (error) {
    console.error('上传失败:', error)
  } finally {
    uploading.value = false
  }
}

const viewResume = (resume) => {
  currentResume.value = resume
  showDetailDialog.value = true
}

const deleteResume = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这份简历吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const res = await deleteResumeApi(id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      loadResumeList()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
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
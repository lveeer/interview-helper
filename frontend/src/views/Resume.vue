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
        <el-table-column label="操作" width="380" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewResume(row)" style="margin-right: 16px;">
              查看
            </el-button>
            <el-button type="warning" size="small" @click="reparseResume(row.id)" :loading="reparseLoading[row.id]" style="margin-right: 16px;">
              重新解析
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
    <el-dialog v-model="showDetailDialog" title="简历详情" width="900px" top="3vh">
      <div v-if="currentResume" class="resume-template">
        <!-- 个人信息 -->
        <div class="resume-section">
          <h3 class="section-header">
            <span class="section-marker"></span>
            个人信息
          </h3>
          <div class="section-content">
            <div class="info-row">
              <span class="info-label">姓名：</span>
              <span class="info-value">{{ currentResume.personal_info?.name || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">年龄：</span>
              <span class="info-value">{{ currentResume.personal_info?.age || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">电话：</span>
              <span class="info-value">{{ currentResume.personal_info?.phone || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">邮箱：</span>
              <span class="info-value">{{ currentResume.personal_info?.email || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">工作年限：</span>
              <span class="info-value">{{ currentResume.personal_info?.work_years || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">个人博客：</span>
              <span class="info-value">
                <a v-if="currentResume.personal_info?.blog" :href="currentResume.personal_info.blog" target="_blank" class="blog-link">
                  {{ currentResume.personal_info.blog }}
                </a>
                <span v-else>-</span>
              </span>
            </div>
          </div>
        </div>

        <!-- 教育背景 -->
        <div v-if="currentResume.education && currentResume.education.length > 0" class="resume-section">
          <h3 class="section-header">
            <span class="section-marker"></span>
            教育背景
          </h3>
          <div class="section-content">
            <div v-for="(edu, index) in currentResume.education" :key="index" class="edu-item">
              <div class="edu-header">
                <span class="edu-school">{{ edu.school }}</span>
                <span class="edu-time">{{ edu.start_date || edu.start_time }} - {{ edu.end_date || edu.end_time }}</span>
              </div>
              <div class="edu-details">
                <span class="edu-major">{{ edu.major }}</span>
                <span class="edu-degree">{{ edu.degree }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 工作经验 -->
        <div v-if="currentResume.experience && currentResume.experience.length > 0" class="resume-section">
          <h3 class="section-header">
            <span class="section-marker"></span>
            工作经验
          </h3>
          <div class="section-content">
            <div v-for="(exp, index) in currentResume.experience" :key="index" class="exp-item">
              <div class="exp-header">
                <div class="exp-title">
                  <span class="exp-company">{{ exp.company }}</span>
                  <span class="exp-position">{{ exp.position }}</span>
                </div>
                <span class="exp-time">{{ exp.start_date || exp.start_time }} - {{ exp.end_date || exp.end_time }}</span>
              </div>
              <div v-if="exp.description" class="exp-description">{{ exp.description }}</div>
              <ul v-if="exp.responsibilities && exp.responsibilities.length > 0" class="achievements-list">
                <li v-for="(achievement, i) in exp.responsibilities" :key="i">
                  {{ achievement }}
                </li>
              </ul>
              <ul v-else-if="exp.achievements && exp.achievements.length > 0" class="achievements-list">
                <li v-for="(achievement, i) in exp.achievements" :key="i">
                  {{ achievement }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 项目经历 -->
        <div v-if="currentResume.projects && currentResume.projects.length > 0" class="resume-section">
          <h3 class="section-header">
            <span class="section-marker"></span>
            项目经历
          </h3>
          <div class="section-content">
            <div v-for="(project, index) in currentResume.projects" :key="index" class="project-item">
              <div class="project-header">
                <div class="project-title">
                  <span class="project-name">{{ project.name }}</span>
                  <span class="project-role">{{ project.role }}</span>
                </div>
                <span class="project-time">{{ project.start_date || project.start_time }} - {{ project.end_date || project.end_time }}</span>
              </div>
              <div v-if="project.background" class="project-description">{{ project.background }}</div>
              <div v-else-if="project.description" class="project-description">{{ project.description }}</div>
              <div v-if="project.tech_stack && project.tech_stack.length > 0" class="tech-stack">
                <span class="tech-label">技术栈：</span>
                <span class="tech-value">{{ project.tech_stack.join('、') }}</span>
              </div>
              <ul v-if="project.responsibilities && project.responsibilities.length > 0" class="achievements-list">
                <li v-for="(achievement, i) in project.responsibilities" :key="i">
                  {{ achievement }}
                </li>
              </ul>
              <ul v-else-if="project.achievements && project.achievements.length > 0" class="achievements-list">
                <li v-for="(achievement, i) in project.achievements" :key="i">
                  {{ achievement }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 技能特长 -->
        <div v-if="currentResume.skills && currentResume.skills.length > 0" class="resume-section">
          <h3 class="section-header">
            <span class="section-marker"></span>
            技能特长
          </h3>
          <div class="section-content">
            <div class="skills-grid">
              <div v-for="(skill, index) in currentResume.skills" :key="index" class="skill-tag">
                {{ skill }}
              </div>
            </div>
          </div>
        </div>

        <!-- 技能详情 -->
        <div v-if="currentResume.skills_raw && currentResume.skills_raw.length > 0" class="resume-section">
          <h3 class="section-header">
            <span class="section-marker"></span>
            技能详情
          </h3>
          <div class="section-content">
            <ul class="achievements-list">
              <li v-for="(skillRaw, index) in currentResume.skills_raw" :key="index">
                {{ skillRaw }}
              </li>
            </ul>
          </div>
        </div>

        <!-- 荣誉证书 -->
        <div v-if="currentResume.highlights && currentResume.highlights.length > 0" class="resume-section">
          <h3 class="section-header">
            <span class="section-marker"></span>
            荣誉证书
          </h3>
          <div class="section-content">
            <ul class="achievements-list">
              <li v-for="(cert, index) in currentResume.highlights" :key="index">
                {{ cert }}
              </li>
            </ul>
          </div>
        </div>

        
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, User, Phone, Message, Location, Clock } from '@element-plus/icons-vue'
import { getResumeList, uploadResume, deleteResume as deleteResumeApi, getResumeDetail, reparseResume as reparseResumeApi } from '@/api/resume'

const loading = ref(false)
const uploading = ref(false)
const showUploadDialog = ref(false)
const showDetailDialog = ref(false)
const uploadRef = ref(null)
const resumeList = ref([])
const currentResume = ref(null)
const selectedFile = ref(null)
const reparseLoading = ref({})

const loadResumeList = async () => {
  loading.value = true
  try {
    const res = await getResumeList()
    if (res.code === 200) {
      resumeList.value = res.data || []
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

const viewResume = async (resume) => {
  try {
    const res = await getResumeDetail(resume.id)
    if (res.code === 200) {
      currentResume.value = res.data
      showDetailDialog.value = true
    } else {
      ElMessage.error('获取简历详情失败')
    }
  } catch (error) {
    console.error('获取简历详情失败:', error)
    ElMessage.error('获取简历详情失败')
  }
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

const reparseResume = async (id) => {
  try {
    await ElMessageBox.confirm('确定要重新解析这份简历吗？这将使用最新的 LLM 提示词重新解析简历内容。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    reparseLoading.value[id] = true
    const res = await reparseResumeApi(id)
    if (res.code === 200) {
      ElMessage.success('重新解析成功')
      loadResumeList()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重新解析失败:', error)
      ElMessage.error('重新解析失败')
    }
  } finally {
    reparseLoading.value[id] = false
  }
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

/* GitHub 风格简历模版 */
.resume-template {
  min-height: 600px;
  max-height: 75vh;
  overflow-y: auto;
  background: var(--bg-color-white);
  padding: 40px 50px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
  color: var(--text-primary);
  line-height: 1.6;
}

/* 版块样式 */
.resume-section {
  margin-bottom: 30px;
}

.resume-section:last-child {
  margin-bottom: 0;
}

/* 版块标题 - GitHub 风格 */
.section-header {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 15px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.section-marker {
  width: 4px;
  height: 18px;
  background: var(--primary-color);
  border-radius: 2px;
  margin-right: 10px;
  flex-shrink: 0;
}

/* 版块内容 */
.section-content {
  padding-left: 14px;
}

/* 信息行样式 */
.info-row {
  display: flex;
  align-items: baseline;
  margin-bottom: 8px;
  line-height: 1.8;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  font-weight: 500;
  color: var(--text-secondary);
  min-width: 100px;
  flex-shrink: 0;
}

.info-value {
  color: var(--text-primary);
  font-weight: 400;
}

/* 教育背景 */
.edu-item {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.edu-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.edu-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 5px;
  flex-wrap: wrap;
  gap: 8px;
}

.edu-school {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.edu-time {
  font-size: 13px;
  color: var(--text-secondary);
}

.edu-details {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.edu-major {
  font-size: 14px;
  color: var(--text-primary);
}

.edu-degree {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 工作经验 */
.exp-item {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.exp-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.exp-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 8px;
  flex-wrap: wrap;
  gap: 8px;
}

.exp-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.exp-company {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.exp-position {
  font-size: 14px;
  color: var(--primary-color);
  font-weight: 500;
}

.exp-time {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.exp-description {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-regular);
  margin-bottom: 10px;
  text-align: justify;
}

/* 项目经历 */
.project-item {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.project-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 8px;
  flex-wrap: wrap;
  gap: 8px;
}

.project-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.project-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.project-role {
  font-size: 14px;
  color: var(--info-color);
  font-weight: 500;
}

.project-time {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.project-description {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-regular);
  margin-bottom: 10px;
  text-align: justify;
}

/* 成就列表 */
.achievements-list {
  margin: 10px 0;
  padding-left: 20px;
  list-style-type: disc;
}

.achievements-list li {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-regular);
  margin-bottom: 5px;
  text-align: justify;
}

/* 技术栈 */
.tech-stack {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 8px 0;
}

.tech-label {
  font-weight: 500;
  color: var(--text-secondary);
}

.tech-value {
  color: var(--primary-color);
}

/* 技能网格 */
.skills-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.skill-tag {
  display: inline-block;
  padding: 6px 12px;
  background: var(--bg-color-light);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 400;
}

/* 证书列表 */
.cert-item {
  font-size: 14px;
  color: var(--text-primary);
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color-light);
}

.cert-item:last-child {
  border-bottom: none;
}

/* 技能详情 */
.skill-raw-item {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-regular);
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color-light);
  text-align: justify;
}

.skill-raw-item:last-child {
  border-bottom: none;
}

/* 个人简介 */
.summary-text {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-regular);
  text-align: justify;
}

/* 博客链接 */
.blog-link {
  color: var(--primary-color);
  text-decoration: none;
  font-size: 14px;
}

.blog-link:hover {
  text-decoration: underline;
}

/* 滚动条样式 */
.resume-template::-webkit-scrollbar {
  width: 8px;
}

.resume-template::-webkit-scrollbar-track {
  background: var(--bg-color-light);
}

.resume-template::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}

.resume-template::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}
</style>
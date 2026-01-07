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
    <el-dialog v-model="showDetailDialog" title="简历详情" width="1000px" top="3vh">
      <div v-if="currentResume" class="resume-template">
        <!-- 左侧栏 -->
        <div class="resume-sidebar">
          <!-- 头像区域 -->
          <div class="avatar-section">
            <div class="avatar-placeholder">
              <el-icon :size="60"><User /></el-icon>
            </div>
            <h3 class="candidate-name">{{ currentResume.personal_info?.name || '候选人' }}</h3>
            <p class="candidate-title">{{ currentResume.personal_info?.expected_position || '求职者' }}</p>
          </div>

          <!-- 联系方式 -->
          <div class="sidebar-section">
            <h4 class="sidebar-title">联系方式</h4>
            <div class="contact-list">
              <div v-if="currentResume.personal_info?.phone" class="contact-item">
                <el-icon><Phone /></el-icon>
                <span>{{ currentResume.personal_info.phone }}</span>
              </div>
              <div v-if="currentResume.personal_info?.email" class="contact-item">
                <el-icon><Message /></el-icon>
                <span>{{ currentResume.personal_info.email }}</span>
              </div>
              <div v-if="currentResume.personal_info?.location" class="contact-item">
                <el-icon><Location /></el-icon>
                <span>{{ currentResume.personal_info.location }}</span>
              </div>
              <div v-if="currentResume.personal_info?.work_years" class="contact-item">
                <el-icon><Clock /></el-icon>
                <span>{{ currentResume.personal_info.work_years }}工作经验</span>
              </div>
            </div>
          </div>

          <!-- 教育背景 -->
          <div v-if="currentResume.education && currentResume.education.length > 0" class="sidebar-section">
            <h4 class="sidebar-title">教育背景</h4>
            <div class="education-list">
              <div v-for="(edu, index) in currentResume.education" :key="index" class="education-item">
                <div class="edu-school">{{ edu.school }}</div>
                <div class="edu-major">{{ edu.major }}</div>
                <div class="edu-degree">{{ edu.degree }}</div>
                <div class="edu-time">{{ edu.start_time }} - {{ edu.end_time }}</div>
              </div>
            </div>
          </div>

          <!-- 技能专长 -->
          <div v-if="currentResume.skills && currentResume.skills.length > 0" class="sidebar-section">
            <h4 class="sidebar-title">技能专长</h4>
            <div class="skills-list">
              <div v-for="(skill, index) in currentResume.skills" :key="index" class="skill-item">
                {{ skill }}
              </div>
            </div>
          </div>

          <!-- 证书荣誉 -->
          <div v-if="currentResume.certificates && currentResume.certificates.length > 0" class="sidebar-section">
            <h4 class="sidebar-title">证书荣誉</h4>
            <div class="certificates-list">
              <div v-for="(cert, index) in currentResume.certificates" :key="index" class="certificate-item">
                {{ cert }}
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧主内容区 -->
        <div class="resume-main">
          <!-- 个人简介 -->
          <div v-if="currentResume.summary" class="main-section">
            <h3 class="section-title">
              <span class="title-line"></span>
              <span>个人简介</span>
            </h3>
            <div class="summary-text">{{ currentResume.summary }}</div>
          </div>

          <!-- 工作经历 -->
          <div v-if="currentResume.experience && currentResume.experience.length > 0" class="main-section">
            <h3 class="section-title">
              <span class="title-line"></span>
              <span>工作经历</span>
            </h3>
            <div class="experience-list">
              <div v-for="(exp, index) in currentResume.experience" :key="index" class="experience-item">
                <div class="exp-header">
                  <div class="exp-company-position">
                    <span class="exp-company">{{ exp.company }}</span>
                    <span class="exp-position">{{ exp.position }}</span>
                  </div>
                  <span class="exp-time">{{ exp.start_time }} - {{ exp.end_time }}</span>
                </div>
                <div v-if="exp.description" class="exp-description">{{ exp.description }}</div>
                <ul v-if="exp.achievements && exp.achievements.length > 0" class="achievements-list">
                  <li v-for="(achievement, i) in exp.achievements" :key="i">
                    {{ achievement }}
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- 项目经历 -->
          <div v-if="currentResume.projects && currentResume.projects.length > 0" class="main-section">
            <h3 class="section-title">
              <span class="title-line"></span>
              <span>项目经历</span>
            </h3>
            <div class="projects-list">
              <div v-for="(project, index) in currentResume.projects" :key="index" class="project-item">
                <div class="project-header">
                  <div class="project-name-role">
                    <span class="project-name">{{ project.name }}</span>
                    <span class="project-role">{{ project.role }}</span>
                  </div>
                  <span class="project-time">{{ project.start_time }} - {{ project.end_time }}</span>
                </div>
                <div v-if="project.description" class="project-description">{{ project.description }}</div>
                <ul v-if="project.achievements && project.achievements.length > 0" class="achievements-list">
                  <li v-for="(achievement, i) in project.achievements" :key="i">
                    {{ achievement }}
                  </li>
                </ul>
              </div>
            </div>
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
import { getResumeList, uploadResume, deleteResume as deleteResumeApi, getResumeDetail } from '@/api/resume'

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

/* 简历模版整体布局 */
.resume-template {
  display: flex;
  min-height: 600px;
  max-height: 75vh;
  overflow-y: auto;
  background: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

/* 左侧栏 */
.resume-sidebar {
  width: 280px;
  background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
  color: #fff;
  padding: 30px 20px;
  flex-shrink: 0;
}

/* 头像区域 */
.avatar-section {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.avatar-placeholder {
  width: 100px;
  height: 100px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.candidate-name {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #fff;
}

.candidate-title {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

/* 左侧栏区块 */
.sidebar-section {
  margin-bottom: 30px;
}

.sidebar-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 15px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.3);
  color: #fff;
}

/* 联系方式 */
.contact-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
}

.contact-item .el-icon {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
}

/* 教育背景 */
.education-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.education-item {
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.education-item:last-child {
  border-bottom: none;
}

.edu-school {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 5px;
  color: #fff;
}

.edu-major {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 3px;
}

.edu-degree {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 3px;
}

.edu-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

/* 技能列表 */
.skills-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skill-item {
  font-size: 13px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.95);
}

/* 证书列表 */
.certificates-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.certificate-item {
  font-size: 13px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.95);
}

/* 右侧主内容区 */
.resume-main {
  flex: 1;
  padding: 30px 35px;
  background: #fff;
}

.main-section {
  margin-bottom: 35px;
}

.main-section:last-child {
  margin-bottom: 0;
}

/* 章节标题 */
.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 20px 0;
  padding-bottom: 10px;
  border-bottom: 3px solid #2c3e50;
}

.title-line {
  width: 5px;
  height: 24px;
  background: #2c3e50;
  border-radius: 2px;
}

/* 个人简介 */
.summary-text {
  font-size: 14px;
  line-height: 1.8;
  color: #555;
  text-align: justify;
  padding: 10px 0;
}

/* 工作经历 */
.experience-list {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.experience-item {
  padding-left: 0;
}

.exp-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
}

.exp-company-position {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.exp-company {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.exp-position {
  font-size: 14px;
  color: #3498db;
  font-weight: 500;
}

.exp-time {
  font-size: 13px;
  color: #7f8c8d;
  white-space: nowrap;
}

.exp-description {
  font-size: 14px;
  line-height: 1.7;
  color: #555;
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
  color: #555;
  margin-bottom: 5px;
  text-align: justify;
}

/* 项目经历 */
.projects-list {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.project-item {
  padding-left: 0;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
}

.project-name-role {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.project-name {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.project-role {
  font-size: 14px;
  color: #e67e22;
  font-weight: 500;
}

.project-time {
  font-size: 13px;
  color: #7f8c8d;
  white-space: nowrap;
}

.project-description {
  font-size: 14px;
  line-height: 1.7;
  color: #555;
  margin-bottom: 10px;
  text-align: justify;
}

/* 滚动条样式 */
.resume-template::-webkit-scrollbar {
  width: 6px;
}

.resume-template::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.resume-template::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.resume-template::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
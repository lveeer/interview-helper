<template>
  <div class="resume-page">
    <!-- macOS 窗口式卡片 -->
    <div class="macos-window">
      <!-- 窗口标题栏 -->
      <div class="window-titlebar">
        <div class="window-title">
          <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
          <span>简历管理</span>
        </div>
        <div class="window-actions">
          <button class="action-btn upload-btn" @click="showUploadDialog = true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <span>上传简历</span>
          </button>
        </div>
      </div>

      <!-- 窗口内容 -->
      <div class="window-content">
        <!-- 表格容器 -->
        <div class="table-container" v-loading="loading">
          <table class="macos-table">
            <thead>
              <tr>
                <th class="col-id">ID</th>
                <th class="col-name">文件名</th>
                <th class="col-type">类型</th>
                <th class="col-date">上传时间</th>
                <th class="col-actions">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="resume in resumeList" :key="resume.id" class="table-row">
                <td class="col-id">
                  <span class="id-badge">{{ resume.id }}</span>
                </td>
                <td class="col-name">
                  <div class="file-info">
                    <div class="file-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                      </svg>
                    </div>
                    <span class="file-name">{{ resume.file_name }}</span>
                  </div>
                </td>
                <td class="col-type">
                  <span class="type-tag" :class="resume.file_type.toLowerCase()">
                    {{ resume.file_type.toUpperCase() }}
                  </span>
                </td>
                <td class="col-date">
                  <span class="date-text">{{ formatDate(resume.created_at) }}</span>
                </td>
                <td class="col-actions">
                  <div class="action-group">
                    <button class="table-btn view" @click="viewResume(resume)" title="查看">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                      </svg>
                    </button>
                    <button class="table-btn refresh" @click="reparseResume(resume.id)" :disabled="reparseLoading[resume.id]" title="重新解析">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ spinning: reparseLoading[resume.id] }">
                        <polyline points="23 4 23 10 17 10"></polyline>
                        <polyline points="1 20 1 14 7 14"></polyline>
                        <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
                      </svg>
                    </button>
                    <button class="table-btn delete" @click="deleteResume(resume.id)" title="删除">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        <line x1="10" y1="11" x2="10" y2="17"></line>
                        <line x1="14" y1="11" x2="14" y2="17"></line>
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="resumeList.length === 0 && !loading">
                <td colspan="5" class="empty-cell">
                  <div class="empty-state">
                    <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                      <polyline points="14 2 14 8 20 8"></polyline>
                    </svg>
                    <p>暂无简历，点击上方按钮上传</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 上传对话框 - macOS 风格 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showUploadDialog" class="modal-overlay" @click.self="showUploadDialog = false">
          <div class="modal-container">
            <div class="modal-titlebar">
              <span class="modal-title">上传简历</span>
            </div>
            <div class="modal-content">
              <div
                class="upload-area"
                :class="{ 'drag-over': isDragOver }"
                @dragover.prevent="isDragOver = true"
                @dragleave.prevent="isDragOver = false"
                @drop.prevent="handleDrop"
                @click="triggerFileInput"
              >
                <input
                  ref="fileInput"
                  type="file"
                  accept=".pdf,.docx,.doc"
                  style="display: none"
                  @change="handleFileSelect"
                />
                <div class="upload-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="17 8 12 3 7 8"></polyline>
                    <line x1="12" y1="3" x2="12" y2="15"></line>
                  </svg>
                </div>
                <p class="upload-text">拖拽文件到此处，或<span class="link">点击选择</span></p>
                <p class="upload-hint">支持 PDF、DOCX、DOC 格式，最大 10MB</p>
              </div>
              <div v-if="selectedFile" class="selected-file">
                <svg class="file-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <span class="file-name">{{ selectedFile.name }}</span>
                <button class="remove-file" @click="clearSelectedFile">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-secondary" @click="showUploadDialog = false">取消</button>
              <button class="btn-primary" :disabled="!selectedFile || uploading" @click="handleUpload">
                <svg v-if="uploading" class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
                  <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"></path>
                </svg>
                {{ uploading ? '上传中...' : '上传' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

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
import { getResumeList, uploadResume, deleteResume as deleteResumeApi, getResumeDetail, reparseResume as reparseResumeApi } from '@/api/resume'

const loading = ref(false)
const uploading = ref(false)
const showUploadDialog = ref(false)
const showDetailDialog = ref(false)
const fileInput = ref(null)
const resumeList = ref([])
const currentResume = ref(null)
const selectedFile = ref(null)
const reparseLoading = ref({})
const isDragOver = ref(false)

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

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (e) => {
  const file = e.target.files?.[0]
  if (file) {
    selectedFile.value = file
  }
}

const handleDrop = (e) => {
  isDragOver.value = false
  const file = e.dataTransfer.files?.[0]
  if (file) {
    const validTypes = ['.pdf', '.docx', '.doc']
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
    if (validTypes.includes(ext)) {
      selectedFile.value = file
    } else {
      ElMessage.warning('请上传 PDF、DOCX 或 DOC 格式的文件')
    }
  }
}

const clearSelectedFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
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
      clearSelectedFile()
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
/* 页面容器 */
.resume-page {
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

/* 窗口标题栏 */
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

.control:hover {
  filter: brightness(1.1);
}

.window-title {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
  letter-spacing: -0.01em;
}

.title-icon {
  width: 18px;
  height: 18px;
  color: #86868b;
}

.window-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn svg {
  width: 14px;
  height: 14px;
}

.upload-btn {
  background: linear-gradient(180deg, #007AFF 0%, #0066d6 100%);
  color: white;
  box-shadow: 0 1px 3px rgba(0, 122, 255, 0.3);
}

.upload-btn:hover {
  background: linear-gradient(180deg, #0084ff 0%, #0070e6 100%);
  box-shadow: 0 2px 6px rgba(0, 122, 255, 0.4);
}

/* 窗口内容 */
.window-content {
  padding: 0;
}

/* 表格容器 */
.table-container {
  overflow-x: auto;
}

/* macOS 风格表格 */
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
  padding: 12px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  vertical-align: middle;
}

.table-row {
  transition: background 0.15s ease;
}

.table-row:hover {
  background: rgba(0, 122, 255, 0.04);
}

.col-id {
  width: 80px;
}

.id-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 24px;
  padding: 0 8px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #86868b;
}

.col-name {
  min-width: 200px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f5f7 0%, #e8e8ed 100%);
  border-radius: 8px;
}

.file-icon svg {
  width: 20px;
  height: 20px;
  color: #86868b;
}

.file-name {
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
}

.col-type {
  width: 100px;
}

.type-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.type-tag.pdf {
  background: rgba(255, 59, 48, 0.1);
  color: #ff3b30;
}

.type-tag.docx, .type-tag.doc {
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
}

.col-date {
  width: 180px;
}

.date-text {
  font-size: 12px;
  color: #86868b;
}

.col-actions {
  width: 140px;
}

.action-group {
  display: flex;
  gap: 4px;
}

.table-btn {
  width: 32px;
  height: 32px;
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
  width: 16px;
  height: 16px;
}

.table-btn.view {
  color: #007aff;
}

.table-btn.view:hover {
  background: rgba(0, 122, 255, 0.1);
}

.table-btn.refresh {
  color: #ff9500;
}

.table-btn.refresh:hover {
  background: rgba(255, 149, 0, 0.1);
}

.table-btn.delete {
  color: #ff3b30;
}

.table-btn.delete:hover {
  background: rgba(255, 59, 48, 0.1);
}

.table-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinning {
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
  width: 580px;
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
  max-width: 90vw;
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

.modal-content.no-padding {
  padding: 0;
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

/* 按钮样式 */
.btn-secondary {
  padding: 8px 16px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  background: linear-gradient(180deg, #ffffff 0%, #f5f5f7 100%);
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-secondary:hover {
  background: linear-gradient(180deg, #f5f5f7 0%, #e8e8ed 100%);
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  background: linear-gradient(180deg, #007AFF 0%, #0066d6 100%);
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
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary .spinner {
  width: 14px;
  height: 14px;
  animation: spin 1s linear infinite;
}

/* 上传区域 */
.upload-area {
  padding: 40px 20px;
  border: 2px dashed rgba(0, 0, 0, 0.15);
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: rgba(0, 0, 0, 0.01);
}

.upload-area:hover {
  border-color: #007aff;
  background: rgba(0, 122, 255, 0.02);
}

.upload-area.drag-over {
  border-color: #007aff;
  background: rgba(0, 122, 255, 0.05);
}

.upload-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  color: #86868b;
}

.upload-icon svg {
  width: 100%;
  height: 100%;
}

.upload-text {
  font-size: 14px;
  color: #1d1d1f;
  margin-bottom: 8px;
}

.upload-text .link {
  color: #007aff;
  font-weight: 500;
}

.upload-hint {
  font-size: 12px;
  color: #86868b;
}

.selected-file {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(0, 122, 255, 0.05);
  border-radius: 8px;
}

.selected-file .file-icon {
  width: 24px;
  height: 24px;
  color: #007aff;
}

.selected-file .file-name {
  flex: 1;
  font-size: 13px;
  color: #1d1d1f;
}

.remove-file {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: #86868b;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.15s ease;
}

.remove-file:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #ff3b30;
}

.remove-file svg {
  width: 14px;
  height: 14px;
}

/* 简历详情样式 */
.resume-detail {
  max-height: 70vh;
  overflow-y: auto;
  padding: 24px;
}

.detail-section {
  margin-bottom: 28px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.section-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.section-icon svg {
  width: 18px;
  height: 18px;
}

.section-icon.personal {
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
}

.section-icon.education {
  background: rgba(88, 86, 214, 0.1);
  color: #5856d6;
}

.section-icon.work {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.section-icon.project {
  background: rgba(52, 199, 89, 0.1);
  color: #34c759;
}

.section-icon.skills {
  background: rgba(255, 59, 48, 0.1);
  color: #ff3b30;
}

.section-icon.awards {
  background: rgba(255, 204, 0, 0.1);
  color: #ffcc00;
}

.section-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px 24px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item .label {
  font-size: 11px;
  font-weight: 500;
  color: #86868b;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.info-item .value {
  font-size: 14px;
  color: #1d1d1f;
}

.info-item .value.link {
  color: #007aff;
  text-decoration: none;
}

.info-item .value.link:hover {
  text-decoration: underline;
}

/* 时间线 */
.timeline {
  position: relative;
  padding-left: 24px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 8px;
  bottom: 8px;
  width: 2px;
  background: rgba(0, 0, 0, 0.06);
  border-radius: 1px;
}

.timeline-item {
  position: relative;
  padding-bottom: 20px;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-dot {
  position: absolute;
  left: -20px;
  top: 6px;
  width: 10px;
  height: 10px;
  background: #007aff;
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.2);
}

.timeline-content {
  padding-left: 4px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 6px;
  flex-wrap: wrap;
  gap: 8px;
}

.timeline-header .title {
  font-size: 15px;
  font-weight: 600;
  color: #1d1d1f;
}

.timeline-header .title-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.timeline-header .position {
  font-size: 13px;
  color: #007aff;
  font-weight: 500;
}

.timeline-header .time {
  font-size: 12px;
  color: #86868b;
}

.timeline-info {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.timeline-info .major {
  font-size: 13px;
  color: #1d1d1f;
}

.timeline-info .degree {
  font-size: 13px;
  color: #86868b;
}

.description {
  font-size: 13px;
  color: #424245;
  line-height: 1.6;
  margin: 0 0 10px 0;
}

.achievements {
  margin: 0;
  padding-left: 18px;
  list-style: disc;
}

.achievements li {
  font-size: 13px;
  color: #424245;
  line-height: 1.6;
  margin-bottom: 4px;
}

/* 项目网格 */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.project-card {
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 10px;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.project-name {
  font-size: 14px;
  font-weight: 600;
  color: #1d1d1f;
}

.project-role {
  font-size: 12px;
  color: #5856d6;
  font-weight: 500;
}

.project-time {
  font-size: 11px;
  color: #86868b;
  margin-bottom: 10px;
}

.project-desc {
  font-size: 13px;
  color: #424245;
  line-height: 1.5;
  margin: 0 0 12px 0;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tech-tag {
  padding: 3px 8px;
  background: rgba(0, 122, 255, 0.08);
  color: #007aff;
  font-size: 11px;
  font-weight: 500;
  border-radius: 4px;
}

/* 技能云 */
.skills-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-chip {
  padding: 6px 14px;
  background: linear-gradient(135deg, rgba(0, 122, 255, 0.08) 0%, rgba(88, 86, 214, 0.08) 100%);
  border: 1px solid rgba(0, 122, 255, 0.15);
  border-radius: 20px;
  font-size: 13px;
  color: #1d1d1f;
  transition: all 0.2s ease;
}

.skill-chip:hover {
  background: linear-gradient(135deg, rgba(0, 122, 255, 0.12) 0%, rgba(88, 86, 214, 0.12) 100%);
  border-color: rgba(0, 122, 255, 0.3);
}

/* 荣誉列表 */
.highlights-list {
  margin: 0;
  padding-left: 18px;
  list-style: disc;
}

.highlights-list li {
  font-size: 13px;
  color: #424245;
  line-height: 1.8;
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

/* 滚动条样式 */
.resume-detail::-webkit-scrollbar,
.modal-content::-webkit-scrollbar {
  width: 8px;
}

.resume-detail::-webkit-scrollbar-track,
.modal-content::-webkit-scrollbar-track {
  background: transparent;
}

.resume-detail::-webkit-scrollbar-thumb,
.modal-content::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 4px;
}

.resume-detail::-webkit-scrollbar-thumb:hover,
.modal-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.25);
}

/* GitHub 风格简历模版样式 */
.resume-template {
  min-height: 600px;
  max-height: 75vh;
  overflow-y: auto;
  background: #ffffff;
  padding: 40px 50px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
  color: #24292e;
  line-height: 1.6;
}

.resume-section {
  margin-bottom: 30px;
}

.resume-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  color: #24292e;
  margin: 0 0 15px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #eaecef;
}

.section-marker {
  width: 4px;
  height: 18px;
  background: #0366d6;
  border-radius: 2px;
  margin-right: 10px;
  flex-shrink: 0;
}

.section-content {
  padding-left: 14px;
}

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
  color: #586069;
  min-width: 100px;
  flex-shrink: 0;
}

.info-value {
  color: #24292e;
  font-weight: 400;
}

.blog-link {
  color: #0366d6;
  text-decoration: none;
}

.blog-link:hover {
  text-decoration: underline;
}

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
  color: #24292e;
}

.edu-time {
  font-size: 13px;
  color: #586069;
}

.edu-details {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.edu-major {
  font-size: 14px;
  color: #24292e;
}

.edu-degree {
  font-size: 14px;
  color: #586069;
}

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
  color: #24292e;
}

.exp-position {
  font-size: 14px;
  color: #0366d6;
  font-weight: 500;
}

.exp-time {
  font-size: 13px;
  color: #586069;
  white-space: nowrap;
}

.exp-description {
  font-size: 14px;
  line-height: 1.8;
  color: #586069;
  margin-bottom: 10px;
  text-align: justify;
}

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
  color: #24292e;
}

.project-role {
  font-size: 14px;
  color: #6f42c1;
  font-weight: 500;
}

.project-time {
  font-size: 13px;
  color: #586069;
  white-space: nowrap;
}

.project-description {
  font-size: 14px;
  line-height: 1.8;
  color: #586069;
  margin-bottom: 10px;
  text-align: justify;
}

.achievements-list {
  margin: 10px 0;
  padding-left: 20px;
  list-style-type: disc;
}

.achievements-list li {
  font-size: 14px;
  line-height: 1.8;
  color: #586069;
  margin-bottom: 5px;
  text-align: justify;
}

.tech-stack {
  font-size: 13px;
  color: #586069;
  margin: 8px 0;
}

.tech-label {
  font-weight: 500;
  color: #586069;
}

.tech-value {
  color: #0366d6;
}

.skills-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.skill-tag {
  display: inline-block;
  padding: 6px 12px;
  background: #f1f8ff;
  border: 1px solid #c8e1ff;
  border-radius: 6px;
  font-size: 13px;
  color: #0366d6;
  font-weight: 400;
}

/* 简历模板滚动条 */
.resume-template::-webkit-scrollbar {
  width: 8px;
}

.resume-template::-webkit-scrollbar-track {
  background: #f6f8fa;
}

.resume-template::-webkit-scrollbar-thumb {
  background: #d1d5da;
  border-radius: 4px;
}

.resume-template::-webkit-scrollbar-thumb:hover {
  background: #959da5;
}
</style>

<template>
  <div class="knowledge">
    <el-row :gutter="20">
      <el-col :span="18">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>知识库文档</span>
              <div class="header-actions">
                <el-select
                  v-model="categoryFilter"
                  placeholder="筛选分类"
                  clearable
                  style="width: 150px; margin-right: 10px;"
                  @change="loadDocumentList"
                >
                  <el-option label="全部" value="" />
                  <el-option label="技术文档" value="技术文档" />
                  <el-option label="面试题" value="面试题" />
                  <el-option label="公司资料" value="公司资料" />
                  <el-option label="其他" value="其他" />
                </el-select>
                <el-button type="primary" @click="showUploadDialog = true">
                  <el-icon><Upload /></el-icon>
                  上传文档
                </el-button>
              </div>
            </div>
          </template>

          <el-table :data="documentList" v-loading="loading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="file_name" label="文件名" />
            <el-table-column prop="file_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag>{{ row.file_type.toUpperCase() }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="分类" width="120">
              <template #default="{ row }">
                <el-select
                  v-model="row.category"
                  size="small"
                  style="width: 100px;"
                  @change="handleCategoryChange(row)"
                >
                  <el-option label="未分类" value="" />
                  <el-option label="技术文档" value="技术文档" />
                  <el-option label="面试题" value="面试题" />
                  <el-option label="公司资料" value="公司资料" />
                  <el-option label="其他" value="其他" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="上传时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="handlePreview(row)">
                  预览
                </el-button>
                <el-button type="danger" size="small" @click="deleteDocument(row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>知识库查询</span>
              <el-tooltip content="清空历史" placement="top">
                <el-button
                  type="text"
                  size="small"
                  @click="handleClearHistory"
                  :disabled="queryHistory.length === 0"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </template>

          <el-input
            v-model="queryText"
            type="textarea"
            :rows="4"
            placeholder="输入问题查询知识库..."
          />
          <el-button
            type="primary"
            style="width: 100%; margin-top: 10px;"
            :loading="querying"
            @click="handleQuery"
          >
            查询
          </el-button>

          <el-divider />

          <!-- 查询历史 -->
          <div v-if="queryHistory.length > 0" class="query-history">
            <div class="history-header">
              <span>查询历史</span>
            </div>
            <div
              v-for="(item, index) in queryHistory"
              :key="index"
              class="history-item"
              @click="handleHistoryClick(item)"
            >
              {{ item }}
            </div>
            <el-divider />
          </div>

          <!-- 查询结果 -->
          <div v-if="queryResults.length > 0" class="query-results">
            <div
              v-for="(result, index) in queryResults"
              :key="index"
              class="result-item"
            >
              <div class="result-source">
                <el-icon><Document /></el-icon>
                {{ result.source }}
              </div>
              <div class="result-content" v-html="highlightText(result.content)"></div>
              <div class="result-score">
                相似度: {{ (result.score * 100).toFixed(1) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 上传对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传知识库文档" width="500px">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept=".pdf,.docx,.doc,.txt"
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 PDF、DOCX、DOC、TXT 格式
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

    <!-- 文档预览对话框 -->
    <el-dialog v-model="showPreviewDialog" :title="previewFileName" width="70%" top="5vh">
      <div v-loading="previewLoading" class="preview-content">
        <div v-html="previewContent" class="preview-text"></div>
      </div>
      <template #footer>
        <el-button @click="showPreviewDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getKnowledgeList,
  uploadKnowledge,
  queryKnowledge,
  deleteKnowledge,
  getDocumentPreview,
  updateDocumentCategory,
  getQueryHistory,
  clearQueryHistory
} from '@/api/knowledge'

const loading = ref(false)
const uploading = ref(false)
const querying = ref(false)
const showUploadDialog = ref(false)
const showPreviewDialog = ref(false)
const previewLoading = ref(false)
const uploadRef = ref(null)
const documentList = ref([])
const queryText = ref('')
const queryResults = ref([])
const queryHistory = ref([])
const selectedFile = ref(null)
const categoryFilter = ref('')
const previewContent = ref('')
const previewFileName = ref('')

// 加载文档列表
const loadDocumentList = async () => {
  loading.value = true
  try {
    const res = await getKnowledgeList()
    if (res.code === 200) {
      let docs = res.data || []
      // 根据分类筛选
      if (categoryFilter.value) {
        docs = docs.filter(doc => doc.category === categoryFilter.value)
      }
      documentList.value = docs
    }
  } catch (error) {
    console.error('加载文档列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载查询历史
const loadQueryHistory = async () => {
  try {
    const res = await getQueryHistory()
    if (res.code === 200) {
      queryHistory.value = res.data || []
    }
  } catch (error) {
    console.error('加载查询历史失败:', error)
  }
}

// 处理文件选择
const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

// 上传文档
const handleUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  uploading.value = true
  try {
    const res = await uploadKnowledge(selectedFile.value)
    if (res.code === 201) {
      ElMessage.success('上传成功')
      showUploadDialog.value = false
      selectedFile.value = null
      uploadRef.value?.clearFiles()
      loadDocumentList()
    }
  } catch (error) {
    console.error('上传失败:', error)
  } finally {
    uploading.value = false
  }
}

// 删除文档
const deleteDocument = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个文档吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const res = await deleteKnowledge(id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      loadDocumentList()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

// 预览文档
const handlePreview = async (doc) => {
  showPreviewDialog.value = true
  previewFileName.value = doc.file_name
  previewLoading.value = true
  previewContent.value = ''

  try {
    const res = await getDocumentPreview(doc.id)
    if (res.code === 200) {
      previewContent.value = res.data.content || '暂无预览内容'
    }
  } catch (error) {
    console.error('获取预览内容失败:', error)
    ElMessage.error('获取预览内容失败')
  } finally {
    previewLoading.value = false
  }
}

// 更新文档分类
const handleCategoryChange = async (row) => {
  try {
    const res = await updateDocumentCategory(row.id, row.category)
    if (res.code === 200) {
      ElMessage.success('分类更新成功')
    }
  } catch (error) {
    console.error('更新分类失败:', error)
    ElMessage.error('更新分类失败')
    // 恢复原值
    row.category = row._prevCategory || ''
  }
}

// 查询知识库
const handleQuery = async () => {
  if (!queryText.value.trim()) {
    ElMessage.warning('请输入查询内容')
    return
  }

  querying.value = true
  try {
    const res = await queryKnowledge({ query: queryText.value })
    if (res.code === 200) {
      queryResults.value = res.data.results || []
      if (queryResults.value.length === 0) {
        ElMessage.info('未找到相关内容')
      }
      // 保存到历史记录
      if (!queryHistory.value.includes(queryText.value)) {
        queryHistory.value.unshift(queryText.value)
        // 最多保留10条历史记录
        if (queryHistory.value.length > 10) {
          queryHistory.value = queryHistory.value.slice(0, 10)
        }
      }
    }
  } catch (error) {
    console.error('查询失败:', error)
  } finally {
    querying.value = false
  }
}

// 点击历史记录
const handleHistoryClick = (item) => {
  queryText.value = item
  handleQuery()
}

// 清空历史记录
const handleClearHistory = async () => {
  try {
    await ElMessageBox.confirm('确定要清空查询历史吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const res = await clearQueryHistory()
    if (res.code === 200) {
      queryHistory.value = []
      ElMessage.success('历史记录已清空')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空历史失败:', error)
    }
  }
}

// 高亮显示匹配文本
const highlightText = (text) => {
  if (!queryText.value || !text) return text
  const keywords = queryText.value.trim().split(/\s+/)
  let highlightedText = text

  keywords.forEach(keyword => {
    if (keyword) {
      const regex = new RegExp(`(${keyword})`, 'gi')
      highlightedText = highlightedText.replace(regex, '<mark class="highlight">$1</mark>')
    }
  })

  return highlightedText
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadDocumentList()
  loadQueryHistory()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.query-results {
  max-height: 400px;
  overflow-y: auto;
}

.query-history {
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 10px;
}

.history-header {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
  font-weight: 500;
}

.history-item {
  padding: 6px 10px;
  cursor: pointer;
  border-radius: 4px;
  font-size: 13px;
  color: #409EFF;
  transition: background-color 0.2s;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-item:hover {
  background-color: #f0f9ff;
}

.result-item {
  padding: 10px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 10px;
}

.result-source {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.result-content {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 5px;
}

.result-content :deep(.highlight) {
  background-color: #fff7b1;
  color: #e6a23c;
  padding: 0 2px;
  border-radius: 2px;
  font-weight: 500;
}

.result-score {
  font-size: 12px;
  color: #409EFF;
}

.preview-content {
  min-height: 400px;
  max-height: 600px;
  overflow-y: auto;
}

.preview-text {
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
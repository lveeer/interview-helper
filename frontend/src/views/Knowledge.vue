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
            <el-table-column prop="file_name" label="文件名" width="450" />
            <el-table-column prop="file_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag>{{ row.file_type.toUpperCase() }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="chunk_strategy" label="分段策略" width="120">
              <template #default="{ row }">
                <el-tag :type="getStrategyTagType(row.chunk_strategy)" size="small">
                  {{ getStrategyLabel(row.chunk_strategy) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="chunk_count" label="分段数" width="80">
              <template #default="{ row }">
                {{ row.chunk_count || 0 }}
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
            <el-table-column label="操作" width="230" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="handlePreview(row)">
                  预览
                </el-button>
                <el-button type="success" size="small" @click="openStrategyDialog(row)">
                  更改策略
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
      <div style="margin-top: 20px;">
        <label style="display: block; margin-bottom: 8px; font-weight: 500;">分段策略</label>
        <el-select v-model="chunkStrategy" style="width: 100%;" placeholder="选择分段策略">
          <el-option
            v-for="option in CHUNK_STRATEGY_OPTIONS"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          >
            <div>
              <span style="font-weight: 500;">{{ option.label }}</span>
              <div style="font-size: 12px; color: #909399; margin-top: 2px;">{{ option.description }}</div>
            </div>
          </el-option>
        </el-select>
        <div style="margin-top: 8px; font-size: 12px; color: #909399;">
          <el-icon><InfoFilled /></el-icon>
          推荐面试场景使用「父子分段」，保证上下文完整性
        </div>
      </div>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">
          上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 文档预览对话框 -->
    <el-dialog v-model="showPreviewDialog" :title="`${previewFileName} (${getStrategyLabel(previewChunkStrategy)})`" width="75%" top="5vh">
      <div v-loading="previewLoading" class="preview-wrapper">
        <!-- 预览统计信息 -->
        <div v-if="!previewLoading" class="preview-stats">
          <div class="stat-item">
            <el-icon><Document /></el-icon>
            <span>分段数: {{ totalChunks || previewChunks.length || 1 }}</span>
          </div>
          <div class="stat-item">
            <el-icon><InfoFilled /></el-icon>
            <span>策略: {{ getStrategyLabel(previewChunkStrategy) }}</span>
          </div>
        </div>

        <!-- 预览内容 -->
        <div class="preview-content">
          <div v-if="previewChunks.length > 0" class="preview-text">
            <div v-for="(chunk, index) in previewChunks" :key="index" class="chunk-item" :class="{ 'is-parent': !chunk.parent_chunk_id, 'is-child': chunk.parent_chunk_id }">
              <div class="chunk-header">
                <div class="chunk-title">
                  <span class="chunk-badge" :class="{ 'parent-badge': !chunk.parent_chunk_id, 'child-badge': chunk.parent_chunk_id }">
                    {{ !chunk.parent_chunk_id ? '父分段' : '子分段' }} {{ index + 1 }} / {{ previewChunks.length }}
                  </span>
                  <span v-if="chunk.parent_chunk_id" class="chunk-tag child-tag">
                    <el-icon><Connection /></el-icon>
                    属于父分段 #{{ chunk.parent_chunk_id }}
                  </span>
                  <span v-else class="chunk-tag parent-tag">
                    <el-icon><Files /></el-icon>
                    包含 {{ getChildChunkCount(chunk.id) }} 个子分段
                  </span>
                </div>
              </div>
              <div class="chunk-content">{{ chunk.content }}</div>
            </div>
          </div>
          <div v-else class="preview-text">{{ previewContent }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showPreviewDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 分段策略选择对话框 -->
    <el-dialog v-model="showStrategyDialog" title="更改分段策略" width="500px">
      <el-alert
        title="注意"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        更改分段策略将触发文档重新处理，可能需要一定时间
      </el-alert>
      <el-radio-group v-model="newChunkStrategy" style="width: 100%;">
        <div
          v-for="option in CHUNK_STRATEGY_OPTIONS"
          :key="option.value"
          style="margin-bottom: 15px; padding: 12px; border: 1px solid #e4e7ed; border-radius: 4px; cursor: pointer;"
          :class="{ 'selected-strategy': newChunkStrategy === option.value }"
          @click="newChunkStrategy = option.value"
        >
          <el-radio :value="option.value" style="margin-bottom: 8px;">
            <span style="font-weight: 500;">{{ option.label }}</span>
          </el-radio>
          <div style="font-size: 13px; color: #606266; margin-left: 24px;">{{ option.description }}</div>
        </div>
      </el-radio-group>
      <template #footer>
        <el-button @click="showStrategyDialog = false">取消</el-button>
        <el-button type="primary" :loading="updatingStrategy" @click="handleUpdateChunkStrategy">
          确认并重新处理
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { InfoFilled, Connection, Files } from '@element-plus/icons-vue'
import {
  getKnowledgeList,
  uploadKnowledge,
  queryKnowledge,
  deleteKnowledge,
  getDocumentPreview,
  updateDocumentCategory,
  getQueryHistory,
  clearQueryHistory,
  updateChunkStrategy,
  CHUNK_STRATEGY_OPTIONS
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
const chunkStrategy = ref('semantic')
const showStrategyDialog = ref(false)
const updatingStrategy = ref(false)
const selectedDoc = ref(null)
const newChunkStrategy = ref('semantic')
const previewChunkStrategy = ref('semantic')
const totalChunks = ref(0)
const previewChunks = ref([])

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
    const res = await uploadKnowledge(selectedFile.value, chunkStrategy.value)
    if (res.code === 201) {
      ElMessage.success('上传成功')
      showUploadDialog.value = false
      selectedFile.value = null
      uploadRef.value?.clearFiles()
      chunkStrategy.value = 'semantic'
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
  previewChunks.value = []
  totalChunks.value = 0

  try {
    const res = await getDocumentPreview(doc.id)
    if (res.code === 200) {
      const chunks = res.data.chunks || []
      const chunkTotal = res.data.total_chunks || 0
      const strategy = res.data.chunk_strategy || 'semantic'

      // 存储分段策略和总数用于显示
      previewChunkStrategy.value = strategy
      totalChunks.value = chunkTotal

      // 清理文本内容的函数
      const cleanContent = (text) => {
        if (!text) return ''

        // 第一步：移除所有字与字之间的空格（中文字符之间的空格）
        let cleaned = text.replace(/([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])/g, '$1$2')

        // 第二步：移除中文字符与标点符号之间的空格
        cleaned = cleaned.replace(/([\u4e00-\u9fa5])\s+([，。！？；：、])/g, '$1$2')
        cleaned = cleaned.replace(/([，。！？；：、])\s+([\u4e00-\u9fa5])/g, '$1$2')

        // 第三步：移除数字之间的空格
        cleaned = cleaned.replace(/(\d)\s+(\d)/g, '$1$2')

        // 第四步：移除字母之间的空格
        cleaned = cleaned.replace(/([a-zA-Z])\s+([a-zA-Z])/g, '$1$2')

        // 第五步：保留段落分隔（双换行），移除多余的空行
        cleaned = cleaned.replace(/\n\s*\n/g, '\n\n')

        // 第六步：移除行首行尾的空格
        cleaned = cleaned.split('\n').map(line => line.trim()).join('\n')

        return cleaned.trim()
      }

      // 格式化显示分段内容
      if (chunkTotal > 1) {
        // 有多个分段，使用 Vue 响应式数据
        previewChunks.value = chunks.map(chunk => ({
          ...chunk,
          content: cleanContent(chunk.content)
        }))
        previewContent.value = ''
      } else {
        // 单个分段或未分段，直接显示内容
        previewChunks.value = []
        previewContent.value = cleanContent(chunks[0]?.content) || '暂无预览内容'
      }
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

// 打开分段策略对话框
const openStrategyDialog = (doc) => {
  selectedDoc.value = doc
  newChunkStrategy.value = doc.chunk_strategy || 'semantic'
  showStrategyDialog.value = true
}

// 更新分段策略
const handleUpdateChunkStrategy = async () => {
  if (!selectedDoc.value) return

  updatingStrategy.value = true
  try {
    const res = await updateChunkStrategy(selectedDoc.value.id, newChunkStrategy.value)
    if (res.code === 200) {
      ElMessage.success('分段策略更新成功，文档正在重新处理')
      showStrategyDialog.value = false
      loadDocumentList()
    }
  } catch (error) {
    console.error('更新分段策略失败:', error)
    ElMessage.error('更新分段策略失败')
  } finally {
    updatingStrategy.value = false
  }
}

// 获取策略标签
const getStrategyLabel = (strategy) => {
  const option = CHUNK_STRATEGY_OPTIONS.find(opt => opt.value === strategy)
  return option ? option.label : strategy
}

// 获取策略标签类型
const getStrategyTagType = (strategy) => {
  switch (strategy) {
    case 'parent_child':
      return 'success'
    case 'recursive':
      return 'warning'
    case 'semantic':
    default:
      return 'info'
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

// 获取父分段的子分段数量
const getChildChunkCount = (parentId) => {
  return previewChunks.value.filter(chunk => chunk.parent_chunk_id === parentId).length
}

// 监听上传对话框关闭，重置状态
watch(showUploadDialog, (newVal) => {
  if (!newVal) {
    chunkStrategy.value = 'semantic'
    selectedFile.value = null
    uploadRef.value?.clearFiles()
  }
})

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

.preview-wrapper {
  background: #f0f2f5;
  border-radius: 12px;
  padding: 24px;
}

.preview-stats {
  display: flex;
  gap: 24px;
  padding: 16px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #ffffff;
  font-size: 15px;
  font-weight: 600;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.stat-item .el-icon {
  font-size: 20px;
}

.preview-content {
  min-height: 400px;
  max-height: 600px;
  overflow-y: auto;
  padding: 8px;
}

.preview-text {
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.selected-strategy {
  border-color: #409EFF !important;
  background-color: #f0f9ff;
}

.chunk-item {
  margin-bottom: 32px;
  padding: 0;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  position: relative;
}

.chunk-item.is-parent {
  border-color: #67C23A;
  margin-bottom: 40px;
}

.chunk-item.is-child {
  border-color: #E6A23C;
  margin-left: 30px;
  margin-bottom: 20px;
  margin-top: -10px;
  position: relative;
}

.chunk-item.is-child::before {
  content: '';
  position: absolute;
  left: -20px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #E6A23C;
  opacity: 0.5;
}

.chunk-item.is-child::after {
  content: '';
  position: absolute;
  left: -22px;
  top: 24px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #E6A23C;
  opacity: 0.7;
}

.chunk-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 5px;
  background: linear-gradient(180deg, #409EFF 0%, #66b1ff 100%);
  border-radius: 12px 0 0 12px;
  z-index: 1;
}

.chunk-item.is-parent::before {
  background: linear-gradient(180deg, #67C23A 0%, #85ce61 100%);
}

.chunk-item.is-child::before {
  background: linear-gradient(180deg, #E6A23C 0%, #ebb563 100%);
}

.chunk-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.chunk-item.is-parent:hover {
  border-color: #67C23A;
  box-shadow: 0 4px 16px rgba(103, 194, 58, 0.3);
}

.chunk-item.is-child:hover {
  border-color: #E6A23C;
  box-shadow: 0 4px 16px rgba(230, 162, 60, 0.3);
}

.chunk-item > * {
  margin: 0;
  padding: 0;
  position: relative;
  z-index: 2;
}

.chunk-header {
  padding: 16px 20px 16px 28px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  border-bottom: 2px solid #409EFF;
  margin: 0;
}

.chunk-item.is-parent .chunk-header {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-bottom: 2px solid #67C23A;
}

.chunk-item.is-child .chunk-header {
  background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
  border-bottom: 2px solid #E6A23C;
}

.chunk-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  padding: 0;
}

.chunk-badge {
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
  color: #ffffff;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 700;
  box-shadow: 0 3px 8px rgba(64, 158, 255, 0.35);
  white-space: nowrap;
  letter-spacing: 0.5px;
}

.chunk-badge.parent-badge {
  background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
  box-shadow: 0 3px 8px rgba(103, 194, 58, 0.35);
}

.chunk-badge.child-badge {
  background: linear-gradient(135deg, #E6A23C 0%, #ebb563 100%);
  box-shadow: 0 3px 8px rgba(230, 162, 60, 0.35);
}

.chunk-tag {
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 600;
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chunk-tag.parent-tag {
  background: #f0f9ff;
  color: #67C23A;
  border: 1px solid #b2e59d;
  box-shadow: 0 2px 4px rgba(103, 194, 58, 0.15);
}

.chunk-tag.child-tag {
  background: #fff7ed;
  color: #E6A23C;
  border: 1px solid #ffd591;
  box-shadow: 0 2px 4px rgba(230, 162, 60, 0.15);
}

.chunk-tag .el-icon {
  font-size: 16px;
}

.chunk-content {
  line-height: 2;
  color: #2c3e50;
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-word;
  font-size: 15px;
  padding: 20px;
  background: #ffffff;
  text-align: justify;
  text-justify: inter-ideograph;
}

.chunk-item.is-child .chunk-content {
  font-size: 14px;
  color: #5a4a3f;
  background: #fffbf0;
}

/* 滚动条美化 */
.preview-content::-webkit-scrollbar {
  width: 8px;
}

.preview-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.preview-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.preview-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
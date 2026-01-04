<template>
  <div class="knowledge">
    <el-row :gutter="20">
      <el-col :span="18">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>知识库文档</span>
              <el-button type="primary" @click="showUploadDialog = true">
                <el-icon><Upload /></el-icon>
                上传文档
              </el-button>
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
            <el-table-column prop="created_at" label="上传时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
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
            <span>知识库查询</span>
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
              <div class="result-content">{{ result.content }}</div>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getKnowledgeList, uploadKnowledge, queryKnowledge, deleteKnowledge } from '@/api/knowledge'

const loading = ref(false)
const uploading = ref(false)
const querying = ref(false)
const showUploadDialog = ref(false)
const uploadRef = ref(null)
const documentList = ref([])
const queryText = ref('')
const queryResults = ref([])
const selectedFile = ref(null)

const loadDocumentList = async () => {
  loading.value = true
  try {
    const res = await getKnowledgeList()
    if (res.code === 200) {
      documentList.value = res.data || []
    }
  } catch (error) {
    console.error('加载文档列表失败:', error)
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
    }
  } catch (error) {
    console.error('查询失败:', error)
  } finally {
    querying.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadDocumentList()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.query-results {
  max-height: 400px;
  overflow-y: auto;
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

.result-score {
  font-size: 12px;
  color: #409EFF;
}
</style>
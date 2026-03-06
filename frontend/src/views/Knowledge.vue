<template>
  <div class="knowledge-page">
    <div class="page-layout">
      <!-- 左侧：文档列表 -->
      <div class="main-section">
        <div class="macos-window">
          <div class="window-titlebar">
            <div class="window-title">
              <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
              </svg>
              <span>知识库文档</span>
            </div>
            <div class="window-actions">
              <div class="select-wrapper small">
                <select v-model="categoryFilter" @change="loadDocumentList" class="macos-select small">
                  <option value="">全部</option>
                  <option value="技术文档">技术文档</option>
                  <option value="面试题">面试题</option>
                  <option value="公司资料">公司资料</option>
                  <option value="其他">其他</option>
                </select>
                <svg class="select-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </div>
              <button class="action-btn warning" @click="goToRecallTest">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
                  <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
                </svg>
                <span>召回测试</span>
              </button>
              <button class="action-btn primary" @click="showUploadDialog = true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                <span>上传文档</span>
              </button>
            </div>
          </div>

          <div class="window-content">
            <div class="table-container" v-loading="loading">
              <table class="macos-table">
                <thead>
                  <tr>
                    <th class="col-id">ID</th>
                    <th class="col-name">文件名</th>
                    <th class="col-type">类型</th>
                    <th class="col-strategy">分段策略</th>
                    <th class="col-chunks">分段数</th>
                    <th class="col-category">分类</th>
                    <th class="col-date">上传时间</th>
                    <th class="col-actions">操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="doc in documentList" :key="doc.id" class="table-row">
                    <td class="col-id">
                      <span class="id-badge">{{ doc.id }}</span>
                    </td>
                    <td class="col-name">
                      <div class="file-info">
                        <div class="file-icon">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                          </svg>
                        </div>
                        <span class="file-name">{{ doc.file_name }}</span>
                      </div>
                    </td>
                    <td class="col-type">
                      <span class="type-tag" :class="doc.file_type?.toLowerCase()">
                        {{ doc.file_type?.toUpperCase() }}
                      </span>
                    </td>
                    <td class="col-strategy">
                      <span class="strategy-tag" :class="doc.chunk_strategy">
                        {{ getStrategyLabel(doc.chunk_strategy) }}
                      </span>
                    </td>
                    <td class="col-chunks">
                      <span class="chunk-count">{{ doc.chunk_count || 0 }}</span>
                    </td>
                    <td class="col-category">
                      <div class="select-wrapper small">
                        <select v-model="doc.category" class="macos-select small" @change="handleCategoryChange(doc)">
                          <option value="">未分类</option>
                          <option value="技术文档">技术文档</option>
                          <option value="面试题">面试题</option>
                          <option value="公司资料">公司资料</option>
                          <option value="其他">其他</option>
                        </select>
                        <svg class="select-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <polyline points="6 9 12 15 18 9"></polyline>
                        </svg>
                      </div>
                    </td>
                    <td class="col-date">
                      <span class="date-text">{{ formatDate(doc.created_at) }}</span>
                    </td>
                    <td class="col-actions">
                      <div class="action-group">
                        <button class="table-btn primary" @click="handlePreview(doc)" title="预览">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                            <circle cx="12" cy="12" r="3"></circle>
                          </svg>
                        </button>
                        <button class="table-btn success" @click="openStrategyDialog(doc)" title="更改策略">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="3"></circle>
                            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                          </svg>
                        </button>
                        <button class="table-btn danger" @click="deleteDocument(doc.id)" title="删除">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="documentList.length === 0 && !loading">
                    <td colspan="8" class="empty-cell">
                      <div class="empty-state">
                        <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                        </svg>
                        <p>暂无文档，点击上方按钮上传</p>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：查询面板 -->
      <div class="side-section">
        <div class="macos-window">
          <div class="window-titlebar">
            <div class="window-controls">
              <span class="control close"></span>
              <span class="control minimize"></span>
              <span class="control maximize"></span>
            </div>
            <div class="window-title">知识库查询</div>
            <button
              v-if="queryHistory.length > 0"
              class="action-btn ghost small"
              @click="handleClearHistory"
              title="清空历史"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
            </button>
          </div>

          <div class="window-content">
            <div class="query-section">
              <textarea
                v-model="queryText"
                class="query-textarea"
                rows="4"
                placeholder="输入问题查询知识库..."
              ></textarea>
              <button class="query-btn" :disabled="querying" @click="handleQuery">
                <svg v-if="!querying" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="11" cy="11" r="8"></circle>
                  <path d="m21 21-4.35-4.35"></path>
                </svg>
                <svg v-else class="spinning" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                </svg>
                <span>{{ querying ? '查询中...' : '查询' }}</span>
              </button>
            </div>

            <div class="divider"></div>

            <!-- 查询历史 -->
            <div v-if="queryHistory.length > 0" class="history-section">
              <div class="section-label">查询历史</div>
              <div class="history-list">
                <div
                  v-for="(item, index) in queryHistory"
                  :key="index"
                  class="history-item"
                  @click="handleHistoryClick(item)"
                >
                  {{ item }}
                </div>
              </div>
              <div class="divider"></div>
            </div>

            <!-- 查询结果 -->
            <div v-if="queryResults.length > 0" class="results-section">
              <div class="section-label">查询结果</div>
              <div class="results-list">
                <div v-for="(result, index) in queryResults" :key="index" class="result-card">
                  <div class="result-source">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                      <polyline points="14 2 14 8 20 8"></polyline>
                    </svg>
                    <span>{{ result.source }}</span>
                  </div>
                  <div class="result-content" v-html="highlightText(result.content)"></div>
                  <div class="result-score">
                    相似度: {{ (result.score * 100).toFixed(1) }}%
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传对话框 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showUploadDialog" class="modal-overlay" @click.self="showUploadDialog = false">
          <div class="modal-container">
            <div class="modal-titlebar">
              <div class="modal-controls">
                <span class="control close" @click="showUploadDialog = false"></span>
                <span class="control minimize"></span>
                <span class="control maximize"></span>
              </div>
              <span class="modal-title">上传知识库文档</span>
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
                  accept=".pdf,.docx,.doc,.txt"
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
                <p class="upload-hint">支持 PDF、DOCX、DOC、TXT 格式</p>
              </div>

              <div v-if="selectedFile" class="selected-file">
                <svg class="file-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <span class="file-name">{{ selectedFile.name }}</span>
                <button class="remove-file" @click.stop="clearSelectedFile">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>

              <div class="strategy-section">
                <label class="form-label">分段策略</label>
                <div class="select-wrapper">
                  <select v-model="chunkStrategy" class="macos-select">
                    <option v-for="option in CHUNK_STRATEGY_OPTIONS" :key="option.value" :value="option.value">
                      {{ option.label }}
                    </option>
                  </select>
                  <svg class="select-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="6 9 12 15 18 9"></polyline>
                  </svg>
                </div>
                <div class="strategy-hint">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="16" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12.01" y2="8"></line>
                  </svg>
                  <span>推荐面试场景使用「父子分段」，保证上下文完整性</span>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-secondary" @click="showUploadDialog = false">取消</button>
              <button class="btn-primary" :disabled="!selectedFile || uploading" @click="handleUpload">
                {{ uploading ? '上传中...' : '上传' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 文档预览对话框 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showPreviewDialog" class="modal-overlay" @click.self="showPreviewDialog = false">
          <div class="modal-container large">
            <div class="modal-titlebar">
              <div class="modal-controls">
                <span class="control close" @click="showPreviewDialog = false"></span>
                <span class="control minimize"></span>
                <span class="control maximize"></span>
              </div>
              <span class="modal-title">{{ previewFileName }} ({{ getStrategyLabel(previewChunkStrategy) }})</span>
            </div>
            <div class="modal-content no-padding">
              <div v-loading="previewLoading" class="preview-wrapper">
                <div v-if="!previewLoading" class="preview-stats">
                  <div class="stat-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                      <polyline points="14 2 14 8 20 8"></polyline>
                    </svg>
                    <span>分段数: {{ totalChunks || previewChunks.length || 1 }}</span>
                  </div>
                  <div class="stat-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10"></circle>
                      <line x1="12" y1="16" x2="12" y2="12"></line>
                      <line x1="12" y1="8" x2="12.01" y2="8"></line>
                    </svg>
                    <span>策略: {{ getStrategyLabel(previewChunkStrategy) }}</span>
                  </div>
                </div>

                <div class="preview-content">
                  <div v-if="previewChunks.length > 0" class="chunks-list">
                    <div
                      v-for="(chunk, index) in previewChunks"
                      :key="index"
                      class="chunk-item"
                      :class="{ parent: !chunk.parent_chunk_id, child: chunk.parent_chunk_id }"
                    >
                      <div class="chunk-header">
                        <span class="chunk-badge" :class="{ parent: !chunk.parent_chunk_id, child: chunk.parent_chunk_id }">
                          {{ !chunk.parent_chunk_id ? '父分段' : '子分段' }} {{ index + 1 }} / {{ previewChunks.length }}
                        </span>
                        <span v-if="chunk.parent_chunk_id" class="chunk-tag child">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                          </svg>
                          属于父分段 #{{ chunk.parent_chunk_id }}
                        </span>
                        <span v-else class="chunk-tag parent">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                          </svg>
                          包含 {{ getChildChunkCount(chunk.id) }} 个子分段
                        </span>
                      </div>
                      <div class="chunk-content">{{ chunk.content }}</div>
                    </div>
                  </div>
                  <div v-else class="preview-text">{{ previewContent }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 分段策略对话框 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showStrategyDialog" class="modal-overlay" @click.self="showStrategyDialog = false">
          <div class="modal-container">
            <div class="modal-titlebar">
              <div class="modal-controls">
                <span class="control close" @click="showStrategyDialog = false"></span>
                <span class="control minimize"></span>
                <span class="control maximize"></span>
              </div>
              <span class="modal-title">更改分段策略</span>
            </div>
            <div class="modal-content">
              <div class="warning-banner">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                  <line x1="12" y1="9" x2="12" y2="13"></line>
                  <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
                <span>更改分段策略将触发文档重新处理，可能需要一定时间</span>
              </div>

              <div class="strategy-options">
                <div
                  v-for="option in CHUNK_STRATEGY_OPTIONS"
                  :key="option.value"
                  class="strategy-option"
                  :class="{ selected: newChunkStrategy === option.value }"
                  @click="newChunkStrategy = option.value"
                >
                  <div class="strategy-radio">
                    <div class="radio-dot" :class="{ checked: newChunkStrategy === option.value }"></div>
                  </div>
                  <div class="strategy-info">
                    <span class="strategy-name">{{ option.label }}</span>
                    <span class="strategy-desc">{{ option.description }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-secondary" @click="showStrategyDialog = false">取消</button>
              <button class="btn-primary" :disabled="updatingStrategy" @click="handleUpdateChunkStrategy">
                确认并重新处理
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
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

const router = useRouter()
const loading = ref(false)
const uploading = ref(false)
const querying = ref(false)
const showUploadDialog = ref(false)
const showPreviewDialog = ref(false)
const previewLoading = ref(false)
const fileInput = ref(null)
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
const isDragOver = ref(false)

const loadDocumentList = async () => {
  loading.value = true
  try {
    const res = await getKnowledgeList()
    if (res.code === 200) {
      let docs = res.data || []
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
    const validTypes = ['.pdf', '.docx', '.doc', '.txt']
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
    if (validTypes.includes(ext)) {
      selectedFile.value = file
    } else {
      ElMessage.warning('请上传 PDF、DOCX、DOC 或 TXT 格式的文件')
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
    const res = await uploadKnowledge(selectedFile.value, chunkStrategy.value)
    if (res.code === 201) {
      ElMessage.success('上传成功')
      showUploadDialog.value = false
      clearSelectedFile()
      chunkStrategy.value = 'semantic'
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

      previewChunkStrategy.value = strategy
      totalChunks.value = chunkTotal

      const cleanContent = (text) => {
        if (!text) return ''
        let cleaned = text.replace(/([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])/g, '$1$2')
        cleaned = cleaned.replace(/([\u4e00-\u9fa5])\s+([，。！？；：、])/g, '$1$2')
        cleaned = cleaned.replace(/([，。！？；：、])\s+([\u4e00-\u9fa5])/g, '$1$2')
        cleaned = cleaned.replace(/(\d)\s+(\d)/g, '$1$2')
        cleaned = cleaned.replace(/([a-zA-Z])\s+([a-zA-Z])/g, '$1$2')
        cleaned = cleaned.replace(/\n\s*\n/g, '\n\n')
        cleaned = cleaned.split('\n').map(line => line.trim()).join('\n')
        return cleaned.trim()
      }

      if (chunkTotal > 1) {
        previewChunks.value = chunks.map(chunk => ({
          ...chunk,
          content: cleanContent(chunk.content)
        }))
        previewContent.value = ''
      } else {
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

const handleCategoryChange = async (row) => {
  try {
    const res = await updateDocumentCategory(row.id, row.category)
    if (res.code === 200) {
      ElMessage.success('分类更新成功')
    }
  } catch (error) {
    console.error('更新分类失败:', error)
    ElMessage.error('更新分类失败')
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
      if (!queryHistory.value.includes(queryText.value)) {
        queryHistory.value.unshift(queryText.value)
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

const handleHistoryClick = (item) => {
  queryText.value = item
  handleQuery()
}

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

const openStrategyDialog = (doc) => {
  selectedDoc.value = doc
  newChunkStrategy.value = doc.chunk_strategy || 'semantic'
  showStrategyDialog.value = true
}

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

const goToRecallTest = () => {
  router.push('/recall-test')
}

const getStrategyLabel = (strategy) => {
  const option = CHUNK_STRATEGY_OPTIONS.find(opt => opt.value === strategy)
  return option ? option.label : strategy
}

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

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const getChildChunkCount = (parentId) => {
  return previewChunks.value.filter(chunk => chunk.parent_chunk_id === parentId).length
}

watch(showUploadDialog, (newVal) => {
  if (!newVal) {
    chunkStrategy.value = 'semantic'
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
})

onMounted(() => {
  loadDocumentList()
  loadQueryHistory()
})
</script>

<style scoped>
/* 页面容器 */
.knowledge-page {
  padding: 24px;
  min-height: 100%;
  background: linear-gradient(180deg, #f5f5f7 0%, #ffffff 100%);
}

.page-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
  height: calc(100vh - 120px);
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
  display: flex;
  flex-direction: column;
}

.window-titlebar {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(180deg, #f6f6f6 0%, #e8e8e8 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  user-select: none;
  flex-shrink: 0;
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
  align-items: center;
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

.action-btn.warning {
  background: linear-gradient(180deg, #FF9500 0%, #e08000 100%);
  color: white;
}

.action-btn.ghost {
  background: transparent;
  color: #86868b;
  padding: 6px 8px;
}

.action-btn.ghost:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #1d1d1f;
}

.action-btn.ghost.small {
  padding: 4px 6px;
}

.action-btn.ghost.small svg {
  width: 12px;
  height: 12px;
}

.window-content {
  padding: 16px;
  overflow-y: auto;
  flex: 1;
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
  padding: 10px 12px;
  font-size: 11px;
  font-weight: 600;
  color: #86868b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-align: left;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  white-space: nowrap;
}

.macos-table td {
  padding: 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  vertical-align: middle;
}

.table-row {
  transition: background 0.15s ease;
}

.table-row:hover {
  background: rgba(0, 122, 255, 0.04);
}

.col-id { width: 50px; }
.col-type { width: 60px; }
.col-strategy { width: 80px; }
.col-chunks { width: 60px; }
.col-category { width: 100px; }
.col-date { width: 140px; }
.col-actions { width: 110px; }

.id-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 20px;
  padding: 0 6px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 5px;
  font-size: 11px;
  font-weight: 500;
  color: #86868b;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f5f7 0%, #e8e8ed 100%);
  border-radius: 6px;
}

.file-icon svg {
  width: 16px;
  height: 16px;
  color: #86868b;
}

.file-name {
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
}

.type-tag {
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  border-radius: 5px;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.type-tag.pdf { background: rgba(255, 59, 48, 0.1); color: #ff3b30; }
.type-tag.docx, .type-tag.doc { background: rgba(0, 122, 255, 0.1); color: #007aff; }
.type-tag.txt { background: rgba(142, 142, 147, 0.1); color: #8e8e93; }

.strategy-tag {
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  border-radius: 5px;
  font-size: 10px;
  font-weight: 500;
}

.strategy-tag.parent_child { background: rgba(52, 199, 89, 0.1); color: #34c759; }
.strategy-tag.recursive { background: rgba(255, 149, 0, 0.1); color: #ff9500; }
.strategy-tag.semantic { background: rgba(0, 122, 255, 0.1); color: #007aff; }

.chunk-count {
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
}

.date-text {
  font-size: 12px;
  color: #86868b;
}

.action-group {
  display: flex;
  gap: 3px;
}

.table-btn {
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 5px;
  background: transparent;
  cursor: pointer;
  transition: all 0.15s ease;
}

.table-btn svg {
  width: 14px;
  height: 14px;
}

.table-btn.primary { color: #007aff; }
.table-btn.primary:hover { background: rgba(0, 122, 255, 0.1); }

.table-btn.success { color: #34c759; }
.table-btn.success:hover { background: rgba(52, 199, 89, 0.1); }

.table-btn.danger { color: #ff3b30; }
.table-btn.danger:hover { background: rgba(255, 59, 48, 0.1); }

/* 选择器样式 */
.select-wrapper {
  position: relative;
}

.select-wrapper.small {
  width: auto;
}

.macos-select {
  padding: 6px 28px 6px 10px;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  font-size: 12px;
  color: #1d1d1f;
  cursor: pointer;
  appearance: none;
  transition: all 0.15s ease;
}

.macos-select.small {
  padding: 4px 24px 4px 8px;
  font-size: 11px;
}

.macos-select:hover {
  border-color: rgba(0, 0, 0, 0.2);
}

.macos-select:focus {
  outline: none;
  border-color: #007aff;
}

.select-arrow {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 12px;
  height: 12px;
  color: #86868b;
  pointer-events: none;
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

/* 查询面板 */
.query-section {
  margin-bottom: 16px;
}

.query-textarea {
  width: 100%;
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.5;
  color: #1d1d1f;
  resize: none;
  transition: all 0.15s ease;
  font-family: inherit;
}

.query-textarea::placeholder {
  color: #86868b;
}

.query-textarea:focus {
  outline: none;
  border-color: #007aff;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.query-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  margin-top: 10px;
  background: linear-gradient(180deg, #007AFF 0%, #0066d6 100%);
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: white;
  cursor: pointer;
  transition: all 0.15s ease;
}

.query-btn:hover:not(:disabled) {
  background: linear-gradient(180deg, #0084ff 0%, #0070e6 100%);
}

.query-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.query-btn svg {
  width: 16px;
  height: 16px;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.divider {
  height: 1px;
  background: rgba(0, 0, 0, 0.06);
  margin: 16px 0;
}

.section-label {
  font-size: 11px;
  font-weight: 600;
  color: #86868b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}

.history-section {
  margin-bottom: 8px;
}

.history-list {
  max-height: 120px;
  overflow-y: auto;
}

.history-item {
  padding: 8px 10px;
  cursor: pointer;
  border-radius: 6px;
  font-size: 12px;
  color: #007aff;
  transition: background 0.15s ease;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-item:hover {
  background: rgba(0, 122, 255, 0.06);
}

.results-section {
  margin-top: 8px;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 300px;
  overflow-y: auto;
}

.result-card {
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.result-source {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #86868b;
  margin-bottom: 6px;
}

.result-source svg {
  width: 12px;
  height: 12px;
}

.result-content {
  font-size: 12px;
  line-height: 1.6;
  color: #424245;
  margin-bottom: 6px;
}

.result-content :deep(.highlight) {
  background: rgba(255, 204, 0, 0.3);
  color: #c67a00;
  padding: 0 2px;
  border-radius: 2px;
}

.result-score {
  font-size: 11px;
  color: #007aff;
  font-weight: 500;
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

.btn-secondary {
  padding: 8px 20px;
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-secondary:hover {
  background: rgba(0, 0, 0, 0.08);
}

.btn-primary {
  padding: 8px 20px;
  background: linear-gradient(180deg, #007AFF 0%, #0066d6 100%);
  border: none;
  border-radius: 8px;
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
  opacity: 0.5;
  cursor: not-allowed;
}

/* 上传区域 */
.upload-area {
  padding: 32px 20px;
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
  width: 40px;
  height: 40px;
  margin: 0 auto 12px;
  color: #86868b;
}

.upload-icon svg {
  width: 100%;
  height: 100%;
}

.upload-text {
  font-size: 13px;
  color: #1d1d1f;
  margin-bottom: 6px;
}

.upload-text .link {
  color: #007aff;
  font-weight: 500;
}

.upload-hint {
  font-size: 11px;
  color: #86868b;
}

.selected-file {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 16px;
  padding: 10px 14px;
  background: rgba(0, 122, 255, 0.05);
  border-radius: 8px;
}

.selected-file .file-icon {
  width: 20px;
  height: 20px;
  color: #007aff;
}

.selected-file .file-name {
  flex: 1;
  font-size: 13px;
  color: #1d1d1f;
}

.remove-file {
  width: 22px;
  height: 22px;
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
  width: 12px;
  height: 12px;
}

.strategy-section {
  margin-top: 20px;
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

.strategy-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  font-size: 11px;
  color: #86868b;
}

.strategy-hint svg {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

/* 预览区域 */
.preview-wrapper {
  padding: 20px;
}

.preview-stats {
  display: flex;
  gap: 16px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  font-size: 13px;
  font-weight: 500;
}

.stat-item svg {
  width: 16px;
  height: 16px;
}

.preview-content {
  max-height: 500px;
  overflow-y: auto;
}

.chunks-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chunk-item {
  padding: 16px;
  border-radius: 10px;
  border: 2px solid rgba(0, 0, 0, 0.06);
}

.chunk-item.parent {
  border-color: rgba(52, 199, 89, 0.3);
  background: rgba(52, 199, 89, 0.02);
}

.chunk-item.child {
  border-color: rgba(255, 149, 0, 0.3);
  background: rgba(255, 149, 0, 0.02);
  margin-left: 20px;
}

.chunk-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.chunk-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.chunk-badge.parent {
  background: rgba(52, 199, 89, 0.15);
  color: #34c759;
}

.chunk-badge.child {
  background: rgba(255, 149, 0, 0.15);
  color: #ff9500;
}

.chunk-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.chunk-tag.parent {
  background: rgba(52, 199, 89, 0.08);
  color: #2d8a4e;
}

.chunk-tag.child {
  background: rgba(255, 149, 0, 0.08);
  color: #c67a00;
}

.chunk-tag svg {
  width: 12px;
  height: 12px;
}

.chunk-content {
  font-size: 13px;
  line-height: 1.8;
  color: #424245;
  white-space: pre-wrap;
}

.preview-text {
  font-size: 13px;
  line-height: 1.8;
  color: #424245;
  white-space: pre-wrap;
}

/* 警告横幅 */
.warning-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(255, 149, 0, 0.08);
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 12px;
  color: #c67a00;
}

.warning-banner svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.strategy-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.strategy-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  border: 2px solid rgba(0, 0, 0, 0.06);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.strategy-option:hover {
  border-color: rgba(0, 122, 255, 0.3);
}

.strategy-option.selected {
  border-color: #007aff;
  background: rgba(0, 122, 255, 0.04);
}

.strategy-radio {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(0, 0, 0, 0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.radio-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: transparent;
  transition: all 0.15s ease;
}

.radio-dot.checked {
  background: #007aff;
}

.strategy-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.strategy-name {
  font-size: 14px;
  font-weight: 500;
  color: #1d1d1f;
}

.strategy-desc {
  font-size: 12px;
  color: #86868b;
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

/* 滚动条 */
.window-content::-webkit-scrollbar,
.results-list::-webkit-scrollbar,
.history-list::-webkit-scrollbar,
.preview-content::-webkit-scrollbar {
  width: 6px;
}

.window-content::-webkit-scrollbar-track,
.results-list::-webkit-scrollbar-track,
.history-list::-webkit-scrollbar-track,
.preview-content::-webkit-scrollbar-track {
  background: transparent;
}

.window-content::-webkit-scrollbar-thumb,
.results-list::-webkit-scrollbar-thumb,
.history-list::-webkit-scrollbar-thumb,
.preview-content::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
}
</style>

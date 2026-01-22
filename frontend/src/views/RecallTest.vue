<template>
  <div class="recall-test">
    <el-row :gutter="20">
      <el-col :span="18">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>召回测试用例</span>
              <el-button type="primary" @click="showCreateDialog = true">
                <el-icon><Plus /></el-icon>
                创建测试用例
              </el-button>
            </div>
          </template>

          <el-table :data="testCases" v-loading="loading" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="query" label="查询语句" min-width="300" show-overflow-tooltip />
            <el-table-column label="期望分段" width="150">
              <template #default="{ row }">
                <el-tag size="small">{{ row.expected_chunk_ids.length }} 个</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="280" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="openRunDialog(row)">
                  运行测试
                </el-button>
                <el-button type="info" size="small" @click="viewResults(row)">
                  查看结果
                </el-button>
                <el-button type="danger" size="small" @click="deleteTestCase(row.id)">
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
              <span>测试汇总</span>
            </div>
          </template>

          <div class="summary-stats">
            <div class="stat-item">
              <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ summary.total_tests }}</div>
                <div class="stat-label">总测试数</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ summary.avg_recall }}%</div>
                <div class="stat-label">平均召回率</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <el-icon><Aim /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ summary.avg_precision }}%</div>
                <div class="stat-label">平均精确率</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <el-icon><Trophy /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ summary.avg_f1_score }}%</div>
                <div class="stat-label">平均 F1 分数</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                <el-icon><Medal /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ summary.avg_mrr }}%</div>
                <div class="stat-label">平均 MRR</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建测试用例对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建召回测试用例" width="600px">
      <el-form :model="newCase" label-width="120px">
        <el-form-item label="查询语句" required>
          <el-input
            v-model="newCase.query"
            type="textarea"
            :rows="3"
            placeholder="输入测试查询语句"
          />
        </el-form-item>
        <el-form-item label="期望分段 ID" required>
          <el-input
            v-model="expectedChunkIdsStr"
            placeholder="输入分段 ID，用逗号分隔，如: 1,2,3"
          />
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            可以在知识库页面预览文档获取分段 ID
          </div>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="newCase.description"
            placeholder="输入测试用例描述（可选）"
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

    <!-- 运行测试对话框 -->
    <el-dialog v-model="showRunDialog" title="运行召回测试" width="600px">
      <el-form :model="testConfig" label-width="140px">
        <el-form-item label="召回数量">
          <el-input-number v-model="testConfig.top_k" :min="1" :max="20" />
        </el-form-item>
        <el-form-item label="查询扩展">
          <el-switch v-model="testConfig.use_query_expansion" />
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            启用查询扩展可以提高召回效果
          </div>
        </el-form-item>
        <el-form-item label="混合检索">
          <el-switch v-model="testConfig.use_hybrid_search" />
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            同时使用语义检索和关键词检索
          </div>
        </el-form-item>
        <el-form-item label="重排序">
          <el-switch v-model="testConfig.use_reranking" />
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            对召回结果进行重新排序，提升精确度
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRunDialog = false">取消</el-button>
        <el-button type="primary" :loading="running" @click="handleRunTest">
          运行测试
        </el-button>
      </template>
    </el-dialog>

    <!-- 测试结果对话框 -->
    <el-dialog v-model="showResultsDialog" title="测试结果详情" width="900px">
      <div v-if="selectedResults.length > 0" class="results-container">
        <div v-for="result in selectedResults" :key="result.id" class="result-card">
          <div class="result-header">
            <span class="result-id">测试结果 #{{ result.id }}</span>
            <span class="result-time">{{ formatDate(result.created_at) }}</span>
          </div>
          <el-divider />
          <div class="result-stats">
            <div class="stat-box">
              <span class="stat-label">召回率</span>
              <span class="stat-value recall">{{ result.recall }}%</span>
            </div>
            <div class="stat-box">
              <span class="stat-label">精确率</span>
              <span class="stat-value precision">{{ result.precision }}%</span>
            </div>
            <div class="stat-box">
              <span class="stat-label">F1 分数</span>
              <span class="stat-value f1">{{ result.f1_score }}%</span>
            </div>
            <div class="stat-box">
              <span class="stat-label">MRR</span>
              <span class="stat-value mrr">{{ result.mrr }}%</span>
            </div>
          </div>
          <el-divider />
          <div class="result-charts">
            <div class="chart-item">
              <span class="chart-label">召回分段 ID:</span>
              <el-tag
                v-for="(chunkId, index) in result.retrieved_chunk_ids"
                :key="chunkId"
                size="small"
                style="margin-right: 8px; margin-bottom: 8px;"
              >
                #{{ chunkId }} ({{ (result.retrieved_scores[index] * 100).toFixed(1) }}%)
              </el-tag>
            </div>
            <div class="chart-item">
              <span class="chart-label">配置:</span>
              <el-tag size="small" type="info">Top-K: {{ result.top_k }}</el-tag>
              <el-tag v-if="result.use_query_expansion" size="small" type="success">查询扩展</el-tag>
              <el-tag v-if="result.use_hybrid_search" size="small" type="warning">混合检索</el-tag>
              <el-tag v-if="result.use_reranking" size="small" type="danger">重排序</el-tag>
            </div>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无测试结果" />
      <template #footer>
        <el-button @click="showResultsDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, InfoFilled, DataAnalysis, TrendCharts, Aim, Trophy, Medal } from '@element-plus/icons-vue'
import {
  createTestCase,
  getTestCases,
  deleteTestCase as deleteTestCaseApi,
  runRecallTest,
  getTestResults,
  getTestSummary
} from '@/api/recallTest'

const loading = ref(false)
const creating = ref(false)
const running = ref(false)
const showCreateDialog = ref(false)
const showRunDialog = ref(false)
const showResultsDialog = ref(false)

const testCases = ref([])
const summary = ref({
  total_tests: 0,
  avg_recall: 0,
  avg_precision: 0,
  avg_f1_score: 0,
  avg_mrr: 0,
  results: []
})

const newCase = ref({
  query: '',
  expected_chunk_ids: [],
  description: ''
})

const expectedChunkIdsStr = ref('')

const testConfig = ref({
  test_case_id: null,
  top_k: 5,
  use_query_expansion: true,
  use_hybrid_search: true,
  use_reranking: true
})

const selectedResults = ref([])

// 加载测试用例
const loadTestCases = async () => {
  loading.value = true
  try {
    const res = await getTestCases()
    if (res.code === 200) {
      testCases.value = res.data || []
    }
  } catch (error) {
    console.error('加载测试用例失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载汇总统计
const loadSummary = async () => {
  try {
    const res = await getTestSummary()
    if (res.code === 200) {
      summary.value = res.data || {
        total_tests: 0,
        avg_recall: 0,
        avg_precision: 0,
        avg_f1_score: 0,
        avg_mrr: 0,
        results: []
      }
    }
  } catch (error) {
    console.error('加载汇总统计失败:', error)
  }
}

// 创建测试用例
const handleCreate = async () => {
  if (!newCase.value.query.trim()) {
    ElMessage.warning('请输入查询语句')
    return
  }
  if (!expectedChunkIdsStr.value.trim()) {
    ElMessage.warning('请输入期望分段 ID')
    return
  }

  newCase.value.expected_chunk_ids = expectedChunkIdsStr.value
    .split(',')
    .map(id => parseInt(id.trim()))
    .filter(id => !isNaN(id))

  if (newCase.value.expected_chunk_ids.length === 0) {
    ElMessage.warning('期望分段 ID 格式不正确')
    return
  }

  creating.value = true
  try {
    const res = await createTestCase(newCase.value)
    if (res.code === 201) {
      ElMessage.success('创建成功')
      showCreateDialog.value = false
      newCase.value = { query: '', expected_chunk_ids: [], description: '' }
      expectedChunkIdsStr.value = ''
      loadTestCases()
    }
  } catch (error) {
    console.error('创建测试用例失败:', error)
  } finally {
    creating.value = false
  }
}

// 删除测试用例
const deleteTestCase = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个测试用例吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const res = await deleteTestCaseApi(id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      loadTestCases()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除测试用例失败:', error)
    }
  }
}

// 打开运行测试对话框
const openRunDialog = (testCase) => {
  testConfig.value.test_case_id = testCase.id
  testConfig.value.top_k = 5
  testConfig.value.use_query_expansion = true
  testConfig.value.use_hybrid_search = true
  testConfig.value.use_reranking = true
  showRunDialog.value = true
}

// 运行测试
const handleRunTest = async () => {
  running.value = true
  try {
    const res = await runRecallTest(testConfig.value)
    if (res.code === 201) {
      ElMessage.success('测试执行成功')
      showRunDialog.value = false
      loadSummary()
    }
  } catch (error) {
    console.error('运行测试失败:', error)
  } finally {
    running.value = false
  }
}

// 查看结果
const viewResults = async (testCase) => {
  try {
    const res = await getTestResults(testCase.id)
    if (res.code === 200) {
      selectedResults.value = res.data || []
      showResultsDialog.value = true
    }
  } catch (error) {
    console.error('获取测试结果失败:', error)
  }
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadTestCases()
  loadSummary()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.stat-icon .el-icon {
  font-size: 28px;
  color: #ffffff;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.form-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
}

.form-tip .el-icon {
  font-size: 14px;
}

.results-container {
  max-height: 600px;
  overflow-y: auto;
}

.result-card {
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 20px;
  background: #fafafa;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-id {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.result-time {
  font-size: 13px;
  color: #909399;
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin: 16px 0;
}

.stat-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.stat-box .stat-label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.stat-box .stat-value {
  font-size: 24px;
  font-weight: 700;
}

.stat-box .stat-value.recall {
  color: #f093fb;
}

.stat-box .stat-value.precision {
  color: #4facfe;
}

.stat-box .stat-value.f1 {
  color: #43e97b;
}

.stat-box .stat-value.mrr {
  color: #fa709a;
}

.result-charts {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chart-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  min-width: 100px;
}

/* 滚动条美化 */
.results-container::-webkit-scrollbar {
  width: 8px;
}

.results-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.results-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.results-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
<template>
  <div class="prompt-config-page">
    <!-- 页面头部 - macOS 风格 -->
    <header class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="title-group">
            <h1 class="page-title">配置中心</h1>
            <p class="page-subtitle">Prompt 模板管理 · 版本控制 · A/B 测试</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button class="action-btn secondary" @click="handleInitFromFiles" :loading="initLoading">
            <el-icon><Upload /></el-icon>
            从文件导入
          </el-button>
          <el-button class="action-btn primary" type="primary" @click="handleCreateConfig">
            <el-icon><Plus /></el-icon>
            新建配置
          </el-button>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 左侧配置列表 -->
      <aside class="config-sidebar">
        <div class="sidebar-header">
          <h3>配置列表</h3>
          <div class="filter-group">
            <el-select v-model="filterCategory" placeholder="全部分类" clearable size="small">
              <el-option
                v-for="cat in CONFIG_CATEGORIES"
                :key="cat.value"
                :label="cat.label"
                :value="cat.value"
              />
            </el-select>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索配置..."
              clearable
              size="small"
              class="search-input"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>

        <div class="config-list" v-loading="listLoading">
          <el-empty v-if="configList.length === 0" description="暂无配置" :image-size="60" />
          <TransitionGroup name="list" tag="div" class="list-container">
            <div
              v-for="config in filteredConfigList"
              :key="config.id"
              class="config-card"
              :class="{ active: selectedConfig?.id === config.id }"
              @click="handleSelectConfig(config)"
            >
              <div class="card-main">
                <div class="card-header">
                  <span class="config-name">{{ config.display_name || config.name }}</span>
                  <el-tag v-if="config.enable_ab_test" size="small" type="success" effect="dark" class="ab-badge">
                    A/B
                  </el-tag>
                </div>
                <div class="card-footer">
                  <el-tag size="small" :type="getCategoryType(config.category)" effect="plain">
                    {{ getCategoryLabel(config.category) }}
                  </el-tag>
                  <span class="version-count">
                    <el-icon><Document /></el-icon>
                    {{ config.version_count || 0 }}
                  </span>
                </div>
              </div>
              <div class="card-indicator"></div>
            </div>
          </TransitionGroup>
        </div>
      </aside>

      <!-- 右侧详情面板 -->
      <section class="detail-panel" v-loading="detailLoading">
        <template v-if="selectedConfig">
          <!-- 配置概览卡片 -->
          <div class="overview-card">
            <div class="overview-header">
              <div class="overview-title">
                <h2>{{ selectedConfig.display_name || selectedConfig.name }}</h2>
                <el-tag :type="selectedConfig.is_active ? 'success' : 'info'" size="small" effect="light">
                  {{ selectedConfig.is_active ? '已启用' : '已禁用' }}
                </el-tag>
              </div>
              <el-dropdown trigger="click" class="more-dropdown">
                <button class="more-btn">
                  <el-icon><MoreFilled /></el-icon>
                </button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="handleEditConfig">
                      <el-icon><Edit /></el-icon>编辑配置
                    </el-dropdown-item>
                    <el-dropdown-item @click="handleDeleteConfig" divided>
                      <el-icon><Delete /></el-icon>删除配置
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
            <div class="overview-meta">
              <div class="meta-item">
                <span class="meta-label">配置标识</span>
                <span class="meta-value code">{{ selectedConfig.name }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">标签</span>
                <span class="meta-value">{{ selectedConfig.tags || '-' }}</span>
              </div>
              <div class="meta-item full">
                <span class="meta-label">描述</span>
                <span class="meta-value">{{ selectedConfig.description || '-' }}</span>
              </div>
            </div>
          </div>

          <!-- Tabs 内容区 -->
          <div class="content-tabs-wrapper">
            <div class="tabs-nav">
              <button
                class="tab-btn"
                :class="{ active: activeTab === 'versions' }"
                @click="activeTab = 'versions'"
              >
                <el-icon><Document /></el-icon>
                版本管理
              </button>
              <button
                class="tab-btn"
                :class="{ active: activeTab === 'abtest' }"
                @click="activeTab = 'abtest'"
              >
                <el-icon><DataLine /></el-icon>
                A/B 测试
              </button>
            </div>

            <!-- 版本管理 -->
            <div v-show="activeTab === 'versions'" class="tab-content">
              <div class="tab-header">
                <span class="tab-title">版本列表</span>
                <el-button type="primary" size="small" @click="handleCreateVersion">
                  <el-icon><Plus /></el-icon>
                  新建版本
                </el-button>
              </div>
              <el-table
                :data="versionList"
                style="width: 100%"
                v-loading="versionLoading"
                class="mac-table"
              >
                <el-table-column prop="version" label="版本" width="100">
                  <template #default="{ row }">
                    <span class="version-tag">{{ row.version }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="change_log" label="变更说明" min-width="200" show-overflow-tooltip />
                <el-table-column label="状态" width="90" align="center">
                  <template #default="{ row }">
                    <span class="status-badge" :class="row.is_published ? 'published' : 'draft'">
                      {{ row.is_published ? '已发布' : '草稿' }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="usage_count" label="使用" width="70" align="center" />
                <el-table-column prop="avg_score" label="评分" width="70" align="center">
                  <template #default="{ row }">
                    <span v-if="row.avg_score != null" class="score">{{ row.avg_score.toFixed(1) }}</span>
                    <span v-else class="muted">-</span>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="60" align="center">
                  <template #default="{ row }">
                    <el-dropdown trigger="click">
                      <button class="action-trigger">
                        <el-icon><Operation /></el-icon>
                      </button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item @click="handleViewVersion(row)">
                            <el-icon><View /></el-icon>查看详情
                          </el-dropdown-item>
                          <el-dropdown-item v-if="!row.is_published" @click="handleEditVersion(row)">
                            <el-icon><Edit /></el-icon>编辑
                          </el-dropdown-item>
                          <el-dropdown-item v-if="!row.is_published" @click="handlePublishVersion(row)">
                            <el-icon><Promotion /></el-icon>发布
                          </el-dropdown-item>
                          <el-dropdown-item
                            v-if="row.id !== selectedConfig.active_version_id"
                            @click="handleActivateVersion(row)"
                          >
                            <el-icon><CircleCheck /></el-icon>激活
                          </el-dropdown-item>
                          <el-dropdown-item v-if="!row.is_published" @click="handleDeleteVersion(row)" divided>
                            <el-icon class="danger"><Delete /></el-icon>删除
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- A/B 测试 -->
            <div v-show="activeTab === 'abtest'" class="tab-content">
              <div class="tab-header">
                <span class="tab-title">实验列表</span>
                <el-button type="primary" size="small" @click="handleCreateABTest">
                  <el-icon><Plus /></el-icon>
                  新建测试
                </el-button>
              </div>
              <el-table
                :data="abTestList"
                style="width: 100%"
                v-loading="abTestLoading"
                class="mac-table"
              >
                <el-table-column prop="name" label="测试名称" min-width="150" />
                <el-table-column label="状态" width="100" align="center">
                  <template #default="{ row }">
                    <span class="status-badge" :class="getABTestStatusClass(row.status)">
                      {{ AB_TEST_STATUS_LABELS[row.status] || row.status }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column label="流量" width="80" align="center">
                  <template #default="{ row }">
                    <span class="traffic-ratio">{{ (row.traffic_ratio * 100).toFixed(0) }}%</span>
                  </template>
                </el-table-column>
                <el-table-column label="样本" width="140" align="center">
                  <template #default="{ row }">
                    <span class="sample-count">
                      <span class="control">{{ row.control_samples }}</span>
                      <span class="divider">/</span>
                      <span class="experiment">{{ row.experiment_samples }}</span>
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="start_time" label="开始时间" width="150">
                  <template #default="{ row }">
                    {{ row.start_time ? formatTime(row.start_time) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="60" align="center">
                  <template #default="{ row }">
                    <el-dropdown trigger="click">
                      <button class="action-trigger">
                        <el-icon><Operation /></el-icon>
                      </button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item @click="handleViewABTest(row)">
                            <el-icon><View /></el-icon>查看详情
                          </el-dropdown-item>
                          <template v-if="row.status === 'draft'">
                            <el-dropdown-item @click="handleStartABTest(row)">
                              <el-icon><VideoPlay /></el-icon>开始测试
                            </el-dropdown-item>
                            <el-dropdown-item @click="handleDeleteABTest(row)" divided>
                              <el-icon class="danger"><Delete /></el-icon>删除
                            </el-dropdown-item>
                          </template>
                          <template v-if="row.status === 'running'">
                            <el-dropdown-item @click="handlePauseABTest(row)">
                              <el-icon><VideoPause /></el-icon>暂停
                            </el-dropdown-item>
                            <el-dropdown-item @click="handleCompleteABTest(row)">
                              <el-icon><CircleCheck /></el-icon>完成
                            </el-dropdown-item>
                          </template>
                          <template v-if="row.status === 'paused'">
                            <el-dropdown-item @click="handleResumeABTest(row)">
                              <el-icon><VideoPlay /></el-icon>恢复
                            </el-dropdown-item>
                            <el-dropdown-item @click="handleCompleteABTest(row)">
                              <el-icon><CircleCheck /></el-icon>完成
                            </el-dropdown-item>
                          </template>
                          <el-dropdown-item v-if="row.status === 'completed'" @click="handleViewStatistics(row)">
                            <el-icon><DataAnalysis /></el-icon>查看统计
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </template>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <div class="empty-icon">
            <el-icon :size="56"><Setting /></el-icon>
          </div>
          <h3>选择一个配置</h3>
          <p>从左侧列表中选择一个配置查看详情</p>
        </div>
      </section>
    </main>

    <!-- 创建/编辑配置对话框 -->
    <el-dialog
      v-model="configDialogVisible"
      :title="configForm.id ? '编辑配置' : '新建配置'"
      width="540px"
      :close-on-click-modal="false"
      class="mac-dialog"
    >
      <el-form ref="configFormRef" :model="configForm" :rules="configRules" label-width="100px" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="配置名称" prop="name">
              <el-input v-model="configForm.name" placeholder="唯一标识" :disabled="!!configForm.id" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="显示名称" prop="display_name">
              <el-input v-model="configForm.display_name" placeholder="友好名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="分类" prop="category">
              <el-select v-model="configForm.category" placeholder="请选择" style="width: 100%">
                <el-option
                  v-for="cat in CONFIG_CATEGORIES"
                  :key="cat.value"
                  :label="cat.label"
                  :value="cat.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="启用状态" prop="is_active">
              <el-switch v-model="configForm.is_active" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="标签" prop="tags">
          <el-input v-model="configForm.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="configForm.description" type="textarea" :rows="2" placeholder="配置描述" />
        </el-form-item>
        <template v-if="!configForm.id">
          <el-form-item label="初始内容" prop="initial_content">
            <el-input v-model="configForm.initial_content" type="textarea" :rows="4" placeholder="初始 Prompt 内容" />
          </el-form-item>
          <el-form-item label="初始版本" prop="initial_version">
            <el-input v-model="configForm.initial_version" placeholder="如：v1.0.0" />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="configDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveConfig" :loading="saveConfigLoading">保存</el-button>
      </template>
    </el-dialog>

    <!-- 创建/编辑版本对话框 -->
    <el-dialog
      v-model="versionDialogVisible"
      :title="versionForm.id ? '编辑版本' : '新建版本'"
      width="640px"
      :close-on-click-modal="false"
      class="mac-dialog"
    >
      <el-form ref="versionFormRef" :model="versionForm" :rules="versionRules" label-width="100px" label-position="top">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="版本号" prop="version">
              <el-input v-model="versionForm.version" placeholder="v1.1.0" :disabled="!!versionForm.id" />
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="变更说明" prop="change_log">
              <el-input v-model="versionForm.change_log" placeholder="本次版本的变更说明" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Prompt 内容" prop="content">
          <el-input
            v-model="versionForm.content"
            type="textarea"
            :rows="12"
            placeholder="Prompt 内容"
            class="code-editor"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="versionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveVersion" :loading="saveVersionLoading">保存</el-button>
      </template>
    </el-dialog>

    <!-- 查看版本内容对话框 -->
    <el-dialog v-model="viewVersionDialogVisible" title="版本详情" width="640px" class="mac-dialog">
      <div class="version-detail">
        <div class="detail-header">
          <div class="detail-row">
            <span class="label">版本号</span>
            <span class="value version-tag">{{ viewVersionData.version }}</span>
          </div>
          <div class="detail-row">
            <span class="label">状态</span>
            <span class="status-badge" :class="viewVersionData.is_published ? 'published' : 'draft'">
              {{ viewVersionData.is_published ? '已发布' : '草稿' }}
            </span>
          </div>
        </div>
        <div class="detail-stats">
          <div class="stat-item">
            <span class="stat-value">{{ viewVersionData.usage_count || 0 }}</span>
            <span class="stat-label">使用次数</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ viewVersionData.avg_score?.toFixed(1) || '-' }}</span>
            <span class="stat-label">平均评分</span>
          </div>
        </div>
        <div class="detail-content">
          <h4>变更说明</h4>
          <p>{{ viewVersionData.change_log || '无' }}</p>
        </div>
        <div class="detail-content">
          <h4>Prompt 内容</h4>
          <pre class="code-block">{{ viewVersionData.content }}</pre>
        </div>
      </div>
    </el-dialog>

    <!-- 创建/编辑 A/B 测试对话框 -->
    <el-dialog
      v-model="abTestDialogVisible"
      :title="abTestForm.id ? '编辑 A/B 测试' : '新建 A/B 测试'"
      width="540px"
      :close-on-click-modal="false"
      class="mac-dialog"
    >
      <el-form ref="abTestFormRef" :model="abTestForm" :rules="abTestRules" label-width="100px" label-position="top">
        <el-form-item label="测试名称" prop="name">
          <el-input v-model="abTestForm.name" placeholder="如：问题生成优化测试" />
        </el-form-item>
        <el-form-item label="测试描述" prop="description">
          <el-input v-model="abTestForm.description" type="textarea" :rows="2" placeholder="测试目的和预期效果" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="对照组版本" prop="control_version_id">
              <el-select v-model="abTestForm.control_version_id" placeholder="选择版本" style="width: 100%">
                <el-option
                  v-for="v in publishedVersions"
                  :key="v.id"
                  :label="v.version"
                  :value="v.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实验组版本" prop="experiment_version_id">
              <el-select v-model="abTestForm.experiment_version_id" placeholder="选择版本" style="width: 100%">
                <el-option
                  v-for="v in publishedVersions"
                  :key="v.id"
                  :label="v.version"
                  :value="v.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="实验组流量比例">
          <el-slider v-model="abTestForm.traffic_ratio" :min="0" :max="100" :format-tooltip="(val) => val + '%'" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="开始时间" prop="start_time">
              <el-date-picker
                v-model="abTestForm.start_time"
                type="datetime"
                placeholder="选择时间"
                value-format="YYYY-MM-DDTHH:mm:ssZ"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间" prop="end_time">
              <el-date-picker
                v-model="abTestForm.end_time"
                type="datetime"
                placeholder="选择时间"
                value-format="YYYY-MM-DDTHH:mm:ssZ"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="abTestDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveABTest" :loading="saveABTestLoading">保存</el-button>
      </template>
    </el-dialog>

    <!-- A/B 测试统计对话框 -->
    <el-dialog v-model="statisticsDialogVisible" title="A/B 测试统计" width="460px" class="mac-dialog">
      <div class="statistics-content" v-if="statisticsData">
        <div class="stats-grid">
          <div class="stats-card">
            <span class="stats-value">{{ statisticsData.total_samples }}</span>
            <span class="stats-label">总样本数</span>
          </div>
          <div class="stats-card">
            <span class="stats-value">{{ statisticsData.control_samples }}</span>
            <span class="stats-label">对照组样本</span>
          </div>
          <div class="stats-card">
            <span class="stats-value">{{ statisticsData.experiment_samples }}</span>
            <span class="stats-label">实验组样本</span>
          </div>
          <div class="stats-card">
            <span class="stats-value">{{ statisticsData.control_avg_score?.toFixed(1) || '-' }}</span>
            <span class="stats-label">对照组评分</span>
          </div>
          <div class="stats-card">
            <span class="stats-value">{{ statisticsData.experiment_avg_score?.toFixed(1) || '-' }}</span>
            <span class="stats-label">实验组评分</span>
          </div>
          <div class="stats-card highlight">
            <span class="stats-value" :class="statisticsData.improvement_rate >= 0 ? 'positive' : 'negative'">
              {{ statisticsData.improvement_rate >= 0 ? '+' : '' }}{{ statisticsData.improvement_rate?.toFixed(2) }}%
            </span>
            <span class="stats-label">提升比例</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Upload, Setting, Document, MoreFilled, Edit, Delete,
  View, Promotion, CircleCheck, Operation, VideoPlay, VideoPause, DataAnalysis, DataLine
} from '@element-plus/icons-vue'
import {
  CONFIG_CATEGORIES,
  AB_TEST_STATUS_LABELS,
  getConfigList,
  getConfigDetail,
  createConfig,
  updateConfig,
  deleteConfig,
  activateVersion,
  getVersionList,
  getVersionDetail,
  createVersion,
  updateVersion,
  publishVersion,
  deleteVersion,
  getABTestList,
  getABTestDetail,
  createABTest,
  updateABTest,
  changeABTestStatus,
  deleteABTest,
  getABTestStatistics,
  initFromFiles
} from '@/api/promptConfig'

// 当前激活的 Tab
const activeTab = ref('versions')

// 列表状态
const listLoading = ref(false)
const configList = ref([])
const selectedConfig = ref(null)
const detailLoading = ref(false)

// 筛选
const filterCategory = ref('')
const searchKeyword = ref('')

// 配置对话框
const configDialogVisible = ref(false)
const configFormRef = ref(null)
const saveConfigLoading = ref(false)
const configForm = ref({
  name: '',
  display_name: '',
  category: '',
  tags: '',
  description: '',
  is_active: true,
  initial_content: '',
  initial_version: 'v1.0.0'
})

const configRules = {
  name: [{ required: true, message: '请输入配置名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }]
}

// 版本管理
const versionLoading = ref(false)
const versionList = ref([])
const versionDialogVisible = ref(false)
const versionFormRef = ref(null)
const saveVersionLoading = ref(false)
const versionForm = ref({
  version: '',
  content: '',
  change_log: ''
})

const versionRules = {
  version: [{ required: true, message: '请输入版本号', trigger: 'blur' }],
  content: [{ required: true, message: '请输入 Prompt 内容', trigger: 'blur' }]
}

// 查看版本
const viewVersionDialogVisible = ref(false)
const viewVersionData = ref({})

// A/B 测试
const abTestLoading = ref(false)
const abTestList = ref([])
const abTestDialogVisible = ref(false)
const abTestFormRef = ref(null)
const saveABTestLoading = ref(false)
const abTestForm = ref({
  name: '',
  description: '',
  control_version_id: null,
  experiment_version_id: null,
  traffic_ratio: 50,
  start_time: '',
  end_time: ''
})

const abTestRules = {
  name: [{ required: true, message: '请输入测试名称', trigger: 'blur' }],
  control_version_id: [{ required: true, message: '请选择对照组版本', trigger: 'change' }],
  experiment_version_id: [{ required: true, message: '请选择实验组版本', trigger: 'change' }]
}

// 统计
const statisticsDialogVisible = ref(false)
const statisticsData = ref(null)

// 初始化
const initLoading = ref(false)

// 计算属性
const filteredConfigList = computed(() => {
  let list = configList.value
  if (filterCategory.value) {
    list = list.filter(c => c.category === filterCategory.value)
  }
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    list = list.filter(c =>
      c.name.toLowerCase().includes(keyword) ||
      (c.display_name && c.display_name.toLowerCase().includes(keyword))
    )
  }
  return list
})

const publishedVersions = computed(() => {
  return versionList.value.filter(v => v.is_published)
})

// 方法
const getCategoryLabel = (category) => {
  const cat = CONFIG_CATEGORIES.find(c => c.value === category)
  return cat ? cat.label : category
}

const getCategoryType = (category) => {
  const typeMap = {
    interview: 'primary',
    resume: 'success',
    evaluation: 'warning',
    rag: 'info',
    game: 'danger',
    other: ''
  }
  return typeMap[category] || ''
}

const getABTestStatusClass = (status) => {
  const classMap = {
    draft: 'draft',
    running: 'running',
    paused: 'paused',
    completed: 'completed',
    archived: 'draft'
  }
  return classMap[status] || ''
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

// 加载配置列表
const loadConfigList = async () => {
  listLoading.value = true
  try {
    const res = await getConfigList({ page_size: 100 })
    configList.value = res.data || []
  } catch (error) {
    ElMessage.error('加载配置列表失败')
  } finally {
    listLoading.value = false
  }
}

// 选择配置
const handleSelectConfig = async (config) => {
  selectedConfig.value = config
  await loadVersionList()
  await loadABTestList()
}

// 加载版本列表
const loadVersionList = async () => {
  if (!selectedConfig.value) return
  versionLoading.value = true
  try {
    const res = await getVersionList(selectedConfig.value.id)
    versionList.value = res.data || []
  } catch (error) {
    ElMessage.error('加载版本列表失败')
  } finally {
    versionLoading.value = false
  }
}

// 加载 A/B 测试列表
const loadABTestList = async () => {
  if (!selectedConfig.value) return
  abTestLoading.value = true
  try {
    const res = await getABTestList(selectedConfig.value.id)
    abTestList.value = res.data || []
  } catch (error) {
    ElMessage.error('加载 A/B 测试列表失败')
  } finally {
    abTestLoading.value = false
  }
}

// 创建配置
const handleCreateConfig = () => {
  configForm.value = {
    name: '',
    display_name: '',
    category: '',
    tags: '',
    description: '',
    is_active: true,
    initial_content: '',
    initial_version: 'v1.0.0'
  }
  configDialogVisible.value = true
}

// 编辑配置
const handleEditConfig = () => {
  configForm.value = {
    id: selectedConfig.value.id,
    name: selectedConfig.value.name,
    display_name: selectedConfig.value.display_name || '',
    category: selectedConfig.value.category,
    tags: selectedConfig.value.tags || '',
    description: selectedConfig.value.description || '',
    is_active: selectedConfig.value.is_active
  }
  configDialogVisible.value = true
}

// 保存配置
const handleSaveConfig = async () => {
  if (!configFormRef.value) return
  try {
    await configFormRef.value.validate()
  } catch {
    return
  }

  saveConfigLoading.value = true
  try {
    if (configForm.value.id) {
      await updateConfig(configForm.value.id, {
        display_name: configForm.value.display_name,
        category: configForm.value.category,
        tags: configForm.value.tags,
        description: configForm.value.description,
        is_active: configForm.value.is_active
      })
      ElMessage.success('配置更新成功')
    } else {
      await createConfig(configForm.value)
      ElMessage.success('配置创建成功')
    }
    configDialogVisible.value = false
    await loadConfigList()
  } catch (error) {
    ElMessage.error(configForm.value.id ? '更新配置失败' : '创建配置失败')
  } finally {
    saveConfigLoading.value = false
  }
}

// 删除配置
const handleDeleteConfig = async () => {
  try {
    await ElMessageBox.confirm('确定要删除此配置吗？删除后无法恢复。', '确认删除', {
      type: 'warning'
    })
    await deleteConfig(selectedConfig.value.id)
    ElMessage.success('删除成功')
    selectedConfig.value = null
    await loadConfigList()
  } catch {
    // 用户取消
  }
}

// 创建版本
const handleCreateVersion = () => {
  versionForm.value = {
    version: '',
    content: '',
    change_log: ''
  }
  versionDialogVisible.value = true
}

// 查看版本
const handleViewVersion = async (version) => {
  try {
    const res = await getVersionDetail(version.id)
    viewVersionData.value = res.data
    viewVersionDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取版本详情失败')
  }
}

// 编辑版本
const handleEditVersion = async (version) => {
  try {
    const res = await getVersionDetail(version.id)
    versionForm.value = {
      id: res.data.id,
      version: res.data.version,
      content: res.data.content,
      change_log: res.data.change_log || ''
    }
    versionDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取版本详情失败')
  }
}

// 保存版本
const handleSaveVersion = async () => {
  if (!versionFormRef.value) return
  try {
    await versionFormRef.value.validate()
  } catch {
    return
  }

  saveVersionLoading.value = true
  try {
    if (versionForm.value.id) {
      await updateVersion(versionForm.value.id, {
        content: versionForm.value.content,
        change_log: versionForm.value.change_log
      })
      ElMessage.success('版本更新成功')
    } else {
      await createVersion(selectedConfig.value.id, versionForm.value)
      ElMessage.success('版本创建成功')
    }
    versionDialogVisible.value = false
    await loadVersionList()
  } catch (error) {
    ElMessage.error(versionForm.value.id ? '更新版本失败' : '创建版本失败')
  } finally {
    saveVersionLoading.value = false
  }
}

// 发布版本
const handlePublishVersion = async (version) => {
  try {
    await ElMessageBox.confirm(`确定要发布版本 ${version.version} 吗？`, '确认发布', {
      type: 'info'
    })
    await publishVersion(version.id)
    ElMessage.success('发布成功')
    await loadVersionList()
  } catch {
    // 用户取消
  }
}

// 激活版本
const handleActivateVersion = async (version) => {
  try {
    await ElMessageBox.confirm(`确定要将 ${version.version} 设为激活版本吗？`, '确认激活', {
      type: 'info'
    })
    await activateVersion(selectedConfig.value.id, version.id)
    ElMessage.success('激活成功')
    await loadConfigList()
    const current = configList.value.find(c => c.id === selectedConfig.value.id)
    if (current) {
      selectedConfig.value = current
    }
  } catch {
    // 用户取消
  }
}

// 删除版本
const handleDeleteVersion = async (version) => {
  try {
    await ElMessageBox.confirm(`确定要删除版本 ${version.version} 吗？`, '确认删除', {
      type: 'warning'
    })
    await deleteVersion(version.id)
    ElMessage.success('删除成功')
    await loadVersionList()
  } catch {
    // 用户取消
  }
}

// 创建 A/B 测试
const handleCreateABTest = () => {
  abTestForm.value = {
    name: '',
    description: '',
    control_version_id: null,
    experiment_version_id: null,
    traffic_ratio: 50,
    start_time: '',
    end_time: ''
  }
  abTestDialogVisible.value = true
}

// 查看 A/B 测试详情
const handleViewABTest = async (test) => {
  try {
    const res = await getABTestDetail(test.id)
    abTestForm.value = {
      id: res.data.id,
      name: res.data.name,
      description: res.data.description || '',
      control_version_id: res.data.control_version_id,
      experiment_version_id: res.data.experiment_version_id,
      traffic_ratio: (res.data.traffic_ratio || 0.5) * 100,
      start_time: res.data.start_time || '',
      end_time: res.data.end_time || ''
    }
    abTestDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取测试详情失败')
  }
}

// 保存 A/B 测试
const handleSaveABTest = async () => {
  if (!abTestFormRef.value) return
  try {
    await abTestFormRef.value.validate()
  } catch {
    return
  }

  saveABTestLoading.value = true
  try {
    const data = {
      ...abTestForm.value,
      traffic_ratio: abTestForm.value.traffic_ratio / 100
    }
    if (abTestForm.value.id) {
      await updateABTest(abTestForm.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await createABTest(selectedConfig.value.id, data)
      ElMessage.success('创建成功')
    }
    abTestDialogVisible.value = false
    await loadABTestList()
  } catch (error) {
    ElMessage.error(abTestForm.value.id ? '更新失败' : '创建失败')
  } finally {
    saveABTestLoading.value = false
  }
}

// 开始 A/B 测试
const handleStartABTest = async (test) => {
  try {
    await ElMessageBox.confirm('确定要开始此 A/B 测试吗？', '确认开始', { type: 'info' })
    await changeABTestStatus(test.id, 'running')
    ElMessage.success('测试已开始')
    await loadABTestList()
  } catch {
    // 用户取消
  }
}

// 暂停 A/B 测试
const handlePauseABTest = async (test) => {
  try {
    await changeABTestStatus(test.id, 'paused')
    ElMessage.success('测试已暂停')
    await loadABTestList()
  } catch {
    ElMessage.error('暂停失败')
  }
}

// 恢复 A/B 测试
const handleResumeABTest = async (test) => {
  try {
    await changeABTestStatus(test.id, 'running')
    ElMessage.success('测试已恢复')
    await loadABTestList()
  } catch {
    ElMessage.error('恢复失败')
  }
}

// 完成 A/B 测试
const handleCompleteABTest = async (test) => {
  try {
    await ElMessageBox.confirm('确定要结束此 A/B 测试吗？', '确认结束', { type: 'warning' })
    await changeABTestStatus(test.id, 'completed')
    ElMessage.success('测试已完成')
    await loadABTestList()
  } catch {
    // 用户取消
  }
}

// 查看统计
const handleViewStatistics = async (test) => {
  try {
    const res = await getABTestStatistics(test.id)
    statisticsData.value = res.data
    statisticsDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  }
}

// 删除 A/B 测试
const handleDeleteABTest = async (test) => {
  try {
    await ElMessageBox.confirm('确定要删除此 A/B 测试吗？', '确认删除', { type: 'warning' })
    await deleteABTest(test.id)
    ElMessage.success('删除成功')
    await loadABTestList()
  } catch {
    // 用户取消
  }
}

// 从文件导入
const handleInitFromFiles = async () => {
  try {
    await ElMessageBox.confirm('将从 prompts/ 目录导入配置，是否继续？', '确认导入', { type: 'info' })
    initLoading.value = true
    const res = await initFromFiles()
    ElMessage.success(`成功导入 ${res.data?.imported_count || 0} 个配置`)
    await loadConfigList()
  } catch {
    // 用户取消或错误
  } finally {
    initLoading.value = false
  }
}

onMounted(() => {
  loadConfigList()
})
</script>

<style scoped>
/* ============================================
   macOS 风格设计系统
   ============================================ */

/* 页面容器 - 浅色背景 */
.prompt-config-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f0f3 0%, #f5f5f7 100%);
  color: #1d1d1f;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', 'PingFang SC', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ============================================
   页面头部
   ============================================ */
.page-header {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.1);
  padding: 20px 28px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1440px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.page-title {
  font-size: 26px;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.5px;
  color: #1d1d1f;
}

.page-subtitle {
  margin: 0;
  font-size: 13px;
  color: #86868b;
  letter-spacing: -0.1px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  padding: 9px 18px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 13px;
  transition: all 0.2s cubic-bezier(0.25, 0.1, 0.25, 1);
  letter-spacing: -0.1px;
}

.action-btn.secondary {
  background: #ffffff;
  border: none;
  color: #1d1d1f;
  box-shadow: 
    0 1px 2px rgba(0, 0, 0, 0.04),
    0 0 0 1px rgba(0, 0, 0, 0.08);
}

.action-btn.secondary:hover {
  background: #f5f5f7;
  box-shadow: 
    0 2px 4px rgba(0, 0, 0, 0.06),
    0 0 0 1px rgba(0, 0, 0, 0.12);
}

.action-btn.primary {
  background: linear-gradient(180deg, #3b9eff 0%, #0071e3 100%);
  border: none;
  color: #ffffff;
  box-shadow: 
    0 1px 2px rgba(0, 113, 227, 0.2),
    0 2px 6px rgba(0, 113, 227, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.action-btn.primary:hover {
  background: linear-gradient(180deg, #4da6ff 0%, #0077ed 100%);
  box-shadow: 
    0 2px 4px rgba(0, 113, 227, 0.3),
    0 4px 12px rgba(0, 113, 227, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

/* ============================================
   主内容区
   ============================================ */
.main-content {
  max-width: 1440px;
  margin: 0 auto;
  padding: 20px 28px;
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
  min-height: calc(100vh - 90px);
}

/* ============================================
   左侧边栏 - Finder 风格
   ============================================ */
.config-sidebar {
  background: #ffffff;
  border-radius: 12px;
  border: none;
  box-shadow: 
    0 1px 3px rgba(0, 0, 0, 0.04),
    0 4px 12px rgba(0, 0, 0, 0.06),
    inset 0 0.5px 0 rgba(255, 255, 255, 0.8);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: fit-content;
  max-height: calc(100vh - 140px);
  position: sticky;
  top: 110px;
}

.sidebar-header {
  padding: 16px 16px 12px;
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.06);
}

.sidebar-header h3 {
  margin: 0 0 12px 0;
  font-size: 13px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.1px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group :deep(.el-input__wrapper),
.filter-group :deep(.el-select__wrapper) {
  background: #f5f5f7;
  border: 1px solid transparent;
  box-shadow: none;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.filter-group :deep(.el-input__wrapper:hover),
.filter-group :deep(.el-select__wrapper:hover) {
  background: #e8e8ed;
}

.filter-group :deep(.el-input__wrapper:focus-within),
.filter-group :deep(.el-select__wrapper:focus-within) {
  background: #ffffff;
  border-color: #0071e3;
  box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.1);
}

.filter-group :deep(.el-input__inner) {
  color: #1d1d1f;
  font-size: 13px;
}

.filter-group :deep(.el-input__prefix) {
  color: #86868b;
}

/* 配置列表 */
.config-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.config-list :deep(.el-empty) {
  padding: 40px 0;
}

.config-list :deep(.el-empty__description) {
  color: #86868b;
  font-size: 13px;
}

.list-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.config-card {
  position: relative;
  padding: 12px 14px;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.25, 0.1, 0.25, 1);
  border: 1px solid transparent;
}

.config-card:hover {
  background: rgba(0, 0, 0, 0.03);
  transform: translateX(2px);
}

.config-card.active {
  background: linear-gradient(135deg, rgba(0, 113, 227, 0.08) 0%, rgba(0, 113, 227, 0.04) 100%);
  border-color: rgba(0, 113, 227, 0.25);
  box-shadow: 0 2px 8px rgba(0, 113, 227, 0.1);
}

.config-card.active .card-indicator {
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 3px;
  background: #0071e3;
  border-radius: 0 2px 2px 0;
}

.card-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.config-name {
  font-weight: 500;
  font-size: 13px;
  color: #1d1d1f;
  letter-spacing: -0.1px;
}

.ab-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-footer :deep(.el-tag) {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
}

.version-count {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  color: #86868b;
}

.version-count .el-icon {
  font-size: 12px;
}

/* 列表过渡动画 */
.list-enter-active,
.list-leave-active {
  transition: all 0.25s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.list-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

/* ============================================
   右侧详情面板
   ============================================ */
.detail-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 概览卡片 */
.overview-card {
  background: #ffffff;
  border-radius: 12px;
  border: none;
  box-shadow: 
    0 1px 3px rgba(0, 0, 0, 0.04),
    0 4px 12px rgba(0, 0, 0, 0.06),
    inset 0 0.5px 0 rgba(255, 255, 255, 0.8);
  padding: 20px;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.overview-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.overview-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.3px;
}

.more-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border: none;
  background: transparent;
  border-radius: 6px;
  color: #86868b;
  cursor: pointer;
  transition: all 0.15s ease;
}

.more-btn:hover {
  background: #f5f5f7;
  color: #1d1d1f;
}

.overview-meta {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-item.full {
  grid-column: span 3;
}

.meta-label {
  font-size: 11px;
  color: #86868b;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.meta-value {
  font-size: 13px;
  color: #1d1d1f;
}

.meta-value.code {
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
  background: #f5f5f7;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  display: inline-block;
}

/* Tabs 容器 */
.content-tabs-wrapper {
  background: #ffffff;
  border-radius: 12px;
  border: none;
  box-shadow: 
    0 1px 3px rgba(0, 0, 0, 0.04),
    0 4px 12px rgba(0, 0, 0, 0.06),
    inset 0 0.5px 0 rgba(255, 255, 255, 0.8);
  overflow: hidden;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.tabs-nav {
  display: flex;
  gap: 2px;
  padding: 6px;
  background: #f5f5f7;
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.06);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  background: transparent;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  color: #86868b;
  cursor: pointer;
  transition: all 0.15s ease;
  letter-spacing: -0.1px;
}

.tab-btn:hover {
  color: #1d1d1f;
}

.tab-btn.active {
  background: #ffffff;
  color: #1d1d1f;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.tab-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.tab-title {
  font-size: 12px;
  font-weight: 500;
  color: #86868b;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

/* macOS 风格表格 */
.mac-table {
  --el-table-bg-color: transparent;
  --el-table-header-bg-color: #f5f5f7;
  --el-table-tr-bg-color: transparent;
  --el-table-row-hover-bg-color: #f5f5f7;
  --el-table-border-color: rgba(0, 0, 0, 0.06);
  --el-table-text-color: #1d1d1f;
  --el-table-header-text-color: #86868b;
  border-radius: 8px;
  overflow: hidden;
}

.mac-table :deep(th.el-table__cell) {
  font-weight: 500;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  padding: 10px 0;
}

.mac-table :deep(td.el-table__cell) {
  font-size: 13px;
  padding: 10px 0;
}

.mac-table :deep(.el-table__inner-wrapper::before) {
  display: none;
}

.version-tag {
  display: inline-block;
  background: #f5f5f7;
  padding: 3px 8px;
  border-radius: 4px;
  font-family: 'SF Mono', 'Monaco', monospace;
  font-size: 12px;
  color: #0071e3;
  font-weight: 500;
}

.status-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}

.status-badge.published {
  background: #e3f9e5;
  color: #1e7f34;
}

.status-badge.draft {
  background: #f5f5f7;
  color: #86868b;
}

.status-badge.running {
  background: #e3f2fd;
  color: #0071e3;
}

.status-badge.paused {
  background: #fff4e5;
  color: #c9341e;
}

.status-badge.completed {
  background: #f5f5f7;
  color: #1d1d1f;
}

.score {
  font-weight: 600;
  color: #1e7f34;
}

.muted {
  color: #86868b;
}

.traffic-ratio {
  font-weight: 500;
  color: #0071e3;
}

.sample-count .control {
  color: #86868b;
}

.sample-count .divider {
  margin: 0 4px;
  color: #d2d2d7;
}

.sample-count .experiment {
  color: #0071e3;
}

.action-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  padding: 0;
  border: none;
  background: transparent;
  border-radius: 6px;
  color: #86868b;
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-trigger:hover {
  background: #f5f5f7;
  color: #0071e3;
}

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: #ffffff;
  border-radius: 12px;
  border: none;
  box-shadow: 
    0 1px 3px rgba(0, 0, 0, 0.04),
    0 4px 12px rgba(0, 0, 0, 0.06),
    inset 0 0.5px 0 rgba(255, 255, 255, 0.8);
  padding: 60px;
}

.empty-icon {
  color: #d2d2d7;
}

.empty-state h3 {
  margin: 0;
  font-size: 17px;
  font-weight: 500;
  color: #1d1d1f;
  letter-spacing: -0.2px;
}

.empty-state p {
  margin: 0;
  font-size: 13px;
  color: #86868b;
}

/* ============================================
   对话框样式
   ============================================ */
.mac-dialog :deep(.el-dialog) {
  background: #ffffff;
  border: none;
  border-radius: 12px;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.15),
    0 0 1px rgba(0, 0, 0, 0.1);
}

.mac-dialog :deep(.el-dialog__header) {
  padding: 16px 20px;
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.06);
  margin-right: 0;
}

.mac-dialog :deep(.el-dialog__title) {
  color: #1d1d1f;
  font-weight: 600;
  font-size: 15px;
  letter-spacing: -0.2px;
}

.mac-dialog :deep(.el-dialog__headerbtn) {
  top: 16px;
  right: 16px;
  width: 20px;
  height: 20px;
}

.mac-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #86868b;
}

.mac-dialog :deep(.el-dialog__headerbtn:hover .el-dialog__close) {
  color: #1d1d1f;
}

.mac-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.mac-dialog :deep(.el-dialog__footer) {
  padding: 14px 20px;
  border-top: 0.5px solid rgba(0, 0, 0, 0.06);
}

.mac-dialog :deep(.el-form-item__label) {
  color: #1d1d1f;
  font-weight: 500;
  font-size: 13px;
  padding-bottom: 6px;
}

.mac-dialog :deep(.el-input__wrapper),
.mac-dialog :deep(.el-textarea__inner),
.mac-dialog :deep(.el-select__wrapper) {
  background: #f5f5f7;
  border: 1px solid transparent;
  box-shadow: none;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.mac-dialog :deep(.el-input__wrapper:hover),
.mac-dialog :deep(.el-textarea__inner:hover),
.mac-dialog :deep(.el-select__wrapper:hover) {
  background: #e8e8ed;
}

.mac-dialog :deep(.el-input__wrapper:focus-within),
.mac-dialog :deep(.el-textarea__inner:focus),
.mac-dialog :deep(.el-select__wrapper:focus-within) {
  background: #ffffff;
  border-color: #0071e3;
  box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.1);
}

.mac-dialog :deep(.el-input__inner),
.mac-dialog :deep(.el-textarea__inner) {
  color: #1d1d1f;
  font-size: 13px;
}

.mac-dialog :deep(.el-input__inner::placeholder),
.mac-dialog :deep(.el-textarea__inner::placeholder) {
  color: #86868b;
}

.code-editor :deep(.el-textarea__inner) {
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
  font-size: 12px;
  line-height: 1.6;
  background: #1d1d1f !important;
  color: #f5f5f7 !important;
  border-color: #1d1d1f !important;
}

.code-editor :deep(.el-textarea__inner:hover) {
  background: #2d2d2f !important;
}

.code-editor :deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.3) !important;
}

/* 版本详情 */
.version-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-header {
  display: flex;
  gap: 20px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.detail-row .label {
  font-size: 12px;
  color: #86868b;
}

.detail-stats {
  display: flex;
  gap: 16px;
  padding: 14px;
  background: #f5f5f7;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  min-width: 80px;
}

.stat-value {
  font-size: 22px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.5px;
}

.stat-label {
  font-size: 11px;
  color: #86868b;
}

.detail-content h4 {
  margin: 0 0 6px 0;
  font-size: 12px;
  font-weight: 500;
  color: #86868b;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.detail-content p {
  margin: 0;
  font-size: 13px;
  color: #1d1d1f;
}

.code-block {
  background: #1d1d1f;
  border-radius: 8px;
  padding: 14px;
  font-family: 'SF Mono', 'Monaco', monospace;
  font-size: 12px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 280px;
  overflow-y: auto;
  color: #f5f5f7;
}

/* 统计内容 */
.statistics-content {
  padding: 4px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stats-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 12px;
  background: #f5f5f7;
  border-radius: 10px;
  text-align: center;
}

.stats-card.highlight {
  background: #e8f4fd;
  border: 1px solid rgba(0, 113, 227, 0.2);
}

.stats-value {
  font-size: 24px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.5px;
}

.stats-value.positive {
  color: #1e7f34;
}

.stats-value.negative {
  color: #c9341e;
}

.stats-label {
  font-size: 11px;
  color: #86868b;
}

/* Dropdown 下拉菜单样式 */
:deep(.el-dropdown-menu) {
  background: #ffffff;
  border: 0.5px solid rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  padding: 4px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  min-width: 140px;
}

:deep(.el-dropdown-menu__item) {
  color: #1d1d1f;
  font-size: 13px;
  padding: 7px 12px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: -0.1px;
}

:deep(.el-dropdown-menu__item:hover) {
  background: #f5f5f7;
  color: #1d1d1f;
}

:deep(.el-dropdown-menu__item .el-icon) {
  font-size: 14px;
  color: #86868b;
}

:deep(.el-dropdown-menu__item:hover .el-icon) {
  color: #1d1d1f;
}

:deep(.el-dropdown-menu__item .danger) {
  color: #c9341e;
}

/* 按钮样式 */
:deep(.el-button--primary) {
  background: linear-gradient(180deg, #3b9eff 0%, #0071e3 100%);
  border-color: transparent;
  box-shadow: 
    0 1px 2px rgba(0, 113, 227, 0.2),
    0 2px 6px rgba(0, 113, 227, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(180deg, #4da6ff 0%, #0077ed 100%);
  box-shadow: 
    0 2px 4px rgba(0, 113, 227, 0.3),
    0 4px 12px rgba(0, 113, 227, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

:deep(.el-button--default) {
  background: #ffffff;
  border-color: transparent;
  color: #1d1d1f;
  box-shadow: 
    0 1px 2px rgba(0, 0, 0, 0.04),
    0 0 0 1px rgba(0, 0, 0, 0.08);
}

:deep(.el-button--default:hover) {
  background: #f5f5f7;
  color: #1d1d1f;
  box-shadow: 
    0 2px 4px rgba(0, 0, 0, 0.06),
    0 0 0 1px rgba(0, 0, 0, 0.12);
}

/* Switch 开关 */
:deep(.el-switch.is-checked .el-switch__core) {
  background: #1e7f34;
  border-color: #1e7f34;
}

/* Tag 标签 */
:deep(.el-tag--primary) {
  background: #e8f4fd;
  border-color: rgba(0, 113, 227, 0.2);
  color: #0071e3;
}

:deep(.el-tag--success) {
  background: #e3f9e5;
  border-color: rgba(30, 127, 52, 0.2);
  color: #1e7f34;
}

:deep(.el-tag--warning) {
  background: #fff4e5;
  border-color: rgba(201, 52, 30, 0.2);
  color: #c9341e;
}

:deep(.el-tag--info) {
  background: #f5f5f7;
  border-color: transparent;
  color: #86868b;
}

:deep(.el-tag--danger) {
  background: #fde8e8;
  border-color: rgba(201, 52, 30, 0.2);
  color: #c9341e;
}

/* ============================================
   响应式设计
   ============================================ */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 280px 1fr;
  }
}

@media (max-width: 900px) {
  .main-content {
    grid-template-columns: 1fr;
  }

  .config-sidebar {
    max-height: none;
    position: static;
  }

  .config-list {
    max-height: 240px;
  }
}

@media (max-width: 640px) {
  .page-header {
    padding: 16px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .action-btn {
    flex: 1;
  }

  .main-content {
    padding: 16px;
  }

  .overview-meta {
    grid-template-columns: 1fr;
  }

  .meta-item.full {
    grid-column: span 1;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .detail-header {
    flex-direction: column;
    gap: 12px;
  }
}

/* 滚动条样式 - macOS 风格 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.25);
}
</style>

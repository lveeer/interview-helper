<template>
  <div class="prompt-config">
    <!-- 头部 -->
    <div class="header">
      <div class="header-title">
        <h1>Prompt 配置</h1>
        <span class="subtitle">管理 Prompt 模板和版本</span>
      </div>
      <div class="header-actions">
        <el-button @click="handleInitFromFiles" :loading="initLoading">
          <el-icon><Upload /></el-icon>导入
        </el-button>
        <el-button type="primary" @click="handleCreateConfig">
          <el-icon><Plus /></el-icon>新建
        </el-button>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="content">
      <!-- 左侧列表 -->
      <div class="sidebar">
        <div class="filter-bar">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索配置..."
            clearable
            size="small"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="filterCategory" placeholder="分类" clearable size="small">
            <el-option
              v-for="cat in CONFIG_CATEGORIES"
              :key="cat.value"
              :label="cat.label"
              :value="cat.value"
            />
          </el-select>
        </div>

        <div class="config-list" v-loading="listLoading">
          <div
            v-for="config in filteredConfigList"
            :key="config.id"
            class="config-item"
            :class="{ active: selectedConfig?.id === config.id }"
            @click="handleSelectConfig(config)"
          >
            <div class="item-name">{{ config.display_name || config.name }}</div>
            <div class="item-meta">
              <el-tag size="small" :type="getCategoryType(config.category)">
                {{ getCategoryLabel(config.category) }}
              </el-tag>
              <span class="version-num">v{{ config.version_count || 0 }}</span>
            </div>
          </div>
          <el-empty v-if="filteredConfigList.length === 0" description="暂无配置" :image-size="80" />
        </div>
      </div>

      <!-- 右侧详情 -->
      <div class="detail" v-if="selectedConfig">
        <!-- 配置信息卡片 -->
        <el-card class="info-card" shadow="never">
          <div class="info-header">
            <div class="info-title">
              <h2>{{ selectedConfig.display_name || selectedConfig.name }}</h2>
              <el-tag :type="selectedConfig.is_active ? 'success' : 'info'" size="small">
                {{ selectedConfig.is_active ? '已启用' : '已禁用' }}
              </el-tag>
            </div>
            <el-dropdown>
              <el-button circle><el-icon><MoreFilled /></el-icon></el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleEditConfig">
                    <el-icon><Edit /></el-icon>编辑
                  </el-dropdown-item>
                  <el-dropdown-item @click="handleDeleteConfig" divided>
                    <el-icon><Delete /></el-icon>删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <el-descriptions :column="3" size="small" border>
            <el-descriptions-item label="标识">{{ selectedConfig.name }}</el-descriptions-item>
            <el-descriptions-item label="标签">{{ selectedConfig.tags || '-' }}</el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">{{ selectedConfig.description || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 版本列表 -->
        <el-card class="version-card" shadow="never">
          <template #header>
            <div class="version-header">
              <span>版本列表</span>
              <el-button type="primary" size="small" @click="handleCreateVersion">
                <el-icon><Plus /></el-icon>新建版本
              </el-button>
            </div>
          </template>
          <el-table :data="versionList" v-loading="versionLoading" stripe>
            <el-table-column prop="version" label="版本" width="100">
              <template #default="{ row }">
                <span class="version-code">{{ row.version }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="change_log" label="变更说明" min-width="200" show-overflow-tooltip />
            <el-table-column label="状态" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="row.is_published ? 'success' : 'info'" size="small">
                  {{ row.is_published ? '已发布' : '草稿' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="usage_count" label="使用" width="70" align="center" />
            <el-table-column label="操作" width="80" align="center" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="handleViewVersion(row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>

      <!-- 空状态 -->
      <div class="empty-detail" v-else>
        <el-empty description="选择左侧配置查看详情" :image-size="120">
          <el-button type="primary" @click="handleCreateConfig">创建配置</el-button>
        </el-empty>
      </div>
    </div>

    <!-- 配置对话框 -->
    <el-dialog v-model="configDialogVisible" :title="configForm.id ? '编辑配置' : '新建配置'" width="500px">
      <el-form ref="configFormRef" :model="configForm" :rules="configRules" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="配置名称" prop="name">
              <el-input v-model="configForm.name" :disabled="!!configForm.id" placeholder="唯一标识" />
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
                <el-option v-for="cat in CONFIG_CATEGORIES" :key="cat.value" :label="cat.label" :value="cat.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="启用状态">
              <el-switch v-model="configForm.is_active" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="标签">
          <el-input v-model="configForm.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="configForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <template v-if="!configForm.id">
          <el-form-item label="初始版本号">
            <el-input v-model="configForm.initial_version" placeholder="v1.0.0" />
          </el-form-item>
          <el-form-item label="初始内容">
            <el-input v-model="configForm.initial_content" type="textarea" :rows="4" placeholder="Prompt 内容" />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="configDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveConfig" :loading="saveConfigLoading">保存</el-button>
      </template>
    </el-dialog>

    <!-- 版本对话框 -->
    <el-dialog v-model="versionDialogVisible" :title="versionForm.id ? '编辑版本' : '新建版本'" width="600px">
      <el-form ref="versionFormRef" :model="versionForm" :rules="versionRules" label-position="top">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="版本号" prop="version">
              <el-input v-model="versionForm.version" :disabled="!!versionForm.id" placeholder="v1.0.0" />
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="变更说明" prop="change_log">
              <el-input v-model="versionForm.change_log" placeholder="本次变更说明" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Prompt 内容" prop="content">
          <el-input v-model="versionForm.content" type="textarea" :rows="12" class="code-input" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="versionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveVersion" :loading="saveVersionLoading">保存</el-button>
      </template>
    </el-dialog>

    <!-- 查看版本对话框 -->
    <el-dialog v-model="viewVersionDialogVisible" title="版本详情" width="600px">
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="版本">{{ viewVersionData.version }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="viewVersionData.is_published ? 'success' : 'info'" size="small">
            {{ viewVersionData.is_published ? '已发布' : '草稿' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="使用次数">{{ viewVersionData.usage_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="平均评分">{{ viewVersionData.avg_score?.toFixed(1) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="变更说明" :span="2">{{ viewVersionData.change_log || '-' }}</el-descriptions-item>
      </el-descriptions>
      <div class="prompt-content">
        <div class="prompt-label">Prompt 内容</div>
        <pre>{{ viewVersionData.content }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Upload, Edit, Delete, MoreFilled, Document, View, Promotion, CircleCheck, ArrowDown
} from '@element-plus/icons-vue'
import {
  CONFIG_CATEGORIES,
  getConfigList,
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
  initFromFiles
} from '@/api/promptConfig'

// 列表数据
const listLoading = ref(false)
const configList = ref([])
const selectedConfig = ref(null)
const searchKeyword = ref('')
const filterCategory = ref('')

// 配置表单
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

// 版本数据
const versionLoading = ref(false)
const versionList = ref([])
const versionDialogVisible = ref(false)
const versionFormRef = ref(null)
const saveVersionLoading = ref(false)
const versionForm = ref({ version: '', content: '', change_log: '' })
const versionRules = {
  version: [{ required: true, message: '请输入版本号', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
}
const viewVersionDialogVisible = ref(false)
const viewVersionData = ref({})

// 初始化
const initLoading = ref(false)

// 计算属性
const filteredConfigList = computed(() => {
  let list = configList.value
  if (filterCategory.value) list = list.filter(c => c.category === filterCategory.value)
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    list = list.filter(c => c.name.toLowerCase().includes(kw) || (c.display_name && c.display_name.toLowerCase().includes(kw)))
  }
  return list
})

// 辅助函数
const getCategoryLabel = (cat) => CONFIG_CATEGORIES.find(c => c.value === cat)?.label || cat
const getCategoryType = (cat) => ({ interview: 'primary', resume: 'success', evaluation: 'warning', rag: 'info', game: 'danger' }[cat] || '')

// 加载数据
const loadConfigList = async () => {
  listLoading.value = true
  try {
    const res = await getConfigList({ page_size: 100 })
    configList.value = res.data || []
  } catch {
    ElMessage.error('加载配置列表失败')
  } finally {
    listLoading.value = false
  }
}

const handleSelectConfig = async (config) => {
  selectedConfig.value = config
  versionLoading.value = true
  try {
    const res = await getVersionList(config.id)
    versionList.value = res.data || []
  } catch {
    ElMessage.error('加载版本列表失败')
  } finally {
    versionLoading.value = false
  }
}

// 配置操作
const handleCreateConfig = () => {
  configForm.value = { name: '', display_name: '', category: '', tags: '', description: '', is_active: true, initial_content: '', initial_version: 'v1.0.0' }
  configDialogVisible.value = true
}
const handleEditConfig = () => {
  const c = selectedConfig.value
  configForm.value = { id: c.id, name: c.name, display_name: c.display_name || '', category: c.category, tags: c.tags || '', description: c.description || '', is_active: c.is_active }
  configDialogVisible.value = true
}
const handleSaveConfig = async () => {
  if (!(await configFormRef.value.validate())) return
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
      ElMessage.success('更新成功')
    } else {
      await createConfig(configForm.value)
      ElMessage.success('创建成功')
    }
    configDialogVisible.value = false
    await loadConfigList()
  } catch {
    ElMessage.error(configForm.value.id ? '更新失败' : '创建失败')
  } finally {
    saveConfigLoading.value = false
  }
}
const handleDeleteConfig = async () => {
  try {
    await ElMessageBox.confirm('确定删除此配置？', '提示', { type: 'warning' })
    await deleteConfig(selectedConfig.value.id)
    ElMessage.success('删除成功')
    selectedConfig.value = null
    await loadConfigList()
  } catch {}
}

// 版本操作
const handleCreateVersion = () => {
  versionForm.value = { version: '', content: '', change_log: '' }
  versionDialogVisible.value = true
}
const handleEditVersion = async (row) => {
  try {
    const res = await getVersionDetail(row.id)
    versionForm.value = { id: res.data.id, version: res.data.version, content: res.data.content, change_log: res.data.change_log || '' }
    versionDialogVisible.value = true
  } catch {
    ElMessage.error('获取详情失败')
  }
}
const handleViewVersion = async (row) => {
  try {
    const res = await getVersionDetail(row.id)
    viewVersionData.value = res.data
    viewVersionDialogVisible.value = true
  } catch {
    ElMessage.error('获取详情失败')
  }
}
const handleSaveVersion = async () => {
  if (!(await versionFormRef.value.validate())) return
  saveVersionLoading.value = true
  try {
    if (versionForm.value.id) {
      await updateVersion(versionForm.value.id, { content: versionForm.value.content, change_log: versionForm.value.change_log })
    } else {
      await createVersion(selectedConfig.value.id, versionForm.value)
    }
    ElMessage.success('保存成功')
    versionDialogVisible.value = false
    await handleSelectConfig(selectedConfig.value)
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saveVersionLoading.value = false
  }
}
const handlePublishVersion = async (row) => {
  try {
    await ElMessageBox.confirm(`发布版本 ${row.version}？`, '确认')
    await publishVersion(row.id)
    ElMessage.success('发布成功')
    await handleSelectConfig(selectedConfig.value)
  } catch {}
}
const handleActivateVersion = async (row) => {
  try {
    await ElMessageBox.confirm(`激活版本 ${row.version}？`, '确认')
    await activateVersion(selectedConfig.value.id, row.id)
    ElMessage.success('激活成功')
    await loadConfigList()
  } catch {}
}
const handleDeleteVersion = async (row) => {
  try {
    await ElMessageBox.confirm(`删除版本 ${row.version}？`, '提示', { type: 'warning' })
    await deleteVersion(row.id)
    ElMessage.success('删除成功')
    await handleSelectConfig(selectedConfig.value)
  } catch {}
}
const handleInitFromFiles = async () => {
  try {
    await ElMessageBox.confirm('从 prompts/ 目录导入配置？', '确认')
    initLoading.value = true
    const res = await initFromFiles()
    ElMessage.success(`成功导入 ${res.data?.imported_count || 0} 个配置`)
    await loadConfigList()
  } catch {} finally {
    initLoading.value = false
  }
}

onMounted(loadConfigList)
</script>

<style scoped>
.prompt-config {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

/* 头部 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.header-title h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.header-title .subtitle {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

/* 内容区 */
.content {
  flex: 1;
  display: flex;
  overflow: hidden;
  padding: 16px;
  gap: 16px;
}

/* 左侧边栏 */
.sidebar {
  width: 360px;
  min-width: 300px;
  background: #fff;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.filter-bar {
  padding: 12px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.config-item {
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
}

.config-item:hover {
  background: #f5f7fa;
}

.config-item.active {
  background: #ecf5ff;
}

.item-name {
  font-weight: 500;
  margin-bottom: 8px;
  font-size: 14px;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.version-num {
  font-size: 12px;
  color: #909399;
}

/* 右侧详情 */
.detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
}

.empty-detail {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.info-card :deep(.el-card__body) {
  padding: 16px;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.info-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-title h2 {
  margin: 0;
  font-size: 16px;
}

.version-card {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.version-card :deep(.el-card__body) {
  flex: 1;
  overflow: hidden;
  padding: 0;
}

.version-card :deep(.el-card__header) {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.version-card :deep(.el-table) {
  height: 100%;
}

.version-code {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
  white-space: nowrap;
}

/* 代码输入框 */
.code-input :deep(textarea) {
  font-family: 'SF Mono', Monaco, monospace;
  font-size: 13px;
  line-height: 1.6;
}

/* Prompt 内容展示 */
.prompt-content {
  margin-top: 16px;
}

.prompt-label {
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
}

.prompt-content pre {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style>

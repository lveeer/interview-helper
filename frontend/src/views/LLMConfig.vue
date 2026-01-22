<template>
  <div class="llm-config-container">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <h2>LLM 配置管理</h2>
          <el-button
            v-if="config.id && config.id > 0"
            type="danger"
            @click="handleDelete"
            :loading="deleteLoading"
          >
            删除配置
          </el-button>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        v-loading="loading"
      >
        <el-form-item label="提供商" prop="provider">
          <el-select
            v-model="formData.provider"
            placeholder="请选择提供商"
            @change="handleProviderChange"
            :disabled="config.id && config.id > 0"
          >
            <el-option
              v-for="provider in providers"
              :key="provider.provider"
              :label="provider.name"
              :value="provider.provider"
            >
              <div class="provider-option">
                <span>{{ provider.name }}</span>
                <span class="provider-desc">{{ provider.description }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="模型" prop="model_name">
          <el-select
            v-model="formData.model_name"
            placeholder="请先选择提供商"
            :disabled="!formData.provider"
          >
            <el-option
              v-for="model in currentModels"
              :key="model"
              :label="model"
              :value="model"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="API Key" prop="api_key">
          <el-input
            v-model="formData.api_key"
            placeholder="请输入 API Key（可选，不填则使用全局配置）"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item label="API 端点" prop="api_base">
          <el-input
            v-model="formData.api_base"
            placeholder="请输入 API 端点（可选）"
            clearable
          />
        </el-form-item>

        <el-form-item label="启用状态" prop="is_active">
          <el-switch v-model="formData.is_active" />
        </el-form-item>

        <el-form-item>
          <el-space>
            <el-button
              type="primary"
              @click="handleTest"
              :loading="testLoading"
            >
              测试连接
            </el-button>
            <el-button
              type="success"
              @click="handleSave"
              :loading="saveLoading"
            >
              {{ config.id && config.id > 0 ? '更新配置' : '保存配置' }}
            </el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-space>
        </el-form-item>
      </el-form>

      <el-alert
        v-if="testResult"
        :title="testResult.success ? '连接成功' : '连接失败'"
        :type="testResult.success ? 'success' : 'error'"
        :description="testResult.success
          ? `延迟: ${testResult.latency_ms}ms`
          : testResult.error"
        :closable="true"
        @close="testResult = null"
        show-icon
        style="margin-top: 20px"
      />
    </el-card>

    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      width="400px"
    >
      <p>删除配置后，系统将自动回退使用全局配置（.env 中的配置），确定要删除吗？</p>
      <template #footer>
        <el-space>
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="confirmDelete" :loading="deleteLoading">
            确认删除
          </el-button>
        </el-space>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getProviders,
  testConnection,
  getMyConfig,
  createConfig,
  updateConfig,
  deleteConfig
} from '@/api/llm_config'

const formRef = ref(null)
const loading = ref(false)
const testLoading = ref(false)
const saveLoading = ref(false)
const deleteLoading = ref(false)
const providers = ref([])
const config = ref({})
const testResult = ref(null)
const deleteDialogVisible = ref(false)

const formData = ref({
  provider: '',
  model_name: '',
  api_key: '',
  api_base: '',
  is_active: true
})

const currentModels = computed(() => {
  const provider = providers.value.find(p => p.provider === formData.value.provider)
  return provider ? provider.models : []
})

const rules = {
  provider: [{ required: true, message: '请选择提供商', trigger: 'change' }],
  model_name: [{ required: true, message: '请选择模型', trigger: 'change' }]
}

const loadProviders = async () => {
  loading.value = true
  try {
    const res = await getProviders()
    providers.value = res.data || []
  } catch (error) {
    ElMessage.error('加载提供商列表失败')
  } finally {
    loading.value = false
  }
}

const loadConfig = async () => {
  loading.value = true
  try {
    const res = await getMyConfig()
    const data = res.data || {}
    config.value = data
    formData.value = {
      provider: data.provider || '',
      model_name: data.model_name || '',
      api_key: data.api_key || '',
      api_base: data.api_base || '',
      is_active: data.is_active !== undefined ? data.is_active : true
    }
  } catch (error) {
    ElMessage.error('加载配置失败')
  } finally {
    loading.value = false
  }
}

const handleProviderChange = () => {
  formData.value.model_name = ''
  const provider = providers.value.find(p => p.provider === formData.value.provider)
  if (provider && provider.models.length > 0) {
    formData.value.model_name = provider.models[0]
    // 只有在 API 端点为空时才使用默认值，保留用户已填写的端点
    if (!formData.value.api_base) {
      formData.value.api_base = provider.default_api_base || ''
    }
  }
}

const handleTest = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    ElMessage.warning('请先填写必填项')
    return
  }

  testLoading.value = true
  testResult.value = null
  try {
    const res = await testConnection({
      provider: formData.value.provider,
      model_name: formData.value.model_name,
      api_key: formData.value.api_key,
      api_base: formData.value.api_base
    })
    testResult.value = res.data
  } catch (error) {
    testResult.value = {
      success: false,
      error: error.response?.data?.detail || error.message || '测试连接失败'
    }
  } finally {
    testLoading.value = false
  }
}

const handleSave = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    ElMessage.warning('请填写完整配置信息')
    return
  }

  saveLoading.value = true
  try {
    if (config.value.id && config.value.id > 0) {
      await updateConfig(formData.value)
      ElMessage.success('配置更新成功')
    } else {
      await createConfig(formData.value)
      ElMessage.success('配置创建成功')
    }
    await loadConfig()
  } catch (error) {
    const detail = error.response?.data?.detail
    if (detail) {
      ElMessage.error(detail)
    } else {
      ElMessage.error(config.value.id && config.value.id > 0 ? '更新配置失败' : '创建配置失败')
    }
  } finally {
    saveLoading.value = false
  }
}

const handleDelete = () => {
  deleteDialogVisible.value = true
}

const confirmDelete = async () => {
  deleteLoading.value = true
  try {
    await deleteConfig()
    ElMessage.success('配置删除成功')
    config.value = {}
    formData.value = {
      provider: '',
      model_name: '',
      api_key: '',
      api_base: '',
      is_active: true
    }
    deleteDialogVisible.value = false
  } catch (error) {
    ElMessage.error('删除配置失败')
  } finally {
    deleteLoading.value = false
  }
}

const handleReset = () => {
  formRef.value?.resetFields()
  if (config.value.id && config.value.id > 0) {
    formData.value = {
      provider: config.value.provider,
      model_name: config.value.model_name,
      api_key: config.value.api_key || '',
      api_base: config.value.api_base || '',
      is_active: config.value.is_active
    }
  } else {
    formData.value = {
      provider: '',
      model_name: '',
      api_key: '',
      api_base: '',
      is_active: true
    }
  }
  testResult.value = null
}

onMounted(() => {
  loadProviders()
  loadConfig()
})
</script>

<style scoped>
.llm-config-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.config-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.provider-option {
  display: flex;
  flex-direction: column;
  color: #303133;
}

.provider-option span:first-child {
  color: #303133;
}

.provider-desc {
  font-size: 12px;
  color: #606266;
  margin-top: 2px;
}

/* 暗色模式样式 */
html[data-theme='dark'] .provider-option {
  color: #e5e7eb;
}

html[data-theme='dark'] .provider-option span:first-child {
  color: #e5e7eb;
}

html[data-theme='dark'] .provider-desc {
  color: #9ca3af;
}
</style>
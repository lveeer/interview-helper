<template>
  <div class="llm-config-page">
    <!-- LLM 配置窗口 -->
    <div class="macos-window">
      <div class="window-titlebar">
        <div class="window-title">
          <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
            <path d="M2 17l10 5 10-5"></path>
            <path d="M2 12l10 5 10-5"></path>
          </svg>
          <span>LLM 配置管理</span>
        </div>
        <div class="window-actions">
          <button
            v-if="config.id && config.id > 0"
            class="action-btn danger"
            @click="deleteDialogVisible = true"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
            <span>删除配置</span>
          </button>
        </div>
      </div>

      <div class="window-content" v-loading="loading">
        <div class="config-form">
          <!-- 提供商选择 -->
          <div class="form-group">
            <label class="form-label required">提供商</label>
            <div class="select-wrapper">
              <select
                v-model="formData.provider"
                class="macos-select"
                @change="handleProviderChange"
                :disabled="config.id && config.id > 0"
              >
                <option value="" disabled>请选择提供商</option>
                <option v-for="provider in providers" :key="provider.provider" :value="provider.provider">
                  {{ provider.name }}
                </option>
              </select>
              <svg class="select-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
            <p class="form-hint" v-if="currentProvider">
              {{ currentProvider.description }}
            </p>
          </div>

          <!-- 模型选择 -->
          <div class="form-group">
            <label class="form-label required">模型</label>
            <div class="select-wrapper">
              <select
                v-model="formData.model_name"
                class="macos-select"
                :disabled="!formData.provider"
              >
                <option value="" disabled>请先选择提供商</option>
                <option v-for="model in currentModels" :key="model" :value="model">
                  {{ model }}
                </option>
              </select>
              <svg class="select-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
          </div>

          <!-- API Key -->
          <div class="form-group">
            <label class="form-label">API Key</label>
            <div class="input-wrapper">
              <input
                v-model="formData.api_key"
                :type="showApiKey ? 'text' : 'password'"
                class="macos-input"
                placeholder="请输入 API Key（可选，不填则使用全局配置）"
              />
              <button type="button" class="input-action" @click="showApiKey = !showApiKey">
                <svg v-if="showApiKey" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
              </button>
            </div>
          </div>

          <!-- API 端点 -->
          <div class="form-group">
            <label class="form-label">API 端点</label>
            <input
              v-model="formData.api_base"
              class="macos-input"
              placeholder="请输入 API 端点（可选）"
            />
          </div>

          <!-- 启用状态 -->
          <div class="form-group">
            <label class="form-label">启用状态</label>
            <div class="switch-wrapper">
              <label class="macos-switch">
                <input type="checkbox" v-model="formData.is_active" />
                <span class="switch-slider"></span>
              </label>
              <span class="switch-label">{{ formData.is_active ? '已启用' : '已禁用' }}</span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="form-actions">
            <button class="btn-secondary" @click="handleReset">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path>
                <path d="M3 3v5h5"></path>
              </svg>
              <span>重置</span>
            </button>
            <button class="btn-info" @click="handleTest" :disabled="testLoading">
              <svg class="spin" v-if="testLoading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M12 6v6l4 2"></path>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
              <span>{{ testLoading ? '测试中...' : '测试连接' }}</span>
            </button>
            <button class="btn-primary" @click="handleSave" :disabled="saveLoading">
              <svg class="spin" v-if="saveLoading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M12 6v6l4 2"></path>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                <polyline points="17 21 17 13 7 13 7 21"></polyline>
                <polyline points="7 3 7 8 15 8"></polyline>
              </svg>
              <span>{{ saveLoading ? '保存中...' : (config.id && config.id > 0 ? '更新配置' : '保存配置') }}</span>
            </button>
          </div>

          <!-- 测试结果 -->
          <Transition name="fade">
            <div v-if="testResult" class="test-result" :class="testResult.success ? 'success' : 'error'">
              <div class="result-icon">
                <svg v-if="testResult.success" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="15" y1="9" x2="9" y2="15"></line>
                  <line x1="9" y1="9" x2="15" y2="15"></line>
                </svg>
              </div>
              <div class="result-content">
                <h4>{{ testResult.success ? '连接成功' : '连接失败' }}</h4>
                <p v-if="testResult.success">延迟: {{ testResult.latency_ms }}ms</p>
                <p v-else>{{ testResult.error }}</p>
              </div>
              <button class="result-close" @click="testResult = null">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="deleteDialogVisible" class="modal-overlay" @click.self="deleteDialogVisible = false">
          <div class="modal-container delete-dialog">
            <div class="modal-titlebar">
              <div class="modal-controls">
                <span class="control close" @click="deleteDialogVisible = false"></span>
                <span class="control minimize"></span>
                <span class="control maximize"></span>
              </div>
              <span class="modal-title">确认删除</span>
            </div>
            <div class="modal-content">
              <div class="delete-warning">
                <svg class="warning-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                  <line x1="12" y1="9" x2="12" y2="13"></line>
                  <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
                <p>删除配置后，系统将自动回退使用全局配置（.env 中的配置），确定要删除吗？</p>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-secondary" @click="deleteDialogVisible = false">取消</button>
              <button class="btn-danger" :disabled="deleteLoading" @click="confirmDelete">
                <svg class="spin" v-if="deleteLoading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <path d="M12 6v6l4 2"></path>
                </svg>
                <span>{{ deleteLoading ? '删除中...' : '确认删除' }}</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getProviders,
  testConnection,
  getMyConfig,
  createConfig,
  updateConfig,
  deleteConfig
} from '@/api/llm_config'

const loading = ref(false)
const testLoading = ref(false)
const saveLoading = ref(false)
const deleteLoading = ref(false)
const providers = ref([])
const config = ref({})
const testResult = ref(null)
const deleteDialogVisible = ref(false)
const showApiKey = ref(false)

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

const currentProvider = computed(() => {
  return providers.value.find(p => p.provider === formData.value.provider)
})

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
    if (!formData.value.api_base) {
      formData.value.api_base = provider.default_api_base || ''
    }
  }
}

const handleTest = async () => {
  if (!formData.value.provider || !formData.value.model_name) {
    ElMessage.warning('请先选择提供商和模型')
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
    if (testResult.value.success) {
      ElMessage.success('连接测试成功')
    }
  } catch (error) {
    testResult.value = {
      success: false,
      error: error.response?.data?.detail || error.message || '测试连接失败'
    }
    ElMessage.error('连接测试失败')
  } finally {
    testLoading.value = false
  }
}

const handleSave = async () => {
  if (!formData.value.provider || !formData.value.model_name) {
    ElMessage.warning('请选择提供商和模型')
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
  showApiKey.value = false
}

onMounted(() => {
  loadProviders()
  loadConfig()
})
</script>

<style scoped>
/* 页面容器 */
.llm-config-page {
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
  max-width: 640px;
  margin: 0 auto;
}

.window-titlebar {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(180deg, #f6f6f6 0%, #e8e8e8 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  user-select: none;
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

.action-btn.danger {
  background: rgba(255, 59, 48, 0.1);
  color: #ff3b30;
}

.action-btn.danger:hover {
  background: rgba(255, 59, 48, 0.2);
}

.window-content {
  padding: 0;
}

/* 表单样式 */
.config-form {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group:last-child {
  margin-bottom: 0;
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

.form-label.required::after {
  content: '*';
  color: #ff3b30;
  margin-left: 4px;
}

.form-hint {
  margin-top: 6px;
  font-size: 11px;
  color: #86868b;
}

.select-wrapper {
  position: relative;
}

.macos-select {
  width: 100%;
  padding: 10px 32px 10px 12px;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 13px;
  color: #1d1d1f;
  appearance: none;
  cursor: pointer;
  transition: all 0.15s ease;
}

.macos-select:hover {
  background: rgba(0, 0, 0, 0.04);
}

.macos-select:focus {
  outline: none;
  border-color: #007aff;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.macos-select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.select-arrow {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 14px;
  height: 14px;
  color: #86868b;
  pointer-events: none;
}

/* 输入框样式 */
.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.macos-input {
  width: 100%;
  padding: 10px 12px;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 13px;
  color: #1d1d1f;
  transition: all 0.15s ease;
}

.input-wrapper .macos-input {
  padding-right: 40px;
}

.macos-input:hover {
  background: rgba(0, 0, 0, 0.04);
}

.macos-input:focus {
  outline: none;
  border-color: #007aff;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.macos-input::placeholder {
  color: #86868b;
}

.input-action {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  padding: 4px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: #86868b;
  transition: color 0.15s ease;
}

.input-action:hover {
  color: #007aff;
}

.input-action svg {
  width: 16px;
  height: 16px;
}

/* 开关样式 */
.switch-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.macos-switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.macos-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border-radius: 24px;
}

.switch-slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: all 0.3s ease;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.macos-switch input:checked + .switch-slider {
  background-color: #34c759;
}

.macos-switch input:checked + .switch-slider:before {
  transform: translateX(20px);
}

.switch-label {
  font-size: 13px;
  color: #86868b;
}

/* 操作按钮 */
.form-actions {
  display: flex;
  gap: 12px;
  padding-top: 8px;
}

.form-actions button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.form-actions button svg {
  width: 14px;
  height: 14px;
}

.form-actions button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(180deg, #007AFF 0%, #0066d6 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(180deg, #0084ff 0%, #0070e6 100%);
}

.btn-secondary {
  background: rgba(0, 0, 0, 0.05);
  color: #1d1d1f;
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.08);
}

.btn-info {
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
}

.btn-info:hover:not(:disabled) {
  background: rgba(0, 122, 255, 0.2);
}

.btn-danger {
  background: rgba(255, 59, 48, 0.1);
  color: #ff3b30;
}

.btn-danger:hover:not(:disabled) {
  background: rgba(255, 59, 48, 0.2);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 测试结果 */
.test-result {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-top: 20px;
  padding: 16px;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.test-result.success {
  background: rgba(52, 199, 89, 0.1);
  border: 1px solid rgba(52, 199, 89, 0.2);
}

.test-result.error {
  background: rgba(255, 59, 48, 0.1);
  border: 1px solid rgba(255, 59, 48, 0.2);
}

.result-icon {
  flex-shrink: 0;
}

.test-result.success .result-icon {
  color: #34c759;
}

.test-result.error .result-icon {
  color: #ff3b30;
}

.result-icon svg {
  width: 20px;
  height: 20px;
}

.result-content {
  flex: 1;
}

.result-content h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
}

.test-result.success .result-content h4 {
  color: #34c759;
}

.test-result.error .result-content h4 {
  color: #ff3b30;
}

.result-content p {
  margin: 0;
  font-size: 12px;
  color: #86868b;
}

.result-close {
  padding: 4px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: #86868b;
  transition: color 0.15s ease;
}

.result-close:hover {
  color: #1d1d1f;
}

.result-close svg {
  width: 16px;
  height: 16px;
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
  width: 480px;
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

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  background: rgba(0, 0, 0, 0.02);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
}

.modal-footer button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.modal-footer button svg {
  width: 14px;
  height: 14px;
}

/* 删除对话框 */
.delete-warning {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.warning-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  color: #ff9500;
}

.delete-warning p {
  margin: 0;
  font-size: 14px;
  color: #424245;
  line-height: 1.6;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}

/* 暗色模式 */
:global(html[data-theme='dark']) .llm-config-page {
  background: linear-gradient(180deg, #1c1c1e 0%, #000000 100%);
}

:global(html[data-theme='dark']) .macos-window {
  background: rgba(44, 44, 46, 0.85);
}

:global(html[data-theme='dark']) .window-titlebar {
  background: linear-gradient(180deg, #3a3a3c 0%, #2c2c2e 100%);
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

:global(html[data-theme='dark']) .window-title {
  color: #f5f5f7;
}

:global(html[data-theme='dark']) .macos-select,
:global(html[data-theme='dark']) .macos-input {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  color: #f5f5f7;
}

:global(html[data-theme='dark']) .macos-select:hover,
:global(html[data-theme='dark']) .macos-input:hover {
  background: rgba(255, 255, 255, 0.08);
}

:global(html[data-theme='dark']) .macos-select:focus,
:global(html[data-theme='dark']) .macos-input:focus {
  border-color: #0a84ff;
  box-shadow: 0 0 0 3px rgba(10, 132, 255, 0.2);
}

:global(html[data-theme='dark']) .modal-container {
  background: rgba(44, 44, 46, 0.95);
}

:global(html[data-theme='dark']) .modal-titlebar {
  background: linear-gradient(180deg, #3a3a3c 0%, #2c2c2e 100%);
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

:global(html[data-theme='dark']) .modal-title {
  color: #f5f5f7;
}

:global(html[data-theme='dark']) .delete-warning p {
  color: #e5e7eb;
}

:global(html[data-theme='dark']) .btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #f5f5f7;
}

:global(html[data-theme='dark']) .btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
}

:global(html[data-theme='dark']) .test-result.success {
  background: rgba(52, 199, 89, 0.15);
}

:global(html[data-theme='dark']) .test-result.error {
  background: rgba(255, 59, 48, 0.15);
}

:global(html[data-theme='dark']) .modal-footer {
  background: rgba(255, 255, 255, 0.02);
  border-top-color: rgba(255, 255, 255, 0.05);
}
</style>

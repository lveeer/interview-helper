<template>
  <div class="persona-selector">
    <div class="persona-header">
      <label class="persona-label">面试官人设</label>
      <el-button
        v-if="showCreate"
        type="primary"
        size="small"
        :icon="Plus"
        @click="handleCreate"
      >
        创建自定义人设
      </el-button>
    </div>

    <div v-loading="loading" class="persona-list">
      <div
        v-for="persona in personas"
        :key="persona.id"
        :class="['persona-item', { active: modelValue === persona.id }]"
        @click="selectPersona(persona.id)"
      >
        <div class="persona-radio">
          <div :class="['radio-circle', { checked: modelValue === persona.id }]">
            <div v-if="modelValue === persona.id" class="radio-dot"></div>
          </div>
        </div>
        <div class="persona-content">
          <div class="persona-title">
            {{ persona.name }}
            <el-tag v-if="persona.is_default" size="small" type="info">默认</el-tag>
          </div>
          <div class="persona-description">{{ persona.description }}</div>
          <div class="persona-meta">
            <span class="meta-item">
              <el-icon><ChatDotRound /></el-icon>
              语气：{{ persona.tone }}
            </span>
            <span class="meta-item">
              <el-icon><Aim /></el-icon>
              关注：{{ persona.focus }}
            </span>
          </div>
        </div>
        <div v-if="!persona.is_default" class="persona-actions">
          <el-button
            type="primary"
            link
            :icon="Edit"
            size="small"
            @click.stop="handleEdit(persona)"
          >
            编辑
          </el-button>
          <el-button
            type="danger"
            link
            :icon="Delete"
            size="small"
            @click.stop="handleDelete(persona)"
          >
            删除
          </el-button>
        </div>
      </div>

      <el-empty v-if="!loading && personas.length === 0" description="暂无人设" />
    </div>

    <!-- 创建/编辑人设对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑人设' : '创建人设'"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="人设名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入人设名称" />
        </el-form-item>
        <el-form-item label="人设描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入人设描述"
          />
        </el-form-item>
        <el-form-item label="语气风格" prop="tone">
          <el-input v-model="form.tone" placeholder="例如：友好、严厉、专业" />
        </el-form-item>
        <el-form-item label="关注重点" prop="focus">
          <el-input v-model="form.focus" placeholder="例如：技术深度、软技能、价值观" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, ChatDotRound, Aim } from '@element-plus/icons-vue'
import { getPersonas, getDefaultPersona, createPersona, updatePersona, deletePersona as deletePersonaApi } from '@/api/persona'

const props = defineProps({
  modelValue: {
    type: Number,
    default: null
  },
  showCreate: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'create'])

const personas = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const currentEditId = ref(null)

const form = ref({
  name: '',
  description: '',
  tone: '',
  focus: ''
})

const rules = {
  name: [
    { required: true, message: '请输入人设名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入人设描述', trigger: 'blur' }
  ],
  tone: [
    { required: true, message: '请输入语气风格', trigger: 'blur' }
  ],
  focus: [
    { required: true, message: '请输入关注重点', trigger: 'blur' }
  ]
}

const loadPersonas = async () => {
  loading.value = true
  try {
    const res = await getPersonas()
    if (res.code === 200) {
      personas.value = res.data || []

      // 如果没有选中的人设，选择默认人设
      if (!props.modelValue && personas.value.length > 0) {
        const defaultPersona = personas.value.find(p => p.is_default) || personas.value[0]
        emit('update:modelValue', defaultPersona.id)
      }
    }
  } catch (error) {
    console.error('加载人设失败:', error)
    ElMessage.error('加载人设失败')
  } finally {
    loading.value = false
  }
}

const selectPersona = (id) => {
  emit('update:modelValue', id)
}

const handleCreate = () => {
  isEdit.value = false
  currentEditId.value = null
  form.value = {
    name: '',
    description: '',
    tone: '',
    focus: ''
  }
  dialogVisible.value = true
  emit('create')
}

const handleEdit = (persona) => {
  isEdit.value = true
  currentEditId.value = persona.id
  form.value = {
    name: persona.name,
    description: persona.description,
    tone: persona.tone,
    focus: persona.focus
  }
  dialogVisible.value = true
}

const handleDelete = async (persona) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除人设「${persona.name}」吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const res = await deletePersonaApi(persona.id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      loadPersonas()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除人设失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      let res
      if (isEdit.value) {
        res = await updatePersona(currentEditId.value, form.value)
      } else {
        res = await createPersona(form.value)
      }

      if (res.code === 200) {
        ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
        dialogVisible.value = false
        loadPersonas()
      }
    } catch (error) {
      console.error('提交失败:', error)
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    } finally {
      submitting.value = false
    }
  })
}

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    // 确保选中的人设存在
    const exists = personas.value.find(p => p.id === newVal)
    if (!exists && personas.value.length > 0) {
      emit('update:modelValue', personas.value[0].id)
    }
  }
})

onMounted(() => {
  loadPersonas()
})
</script>

<style scoped>
.persona-selector {
  width: 100%;
}

.persona-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.persona-label {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.persona-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 500px;
  overflow-y: auto;
}

.persona-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  border: 2px solid var(--border-color-light);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg-color-white);
}

.persona-item:hover {
  border-color: var(--primary-color);
  background: var(--bg-color-light);
}

.persona-item.active {
  border-color: var(--primary-color);
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.05) 0%, rgba(64, 158, 255, 0.02) 100%);
}

.persona-radio {
  display: flex;
  align-items: flex-start;
  padding-top: 2px;
}

.radio-circle {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.radio-circle.checked {
  border-color: var(--primary-color);
}

.radio-dot {
  width: 10px;
  height: 10px;
  background: var(--primary-color);
  border-radius: 50%;
}

.persona-content {
  flex: 1;
  min-width: 0;
}

.persona-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.persona-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  line-height: 1.5;
}

.persona-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-secondary);
}

.persona-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.persona-item:hover .persona-actions {
  opacity: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .persona-item {
    flex-direction: column;
  }

  .persona-radio {
    align-items: center;
  }

  .persona-actions {
    flex-direction: row;
    opacity: 1;
  }
}
</style>
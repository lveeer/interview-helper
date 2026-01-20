<template>
  <div class="job-match">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>岗位匹配分析</span>
        </div>
      </template>

      <el-form :model="matchForm" label-width="100px">
        <el-form-item label="选择简历">
          <el-select
            v-model="matchForm.resume_id"
            placeholder="请选择简历"
            style="width: 100%"
          >
            <el-option
              v-for="resume in resumeList"
              :key="resume.id"
              :label="resume.file_name"
              :value="resume.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="岗位描述">
          <el-input
            v-model="matchForm.job_description"
            type="textarea"
            :rows="10"
            placeholder="请输入目标岗位的职位描述（JD）"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="analyzing" @click="handleMatch">
            开始分析
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="matchResult" class="mb-4">
      <template #header>
        <span>匹配结果</span>
      </template>

      <el-row :gutter="20">
        <el-col :span="12">
          <div class="match-score">
            <el-progress
              type="circle"
              :percentage="matchResult.match_score"
              :color="getScoreColor(matchResult.match_score)"
              :width="200"
            >
              <template #default="{ percentage }">
                <span class="percentage-value">{{ percentage }}%</span>
                <span class="percentage-label">总体匹配度</span>
              </template>
            </el-progress>
          </div>
        </el-col>

        <el-col :span="12">
          <div class="detail-scores">
            <div class="score-item">
              <span class="label">关键词匹配</span>
              <el-progress
                :percentage="matchResult.keyword_match"
                :color="getScoreColor(matchResult.keyword_match)"
              />
            </div>
            <div class="score-item">
              <span class="label">技能匹配</span>
              <el-progress
                :percentage="matchResult.skill_match"
                :color="getScoreColor(matchResult.skill_match)"
              />
            </div>
            <div class="score-item">
              <span class="label">项目相关性</span>
              <el-progress
                :percentage="matchResult.project_relevance"
                :color="getScoreColor(matchResult.project_relevance)"
              />
            </div>
          </div>
        </el-col>
      </el-row>

      <el-divider />

      <el-alert
        title="优势"
        type="success"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <ul>
          <li v-for="strength in matchResult.strengths" :key="strength">
            {{ strength }}
          </li>
        </ul>
      </el-alert>

      <el-alert
        title="缺失技能"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <el-tag
          v-for="skill in matchResult.missing_skills"
          :key="skill"
          style="margin-right: 10px; margin-bottom: 5px;"
        >
          {{ skill }}
        </el-tag>
      </el-alert>

      <el-alert
        title="优化建议"
        type="info"
        :closable="false"
      >
        <ul>
          <li v-for="suggestion in matchResult.suggestions" :key="suggestion">
            {{ suggestion }}
          </li>
        </ul>
      </el-alert>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getResumeList } from '@/api/resume'
import { matchJob } from '@/api/job'

const analyzing = ref(false)
const resumeList = ref([])
const matchResult = ref(null)

const matchForm = ref({
  resume_id: '',
  job_description: ''
})

const loadResumeList = async () => {
  try {
    const res = await getResumeList()
    if (res.code === 200) {
      resumeList.value = res.data || []
    }
  } catch (error) {
    console.error('加载简历列表失败:', error)
  }
}

const handleMatch = async () => {
  if (!matchForm.value.resume_id) {
    ElMessage.warning('请选择简历')
    return
  }

  if (!matchForm.value.job_description.trim()) {
    ElMessage.warning('请输入岗位描述')
    return
  }

  analyzing.value = true
  try {
    const res = await matchJob(matchForm.value)
    if (res.code === 200) {
      matchResult.value = res.data
      ElMessage.success('分析完成')
    }
  } catch (error) {
    console.error('分析失败:', error)
  } finally {
    analyzing.value = false
  }
}

const resetForm = () => {
  matchForm.value = {
    resume_id: '',
    job_description: ''
  }
  matchResult.value = null
}

const getScoreColor = (score) => {
  if (score >= 80) return '#67C23A'
  if (score >= 60) return '#E6A23C'
  return '#F56C6C'
}

onMounted(() => {
  loadResumeList()
})
</script>

<style scoped>
.match-score {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.percentage-value {
  display: block;
  font-size: 28px;
  font-weight: bold;
}

.percentage-label {
  display: block;
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.detail-scores {
  padding: 20px;
}

.score-item {
  margin-bottom: 20px;
}

.score-item .label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

.el-alert ul {
  margin: 10px 0 0 20px;
}

.el-alert li {
  margin-bottom: 5px;
}

.mb-4 {
  margin-bottom: 20px;
}
</style>
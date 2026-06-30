<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick, Select } from '@element-plus/icons-vue'
import { aiReview } from '../../api/ai'
import { getAchievement } from '../../api/achievements'
import { listIndicators } from '../../api/indicators'
import { createEvalResult } from '../../api/evalResults'

const loading = ref(false)
const result = ref(null)
const achievementLoading = ref(false)
const currentAchievement = ref(null)
const indicators = ref([])
const scoreSubmitting = ref(false)

const form = reactive({
  training_requirement: '',
  student_content: '',
  achievement_id: null,
})

const scoreForm = reactive({
  indicator_id: null,
  score: 80,
  comment: '',
  suggestion: '',
})

async function loadAchievementContext() {
  if (!form.achievement_id) {
    ElMessage.warning('请先填写成果 ID')
    return
  }
  achievementLoading.value = true
  try {
    const achievement = await getAchievement(form.achievement_id)
    currentAchievement.value = achievement
    const data = await listIndicators({ project_id: achievement.project_id, page: 1, page_size: 100 })
    indicators.value = data.items
    if (!scoreForm.indicator_id && indicators.value.length) {
      scoreForm.indicator_id = indicators.value[0].id
    }
    ElMessage.success('成果与指标已加载')
  } finally {
    achievementLoading.value = false
  }
}

async function runReview() {
  if (!form.achievement_id && (!form.training_requirement || !form.student_content)) {
    ElMessage.warning('请填写成果 ID，或同时填写实训要求和提交内容')
    return
  }
  loading.value = true
  result.value = null
  try {
    result.value = await aiReview({
      training_requirement: form.training_requirement || null,
      student_content: form.student_content || null,
      achievement_id: form.achievement_id || null,
    })
    if (result.value.available === false) {
      ElMessage.warning('AI 未完成，已返回人工复核提示')
    } else {
      ElMessage.success('AI 核查完成')
    }
  } finally {
    loading.value = false
  }
}

async function submitTeacherScore() {
  if (!form.achievement_id) {
    ElMessage.warning('请先填写成果 ID')
    return
  }
  if (!scoreForm.indicator_id) {
    ElMessage.warning('请选择评价指标')
    return
  }
  scoreSubmitting.value = true
  try {
    await createEvalResult({
      achievement_id: form.achievement_id,
      indicator_id: scoreForm.indicator_id,
      eval_type: 2,
      score: scoreForm.score,
      comment: scoreForm.comment || result.value?.summary || null,
      suggestion: scoreForm.suggestion || result.value?.standard_suggestion || null,
    })
    ElMessage.success('教师评价已提交')
  } finally {
    scoreSubmitting.value = false
  }
}
</script>

<template>
  <section class="feature-page">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">TEACHER · AI REVIEW</p>
        <h2>智能评价</h2>
        <p>按成果 ID 自动读取材料，也支持手动粘贴内容进行 AI 核查和教师评分。</p>
      </div>
    </div>

    <div class="review-layout">
      <article class="data-panel">
        <el-form :model="form" label-position="top">
          <el-form-item label="关联成果 ID">
            <div class="achievement-line">
              <el-input-number v-model="form.achievement_id" :min="1" controls-position="right" />
              <el-button :loading="achievementLoading" @click="loadAchievementContext">加载成果</el-button>
            </div>
          </el-form-item>
          <el-form-item label="实训要求">
            <el-input v-model="form.training_requirement" type="textarea" :rows="4" placeholder="填写成果 ID 时可留空，由后端读取项目要求" />
          </el-form-item>
          <el-form-item label="学生提交的代码 / 文档">
            <el-input v-model="form.student_content" type="textarea" :rows="8" placeholder="填写成果 ID 时可留空，由后端读取成果说明和附件解析内容" />
          </el-form-item>
          <el-button type="primary" :icon="MagicStick" :loading="loading" @click="runReview">开始 AI 核查</el-button>
        </el-form>
      </article>

      <article class="data-panel result-panel" v-loading="loading">
        <template v-if="result">
          <div class="score-head">
            <div class="score-circle" :class="{ muted: result.available === false }">{{ result.standard_score }}</div>
            <div>
              <strong>规范得分</strong>
              <span>{{ result.available === false ? 'AI 未完成' : '满分 100' }}</span>
            </div>
          </div>

          <div class="check-block">
            <div class="check-title">
              <span>功能实现</span>
              <el-tag :type="result.function_check.is_complete ? 'success' : 'danger'" effect="plain">
                {{ result.function_check.is_complete ? '完整' : '有缺失' }}
              </el-tag>
            </div>
            <ul v-if="result.function_check.problem_list.length">
              <li v-for="(p, i) in result.function_check.problem_list" :key="i">{{ p }}</li>
            </ul>
            <p v-else class="ok-text">无未完成功能点</p>
          </div>

          <div class="check-block">
            <div class="check-title">
              <span>逻辑风险</span>
              <el-tag :type="result.logic_check.has_risk ? 'warning' : 'success'" effect="plain">
                {{ result.logic_check.has_risk ? '存在风险' : '未发现明显风险' }}
              </el-tag>
            </div>
            <ul v-if="result.logic_check.risk_list.length">
              <li v-for="(p, i) in result.logic_check.risk_list" :key="i">{{ p }}</li>
            </ul>
            <p v-else class="ok-text">未发现逻辑风险</p>
          </div>

          <div class="check-block">
            <div class="check-title"><span>改进建议</span></div>
            <p>{{ result.standard_suggestion }}</p>
          </div>

          <div class="check-block">
            <div class="check-title"><span>整体总结</span></div>
            <p>{{ result.summary }}</p>
          </div>
        </template>
        <el-empty v-else description="填写左侧表单后开始 AI 核查" />
      </article>
    </div>

    <article class="data-panel score-panel">
      <div class="panel-head">
        <div>
          <strong>教师人工评价</strong>
          <span>AI 只提供建议，最终评分以人工评价为准。</span>
        </div>
        <el-button :loading="achievementLoading" @click="loadAchievementContext">刷新指标</el-button>
      </div>
      <el-form :model="scoreForm" label-width="90px" class="score-form">
        <el-form-item label="评价指标">
          <el-select v-model="scoreForm.indicator_id" placeholder="选择指标" style="width: 100%">
            <el-option v-for="i in indicators" :key="i.id" :label="`${i.indicator_name}（满分 ${i.max_score}）`" :value="i.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="得分">
          <el-input-number v-model="scoreForm.score" :min="0" :max="100" controls-position="right" />
        </el-form-item>
        <el-form-item label="评语">
          <el-input v-model="scoreForm.comment" type="textarea" :rows="2" placeholder="默认可使用 AI 总结" />
        </el-form-item>
        <el-form-item label="建议">
          <el-input v-model="scoreForm.suggestion" type="textarea" :rows="2" placeholder="默认可使用 AI 改进建议" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Select" :loading="scoreSubmitting" @click="submitTeacherScore">提交教师评价</el-button>
        </el-form-item>
      </el-form>
      <el-empty v-if="!indicators.length" description="填写成果 ID 并加载后显示项目指标" />
    </article>
  </section>
</template>

<style scoped>
.review-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-items: start; }
@media (max-width: 1100px) { .review-layout { grid-template-columns: 1fr; } }
.achievement-line { display: flex; gap: 10px; align-items: center; }
.result-panel { min-height: 320px; }
.score-head { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }
.score-circle {
  width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 24px; font-weight: 700; color: #fff; background: var(--el-color-primary);
}
.score-circle.muted { background: var(--el-color-info); }
.score-head span { display: block; color: var(--el-text-color-secondary); font-size: 12px; }
.check-block { padding: 12px 0; border-top: 1px solid var(--el-border-color-lighter); }
.check-title { display: flex; align-items: center; gap: 10px; font-weight: 600; margin-bottom: 6px; }
.check-block ul { margin: 0; padding-left: 18px; color: var(--el-text-color-regular); }
.check-block li { margin: 4px 0; }
.ok-text { color: var(--el-color-success); margin: 0; }
.score-panel { margin-top: 16px; }
.panel-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.panel-head strong { display: block; }
.panel-head span { color: var(--el-text-color-secondary); font-size: 13px; }
.score-form { max-width: 720px; }
</style>

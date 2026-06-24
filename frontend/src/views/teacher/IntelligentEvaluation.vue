<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick } from '@element-plus/icons-vue'
import { aiReview } from '../../api/ai'

const formRef = ref()
const loading = ref(false)
const result = ref(null)

const form = reactive({
  training_requirement: '',
  student_content: '',
  achievement_id: null,
})

const rules = {
  training_requirement: [{ required: true, message: '请输入实训要求', trigger: 'blur' }],
  student_content: [{ required: true, message: '请输入学生提交内容', trigger: 'blur' }],
}

async function runReview() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  result.value = null
  try {
    result.value = await aiReview({
      training_requirement: form.training_requirement,
      student_content: form.student_content,
      achievement_id: form.achievement_id || null,
    })
    ElMessage.success('AI 核查完成')
  } catch (e) {
    // http 拦截器已弹出错误信息
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="feature-page">
    <div class="feature-hero">
      <div>
        <p class="page-eyebrow">TEACHER · AI REVIEW</p>
        <h2>智能评价</h2>
        <p>基于大模型对实训成果做功能 / 逻辑 / 步骤 / 规范四维核查。</p>
      </div>
    </div>

    <div class="review-layout">
      <article class="data-panel">
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
          <el-form-item label="实训要求" prop="training_requirement">
            <el-input v-model="form.training_requirement" type="textarea" :rows="5" placeholder="粘贴本次实训的目标与要求…" />
          </el-form-item>
          <el-form-item label="学生提交的代码 / 文档" prop="student_content">
            <el-input v-model="form.student_content" type="textarea" :rows="10" placeholder="粘贴学生提交的代码或文档内容…" />
          </el-form-item>
          <el-form-item label="关联成果ID（选填）">
            <el-input-number v-model="form.achievement_id" :min="1" controls-position="right" placeholder="用于日志追溯" />
          </el-form-item>
          <el-button type="primary" :icon="MagicStick" :loading="loading" @click="runReview">开始 AI 核查</el-button>
        </el-form>
      </article>

      <article class="data-panel result-panel" v-loading="loading">
        <template v-if="result">
          <div class="score-head">
            <div class="score-circle">{{ result.standard_score }}</div>
            <div><strong>规范得分</strong><span>满分 100</span></div>
          </div>

          <div class="check-block">
            <div class="check-title">
              <span>功能实现</span>
              <el-tag :type="result.function_check.is_complete ? 'success' : 'danger'" effect="plain">
                {{ result.function_check.is_complete ? '完整' : '有缺失' }}
              </el-tag>
            </div>
            <ul v-if="result.function_check.problem_list.length"><li v-for="(p,i) in result.function_check.problem_list" :key="i">{{ p }}</li></ul>
            <p v-else class="ok-text">无未完成功能点</p>
          </div>

          <div class="check-block">
            <div class="check-title">
              <span>逻辑漏洞</span>
              <el-tag :type="result.logic_check.has_risk ? 'warning' : 'success'" effect="plain">
                {{ result.logic_check.has_risk ? '存在风险' : '无明显风险' }}
              </el-tag>
            </div>
            <ul v-if="result.logic_check.risk_list.length"><li v-for="(p,i) in result.logic_check.risk_list" :key="i">{{ p }}</li></ul>
            <p v-else class="ok-text">未发现逻辑风险</p>
          </div>

          <div class="check-block">
            <div class="check-title">
              <span>步骤完整性</span>
              <el-tag :type="result.step_check.is_complete ? 'success' : 'danger'" effect="plain">
                {{ result.step_check.is_complete ? '完整' : '有缺失' }}
              </el-tag>
            </div>
            <ul v-if="result.step_check.missing_steps.length"><li v-for="(p,i) in result.step_check.missing_steps" :key="i">{{ p }}</li></ul>
            <p v-else class="ok-text">步骤完整</p>
          </div>

          <div class="check-block">
            <div class="check-title"><span>规范建议</span></div>
            <p>{{ result.standard_suggestion }}</p>
          </div>

          <div class="check-block">
            <div class="check-title"><span>整体总结</span></div>
            <p>{{ result.summary }}</p>
          </div>
        </template>
        <el-empty v-else description="填写左侧表单并点击「开始 AI 核查」" />
      </article>
    </div>
  </section>
</template>

<style scoped>
.review-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-items: start; }
@media (max-width: 1100px) { .review-layout { grid-template-columns: 1fr; } }
.result-panel { min-height: 320px; }
.score-head { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }
.score-circle {
  width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 24px; font-weight: 700; color: #fff; background: var(--el-color-primary);
}
.score-head span { display: block; color: var(--el-text-color-secondary); font-size: 12px; }
.check-block { padding: 12px 0; border-top: 1px solid var(--el-border-color-lighter); }
.check-title { display: flex; align-items: center; gap: 10px; font-weight: 600; margin-bottom: 6px; }
.check-block ul { margin: 0; padding-left: 18px; color: var(--el-text-color-regular); }
.check-block li { margin: 4px 0; }
.ok-text { color: var(--el-color-success); margin: 0; }
</style>

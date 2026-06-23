<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Lock, User } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { roleCredentials, roleLabels } from '../../router/route-data'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const form = reactive({ role: 'teacher', account: 'teacher', password: '123456' })
const roles = ['student', 'teacher', 'enterprise', 'admin']
const roleDescriptions = {
  student: '查看实训任务、反馈与成长档案',
  teacher: '管理实训过程并完成评价复核',
  enterprise: '协同导师、指导项目与评价人才',
  admin: '维护组织、用户与系统评价规则',
}
const rules = {
  account: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}
const selectedRole = computed(() => roleLabels[form.role])

watch(() => form.role, (role) => {
  const credential = roleCredentials[role]
  form.account = credential.account
  form.password = credential.password
})

async function submit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await userStore.login(form)
    ElMessage.success(`欢迎回来，${selectedRole.value}`)
    router.replace(String(route.query.redirect || '/dashboard'))
  } catch (error) {
    ElMessage.error(error.message || '登录失败，请检查账号和密码')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-intro" aria-labelledby="login-intro-title">
      <div class="login-brand"><span class="brand-mark">智</span><strong>智训评</strong></div>
      <div class="intro-content">
        <span class="intro-kicker">SOFTWARE TRAINING EVALUATION</span>
        <h1 id="login-intro-title">让每一次实践<br />都留下成长证据</h1>
        <p>连接院校、企业与学习者，将实训过程、能力表现和评价反馈沉淀为可用的人才档案。</p>
      </div>
      <div class="intro-stats" aria-label="平台数据">
        <div><strong>126</strong><span>合作院校</span></div>
        <div><strong>2,860</strong><span>实训项目</span></div>
        <div><strong>98.6%</strong><span>评价完成率</span></div>
      </div>
    </section>

    <section class="login-panel" aria-labelledby="login-title">
      <div class="login-form-wrap">
        <div class="login-heading">
          <span>WELCOME BACK</span>
          <h2 id="login-title">登录智训评</h2>
          <p>选择身份后进入对应工作空间</p>
        </div>
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="submit">
          <el-form-item label="登录身份" prop="role">
            <el-radio-group v-model="form.role" class="role-grid" aria-label="登录身份">
              <el-radio v-for="role in roles" :key="role" :value="role" class="role-choice">
                <strong>{{ roleLabels[role] }}</strong>
                <span>{{ roleDescriptions[role] }}</span>
              </el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="账号" prop="account">
            <el-input v-model="form.account" size="large" autocomplete="username" placeholder="请输入账号">
              <template #prefix><el-icon><User /></el-icon></template>
            </el-input>
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" size="large" type="password" show-password autocomplete="current-password" placeholder="请输入密码" @keyup.enter="submit">
              <template #prefix><el-icon><Lock /></el-icon></template>
            </el-input>
          </el-form-item>
          <div class="login-utilities">
            <el-checkbox>记住登录状态</el-checkbox>
            <a href="#help" @click.prevent="ElMessage.info('请联系平台管理员重置密码')">忘记密码？</a>
          </div>
          <el-button native-type="submit" type="primary" size="large" class="login-submit" :loading="loading">登录系统</el-button>
          <p class="demo-tip" aria-live="polite">演示账号已自动填充，默认密码为 123456</p>
        </el-form>
      </div>
    </section>
  </main>
</template>

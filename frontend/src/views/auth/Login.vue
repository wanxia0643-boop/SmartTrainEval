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
  <main class="auth">
    <!-- 高校校园实景背景 -->
    <div class="auth-bg" aria-hidden="true"></div>

    <div class="auth-content">
      <aside class="auth-brand">
        <div class="brand-row"><span class="brand-mark">智</span><strong>智训评</strong></div>
        <h1>高校软件实训<br />智能评价平台</h1>
        <p>贯通院校教学、企业实践与学习者成长，把实训过程、能力表现与评价反馈沉淀为可信的人才档案。</p>
        <ul class="brand-points">
          <li><i></i>教学 · 实训 · 评价一体化</li>
          <li><i></i>AI 智能核查，多方协同评分</li>
          <li><i></i>能力图谱与成长档案可追溯</li>
        </ul>
      </aside>

      <section class="auth-card" aria-labelledby="login-title">
        <div class="card-head">
          <span class="card-kicker">WELCOME BACK</span>
          <h2 id="login-title">登录智训评</h2>
          <p>选择身份后进入对应工作空间</p>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="submit">
          <el-form-item label="登录身份" prop="role">
            <el-radio-group v-model="form.role" class="role-grid" aria-label="登录身份">
              <el-radio v-for="role in roles" :key="role" :value="role" class="role-choice" border>
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
      </section>
    </div>

    <p class="auth-credit">校园实景 · 上海交通大学　摄影 Ziqi CHAI · CC BY-SA 4.0 / Wikimedia Commons</p>
  </main>
</template>

<style scoped>
.auth {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 20px;
  overflow: hidden;
}

/* ===== 背景：真实校园照片 + 对比遮罩 ===== */
.auth-bg {
  position: absolute;
  inset: 0;
  background: url('/login-bg.jpg') center / cover no-repeat;
  transform: scale(1.04);
}
.auth-bg::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(105deg, rgba(6, 17, 40, .9) 0%, rgba(6, 17, 40, .62) 40%, rgba(6, 17, 40, .28) 72%, rgba(6, 17, 40, .12) 100%),
    linear-gradient(to top, rgba(6, 17, 40, .55), transparent 36%);
}

/* ===== 内容布局 ===== */
.auth-content {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 1080px;
  display: grid;
  grid-template-columns: 1.1fr 440px;
  gap: 48px;
  align-items: center;
}

.auth-brand { color: #eaf1ff; text-shadow: 0 2px 18px rgba(0, 0, 0, .35); }
.brand-row { display: flex; align-items: center; gap: 12px; margin-bottom: 30px; }
.brand-mark {
  display: grid; place-items: center; width: 44px; height: 44px; border-radius: 12px;
  font-size: 22px; font-weight: 800; color: #fff;
  background: linear-gradient(135deg, #3b82f6, #2f6bff); box-shadow: 0 8px 22px rgba(47, 107, 255, .45);
}
.brand-row strong { font-size: 22px; letter-spacing: .04em; }
.auth-brand h1 { margin: 0 0 16px; font-size: 40px; line-height: 1.22; font-weight: 800; letter-spacing: -.01em; }
.auth-brand > p { margin: 0 0 26px; max-width: 460px; color: #d2def6; font-size: 15px; line-height: 1.8; }
.brand-points { list-style: none; margin: 0; padding: 0; display: grid; gap: 13px; }
.brand-points li { display: flex; align-items: center; gap: 10px; color: #e3ecfb; font-size: 14.5px; }
.brand-points i { width: 7px; height: 7px; border-radius: 50%; background: #4ade80; box-shadow: 0 0 0 4px rgba(74, 222, 128, .2); }

/* ===== 登录卡片 ===== */
.auth-card {
  background: rgba(255, 255, 255, .97);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, .65);
  border-radius: 20px;
  padding: 36px 36px 30px;
  box-shadow: 0 30px 70px rgba(4, 12, 32, .5);
}
.card-head { margin-bottom: 22px; }
.card-kicker { color: #2f6bff; font-size: 12px; font-weight: 700; letter-spacing: .14em; }
.card-head h2 { margin: 8px 0 6px; font-size: 26px; color: #16203a; font-weight: 750; }
.card-head p { margin: 0; color: #7a8499; font-size: 13.5px; }

.role-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; width: 100%; }
.role-grid :deep(.el-radio.role-choice) {
  height: auto; margin: 0; padding: 11px 12px; border-radius: 12px; align-items: flex-start;
}
.role-grid :deep(.el-radio.role-choice .el-radio__label) { display: flex; flex-direction: column; gap: 2px; padding-left: 8px; }
.role-grid :deep(.el-radio.role-choice strong) { font-size: 14px; color: #1f2a44; }
.role-grid :deep(.el-radio.role-choice span) { font-size: 11.5px; color: #97a1b5; line-height: 1.35; }
.role-grid :deep(.el-radio.role-choice.is-checked) { border-color: #2f6bff; background: #f2f6ff; }
.role-grid :deep(.el-radio.role-choice.is-checked strong) { color: #2f6bff; }

.login-utilities { display: flex; align-items: center; justify-content: space-between; margin: 4px 0 18px; font-size: 13px; }
.login-utilities a { color: #2f6bff; text-decoration: none; }
.login-submit {
  width: 100%; height: 46px; font-size: 15px; font-weight: 600; letter-spacing: .06em; border: none;
  background: linear-gradient(135deg, #3b82f6, #2f6bff); box-shadow: 0 12px 26px rgba(47, 107, 255, .38);
}
.demo-tip { margin: 14px 0 0; text-align: center; color: #9aa4b8; font-size: 12.5px; }

.auth-credit {
  position: absolute; right: 16px; bottom: 12px; z-index: 2; margin: 0;
  color: rgba(255, 255, 255, .55); font-size: 11px; letter-spacing: .02em;
}

@media (max-width: 920px) {
  .auth-content { grid-template-columns: 1fr; max-width: 440px; gap: 26px; }
  .auth-brand { text-align: center; }
  .auth-brand h1 { font-size: 30px; }
  .auth-brand > p, .brand-points { display: none; }
  .brand-row { justify-content: center; margin-bottom: 4px; }
  .auth-credit { display: none; }
}
@media (max-width: 520px) {
  .auth-card { padding: 26px 22px; }
  .role-grid { grid-template-columns: 1fr; }
}
</style>

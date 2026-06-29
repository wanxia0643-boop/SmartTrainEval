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
    <!-- 高校教学体系主题背景 -->
    <div class="auth-bg" aria-hidden="true">
      <span class="glow glow-a"></span>
      <span class="glow glow-b"></span>

      <!-- 知识网络 -->
      <svg class="auth-net" viewBox="0 0 600 320" preserveAspectRatio="xMidYMid slice">
        <g stroke="rgba(255,255,255,.16)" stroke-width="1" fill="none">
          <path d="M70 60 L180 120 L120 220 L70 60 M180 120 L300 70 L300 70 M300 70 L430 130 L380 240 M430 130 L520 70 M180 120 L240 230" />
        </g>
        <g fill="rgba(255,255,255,.55)">
          <circle cx="70" cy="60" r="3.5" /><circle cx="180" cy="120" r="3" /><circle cx="300" cy="70" r="4" />
          <circle cx="430" cy="130" r="3" /><circle cx="520" cy="70" r="3.5" /><circle cx="120" cy="220" r="3" />
          <circle cx="240" cy="230" r="3" /><circle cx="380" cy="240" r="3.5" />
        </g>
      </svg>

      <!-- 校园天际线 -->
      <svg class="auth-campus" viewBox="0 0 1440 420" preserveAspectRatio="xMidYMax slice">
        <g fill="#0a1c3f">
          <!-- 左侧教学楼 -->
          <rect x="60" y="250" width="200" height="170" />
          <rect x="280" y="210" width="150" height="210" />
          <!-- 右侧实训楼 -->
          <rect x="1020" y="230" width="170" height="190" />
          <rect x="1210" y="270" width="170" height="150" />
        </g>

        <!-- 中央主楼（古典学院建筑） -->
        <g fill="#0c2552">
          <rect x="560" y="200" width="320" height="220" />
          <!-- 三角山墙 -->
          <polygon points="540,200 720,110 900,200" />
          <!-- 立柱门廊 -->
          <rect x="566" y="220" width="14" height="200" />
          <rect x="612" y="220" width="14" height="200" />
          <rect x="658" y="220" width="14" height="200" />
          <rect x="768" y="220" width="14" height="200" />
          <rect x="814" y="220" width="14" height="200" />
          <rect x="860" y="220" width="14" height="200" />
          <!-- 钟楼 -->
          <rect x="690" y="60" width="60" height="80" />
          <circle cx="720" cy="55" r="34" />
        </g>
        <circle cx="720" cy="100" r="13" fill="#0a1c3f" />
        <line x1="720" y1="100" x2="720" y2="90" stroke="#ffd98a" stroke-width="2" />
        <line x1="720" y1="100" x2="728" y2="100" stroke="#ffd98a" stroke-width="2" />

        <!-- 灯光窗格 -->
        <g fill="#ffd27a" opacity=".85">
          <rect x="90" y="280" width="16" height="22" /><rect x="124" y="280" width="16" height="22" /><rect x="158" y="280" width="16" height="22" /><rect x="192" y="280" width="16" height="22" />
          <rect x="90" y="320" width="16" height="22" /><rect x="158" y="320" width="16" height="22" /><rect x="192" y="320" width="16" height="22" />
          <rect x="300" y="240" width="15" height="20" /><rect x="332" y="240" width="15" height="20" /><rect x="364" y="240" width="15" height="20" /><rect x="396" y="240" width="15" height="20" />
          <rect x="300" y="280" width="15" height="20" /><rect x="364" y="280" width="15" height="20" />
          <rect x="1050" y="260" width="16" height="22" /><rect x="1086" y="260" width="16" height="22" /><rect x="1122" y="260" width="16" height="22" /><rect x="1158" y="260" width="16" height="22" />
          <rect x="1050" y="300" width="16" height="22" /><rect x="1122" y="300" width="16" height="22" />
          <rect x="1240" y="300" width="15" height="20" /><rect x="1272" y="300" width="15" height="20" /><rect x="1304" y="300" width="15" height="20" />
          <rect x="700" y="260" width="40" height="60" opacity=".55" />
        </g>
      </svg>

      <!-- 漂浮的教育/科技意象 -->
      <svg class="float float-cap" viewBox="0 0 64 64"><path d="M32 14 4 26l28 12 22-9.4V42h4V26z" fill="rgba(255,255,255,.9)"/><path d="M16 34v8c0 4 7.2 7 16 7s16-3 16-7v-8l-16 6.8z" fill="rgba(255,255,255,.55)"/></svg>
      <svg class="float float-book" viewBox="0 0 64 64"><path d="M10 14c8-3 16-3 22 1v38c-6-4-14-4-22-1z" fill="rgba(255,255,255,.85)"/><path d="M54 14c-8-3-16-3-22 1v38c6-4 14-4 22-1z" fill="rgba(255,255,255,.6)"/></svg>
      <svg class="float float-code" viewBox="0 0 64 64"><g fill="none" stroke="rgba(255,255,255,.8)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"><path d="M24 20 12 32l12 12"/><path d="M40 20l12 12-12 12"/></g></svg>
    </div>

    <!-- 内容 -->
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
  background: radial-gradient(120% 120% at 15% 10%, #1b3e83 0%, #102a5c 45%, #081a3d 100%);
}

/* ===== 背景层 ===== */
.auth-bg { position: absolute; inset: 0; overflow: hidden; }
.glow { position: absolute; border-radius: 50%; filter: blur(70px); opacity: .55; }
.glow-a { width: 460px; height: 460px; top: -120px; left: -80px; background: radial-gradient(circle, #2f6bff, transparent 70%); }
.glow-b { width: 520px; height: 520px; bottom: -160px; right: -120px; background: radial-gradient(circle, #14b8a6, transparent 70%); opacity: .4; }
.auth-net { position: absolute; top: 0; left: 0; width: 60%; height: 60%; opacity: .8; }
.auth-campus { position: absolute; bottom: 0; left: 0; width: 100%; height: 46%; opacity: .92; }

.float { position: absolute; width: 56px; height: 56px; opacity: .5; animation: floaty 7s ease-in-out infinite; }
.float-cap { top: 16%; right: 18%; animation-delay: 0s; }
.float-book { top: 60%; left: 9%; width: 46px; height: 46px; animation-delay: 1.6s; }
.float-code { top: 30%; right: 32%; width: 44px; height: 44px; animation-delay: .8s; }
@keyframes floaty { 0%, 100% { transform: translateY(0) rotate(-3deg); } 50% { transform: translateY(-14px) rotate(3deg); } }

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

.auth-brand { color: #eaf1ff; }
.brand-row { display: flex; align-items: center; gap: 12px; margin-bottom: 30px; }
.brand-mark {
  display: grid; place-items: center; width: 44px; height: 44px; border-radius: 12px;
  font-size: 22px; font-weight: 800; color: #fff;
  background: linear-gradient(135deg, #3b82f6, #2f6bff); box-shadow: 0 8px 22px rgba(47, 107, 255, .45);
}
.brand-row strong { font-size: 22px; letter-spacing: .04em; }
.auth-brand h1 { margin: 0 0 16px; font-size: 40px; line-height: 1.22; font-weight: 800; letter-spacing: -.01em; }
.auth-brand > p { margin: 0 0 26px; max-width: 460px; color: #b8c8ea; font-size: 15px; line-height: 1.8; }
.brand-points { list-style: none; margin: 0; padding: 0; display: grid; gap: 13px; }
.brand-points li { display: flex; align-items: center; gap: 10px; color: #d4e0f7; font-size: 14.5px; }
.brand-points i { width: 7px; height: 7px; border-radius: 50%; background: #4ade80; box-shadow: 0 0 0 4px rgba(74, 222, 128, .18); }

/* ===== 登录卡片 ===== */
.auth-card {
  background: rgba(255, 255, 255, .96);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, .6);
  border-radius: 20px;
  padding: 36px 36px 30px;
  box-shadow: 0 30px 70px rgba(8, 22, 55, .45);
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

@media (max-width: 920px) {
  .auth-content { grid-template-columns: 1fr; max-width: 440px; gap: 26px; }
  .auth-brand { text-align: center; }
  .auth-brand h1 { font-size: 30px; }
  .auth-brand > p, .brand-points { display: none; }
  .brand-row { justify-content: center; margin-bottom: 4px; }
}
@media (max-width: 520px) {
  .auth-card { padding: 26px 22px; }
  .role-grid { grid-template-columns: 1fr; }
}
</style>

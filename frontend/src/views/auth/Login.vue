<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  ArrowRight,
  BarChart3,
  BookOpen,
  BriefcaseBusiness,
  ClipboardCheck,
  ContactRound,
  FileSearch,
  GraduationCap,
  LayoutDashboard,
  LockKeyhole,
  Presentation,
  ShieldCheck,
  Sparkles,
  UserRound,
  UsersRound,
} from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { roleCredentials, roleLabels } from '../../router/route-data'

const VIDEO_URL = 'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260505_101331_74f9b798-3f00-4e86-8a01-377aa16ffeaa.mp4'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const formRef = ref()
const accountInput = ref()
const capabilitySection = ref()
const loading = ref(false)
const form = reactive({ role: 'teacher', account: 'teacher', password: '123456' })

const roles = [
  { value: 'student', title: '学生', description: '完成实训与查看反馈', icon: GraduationCap },
  { value: 'teacher', title: '教师', description: '组织项目与评价成果', icon: Presentation },
  { value: 'enterprise', title: '企业导师', description: '协同指导与岗位评价', icon: BriefcaseBusiness },
  { value: 'admin', title: '系统管理员', description: '维护组织与运行规则', icon: ShieldCheck },
]

const capabilities = [
  { name: '课程组织', icon: BookOpen, colors: ['#60a5fa', '#2563eb'] },
  { name: '实训项目', icon: BriefcaseBusiness, colors: ['#fde68a', '#f59e0b'] },
  { name: '任务中心', icon: ClipboardCheck, colors: ['#67e8f9', '#0891b2'] },
  { name: '过程辅导', icon: Sparkles, colors: ['#c4b5fd', '#8b5cf6'] },
  { name: '多方评价', icon: UsersRound, colors: ['#fda4af', '#e11d48'] },
  { name: '能力画像', icon: ContactRound, colors: ['#bef264', '#16a34a'] },
  { name: '数据报表', icon: BarChart3, colors: ['#bae6fd', '#0284c7'] },
  { name: '实训大屏', icon: LayoutDashboard, colors: ['#5eead4', '#0f766e'] },
]

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

function showGuide() {
  ElMessage.info('选择身份后，演示账号会自动填充，直接进入对应工作台即可。')
}

function showContact() {
  ElMessage.info('比赛演示环境已开启，系统问题请联系平台管理员。')
}

function focusLogin() {
  accountInput.value?.focus?.()
}

function showCapabilities() {
  capabilitySection.value?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

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
  <main class="epoch-login">
    <section class="login-hero" aria-labelledby="login-hero-title">
      <div class="hero-video-layer" aria-hidden="true">
        <video :src="VIDEO_URL" autoplay loop muted playsinline class="hero-video"></video>
      </div>

      <div class="hero-content">
        <div class="hero-copy">
          <div class="hero-brand">
            <span class="hero-brand-mark"><img src="/logo.svg" alt="" /></span>
            <span><strong>智训评</strong><small>SmartTrainEval</small></span>
          </div>
          <p class="hero-kicker">软件实训协同评价平台</p>
          <h1 id="login-hero-title">让每一次实训，<br />都形成可信能力证据</h1>
          <p class="hero-summary">贯通课程、项目、过程辅导与多方评价，为学生沉淀成长档案，为教师提供清晰、可追踪的教学依据。</p>
          <button class="hero-action" type="button" @click="showCapabilities">
            了解平台
            <ArrowRight :size="16" aria-hidden="true" />
          </button>
        </div>

        <section class="login-panel" aria-labelledby="login-title">
          <div class="login-panel-head">
            <span class="login-panel-icon"><FileSearch :size="19" aria-hidden="true" /></span>
            <div>
              <h2 id="login-title">进入工作台</h2>
              <p>选择身份，继续今天的实训任务</p>
            </div>
          </div>

          <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="submit">
            <el-form-item label="登录身份" prop="role">
              <el-radio-group v-model="form.role" class="role-selector" aria-label="登录身份">
                <el-radio v-for="role in roles" :key="role.value" :value="role.value" class="role-option">
                  <component :is="role.icon" :size="17" :stroke-width="1.8" aria-hidden="true" />
                  <span><strong>{{ role.title }}</strong><small>{{ role.description }}</small></span>
                </el-radio>
              </el-radio-group>
            </el-form-item>

            <div class="credential-grid">
              <el-form-item label="账号" prop="account">
                <el-input ref="accountInput" v-model="form.account" autocomplete="username" placeholder="请输入账号">
                  <template #prefix><UserRound :size="16" aria-hidden="true" /></template>
                </el-input>
              </el-form-item>
              <el-form-item label="密码" prop="password">
                <el-input v-model="form.password" type="password" show-password autocomplete="current-password" placeholder="请输入密码" @keyup.enter="submit">
                  <template #prefix><LockKeyhole :size="16" aria-hidden="true" /></template>
                </el-input>
              </el-form-item>
            </div>

            <div class="login-utilities">
              <el-checkbox>记住登录状态</el-checkbox>
              <button type="button" @click="showContact">忘记密码？</button>
            </div>

            <button class="login-submit" type="submit" :disabled="loading">
              <span>{{ loading ? '正在进入...' : '进入工作台' }}</span>
              <ArrowRight :size="16" aria-hidden="true" />
            </button>
            <p class="demo-tip">演示账号已自动填充，默认密码为 123456</p>
          </el-form>
        </section>
      </div>

      <div class="floating-nav-wrap">
        <nav class="floating-nav" aria-label="登录页导航">
          <button class="nav-logo" type="button" aria-label="定位登录表单" @click="focusLogin"><img src="/logo.svg" alt="" /></button>
          <button type="button" @click="showCapabilities">产品能力</button>
          <button type="button" @click="showGuide">使用指南</button>
          <button class="nav-contact" type="button" @click="showContact">联系我们 <ArrowRight :size="14" aria-hidden="true" /></button>
        </nav>
      </div>
    </section>

    <section ref="capabilitySection" class="capability-marquee" aria-label="平台能力">
      <div class="marquee-track">
        <template v-for="copy in 2" :key="copy">
          <article
            v-for="item in capabilities"
            :key="`${copy}-${item.name}`"
            class="capability-pill"
            :style="{ '--glow-from': item.colors[0], '--glow-to': item.colors[1] }"
            :aria-hidden="copy === 2"
          >
            <span class="capability-glow" aria-hidden="true"></span>
            <component :is="item.icon" :size="23" :stroke-width="1.7" aria-hidden="true" />
            <strong>{{ item.name }}</strong>
          </article>
        </template>
      </div>
    </section>
  </main>
</template>

<style scoped>
.epoch-login {
  min-height: 100vh;
  padding: 24px 20px 36px;
  overflow: hidden;
  color: #0a1b33;
  background: #f9fafb;
  font-family: var(--font-sans);
}

.login-hero {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1400px;
  height: 600px;
  margin: 0 auto;
  overflow: hidden;
  background: #fff;
  border: 1px solid rgba(226, 232, 240, .5);
  border-radius: 48px;
  box-shadow: 0 40px 100px -20px rgba(0, 0, 0, .03);
}

.hero-video-layer {
  position: absolute;
  z-index: 0;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  user-select: none;
}

.hero-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.05);
  transition: transform 1s ease;
}

.login-hero:hover .hero-video { transform: scale(1.02); }

.hero-content {
  position: relative;
  z-index: 20;
  display: grid;
  flex: 1;
  grid-template-columns: minmax(0, 1fr) 410px;
  gap: 56px;
  align-items: start;
  padding: 48px 64px 112px;
}

.hero-copy {
  max-width: 610px;
  animation: copy-enter .72s cubic-bezier(.22, 1, .36, 1) both;
}

.hero-brand {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 44px;
}

.hero-brand-mark {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  background: rgba(255, 255, 255, .92);
  border: 1px solid rgba(226, 232, 240, .72);
  border-radius: 50%;
  box-shadow: 0 8px 22px rgba(15, 23, 42, .06);
}

.hero-brand-mark img { width: 25px; height: 25px; }
.hero-brand > span:last-child { display: grid; }
.hero-brand strong { font-family: var(--font-display); font-size: 16px; font-weight: 600; }
.hero-brand small { color: #64748b; font-size: 10px; }
.hero-kicker { margin: 0 0 14px; color: #2563eb; font-size: 13px; font-weight: 600; }

.hero-copy h1 {
  margin: 0;
  color: #0a1b33;
  font-family: var(--font-display);
  font-size: 54px;
  font-weight: 500;
  line-height: 1.08;
  letter-spacing: 0;
}

.hero-summary {
  max-width: 535px;
  margin: 22px 0 28px;
  color: #64748b;
  font-size: 15px;
  line-height: 1.8;
}

.hero-action,
.login-submit,
.floating-nav button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  cursor: pointer;
}

.hero-action {
  gap: 9px;
  min-height: 44px;
  padding: 0 22px;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  background: #0a152d;
  border-radius: 999px;
  box-shadow: 0 12px 26px rgba(10, 21, 45, .14);
  transition: transform .22s ease, box-shadow .22s ease;
}

.hero-action:hover { transform: scale(1.04); box-shadow: 0 16px 32px rgba(10, 21, 45, .2); }
.hero-action:active { transform: scale(.98); }

.login-panel {
  width: 100%;
  padding: 24px;
  background: rgba(255, 255, 255, .88);
  border: 1px solid rgba(255, 255, 255, .72);
  border-radius: 26px;
  box-shadow: 0 24px 70px rgba(15, 23, 42, .1);
  backdrop-filter: blur(24px);
  animation: panel-enter .74s .12s cubic-bezier(.22, 1, .36, 1) both;
}

.login-panel-head {
  display: flex;
  gap: 11px;
  align-items: center;
  margin-bottom: 18px;
}

.login-panel-icon {
  display: grid;
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  place-items: center;
  color: #0a152d;
  background: #fff;
  border: 1px solid rgba(226, 232, 240, .8);
  border-radius: 50%;
  box-shadow: 0 6px 16px rgba(15, 23, 42, .05);
}

.login-panel-head h2 { margin: 0 0 3px; font-family: var(--font-display); font-size: 20px; font-weight: 600; }
.login-panel-head p { margin: 0; color: #64748b; font-size: 12px; }
.login-panel :deep(.el-form-item) { margin-bottom: 14px; }
.login-panel :deep(.el-form-item__label) { height: auto; margin-bottom: 6px; color: #334155; font-size: 12px; font-weight: 600; line-height: 1.4; }

.role-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 7px;
  width: 100%;
}

.role-selector :deep(.role-option.el-radio) {
  display: flex;
  align-items: center;
  min-width: 0;
  height: 60px;
  margin: 0;
  padding: 8px 10px;
  color: #64748b;
  background: rgba(255, 255, 255, .74);
  border: 1px solid rgba(203, 213, 225, .68);
  border-radius: 14px;
  transition: border-color .2s ease, background-color .2s ease, transform .2s ease;
}

.role-selector :deep(.role-option.el-radio:hover) { transform: translateY(-1px); border-color: #94a3b8; }
.role-selector :deep(.role-option .el-radio__input) { display: none; }
.role-selector :deep(.role-option .el-radio__label) { display: flex; gap: 8px; align-items: center; min-width: 0; width: 100%; padding: 0; color: inherit; }
.role-selector :deep(.role-option .el-radio__label > span) { display: grid; min-width: 0; }
.role-selector :deep(.role-option strong) { overflow: hidden; color: #0f172a; font-size: 12px; font-weight: 600; text-overflow: ellipsis; white-space: nowrap; }
.role-selector :deep(.role-option small) { overflow: hidden; color: #94a3b8; font-size: 9px; text-overflow: ellipsis; white-space: nowrap; }
.role-selector :deep(.role-option.is-checked) { color: #2563eb; background: #fff; border-color: #3b82f6; box-shadow: 0 6px 18px rgba(37, 99, 235, .08); }

.credential-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 9px; }
.login-panel :deep(.el-input__wrapper) { min-height: 40px; background: rgba(255, 255, 255, .82); border-radius: 14px; box-shadow: 0 0 0 1px rgba(203, 213, 225, .72) inset; }
.login-panel :deep(.el-input__wrapper:hover) { box-shadow: 0 0 0 1px #94a3b8 inset; }
.login-panel :deep(.el-input__wrapper.is-focus) { box-shadow: 0 0 0 1px #2563eb inset !important; }
.login-panel :deep(.el-input__prefix) { color: #94a3b8; }

.login-utilities {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: -2px 0 12px;
}

.login-utilities :deep(.el-checkbox__label) { color: #64748b; font-size: 11px; }
.login-utilities button { padding: 0; color: #2563eb; font-size: 11px; background: transparent; border: 0; cursor: pointer; }

.login-submit {
  gap: 9px;
  width: 100%;
  min-height: 42px;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  background: #0a152d;
  border-radius: 999px;
  transition: transform .22s ease, background-color .22s ease;
}

.login-submit:hover:not(:disabled) { transform: scale(1.015); background: #13203b; }
.login-submit:active:not(:disabled) { transform: scale(.99); }
.login-submit:disabled { cursor: wait; opacity: .72; }
.demo-tip { margin: 9px 0 0; color: #94a3b8; font-size: 10px; text-align: center; }

.floating-nav-wrap {
  position: absolute;
  z-index: 30;
  bottom: 26px;
  left: 50%;
  transform: translateX(-50%);
}

.floating-nav {
  display: flex;
  gap: 2px;
  align-items: center;
  padding: 6px;
  background: rgba(255, 255, 255, .9);
  border: 1px solid rgba(226, 232, 240, .4);
  border-radius: 999px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, .08);
  backdrop-filter: blur(24px);
  animation: nav-enter .64s .28s cubic-bezier(.22, 1, .36, 1) both;
}

.floating-nav button {
  min-height: 36px;
  padding: 0 15px;
  color: #64748b;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  background: transparent;
  border-radius: 999px;
  transition: color .2s ease, background-color .2s ease, transform .2s ease;
}

.floating-nav button:hover { color: #0a1b33; background: #fff; }
.floating-nav .nav-logo { width: 36px; min-width: 36px; height: 36px; padding: 0; background: #fff; border: 1px solid #f1f5f9; box-shadow: 0 3px 10px rgba(15, 23, 42, .05); }
.nav-logo img { width: 22px; height: 22px; }
.floating-nav .nav-contact { gap: 5px; padding: 0 18px; color: #0a1b33; background: #fff; border: 1px solid rgba(203, 213, 225, .6); box-shadow: 0 3px 10px rgba(15, 23, 42, .05); }
.floating-nav .nav-contact:hover { border-color: #cbd5e1; transform: translateX(2px); }

.capability-marquee {
  width: 100%;
  max-width: 1400px;
  margin: 40px auto 0;
  overflow: hidden;
  mask-image: linear-gradient(to right, transparent, #000 9%, #000 91%, transparent);
}

.marquee-track {
  display: flex;
  gap: 16px;
  width: max-content;
  animation: marquee 34s linear infinite;
  will-change: transform;
}

.capability-marquee:hover .marquee-track { animation-play-state: paused; }

.capability-pill {
  position: relative;
  display: flex;
  width: 160px;
  height: 96px;
  flex: 0 0 160px;
  gap: 9px;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  color: #0a1b33;
  background: #fff;
  border: 1px solid rgba(203, 213, 225, .6);
  border-radius: 999px;
  box-shadow: 0 3px 12px rgba(15, 23, 42, .04);
  transition: border-color .2s ease, transform .2s ease;
}

.capability-pill:hover { color: #07111f; border-color: #cbd5e1; transform: translateY(-2px); }
.capability-pill > svg, .capability-pill > strong { position: relative; z-index: 1; }
.capability-pill strong { font-size: 12px; font-weight: 600; }
.capability-glow { position: absolute; inset: 0; background: linear-gradient(135deg, var(--glow-from), var(--glow-to)); opacity: 0; transform: scale(1.5); transition: opacity .3s ease, transform .3s ease; }
.capability-pill:hover .capability-glow { opacity: 1; transform: scale(1); }

@keyframes marquee { from { transform: translateX(0); } to { transform: translateX(calc(-50% - 8px)); } }
@keyframes copy-enter { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: translateY(0); } }
@keyframes panel-enter { from { opacity: 0; transform: translateY(22px) scale(.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
@keyframes nav-enter { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 1120px) {
  .hero-content { grid-template-columns: minmax(0, 1fr) 380px; gap: 32px; padding-right: 40px; padding-left: 40px; }
  .hero-copy h1 { font-size: 46px; }
  .hero-summary { max-width: 460px; }
}

@media (max-width: 860px) {
  .epoch-login { padding: 14px 12px 28px; }
  .login-hero { height: auto; min-height: 850px; border-radius: 32px; }
  .hero-video { object-position: 62% center; }
  .hero-content { grid-template-columns: 1fr; gap: 24px; padding: 30px 28px 116px; }
  .hero-brand { margin-bottom: 26px; }
  .hero-copy { max-width: 560px; }
  .hero-copy h1 { font-size: 42px; }
  .hero-summary { margin: 16px 0 20px; }
  .login-panel { max-width: 520px; justify-self: end; }
}

@media (max-width: 560px) {
  .login-hero { min-height: 930px; border-radius: 26px; }
  .hero-content { padding: 24px 18px 122px; }
  .hero-copy h1 { font-size: 36px; }
  .hero-summary { font-size: 13px; }
  .login-panel { padding: 20px; border-radius: 22px; }
  .credential-grid { grid-template-columns: 1fr; gap: 0; }
  .role-selector { grid-template-columns: 1fr; }
  .floating-nav button:not(.nav-logo):not(.nav-contact) { display: none; }
  .capability-marquee { margin-top: 24px; }
  .capability-pill { width: 144px; height: 82px; flex-basis: 144px; }
}

@media (prefers-reduced-motion: reduce) {
  .hero-copy, .login-panel, .floating-nav, .marquee-track { animation: none; }
  .hero-video, .hero-action, .login-submit, .capability-pill { transition: none; }
}
</style>

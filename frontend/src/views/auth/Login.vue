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
    <!-- 蓝白动态高校实训教学背景 -->
    <svg class="auth-scene" viewBox="0 0 1440 820" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#eef5ff" /><stop offset=".55" stop-color="#d8e8ff" /><stop offset="1" stop-color="#c6dcfb" />
        </linearGradient>
        <linearGradient id="screen" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#eaf3ff" /><stop offset="1" stop-color="#cfe2ff" />
        </linearGradient>
      </defs>

      <rect width="1440" height="820" fill="url(#sky)" />

      <!-- 漂浮的云 -->
      <g fill="#ffffff" opacity=".7">
        <g><animateTransform attributeName="transform" type="translate" values="0 0;70 0;0 0" dur="26s" repeatCount="indefinite"/>
          <ellipse cx="240" cy="120" rx="70" ry="26"/><ellipse cx="300" cy="108" rx="54" ry="24"/></g>
        <g opacity=".75"><animateTransform attributeName="transform" type="translate" values="0 0;-60 0;0 0" dur="32s" repeatCount="indefinite"/>
          <ellipse cx="1080" cy="150" rx="80" ry="28"/><ellipse cx="1150" cy="138" rx="56" ry="24"/></g>
      </g>

      <!-- 知识网络（脉冲节点） -->
      <g stroke="#9cc0f5" stroke-width="1.4" fill="none" opacity=".7">
        <path d="M170 250 L320 200 L470 280 M320 200 L300 330"/>
      </g>
      <g fill="#2f6bff">
        <circle cx="170" cy="250" r="4"><animate attributeName="r" values="4;7;4" dur="2.6s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;.5;1" dur="2.6s" repeatCount="indefinite"/></circle>
        <circle cx="320" cy="200" r="5"><animate attributeName="r" values="5;8;5" dur="3.2s" repeatCount="indefinite"/></circle>
        <circle cx="470" cy="280" r="4"><animate attributeName="r" values="4;7;4" dur="2.9s" repeatCount="indefinite"/></circle>
        <circle cx="300" cy="330" r="3.5"><animate attributeName="r" values="3.5;6;3.5" dur="2.3s" repeatCount="indefinite"/></circle>
      </g>

      <!-- 高校建筑群 -->
      <g>
        <!-- 左教学楼 -->
        <rect x="120" y="430" width="230" height="150" fill="#c4d9f6"/>
        <g fill="#ffffff" opacity=".85">
          <rect x="150" y="455" width="22" height="28"/><rect x="186" y="455" width="22" height="28"/><rect x="222" y="455" width="22" height="28"/><rect x="258" y="455" width="22" height="28"/><rect x="294" y="455" width="22" height="28"/>
          <rect x="150" y="500" width="22" height="28"/><rect x="222" y="500" width="22" height="28"/><rect x="294" y="500" width="22" height="28"/>
        </g>
        <!-- 中央主楼（古典学院建筑） -->
        <polygon points="560,360 730,290 900,360" fill="#b6cef2"/>
        <rect x="585" y="360" width="290" height="220" fill="#c9dcf7"/>
        <g fill="#aecbf2"><rect x="600" y="380" width="16" height="200"/><rect x="640" y="380" width="16" height="200"/><rect x="680" y="380" width="16" height="200"/><rect x="764" y="380" width="16" height="200"/><rect x="804" y="380" width="16" height="200"/><rect x="844" y="380" width="16" height="200"/></g>
        <rect x="705" y="250" width="50" height="60" fill="#b6cef2"/>
        <circle cx="730" cy="246" r="26" fill="#b6cef2"/>
        <line x1="730" y1="222" x2="730" y2="206" stroke="#8fb4ee" stroke-width="3"/>
        <circle cx="730" cy="270" r="9" fill="#ffffff"/>
        <!-- 右实训楼 -->
        <rect x="1010" y="400" width="300" height="180" fill="#bcd4f5"/>
        <g fill="#ffffff" opacity=".8">
          <rect x="1040" y="425" width="26" height="30"/><rect x="1086" y="425" width="26" height="30"/><rect x="1132" y="425" width="26" height="30"/><rect x="1178" y="425" width="26" height="30"/><rect x="1224" y="425" width="26" height="30"/><rect x="1270" y="425" width="26" height="30"/>
          <rect x="1040" y="475" width="26" height="30"/><rect x="1132" y="475" width="26" height="30"/><rect x="1224" y="475" width="26" height="30"/>
        </g>
      </g>

      <!-- 地面 -->
      <rect x="0" y="580" width="1440" height="240" fill="#b3d0f4"/>
      <rect x="0" y="580" width="1440" height="10" fill="#a6c7f1"/>

      <!-- 流动的成长路径 + 移动光点 -->
      <path id="flowpath" d="M120 640 C320 600 360 720 560 670 C760 620 820 730 1020 680" fill="none" stroke="#2f6bff" stroke-width="3" stroke-dasharray="2 12" stroke-linecap="round" opacity=".55">
        <animate attributeName="stroke-dashoffset" values="0;-140" dur="4s" repeatCount="indefinite"/>
      </path>
      <circle r="6" fill="#2f6bff"><animateMotion dur="6s" repeatCount="indefinite"><mpath href="#flowpath"/></animateMotion></circle>

      <!-- 实训机房：教师 + 学生工位 -->
      <!-- 讲台教师 -->
      <g>
        <rect x="150" y="470" width="92" height="64" rx="6" fill="#dbe8fb" stroke="#9cc0f5" stroke-width="2"/>
        <line x1="196" y1="534" x2="196" y2="560" stroke="#9cc0f5" stroke-width="3"/>
        <circle cx="300" cy="600" r="16" fill="#5b8fe0"/>
        <path d="M276 686 v-46 a24 24 0 0 1 48 0 v46 Z" fill="#6f9fe6"/>
        <path d="M324 648 l40 -30" stroke="#6f9fe6" stroke-width="10" stroke-linecap="round"/>
      </g>

      <!-- 学生工位（头 + 显示器，屏幕闪烁） -->
      <g>
        <!-- 长桌 -->
        <rect x="430" y="700" width="640" height="16" rx="4" fill="#5b8fe0"/>
        <g>
          <!-- 工位 1 -->
          <circle cx="480" cy="636" r="15" fill="#6f9fe6"/><path d="M459 700 v-34 a21 21 0 0 1 42 0 v34 Z" fill="#7fa8e6"/>
          <rect x="452" y="668" width="56" height="38" rx="3" fill="#4f86e8"/><rect x="457" y="673" width="46" height="28" rx="2" fill="url(#screen)"><animate attributeName="opacity" values="1;.55;1" dur="3.4s" repeatCount="indefinite"/></rect>
          <!-- 工位 2 -->
          <circle cx="620" cy="636" r="15" fill="#6f9fe6"/><path d="M599 700 v-34 a21 21 0 0 1 42 0 v34 Z" fill="#7fa8e6"/>
          <rect x="592" y="668" width="56" height="38" rx="3" fill="#4f86e8"/><rect x="597" y="673" width="46" height="28" rx="2" fill="url(#screen)"><animate attributeName="opacity" values="1;.6;1" dur="2.8s" repeatCount="indefinite"/></rect>
          <!-- 工位 3 -->
          <circle cx="760" cy="636" r="15" fill="#6f9fe6"/><path d="M739 700 v-34 a21 21 0 0 1 42 0 v34 Z" fill="#7fa8e6"/>
          <rect x="732" y="668" width="56" height="38" rx="3" fill="#4f86e8"/><rect x="737" y="673" width="46" height="28" rx="2" fill="url(#screen)"><animate attributeName="opacity" values="1;.5;1" dur="3.9s" repeatCount="indefinite"/></rect>
          <!-- 工位 4 -->
          <circle cx="900" cy="636" r="15" fill="#6f9fe6"/><path d="M879 700 v-34 a21 21 0 0 1 42 0 v34 Z" fill="#7fa8e6"/>
          <rect x="872" y="668" width="56" height="38" rx="3" fill="#4f86e8"/><rect x="877" y="673" width="46" height="28" rx="2" fill="url(#screen)"><animate attributeName="opacity" values="1;.62;1" dur="3.1s" repeatCount="indefinite"/></rect>
        </g>
      </g>

      <!-- 漂浮的学士帽 / 书 / 齿轮 -->
      <g transform="translate(1015 250)" opacity=".9">
        <animateTransform attributeName="transform" type="translate" values="1015 250;1015 232;1015 250" dur="6s" repeatCount="indefinite" additive="sum"/>
        <path d="M0 0 -34 14 0 28 34 14 Z" fill="#2f57e0"/><path d="M-20 20 v12 c0 6 40 6 40 0 v-12 l-20 8 Z" fill="#19a7e6"/>
      </g>
      <g opacity=".85">
        <animateTransform attributeName="transform" type="translate" values="0 0;0 -16;0 0" dur="5s" repeatCount="indefinite"/>
        <path d="M430 250 c10 -5 22 -5 30 1 v34 c-8 -6 -20 -6 -30 -1 Z" fill="#19a7e6"/>
        <path d="M492 250 c-10 -5 -22 -5 -30 1 v34 c8 -6 20 -6 30 -1 Z" fill="#2f57e0"/>
      </g>
      <g transform="translate(980 360)" opacity=".5">
        <g><animateTransform attributeName="transform" type="rotate" from="0 0 0" to="360 0 0" dur="16s" repeatCount="indefinite"/>
          <path d="M-4 -22 h8 l2 8 6 3 7 -4 6 6 -4 7 3 6 8 2 v8 l-8 2 -3 6 4 7 -6 6 -7 -4 -6 3 -2 8 h-8 l-2 -8 -6 -3 -7 4 -6 -6 4 -7 -3 -6 -8 -2 v-8 l8 -2 3 -6 -4 -7 6 -6 7 4 6 -3 Z" fill="#8fb4ee"/>
          <circle r="8" fill="#d8e8ff"/>
        </g>
      </g>
    </svg>

    <div class="auth-content">
      <aside class="auth-brand">
        <div class="brand-row"><span class="brand-mark"><img src="/logo.svg" alt="" /></span><strong>智训评</strong></div>
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
  background: #e7f0ff;
}
.auth-scene { position: absolute; inset: 0; width: 100%; height: 100%; }

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

.auth-brand { color: #16233f; }
.brand-row { display: flex; align-items: center; gap: 12px; margin-bottom: 30px; }
.brand-mark {
  display: grid; place-items: center; width: 46px; height: 46px; border-radius: 13px;
  background: #fff; box-shadow: 0 8px 22px rgba(33, 82, 180, .22);
}
.brand-mark img { width: 34px; height: 34px; display: block; }
.brand-row strong { font-size: 22px; letter-spacing: .04em; color: #14213d; }
.auth-brand h1 { margin: 0 0 16px; font-size: 40px; line-height: 1.22; font-weight: 800; letter-spacing: -.01em; color: #15264a; }
.auth-brand > p { margin: 0 0 26px; max-width: 460px; color: #41527a; font-size: 15px; line-height: 1.8; }
.brand-points { list-style: none; margin: 0; padding: 0; display: grid; gap: 13px; }
.brand-points li { display: flex; align-items: center; gap: 10px; color: #2c3e63; font-size: 14.5px; font-weight: 500; }
.brand-points i { width: 7px; height: 7px; border-radius: 50%; background: #2f6bff; box-shadow: 0 0 0 4px rgba(47, 107, 255, .16); }

.auth-card {
  background: rgba(255, 255, 255, .98);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, .8);
  border-radius: 20px;
  padding: 36px 36px 30px;
  box-shadow: 0 30px 70px rgba(20, 50, 110, .26);
}
.card-head { margin-bottom: 22px; }
.card-kicker { color: #2f6bff; font-size: 12px; font-weight: 700; letter-spacing: .14em; }
.card-head h2 { margin: 8px 0 6px; font-size: 26px; color: #16203a; font-weight: 750; }
.card-head p { margin: 0; color: #7a8499; font-size: 13.5px; }

.role-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; width: 100%; }
.role-grid :deep(.el-radio.role-choice) { height: auto; margin: 0; padding: 11px 12px; border-radius: 12px; align-items: flex-start; }
.role-grid :deep(.el-radio.role-choice .el-radio__label) { display: flex; flex-direction: column; gap: 2px; padding-left: 8px; }
.role-grid :deep(.el-radio.role-choice strong) { font-size: 14px; color: #1f2a44; }
.role-grid :deep(.el-radio.role-choice span) { font-size: 11.5px; color: #97a1b5; line-height: 1.35; }
.role-grid :deep(.el-radio.role-choice.is-checked) { border-color: #2f6bff; background: #f2f6ff; }
.role-grid :deep(.el-radio.role-choice.is-checked strong) { color: #2f6bff; }

.login-utilities { display: flex; align-items: center; justify-content: space-between; margin: 4px 0 18px; font-size: 13px; }
.login-utilities a { color: #2f6bff; text-decoration: none; }
.login-submit { width: 100%; height: 46px; font-size: 15px; font-weight: 600; letter-spacing: .06em; border: none; background: linear-gradient(135deg, #3b82f6, #2f6bff); box-shadow: 0 12px 26px rgba(47, 107, 255, .38); }
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

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const lang = ref(localStorage.getItem('ml_lang') || 'ar')
const dir = computed(() => (lang.value === 'ar' ? 'rtl' : 'ltr'))
const t = (key) => ({
  en: {
    signin: 'Sign In',
    signup: 'Create Account',
    username: 'Username',
    password: 'Password',
    confirm: 'Confirm Password',
    login: 'Login',
    register: 'Signup',
    toSignup: 'Create account',
    toSignin: 'Back to login',
    forgot: 'Forgot password?'
  },
  ar: {
    signin: 'تسجيل الدخول',
    signup: 'إنشاء حساب',
    username: 'اسم المستخدم',
    password: 'كلمة المرور',
    confirm: 'تأكيد كلمة المرور',
    login: 'دخول',
    register: 'تسجيل',
    toSignup: 'إنشاء حساب',
    toSignin: 'العودة لتسجيل الدخول',
    forgot: 'نسيت كلمة المرور؟'
  }
}[lang.value][key])

const isArabic = computed(() => lang.value === 'ar')
function toggleLang() {
  lang.value = isArabic.value ? 'en' : 'ar'
}

const theme = ref(localStorage.getItem('ml_theme') || 'light')
const isDark = computed(() => theme.value === 'dark')
const themeToggleText = computed(() => (isArabic.value ? (isDark.value ? 'فاتح' : 'داكن') : isDark.value ? 'Light' : 'Dark'))
const themeAria = computed(() =>
  isArabic.value
    ? isDark.value
      ? 'التبديل إلى الوضع الفاتح'
      : 'التبديل إلى الوضع الداكن'
    : isDark.value
    ? 'Switch to light theme'
    : 'Switch to dark theme'
)
function toggleTheme() {
  theme.value = isDark.value ? 'light' : 'dark'
}

function applyTheme(value) {
  document.documentElement.setAttribute('data-ml-theme', value)
}

watch(lang, (value) => {
  localStorage.setItem('ml_lang', value)
  document.documentElement.dir = dir.value
  document.documentElement.lang = value
})

watch(theme, (value) => {
  localStorage.setItem('ml_theme', value)
  applyTheme(value)
})

onMounted(() => {
  document.documentElement.dir = dir.value
  document.documentElement.lang = lang.value
  applyTheme(theme.value)
})

const showSignup = ref(false)
const inForm = ref({ username: '', password: '' })
const upForm = ref({ username: '', password: '', confirm: '' })
const submitting = ref(false)
const notice = ref(null)

watch(showSignup, () => {
  notice.value = null
})

const logoUrl = new URL('../assets/images/logo3.jpeg', import.meta.url).href

const heroTitle = computed(() => (isArabic.value ? 'منصة زعماء الرياضيات' : 'Mathematics Leaders Platform'))
const heroSubtitle = computed(() =>
  isArabic.value
    ? 'تعلم الرياضيات بأسلوب ممتع وتفاعلي مصمم للقادة الصغار.'
    : 'Master mathematics with playful, interactive journeys built for young leaders.'
)
const heroHighlights = computed(() =>
  isArabic.value
    ? ['برامج تفاعلية مدعومة بالذكاء الاصطناعي', 'تتبع تقدّم ذكي ومباشر', 'مجتمع محفّز من المعلمين والطلاب']
    : ['Interactive, AI-guided programmes', 'Real-time progress insights', 'A supportive teacher & student community']
)
const statBlocks = computed(() =>
  isArabic.value
    ? [
        { value: '12+', label: 'وحدة تعليمية متدرجة' },
        { value: '4K', label: 'طالب نشط' },
        { value: '92%', label: 'نسبة إكمال المهام' }
      ]
    : [
        { value: '12+', label: 'Adaptive learning tracks' },
        { value: '4K', label: 'Active learners' },
        { value: '92%', label: 'Task completion rate' }
      ]
)

const BASE = ''

async function get(url, params = {}) {
  const qs = new URLSearchParams(params).toString()
  const response = await fetch(BASE + url + (qs ? `?${qs}` : ''), {
    method: 'GET',
    credentials: 'include'
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw data
  return data
}

function extractErr(error) {
  if (typeof error === 'string') return error
  if (error?._server_messages) {
    try {
      const list = JSON.parse(error._server_messages)
      const first = list?.[0] && JSON.parse(list[0])
      return first?.message || first?._error_message || 'Invalid Request'
    } catch {}
  }
  return error?.message || error?.exc || 'Invalid Request'
}

function goHome(profile) {
  const payload = profile || { username: inForm.value.username }
  localStorage.setItem('ml_profile', JSON.stringify({ ...payload, language: lang.value }))
  window.location.href = '/math-leaders-games/#/home'
}

async function submit() {
  submitting.value = true
  notice.value = null
  try {
    if (showSignup.value) {
      if (!upForm.value.username || !upForm.value.password || !upForm.value.confirm) {
        throw {
          message: isArabic.value ? 'الرجاء ملء كل الحقول.' : 'Please fill all fields.'
        }
      }
      if (upForm.value.password !== upForm.value.confirm) {
        throw {
          message: isArabic.value ? 'كلمتا المرور غير متطابقتين.' : 'Passwords do not match.'
        }
      }

      await get('/api/method/mathematics_leaders.api.signup_and_login.signup_user', {
        username: upForm.value.username,
        password: upForm.value.password,
        language: lang.value
      })

      const loginRes = await get('/api/method/mathematics_leaders.api.signup_and_login.verify_login', {
        usr: upForm.value.username,
        pwd: upForm.value.password
      })

      goHome(loginRes?.message?.profile || { username: upForm.value.username })
    } else {
      const loginRes = await get('/api/method/mathematics_leaders.api.signup_and_login.verify_login', {
        usr: inForm.value.username,
        pwd: inForm.value.password
      })
      goHome(loginRes?.message?.profile || { username: inForm.value.username })
    }
  } catch (error) {
    notice.value = extractErr(error)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section :class="['landing', theme]" :dir="dir">
    <div class="background" aria-hidden="true">
      <span class="glow glow-one"></span>
      <span class="glow glow-two"></span>
      <span class="glow glow-three"></span>
      <span class="grid"></span>
    </div>

    <div class="floating-controls">
      <button
        type="button"
        class="control-btn theme-toggle"
        :aria-label="themeAria"
        @click="toggleTheme"
      >
        <span class="control-icon" aria-hidden="true">
          <svg v-if="isDark" viewBox="0 0 24 24" focusable="false">
            <circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.6" />
            <line x1="12" y1="2.4" x2="12" y2="5.4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
            <line x1="12" y1="18.6" x2="12" y2="21.6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
            <line x1="2.4" y1="12" x2="5.4" y2="12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
            <line x1="18.6" y1="12" x2="21.6" y2="12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
            <line x1="5.4" y1="5.4" x2="7.7" y2="7.7" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
            <line x1="16.3" y1="16.3" x2="18.6" y2="18.6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
            <line x1="5.4" y1="18.6" x2="7.7" y2="16.3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
            <line x1="16.3" y1="7.7" x2="18.6" y2="5.4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
          </svg>
          <svg v-else viewBox="0 0 24 24" focusable="false">
            <path
              d="M15.8 21.2a7.6 7.6 0 0 1-6.9-10.6 6.9 6.9 0 0 0 8.5 8.5 7.6 7.6 0 0 1-1.6 2.1Z"
              fill="none"
              stroke="currentColor"
              stroke-width="1.6"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>
        <span class="control-text">{{ themeToggleText }}</span>
      </button>

      <button
        type="button"
        class="control-btn lang-toggle"
        :aria-label="isArabic ? 'Switch to English' : 'التبديل إلى العربية'"
        @click="toggleLang"
      >
        <span>{{ isArabic ? 'EN' : 'ع' }}</span>
      </button>
    </div>

    <div class="landing__wrapper">
      <div class="landing__intro">
        <div class="logo-card">
          <img :src="logoUrl" alt="شعار زعماء الرياضيات" />
        </div>
        <h1 class="intro__title">{{ heroTitle }}</h1>
        <p class="intro__subtitle">{{ heroSubtitle }}</p>
        <ul class="feature-grid">
          <li v-for="(feature, idx) in heroHighlights" :key="idx" class="feature-item">
            <span class="feature-index">0{{ idx + 1 }}</span>
            <span class="feature-text">{{ feature }}</span>
          </li>
        </ul>
        <div class="stats-row">
          <div v-for="(stat, idx) in statBlocks" :key="idx" class="stat-card">
            <span class="stat-value">{{ stat.value }}</span>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
        </div>
      </div>

      <div class="landing__auth">
        <div class="auth-card">
          <div class="auth-tabs" role="tablist">
            <button
              type="button"
              class="tab-btn"
              :class="{ active: !showSignup }"
              role="tab"
              :aria-selected="!showSignup"
              @click="showSignup = false"
            >
              {{ t('signin') }}
            </button>
            <button
              type="button"
              class="tab-btn"
              :class="{ active: showSignup }"
              role="tab"
              :aria-selected="showSignup"
              @click="showSignup = true"
            >
              {{ t('signup') }}
            </button>
          </div>

          <transition name="slide-fade" mode="out-in">
            <form v-if="!showSignup" key="signin" class="auth-form" @submit.prevent="submit">
              <div class="input-field">
                <label :for="isArabic ? 'signin-username-ar' : 'signin-username-en'">{{ t('username') }}</label>
                <input
                  :id="isArabic ? 'signin-username-ar' : 'signin-username-en'"
                  v-model="inForm.username"
                  type="text"
                  :placeholder="t('username')"
                  autocomplete="username"
                  required
                />
              </div>
              <div class="input-field">
                <label :for="isArabic ? 'signin-password-ar' : 'signin-password-en'">{{ t('password') }}</label>
                <input
                  :id="isArabic ? 'signin-password-ar' : 'signin-password-en'"
                  v-model="inForm.password"
                  type="password"
                  :placeholder="t('password')"
                  autocomplete="current-password"
                  required
                />
              </div>
              <div class="form-meta">
                <a href="#">{{ t('forgot') }}</a>
              </div>
              <button class="primary-btn" type="submit" :disabled="submitting">
                <span>{{ t('login') }}</span>
              </button>
              <p class="switch-text">
                {{ isArabic ? 'لا تملك حساباً؟' : "Don't have an account?" }}
                <button type="button" @click="showSignup = true">{{ t('toSignup') }}</button>
              </p>
            </form>

            <form v-else key="signup" class="auth-form" @submit.prevent="submit">
              <div class="input-field">
                <label :for="isArabic ? 'signup-username-ar' : 'signup-username-en'">{{ t('username') }}</label>
                <input
                  :id="isArabic ? 'signup-username-ar' : 'signup-username-en'"
                  v-model="upForm.username"
                  type="text"
                  :placeholder="t('username')"
                  autocomplete="username"
                  required
                />
              </div>
              <div class="input-field">
                <label :for="isArabic ? 'signup-password-ar' : 'signup-password-en'">{{ t('password') }}</label>
                <input
                  :id="isArabic ? 'signup-password-ar' : 'signup-password-en'"
                  v-model="upForm.password"
                  type="password"
                  :placeholder="t('password')"
                  autocomplete="new-password"
                  required
                />
              </div>
              <div class="input-field">
                <label :for="isArabic ? 'signup-confirm-ar' : 'signup-confirm-en'">{{ t('confirm') }}</label>
                <input
                  :id="isArabic ? 'signup-confirm-ar' : 'signup-confirm-en'"
                  v-model="upForm.confirm"
                  type="password"
                  :placeholder="t('confirm')"
                  autocomplete="new-password"
                  required
                />
              </div>
              <button class="primary-btn" type="submit" :disabled="submitting">
                <span>{{ t('register') }}</span>
              </button>
              <p class="switch-text">
                {{ isArabic ? 'لديك حساب بالفعل؟' : 'Already have an account?' }}
                <button type="button" @click="showSignup = false">{{ t('toSignin') }}</button>
              </p>
            </form>
          </transition>

          <p v-if="notice" class="auth-notice">{{ notice }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.landing {
  position: relative;
  min-height: 100vh;
  padding: clamp(32px, 6vw, 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: var(--bg-gradient);
  color: var(--text-primary);
  transition: background 0.4s ease, color 0.4s ease;
  --bg-gradient: linear-gradient(135deg, #fdfcf8 0%, #f4f6ef 45%, #e6efe2 100%);
  --text-primary: #1f2a24;
  --text-secondary: #335343;
  --accent-green: #0f8a3e;
  --accent-green-dark: #1c6b39;
  --accent-gold: #c6a034;
  --accent-gold-soft: rgba(198, 160, 52, 0.35);
  --surface: rgba(255, 255, 255, 0.92);
  --surface-soft: linear-gradient(120deg, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.65));
  --surface-card-border: rgba(198, 160, 52, 0.28);
  --surface-card-shadow: 0 30px 60px rgba(31, 42, 36, 0.18);
  --feature-shadow: 0 12px 26px rgba(15, 138, 62, 0.12);
  --stat-bg: rgba(24, 77, 45, 0.08);
  --stat-border: rgba(24, 77, 45, 0.12);
  --input-border: rgba(31, 42, 36, 0.12);
  --input-bg: rgba(255, 255, 255, 0.96);
  --input-focus-ring: rgba(15, 138, 62, 0.12);
  --notice-bg: rgba(143, 41, 33, 0.1);
  --notice-color: #8f2921;
  --grid-color: rgba(31, 42, 36, 0.06);
  --grid-opacity: 0.5;
  --floating-shadow: 0 14px 30px rgba(15, 138, 62, 0.32);
  --floating-shadow-hover: 0 18px 40px rgba(15, 138, 62, 0.36);
  --control-icon: #ffffff;
  --glow-green: rgba(15, 138, 62, 0.35);
  --glow-gold: rgba(198, 160, 52, 0.4);
  --glow-white: rgba(255, 255, 255, 0.3);
  --tab-track: rgba(24, 77, 45, 0.08);
  --primary-btn-shadow: 0 16px 28px rgba(15, 138, 62, 0.25);
  --primary-btn-hover-shadow: 0 24px 36px rgba(15, 138, 62, 0.3);
}

.landing.dark {
  --bg-gradient: linear-gradient(135deg, #050806 0%, #0e2419 45%, #041009 100%);
  --text-primary: #f0f6f3;
  --text-secondary: #c1d6cb;
  --accent-green: #5ad48c;
  --accent-green-dark: #2f9a54;
  --accent-gold: #d6ba68;
  --accent-gold-soft: rgba(214, 186, 104, 0.55);
  --surface: rgba(10, 22, 16, 0.86);
  --surface-soft: linear-gradient(140deg, rgba(30, 49, 38, 0.92), rgba(16, 30, 24, 0.78));
  --surface-card-border: rgba(90, 212, 140, 0.22);
  --surface-card-shadow: 0 32px 60px rgba(0, 0, 0, 0.45);
  --feature-shadow: 0 16px 28px rgba(0, 0, 0, 0.36);
  --stat-bg: rgba(20, 46, 33, 0.72);
  --stat-border: rgba(90, 212, 140, 0.26);
  --input-border: rgba(255, 255, 255, 0.14);
  --input-bg: rgba(14, 28, 21, 0.9);
  --input-focus-ring: rgba(90, 212, 140, 0.2);
  --notice-bg: rgba(217, 99, 91, 0.22);
  --notice-color: #ffd7d4;
  --grid-color: rgba(255, 255, 255, 0.08);
  --grid-opacity: 0.25;
  --floating-shadow: 0 18px 36px rgba(0, 0, 0, 0.45);
  --floating-shadow-hover: 0 26px 46px rgba(0, 0, 0, 0.55);
  --control-icon: #0d1a13;
  --glow-green: rgba(62, 171, 115, 0.55);
  --glow-gold: rgba(214, 186, 104, 0.46);
  --glow-white: rgba(32, 54, 42, 0.55);
  --tab-track: rgba(90, 212, 140, 0.12);
  --primary-btn-shadow: 0 20px 34px rgba(0, 0, 0, 0.4);
  --primary-btn-hover-shadow: 0 28px 42px rgba(0, 0, 0, 0.5);
}

.background {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.glow {
  position: absolute;
  filter: blur(120px);
  opacity: 0.55;
  transition: background 0.4s ease, opacity 0.4s ease;
}

.glow-one {
  top: -10%;
  left: 15%;
  width: 320px;
  height: 320px;
  background: var(--glow-green);
}

.glow-two {
  bottom: -20%;
  right: 10%;
  width: 420px;
  height: 420px;
  background: var(--glow-gold);
}

.glow-three {
  top: 40%;
  right: 35%;
  width: 260px;
  height: 260px;
  background: var(--glow-white);
}

.grid {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle at 1px 1px, var(--grid-color) 1px, transparent 0);
  background-size: 32px 32px;
  opacity: var(--grid-opacity);
  transition: opacity 0.4s ease;
}

.floating-controls {
  position: absolute;
  top: clamp(20px, 4vw, 36px);
  inset-inline-end: clamp(20px, 4vw, 36px);
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
  z-index: 25;
}

.control-btn {
  border: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px 18px;
  border-radius: 22px;
  background: linear-gradient(135deg, var(--accent-green), var(--accent-gold));
  color: #ffffff;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  box-shadow: var(--floating-shadow);
  transition: transform 0.25s ease, box-shadow 0.25s ease, background 0.3s ease;
}

.control-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--floating-shadow-hover);
}

.control-btn:focus-visible {
  outline: none;
  box-shadow: var(--floating-shadow-hover), 0 0 0 3px rgba(255, 255, 255, 0.32);
}

.control-icon {
  display: grid;
  place-items: center;
  color: var(--control-icon);
}

.control-icon svg {
  width: 26px;
  height: 26px;
}

.control-text {
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.lang-toggle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  padding: 0;
  font-size: 18px;
  letter-spacing: 0.08em;
}

.lang-toggle span {
  line-height: 1;
}

.theme-toggle .control-icon {
  color: #ffffff;
}

.landing__wrapper {
  position: relative;
  display: grid;
  gap: clamp(32px, 5vw, 64px);
  grid-template-columns: repeat(2, minmax(0, 1fr));
  max-width: 1120px;
  width: 100%;
  z-index: 10;
}

.landing__intro {
  display: flex;
  flex-direction: column;
  gap: clamp(24px, 3vw, 36px);
}

.logo-card {
  position: relative;
  width: clamp(110px, 14vw, 160px);
  aspect-ratio: 1 / 1;
  border-radius: 24px;
  display: grid;
  place-items: center;
  background: var(--surface-soft);
  border: 1px solid var(--surface-card-border);
  box-shadow: var(--surface-card-shadow);
  backdrop-filter: blur(16px);
  overflow: hidden;
  animation: logoFloat 6s ease-in-out infinite;
}

.logo-card::before,
.logo-card::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  inset: 16%;
  pointer-events: none;
}

.logo-card::before {
  background: radial-gradient(circle, rgba(255, 255, 255, 0.55) 0%, transparent 70%);
  opacity: 0.65;
  animation: logoPulse 5.8s ease-in-out infinite;
}

.logo-card::after {
  border: 2px solid var(--accent-gold-soft);
  animation: logoPulse 4.5s ease-in-out infinite;
}

.logo-card img {
  position: relative;
  width: 76%;
  height: auto;
  z-index: 1;
}

.intro__title {
  font-size: clamp(32px, 4vw, 52px);
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.intro__subtitle {
  font-size: clamp(16px, 2.2vw, 20px);
  line-height: 1.7;
  max-width: 480px;
  margin: 0;
  color: var(--text-secondary);
}

.feature-grid {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 18px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-radius: 18px;
  background: var(--surface-soft);
  box-shadow: var(--feature-shadow);
  transition: transform 0.25s ease, box-shadow 0.25s ease, background 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-6px);
}

.feature-index {
  font-weight: 700;
  color: var(--accent-gold);
  font-size: 18px;
}

.feature-text {
  font-size: 16px;
  color: var(--text-primary);
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.stat-card {
  padding: 18px 20px;
  border-radius: 16px;
  background: var(--stat-bg);
  border: 1px solid var(--stat-border);
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: start;
  transition: background 0.3s ease, border 0.3s ease;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--accent-green);
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.landing__auth {
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-card {
  width: min(100%, 420px);
  padding: clamp(24px, 3vw, 32px);
  border-radius: 28px;
  background: var(--surface);
  box-shadow: var(--surface-card-shadow);
  backdrop-filter: blur(16px);
  border: 1px solid var(--surface-card-border);
  display: flex;
  flex-direction: column;
  gap: 24px;
  transition: background 0.3s ease, border 0.3s ease, box-shadow 0.3s ease;
}

.auth-tabs {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  background: var(--tab-track);
  border-radius: 18px;
  padding: 4px;
}

.tab-btn {
  border: none;
  padding: 12px 16px;
  background: transparent;
  border-radius: 14px;
  font-weight: 700;
  font-size: 15px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: background 0.25s ease, color 0.25s ease, transform 0.25s ease;
}

.tab-btn.active {
  background: linear-gradient(135deg, var(--accent-green), var(--accent-gold));
  color: #ffffff;
  transform: translateY(-2px);
  box-shadow: 0 14px 24px rgba(0, 0, 0, 0.2);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.input-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-field label {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 14px;
}

.input-field input {
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  font-size: 15px;
  color: var(--text-primary);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.3s ease;
}

.input-field input:focus {
  border-color: var(--accent-green);
  box-shadow: 0 0 0 4px var(--input-focus-ring);
  outline: none;
}

.form-meta {
  text-align: end;
  font-size: 13px;
}

.form-meta a {
  color: var(--accent-green);
  text-decoration: none;
  font-weight: 600;
}

.primary-btn {
  position: relative;
  border: none;
  border-radius: 16px;
  padding: 14px 16px;
  font-weight: 700;
  font-size: 16px;
  background: linear-gradient(135deg, var(--accent-green), var(--accent-green-dark));
  color: #ffffff;
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  box-shadow: var(--primary-btn-shadow);
}

.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}

.primary-btn:not(:disabled):hover {
  transform: translateY(-2px);
  box-shadow: var(--primary-btn-hover-shadow);
}

.primary-btn:focus-visible {
  outline: none;
  box-shadow: var(--primary-btn-hover-shadow), 0 0 0 3px var(--input-focus-ring);
}

.switch-text {
  font-size: 14px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: center;
}

.switch-text button {
  border: none;
  background: none;
  color: var(--accent-gold);
  font-weight: 700;
  cursor: pointer;
}

.auth-notice {
  text-align: center;
  font-size: 14px;
  font-weight: 600;
  color: var(--notice-color);
  background: var(--notice-bg);
  border-radius: 14px;
  padding: 10px 14px;
  transition: background 0.3s ease, color 0.3s ease;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.28s ease;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

@keyframes logoFloat {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes logoPulse {
  0% {
    transform: scale(0.92);
    opacity: 0.55;
  }
  50% {
    transform: scale(1.05);
    opacity: 0;
  }
  100% {
    transform: scale(0.92);
    opacity: 0.55;
  }
}

@media (max-width: 1024px) {
  .landing__wrapper {
    grid-template-columns: minmax(0, 1fr);
  }

  .landing__intro {
    align-items: center;
    text-align: center;
  }

  .intro__subtitle {
    max-width: 580px;
  }

  .feature-item {
    justify-content: center;
  }

  .stats-row {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  }
}

@media (max-width: 680px) {
  .landing {
    padding: 24px 20px 40px;
  }

  .floating-controls {
    flex-direction: row;
    align-items: center;
    gap: 10px;
  }

  .theme-toggle {
    padding: 10px 14px;
  }

  .lang-toggle {
    width: 54px;
    height: 54px;
    font-size: 16px;
  }

  .feature-item {
    padding: 14px 16px;
  }

  .auth-card {
    padding: 22px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .logo-card,
  .logo-card::before,
  .logo-card::after,
  .feature-item:hover,
  .control-btn:hover {
    animation: none;
    transform: none;
  }
}
</style>

<script setup>
import { ref, computed, reactive, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  Target, Settings, LogOut, ChevronDown, Sun, Moon,
  Hand, ChevronLeft, Menu, Crown, Loader2
} from 'lucide-vue-next'

import Challenge1 from '@/pages/challenges/challenge_1.vue'
import Challenge2 from '@/pages/challenges/challenge_2.vue'
import Challenge3 from '@/pages/challenges/challenge_3.vue'
import Challenge4 from '@/pages/challenges/challenge_4.vue'
import Challenge5 from '@/pages/challenges/challenge_5.vue'
import Challenge6 from '@/pages/challenges/challenge_6.vue'
import Challenge7 from '@/pages/challenges/challenge_7.vue'
import challenge_level_two_1 from '@/pages/challenges/challenge_level_two_1.vue'
import challenge_level_two_2 from '@/pages/challenges/challenge_level_two_2.vue'
import challenge_level_two_3 from '@/pages/challenges/challenge_level_two_3.vue'
import challenge_level_two_4 from '@/pages/challenges/challenge_level_two_4.vue'
import challenge_level_two_5 from '@/pages/challenges/challenge_level_two_5.vue'
import challenge_level_two_6 from '@/pages/challenges/challenge_level_two_6.vue'
import challenge_level_three_1 from '@/pages/challenges/challenge_level_three_1.vue'
import challenge_level_three_2 from '@/pages/challenges/challenge_level_three_2.vue'
import challenge_level_three_3 from '@/pages/challenges/challenge_level_three_3.vue'
import challenge_level_three_4 from '@/pages/challenges/challenge_level_three_4.vue'
import challenge_level_three_5 from '@/pages/challenges/challenge_level_three_5.vue'
import challenge_level_three_6 from '@/pages/challenges/challenge_level_three_6.vue'
import challenge_level_three_7 from '@/pages/challenges/challenge_level_three_7.vue'
import challenge_level_three_8 from '@/pages/challenges/challenge_level_three_8.vue'
import challenge_level_three_9 from '@/pages/challenges/challenge_level_three_9.vue'
import MyScores from '@/pages/other/my_scores.vue'
import SettingsPage from '@/pages/other/settings.vue'
import { useGameScore } from '@/composables/useGameScore'
import { onToast } from '@/utils/toastBus'

const router = useRouter()
const props = defineProps({ view: { type: String, default: '' } })

const levels = [
  {
    id: 'level1',
    label: { ar: 'المستوى الأول', en: 'Level One' },
    challenges: [
      { id: 'challenge_1', component: Challenge1, symbol: '∑', label: { ar: 'التحدي 1', en: 'Challenge 1' }, summary: { ar: 'إكمال عملية جمع عمودية بأرقام مخفية.', en: 'Complete a column addition puzzle with hidden digits.' } },
      { id: 'challenge_2', component: Challenge2, symbol: '√', label: { ar: 'التحدي 2', en: 'Challenge 2' }, summary: { ar: 'شبكة أعداد تتزايد بمقدار ثابت، أعد القيم المفقودة.', en: 'Fill a number grid that increases by a fixed step.' } },
      { id: 'challenge_3', component: Challenge3, symbol: 'π', label: { ar: 'التحدي 3', en: 'Challenge 3' }, summary: { ar: 'اختر زوج الأعداد الصحيح حسب المجموع والفرق.', en: 'Pick the number pair that matches the given sum and difference.' } },
      { id: 'challenge_4', component: Challenge4, symbol: '×', label: { ar: 'التحدي 4', en: 'Challenge 4' }, summary: { ar: 'استكمل جدول ضرب مصغر.', en: 'Complete the mini multiplication table.' } },
      { id: 'challenge_5', component: Challenge5, symbol: 'Δ', label: { ar: 'التحدي 5', en: 'Challenge 5' }, summary: { ar: 'املأ مثلث الضرب على الأضلاع.', en: 'Fill in the edge products of the triangle.' } },
      { id: 'challenge_6', component: Challenge6, symbol: '≡', label: { ar: 'التحدي 6', en: 'Challenge 6' }, summary: { ar: 'اختر ثلاث خلايا مختلفة الصف والعمود لتحقيق مجموع محدد.', en: 'Pick three distinct-row/column cells to reach the target sum.' } },
      { id: 'challenge_7', component: Challenge7, symbol: '∴', label: { ar: 'التحدي 7', en: 'Challenge 7' }, summary: { ar: 'أكمل هرم الجمع بإسقاط القيم الصحيحة.', en: 'Complete the sum pyramid with the correct values.' } },
    ],
  },
  {
    id: 'level2',
    label: { ar: 'المستوى الثاني', en: 'Level Two' },
    challenges: [
      { id: 'challenge_level_two_1', component: challenge_level_two_1, symbol: '∫', label: { ar: 'التحدي 1', en: 'Challenge 1' }, summary: { ar: 'كوّن تعبيرًا يستخدم الأرقام 1 إلى 5 مرة واحدة.', en: 'Build an expression that uses digits 1–5 exactly once.' } },
      { id: 'challenge_level_two_2', component: challenge_level_two_2, symbol: '≠', label: { ar: 'التحدي 2', en: 'Challenge 2' }, summary: { ar: 'أكمل مربّعًا سحريًا بمجاميع متساوية.', en: 'Complete a magic square with equal sums.' } },
      { id: 'challenge_level_two_3', component: challenge_level_two_3, symbol: '≈', label: { ar: 'التحدي 3', en: 'Challenge 3' }, summary: { ar: 'طابق أعدادًا سداسية مع خواص القسمة.', en: 'Match six-digit numbers to divisibility rules.' } },
      { id: 'challenge_level_two_4', component: challenge_level_two_4, symbol: '∞', label: { ar: 'التحدي 4', en: 'Challenge 4' }, summary: { ar: 'اختر الزوج الذي يطابق المجموع والفرق.', en: 'Choose the pair that matches the required sum and difference.' } },
      { id: 'challenge_level_two_5', component: challenge_level_two_5, symbol: '∂', label: { ar: 'التحدي 5', en: 'Challenge 5' }, summary: { ar: 'اكمل طرح الكسور بوضع الأعداد الصحيحة.', en: 'Complete the fraction subtraction by placing the right integers.' } },
      { id: 'challenge_level_two_6', component: challenge_level_two_6, symbol: '⊗', label: { ar: 'التحدي 6', en: 'Challenge 6' }, summary: { ar: 'رتّب خطوات حل معادلة الموازين.', en: 'Order the solution steps for the balance puzzle.' } },
    ],
  },
  {
    id: 'level3',
    label: { ar: 'المستوى الثالث', en: 'Level Three' },
    challenges: [
      { id: 'challenge_level_three_1', component: challenge_level_three_1, symbol: 'Φ', label: { ar: 'التحدي 1', en: 'Challenge 1' }, summary: { ar: 'ابن هرم الضرب من أرقام مبعثرة.', en: 'Rebuild the multiplication pyramid from scattered numbers.' } },
      { id: 'challenge_level_three_2', component: challenge_level_three_2, symbol: 'Ψ', label: { ar: 'التحدي 2', en: 'Challenge 2' }, summary: { ar: 'لغز تفكير متقدم في الأعداد.', en: 'An advanced numerical reasoning puzzle.' } },
      { id: 'challenge_level_three_3', component: challenge_level_three_3, symbol: 'Λ', label: { ar: 'التحدي 3', en: 'Challenge 3' }, summary: { ar: 'لغز منطق متقدم لاختبار السرعة.', en: 'Advanced logic to test your speed.' } },
      { id: 'challenge_level_three_4', component: challenge_level_three_4, symbol: 'Ξ', label: { ar: 'التحدي 4', en: 'Challenge 4' }, summary: { ar: 'تحدٍ عالي المستوى لربط الأنماط.', en: 'High-level challenge for spotting patterns.' } },
      { id: 'challenge_level_three_5', component: challenge_level_three_5, symbol: 'Θ', label: { ar: 'التحدي 5', en: 'Challenge 5' }, summary: { ar: 'مسألة حسابية تحتاج إلى خطوات دقيقة.', en: 'A numeric problem that needs careful steps.' } },
      { id: 'challenge_level_three_6', component: challenge_level_three_6, symbol: 'β', label: { ar: 'التحدي 6', en: 'Challenge 6' }, summary: { ar: 'إستراتيجية جديدة لبناء الحل خطوة بخطوة.', en: 'Strategic puzzle solved step by step.' } },
      { id: 'challenge_level_three_7', component: challenge_level_three_7, symbol: 'γ', label: { ar: 'التحدي 7', en: 'Challenge 7' }, summary: { ar: 'هرم جمع متقدّم بقيم أكبر.', en: 'A larger, more demanding sum pyramid.' } },
      { id: 'challenge_level_three_8', component: challenge_level_three_8, symbol: 'η', label: { ar: 'التحدي 8', en: 'Challenge 8' }, summary: { ar: 'اختبار المنطق السريع بالأرقام.', en: 'Fast-paced numeric logic test.' } },
      { id: 'challenge_level_three_9', component: challenge_level_three_9, symbol: 'ζ', label: { ar: 'التحدي 9', en: 'Challenge 9' }, summary: { ar: 'لغز أخير يجمع بين التفكير والسرعة.', en: 'A final puzzle mixing reasoning with speed.' } },
    ],
  },
]

const levelAccents = {
  level1: { primary: 'var(--color-primary)', secondary: 'rgba(15,138,62,0.16)' },
  level2: { primary: 'var(--color-secondary)', secondary: 'rgba(200,160,59,0.22)' },
  level3: { primary: 'var(--color-accent)', secondary: 'rgba(13,110,140,0.24)' },
}
const fallbackAccent = { primary: 'var(--color-primary)', secondary: 'rgba(15,138,62,0.15)' }
const CARD_SYMBOLS = ['∑','√','π','∞','Δ','∫','≠','⊕','≈','∂','Φ','Ψ','Ω','λ','μ','θ','β','γ','η','ζ','ξ']

const cardSymbol = (levelId, challenge, index) => challenge.symbol || CARD_SYMBOLS[index % CARD_SYMBOLS.length] || '∑'
const cardStyle = (levelId, index) => {
  const palette = levelAccents[levelId] || fallbackAccent
  return {
    '--card-accent': palette.primary,
    '--card-accent-soft': palette.secondary,
    '--card-index': index,
  }
}

const scoreStore = useGameScore()
const dashTiers = [
  { threshold: 0, title: { ar: 'مبتدئ', en: 'Novice' } },
  { threshold: 25, title: { ar: 'متقدم', en: 'Skilled' } },
  { threshold: 80, title: { ar: 'قائد', en: 'Leader' } },
  { threshold: 160, title: { ar: 'أسطورة', en: 'Legend' } },
]

const scoreValue = computed(() => Number(scoreStore.score.value || 0))
const tierIndex = computed(() => {
  let idx = 0
  dashTiers.forEach((tier, index) => {
    if (scoreValue.value >= tier.threshold) idx = index
  })
  return idx
})
const scoreTier = computed(() => dashTiers[tierIndex.value])
const nextTier = computed(() => dashTiers[tierIndex.value + 1] || null)
const scoreTierName = computed(() => scoreTier.value?.title?.[lang.value] || scoreTier.value?.title?.en || '')
const scoreProgress = computed(() => {
  if (!nextTier.value) return 1
  const span = nextTier.value.threshold - scoreTier.value.threshold
  if (span <= 0) return 1
  return Math.min(1, (scoreValue.value - scoreTier.value.threshold) / span)
})
const scoreFormatter = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 })
const scoreDisplay = computed(() => scoreFormatter.format(scoreValue.value))
const rankDisplay = computed(() => {
  const rank = scoreStore.rank.value
  return rank ? `#${rank}` : '--'
})
const totalPlayersDisplay = computed(() => {
  const total = scoreStore.totalPlayers.value
  return total ? scoreFormatter.format(total) : '--'
})
const scoreLoading = computed(() => scoreStore.loading.value)
const scoreProgressPercent = computed(() => Math.round(scoreProgress.value * 100))
const avatarUrl = computed(() => scoreStore.profileImage.value || null)
const avatarInitial = computed(() => {
  const source = fullName.value || scoreStore.username.value || username.value || 'P'
  return source.trim().charAt(0).toUpperCase() || 'P'
})
const scoreDisplayKey = computed(() => (scoreLoading.value ? 'loading' : `score-${scoreValue.value}`))
const progressSpring = ref(0)
const scorePulse = ref(false)

watch(scoreProgress, value => {
  progressSpring.value = value
}, { immediate: true })

watch(() => scoreStore.score.value, (next, prev) => {
  if (prev == null || Number(next) === Number(prev)) return
  scorePulse.value = false
  requestAnimationFrame(() => {
    scorePulse.value = true
    setTimeout(() => { scorePulse.value = false }, 720)
  })
})

function viewScores(){
  goto('/scores')
}

const componentRegistry = {}
levels.forEach(level => {
  level.challenges.forEach(challenge => {
    componentRegistry[challenge.id] = challenge.component
  })
})
const specialViews = { scores: MyScores, settings: SettingsPage }

/* ================= اللغة ================= */
const lang = ref(localStorage.getItem('ml_lang') || 'ar')
const dir  = computed(() => (lang.value === 'ar' ? 'rtl' : 'ltr'))
const T = {
  ar: {
    challenges:'المستوى الأول', challenges2:'المستوى الثاني', myScores:'درجاتي', settings:'الإعدادات', logout:'خروج',
    hello:'مرحبًا', sub:'اختر تحديًا وابدأ اللعب!', challenge:'التحدي',
    brand:'زعماء الرياضيات', tagline:'رحلة إنجاز رقمية', pickPrompt:'اختر تحديًا من البطاقات أدناه للبدء.',
    cardCTA:'ابدأ التحدي',
    scoreWidgetTitle:'نقاطي', scoreWidgetSubtitle:'نظرة سريعة على تقدّمك',
    scoreWidgetRank:'الترتيب', scoreWidgetPlayers:'عدد اللاعبين',
    scoreWidgetProgress:'نحو الرتبة التالية', scoreWidgetView:'عرض التفاصيل',
    scoreWidgetLoading:'جار تحديث النقاط...',
    teacherTitle:'الشريك التربوي',
    teacherSubtitle:'ميعاد سفر المالكي',
    teacherMessage:'✨ “من هنا بدأت الرحلة… رحلة شغف صاغتها الأستاذة ميعاد سفر المالكي لتلهم طلابها نحو الإبداع والتفكير.'
  },
  en: {
    challenges:'Level One', challenges2:'Level Two', myScores:'My Scores', settings:'Settings', logout:'Log out',
    hello:'Hello', sub:'Pick a challenge and start!', challenge:'Challenge',
    brand:'Math Leaders', tagline:'Interactive mastery journey', pickPrompt:'Select a challenge from the cards below to get started.',
    cardCTA:'Start challenge',
    scoreWidgetTitle:'My points', scoreWidgetSubtitle:'Quick glance at your progress',
    scoreWidgetRank:'Rank', scoreWidgetPlayers:'Players',
    scoreWidgetProgress:'To next tier', scoreWidgetView:'View details',
    scoreWidgetLoading:'Refreshing score...',
    teacherTitle:'Presented by',
    teacherSubtitle:'Miyaad Safar Al-Malki',
    teacherMessage:'A heartfelt thanks to Ms. Miyaad Safar Al-Malki for curating these inspiring challenges.'
  }
}
const t = (k)=>T[lang.value][k]
const extraView = computed(() => props.view || '')
watch(lang, v=>{
  localStorage.setItem('ml_lang', v)
  document.documentElement.dir = dir.value
  document.documentElement.lang = v
})

/* ================= الثيم ================= */
const theme = ref(localStorage.getItem('ml_theme') || 'light')
const shellTransitioning = ref(false)
const isCompact = ref(false)
const globalToasts = ref([])

function applyTheme(value){
  document.documentElement.setAttribute('data-ml-theme', value)
}

let disposeToastListener = null

function animateShell(){
  shellTransitioning.value = true
  window.clearTimeout(animateShell.timer)
  animateShell.timer = window.setTimeout(() => {
    shellTransitioning.value = false
  }, 360)
}

function dismissToast(id){
  globalToasts.value = globalToasts.value.filter(toast => toast.id !== id)
}

function switchLang(){
  animateShell()
  lang.value = lang.value === 'ar' ? 'en' : 'ar'
}

function switchTheme(){
  animateShell()
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}

watch(theme, v=>{
  localStorage.setItem('ml_theme', v)
  applyTheme(v)
})

function handleViewportChange(){
  if (typeof window === 'undefined') return
  const compact = window.matchMedia('(max-width: 1024px)').matches
  isCompact.value = compact
  if (!compact) {
    sidebarCollapsed.value = false
  }
}

function handleClickOutside(event){
  if (!profileRef.value) return
  if (!profileRef.value.contains(event.target)) {
    profileOpen.value = false
  }
}

/* ================= GET helper ================= */
async function get(url, params = {}) {
  const qs = new URLSearchParams(params).toString()
  const r  = await fetch(url + (qs ? `?${qs}` : ''), {
    method: 'GET',
    credentials: 'include',
  })
  const data = await r.json().catch(()=> ({}))
  if (!r.ok) throw data
  return data
}

/* ================= المستخدم/الحماية ================= */
const username = ref('player')
const fullName = ref('')

async function fetchMe(){
  try {
    const data = await get('/api/method/mathematics_leaders.api.get_my_details.get_me')
    const msg  = data?.message
    if (!msg?.ok) { router.replace('/'); return }
    const prof = msg.profile || {}
    username.value = prof.username || 'player'
    fullName.value = prof.full_name || ''
    if (prof.language && !localStorage.getItem('ml_lang')) lang.value = prof.language
  } catch {
    router.replace('/')
  }
}

/* ================= تنقّل وقائمة ================= */
const profileOpen      = ref(false)
const profileRef       = ref(null)
const sidebarCollapsed = ref(false)
const expandedLevels = reactive(Object.fromEntries(levels.map((lvl) => [lvl.id, false])))
const selectedLevel = ref(levels[0]?.id || 'level1')
const selectedChallenge = ref(null)

function toggleSidebar(){
  sidebarCollapsed.value = !sidebarCollapsed.value
}
function goto(path){ router.push(path) }
async function logout(){
  await get('/api/method/logout')
  router.replace('/')
}
function toggleLevel(levelId){
  expandedLevels[levelId] = !expandedLevels[levelId]
}
function isExpanded(levelId){
  return !!expandedLevels[levelId]
}
function selectChallenge(levelId, challengeId){
  expandedLevels[levelId] = true
  selectedLevel.value = levelId
  selectedChallenge.value = challengeId
  if (isCompact.value) {
    sidebarCollapsed.value = true
  }
  if (router.currentRoute.value.path !== '/home') {
    router.push('/home')
  }
}
function isActiveChallenge(levelId, challengeId){
  return selectedLevel.value === levelId && selectedChallenge.value === challengeId
}

const currentSelection = computed(() => {
  if (props.view && specialViews[props.view]) {
    return { level: null, challenge: null }
  }
  if (!selectedChallenge.value) {
    const level = levels.find(l => l.id === selectedLevel.value) || null
    return { level, challenge: null }
  }
  for (const level of levels) {
    const challenge = level.challenges.find(ch => ch.id === selectedChallenge.value)
    if (challenge) return { level, challenge }
  }
  return { level: levels.find(l => l.id === selectedLevel.value) || null, challenge: null }
})
const currentComponent = computed(() => {
  if (props.view && specialViews[props.view]) {
    return specialViews[props.view]
  }
  const id = selectedChallenge.value
  return id ? componentRegistry[id] : null
})

/* ================= تهيئة ================= */
onMounted(()=>{
  document.documentElement.dir  = dir.value
  document.documentElement.lang = lang.value
  applyTheme(theme.value)
  fetchMe()
  scoreStore.refresh()
  handleViewportChange()
  if (isCompact.value) {
    sidebarCollapsed.value = true
  }
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', handleViewportChange)
  }
  document.addEventListener('click', handleClickOutside)
  disposeToastListener = onToast(event => {
    const detail = event.detail || {}
    if (!detail.message) return
    const toast = {
      id: detail.id || Math.random().toString(36).slice(2),
      message: detail.message,
      type: detail.type || 'info',
    }
    globalToasts.value.push(toast)
    if (globalToasts.value.length > 4) {
      globalToasts.value.shift()
    }
    const lifetime = Math.max(1500, detail.duration || 2600)
    window.setTimeout(() => dismissToast(toast.id), lifetime)
  })
})

onUnmounted(() => {
  if (disposeToastListener) disposeToastListener()
  window.clearTimeout(animateShell.timer)
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', handleViewportChange)
  }
  document.removeEventListener('click', handleClickOutside)
})

/* شعار */
const logoUrl = new URL('../assets/images/logo3.jpeg', import.meta.url).href
</script>


<template>
  <div :class="['dashboard', theme, { transitioning: shellTransitioning }]" :dir="dir">
    <div class="dashboard__background" aria-hidden="true">
      <span class="glow glow-one"></span>
      <span class="glow glow-two"></span>
      <span class="glow glow-three"></span>
      <span class="mesh"></span>
    </div>

    <transition-group name="toast-fade" tag="div" class="toasts" aria-live="polite">
      <div v-for="toast in globalToasts" :key="toast.id" class="toast" :class="toast.type">
        <span class="toast__dot"></span>
        <p>{{ toast.message }}</p>
        <button type="button" class="toast__close" @click="dismissToast(toast.id)">×</button>
      </div>
    </transition-group>

    <header class="dashboard__topbar">
      <div class="topbar__left">
        <button
          v-if="isCompact"
          class="topbar__menu"
          type="button"
          @click="toggleSidebar"
          :aria-expanded="!sidebarCollapsed"
          :aria-label="sidebarCollapsed ? (lang === 'ar' ? 'فتح قائمة التحديات' : 'Open challenges') : (lang === 'ar' ? 'إخفاء قائمة التحديات' : 'Hide challenges')"
        >
          <Menu v-if="sidebarCollapsed" />
          <ChevronLeft v-else :style="{ transform: dir === 'rtl' ? 'scaleX(-1)' : '' }" />
        </button>

        <div class="brand-chip">
          <div class="brand-chip__logo">
            <img :src="logoUrl" alt="logo" />
          </div>
          <div class="brand-chip__text">
            <span class="brand-chip__title">{{ T[lang].brand }}</span>
            <span class="brand-chip__subtitle">{{ T[lang].tagline }}</span>
          </div>
        </div>
      </div>

      <div class="topbar__center">
        <Hand class="wave" />
        <div class="greet">
          <h1>{{ T[lang].hello }} {{ fullName || username }}</h1>
          <p>{{ t('sub') }}</p>
        </div>
      </div>

      <div class="topbar__actions">
        <button
          class="action-btn"
          type="button"
          :aria-label="theme === 'dark' ? (lang === 'ar' ? 'التبديل إلى الوضع الفاتح' : 'Switch to light theme') : (lang === 'ar' ? 'التبديل إلى الوضع الداكن' : 'Switch to dark theme')"
          @click="switchTheme"
        >
          <Sun v-if="theme === 'light'" />
          <Moon v-else />
        </button>

        <button
          class="action-btn"
          type="button"
          :aria-label="lang === 'ar' ? 'Switch to English' : 'التبديل إلى العربية'"
          @click="switchLang"
        >
          {{ lang === 'ar' ? 'EN' : 'ع' }}
        </button>

        <div class="profile" ref="profileRef" @click.stop="profileOpen = !profileOpen">
          <div class="avatar">
            <span v-if="avatarUrl" class="avatar__image" :style="{ backgroundImage: `url(${avatarUrl})` }"></span>
            <span v-else class="avatar__initial">{{ avatarInitial }}</span>
          </div>
          <div class="profile__text">
            <span class="profile__name">{{ fullName || username }}</span>
            <span class="profile__meta">{{ T[lang].brand }}</span>
          </div>
          <ChevronDown class="profile__chevron" :class="{ open: profileOpen }" />
          <transition name="fade">
            <ul v-if="profileOpen" class="profile__menu">
              <li>
                <button type="button" @click="goto('/settings')">
                  <Settings /> <span>{{ T[lang].settings }}</span>
                </button>
              </li>
              <li>
                <button type="button" class="danger" @click="logout">
                  <LogOut /> <span>{{ T[lang].logout }}</span>
                </button>
              </li>
            </ul>
          </transition>
        </div>
      </div>
    </header>

    <main class="dashboard__main">
      <section class="overview-grid">
        <article class="welcome-card">
          <div class="welcome-card__icon">
            <Crown />
          </div>
          <div class="welcome-card__copy">
            <h2>{{ T[lang].brand }}</h2>
            <p>{{ T[lang].pickPrompt }}</p>
          </div>
          <div class="welcome-card__metrics">
            <div class="metric">
              <span class="metric__label">{{ T[lang].scoreWidgetRank }}</span>
              <strong>{{ scoreRankDisplay }}</strong>
            </div>
            <div class="metric">
              <span class="metric__label">{{ T[lang].scoreWidgetPlayers }}</span>
              <strong>{{ totalPlayersDisplay }}</strong>
            </div>
          </div>
        </article>

        <article class="score-card" :class="{ loading: scoreLoading, pulse: scorePulse }" :aria-busy="scoreLoading">
          <div v-if="scoreLoading" class="score-card__overlay" aria-hidden="true">
            <Loader2 class="overlay-spinner" />
          </div>
          <div class="score-card__ring">
            <svg viewBox="0 0 120 120" role="presentation">
              <defs>
                <linearGradient id="dashboardScoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#c6a034" />
                  <stop offset="100%" stop-color="#0f8a3e" />
                </linearGradient>
              </defs>
              <circle class="ring-bg" cx="60" cy="60" r="52" />
              <circle class="ring-fg" cx="60" cy="60" r="52" stroke="url(#dashboardScoreGradient)" :style="{ '--progress': progressSpring }" />
            </svg>
            <div class="score-card__center">
              <transition name="score-flip" mode="out-in">
                <span class="score-card__points" :key="scoreDisplayKey">{{ scoreLoading ? '...' : scoreDisplay }}</span>
              </transition>
              <small>{{ T[lang].scoreWidgetTitle }}</small>
            </div>
          </div>
          <div class="score-card__details">
            <span class="score-card__tier">{{ scoreTierName }}</span>
            <p class="score-card__subtitle">
              {{ scoreLoading ? T[lang].scoreWidgetLoading : T[lang].scoreWidgetSubtitle }}
            </p>
            <div
              class="progress"
              role="progressbar"
              :aria-valuenow="scoreProgressPercent"
              aria-valuemin="0"
              aria-valuemax="100"
            >
              <div class="progress__track">
                <div class="progress__fill" :style="{ '--progress': progressSpring }"></div>
              </div>
              <div class="progress__meta">
                <span>{{ scoreProgressPercent }}%</span>
                <button type="button" class="progress__link" @click="viewScores">{{ T[lang].scoreWidgetView }}</button>
              </div>
            </div>
          </div>
        </article>

        <article class="mentor-card">
          <div class="mentor-card__badge">{{ T[lang].teacherTitle }}</div>
          <h3>{{ T[lang].teacherSubtitle }}</h3>
          <p>{{ T[lang].teacherMessage }}</p>
        </article>
      </section>

      <section class="challenge-section">
        <aside class="challenge-list" :class="{ collapsed: sidebarCollapsed && isCompact }">
          <header class="challenge-list__header">
            <h2>{{ T[lang].challenge }}</h2>
            <p>{{ T[lang].pickPrompt }}</p>
          </header>

          <div class="levels">
            <div class="level-block" v-for="level in levels" :key="level.id">
              <button type="button" class="level-head" @click="toggleLevel(level.id)">
                <div class="level-head__info">
                  <Target class="level-head__icon" />
                  <span class="level-head__title">{{ level.label[lang] }}</span>
                </div>
                <span class="level-head__count">{{ level.challenges.length }}</span>
                <ChevronDown class="level-head__chevron" :class="{ open: isExpanded(level.id) }" />
              </button>
              <transition name="fade">
                <div v-if="isExpanded(level.id)" class="challenge-cards">
                  <button
                    v-for="challenge in level.challenges"
                    :key="challenge.id"
                    type="button"
                    class="challenge-card"
                    :class="{ active: isActiveChallenge(level.id, challenge.id) }"
                    @click="selectChallenge(level.id, challenge.id)"
                  >
                    <span class="challenge-card__symbol">{{ challenge.symbol }}</span>
                    <div class="challenge-card__body">
                      <span class="challenge-card__title">{{ challenge.label[lang] }}</span>
                      <p class="challenge-card__summary">{{ challenge.summary[lang] }}</p>
                    </div>
                    <span class="challenge-card__cta">{{ T[lang].cardCTA }}</span>
                  </button>
                </div>
              </transition>
            </div>
          </div>
       
            <div class="logout-block">
            <button type="button" class="logout-btn" @click="logout">
              <LogOut />
              <span>{{ T[lang].logout }}</span>
            </button>
          </div>
 </aside>
        <div class="challenge-preview">
          <div class="preview-header">
            <span v-if="currentSelection.level" class="preview-pill">{{ currentSelection.level.label[lang] }}</span>
            <div class="preview-text">
              <h3 v-if="extraView === 'scores'">{{ T[lang].myScores }}</h3>
              <h3 v-else-if="extraView === 'settings'">{{ T[lang].settings }}</h3>
              <h3 v-else-if="currentSelection.challenge">{{ currentSelection.challenge.label[lang] }}</h3>
              <h3 v-else>{{ T[lang].brand }}</h3>

              <p v-if="currentSelection.challenge">{{ currentSelection.challenge.summary[lang] }}</p>
              <p v-else-if="extraView === 'scores'">{{ T[lang].scoreWidgetSubtitle }}</p>
              <p v-else-if="extraView === 'settings'">{{ T[lang].settings }}</p>
              <p v-else>{{ T[lang].pickPrompt }}</p>
            </div>
          </div>

          <div class="preview-surface">
            <transition name="preview-fade" mode="out-in">
              <component
                v-if="currentComponent"
                :is="currentComponent"
                :key="extraView || currentSelection.challenge?.id || 'welcome'"
                class="preview-component"
                v-bind="{ lang, theme }"
              />
              <div v-else class="preview-placeholder" key="placeholder">
                <Crown />
                <p>{{ T[lang].pickPrompt }}</p>
              </div>
            </transition>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.dashboard {
  position: relative;
  min-height: 100vh;
  padding: clamp(28px, 6vw, 64px);
  display: flex;
  flex-direction: column;
  gap: clamp(28px, 5vw, 44px);
  background: var(--bg-gradient);
  color: var(--text-primary);
  transition: background 0.4s ease, color 0.4s ease;
  overflow-x: hidden;
  --bg-gradient: linear-gradient(135deg, #fdfcf8 0%, #f2f5ef 45%, #e6efe2 100%);
  --text-primary: #1f2a24;
  --text-secondary: #375447;
  --text-muted: #5f7669;
  --card-surface: rgba(255, 255, 255, 0.92);
  --card-soft: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.7));
  --card-border: rgba(198, 160, 52, 0.28);
  --card-shadow: 0 28px 58px rgba(31, 42, 36, 0.18);
  --glass-surface: rgba(255,255,255,0.78);
  --glass-border: rgba(198,160,52,0.2);
  --accent-green: #0f8a3e;
  --accent-green-dark: #1c6b39;
  --accent-gold: #c6a034;
  --accent-gold-soft: rgba(198,160,52,0.38);
  --chip-bg: rgba(15,138,62,0.12);
  --chip-color: #0f8a3e;
  --badge-bg: rgba(15,138,62,0.16);
  --badge-color: #0f8a3e;
  --outline: rgba(15,138,62,0.35);
  --grid-color: rgba(31, 42, 36, 0.08);
  --grid-opacity: 0.4;
  --control-shadow: 0 18px 32px rgba(15,138,62,0.22);
  --control-shadow-hover: 0 24px 42px rgba(15,138,62,0.28);
  --toast-surface: linear-gradient(135deg, rgba(15,138,62,0.92), rgba(198,160,52,0.82));
}

.dashboard.dark {
  --bg-gradient: linear-gradient(135deg, #040b07 0%, #102017 45%, #050f0a 100%);
  --text-primary: #f4f8f5;
  --text-secondary: #c5ded0;
  --text-muted: #9eb6a9;
  --card-surface: rgba(11, 23, 18, 0.9);
  --card-soft: linear-gradient(135deg, rgba(28,45,35,0.92), rgba(10,22,16,0.82));
  --card-border: rgba(90, 212, 140, 0.24);
  --card-shadow: 0 32px 64px rgba(0, 0, 0, 0.48);
  --glass-surface: rgba(18,32,26,0.78);
  --glass-border: rgba(90,212,140,0.28);
  --accent-green: #5ad48c;
  --accent-green-dark: #2f9a54;
  --accent-gold: #d6ba68;
  --accent-gold-soft: rgba(214,186,104,0.48);
  --chip-bg: rgba(214,186,104,0.18);
  --chip-color: #f5d98a;
  --badge-bg: rgba(90,212,140,0.16);
  --badge-color: #edfaef;
  --outline: rgba(90,212,140,0.42);
  --grid-color: rgba(255, 255, 255, 0.08);
  --grid-opacity: 0.2;
  --control-shadow: 0 22px 40px rgba(0,0,0,0.45);
  --control-shadow-hover: 0 30px 52px rgba(0,0,0,0.55);
  --toast-surface: linear-gradient(135deg, rgba(54,171,110,0.92), rgba(214,186,104,0.86));
}

.dashboard__background {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.glow {
  position: absolute;
  filter: blur(140px);
  opacity: 0.6;
  transition: opacity 0.4s ease;
}

.glow-one {
  top: -12%;
  left: 10%;
  width: 360px;
  height: 360px;
  background: rgba(15,138,62,0.42);
}

.glow-two {
  bottom: -24%;
  right: 18%;
  width: 460px;
  height: 460px;
  background: rgba(198,160,52,0.42);
}

.glow-three {
  top: 35%;
  right: 40%;
  width: 280px;
  height: 280px;
  background: rgba(255,255,255,0.4);
}

.dashboard.dark .glow-three {
  background: rgba(40,65,52,0.52);
}

.mesh {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle at 1px 1px, var(--grid-color) 1px, transparent 0);
  background-size: 32px 32px;
  opacity: var(--grid-opacity);
}

.toasts {
  position: fixed;
  top: clamp(12px, 2vw, 20px);
  inset-inline: 0;
  display: grid;
  justify-content: center;
  gap: 12px;
  z-index: 200;
  pointer-events: none;
}

.toast {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 18px;
  border-radius: 999px;
  background: var(--toast-surface);
  color: #ffffff;
  box-shadow: var(--control-shadow);
  backdrop-filter: blur(10px);
}

.toast.success {
  background: linear-gradient(135deg, rgba(34,197,94,0.92), rgba(15,138,62,0.9));
}

.toast.danger {
  background: linear-gradient(135deg, rgba(214,76,66,0.92), rgba(143,44,36,0.9));
}

.toast__dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255,255,255,0.82);
}

.toast__close {
  border: none;
  background: transparent;
  color: inherit;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  opacity: 0.85;
}

.toast__close:hover {
  opacity: 1;
}

.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.dashboard__topbar {
  position: relative;
  z-index: 5;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: clamp(16px, 3vw, 24px);
}

.topbar__left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.topbar__menu {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 16px;
  border: none;
  background: linear-gradient(135deg, var(--accent-green), var(--accent-gold));
  color: #ffffff;
  cursor: pointer;
  box-shadow: var(--control-shadow);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.topbar__menu:hover {
  transform: translateY(-2px);
  box-shadow: var(--control-shadow-hover);
}


.brand-chip {
  display: inline-flex;
  align-items: center;
  gap: 18px;
  padding: 18px 24px;
  border-radius: 32px;
  background: var(--card-soft);
  border: 1px solid var(--card-border);
  box-shadow: 0 24px 48px rgba(15, 23, 42, 0.14);
  backdrop-filter: blur(20px);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.brand-chip:hover {
  transform: translateY(-2px);
  box-shadow: 0 30px 60px rgba(15, 23, 42, 0.18);
}

.brand-chip__logo {
  width: 78px;
  height: 78px;
  border-radius: 24px;
  background: var(--glass-surface);
  border: 1px solid var(--glass-border);
  display: grid;
  place-items: center;
  overflow: hidden;
  box-shadow: 0 18px 32px rgba(15, 138, 62, 0.15);
}

.brand-chip__logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.brand-chip:hover .brand-chip__logo img {
  transform: scale(1.05);
}

.brand-chip__text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.brand-chip__title {
  font-weight: 800;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.brand-chip__subtitle {
  font-size: 0.88rem;
  color: var(--text-muted);
}

.topbar__center {
  display: flex;
  align-items: center;
  gap: 16px;
}

.wave {
  width: 32px;
  height: 32px;
  color: var(--accent-gold);
}

.greet h1 {
  margin: 0;
  font-size: clamp(1.1rem, 2.4vw, 1.6rem);
  font-weight: 700;
  color: var(--text-primary);
}

.greet p {
  margin: 4px 0 0;
  font-size: 0.92rem;
  color: var(--text-muted);
}

.topbar__actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 16px;
  border: none;
  background: linear-gradient(135deg, var(--accent-green), var(--accent-gold));
  color: #ffffff;
  cursor: pointer;
  font-weight: 700;
  box-shadow: var(--control-shadow);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--control-shadow-hover);
}

.profile {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 24px;
  background: var(--card-soft);
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow);
  cursor: pointer;
}

.avatar {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  overflow: hidden;
  display: grid;
  place-items: center;
  background: var(--chip-bg);
  color: var(--chip-color);
  font-weight: 700;
  letter-spacing: 0.02em;
}

.avatar__image {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
}

.avatar__initial {
  font-size: 1rem;
}

.profile__text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.profile__name {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--text-primary);
}

.profile__meta {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.profile__chevron {
  width: 18px;
  height: 18px;
  color: var(--accent-gold);
  transition: transform 0.25s ease;
}

.profile__chevron.open {
  transform: rotate(180deg);
}

.profile__menu {
  position: absolute;
  inset-inline-end: 0;
  top: calc(100% + 12px);
  display: grid;
  gap: 8px;
  padding: 12px;
  border-radius: 18px;
  background: var(--glass-surface);
  border: 1px solid var(--glass-border);
  box-shadow: var(--card-shadow);
  backdrop-filter: blur(18px);
  min-width: 180px;
  z-index: 20;
}

.profile__menu li {
  list-style: none;
}

.profile__menu button {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 10px;
  border: none;
  border-radius: 12px;
  background: transparent;
  color: var(--text-primary);
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}

.profile__menu button:hover {
  background: var(--chip-bg);
  color: var(--chip-color);
}

.profile__menu button svg {
  width: 18px;
  height: 18px;
}

.profile__menu button.danger {
  color: #c74b3f;
}

.dashboard__main {
  position: relative;
  /* z-index: 5; */
  display: flex;
  flex-direction: column;
  gap: clamp(24px, 4vw, 36px);
}

.overview-grid {
  display: grid;
  gap: clamp(18px, 3vw, 24px);
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.welcome-card,
.score-card,
.mentor-card {
  position: relative;
  border-radius: 28px;
  background: var(--card-surface);
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow);
  padding: clamp(20px, 3vw, 28px);
  display: flex;
  flex-direction: column;
  gap: 18px;
  backdrop-filter: blur(18px);
}

.welcome-card__icon {
  width: 54px;
  height: 54px;
  border-radius: 18px;
  background: var(--chip-bg);
  color: var(--chip-color);
  display: grid;
  place-items: center;
  font-size: 1.2rem;
}

.welcome-card__copy h2 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--text-primary);
}

.welcome-card__copy p {
  margin: 6px 0 0;
  color: var(--text-muted);
  font-size: 0.95rem;
}

.welcome-card__metrics {
  display: flex;
  gap: 18px;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.metric__label {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

.metric strong {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--accent-green);
}

.dashboard.dark .metric strong {
  color: var(--accent-gold);
}

.score-card {
  position: relative;
  overflow: hidden;
}

.score-card__overlay {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgba(0, 0, 0, 0.18);
  z-index: 2;
}

.overlay-spinner {
  width: 36px;
  height: 36px;
  animation: spin 1s linear infinite;
}

.score-card__ring {
  position: relative;
  display: grid;
  place-items: center;
}

.score-card__ring svg {
  width: clamp(140px, 16vw, 180px);
  height: clamp(140px, 16vw, 180px);
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: rgba(0, 0, 0, 0.08);
  stroke-width: 10;
}

.dashboard.dark .ring-bg {
  stroke: rgba(255, 255, 255, 0.08);
}

.ring-fg {
  fill: none;
  stroke-width: 10;
  stroke-linecap: round;
  stroke-dasharray: 327;
  stroke-dashoffset: calc(327 - (327 * var(--progress, 0)));
  transition: stroke-dashoffset 0.8s cubic-bezier(0.22, 1, 0.36, 1);
}

.score-card__center {
  position: absolute;
  display: grid;
  place-items: center;
  gap: 6px;
  text-align: center;
}

.score-card__points {
  font-size: clamp(1.6rem, 3vw, 2rem);
  font-weight: 800;
  color: var(--accent-green);
}

.dashboard.dark .score-card__points {
  color: var(--accent-gold);
}

.score-card__center small {
  font-size: 0.82rem;
  color: var(--text-muted);
}

.score-card__details {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.score-card__tier {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 999px;
  background: var(--chip-bg);
  color: var(--chip-color);
  font-weight: 700;
  letter-spacing: 0.08em;
  font-size: 0.78rem;
  text-transform: uppercase;
  width: max-content;
}

.score-card__subtitle {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.94rem;
}

.progress {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.progress__track {
  position: relative;
  width: 100%;
  height: 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.5);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.7);
}

.dashboard.dark .progress__track {
  background: rgba(17, 28, 22, 0.72);
  border-color: rgba(90, 212, 140, 0.3);
}

.progress__fill {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, var(--accent-green), var(--accent-gold));
  transform-origin: left center;
  transform: scaleX(var(--progress, 0));
  transition: transform 0.8s cubic-bezier(0.22, 1, 0.36, 1);
}

.progress__meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.progress__link {
  border: none;
  background: none;
  color: var(--accent-green);
  font-weight: 700;
  cursor: pointer;
  text-decoration: underline;
}

.dashboard.dark .progress__link {
  color: var(--accent-gold);
}

.score-card.pulse .score-card__points {
  animation: scorePulse 0.72s ease;
}

.mentor-card {
  overflow: hidden;
}

.mentor-card__badge {
  align-self: flex-start;
  padding: 6px 16px;
  border-radius: 999px;
  background: var(--badge-bg);
  color: var(--badge-color);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.mentor-card h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.mentor-card p {
  margin: 6px 0 0;
  color: var(--text-muted);
  font-size: 0.94rem;
}

.challenge-section {
  display: grid;
  grid-template-columns: minmax(320px, 380px) minmax(0, 1fr);
  gap: clamp(20px, 4vw, 32px);
}

.challenge-list {
  position: relative;
  border-radius: 32px;
  background: var(--card-surface);
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow);
  padding: clamp(20px, 3vw, 26px);
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-height: 720px;
  overflow-y: auto;
  overflow-x: hidden;
  backdrop-filter: blur(18px);
  scroll-behavior: smooth;
  transition: background 0.35s ease, border-color 0.35s ease, box-shadow 0.35s ease;
}

.challenge-list.collapsed {
  display: none;
}

.challenge-list__header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text-primary);
}

.challenge-list__header p {
  margin: 6px 0 0;
  color: var(--text-muted);
  font-size: 0.92rem;
}

.level-block {
  border-radius: 22px;
  background: var(--glass-surface);
  border: 1px solid var(--glass-border);
  overflow: hidden;
  transition: background 0.3s ease, border-color 0.3s ease;
}

.level-head {
  width: 100%;
  border: none;
  background: transparent;
  padding: 16px 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  color: var(--text-primary);
}

.level-head__info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.level-head__icon {
  width: 22px;
  height: 22px;
  color: var(--accent-green);
}

.dashboard.dark .level-head__icon {
  color: var(--accent-gold);
}

.level-head__title {
  font-weight: 700;
  font-size: 1rem;
}

.level-head__count {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-muted);
}

.level-head__chevron {
  width: 18px;
  height: 18px;
  transition: transform 0.25s ease;
  color: var(--accent-gold);
}

.level-head__chevron.open {
  transform: rotate(180deg);
}

.challenge-cards {
  display: grid;
  gap: 12px;
  padding: 0 18px 18px;
}

.challenge-card {
  position: relative;
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 14px;
  align-items: center;
  padding: 16px 18px;
  border-radius: 18px;
  border: 1px solid rgba(233,236,239,0.65);
  background: rgba(255,255,255,0.9);
  color: var(--text-primary);
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border 0.25s ease, background 0.25s ease;
  box-shadow: 0 16px 32px rgba(31,42,36,0.14);
}

.dashboard.dark .challenge-card {
  background: rgba(15,23,32,0.85);
  border-color: rgba(90,212,140,0.2);
  box-shadow: 0 18px 36px rgba(0,0,0,0.45);
}

.challenge-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 22px 40px rgba(15,138,62,0.22);
  border-color: var(--outline);
}

.challenge-card.active {
  border-color: var(--accent-gold);
  box-shadow: 0 24px 42px rgba(15,138,62,0.26);
}

.challenge-card__symbol {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--accent-green);
}

.dashboard.dark .challenge-card__symbol {
  color: var(--accent-gold);
}

.challenge-card__body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.challenge-card__title {
  font-weight: 700;
  font-size: 1rem;
}

.challenge-card__summary {
  margin: 0;
  font-size: 0.86rem;
  color: var(--text-muted);
  line-height: 1.5;
}

.challenge-card__cta {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--accent-gold);
}

.challenge-preview {
  position: relative;
  border-radius: 32px;
  background: var(--card-surface);
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow);
  padding: clamp(22px, 3vw, 30px);
  display: flex;
  flex-direction: column;
  gap: 20px;
  backdrop-filter: blur(18px);
  min-height: 520px;
  transition: background 0.35s ease, border-color 0.35s ease, box-shadow 0.35s ease;
}

.preview-header {
  display: flex;
  gap: 18px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.preview-pill {
  padding: 6px 16px;
  border-radius: 999px;
  background: var(--chip-bg);
  color: var(--chip-color);
  font-weight: 700;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.preview-text h3 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--text-primary);
}

.preview-text p {
  margin: 8px 0 0;
  color: var(--text-muted);
  font-size: 0.95rem;
  max-width: 640px;
}

.preview-surface {
  position: relative;
  flex: 1;
  border-radius: 26px;
  background: rgba(255,255,255,0.82);
  border: 1px solid rgba(233,236,239,0.8);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
  overflow: hidden;
  transition: background 0.35s ease, border-color 0.35s ease, box-shadow 0.35s ease;
}

.dashboard.dark .preview-surface {
  background: rgba(15,23,32,0.85);
  border-color: rgba(90,212,140,0.32);
  box-shadow: inset 0 1px 0 rgba(90,212,140,0.12);
}

.preview-component {
  width: 100%;
  height: 100%;
  padding: clamp(16px, 3vw, 22px);
  overflow: auto;
}

.preview-placeholder {
  height: 100%;
  display: grid;
  place-items: center;
  gap: 12px;
  text-align: center;
  color: var(--text-muted);
  font-size: 1rem;
}

.preview-placeholder svg {
  width: 54px;
  height: 54px;
  color: var(--accent-gold);
}

.fade-enter-active,
.fade-leave-active,
.preview-fade-enter-active,
.preview-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.fade-enter-from,
.fade-leave-to,
.preview-fade-enter-from,
.preview-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.score-flip-enter-active,
.score-flip-leave-active {
  transition: transform 0.28s ease, opacity 0.28s ease;
}

.score-flip-enter-from {
  transform: rotateX(-90deg);
  opacity: 0;
}

.score-flip-leave-to {
  transform: rotateX(90deg);
  opacity: 0;
}
.logout-block{
  margin: 12px; padding-top: 10px; border-top: 1px solid var(--border-color,#ddd);
}
.logout-btn{
  width: 100%; display: flex; align-items: center; gap: 8px;
  background: transparent; border: 0; padding: 10px 8px; border-radius: 10px;
  color: #b32020; font-weight: 700; cursor: pointer;
}
.logout-btn:hover{ background: rgba(179,32,32,.08); }
.logout-btn svg{ width: 18px; height: 18px; }

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes scorePulse {
  0% {
    transform: scale(1);
  }
  40% {
    transform: scale(1.08);
  }
  100% {
    transform: scale(1);
  }
}

@media (max-width: 1200px) {
  .overview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .mentor-card {
    grid-column: span 2;
  }
}

@media (max-width: 1024px) {
  .dashboard {
    padding: clamp(20px, 6vw, 32px);
  }

  .dashboard__topbar {
    grid-template-columns: 1fr;
    justify-items: stretch;
  }

  .brand-chip {
    gap: 14px;
    padding: 14px 18px;
    border-radius: 26px;
  }

  .brand-chip__logo {
    width: 66px;
    height: 66px;
  }

  .topbar__left {
    justify-content: space-between;
  }

  .topbar__center {
    justify-content: space-between;
    flex-wrap: wrap;
  }

  .topbar__actions {
    justify-content: flex-end;
    column-gap: 10px;
  }

  .overview-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .mentor-card {
    grid-column: span 1;
  }

  .challenge-section {
    grid-template-columns: minmax(0, 1fr);
  }

  .challenge-list {
    position: fixed;
    inset: clamp(16px, 4vw, 24px);
    inset-inline: clamp(16px, 4vw, 24px);
    max-width: unset;
    z-index: 40;
    max-height: calc(100vh - clamp(32px, 8vw, 48px));
    overflow-y: auto;
  }

  .challenge-list.collapsed {
    display: none;
  }

  .challenge-preview {
    min-height: 400px;
  }
}

@media (max-width: 720px) {
  .profile {
    padding: 8px 12px;
  }

  .profile__text {
    display: none;
  }

  .brand-chip {
    gap: 12px;
    padding: 12px 16px;
  }

  .brand-chip__logo {
    width: 58px;
    height: 58px;
    border-radius: 20px;
  }

  .overview-grid {
    gap: 16px;
  }

  .challenge-list__header h2 {
    font-size: 1.1rem;
  }

  .challenge-card {
    grid-template-columns: auto 1fr;
    row-gap: 10px;
  }

  .challenge-card__cta {
    grid-column: span 2;
    justify-self: flex-start;
  }
}

@media (prefers-reduced-motion: reduce) {
  .action-btn,
  .topbar__menu,
  .challenge-card,
  .score-card__points {
    transition: none;
    animation: none;
  }

  .score-flip-enter-active,
  .score-flip-leave-active,
  .preview-fade-enter-active,
  .preview-fade-leave-active,
  .fade-enter-active,
  .fade-leave-active {
    transition: none;
  }
}
</style>

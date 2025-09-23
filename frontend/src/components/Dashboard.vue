<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  Target, Trophy, Settings, LogOut, ChevronDown, Globe, Sun, Moon,
  Hand, ChevronLeft, Menu
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

const router = useRouter()
const props = defineProps({ view: { type: String, default: '' } })

const levels = [
  {
    id: 'level1',
    label: { ar: 'المستوى الأول', en: 'Level One' },
    challenges: [
      { id: 'challenge_1', component: Challenge1, label: { ar: 'التحدي 1', en: 'Challenge 1' }, summary: { ar: 'إكمال عملية جمع عمودية بأرقام مخفية.', en: 'Complete a column addition puzzle with hidden digits.' } },
      { id: 'challenge_2', component: Challenge2, label: { ar: 'التحدي 2', en: 'Challenge 2' }, summary: { ar: 'شبكة أعداد تتزايد بمقدار ثابت، أعد القيم المفقودة.', en: 'Fill a number grid that increases by a fixed step.' } },
      { id: 'challenge_3', component: Challenge3, label: { ar: 'التحدي 3', en: 'Challenge 3' }, summary: { ar: 'اختر زوج الأعداد الصحيح حسب المجموع والفرق.', en: 'Pick the number pair that matches the given sum and difference.' } },
      { id: 'challenge_4', component: Challenge4, label: { ar: 'التحدي 4', en: 'Challenge 4' }, summary: { ar: 'استكمل جدول ضرب مصغر.', en: 'Complete the mini multiplication table.' } },
      { id: 'challenge_5', component: Challenge5, label: { ar: 'التحدي 5', en: 'Challenge 5' }, summary: { ar: 'املأ مثلث الضرب على الأضلاع.', en: 'Fill in the edge products of the triangle.' } },
      { id: 'challenge_6', component: Challenge6, label: { ar: 'التحدي 6', en: 'Challenge 6' }, summary: { ar: 'اختر ثلاث خلايا مختلفة الصف والعمود لتحقيق مجموع محدد.', en: 'Pick three distinct-row/column cells to reach the target sum.' } },
      { id: 'challenge_7', component: Challenge7, label: { ar: 'التحدي 7', en: 'Challenge 7' }, summary: { ar: 'أكمل هرم الجمع بإسقاط القيم الصحيحة.', en: 'Complete the sum pyramid with the correct values.' } },
    ],
  },
  {
    id: 'level2',
    label: { ar: 'المستوى الثاني', en: 'Level Two' },
    challenges: [
      { id: 'challenge_level_two_1', component: challenge_level_two_1, label: { ar: 'التحدي 1', en: 'Challenge 1' }, summary: { ar: 'كوّن تعبيرًا يستخدم الأرقام 1 إلى 5 مرة واحدة.', en: 'Build an expression that uses digits 1–5 exactly once.' } },
      { id: 'challenge_level_two_2', component: challenge_level_two_2, label: { ar: 'التحدي 2', en: 'Challenge 2' }, summary: { ar: 'أكمل مربّعًا سحريًا بمجاميع متساوية.', en: 'Complete a magic square with equal sums.' } },
      { id: 'challenge_level_two_3', component: challenge_level_two_3, label: { ar: 'التحدي 3', en: 'Challenge 3' }, summary: { ar: 'طابق أعدادًا سداسية مع خواص القسمة.', en: 'Match six-digit numbers to divisibility rules.' } },
      { id: 'challenge_level_two_4', component: challenge_level_two_4, label: { ar: 'التحدي 4', en: 'Challenge 4' }, summary: { ar: 'اختر الزوج الذي يطابق المجموع والفرق.', en: 'Choose the pair that matches the required sum and difference.' } },
      { id: 'challenge_level_two_5', component: challenge_level_two_5, label: { ar: 'التحدي 5', en: 'Challenge 5' }, summary: { ar: 'اكمل طرح الكسور بوضع الأعداد الصحيحة.', en: 'Complete the fraction subtraction by placing the right integers.' } },
      { id: 'challenge_level_two_6', component: challenge_level_two_6, label: { ar: 'التحدي 6', en: 'Challenge 6' }, summary: { ar: 'رتّب خطوات حل معادلة الموازين.', en: 'Order the solution steps for the balance puzzle.' } },
    ],
  },
  {
    id: 'level3',
    label: { ar: 'المستوى الثالث', en: 'Level Three' },
    challenges: [
      { id: 'challenge_level_three_1', component: challenge_level_three_1, label: { ar: 'التحدي 1', en: 'Challenge 1' }, summary: { ar: 'ابن هرم الضرب من أرقام مبعثرة.', en: 'Rebuild the multiplication pyramid from scattered numbers.' } },
      { id: 'challenge_level_three_2', component: challenge_level_three_2, label: { ar: 'التحدي 2', en: 'Challenge 2' }, summary: { ar: 'لغز تفكير متقدم في الأعداد.', en: 'An advanced numerical reasoning puzzle.' } },
      { id: 'challenge_level_three_3', component: challenge_level_three_3, label: { ar: 'التحدي 3', en: 'Challenge 3' }, summary: { ar: 'لغز منطق متقدم لاختبار السرعة.', en: 'Advanced logic to test your speed.' } },
      { id: 'challenge_level_three_4', component: challenge_level_three_4, label: { ar: 'التحدي 4', en: 'Challenge 4' }, summary: { ar: 'تحدٍ عالي المستوى لربط الأنماط.', en: 'High-level challenge for spotting patterns.' } },
      { id: 'challenge_level_three_5', component: challenge_level_three_5, label: { ar: 'التحدي 5', en: 'Challenge 5' }, summary: { ar: 'مسألة حسابية تحتاج إلى خطوات دقيقة.', en: 'A numeric problem that needs careful steps.' } },
      { id: 'challenge_level_three_6', component: challenge_level_three_6, label: { ar: 'التحدي 6', en: 'Challenge 6' }, summary: { ar: 'إستراتيجية جديدة لبناء الحل خطوة بخطوة.', en: 'Strategic puzzle solved step by step.' } },
      { id: 'challenge_level_three_7', component: challenge_level_three_7, label: { ar: 'التحدي 7', en: 'Challenge 7' }, summary: { ar: 'هرم جمع متقدّم بقيم أكبر.', en: 'A larger, more demanding sum pyramid.' } },
      { id: 'challenge_level_three_8', component: challenge_level_three_8, label: { ar: 'التحدي 8', en: 'Challenge 8' }, summary: { ar: 'اختبار المنطق السريع بالأرقام.', en: 'Fast-paced numeric logic test.' } },
      { id: 'challenge_level_three_9', component: challenge_level_three_9, label: { ar: 'التحدي 9', en: 'Challenge 9' }, summary: { ar: 'لغز أخير يجمع بين التفكير والسرعة.', en: 'A final puzzle mixing reasoning with speed.' } },
    ],
  },
]

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
    brand:'زعماء الرياضيات', pickPrompt:'اختر تحديًا من البطاقات أدناه للبدء.',
    scoreWidgetTitle:'نقاطي', scoreWidgetSubtitle:'نظرة سريعة على تقدّمك',
    scoreWidgetRank:'الترتيب', scoreWidgetPlayers:'عدد اللاعبين',
    scoreWidgetProgress:'نحو الرتبة التالية', scoreWidgetView:'عرض التفاصيل',
    scoreWidgetLoading:'جار تحديث النقاط...',
    teacherTitle:'الشريك التربوي',
    teacherSubtitle:'ميعاد سفر المالكي',
    teacherMessage:'شكرًا للأستاذة ميعاد سفر المالكي على إعداد هذه التحديات المُلهمة للطلبة.'
  },
  en: {
    challenges:'Level One', challenges2:'Level Two', myScores:'My Scores', settings:'Settings', logout:'Log out',
    hello:'Hello', sub:'Pick a challenge and start!', challenge:'Challenge',
    brand:'Math Leaders', pickPrompt:'Select a challenge from the cards below to get started.',
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
watch(theme, v=>{
  localStorage.setItem('ml_theme', v)
})

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
const sidebarCollapsed = ref(false)
const expandedLevels = reactive(Object.fromEntries(levels.map((lvl, idx) => [lvl.id, idx === 0])))
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
  fetchMe()
  scoreStore.refresh()
})

/* شعار */
const logoUrl = new URL('../assets/images/logo3.jpeg', import.meta.url).href
</script>

<template>
  <div class="shell" :dir="dir" :data-theme="theme">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="brand" :title="t('brand')">
        <img class="logo" :src="logoUrl" alt="ML logo" />
        <span class="brand-name" v-show="!sidebarCollapsed">{{ t('brand') }}</span>
      </div>

      <nav class="menu">
        <div class="menu-group" v-for="level in levels" :key="level.id">
          <button class="menu-item" @click="toggleLevel(level.id)" :disabled="sidebarCollapsed">
            <Target class="mi" />
            <span class="mt" v-show="!sidebarCollapsed">{{ level.label[lang] }}</span>
            <ChevronDown class="chev" :class="{rot: isExpanded(level.id)}" v-show="!sidebarCollapsed" />
          </button>
          <transition name="fade">
            <ul v-if="isExpanded(level.id) && !sidebarCollapsed" class="submenu">
              <li v-for="challenge in level.challenges" :key="challenge.id">
                <a
                  href="javascript:;"
                  :class="{ active: isActiveChallenge(level.id, challenge.id) }"
                  @click="selectChallenge(level.id, challenge.id)"
                >
                  {{ challenge.label[lang] }}
                </a>
              </li>
            </ul>
          </transition>
        </div>

        <button class="menu-item" @click="goto('/scores')" :title="t('myScores')">
          <Trophy class="mi" />
          <span class="mt" v-show="!sidebarCollapsed">{{ t('myScores') }}</span>
        </button>

        <button class="menu-item" @click="goto('/settings')" :title="t('settings')">
          <Settings class="mi" />
          <span class="mt" v-show="!sidebarCollapsed">{{ t('settings') }}</span>
        </button>

        <button class="menu-item danger" @click="logout" :title="t('logout')">
          <LogOut class="mi" />
          <span class="mt" v-show="!sidebarCollapsed">{{ t('logout') }}</span>
        </button>
      </nav>
    </aside>

    <!-- Main -->
    <main class="main">
      <header class="topbar">
        <div class="left">
          <button class="pill ghost toggle" @click="toggleSidebar" :aria-label="sidebarCollapsed ? 'Open sidebar' : 'Collapse sidebar'">
            <Menu v-if="sidebarCollapsed" />
            <ChevronLeft v-else :style="{ transform: dir==='rtl' ? 'scaleX(-1)' : '' }" />
          </button>

          <div class="welcome">
            <Hand class="wave" />
            <strong>{{ T[lang].hello }} {{ fullName || username }}</strong>
            <small>— {{ t('sub') }}</small>
          </div>
        </div>

        <div class="right">
          <button class="pill ghost" title="Language" @click="lang = (lang==='ar'?'en':'ar')">
            <Globe style="margin-inline-end:6px" /> {{ lang==='ar' ? 'EN' : 'ع' }}
          </button>
          <button class="pill ghost" title="Theme" @click="theme = (theme==='light'?'dark':'light')">
            <Sun v-if="theme==='light'" /> <Moon v-else />
          </button>

          <div class="avatar" @click="profileOpen=!profileOpen">
            <UserCircle2 class="avatar-ico" />
            <span class="name">{{ fullName || username }}</span>
            <ChevronDown class="chev" :class="{rot: profileOpen}" />

            <transition name="fade">
              <ul v-if="profileOpen" class="dropdown">
                <li><a href="javascript:;" @click="goto('/settings')"><Settings /> <span> {{ T[lang].settings }}</span></a></li>
                <li><a href="javascript:;" class="danger" @click="logout"><LogOut /> <span> {{ T[lang].logout }}</span></a></li>
              </ul>
            </transition>
          </div>
        </div>
      </header>

      <section class="content">
        <div class="score-widget" :class="{ loading: scoreLoading }">
          <div class="score-main">
            <div class="score-ring">
              <svg viewBox="0 0 120 120">
                <circle class="bg" cx="60" cy="60" r="52" />
                <circle class="fg" cx="60" cy="60" r="52" :style="{ '--progress': scoreProgress }" />
              </svg>
              <div class="center">
                <span class="points">{{ scoreLoading ? '...' : scoreDisplay }}</span>
                <small>{{ T[lang].scoreWidgetTitle }}</small>
              </div>
            </div>
            <div class="tier">
              <span class="tier-name">{{ scoreTierName }}</span>
              <p class="subtitle">{{ scoreLoading ? T[lang].scoreWidgetLoading : T[lang].scoreWidgetSubtitle }}</p>
            </div>
            <div class="progress">
              <div class="bar"><div class="fill" :style="{ '--progress': scoreProgress }"></div></div>
              <div class="caption">
                <span>{{ T[lang].scoreWidgetProgress }}</span>
                <span>{{ scoreProgressPercent }}%</span>
              </div>
            </div>
          </div>
          <div class="score-meta">
            <div class="meta-card">
              <span>{{ T[lang].scoreWidgetRank }}</span>
              <strong>{{ scoreLoading ? '--' : rankDisplay }}</strong>
            </div>
            <div class="meta-card">
              <span>{{ T[lang].scoreWidgetPlayers }}</span>
              <strong>{{ scoreLoading ? '--' : totalPlayersDisplay }}</strong>
            </div>
            <button class="meta-link" @click="viewScores">{{ T[lang].scoreWidgetView }}</button>
          </div>
        </div>

        <div class="teacher-card">
          <div class="frame">
            <span class="label">{{ T[lang].teacherTitle }}</span>
            <h3>{{ T[lang].teacherSubtitle }}</h3>
            <p>{{ T[lang].teacherMessage }}</p>
          </div>
        </div>

        <div v-if="currentComponent" class="active-panel">
          <header class="active-header">
            <span class="level-chip" v-if="currentSelection.level">{{ currentSelection.level.label[lang] }}</span>
            <div class="titles" v-if="currentSelection.challenge">
              <h2 class="challenge-title">{{ currentSelection.challenge.label[lang] }}</h2>
              <p class="challenge-desc">{{ currentSelection.challenge.summary[lang] }}</p>
            </div>
          </header>
          <component :is="currentComponent" :lang="lang" :theme="theme" />
        </div>
        <div v-else class="empty-state">
          <p>{{ T[lang].pickPrompt }}</p>
        </div>

        <div class="levels-browser">
          <section class="level-section" v-for="level in levels" :key="level.id">
            <div class="level-heading">
              <h3>{{ level.label[lang] }}</h3>
              <small>{{ level.challenges.length }}</small>
            </div>
            <div class="cards">
              <div
                class="card"
                v-for="challenge in level.challenges"
                :key="challenge.id"
                :class="{ active: isActiveChallenge(level.id, challenge.id) }"
                @click="selectChallenge(level.id, challenge.id)"
              >
                <h4>{{ challenge.label[lang] }}</h4>
                <p>{{ challenge.summary[lang] }}</p>
              </div>
            </div>
          </section>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.shell{
  --primary:#8f2c24; --accent:#d64c42; --peach:#ffe7db; --sand:#fff4e9; --ink:#2b1a1a;
  --bg:linear-gradient(180deg,#fffaf6,#fff4e9);
  --fg:var(--ink); --side-bg:rgba(255,255,255,.92); --bd:#f1d8cf; --hover:rgba(214,76,66,.08);
  --glass:rgba(255,255,255,.75); --pill-bg:#fff; --shadow:0 10px 28px rgba(214,76,66,.12);
  min-height:100vh; background:var(--bg); color:var(--fg); display:flex; transition:background .2s,color .2s
}
.shell[data-theme="dark"]{
  --primary:#ffb4a3; --accent:#ff8c7a; --peach:#2a1714; --sand:#1c1512; --ink:#f7ebe7;
  --bg:linear-gradient(180deg,#1b1412,#241815);
  --fg:var(--ink); --side-bg:rgba(24,15,13,.88); --bd:#3c2722; --hover:rgba(255,140,122,.12);
  --glass:rgba(24,15,13,.55); --pill-bg:#2a1a16; --shadow:0 10px 28px rgba(0,0,0,.35)
}

.sidebar{width:270px;background:var(--side-bg);backdrop-filter: blur(8px) saturate(1.08);
  border-inline-end:1px solid var(--bd);display:flex;flex-direction:column;gap:16px;padding:16px 12px;
  position:sticky;top:0;height:100vh;transition:width .18s ease}
.sidebar.collapsed{ width:80px; }
.brand{display:flex;align-items:center;gap:12px;padding:6px 10px;margin-bottom:6px}
.logo{width:40px;height:40px;border-radius:12px;object-fit:cover;box-shadow:var(--shadow)}
.brand-name{font-weight:800;letter-spacing:.2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

.menu{display:flex;flex-direction:column;gap:6px}
.menu-group{border-radius:14px;background:var(--glass);box-shadow:var(--shadow);padding:6px;border:1px solid var(--bd)}
.menu-item{width:100%;display:flex;align-items:center;gap:12px;padding:11px 12px;border-radius:12px;
  border:none;background:transparent;color:inherit;text-align:start;cursor:pointer;transition:.15s}
.menu-item:hover{background:var(--hover)}
.menu-item.danger:hover{background:rgba(255,0,0,.06)}
.mi{width:22px;height:22px}
.mt{flex:1}
.chev{opacity:.6;transition:transform .2s}
.chev.rot{transform:rotate(180deg)}
.submenu{padding:6px 6px 6px 42px;display:grid;gap:6px}
.submenu a{display:block;padding:8px 10px;border-radius:9px;text-decoration:none;color:inherit;transition:.15s}
.submenu a:hover{background:var(--hover)}
.submenu a.active{background:rgba(214,76,66,.18);font-weight:600}

.main{flex:1;display:flex;flex-direction:column;min-width:0}
.topbar{display:flex;align-items:center;justify-content:space-between;padding:14px 20px;
  border-bottom:1px solid var(--bd);backdrop-filter: blur(6px) saturate(1.05)}
.left{display:flex;align-items:center;gap:10px}
.welcome{display:flex;align-items:center;gap:10px;font-size:18px}
.welcome small{opacity:.7}
.wave{width:22px;height:22px;color:#ffccba}
.right{display:flex;align-items:center;gap:10px}

.pill{border:1px solid var(--bd);background:var(--pill-bg);color:inherit;border-radius:999px;
  padding:8px 12px;cursor:pointer;transition:.15s;display:inline-flex;align-items:center;gap:8px}
.pill.ghost{background:transparent}
.pill:hover{transform:translateY(-1px);background:var(--hover)}
.toggle svg{width:20px;height:20px}

.avatar{position:relative;display:flex;align-items:center;gap:10px;padding:6px 10px;border-radius:999px;
  background:var(--pill-bg);border:1px solid var(--bd);cursor:pointer}
.avatar-ico{width:24px;height:24px}
.avatar .name{max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dropdown{position:absolute;inset-inline-end:0;top:calc(100% + 6px);min-width:200px;background:var(--side-bg);
  border:1px solid var(--bd);border-radius:12px;box-shadow:var(--shadow);padding:6px;z-index:10}
.dropdown li a{display:flex;align-items:center;gap:8px;padding:10px;border-radius:8px;color:inherit;text-decoration:none}
.dropdown li a:hover{background:var(--hover)}
.dropdown .danger{color:#c03}

.content{padding:24px;display:flex;flex-direction:column;gap:28px}
.score-widget{display:flex;gap:24px;flex-wrap:wrap;align-items:center;background:var(--glass);border:1px solid var(--bd);border-radius:20px;padding:20px;box-shadow:var(--shadow)}
.score-widget.loading{opacity:.85}
.score-main{display:flex;flex-direction:column;gap:14px;min-width:260px}
.score-ring{position:relative;width:140px;height:140px}
.score-ring svg{width:100%;height:100%;transform:rotate(-90deg)}
.score-ring circle{fill:none;stroke-width:10px;stroke-linecap:round}
.score-ring circle.bg{stroke:rgba(214,76,66,.18)}
.score-ring circle.fg{stroke:var(--accent);stroke-dasharray:327;stroke-dashoffset:calc(327 - 327 * var(--progress,0));transition:stroke-dashoffset .6s ease}
.score-ring .center{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
.score-ring .points{font-size:2.4rem;font-weight:800;color:var(--accent)}
.score-ring small{font-weight:600;color:var(--fg)}
.tier-name{font-weight:700;font-size:1.05rem}
.subtitle{margin:0;color:rgba(0,0,0,.55)}
[data-theme="dark"] .subtitle{color:rgba(255,255,255,.7)}
.progress .bar{width:100%;height:10px;border-radius:999px;background:rgba(214,76,66,.15);overflow:hidden}
.progress .fill{width:calc(var(--progress,0)*100%);height:100%;background:linear-gradient(90deg,var(--accent),#ffb199)}
.progress .caption{display:flex;justify-content:space-between;font-size:.85rem;opacity:.7;margin-top:4px}
.score-meta{display:flex;gap:16px;align-items:stretch;flex:1;min-width:220px}
.meta-card{flex:1;background:var(--panel,#fff);border-radius:16px;border:1px solid var(--bd);box-shadow:0 10px 24px rgba(0,0,0,.08);padding:18px;display:flex;flex-direction:column;gap:6px;font-weight:600}
.meta-card strong{font-size:1.6rem}
.meta-link{align-self:flex-start;margin-inline-start:auto;border:none;background:var(--accent);color:#fff;padding:10px 18px;border-radius:12px;cursor:pointer;font-weight:700;box-shadow:0 10px 24px rgba(214,76,66,.2)}
.meta-link:hover{transform:translateY(-1px)}
.teacher-card{background:linear-gradient(120deg,rgba(214,76,66,.18),rgba(37,99,235,.18));border-radius:22px;padding:18px 22px;box-shadow:0 14px 30px rgba(0,0,0,.08);position:relative;overflow:hidden}
.teacher-card::after{content:'';position:absolute;inset:-80px -40px auto auto;width:220px;height:220px;background:radial-gradient(rgba(214,76,66,.45),transparent 65%);transform:rotate(25deg);opacity:.65}
.teacher-card .frame{position:relative;display:flex;flex-direction:column;gap:8px;z-index:1}
.teacher-card .label{display:inline-block;padding:6px 12px;border-radius:999px;background:rgba(255,255,255,.65);font-weight:700;color:#8f2c24;width:max-content}
.teacher-card h3{margin:0;font-size:1.4rem;font-weight:800;color:#8f2c24}
[data-theme="dark"] .teacher-card h3{color:#ffd0c5}
.teacher-card p{margin:0;color:#2b1a1a;font-size:.95rem;max-width:520px}
[data-theme="dark"] .teacher-card p{color:#f7ebe7}
.active-panel{background:var(--glass);border:1px solid var(--bd);border-radius:18px;padding:20px;box-shadow:var(--shadow)}
.active-header{display:flex;flex-direction:column;gap:12px;margin-bottom:16px}
.level-chip{display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:999px;
  background:rgba(214,76,66,.12);color:var(--accent);font-weight:600;font-size:.85rem;width:max-content}
.challenge-title{margin:0;font-size:1.5rem;font-weight:700}
.challenge-desc{margin:6px 0 0;opacity:.75}
.empty-state{background:var(--glass);border:1px dashed var(--bd);border-radius:16px;padding:24px;text-align:center;color:rgba(0,0,0,.6)}
.shell[data-theme="dark"] .empty-state{color:rgba(255,255,255,.7)}

.levels-browser{display:flex;flex-direction:column;gap:26px}
.level-section{background:var(--glass);border:1px solid var(--bd);border-radius:18px;padding:18px 20px;box-shadow:var(--shadow)}
.level-heading{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.level-heading small{background:rgba(0,0,0,.06);padding:4px 10px;border-radius:8px;font-weight:600}
.shell[data-theme="dark"] .level-heading small{background:rgba(255,255,255,.12)}

.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}
.card{background:var(--pill-bg);border:1px solid var(--bd);border-radius:16px;padding:18px;box-shadow:var(--shadow);
  cursor:pointer;transition:.15s;display:flex;flex-direction:column;gap:8px}
.card:hover{transform:translateY(-2px)}
.card.active{border-color:var(--accent);box-shadow:0 10px 28px rgba(214,76,66,.22);transform:translateY(-2px)}
.card h4{margin:0;font-size:1.1rem;font-weight:700}
.card p{margin:0;opacity:.72}

.fade-enter-active,.fade-leave-active{transition:opacity .15s}
.fade-enter-from,.fade-leave-to{opacity:0}

@media (max-width: 900px){
  .sidebar{position:fixed;inset-block:0;inset-inline-start:0;z-index:30}
  .main{margin-inline-start:270px}
  .sidebar.collapsed + .main{ margin-inline-start:80px; }
  .content{padding:20px}
}
</style>

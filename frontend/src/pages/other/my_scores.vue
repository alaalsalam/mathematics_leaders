<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RefreshCw, TrendingUp, Award, Activity, Target } from 'lucide-vue-next'
import { useGameScore } from '@/composables/useGameScore'

const {
  score,
  rank,
  totalPlayers,
  bestScore,
  loading,
  error,
  lastUpdated,
  refresh,
} = useGameScore()

const detectLang = () => {
  const htmlLang = (document.documentElement.lang || '').toLowerCase()
  if (htmlLang.startsWith('en')) return 'en'
  const stored = (localStorage.getItem('ml_lang') || '').toLowerCase()
  return stored.startsWith('en') ? 'en' : 'ar'
}
const detectTheme = () => (localStorage.getItem('ml_theme') || 'light')

const langState = ref(detectLang())
const theme = ref(detectTheme())

const isRTL = computed(() => langState.value === 'ar')
const strings = computed(() => langState.value === 'ar' ? {
  totalPoints: 'إجمالي النقاط',
  progressLabel: 'التقدم نحو الرتبة التالية',
  refresh: 'تحديث النقاط',
  lastUpdated: 'آخر تحديث',
  insightHeading: 'تحليلات سريعة',
  scoreTrendTitle: 'منحنى الأداء',
  scoreTrendCopy: 'يميل الأداء إلى التحسن خلال آخر المحاولات.',
  percentRankTitle: 'موقعك بين اللاعبين',
  topTierCopy: 'لقد بلغت أعلى رتبة متاحة! استمر في التألق.',
  nextTierLabel: 'المتبقي للوصول للرتبة التالية',
  recordTitle: 'أفضل نتيجة مسجلة',
  sparkLabel: 'تحوّل النقاط (آخر الجلسات)',
  metricsHeading: 'مؤشرات سريعة',
  playersLabel: 'عدد اللاعبين',
  rankLabel: 'ترتيبك',
  recordLabel: 'رقمك القياسي',
  minutesAgo: 'منذ دقائق',
  justNow: 'الآن',
} : {
  totalPoints: 'Total points',
  progressLabel: 'Progress to next tier',
  refresh: 'Refresh score',
  lastUpdated: 'Last updated',
  insightHeading: 'Quick insights',
  scoreTrendTitle: 'Performance trend',
  scoreTrendCopy: 'Your recent attempts show an upward trend.',
  percentRankTitle: 'Position among players',
  topTierCopy: 'You already sit at the highest tier—keep shining!',
  nextTierLabel: 'To reach the next tier',
  recordTitle: 'Best recorded score',
  sparkLabel: 'Score changes (recent sessions)',
  metricsHeading: 'Key metrics',
  playersLabel: 'Players',
  rankLabel: 'Your rank',
  recordLabel: 'Personal best',
  minutesAgo: 'minutes ago',
  justNow: 'just now',
})

const tiers = [
  { threshold: 0, title: { ar: 'مبتدئ الأرقام', en: 'Number Novice' } },
  { threshold: 25, title: { ar: 'مستكشف الأنماط', en: 'Pattern Explorer' } },
  { threshold: 75, title: { ar: 'مايسترو الرياضيات', en: 'Math Maestro' } },
  { threshold: 150, title: { ar: 'أسطورة التحديات', en: 'Challenge Legend' } },
]

const scoreValue = computed(() => Number(score.value || 0))
const bestValue = computed(() => Number(bestScore.value || 0))

const tierIndex = computed(() => {
  let idx = 0
  tiers.forEach((tier, i) => {
    if (scoreValue.value >= tier.threshold) idx = i
  })
  return idx
})

const currentTier = computed(() => tiers[tierIndex.value])
const nextTier = computed(() => tiers[tierIndex.value + 1] || null)
const tierLabel = computed(() => currentTier.value?.title?.[langState.value] || currentTier.value?.title?.en || '')

const progress = computed(() => {
  if (!nextTier.value) return 1
  const span = nextTier.value.threshold - currentTier.value.threshold
  if (span <= 0) return 1
  return Math.min(1, (scoreValue.value - currentTier.value.threshold) / span)
})

const intl = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 })

const formattedScore = computed(() => intl.format(scoreValue.value))
const formattedBest = computed(() => intl.format(bestValue.value))
const formattedRank = computed(() => (rank.value != null ? `#${rank.value}` : '--'))
const totalPlayersLabel = computed(() => (totalPlayers.value != null ? intl.format(totalPlayers.value) : '--'))

const lastUpdatedLabel = computed(() => {
  if (!lastUpdated.value) return '--'
  const delta = Date.now() - lastUpdated.value
  if (delta < 60_000) return strings.value.justNow
  const minutes = Math.round(delta / 60_000)
  return `${minutes} ${strings.value.minutesAgo}`
})

const sparkSteps = 9
const trendPoints = computed(() => {
  const peak = Math.max(scoreValue.value, bestValue.value, 1)
  const baseline = Math.max(10, peak * 0.45)
  const result = []
  for (let i = 0; i < sparkSteps; i += 1) {
    const ratio = sparkSteps === 1 ? 1 : i / (sparkSteps - 1)
    const wave = Math.sin((scoreValue.value + i) * 0.35) * peak * 0.05
    const val = Math.max(0, baseline + (peak - baseline) * ratio + wave)
    result.push(Math.round(val))
  }
  result[result.length - 1] = Math.max(scoreValue.value, 0)
  return result
})

const sparklineGeometry = computed(() => {
  const pts = trendPoints.value
  if (!pts.length) return []
  const width = 180
  const height = 54
  const max = Math.max(...pts)
  const min = Math.min(...pts)
  const range = max - min || 1
  return pts.map((value, index) => {
    const x = pts.length === 1 ? width : (width / (pts.length - 1)) * index
    const y = height - ((value - min) / range) * height
    return { x: Number(x.toFixed(2)), y: Number(y.toFixed(2)), value }
  })
})

const sparklinePath = computed(() => {
  const pts = sparklineGeometry.value
  if (!pts.length) return ''
  return pts.map((pt, idx) => `${idx === 0 ? 'M' : 'L'}${pt.x},${pt.y}`).join(' ')
})

const sparklineArea = computed(() => {
  const pts = sparklineGeometry.value
  if (!pts.length) return ''
  const height = 54
  const first = pts[0]
  const last = pts[pts.length - 1]
  const line = pts.map((pt, idx) => `${idx === 0 ? 'L' : 'L'}${pt.x},${pt.y}`).join(' ')
  return `M${first.x},${height} ${line} L${last.x},${height} Z`
})

const trendDelta = computed(() => {
  const pts = trendPoints.value
  if (pts.length < 2) return 0
  return pts[pts.length - 1] - pts[0]
})

const donutRadius = 58
const donutCircumference = 2 * Math.PI * donutRadius
const donutOffset = computed(() => donutCircumference * (1 - progress.value))
const progressPercent = computed(() => Math.round(progress.value * 100))

const percentile = computed(() => {
  if (!rank.value || !totalPlayers.value) return null
  const pct = Math.max(0, 100 - Math.round(((rank.value - 1) / totalPlayers.value) * 100))
  return pct
})

const iconLibrary = { trend: TrendingUp, award: Award, activity: Activity, target: Target }

const insightCards = computed(() => {
  const cards = []
  if (nextTier.value) {
    const remaining = Math.max(0, nextTier.value.threshold - scoreValue.value)
    cards.push({
      icon: 'target',
      title: strings.value.nextTierLabel,
      body: langState.value === 'ar'
        ? `تبقى ${intl.format(remaining)} نقطة للوصول إلى «${nextTier.value.title.ar}».`
        : `${intl.format(remaining)} pts to unlock “${nextTier.value.title.en}”.`,
    })
  } else {
    cards.push({
      icon: 'target',
      title: strings.value.nextTierLabel,
      body: langState.value === 'ar' ? strings.value.topTierCopy : strings.value.topTierCopy,
    })
  }

  cards.push({
    icon: 'trend',
    title: strings.value.scoreTrendTitle,
    body: langState.value === 'ar'
      ? `${strings.value.scoreTrendCopy} (+${intl.format(Math.max(0, trendDelta.value))}).`
      : `${strings.value.scoreTrendCopy} (+${intl.format(Math.max(0, trendDelta.value))}).`,
  })

  if (percentile.value != null) {
    cards.push({
      icon: 'award',
      title: strings.value.percentRankTitle,
      body: langState.value === 'ar'
        ? `أنت ضمن أفضل ${percentile.value}% من اللاعبين.`
        : `You currently outperform ${percentile.value}% of players.`,
    })
  }

  cards.push({
    icon: 'activity',
    title: strings.value.recordTitle,
    body: langState.value === 'ar'
      ? `أفضل نتيجة حققتها هي ${formattedBest.value} نقطة.`
      : `Your personal best sits at ${formattedBest.value} pts.`,
  })

  return cards
})

const metrics = computed(() => [
  { label: strings.value.rankLabel, value: formattedRank.value },
  { label: strings.value.playersLabel, value: totalPlayersLabel.value },
  { label: strings.value.recordLabel, value: formattedBest.value },
])

function handleRefresh() {
  refresh(true)
}

let langObserver = null
let themeObserver = null
let storageHandler = null

onMounted(() => {
  refresh(true)

  const updateLang = () => { langState.value = detectLang() }
  const updateTheme = () => { theme.value = detectTheme() }

  langObserver = new MutationObserver(updateLang)
  langObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] })

  themeObserver = new MutationObserver(updateTheme)
  themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })

  storageHandler = () => {
    updateLang()
    updateTheme()
  }
  window.addEventListener('storage', storageHandler)
})

onUnmounted(() => {
  if (langObserver) langObserver.disconnect()
  if (themeObserver) themeObserver.disconnect()
  if (storageHandler) window.removeEventListener('storage', storageHandler)
})
</script>

<template>
  <div
    class="scores-page"
    :dir="isRTL ? 'rtl' : 'ltr'"
    :data-theme="theme"
  >
    <section class="overview">
      <article class="panel donut-panel">
        <header class="panel__header">
          <span class="tier-chip">{{ tierLabel }}</span>
          <button class="refresh" data-ripple :disabled="loading" @click="handleRefresh">
            <RefreshCw class="ic" :class="{ spin: loading }" />
            {{ strings.refresh }}
          </button>
        </header>

        <div class="donut">
          <svg viewBox="0 0 160 160" aria-hidden="true">
            <defs>
              <linearGradient id="donutGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#c8a03b" />
                <stop offset="100%" stop-color="#0f8a3e" />
              </linearGradient>
            </defs>
            <circle class="track" cx="80" cy="80" :r="donutRadius" />
            <circle
              class="progress"
              cx="80"
              cy="80"
              :r="donutRadius"
              :style="{ strokeDasharray: `${donutCircumference}px`, strokeDashoffset: `${donutOffset}px` }"
            />
          </svg>
          <div class="donut__label">
            <strong>{{ formattedScore }}</strong>
            <span>{{ strings.totalPoints }}</span>
          </div>
        </div>

        <footer class="panel__footer">
          <div class="progress-caption">
            <span>{{ strings.progressLabel }}</span>
            <span>{{ progressPercent }}%</span>
          </div>
          <div class="timestamp">{{ strings.lastUpdated }} · {{ lastUpdatedLabel }}</div>
        </footer>
      </article>

      <article class="panel spark-panel">
        <header class="panel__header">
          <span class="panel__title">{{ strings.sparkLabel }}</span>
        </header>
        <div class="spark">
          <svg viewBox="0 0 180 72" aria-hidden="true">
            <defs>
              <linearGradient id="sparkFill" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="rgba(15,138,62,0.35)" />
                <stop offset="100%" stop-color="rgba(200,160,59,0.05)" />
              </linearGradient>
            </defs>
            <path v-if="sparklineArea" class="spark__area" :d="sparklineArea" fill="url(#sparkFill)" />
            <path v-if="sparklinePath" class="spark__path" :d="sparklinePath" />
          </svg>
          <div class="spark__meta">
            <span class="spark__delta" :class="{ up: trendDelta >= 0 }">
              {{ trendDelta >= 0 ? '+' : '' }}{{ intl.format(trendDelta) }}
            </span>
            <span class="spark__hint">{{ strings.scoreTrendCopy }}</span>
          </div>
        </div>

        <div class="metrics">
          <div v-for="metric in metrics" :key="metric.label" class="metric">
            <span class="metric__label">{{ metric.label }}</span>
            <strong class="metric__value">{{ metric.value }}</strong>
          </div>
        </div>
      </article>
    </section>

    <section class="insights">
      <h3>{{ strings.insightHeading }}</h3>
      <div class="insights__grid">
        <article
          v-for="(card, index) in insightCards"
          :key="index"
          class="insight-card"
        >
          <div class="insight-card__icon">
            <component :is="iconLibrary[card.icon]" class="glyph" />
          </div>
          <div class="insight-card__body">
            <h4>{{ card.title }}</h4>
            <p>{{ card.body }}</p>
          </div>
        </article>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
    </section>
  </div>
</template>

<style scoped>
.scores-page{
  display:flex;
  flex-direction:column;
  gap:28px;
  width:min(1100px,100%);
  margin:0 auto;
  padding:24px 20px 48px;
  color:var(--color-neutral-900);
}
.scores-page[data-theme="dark"]{
  color:var(--color-neutral-900);
}

.overview{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
  gap:20px;
}

.panel{
  position:relative;
  display:flex;
  flex-direction:column;
  gap:18px;
  padding:22px 24px;
  border-radius:26px;
  background:linear-gradient(135deg,rgba(15,138,62,0.08),rgba(200,160,59,0.12));
  border:1px solid rgba(200,160,59,0.25);
  box-shadow:0 28px 52px rgba(15,138,62,0.18);
  overflow:hidden;
}
[data-theme="dark"] .panel{
  background:linear-gradient(135deg,rgba(15,138,62,0.32),rgba(21,32,43,0.82));
  border-color:rgba(200,160,59,0.32);
  box-shadow:0 30px 60px rgba(0,0,0,0.55);
}

.panel::after{
  content:"";
  position:absolute;
  inset:-40% -20% auto -20%;
  height:70%;
  background:radial-gradient(circle at top,rgba(255,255,255,0.48),transparent 60%);
  opacity:.4;
  pointer-events:none;
}

.panel__header{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  position:relative;
  z-index:1;
}

.panel__title{font-weight:700;font-size:1.08rem}

.panel__footer{
  display:flex;
  flex-direction:column;
  gap:10px;
  position:relative;
  z-index:1;
}

.tier-chip{
  display:inline-flex;
  align-items:center;
  gap:6px;
  padding:6px 16px;
  border-radius:999px;
  background:rgba(200,160,59,0.18);
  color:#0f8a3e;
  font-weight:700;
  letter-spacing:.08em;
  text-transform:uppercase;
}
[data-theme="dark"] .tier-chip{
  background:rgba(200,160,59,0.36);
  color:#f4d67c;
}

.refresh{
  display:inline-flex;
  align-items:center;
  gap:6px;
  border-radius:999px;
  border:1px solid rgba(200,160,59,0.4);
  background:rgba(255,255,255,0.2);
  color:#0f8a3e;
  padding:8px 14px;
  font-weight:600;
  cursor:pointer;
  transition:transform .2s ease, box-shadow .2s ease;
}
.refresh:disabled{opacity:.6;cursor:wait}
.refresh:not(:disabled):hover{transform:translateY(-2px);box-shadow:0 14px 28px rgba(15,138,62,0.18)}
[data-theme="dark"] .refresh{background:rgba(21,32,43,0.6);color:#f4d67c;border-color:rgba(200,160,59,0.45)}

.ic{width:18px;height:18px}
.spin{animation:spin 1.1s linear infinite}

.donut{
  position:relative;
  display:flex;
  align-items:center;
  justify-content:center;
  width:100%;
  min-height:200px;
  z-index:1;
}
.donut svg{width:200px;height:200px;transform:rotate(-90deg)}
.track{fill:none;stroke:rgba(200,160,59,0.18);stroke-width:14;stroke-linecap:round}
.progress{fill:none;stroke:url(#donutGradient);stroke-width:14;stroke-linecap:round;transition:stroke-dashoffset .9s cubic-bezier(.22,1,.36,1)}

.donut__label{
  position:absolute;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  gap:6px;
  color:#0f8a3e;
}
.donut__label strong{font-size:2.8rem;line-height:1;font-weight:800;text-shadow:0 12px 26px rgba(15,138,62,0.28)}
.donut__label span{font-weight:600;letter-spacing:.04em}
[data-theme="dark"] .donut__label{color:#f4d67c;text-shadow:0 14px 32px rgba(0,0,0,0.55)}

.progress-caption{
  display:flex;
  justify-content:space-between;
  font-weight:600;
  color:rgba(17,24,39,0.75);
}
[data-theme="dark"] .progress-caption{color:rgba(255,255,255,0.72)}
.timestamp{font-size:.82rem;opacity:.7}

.spark{display:flex;flex-direction:column;gap:10px;position:relative;z-index:1}
.spark svg{width:100%;max-width:220px}
.spark__area{stroke:none;opacity:.9}
.spark__path{fill:none;stroke:#0f8a3e;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 10px 16px rgba(15,138,62,0.25))}
.spark__meta{display:flex;align-items:center;gap:10px;font-size:.9rem}
.spark__delta{font-weight:700;color:#0f8a3e}
.spark__delta.up::before{content:'↗';margin-inline-end:4px}
[data-theme="dark"] .spark__delta{color:#f4d67c}
.spark__hint{opacity:.7}

.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:12px}
.metric{position:relative;padding:14px 16px;border-radius:18px;background:rgba(255,255,255,0.78);border:1px solid rgba(200,160,59,0.25);box-shadow:0 16px 26px rgba(15,138,62,0.12)}
.metric__label{display:block;font-size:.85rem;opacity:.75;font-weight:600}
.metric__value{display:block;font-size:1.6rem;font-weight:800;color:#0f8a3e}
[data-theme="dark"] .metric{background:rgba(21,32,43,0.85);border-color:rgba(200,160,59,0.3);box-shadow:0 20px 42px rgba(0,0,0,0.55)}
[data-theme="dark"] .metric__value{color:#f4d67c}

.insights{display:flex;flex-direction:column;gap:18px}
.insights h3{margin:0;font-size:1.3rem;font-weight:800}
.insights__grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}

.insight-card{
  position:relative;
  display:flex;
  gap:14px;
  padding:18px 20px;
  border-radius:22px;
  background:rgba(255,255,255,0.92);
  border:1px solid rgba(200,160,59,0.25);
  box-shadow:0 18px 36px rgba(15,138,62,0.16);
  overflow:hidden;
}
.insight-card::after{
  content:"";
  position:absolute;
  inset:auto -30% -50% 0;
  height:140px;
  background:linear-gradient(135deg,rgba(200,160,59,0.18),transparent);
  opacity:.4;
}
[data-theme="dark"] .insight-card{background:rgba(21,32,43,0.88);border-color:rgba(200,160,59,0.28);box-shadow:0 26px 48px rgba(0,0,0,0.6)}

.insight-card__icon{width:40px;height:40px;border-radius:14px;background:linear-gradient(135deg,#c8a03b,#0f8a3e);display:flex;align-items:center;justify-content:center;flex-shrink:0;animation:float 3.2s ease-in-out infinite}
[data-theme="dark"] .insight-card__icon{background:linear-gradient(135deg,#f4d67c,#0f8a3e)}
.glyph{width:22px;height:22px;color:#fff}

.insight-card__body{position:relative;z-index:1;display:flex;flex-direction:column;gap:6px}
.insight-card__body h4{margin:0;font-size:1.05rem;font-weight:700}
.insight-card__body p{margin:0;opacity:.78;line-height:1.45}
[data-theme="dark"] .insight-card__body p{color:rgba(255,255,255,0.78)}

.error{color:#dc2626;font-weight:600}

@keyframes spin{to{transform:rotate(360deg)}}
@keyframes float{0%,100%{transform:translateY(0);}50%{transform:translateY(-6px);}}

@media (max-width: 720px){
  .panel{padding:18px}
  .metrics{grid-template-columns:repeat(auto-fit,minmax(140px,1fr))}
  .insight-card{padding:16px}
  .scores-page{padding:20px 16px 36px}
}
</style>

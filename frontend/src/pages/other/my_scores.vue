<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RefreshCw } from 'lucide-vue-next'
import { useGameScore } from '@/composables/useGameScore'

const { score, rank, totalPlayers, bestScore, loading, error, lastUpdated, refresh } = useGameScore()

const tiers = [
  { threshold: 0, title:{ ar:'مبتدئ الأرقام', en:'Number Novice' } },
  { threshold: 25, title:{ ar:'مستكشف الأنماط', en:'Pattern Explorer' } },
  { threshold: 75, title:{ ar:'مايسترو الرياضيات', en:'Math Maestro' } },
  { threshold: 150, title:{ ar:'أسطورة التحديات', en:'Challenge Legend' } },
]
const detectLang = () => {
  const fromAttr = (document.documentElement.lang || '').toLowerCase()
  if (fromAttr.startsWith('en')) return 'en'
  const stored = (localStorage.getItem('ml_lang') || '').toLowerCase()
  if (stored.startsWith('en')) return 'en'
  return 'ar'
}
const langState = ref(detectLang())
const propsLang = computed(() => langState.value)

const scoreValue = computed(() => Number(score.value || 0))
const tierIndex = computed(() => {
  let idx = 0
  tiers.forEach((tier, i) => {
    if(scoreValue.value >= tier.threshold) idx = i
  })
  return idx
})

const currentTier = computed(() => tiers[tierIndex.value])
const nextTier = computed(() => tiers[tierIndex.value + 1] || null)

const tierTitle = computed(() => currentTier.value?.title?.[propsLang.value] || currentTier.value?.title?.en || '')

const progress = computed(() => {
  if(!nextTier.value) return 1
  const span = nextTier.value.threshold - currentTier.value.threshold
  if(span <= 0) return 1
  return Math.min(1, (scoreValue.value - currentTier.value.threshold) / span)
})

const intl = new Intl.NumberFormat('en-US', { minimumFractionDigits:0, maximumFractionDigits:0 })

const formattedScore = computed(() => intl.format(scoreValue.value))
const formattedBest = computed(() => intl.format(Number(bestScore.value || 0)))
const formattedRank = computed(() => rank.value != null ? `#${rank.value}` : '--')
const totalPlayersLabel = computed(() => totalPlayers.value != null ? intl.format(totalPlayers.value) : '--')

const lastUpdatedLabel = computed(() => {
  if(!lastUpdated.value) return '--'
  const date = new Date(lastUpdated.value)
  return date.toLocaleString()
})

onMounted(() => {
  refresh(true)
  const update = () => { langState.value = detectLang() }
  const observer = new MutationObserver(update)
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] })
  window.addEventListener('storage', update)
  onUnmounted(() => {
    observer.disconnect()
    window.removeEventListener('storage', update)
  })
})

function handleRefresh(){ refresh(true) }

const insights = computed(() => {
  const items = []
  if(nextTier.value){
    const remaining = Math.max(0, nextTier.value.threshold - scoreValue.value)
    items.push(propsLang.value==='ar'
      ? `أنت بحاجة إلى ${intl.format(remaining)} نقطة للوصول إلى «${nextTier.value.title.ar}».`
      : `You need ${intl.format(remaining)} pts to reach “${nextTier.value.title.en}”.`)
  } else {
    items.push(propsLang.value==='ar'
      ? 'لقد بلغت أعلى رتبة حالية! استمر في تحقيق النجاحات.'
      : 'You are at the top tier—keep the streak going!')
  }
  if(rank.value && totalPlayers.value){
    const percentile = Math.max(0, 100 - Math.round((rank.value - 1) / totalPlayers.value * 100))
    items.push(propsLang.value==='ar'
      ? `أنت ضمن أفضل ${percentile}% من اللاعبين النشطين.`
      : `You are in the top ${percentile}% of active players.`)
  }
  items.push(propsLang.value==='ar'
    ? `أفضل نتيجة مسجلة حاليًا هي ${formattedBest.value} نقطة.`
    : `The current record stands at ${formattedBest.value} pts.`)
  return items
})
</script>

<template>
<div class="scores-page" :data-theme="propsLang">
    <section class="hero">
      <div class="score-card">
        <div class="badge">{{ tierTitle }}</div>
        <div class="value">{{ formattedScore }}</div>
        <div class="label">{{ propsLang==='ar' ? 'مجموع نقاطك' : 'Total Points' }}</div>
        <div class="meter">
          <div class="meter-fill" :style="{ '--progress': progress }"></div>
        </div>
        <div class="meter-caption">
          <span>{{ propsLang==='ar' ? 'تقدمك نحو الرتبة التالية' : 'Progress to next tier' }}</span>
          <span>{{ Math.round(progress * 100) }}%</span>
        </div>
        <button class="refresh" :disabled="loading" @click="handleRefresh">
          <RefreshCw class="ic" :class="{ spin: loading }" />
          {{ propsLang==='ar' ? 'تحديث النقاط' : 'Refresh score' }}
        </button>
        <small class="timestamp">{{ propsLang==='ar' ? 'آخر تحديث:' : 'Last updated:' }} {{ lastUpdatedLabel }}</small>
      </div>
      <div class="stats">
        <div class="stats-card">
          <span class="label">{{ propsLang==='ar' ? 'ترتيبك' : 'Your rank' }}</span>
          <strong class="stat">{{ formattedRank }}</strong>
        </div>
        <div class="stats-card">
          <span class="label">{{ propsLang==='ar' ? 'عدد اللاعبين' : 'Players' }}</span>
          <strong class="stat">{{ totalPlayersLabel }}</strong>
        </div>
        <div class="stats-card">
          <span class="label">{{ propsLang==='ar' ? 'رقم قياسي' : 'Record' }}</span>
          <strong class="stat">{{ formattedBest }}</strong>
        </div>
      </div>
    </section>

    <section class="insights">
      <h3>{{ propsLang==='ar' ? 'ملخص سريع' : 'Quick insights' }}</h3>
      <ul>
        <li v-for="(line, idx) in insights" :key="idx">{{ line }}</li>
      </ul>
      <p v-if="error" class="error">{{ error }}</p>
    </section>
  </div>
</template>

<style scoped>
.scores-page{ display:flex; flex-direction:column; gap:20px; padding:0; width:100% }
.hero{ display:flex; gap:20px; flex-wrap:wrap; justify-content:center }
.score-card{ position:relative; width:100%; max-width:360px; background:linear-gradient(160deg,#2563eb,#1e3a8a); color:#fff; border-radius:24px; padding:24px; box-shadow:0 18px 36px rgba(30,64,175,.35); display:flex; flex-direction:column; gap:14px; align-items:flex-start }
.badge{ background:rgba(255,255,255,.18); padding:6px 14px; border-radius:999px; font-weight:600 }
.value{ font-size:3rem; font-weight:800; letter-spacing:1px }
.label{ opacity:.9; font-weight:500 }
.meter{ width:100%; height:10px; border-radius:999px; background:rgba(255,255,255,.25); overflow:hidden }
.meter-fill{ width:calc(var(--progress) * 100%); height:100%; background:linear-gradient(90deg,#fcd34d,#22c55e) }
.meter-caption{ width:100%; display:flex; justify-content:space-between; font-size:.85rem; opacity:.85 }
.refresh{ margin-top:4px; display:inline-flex; align-items:center; gap:6px; border:none; border-radius:10px; background:rgba(15,23,42,.15); color:#fff; padding:8px 14px; cursor:pointer; font-weight:600 }
.refresh:disabled{ opacity:.6; cursor:wait }
.ic{ width:18px; height:18px }
.spin{ animation: spin 1s linear infinite }
.timestamp{ font-size:.7rem; opacity:.65 }

.stats{ flex:1; min-width:220px; display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:18px }
.stats-card{ background:var(--panel,#fff); color:var(--fg,#1f2937); border-radius:16px; padding:18px; box-shadow:0 12px 24px rgba(15,23,42,.1); display:flex; flex-direction:column; gap:6px }
.stats-card .label{ font-size:.9rem; opacity:.75 }
.stats-card .stat{ font-size:1.8rem; font-weight:700 }

.insights{ background:var(--panel,#fff); border-radius:16px; padding:18px; box-shadow:0 12px 28px rgba(15,23,42,.08) }
.insights h3{ margin:0 0 12px; font-size:1.2rem; font-weight:700 }
.insights ul{ margin:0; padding-inline-start:20px; display:grid; gap:8px }
.error{ margin-top:12px; color:#b91c1c; font-weight:600 }

@keyframes spin{ to{ transform:rotate(360deg) } }

@media(max-width:720px){
  .hero{ gap:16px }
}
</style>

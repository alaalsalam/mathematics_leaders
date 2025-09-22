<script setup>
import { ref, computed, onMounted } from 'vue'

// لغة بسيطة من localStorage
const lang = ref(localStorage.getItem('ml_lang') || 'ar')
const dir  = computed(() => (lang.value === 'ar' ? 'rtl' : 'ltr'))

// بروفايل اللاعب (تم تخزينه بعد تسجيل الدخول)
const profile = ref(JSON.parse(localStorage.getItem('ml_profile') || '{}'))

// عناوين
const t = (k)=>({
  en:{
    welcome: 'Welcome',
    subtitle: 'Choose something to start playing & learning!',
    quick: 'Quick links',
    start1: 'Start Challenge 1',
    start2: 'Start Challenge 2',
    scores: 'My Scores',
    settings: 'Settings',
  },
  ar:{
    welcome: 'مرحبًا',
    subtitle: 'اختر شيئًا للبدء باللعب والتعلّم!',
    quick: 'روابط سريعة',
    start1: 'ابدأ التحدي 1',
    start2: 'ابدأ التحدي 2',
    scores: 'درجاتي',
    settings: 'الإعدادات',
  }
}[lang.value][k])

// حماية بسيطة: لو ما في بروفايل نرجّع لصفحة الدخول
onMounted(() => {
  document.documentElement.dir = dir.value
  document.documentElement.lang = lang.value
  if (!profile.value?.username){
    window.location.href = '/math-leaders-games/#/login'
  }
})

// أفعال مؤقتة
function go(ch){ alert((lang.value==='ar'?'فتح ':'Open ')+ch) }
</script>

<template>
  <div class="page" :dir="dir">
    <section class="hero">
      <h1>{{ t('welcome') }} {{ profile?.username }} 👋</h1>
      <p class="sub">{{ t('subtitle') }}</p>
    </section>

    <section class="grid">
      <div class="card big" @click="go('Challenge 1')">
        <div class="badge">1</div>
        <h3>{{ t('start1') }}</h3>
        <p>Numbers • Patterns • Fun</p>
      </div>

      <div class="card big" @click="go('Challenge 2')">
        <div class="badge">2</div>
        <h3>{{ t('start2') }}</h3>
        <p>Shapes • Logic • Puzzles</p>
      </div>

      <div class="card" @click="go('Scores')">
        <h4>🏆 {{ t('scores') }}</h4>
      </div>

      <div class="card" @click="go('Settings')">
        <h4>⚙️ {{ t('settings') }}</h4>
      </div>
    </section>
  </div>
</template>

<style scoped>
:root{
  --brand1:#8f2c24; --brand2:#d64c42; --brand3:#ff7a59;
  --bg:#fff; --text:#1f2937; --muted:#6b7280;
  --card:rgba(255,255,255,.7); --shadow:0 10px 30px rgba(0,0,0,.10);
}
:global(body.theme-dark){
  --bg:#0f1013; --text:#f1f5f9; --muted:#94a3b8;
  --card:rgba(15,16,19,.7); --shadow:0 10px 30px rgba(0,0,0,.35);
}

.page{min-height:100vh;background:var(--bg);color:var(--text);padding:26px}
.hero{
  max-width:960px;margin:0 auto 22px auto;text-align:center;
  background:var(--card);backdrop-filter:blur(10px);box-shadow:var(--shadow);
  border-radius:22px;padding:34px 18px;
}
.hero h1{margin:0 0 8px 0;font-size:2rem}
.sub{margin:0;color:var(--muted)}

.grid{
  max-width:1000px;margin:0 auto;
  display:grid;gap:16px;
  grid-template-columns: repeat(12,1fr);
}
.card{
  grid-column: span 6 / span 6;
  background:var(--card);backdrop-filter:blur(8px);box-shadow:var(--shadow);
  border-radius:18px;padding:18px;cursor:pointer;transition:.18s;
}
.card:hover{transform:translateY(-2px);box-shadow:0 16px 36px rgba(0,0,0,.16)}
.card.big{grid-column: span 6 / span 6; display:flex; flex-direction:column; gap:6px}
.badge{
  width:36px;height:36px;border-radius:50%;display:grid;place-items:center;
  color:#fff;font-weight:900;background:linear-gradient(135deg,var(--brand3),var(--brand1));
  box-shadow:0 6px 14px rgba(214,76,66,.25)
}
h3,h4{margin:.2rem 0}
p{margin:0;color:var(--muted)}

@media (max-width: 880px){
  .card, .card.big{grid-column: span 12 / span 12}
}
</style>

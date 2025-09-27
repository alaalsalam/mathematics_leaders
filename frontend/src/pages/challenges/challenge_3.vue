<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { RefreshCw, RotateCcw, Check } from 'lucide-vue-next'

const props = defineProps({
  lang: { type: String, default: 'ar' },
  theme: { type: String, default: 'light' }
})

const T = {
  ar: {
    title: 'التحدي 3: إيجاد عددين من المجموع والفرق',
    rule: 'اختر الزوج الصحيح (أكبر، أصغر) بحيث يكون مجموعهما S والفرق بينهما D.',
    newQ: 'سؤال جديد',
    reset: 'إعادة تعيين',
    check: 'تحقّق',
    correct: 'إجابة صحيحة',
    wrong: 'إجابة غير صحيحة',
    done: 'أكملت هذه الجولة',
    q: (i, S, D) => `(${i}) جد عددين ناتج جمعهما ${S} والفرق بينهما ${D}`
  },
  en: {
    title: 'Challenge 3: Find two numbers from sum and difference',
    rule: 'Pick the correct pair (greater, smaller) with sum S and difference D.',
    newQ: 'New puzzle',
    reset: 'Reset',
    check: 'Check',
    correct: 'Correct',
    wrong: 'Incorrect',
    done: 'Round completed',
    q: (i, S, D) => `(${i}) Find two numbers with sum ${S} and difference ${D}`
  }
}
const L = computed(() => (T[props.lang] ? props.lang : 'ar'))

/* ===== sounds ===== */
import successUrl from '@/assets/sounds/success3.mp3'
// import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong3.mp3'   // تأكد من الاسم الصحيح للملف

const sOK   = typeof Audio !== 'undefined' ? new Audio(successUrl) : null
// const sClap = typeof Audio !== 'undefined' ? new Audio(clapUrl)    : null
const sWrong= typeof Audio !== 'undefined' ? new Audio(wrongUrl)   : null

sOK && (sOK.preload = 'auto')
// sClap && (sClap.preload = 'auto')
sWrong && (sWrong.preload = 'auto')


// عشوائي
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]]} return x }

// بنية السؤال
/**
 * question = {
 *  S, D, ans:[A,B], options:[{a,b,isAns}], pickedIndex:null|number, judged:false, firstTry:true
 * }
 */
const N = 4
const questions = ref([])
const solvedCount = computed(() => questions.value.filter(q => q.judged && q.options[q.pickedIndex]?.isAns).length)
const allAnswered = computed(() => questions.value.length>0 && questions.value.every(q => q.judged))

function makeAns(S,D){
  // الشرط: نفس الإشارة parity، و S >= D >= 0
  // الحل: A=(S+D)/2 ، B=(S-D)/2
  return [(S + D)/2, (S - D)/2]
}
function validPair(x){ return Number.isInteger(x) && x>=0 }
function mkQuestion(){
  // نختار S,D بحيث يعطيان حلين صحيحين صحيحين (A,B)
  let S,D,A,B
  while(true){
    S = rndInt(10, 60)                 // نطاق مجموع معقول
    D = rndInt(0, 20)                  // نطاق فرق معقول
    if ((S & 1) !== (D & 1)) continue  // شرط التكافؤ
    if (S < D) continue
    ;[A,B] = makeAns(S,D)
    if (validPair(A) && validPair(B)) break
  }
  // البدائل: تبديل طفيف يضلّل بدون كسر المنطق
  const alts = new Set()
  const addAlt = (x,y)=>{
    const k = `${x},${y}`
    if (x>=0 && y>=0 && Number.isInteger(x) && Number.isInteger(y) && k !== `${A},${B}`) alts.add(k)
  }
  addAlt(A+1,B-1)
  addAlt(A-1,B+1)
  addAlt(A+2,B-2)
  addAlt(A-2,B+2)
  addAlt(A+1,B)    // خطأ في الفرق
  addAlt(A,B+1)    // خطأ في الفرق
  const opts = [{a:A,b:B,isAns:true}]
  for (const k of Array.from(alts).slice(0,3)) {
    const [a,b] = k.split(',').map(n=>Number(n))
    opts.push({a,b,isAns:false})
    if (opts.length===4) break
  }
  while(opts.length<4){ // احتياط
    const da = rndInt(-3,3), db = rndInt(-3,3)
    const a = Math.max(0, A+da), b = Math.max(0, B+db)
    if(!(a===A && b===B)) opts.push({a,b,isAns:false})
  }
  return {
    S, D, ans:[A,B],
    options: shuffle(opts),
    pickedIndex: null,
    judged: false,
    firstTry: true
  }
}

function newRound(){
  questions.value = Array.from({length:N}, ()=> mkQuestion())
}
function resetRound(){
  for(const q of questions.value){
    q.pickedIndex = null
    q.judged = false
    q.firstTry = true
  }
}
async function addPoint(){
  try{
    await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1', {
      method:'GET', credentials:'include'
    })
  }catch{}
}
async function pickOption(q, idx){
  if(q.judged) return
  q.pickedIndex = idx
  q.judged = true
  const ok = q.options[idx].isAns
  if(ok){
    sOK && sOK.play()
    if(allAnswered.value) sOK && sOK.play()
    // نقطة واحدة للإجابة الصحيحة من أول محاولة
    if(q.firstTry) await addPoint()
  }else{
    sWrong && sWrong.play()
  }
}
function unjudge(q){ // يسمح بالمحاولة مجدداً إن أراد
  q.judged = false
  q.firstTry = false
  q.pickedIndex = null
}

onMounted(newRound)
watch(()=>props.lang,()=>{}) // لا شيء، فقط الحفاظ على توافق الواجهة
</script>

<template>
  <div class="challenge3 challenge-surface" :data-theme="props.theme">
    <h2 class="title">{{ T[L].title }}</h2>
    <p class="rule">{{ T[L].rule }}</p>

    <div class="qs">
      <div v-for="(q,i) in questions" :key="i" class="qcard">
        <div class="qtext">{{ T[L].q(i+1, q.S, q.D) }}</div>

        <div class="opts">
          <button
            v-for="(op,j) in q.options"
            :key="j"
            class="opt"
            :class="{
              chosen: q.pickedIndex===j,
              ok: q.judged && q.options[j].isAns,
              bad: q.judged && q.pickedIndex===j && !q.options[j].isAns
            }"
            @click="pickOption(q, j)"
          >
            ( {{ op.a }} ، {{ op.b }} )
          </button>
        </div>

        <div v-if="q.judged" class="feedback" :class="{ok: q.options[q.pickedIndex].isAns}">
          {{ q.options[q.pickedIndex].isAns ? T[L].correct : T[L].wrong }}
          <button class="retry" v-if="!q.options[q.pickedIndex].isAns" @click="unjudge(q)">↺</button>
        </div>
      </div>
    </div>

    <div class="toolbar">
      <div class="status">
        <Check class="ic" /> {{ solvedCount }} / {{ questions.length }}
        <span v-if="allAnswered && solvedCount===questions.length" class="done"> · {{ T[L].done }}</span>
      </div>
      <div class="actions">
        <button class="btn" @click="resetRound"><RotateCcw class="ic" /> {{ T[L].reset }}</button>
        <button class="btn" @click="newRound"><RefreshCw class="ic" /> {{ T[L].newQ }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.challenge3{ --bg:var(--c-bg,#fff); --fg:var(--c-fg,#111827); --muted:#6b7280 }
[data-theme="dark"] .challenge3{ --bg:#0b1220; --fg:#e5e7eb; --muted:#9ca3af }

.title{ font-weight:700; margin:0 0 .25rem }
.rule{ color:var(--muted); margin:0 0 1rem }

.qs{ display:grid; gap:.75rem }
.qcard{
  background:var(--bg);
  border:1px solid #e5e7eb55; border-radius:1rem;
  padding:.75rem .9rem; box-shadow:0 4px 14px rgba(0,0,0,.06)
}
.qtext{ font-weight:600; margin-bottom:.5rem }
.opts{ display:flex; flex-wrap:wrap; gap:.5rem }
.opt{
  padding:.45rem .7rem; border-radius:.75rem; cursor:pointer;
  border:1px solid #e5e7ebaa; background:var(--bg);
  font-variant-numeric:tabular-nums;
}
.opt.chosen{ box-shadow:0 0 0 2px rgba(99,102,241,.35) inset }
.opt.ok{ background:#dcfce7; border-color:#bbf7d0; color:#166534 }
.opt.bad{ background:#fee2e2; border-color:#fecaca; color:#991b1b }

.feedback{ margin-top:.4rem; font-size:.9rem; color:#991b1b }
.feedback.ok{ color:#166534 }
.retry{ margin-inline-start:.5rem; border:none; background:transparent; cursor:pointer }

.toolbar{
  display:flex; justify-content:space-between; align-items:center; margin-top:1rem
}
.status{ color:var(--muted); display:flex; align-items:center; gap:.35rem }
.done{ color:#166534 }
.actions{ display:flex; gap:.5rem }
.btn{ display:inline-flex; align-items:center; gap:.35rem; padding:.5rem .7rem;
      border-radius:.75rem; border:1px solid #e5e7eb55; background:var(--bg); cursor:pointer }
.ic{ width:16px; height:16px }
[data-theme="dark"] .challenge3{ background:transparent; color:#e2e8f0 }
[data-theme="dark"] .challenge3 .rule{ color:#cbd5f5 }
[data-theme="dark"] .challenge3 .qcard{ background:#132338; border:1px solid rgba(148,163,184,.45); box-shadow:0 18px 32px rgba(7,15,32,.55) }
[data-theme="dark"] .challenge3 .qtext{ color:#f1f5f9 }
[data-theme="dark"] .challenge3 .opt{ background:#1c3050; border-color:rgba(148,163,184,.5); color:#f8fafc }
[data-theme="dark"] .challenge3 .opt:hover{ border-color:#60a5fa; background:#223a60 }
[data-theme="dark"] .challenge3 .opt.chosen{ box-shadow:0 0 0 2px rgba(96,165,250,.55) inset }
[data-theme="dark"] .challenge3 .opt.ok{ background:rgba(34,197,94,.26); border-color:rgba(74,222,128,.6); color:#dcfce7 }
[data-theme="dark"] .challenge3 .opt.bad{ background:rgba(248,113,113,.28); border-color:rgba(248,113,113,.55); color:#fee2e2 }
[data-theme="dark"] .challenge3 .feedback{ color:#fca5a5 }
[data-theme="dark"] .challenge3 .feedback.ok{ color:#bbf7d0 }
[data-theme="dark"] .challenge3 .status{ color:#d1d9ff }
[data-theme="dark"] .challenge3 .done{ color:#86efac }
[data-theme="dark"] .challenge3 .btn{ background:#1c3050; border-color:rgba(148,163,184,.45); color:#f8fafc; box-shadow:0 10px 22px rgba(7,15,32,.4) }
</style>

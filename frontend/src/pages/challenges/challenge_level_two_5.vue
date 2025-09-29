<script setup>
/* =========================================================
   Level 2 — Challenge 5: Fraction subtraction (dark-mode pass)
   -----------------------------------------------------------
   What changed (UI only):
   - Strong theme tokens for light/dark (panels, borders, dividers).
   - Higher-contrast fraction bars, dashed drops, and number chips.
   - Numeric isolation + Arabic digits rendering kept and refined.
   - Clear hover/focus states and subtle elevation on cards.
========================================================= */

import { ref, computed, onMounted } from 'vue'
import { Check, RotateCcw, RefreshCw } from 'lucide-vue-next'

const props = defineProps({
  lang:{type:String,default:'ar'},
  theme:{type:String,default:'light'}
})

/* --------- copy --------- */
const T = {
  ar:{
    title:'المستوى الثاني – التحدي 5: أكمل طرح الكسور',
    rule:(t)=>`ضع عددًا كليًا في كل مربع لتصبح المعادلة صحيحة:  ${t.num}/${t.den} =  ١/□  −  □/${t.d2}.  اسحب الرقمين من لوحة الأعداد.`,
    bank:'لوحة الأعداد', newQ:'سؤال جديد', reset:'إعادة تعيين', check:'تحقّق',
    correct:'إجابة صحيحة', wrong:'تحقق من القيم', clear:'تفريغ الخلية'
  },
  en:{
    title:'Level 2 – Challenge 5: Complete the fraction subtraction',
    rule:(t)=>`Place integers to make the equation true:  ${t.num}/${t.den} =  1/□  −  □/${t.d2}.  Drag the two numbers from the bank.`,
    bank:'Number bank', newQ:'New puzzle', reset:'Reset', check:'Check',
    correct:'Correct answer', wrong:'Check values', clear:'Clear'
  }
}
const L = computed(()=> (T[props.lang]?props.lang:'ar'))

/* --------- sounds (optional) --------- */
import successUrl from '@/assets/sounds/success2.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong2.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK&&(sOK.preload='auto'); sClap&&(sClap.preload='auto'); sWrong&&(sWrong.preload='auto')

/* --------- helpers --------- */
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]] } return x }

/* --------- puzzles --------- */
const target = ref({num:1, den:6, d2:6})
const bank   = ref([])
const answer = ref({ A:null, N:null })
const toast  = ref(null)
const solved = ref(false)

const puzzleBank = [
  { id:'p1',  target:{ num:1, den:6 },  d2:6,  solution:{ A:2, N:2 }, extras:[1,3,4,5,7,8] },
  { id:'p2',  target:{ num:1, den:6 },  d2:9,  solution:{ A:2, N:3 }, extras:[1,4,5,6,7,8] },
  { id:'p3',  target:{ num:1, den:6 },  d2:12, solution:{ A:2, N:4 }, extras:[1,3,5,6,7,9] },
  { id:'p4',  target:{ num:1, den:6 },  d2:6,  solution:{ A:3, N:1 }, extras:[2,4,5,7,8,9] },
  { id:'p5',  target:{ num:2, den:6 },  d2:6,  solution:{ A:2, N:1 }, extras:[3,4,5,7,8,9] },
  { id:'p6',  target:{ num:1, den:8 },  d2:8,  solution:{ A:2, N:3 }, extras:[1,2,4,5,6,7] },
  { id:'p7',  target:{ num:3, den:8 },  d2:8,  solution:{ A:2, N:1 }, extras:[2,4,5,6,7,9] },
  { id:'p8',  target:{ num:1, den:9 },  d2:9,  solution:{ A:3, N:2 }, extras:[1,3,4,5,6,7] },
  { id:'p9',  target:{ num:3, den:9 },  d2:6,  solution:{ A:2, N:1 }, extras:[2,4,5,7,8,9] },
  { id:'p10', target:{ num:1, den:10 }, d2:5,  solution:{ A:2, N:2 }, extras:[1,3,4,6,7,8] },
  { id:'p11', target:{ num:2, den:10 }, d2:10, solution:{ A:2, N:3 }, extras:[1,4,5,6,7,9] },
  { id:'p12', target:{ num:1, den:12 }, d2:4,  solution:{ A:3, N:1 }, extras:[2,5,6,7,8,9] }
]
const currentPuzzle = ref(puzzleBank[0])
const lastPuzzleId  = ref(null)

function pickNextPuzzle(){
  let candidate
  do{ candidate = puzzleBank[Math.floor(Math.random()*puzzleBank.length)] }
  while(candidate.id === lastPuzzleId.value)
  lastPuzzleId.value = candidate.id
  return candidate
}
function buildBank(puz){
  const set = new Set([puz.solution.A, puz.solution.N, ...(puz.extras||[])])
  while(set.size<8) set.add(rndInt(1,15))
  return shuffle([...set])
}

/* --------- Arabic digits with isolation --------- */
const digitsMap = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩']
const LRI = '\u2066', PDI = '\u2069'
function formatDigit(value){
  const s = String(value)
  return (props.lang==='ar') ? (LRI + s.replace(/[0-9]/g, d=>digitsMap[+d]) + PDI) : s
}

/* --------- rule line --------- */
const ruleText = computed(() => {
  if(L.value==='ar'){
    return `ضع عددًا كليًا في كل مربع لتصبح المعادلة صحيحة:  ${formatDigit(target.value.num)}/${formatDigit(target.value.den)} =  ${formatDigit(1)}/□  −  □/${formatDigit(target.value.d2)}.`
  }
  return `Place integers to make the equation true:  ${target.value.num}/${target.value.den} =  1/□  −  □/${target.value.d2}.`
})

/* --------- game flow --------- */
function newPuzzle(){
  solved.value=false; toast.value=null; answer.value={A:null,N:null}
  const puz = pickNextPuzzle()
  currentPuzzle.value = puz
  target.value = { num:puz.target.num, den:puz.target.den, d2:puz.d2 }
  bank.value = buildBank(puz)
}
function onDragStart(ev,v){ ev.dataTransfer.setData('text/plain', String(v)) }
function allowDrop(ev){ ev.preventDefault() }
function dropTo(key, ev){
  ev.preventDefault()
  answer.value[key] = Number(ev.dataTransfer.getData('text/plain'))
  toast.value=null
}
function isFilled(){ return answer.value.A!=null && answer.value.N!=null }
function isCorrect(){
  if(!isFilled()) return false
  const lhs = (1/answer.value.A) - (answer.value.N/target.value.d2)
  const rhs = target.value.num/target.value.den
  return Math.abs(lhs-rhs) < 1e-9
}

async function addPoint(){
  try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{}
}
async function checkNow(){
  if(!isFilled()){ toast.value = L.value==='ar'?'أكمل الخانتين':'Fill both blanks'; sWrong&&sWrong.play(); return }
  if(isCorrect()){ solved.value=true; toast.value=T[L.value].correct; sOK&&sOK.play(); sClap&&sClap.play(); await addPoint() }
  else { toast.value=T[L.value].wrong; sWrong&&sWrong.play() }
}
function resetAll(){ answer.value={A:null,N:null}; toast.value=null; solved.value=false }

onMounted(newPuzzle)
</script>

<template>
  <div class="lvl2c5 challenge-surface" :data-theme="props.theme">
    <h2 class="title">{{ T[L].title }}</h2>
    <p class="rule">{{ ruleText }}</p>

    <!-- equation card -->
    <div class="equation" :dir="L==='ar' ? 'rtl' : 'ltr'">
      <!-- AR layout:  □/d2  −  1/□ -->
      <template v-if="L==='ar'">
        <div class="frac">
          <div class="top">
            <div class="drop" @dragover="allowDrop" @drop="dropTo('N',$event)">
              <span v-if="answer.N!=null" class="num">{{ formatDigit(answer.N) }}</span>
              <span v-else class="placeholder">□</span>
            </div>
          </div>
          <div class="bar"></div>
          <div class="bot">{{ formatDigit(target.d2) }}</div>
        </div>

        <span class="minus">−</span>

        <div class="frac">
          <div class="top">{{ formatDigit(1) }}</div>
          <div class="bar"></div>
          <div class="bot">
            <div class="drop" @dragover="allowDrop" @drop="dropTo('A',$event)">
              <span v-if="answer.A!=null" class="num">{{ formatDigit(answer.A) }}</span>
              <span v-else class="placeholder">□</span>
            </div>
          </div>
        </div>
      </template>

      <!-- EN layout:  1/□ − □/d2 -->
      <template v-else>
        <div class="frac">
          <div class="top">1</div>
          <div class="bar"></div>
          <div class="bot">
            <div class="drop" @dragover="allowDrop" @drop="dropTo('A',$event)">
              <span v-if="answer.A!=null" class="num">{{ formatDigit(answer.A) }}</span>
              <span v-else class="placeholder">□</span>
            </div>
          </div>
        </div>

        <span class="minus">−</span>

        <div class="frac">
          <div class="top">
            <div class="drop" @dragover="allowDrop" @drop="dropTo('N',$event)">
              <span v-if="answer.N!=null" class="num">{{ formatDigit(answer.N) }}</span>
              <span v-else class="placeholder">□</span>
            </div>
          </div>
          <div class="bar"></div>
          <div class="bot">{{ formatDigit(target.d2) }}</div>
        </div>
      </template>

      <!-- fixed left side -->
      <span class="eq">=</span>
      <div class="frac">
        <div class="top">{{ formatDigit(target.num) }}</div>
        <div class="bar"></div>
        <div class="bot">{{ formatDigit(target.den) }}</div>
      </div>
    </div>

    <!-- bank -->
    <div class="bank">
      <div class="bank-title">{{ T[L].bank }}</div>
      <div class="bank-items">
        <button
          v-for="v in bank" :key="v" class="chip"
          draggable="true" @dragstart="onDragStart($event,v)"
        >
          {{ formatDigit(v) }}
        </button>
      </div>
    </div>

    <div class="actions">
      <button class="btn" @click="resetAll"><RotateCcw class="ic" /> {{ T[L].reset }}</button>
      <button class="btn primary" @click="checkNow"><Check class="ic" /> {{ T[L].check }}</button>
      <button class="btn" @click="newPuzzle"><RefreshCw class="ic" /> {{ T[L].newQ }}</button>
    </div>

    <div v-if="toast" class="toast" :class="{ ok: solved }">{{ toast }}</div>
  </div>
</template>

<style scoped>
/* =========================
   Theme tokens (high contrast)
========================= */
.lvl2c5{
  --bg:#ffffff; --fg:#0b1220; --muted:#64748b;

  --panel:#ffffff; --panel-bd:#cbd5e1; --panel-shadow:0 10px 24px rgba(2,6,23,.08);

  --divider:#94a3b8;           /* fraction bar */
  --drop-bg:#eef2ff;           /* drop area fill */
  --drop-bd:#cbd5e1;

  --chip-bg:#ffffff; --chip-bd:#cbd5e1;

  --btn-bg:#ffffff; --btn-bd:#cbd5e1; --btn-fg:#0b1220;
  --btn-primary-bg:#0ea5e9; --btn-primary-fg:#ffffff;

  --toast-err-bg:#fee2e2; --toast-err-fg:#991b1b; --toast-err-bd:#fecaca;
  --toast-ok-bg:#dcfce7;  --toast-ok-fg:#166534;  --toast-ok-bd:#bbf7d0;
}

[data-theme="dark"] .lvl2c5{
  --bg:#0b1220; --fg:#e5e7eb; --muted:#9ca3af;

  --panel:#0f172a; --panel-bd:#334155; --panel-shadow:0 12px 28px rgba(0,0,0,.55);

  --divider:#94a3b8;            /* lighter line for contrast */
  --drop-bg:rgba(99,102,241,.18);
  --drop-bd:#475569;

  --chip-bg:#111827; --chip-bd:#475569;

  --btn-bg:#111827; --btn-bd:#475569; --btn-fg:#e5e7eb;
  --btn-primary-bg:#38bdf8; --btn-primary-fg:#0b1220;

  --toast-err-bg:rgba(248,113,113,.16); --toast-err-fg:#fecaca; --toast-err-bd:rgba(248,113,113,.45);
  --toast-ok-bg:rgba(34,197,94,.22);    --toast-ok-fg:#bbf7d0;  --toast-ok-bd:rgba(34,197,94,.5);
}

/* =========================
   Headings
========================= */
.title{ font-weight:800; margin:0 0 .35rem; color:var(--fg) }
.rule{ color:var(--muted); margin:0 0 1rem }

/* =========================
   Equation card
========================= */
.equation{
  display:flex; align-items:center; gap:1rem;
  background:var(--panel); color:var(--fg);
  border:1px solid var(--panel-bd);
  border-radius:16px; padding:1rem;
  box-shadow:var(--panel-shadow); width:max-content;
}
.eq,.minus{ font-size:1.35rem; font-weight:800 }
.frac{ display:grid; grid-template-rows:auto 4px auto; align-items:center; min-width:66px }
.frac .bar{ height:4px; background:var(--divider); border-radius:2px; margin:.15rem 0 }
.top,.bot{ display:flex; align-items:center; justify-content:center; font-variant-numeric:tabular-nums; font-weight:800; font-size:1.2rem }

/* drop zones */
.drop{
  min-width:46px; min-height:36px;
  border:1px dashed var(--drop-bd);
  border-radius:10px; background:var(--drop-bg);
  display:flex; align-items:center; justify-content:center;
  transition: box-shadow .15s, transform .1s;
}
.drop:focus-visible{ outline:none; box-shadow:0 0 0 3px rgba(56,189,248,.35) inset }
.placeholder{ color:var(--muted); font-size:1.1rem }
.num{ font-variant-numeric:tabular-nums; font-weight:800; font-size:1.1rem }

/* =========================
   Number bank
========================= */
.bank-title{ font-weight:700; color:var(--muted); margin:.85rem 0 .35rem }
.bank-items{ display:flex; flex-wrap:wrap; gap:.5rem }
.chip{
  border:1px solid var(--chip-bd); background:var(--chip-bg); color:var(--fg);
  padding:.48rem .66rem; border-radius:12px; cursor:grab;
  font-variant-numeric:tabular-nums; min-width:46px; text-align:center;
  transition: transform .08s, box-shadow .12s
}
.chip:hover{ transform:translateY(-1px); box-shadow:0 10px 22px rgba(0,0,0,.18) }

/* =========================
   Actions / toasts
========================= */
.actions{ display:flex; gap:.6rem; flex-wrap:wrap; margin-top:.6rem }
.btn{
  display:inline-flex; align-items:center; gap:.45rem;
  padding:.55rem .85rem; border-radius:.9rem;
  border:1px solid var(--btn-bd); background:var(--btn-bg); color:var(--btn-fg);
  cursor:pointer; transition: transform .1s, box-shadow .1s
}
.btn:hover{ transform:translateY(-1px); box-shadow:0 10px 22px rgba(0,0,0,.14) }
.btn.primary{ background:var(--btn-primary-bg); color:var(--btn-primary-fg); border-color:transparent }
.ic{ width:16px; height:16px }

.toast{
  margin-top:.7rem; padding:.6rem .9rem; border-radius:.9rem; text-align:center; font-weight:800;
  background:var(--toast-err-bg); color:var(--toast-err-fg); border:1px solid var(--toast-err-bd)
}
.toast.ok{ background:var(--toast-ok-bg); color:var(--toast-ok-fg); border-color:var(--toast-ok-bd) }

/* Ensure numerals are left-to-right inside fractions */
.top, .bot, .num { direction:ltr; unicode-bidi:isolate; }
</style>

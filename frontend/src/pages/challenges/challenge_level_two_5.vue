<script setup>
import { ref, computed, onMounted } from 'vue'
import { Check, RotateCcw, RefreshCw } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

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

/* ===== sounds (approved style) ===== */
import successUrl from '@/assets/sounds/success2.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong2.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

/* ===== utils ===== */
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]] } return x }

/* ===== state ===== */
const target = ref({num:1, den:6, d2:6})  // المعادلة الحالية
const bank = ref([])              // أرقام السحب
const answer = ref({ A:null, N:null })
const toast = ref(null)
const solved = ref(false)
const puzzleBank = [
  { id:'p1', target:{ num:1, den:6 }, d2:6,  solution:{ A:2, N:2 }, extras:[1,3,4,5,7,8] },
  { id:'p2', target:{ num:1, den:6 }, d2:9,  solution:{ A:2, N:3 }, extras:[1,4,5,6,7,8] },
  { id:'p3', target:{ num:1, den:6 }, d2:12, solution:{ A:2, N:4 }, extras:[1,3,5,6,7,9] },
  { id:'p4', target:{ num:1, den:6 }, d2:6,  solution:{ A:3, N:1 }, extras:[2,4,5,7,8,9] },
  { id:'p5', target:{ num:2, den:6 }, d2:6,  solution:{ A:2, N:1 }, extras:[3,4,5,7,8,9] },
  { id:'p6', target:{ num:1, den:8 }, d2:8,  solution:{ A:2, N:3 }, extras:[1,2,4,5,6,7] },
  { id:'p7', target:{ num:3, den:8 }, d2:8,  solution:{ A:2, N:1 }, extras:[2,4,5,6,7,9] },
  { id:'p8', target:{ num:1, den:9 }, d2:9,  solution:{ A:3, N:2 }, extras:[1,3,4,5,6,7] },
  { id:'p9', target:{ num:3, den:9 }, d2:6,  solution:{ A:2, N:1 }, extras:[2,4,5,7,8,9] },
  { id:'p10', target:{ num:1, den:10 }, d2:5, solution:{ A:2, N:2 }, extras:[1,3,4,6,7,8] },
  { id:'p11', target:{ num:2, den:10 }, d2:10, solution:{ A:2, N:3 }, extras:[1,4,5,6,7,9] },
  { id:'p12', target:{ num:1, den:12 }, d2:4, solution:{ A:3, N:1 }, extras:[2,5,6,7,8,9] }
]

const currentPuzzle = ref(puzzleBank[0])
const lastPuzzleId = ref(null)

function pickNextPuzzle(){
  if(puzzleBank.length === 1){
    lastPuzzleId.value = puzzleBank[0].id
    return puzzleBank[0]
  }
  let candidate
  do{
    candidate = puzzleBank[Math.floor(Math.random() * puzzleBank.length)]
  }while(candidate.id === lastPuzzleId.value)
  lastPuzzleId.value = candidate.id
  return candidate
}

function buildBank(puzzle){
  const options = new Set([puzzle.solution.A, puzzle.solution.N])
  const spreads = puzzle.extras || []
  spreads.forEach(v => options.add(v))
  while(options.size < 8){
    options.add(rndInt(1, 15))
  }
  return shuffle([...options])
}

const digitsMap = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩']

function formatDigit(value){
  const str = String(value)
  return props.lang==='ar' ? str.replace(/[0-9]/g, d => digitsMap[Number(d)]) : str
}

const ruleText = computed(() => {
  if(L.value === 'ar'){
    return `ضع عددًا كليًا في كل مربع لتصبح المعادلة صحيحة:  ${formatDigit(target.value.num)}/${formatDigit(target.value.den)} =  ١/□  −  □/${formatDigit(target.value.d2)}.`
  }
  return `Place integers to make the equation true:  ${target.value.num}/${target.value.den} =  1/□  −  □/${target.value.d2}.`
})

function newPuzzle(){
  solved.value = false
  toast.value = null
  answer.value = { A:null, N:null }

  const puzzle = pickNextPuzzle()
  currentPuzzle.value = puzzle
  target.value = { num:puzzle.target.num, den:puzzle.target.den, d2:puzzle.d2 }
  bank.value = buildBank(puzzle)
}

function onDragStart(ev, value){ ev.dataTransfer.setData('text/plain', String(value)) }
function allowDrop(ev){ ev.preventDefault() }
function dropTo(key, ev){
  ev.preventDefault()
  const v = Number(ev.dataTransfer.getData('text/plain'))
  answer.value[key] = v
  toast.value=null
}
function isFilled(){ return answer.value.A!=null && answer.value.N!=null }
function isCorrect(){
  if(!isFilled()) return false
  const AVal = answer.value.A
  const NVal = answer.value.N
  if(!AVal || !NVal) return false
  const lhs = (1 / AVal) - (NVal / target.value.d2)
  const rhs = target.value.num / target.value.den
  return Math.abs(lhs - rhs) < 1e-9
}

async function addPoint(){
  try{
    await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',
      {method:'GET',credentials:'include'})
  }catch{}
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

    <!-- المعادلة -->
    <div class="equation" dir="ltr">
      <div class="frac">
        <div class="top">{{ formatDigit(target.num) }}</div>
        <div class="bar"></div>
        <div class="bot">{{ formatDigit(target.den) }}</div>
      </div>
      <span class="eq">=</span>

      <div class="frac">
        <div class="top">1</div>
        <div class="bar"></div>
        <div class="bot">
          <div class="drop" @dragover="allowDrop" @drop="dropTo('A', $event)">
            <span v-if="answer.A!=null" class="num">{{ formatDigit(answer.A) }}</span>
            <span v-else class="placeholder">□</span>
          </div>
        </div>
      </div>

      <span class="minus">−</span>

      <div class="frac">
        <div class="top">
          <div class="drop" @dragover="allowDrop" @drop="dropTo('N', $event)">
            <span v-if="answer.N!=null" class="num">{{ formatDigit(answer.N) }}</span>
            <span v-else class="placeholder">□</span>
          </div>
        </div>
        <div class="bar"></div>
        <div class="bot">{{ formatDigit(target.d2) }}</div>
      </div>
    </div>

    <!-- البنك -->
    <div class="bank">
      <div class="bank-title">{{ T[L].bank }}</div>
      <div class="bank-items">
        <button v-for="v in bank" :key="v" class="chip" draggable="true" @dragstart="onDragStart($event, v)">
          {{ formatDigit(v) }}
        </button>
      </div>
    </div>

    <div class="actions">
      <button class="btn" @click="resetAll"><RotateCcw class="ic" /> {{ T[L].reset }}</button>
      <button class="btn" @click="checkNow"><Check class="ic" /> {{ T[L].check }}</button>
      <button class="btn" @click="newPuzzle"><RefreshCw class="ic" /> {{ T[L].newQ }}</button>
    </div>

    <div v-if="toast" class="toast" :class="{ ok: solved }">{{ toast }}</div>
  </div>
</template>

<style scoped>
.lvl2c5{ --bg:var(--c-bg,#fff); --fg:var(--c-fg,#111827); --muted:#6b7280 }
[data-theme="dark"] .lvl2c5{ --bg:#0b1220; --fg:#e5e7eb; --muted:#9ca3af }

.title{ font-weight:700; margin:0 0 .25rem }
.rule{ color:var(--muted); margin:0 0 1rem }

.equation{
  display:flex; align-items:center; gap:1rem;
  background:var(--bg); border-radius:1rem; padding:1rem;
  box-shadow:0 4px 14px rgba(0,0,0,.06); width:max-content
}
.eq,.minus{ font-size:1.4rem; font-weight:700 }
.frac{ display:grid; grid-template-rows:auto 4px auto; align-items:center; min-width:64px }
.frac .bar{ height:4px; background:#cbd5e1; border-radius:2px; margin:.15rem 0 }
.top,.bot{ display:flex; align-items:center; justify-content:center; font-variant-numeric:tabular-nums; font-weight:700; font-size:1.25rem }

.drop{
  min-width:46px; min-height:36px; border:1px dashed #cbd5e1; border-radius:.5rem;
  background:rgba(99,102,241,.06); display:flex; align-items:center; justify-content:center;
}
.placeholder{ color:#9ca3af; font-size:1.1rem }
.num{ font-variant-numeric:tabular-nums; font-weight:700; font-size:1.1rem }

.bank-title{ font-weight:600; color:var(--muted); margin:.75rem 0 .25rem }
.bank-items{ display:flex; flex-wrap:wrap; gap:.5rem }
.chip{
  border:1px solid #e5e7eb55; background:var(--bg); padding:.45rem .6rem; border-radius:.75rem;
  cursor:grab; font-variant-numeric:tabular-nums; min-width:46px; text-align:center
}

.actions{ display:flex; gap:.5rem; flex-wrap:wrap; margin-top:.5rem }
.btn{
  display:inline-flex; align-items:center; gap:.35rem; padding:.5rem .7rem;
  border-radius:.75rem; border:1px solid #e5e7eb55; background:var(--bg); cursor:pointer
}
.ic{ width:16px; height:16px }

.toast{ margin-top:.6rem; padding:.55rem .8rem; border-radius:.75rem; background:#fee2e2; color:#991b1b; border:1px solid #fecaca }
.toast.ok{ background:#dcfce7; color:#166534; border-color:#bbf7d0 }
</style>

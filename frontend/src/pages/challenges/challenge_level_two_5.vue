<script setup>
import { ref, computed, onMounted } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

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
const target = ref({num:3, den:10, d2:5})  // t/den = 1/A - N/d2
const A = ref(2)   // الحل الصحيح لمقام الكسر الأول
const N = ref(1)   // الحل الصحيح لبسط الكسر الثاني
const bank = ref([])              // أرقام السحب
const answer = ref({ A:null, N:null })
const toast = ref(null)
const solved = ref(false)

function gcd(a,b){ return b?gcd(b,a%b):Math.abs(a) }
function simplify(n,d){ const g=gcd(n,d); return [n/g, d/g] }

/* ابحث عشوائياً عن معادلة سليمة: t/10 مع حلول صحيحة */
function newPuzzle(){
  solved.value=false; toast.value=null; answer.value={A:null,N:null}

  let found=false
  for(let tries=0; tries<200 && !found; tries++){
    const den = 10               // نبقي المقام 10 كالورقة، ويمكن تغييره لاحقاً بسهولة
    const num = rndInt(1,9)      // 1..9
    const d2cand = shuffle([4,5,6,8,9,10])[0]  // مقام الكسر الثاني
    // جرّب قيم A من 2..12 ثم احسب N
    for(let a=2;a<=12 && !found;a++){
      const value = 1/a - num/den
      if(value <= 0) continue
      const n = Math.round(d2cand * value)
      if(Math.abs(d2cand*value - n) < 1e-9 && n>=1 && n<d2cand){
        // تحقق من الصحة النهائية
        const left = 1/a - n/d2cand
        if(Math.abs(left - num/den) < 1e-9){
          target.value = {num, den, d2:d2cand}
          A.value=a; N.value=n
          found=true
        }
      }
    }
  }

  // بنك الأرقام: الإجابتان + مشتتات قريبة
  const choices = new Set([A.value, N.value])
  while(choices.size<8){
    const v = rndInt(1,12)
    choices.add(v)
  }
  bank.value = shuffle([...choices])
}

function onDragStart(ev, value){ ev.dataTransfer.setData('text/plain', String(value)) }
function allowDrop(ev){ ev.preventDefault() }
function dropTo(key, ev){
  ev.preventDefault()
  const v = Number(ev.dataTransfer.getData('text/plain'))
  answer.value[key] = v
  toast.value=null
}
function clearCell(key){ answer.value[key]=null }

function isFilled(){ return answer.value.A!=null && answer.value.N!=null }
function isCorrect(){
  if(!isFilled()) return false
  const lhs = 1/answer.value.A - answer.value.N/target.value.d2
  const rhs = target.value.num/target.value.den
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
  <div class="lvl2c5" :data-theme="props.theme">
    <h2 class="title">{{ T[L].title }}</h2>
    <p class="rule">{{ T[L].rule(target) }}</p>

    <!-- المعادلة -->
    <div class="equation" dir="ltr">
      <div class="frac">
        <div class="top">{{ target.num }}</div>
        <div class="bar"></div>
        <div class="bot">{{ target.den }}</div>
      </div>
      <span class="eq">=</span>

      <div class="frac">
        <div class="top">1</div>
        <div class="bar"></div>
        <div class="bot">
          <div class="drop" @dragover="allowDrop" @drop="dropTo('A', $event)">
            <span v-if="answer.A!=null" class="num">{{ answer.A }}</span>
            <span v-else class="placeholder">□</span>
          </div>
        </div>
      </div>

      <span class="minus">−</span>

      <div class="frac">
        <div class="top">
          <div class="drop" @dragover="allowDrop" @drop="dropTo('N', $event)">
            <span v-if="answer.N!=null" class="num">{{ answer.N }}</span>
            <span v-else class="placeholder">□</span>
          </div>
        </div>
        <div class="bar"></div>
        <div class="bot">{{ target.d2 }}</div>
      </div>
    </div>

    <!-- البنك -->
    <div class="bank">
      <div class="bank-title">{{ T[L].bank }}</div>
      <div class="bank-items">
        <button v-for="v in bank" :key="v" class="chip" draggable="true" @dragstart="onDragStart($event, v)">
          {{ v }}
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

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

const T = {
  ar:{
    title:'المستوى الثاني – التحدي 3: أوصل المسألة بالنتيجة الصحيحة',
    rule:'اسحب عدداً من ستة أرقام إلى كل خانة بحسب الخاصية المطلوبة: مضاعف 2، 3، 4، 5. كل عدد يُستخدم مرة واحدة.',
    bank:'لوحة الأعداد', newQ:'سؤال جديد', reset:'إعادة تعيين', check:'تحقّق',
    correct:'إجابة صحيحة', wrong:'تحقق من الخواص', clear:'تفريغ الخلية',
    lab2:'مضاعفًا للعدد 2', lab3:'مضاعفًا للعدد 3', lab4:'مضاعفًا للعدد 4', lab5:'مضاعفًا للعدد 5'
  },
  en:{
    title:'Level 2 – Challenge 3: Match each rule to a six-digit number',
    rule:'Drag one six-digit number to each rule: multiple of 2, 3, 4, 5. Each number can be used once.',
    bank:'Number bank', newQ:'New puzzle', reset:'Reset', check:'Check',
    correct:'Correct', wrong:'Check the properties', clear:'Clear cell',
    lab2:'Multiple of 2', lab3:'Multiple of 3', lab4:'Multiple of 4', lab5:'Multiple of 5'
  }
}
const L = computed(()=> (T[props.lang]?props.lang:'ar'))

/* sounds (approved style) */
import successUrl from '@/assets/sounds/success3.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong2.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

/* utils */
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]]} return x }

/* state */
const bank = ref([])                // numbers to drag
const bankCounts = ref({})          // number -> remaining count (always 1 here)
const answer = ref({ m2:null, m3:null, m4:null, m5:null })
const toast = ref(null)
const solved = ref(false)

/* helpers: properties */
const isMul2 = n => n%2===0
const isMul3 = n => (String(n).split('').reduce((s,d)=>s+ +d,0))%3===0
const isMul4 = n => n%100 % 4===0
const isMul5 = n => n%10===0 || n%10===5

/* random six-digit generators with constraints */
function rand6(predicate=(n)=>true){
  // ensure six digits (no leading zero)
  while(true){
    const first = rndInt(1,9)
    let s = String(first)
    for(let i=0;i<5;i++) s += String(rndInt(0,9))
    const n = Number(s)
    if(predicate(n)) return n
  }
}
function rand6_last(d, extra=()=>true){
  // generate with last digit d and extra predicate
  while(true){
    const first = rndInt(1,9)
    let s = String(first)
    for(let i=0;i<4;i++) s += String(rndInt(0,9))
    s += String(d)
    const n = Number(s)
    if(extra(n)) return n
  }
}

/* build puzzle: guarantee at least one valid for each slot */
function newPuzzle(){
  solved.value=false; toast.value=null
  answer.value = { m2:null, m3:null, m4:null, m5:null }

  const picked = new Set()
  const addUnique = (n)=>{
    const k=String(n); if(picked.has(k)) return false; picked.add(k); return true
  }

  // One clear candidate for each property
  // m5: end with 5 (not even)
  let a5 = rand6_last(5, n=>!isMul3(n) || rndInt(0,1)) // sometimes also mult3
  while(!addUnique(a5)) a5 = rand6_last(5)
  // m2: even but not *4 (to reduce ambiguity)
  let a2 = rand6_last([0,2,4,6,8][rndInt(0,4)], n=>!isMul5(n) && !isMul4(n))
  while(!addUnique(a2)) a2 = rand6_last([0,2,4,6,8][rndInt(0,4)], n=>!isMul5(n) && !isMul4(n))
  // m4: divisible by 4 (this is even by nature)
  let a4 = rand6(n=>isMul4(n))
  while(!addUnique(a4)) a4 = rand6(n=>isMul4(n))
  // m3: sum of digits divisible by 3, avoid ending 0/5 to reduce overlap
  let a3 = rand6(n=>isMul3(n) && !isMul5(n))
  while(!addUnique(a3)) a3 = rand6(n=>isMul3(n) && !isMul5(n))

  const core = [a2,a3,a4,a5]

  // add distractors that satisfy none of the four props
  const distract = []
  while(distract.length<4){
    let d = rand6(n=> (n%2!==0) && !isMul3(n) && !isMul5(n) && !isMul4(n))
    if(addUnique(d)) distract.push(d)
  }

  bank.value = shuffle(core.concat(distract))
  bankCounts.value = Object.fromEntries(bank.value.map(v=>[v,1]))
}

function onDragStart(ev, value){ ev.dataTransfer.setData('text/plain', String(value)) }
function allowDrop(ev){ ev.preventDefault() }
function dropTo(key, ev){
  ev.preventDefault()
  const v = Number(ev.dataTransfer.getData('text/plain'))
  if((bankCounts.value[v]||0)===0) return
  // return previous value to bank
  if(answer.value[key]!=null){
    bankCounts.value[answer.value[key]] = (bankCounts.value[answer.value[key]]||0)+1
  }
  answer.value[key] = v
  bankCounts.value[v]-=1
  toast.value=null
}
function clearCell(key){
  if(answer.value[key]!=null){
    bankCounts.value[answer.value[key]] = (bankCounts.value[answer.value[key]]||0)+1
    answer.value[key]=null
  }
}

function isFilled(){ return ['m2','m3','m4','m5'].every(k=>answer.value[k]!=null) }
function isCorrect(){
  return  isMul2(answer.value.m2) &&
          isMul3(answer.value.m3) &&
          isMul4(answer.value.m4) &&
          isMul5(answer.value.m5)
}

async function addPoint(){
  try{
    await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',
      {method:'GET',credentials:'include'})
  }catch{}
}
async function checkNow(){
  if(!isFilled()){ toast.value=L.value==='ar'?'أكمل كل الخانات':'Fill all blanks'; sWrong&&sWrong.play(); return }
  if(isCorrect()){
    solved.value=true; toast.value=T[L.value].correct; sOK&&sOK.play(); sClap&&sClap.play(); await addPoint()
  }else{ toast.value=T[L.value].wrong; sWrong&&sWrong.play() }
}
function resetAll(){
  answer.value = { m2:null, m3:null, m4:null, m5:null }
  // restore counts
  bankCounts.value = Object.fromEntries(bank.value.map(v=>[v,1]))
  toast.value=null; solved.value=false
}

onMounted(newPuzzle)
watch(()=>props.lang,()=>{})
</script>

<template>
  <div class="lvl2c3 challenge-surface" :data-theme="props.theme">
    <h2 class="title">{{ T[L].title }}</h2>
    <p class="rule">{{ T[L].rule }}</p>

    <div class="cards">
      <div class="card">
        <div class="label">{{ T[L].lab2 }}</div>
        <div class="drop"
             @dragover="allowDrop" @drop="dropTo('m2', $event)">
          <span v-if="answer.m2!=null" class="num">{{ answer.m2 }}</span>
          <span v-else class="placeholder">؟</span>
        </div>
        <button class="clear" @click="clearCell('m2')"><Eraser class="ic"/>{{ T[L].clear }}</button>
      </div>

      <div class="card">
        <div class="label">{{ T[L].lab3 }}</div>
        <div class="drop"
             @dragover="allowDrop" @drop="dropTo('m3', $event)">
          <span v-if="answer.m3!=null" class="num">{{ answer.m3 }}</span>
          <span v-else class="placeholder">؟</span>
        </div>
        <button class="clear" @click="clearCell('m3')"><Eraser class="ic"/>{{ T[L].clear }}</button>
      </div>

      <div class="card">
        <div class="label">{{ T[L].lab4 }}</div>
        <div class="drop"
             @dragover="allowDrop" @drop="dropTo('m4', $event)">
          <span v-if="answer.m4!=null" class="num">{{ answer.m4 }}</span>
          <span v-else class="placeholder">؟</span>
        </div>
        <button class="clear" @click="clearCell('m4')"><Eraser class="ic"/>{{ T[L].clear }}</button>
      </div>

      <div class="card">
        <div class="label">{{ T[L].lab5 }}</div>
        <div class="drop"
             @dragover="allowDrop" @drop="dropTo('m5', $event)">
          <span v-if="answer.m5!=null" class="num">{{ answer.m5 }}</span>
          <span v-else class="placeholder">؟</span>
        </div>
        <button class="clear" @click="clearCell('m5')"><Eraser class="ic"/>{{ T[L].clear }}</button>
      </div>
    </div>

    <div class="bank">
      <div class="bank-title">{{ T[L].bank }}</div>
      <div class="bank-items">
        <button v-for="v in bank"
                :key="v"
                class="chip"
                :disabled="(bankCounts[v]||0)===0"
                draggable="true"
                @dragstart="onDragStart($event, v)">
          {{ v }}
          <small v-if="(bankCounts[v]||0)===0">✓</small>
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
.lvl2c3{ --bg:var(--c-bg,#fff); --fg:var(--c-fg,#111827); --muted:#6b7280 }
[data-theme="dark"] .lvl2c3{ --bg:#0b1220; --fg:#e5e7eb; --muted:#9ca3af }
.title{ font-weight:700; margin:0 0 .25rem }
.rule{ color:var(--muted); margin:0 0 1rem }

.cards{ display:grid; grid-template-columns: repeat(2, minmax(260px,1fr)); gap:1rem; margin-bottom:.75rem }
.card{ background:var(--bg); border:1px solid #e5e7eb55; border-radius:1rem; padding:.75rem }
.label{ color:var(--muted); margin-bottom:.35rem }
.drop{
  height:74px; border:1px dashed #cbd5e1; border-radius:.75rem; background:rgba(99,102,241,.06);
  display:flex; align-items:center; justify-content:center;
}
.num{ font-variant-numeric:tabular-nums; font-weight:700; font-size:1.25rem }
.placeholder{ color:var(--muted); font-size:1.25rem }
.clear{ margin-top:.35rem; font-size:.8rem; border:none; background:transparent; color:var(--muted); display:flex; align-items:center; gap:.25rem; cursor:pointer }
.ic{ width:16px; height:16px }

.bank-title{ font-weight:600; color:var(--muted); margin:.25rem 0 }
.bank-items{ display:flex; flex-wrap:wrap; gap:.5rem }
.chip{
  border:1px solid #e5e7eb55; background:var(--bg); padding:.45rem .6rem; border-radius:.75rem; cursor:grab;
  font-variant-numeric:tabular-nums; min-width:108px; display:flex; justify-content:space-between; align-items:center;
}
.chip[disabled]{ opacity:.55; cursor:not-allowed }

.actions{ display:flex; gap:.5rem; flex-wrap:wrap; margin-top:.5rem }
.btn{ display:inline-flex; align-items:center; gap:.35rem; padding:.5rem .7rem; border-radius:.75rem; border:1px solid #e5e7eb55; background:var(--bg); cursor:pointer }

.toast{ margin-top:.6rem; padding:.55rem .8rem; border-radius:.75rem; background:#fee2e2; color:#991b1b; border:1px solid #fecaca }
.toast.ok{ background:#dcfce7; color:#166534; border-color:#bbf7d0 }
</style>

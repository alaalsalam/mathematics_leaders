<!-- <script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

const T = {
  ar:{ title:'التحدي 2: شبكة أعداد تزيد بمقدار {STEP}',
       rule:'كل خانة تزيد {STEP} عن اليسار وعن الأعلى. اسحب الأعداد المفقودة إلى أماكنها.',
       newQ:'سؤال جديد', check:'تحقّق', reset:'إعادة تعيين', correct:'إجابة صحيحة',
       wrong:'تحقق من القيم', bank:'لوحة الأعداد', clear:'تفريغ الخلية' },
  en:{ title:'Challenge 2: Number grid with step {STEP}',
       rule:'Each cell increases by {STEP} from its left and its top. Drag the missing numbers into place.',
       newQ:'New puzzle', check:'Check', reset:'Reset', correct:'Correct answer',
       wrong:'Check your values', bank:'Number bank', clear:'Clear cell' }
}
const L = computed(()=> (T[props.lang]?props.lang:'ar'))

// أصوات
// const sOK = typeof Audio!=='undefined'?new Audio('/sounds/success.mp3'):null
// const sClap = typeof Audio!=='undefined'?new Audio('/sounds/clap.mp3'):null
// const sWrong = typeof Audio!=='undefined'?new Audio('/sounds/wrong.mp3'):null

/* ===== sounds ===== */
import successUrl from '@/assets/sounds/success2.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong2.mp3'

const sOK   = typeof Audio !== 'undefined' ? new Audio(successUrl) : null
const sClap = typeof Audio !== 'undefined' ? new Audio(clapUrl)    : null
const sWrong= typeof Audio !== 'undefined' ? new Audio(wrongUrl)   : null

sOK && (sOK.preload = 'auto')
sClap && (sClap.preload = 'auto')
sWrong && (sWrong.preload = 'auto')


// عشوائي
const stepsPool = [100,200,500,1000,2000]        // يمكنك تعديل القائمة
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]]} return x }

// حالة
const size = ref(3)
const step = ref(1000)          // متغير وعشوائي لكل لغز
const base = ref(0)
const grid = ref([])            // القيم الصحيحة
const blanks = ref(new Set())   // "r,c"
const answerMap = ref({})       // "r,c" -> value
const manualDrafts = ref({})    // "r,c" -> string for manual input
const bankCounts = ref({})      // value -> remaining count
const solved = ref(false)
const toast = ref(null)

// عناوين ديناميكية تظهر الـ step الحالي
const titleText = computed(()=> T[L.value].title.replaceAll('{STEP}', step.value))
const ruleText  = computed(()=> T[L.value].rule.replaceAll('{STEP}', step.value))

const keyOf = (r,c)=>`${r},${c}`

function buildGrid(n, start, stp){
  const g=[]
  for(let r=0;r<n;r++){ const row=[]
    for(let c=0;c<n;c++){ row.push(start + stp*(r+c)) }
    g.push(row)
  } return g
}

function pickBlanks(n){
  const all=[]
  for(let r=0;r<n;r++) for(let c=0;c<n;c++) all.push([r,c])
  const filtered = all.filter(([r,c])=>!(r===0&&c===0))
  const k=rndInt(3,5)
  return new Set(shuffle(filtered).slice(0,k).map(([r,c])=>keyOf(r,c)))
}

function buildBankCounts(){
  const counts={}
  blanks.value.forEach(k=>{
    const [r,c]=k.split(',').map(Number)
    const v=grid.value[r][c]
    counts[v]=(counts[v]||0)+1
  })
  bankCounts.value=counts
}

// مصفوفة عرض للبنك وفق الكميّات الحالية
const bankList = computed(()=>{
  const out=[]
  for(const [v,ct] of Object.entries(bankCounts.value)){
    for(let i=0;i<ct;i++) out.push(Number(v))
  }
  return shuffle(out)
})

function newPuzzle(){
  solved.value=false; toast.value=null; answerMap.value={}; manualDrafts.value={}
  // اختيار step وقاعدة
  step.value = stepsPool[rndInt(0, stepsPool.length-1)]
  // اختيار base
  const thousands = rndInt(5, 19) * 100     // قاعدة لطيفة لأرقام 3–5 خانات
  base.value = thousands
  const n=size.value
  grid.value=buildGrid(n, base.value, step.value)
  blanks.value=pickBlanks(n)
  buildBankCounts()
}

function isFilled(){
  for(const k of blanks.value){ if(answerMap.value[k]==null) return false }
  return true
}
function isCorrect(){
  if(!isFilled()) return false
  for(const k of blanks.value){
    const [r,c]=k.split(',').map(Number)
    if(answerMap.value[k]!==grid.value[r][c]) return false
  }
  return true
}

async function addPoint(){
  try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{}
}
async function checkNow(){
  if(!isFilled()){ toast.value=L.value==='ar'?'أكمل كل الخانات':'Fill all blanks'; sWrong&&sWrong.play(); return }
  if(isCorrect()){ solved.value=true; toast.value=T[L.value].correct; sOK&&sOK.play(); sClap&&sClap.play(); await addPoint() }
  else { toast.value=T[L.value].wrong; sWrong&&sWrong.play() }
}

function resetAnswers(){
  answerMap.value={}
  manualDrafts.value={}
  buildBankCounts()
  toast.value=null; solved.value=false
}

// سحب وإفلات بكميّات
function setAnswer(key, value, { fromManual = false } = {}){
  if(Number.isNaN(value)) return
  if(answerMap.value[key]!=null){
    const old=answerMap.value[key]
    bankCounts.value[old]=(bankCounts.value[old]||0)+1
  }
  if(fromManual){
    if((bankCounts.value[value]||0)>0){
      bankCounts.value[value]-=1
    }
  } else {
    if((bankCounts.value[value]||0)===0){
      return
    }
    bankCounts.value[value]-=1
  }
  answerMap.value[key]=value
  manualDrafts.value = { ...manualDrafts.value, [key]: String(value) }
  toast.value=null
}

function onDragStart(ev,value){ ev.dataTransfer.setData('text/plain', String(value)) }
function allowDrop(ev){ ev.preventDefault() }
function onDrop(ev,key){
  ev.preventDefault()
  const v=Number(ev.dataTransfer.getData('text/plain'))
  setAnswer(key, v)
}
function clearCell(key){
  if(answerMap.value[key]!=null){
    const old=answerMap.value[key]
    bankCounts.value[old]=(bankCounts.value[old]||0)+1
    delete answerMap.value[key]
  }
  manualDrafts.value = { ...manualDrafts.value, [key]: '' }
}

function onManualInput(key, value){
  manualDrafts.value = { ...manualDrafts.value, [key]: value }
}

function commitManual(key){
  const raw = (manualDrafts.value[key] ?? '').trim()
  if(raw === ''){
    clearCell(key)
    return
  }
  const num = Number(raw)
  if(!Number.isFinite(num)) return
  setAnswer(key, num, { fromManual: true })
}

const numDir = computed(()=>({direction:'ltr', unicodeBidi:'isolate'}))
onMounted(newPuzzle)
watch(()=>props.lang,()=>toast.value=null)
</script>

<template>
  <div class="challenge2 challenge-surface" :data-theme="props.theme">
    <h2 class="title">{{ titleText }}</h2>
    <p class="rule">{{ ruleText }}</p>

    <div class="layout">
      <div class="grid">
        <div v-for="r in size" :key="'r'+r" class="row">
          <div v-for="c in size" :key="'c'+r+'-'+c" class="cell">
            <template v-if="!blanks.has(`${r-1},${c-1}`)">
              <span class="num" :style="numDir">{{ grid[r-1][c-1] }}</span>
            </template>
            <template v-else>
              <div class="dropzone" @dragover="allowDrop" @drop="onDrop($event, `${r-1},${c-1}`)">
                <span v-if="answerMap[`${r-1},${c-1}`]!=null" class="num" :style="numDir">
                  {{ answerMap[`${r-1},${c-1}`] }}
                </span>
                <span v-else class="placeholder">؟</span>
              </div>
              <input
                class="manual-entry"
                type="number"
                :value="manualDrafts[`${r-1},${c-1}`] ?? ''"
                @input="onManualInput(`${r-1},${c-1}`, $event.target.value)"
                @change="commitManual(`${r-1},${c-1}`)"
                @blur="commitManual(`${r-1},${c-1}`)"
                :placeholder="props.lang==='ar' ? 'أدخل رقمًا' : 'Enter value'"
              />
              <button class="clear" @click="clearCell(`${r-1},${c-1}`)"><Eraser class="ic" /> {{ T[L].clear }}</button>
            </template>
          </div>
        </div>
      </div>

      <div class="bank">
        <div class="bank-title">{{ T[L].bank }}</div>
        <div class="bank-items">
          <button v-for="v in bankList" :key="v + '_' + Math.random()" class="chip"
                  draggable="true" @dragstart="onDragStart($event, v)" :style="numDir">
            {{ v }}
          </button>
        </div>

        <div class="actions">
          <button class="btn" @click="resetAnswers"><RotateCcw class="ic" /> {{ T[L].reset }}</button>
          <button class="btn" @click="checkNow"><Check class="ic" /> {{ T[L].check }}</button>
          <button class="btn" @click="newPuzzle"><RefreshCw class="ic" /> {{ T[L].newQ }}</button>
        </div>

        <div v-if="toast" class="toast" :class="{ ok: solved }">{{ toast }}</div>
      </div>
    </div>

    <div v-if="solved" class="overlay">
      <div class="card">
        <div class="big">{{ T[L].correct }}</div>
        <button class="btn" @click="newPuzzle">{{ T[L].newQ }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* نفس أنماطك تقريباً، مع زر تفريغ */
.challenge2{ --bg:var(--c-bg,#fff); --fg:var(--c-fg,#111827); --muted:#6b7280 }
[data-theme="dark"] .challenge2{ --bg:#0b1220; --fg:#e5e7eb; --muted:#9ca3af }
.title{ font-weight:700; margin:0 0 .25rem } .rule{ color:var(--muted); margin:0 0 1rem }
.layout{ display:grid; grid-template-columns:1fr 260px; gap:1rem }
.grid{ background:var(--bg); border:1px solid #e5e7eb22; border-radius:1rem; padding:1rem; box-shadow:0 4px 14px rgba(0,0,0,.06) }
.row{ display:grid; grid-template-columns:repeat(3,1fr) }
.cell{ border:1px dashed #cbd5e1; min-height:86px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:.25rem; padding:.25rem }
.num{ font-variant-numeric:tabular-nums; font-weight:700; font-size:1.25rem }
.placeholder{ color:var(--muted); font-size:1.25rem }
.dropzone{ width:100%; flex:1; display:flex; align-items:center; justify-content:center; background:rgba(99,102,241,.06); border-radius:.5rem }
.manual-entry{ width:100%; padding:.45rem .6rem; border-radius:.6rem; border:1px solid rgba(99,102,241,.2); background:rgba(255,255,255,.92); font-size:.95rem; direction:ltr; color:var(--fg); }
.manual-entry:focus{ outline:none; border-color:rgba(15,138,62,.45); box-shadow:0 0 0 3px rgba(15,138,62,.16); }
[data-theme="dark"] .manual-entry{ background:rgba(15,23,42,.8); border-color:rgba(148,163,184,.25); color:var(--fg); }
.clear{ font-size:.75rem; border:none; background:transparent; color:var(--muted); display:flex; align-items:center; gap:.25rem; cursor:pointer }
.bank{ display:flex; flex-direction:column; gap:.75rem }
.bank-title{ font-weight:600; color:var(--muted) }
.bank-items{ display:flex; flex-wrap:wrap; gap:.5rem }
.chip{ border:1px solid #e5e7eb55; background:var(--bg); padding:.4rem .6rem; border-radius:.75rem; cursor:grab; font-variant-numeric:tabular-nums }
.actions{ display:flex; gap:.5rem; flex-wrap:wrap; margin-top:.25rem }
.btn{ display:inline-flex; align-items:center; gap:.35rem; padding:.5rem .7rem; border-radius:.75rem; border:1px solid #e5e7eb55; background:var(--bg); cursor:pointer }
.ic{ width:16px; height:16px }
.toast{ margin-top:.5rem; padding:.5rem .75rem; border-radius:.75rem; background:#fee2e2; color:#991b1b; border:1px solid #fecaca }
.toast.ok{ background:#dcfce7; color:#166534; border-color:#bbf7d0 }
.overlay{ position:fixed; inset:0; background:rgba(0,0,0,.35); display:flex; align-items:center; justify-content:center }
.card{ background:var(--bg); color:var(--fg); padding:1rem 1.25rem; border-radius:1rem; box-shadow:0 10px 30px rgba(0,0,0,.25); display:flex; flex-direction:column; gap:.75rem; align-items:center }
.big{ font-size:1.25rem; font-weight:700 }
</style> -->
<script setup>
/* ------------ Imports ------------ */
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

/* ------------ Props ------------ */
const props = defineProps({
  lang:  { type: String, default: 'ar' },
  theme: { type: String, default: 'light' } // 'light' | 'dark'
})

/* ------------ Copy ------------ */
const T = {
  ar: {
    title: 'التحدي 2: شبكة أعداد تزيد بمقدار {STEP}',
    rule:  'كل خانة تزيد {STEP} عن اليسار وعن الأعلى. اسحب الأعداد المفقودة إلى أماكنها.',
    newQ:  'سؤال جديد', check: 'تحقّق', reset: 'إعادة تعيين',
    correct: 'إجابة صحيحة', wrong: 'تحقق من القيم',
    bank: 'لوحة الأعداد', clear: 'تفريغ الخلية'
  },
  en: {
    title: 'Challenge 2: Number grid with step {STEP}',
    rule:  'Each cell increases by {STEP} from its left and from the top. Drag the missing numbers into place.',
    newQ:  'New puzzle', check: 'Check', reset: 'Reset',
    correct: 'Correct answer', wrong: 'Check your values',
    bank: 'Number bank', clear: 'Clear cell'
  }
}
const L = computed(() => (T[props.lang] ? props.lang : 'ar'))

/* ------------ Sounds (kept lightweight) ------------ */
import successUrl from '@/assets/sounds/success2.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong2.mp3'
const sOK    = typeof Audio !== 'undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio !== 'undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio !== 'undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

/* ------------ Helpers ------------ */
// Return random int in [a,b]
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
// Fisher–Yates
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]]} return x }

/* ------------ State ------------ */
const size  = ref(3)                     // grid is size x size
const step  = ref(1000)                  // arithmetic step
const base  = ref(0)                     // top-left value
const grid  = ref([])                    // correct values matrix
const blanks = ref(new Set())            // set of "r,c" positions made blank

// answerMap keeps user answers; manualDrafts mirrors input fields
const answerMap = ref({})
const manualDrafts = ref({})

// bankCounts maps number -> remaining copies in the bank
const bankCounts = ref({})
const solved = ref(false)
const toast  = ref(null)

// dynamic title/rule with live step
const titleText = computed(() => T[L.value].title.replaceAll('{STEP}', step.value))
const ruleText  = computed(() => T[L.value].rule.replaceAll('{STEP}', step.value))

/* ------------ Grid generation ------------ */
// Build arithmetic grid: value = base + step*(row+col)
function buildGrid(n, start, stp){
  const g=[]
  for(let r=0;r<n;r++){
    const row=[]
    for(let c=0;c<n;c++) row.push(start + stp*(r+c))
    g.push(row)
  }
  return g
}

// Pick K blank cells (not including [0,0]) where K∈[3..5]
function pickBlanks(n){
  const cells=[]
  for(let r=0;r<n;r++) for(let c=0;c<n;c++) if(!(r===0&&c===0)) cells.push([r,c])
  const K=rndInt(3,5)
  return new Set(shuffle(cells).slice(0,K).map(([r,c])=>`${r},${c}`))
}

// Build bank according to the correct values at blank positions
function buildBankCounts(){
  const counts={}
  blanks.value.forEach(k=>{
    const [r,c]=k.split(',').map(Number)
    const v=grid.value[r][c]
    counts[v]=(counts[v]||0)+1
  })
  bankCounts.value=counts
}

/* ------------ New puzzle ------------ */
const stepsPool = [100,200,500,1000,2000]
function newPuzzle(){
  solved.value=false
  toast.value=null
  answerMap.value={}
  manualDrafts.value={}

  // choose step and base; base aligned to hundreds for neat numbers
  step.value = stepsPool[rndInt(0, stepsPool.length-1)]
  base.value = rndInt(5, 19) * 100

  const n=size.value
  grid.value = buildGrid(n, base.value, step.value)
  blanks.value = pickBlanks(n)
  buildBankCounts()
}

/* ------------ Bank list (expanded per remaining count) ------------ */
const bankList = computed(()=>{
  const out=[]
  for(const [v,ct] of Object.entries(bankCounts.value)){
    for(let i=0;i<ct;i++) out.push(Number(v))
  }
  return shuffle(out)
})

/* ------------ DnD + manual entry ------------ */
const keyOf = (r,c)=>`${r},${c}`

function setAnswer(key, value, { fromManual=false } = {}){
  if(Number.isNaN(value)) return
  // return previous to bank if replacing
  if(answerMap.value[key]!=null){
    const prev=answerMap.value[key]
    bankCounts.value[prev]=(bankCounts.value[prev]||0)+1
  }
  // bank decremented whether drag or manual (manual still limited by counts)
  if((bankCounts.value[value]||0) <= 0) return
  bankCounts.value[value]-=1

  answerMap.value[key]=value
  manualDrafts.value = { ...manualDrafts.value, [key]: String(value) }
  toast.value=null; solved.value=false
}

function onDragStart(ev, value){ ev.dataTransfer.setData('text/plain', String(value)) }
function allowDrop(ev){ ev.preventDefault() }
function onDrop(ev, key){
  ev.preventDefault()
  const v=Number(ev.dataTransfer.getData('text/plain'))
  setAnswer(key, v)
}

function clearCell(key){
  if(answerMap.value[key]!=null){
    const prev=answerMap.value[key]
    bankCounts.value[prev]=(bankCounts.value[prev]||0)+1
    delete answerMap.value[key]
  }
  manualDrafts.value = { ...manualDrafts.value, [key]: '' }
  toast.value=null; solved.value=false
}

function onManualInput(key, value){
  manualDrafts.value = { ...manualDrafts.value, [key]: value }
}
function commitManual(key){
  const raw = (manualDrafts.value[key] ?? '').trim()
  if(raw===''){ clearCell(key); return }
  const num = Number(raw)
  if(!Number.isFinite(num)) return
  setAnswer(key, num, { fromManual:true })
}

/* ------------ Validation ------------ */
function isFilled(){
  for(const k of blanks.value) if(answerMap.value[k]==null) return false
  return true
}
function isCorrect(){
  if(!isFilled()) return false
  for(const k of blanks.value){
    const [r,c]=k.split(',').map(Number)
    if(answerMap.value[k] !== grid.value[r][c]) return false
  }
  return true
}

async function addPoint(){
  try{
    await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',
      { method:'GET', credentials:'include' })
  }catch{}
}

async function checkNow(){
  if(!isFilled()){ toast.value = L.value==='ar' ? 'أكمل كل الخانات' : 'Fill all blanks'; sWrong&&sWrong.play(); return }
  if(isCorrect()){ solved.value=true; toast.value=T[L.value].correct; sOK&&sOK.play(); sClap&&sClap.play(); await addPoint() }
  else { toast.value=T[L.value].wrong; sWrong&&sWrong.play() }
}

function resetAnswers(){
  answerMap.value={}
  manualDrafts.value={}
  buildBankCounts()
  toast.value=null; solved.value=false
}

/* ------------ Number direction isolation (for RTL) ------------ */
const numDir = computed(()=>({ direction:'ltr', unicodeBidi:'isolate' }))

/* ------------ Lifecycle ------------ */
onMounted(newPuzzle)
watch(() => props.lang, () => { if(!solved.value) toast.value=null })
</script>

<template>
  <div class="challenge2 challenge-surface" :data-theme="props.theme">
    <h2 class="title">{{ titleText }}</h2>
    <p class="rule">{{ ruleText }}</p>

    <div class="layout">
      <!-- Grid -->
      <div class="grid">
        <div v-for="r in size" :key="'r'+r" class="row">
          <div v-for="c in size" :key="'c'+r+'-'+c" class="cell">
            <template v-if="!blanks.has(`${r-1},${c-1}`)">
              <span class="num" :style="numDir">{{ grid[r-1][c-1] }}</span>
            </template>
            <template v-else>
              <div class="dropzone"
                   @dragover="allowDrop"
                   @drop="onDrop($event, `${r-1},${c-1}`)">
                <span v-if="answerMap[`${r-1},${c-1}`]!=null"
                      class="num filled" :style="numDir">
                  {{ answerMap[`${r-1},${c-1}`] }}
                </span>
                <span v-else class="placeholder">؟</span>
              </div>

              <input class="manual-entry" type="number"
                     :value="manualDrafts[`${r-1},${c-1}`] ?? ''"
                     @input="onManualInput(`${r-1},${c-1}`, $event.target.value)"
                     @change="commitManual(`${r-1},${c-1}`)"
                     @blur="commitManual(`${r-1},${c-1}`)"
                     :placeholder="props.lang==='ar' ? 'أدخل رقمًا' : 'Enter value'"/>

              <button class="clear" @click="clearCell(`${r-1},${c-1}`)">
                <Eraser class="ic" /> {{ T[L].clear }}
              </button>
            </template>
          </div>
        </div>
      </div>

      <!-- Bank -->
      <div class="bank">
        <div class="bank-title">{{ T[L].bank }}</div>
        <div class="bank-items">
          <button v-for="v in bankList"
                  :key="v + '_' + Math.random()"
                  class="chip"
                  :style="numDir"
                  draggable="true"
                  @dragstart="onDragStart($event, v)">
            {{ v }}
          </button>
        </div>

        <div class="actions">
          <button class="btn" @click="resetAnswers"><RotateCcw class="ic" /> {{ T[L].reset }}</button>
          <button class="btn primary" @click="checkNow"><Check class="ic" /> {{ T[L].check }}</button>
          <button class="btn" @click="newPuzzle"><RefreshCw class="ic" /> {{ T[L].newQ }}</button>
        </div>

        <div v-if="toast" class="toast" :class="{ ok: solved }">{{ toast }}</div>
      </div>
    </div>

    <!-- Success overlay -->
    <div v-if="solved" class="overlay">
      <div class="card">
        <div class="big">{{ T[L].correct }}</div>
        <button class="btn primary" @click="newPuzzle">{{ T[L].newQ }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ---------- Theme tokens (light) ---------- */
.challenge2{
  --bg: #ffffff;              /* page background */
  --fg: #0b1220;              /* text color */
  --muted: #64748b;           /* secondary text */
  --panel: #ffffff;           /* card background */
  --panel-bd: #e2e8f0;        /* card border */
  --panel-shadow: 0 6px 20px rgba(2,6,23,.08);

  --drop-bg: rgba(99,102,241,.06);
  --drop-bd: #cbd5e1;
  --placeholder: #94a3b8;

  --chip-bg: #ffffff;
  --chip-bd: #e5e7ebaa;

  --btn-bg: #ffffff;
  --btn-bd: #e5e7ebaa;
  --btn-fg: #0b1220;

  --btn-primary-bg: #0ea5e9;
  --btn-primary-fg: #fff;

  --toast-err-bg: #fee2e2;
  --toast-err-fg: #991b1b;
  --toast-err-bd: #fecaca;

  --toast-ok-bg: #dcfce7;
  --toast-ok-fg: #166534;
  --toast-ok-bd: #bbf7d0;

  --overlay: rgba(2,6,23,.45);
}

/* ---------- Theme tokens (dark) ---------- */
[data-theme="dark"] .challenge2{
  --bg: #0b1220;
  --fg: #e5e7eb;
  --muted: #9ca3af;
  --panel: #0f172a;                 /* higher contrast than before */
  --panel-bd: #334155;
  --panel-shadow: 0 8px 28px rgba(0,0,0,.45);

  --drop-bg: rgba(59,130,246,.15);  /* visible in dark */
  --drop-bd: #475569;
  --placeholder: #94a3b8;

  --chip-bg: #111827;
  --chip-bd: #475569;

  --btn-bg: #111827;
  --btn-bd: #475569;
  --btn-fg: #e5e7eb;

  --btn-primary-bg: #38bdf8;       /* cyan for contrast on dark */
  --btn-primary-fg: #0b1220;

  --toast-err-bg: rgba(248,113,113,.18);
  --toast-err-fg: #fecaca;
  --toast-err-bd: rgba(248,113,113,.45);

  --toast-ok-bg: rgba(34,197,94,.22);
  --toast-ok-fg: #bbf7d0;
  --toast-ok-bd: rgba(34,197,94,.5);

  --overlay: rgba(0,0,0,.55);
}

/* ---------- Layout ---------- */
.title{ font-weight:700; margin:0 0 .25rem; color:var(--fg) }
.rule{ color:var(--muted); margin:0 0 1rem }

.layout{ display:grid; grid-template-columns:1fr 280px; gap:1rem }
.grid{
  background:var(--panel);
  border:1px solid var(--panel-bd);
  border-radius:1rem;
  padding:1rem;
  box-shadow:var(--panel-shadow);
}
.row{ display:grid; grid-template-columns:repeat(3,1fr); gap:.5rem }
.cell{
  border:1px dashed var(--panel-bd);
  min-height:92px;
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:.35rem;
  padding:.35rem; border-radius:.75rem; background:color-mix(in oklab, var(--panel) 92%, black 8%);
}

.num{ font-variant-numeric:tabular-nums; font-weight:700; font-size:1.2rem; color:var(--fg) }
.num.filled{ color:var(--fg) }

.placeholder{ color:var(--placeholder); font-size:1.2rem }

.dropzone{
  width:100%; flex:1; display:flex; align-items:center; justify-content:center;
  background:var(--drop-bg); border:2px dashed var(--drop-bd);
  border-radius:.65rem; transition: box-shadow .15s, border-color .15s;
}
.dropzone:hover{ box-shadow:0 0 0 3px color-mix(in oklab, var(--drop-bd) 40%, transparent); }

.manual-entry{
  width:100%; padding:.5rem .65rem; border-radius:.6rem;
  border:1px solid var(--panel-bd); background:var(--panel);
  font-size:.95rem; direction:ltr; color:var(--fg)
}
.manual-entry:focus{ outline:none; border-color:color-mix(in oklab, var(--btn-primary-bg) 65%, white 35%);
  box-shadow:0 0 0 3px color-mix(in oklab, var(--btn-primary-bg) 30%, transparent) }

.clear{
  font-size:.8rem; border:none; background:transparent; color:var(--muted);
  display:flex; align-items:center; gap:.35rem; cursor:pointer
}
.ic{ width:16px; height:16px }

/* ---------- Bank ---------- */
.bank{ display:flex; flex-direction:column; gap:.75rem }
.bank-title{ font-weight:700; color:var(--muted) }
.bank-items{ display:flex; flex-wrap:wrap; gap:.5rem }
.chip{
  border:1px solid var(--chip-bd); background:var(--chip-bg); color:var(--fg);
  padding:.45rem .65rem; border-radius:.75rem; cursor:grab;
  font-variant-numeric:tabular-nums; min-width:54px; text-align:center;
  box-shadow:0 6px 16px rgba(0,0,0,.08)
}
.chip:active{ cursor:grabbing }

/* ---------- Actions / Buttons ---------- */
.actions{ display:flex; gap:.6rem; flex-wrap:wrap; margin-top:.25rem }
.btn{
  display:inline-flex; align-items:center; gap:.4rem; padding:.55rem .8rem;
  border-radius:.8rem; border:1px solid var(--btn-bd); background:var(--btn-bg);
  color:var(--btn-fg); cursor:pointer; transition:.15s
}
.btn:hover{ transform:translateY(-1px); box-shadow:0 10px 22px rgba(0,0,0,.12) }
.btn.primary{ background:var(--btn-primary-bg); color:var(--btn-primary-fg); border-color:transparent }

/* ---------- Toast ---------- */
.toast{
  margin-top:.6rem; padding:.6rem .85rem; border-radius:.85rem;
  background:var(--toast-err-bg); color:var(--toast-err-fg); border:1px solid var(--toast-err-bd);
  font-weight:700; text-align:center
}
.toast.ok{ background:var(--toast-ok-bg); color:var(--toast-ok-fg); border-color:var(--toast-ok-bd) }

/* ---------- Overlay ---------- */
.overlay{ position:fixed; inset:0; background:var(--overlay); display:flex; align-items:center; justify-content:center; z-index:30 }
.card{
  background:var(--panel); color:var(--fg); padding:1rem 1.25rem; border-radius:1rem;
  box-shadow:var(--panel-shadow); display:flex; flex-direction:column; gap:.75rem; align-items:center; border:1px solid var(--panel-bd)
}
.big{ font-size:1.25rem; font-weight:800 }
</style>

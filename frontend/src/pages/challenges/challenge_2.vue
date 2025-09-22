<script setup>
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
  solved.value=false; toast.value=null; answerMap.value={}
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
  buildBankCounts()
  toast.value=null; solved.value=false
}

// سحب وإفلات بكميّات
function onDragStart(ev,value){ ev.dataTransfer.setData('text/plain', String(value)) }
function allowDrop(ev){ ev.preventDefault() }
function onDrop(ev,key){
  ev.preventDefault()
  const v=Number(ev.dataTransfer.getData('text/plain'))
  // إعادة المخزون لقيمة كانت في الخلية
  if(answerMap.value[key]!=null){
    const old=answerMap.value[key]
    bankCounts.value[old]=(bankCounts.value[old]||0)+1
  }
  // استهلاك من البنك إن متوفر
  if((bankCounts.value[v]||0)===0){ return } // لا توجد قطع متاحة
  bankCounts.value[v]-=1
  answerMap.value[key]=v
  toast.value=null
}
function clearCell(key){
  if(answerMap.value[key]!=null){
    const old=answerMap.value[key]
    bankCounts.value[old]=(bankCounts.value[old]||0)+1
    delete answerMap.value[key]
  }
}

const numDir = computed(()=>({direction:'ltr', unicodeBidi:'isolate'}))
onMounted(newPuzzle)
watch(()=>props.lang,()=>toast.value=null)
</script>

<template>
  <div class="challenge2" :data-theme="props.theme">
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
</style>

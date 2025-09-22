<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

const T = {
  ar:{ title:'التحدي 7: جدار أعداد (هرم جمع)',
       rule:'كل خانة تساوي مجموع الخليتين اللتين تحتها مباشرة. اسحب القيم المفقودة لإكمال الهرم.',
       bank:'لوحة الأعداد', newQ:'سؤال جديد', reset:'إعادة تعيين', check:'تحقّق',
       correct:'إجابة صحيحة', wrong:'تحقق من القيم', clear:'تفريغ الخلية' },
  en:{ title:'Challenge 7: Sum Pyramid',
       rule:'Each cell equals the sum of the two cells directly below. Drag missing values to complete the pyramid.',
       bank:'Number bank', newQ:'New puzzle', reset:'Reset', check:'Check',
       correct:'Correct answer', wrong:'Check your values', clear:'Clear cell' }
}
const L = computed(()=> (T[props.lang]?props.lang:'ar'))

/* ===== sounds (approved style) ===== */
import successUrl from '@/assets/sounds/success3.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong.mp3'

const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

/* ===== utils ===== */
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j]]=[x[j],x[i]]} return x }

/* ===== state ===== */
const baseN = ref(4)                 // عدد خلايا القاعدة
const rows = ref([])                 // rows[0]=القاعدة، ثم للأعلى
const blanks = ref(new Set())        // "r,c" حيث r فهرس الصف السفلي=0
const answerMap = ref({})            // "r,c" -> value
const bankCounts = ref({})           // value -> count
const solved = ref(false)
const toast = ref(null)

const numDir = computed(()=>({direction:'ltr', unicodeBidi:'isolate'}))

/* بناء الهرم */
function buildPyramid(n){
  const rs = []
  // القاعدة 1..9
  rs[0] = Array.from({length:n}, ()=> rndInt(1,9))
  for(let r=1;r<n;r++){
    rs[r] = Array.from({length:n-r}, (_,c)=> rs[r-1][c] + rs[r-1][c+1])
  }
  return rs
}

function keyOf(r,c){ return `${r},${c}` }

function pickBlanks(n){
  const all=[]
  for(let r=0;r<n;r++){
    for(let c=0;c<rows.value[r].length;c++){
      all.push([r,c])
    }
  }
  // دع واحدة على الأقل ظاهرة في كل صف غير القاعدة
  const keep = new Set()
  for(let r=1;r<n;r++){
    const idx = rndInt(0, rows.value[r].length-1)
    keep.add(keyOf(r, idx))
  }
  const candidates = all.filter(([r,c])=> r>0 && !keep.has(keyOf(r,c))) // لا نفرّغ القاعدة كلها
  const k = rndInt(4, 6)
  const chosen = shuffle(candidates).slice(0,k)
  return new Set(chosen.map(([r,c])=> keyOf(r,c)))
}

function rebuildBank(){
  const counts={}
  blanks.value.forEach(k=>{
    const [r,c]=k.split(',').map(Number)
    const v = rows.value[r][c]
    counts[v]=(counts[v]||0)+1
  })
  for(const [k,v] of Object.entries(answerMap.value)){
    counts[v]=(counts[v]||0)-1
  }
  for(const [v,ct] of Object.entries(counts)){ if(ct<=0) delete counts[v] }
  bankCounts.value=counts
}

const bankList = computed(()=>{
  const out=[]
  for(const [v,ct] of Object.entries(bankCounts.value)){
    for(let i=0;i<ct;i++) out.push(Number(v))
  }
  return shuffle(out)
})

function newPuzzle(){
  solved.value=false; toast.value=null; answerMap.value={}
  rows.value = buildPyramid(baseN.value)
  blanks.value = pickBlanks(baseN.value)
  rebuildBank()
}

function isFilled(){
  for(const k of blanks.value){ if(answerMap.value[k]==null) return false }
  return true
}
function isCorrect(){
  if(!isFilled()) return false
  for(const k of blanks.value){
    const [r,c]=k.split(',').map(Number)
    if(answerMap.value[k] !== rows.value[r][c]) return false
  }
  return true
}

async function addPoint(){
  try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{}
}
async function checkNow(){
  if(!isFilled()){ toast.value = L.value==='ar'?'أكمل كل الخانات':'Fill all blanks'; sWrong&&sWrong.play(); return }
  if(isCorrect()){ solved.value=true; toast.value=T[L.value].correct; sOK&&sOK.play(); sClap&&sClap.play(); await addPoint() }
  else { toast.value=T[L.value].wrong; sWrong&&sWrong.play() }
}
function resetAll(){
  answerMap.value={}
  rebuildBank()
  toast.value=null; solved.value=false
}

/* سحب/إفلات */
function onDragStart(ev,value){ ev.dataTransfer.setData('text/plain', String(value)) }
function allowDrop(ev){ ev.preventDefault() }
function onDrop(ev,key){
  ev.preventDefault()
  const v = Number(ev.dataTransfer.getData('text/plain'))
  if(answerMap.value[key]!=null){
    const old=answerMap.value[key]
    bankCounts.value[old]=(bankCounts.value[old]||0)+1
  }
  if((bankCounts.value[v]||0)===0) return
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

onMounted(newPuzzle)
watch(()=>props.lang,()=>{})
</script>

<template>
  <div class="challenge7" :data-theme="props.theme">
    <h2 class="title">{{ T[L].title }}</h2>
    <p class="rule">{{ T[L].rule }}</p>

    <div class="pyramid">
      <!-- من الأسفل للأعلى -->
      <div class="prow" v-for="(row,r) in rows" :key="'r'+r" :style="{ '--cols': row.length }">
        <div class="cell" v-for="(v,c) in row" :key="r+'-'+c">
          <template v-if="!(blanks.has(`${r},${c}`))">
            <span class="num" :style="numDir">{{ v }}</span>
          </template>
          <template v-else>
            <div class="dropzone" @dragover="allowDrop" @drop="onDrop($event, `${r},${c}`)">
              <span v-if="answerMap[`${r},${c}`]!=null" class="num" :style="numDir">
                {{ answerMap[`${r},${c}`] }}
              </span>
              <span v-else class="placeholder">؟</span>
            </div>
            <button class="clear" @click="clearCell(`${r},${c}`)"><Eraser class="ic" /> {{ T[L].clear }}</button>
          </template>
        </div>
      </div>
    </div>

    <div class="side">
      <div class="bank-title">{{ T[L].bank }}</div>
      <div class="bank-items">
        <button v-for="v in bankList" :key="v + '_' + Math.random()" class="chip"
                draggable="true" @dragstart="onDragStart($event, v)" :style="numDir">
          {{ v }}
        </button>
      </div>

      <div class="actions">
        <button class="btn" @click="resetAll"><RotateCcw class="ic" /> {{ T[L].reset }}</button>
        <button class="btn" @click="checkNow"><Check class="ic" /> {{ T[L].check }}</button>
        <button class="btn" @click="newPuzzle"><RefreshCw class="ic" /> {{ T[L].newQ }}</button>
      </div>

      <div v-if="toast" class="toast" :class="{ ok: solved }">{{ toast }}</div>
    </div>
  </div>
</template>

<style scoped>
.challenge7{ --bg:var(--c-bg,#fff); --fg:var(--c-fg,#111827); --muted:#6b7280 }
[data-theme="dark"] .challenge7{ --bg:#0b1220; --fg:#e5e7eb; --muted:#9ca3af }
.title{ font-weight:700; margin:0 0 .25rem } .rule{ color:var(--muted); margin:0 0 1rem }

/* الهرم */
.pyramid{
  background:var(--bg);
  border-radius:1rem;
  box-shadow:0 4px 14px rgba(0,0,0,.06);
  padding:1rem;
  width:max-content;
  margin-bottom:1rem;
}
.prow{
  display:grid;
  grid-template-columns: repeat(var(--cols), 88px);
  gap:.5rem;
  justify-content:center;
  margin-top:.5rem;
}
.cell{
  min-height:64px;
  border:1px dashed #cbd5e1;
  background:rgba(99,102,241,.06);
  border-radius:.75rem;
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:.25rem;
}
.num{ font-variant-numeric:tabular-nums; font-weight:700; font-size:1.15rem }
.placeholder{ color:var(--muted); font-size:1.15rem }
.dropzone{ width:100%; height:100%; display:flex; align-items:center; justify-content:center; }
.clear{ font-size:.75rem; border:none; background:transparent; color:var(--muted); display:flex; align-items:center; gap:.25rem; cursor:pointer }

/* البنك */
.side{ max-width:520px }
.bank-title{ font-weight:600; color:var(--muted); margin:.25rem 0 }
.bank-items{ display:flex; flex-wrap:wrap; gap:.5rem }
.chip{ border:1px solid #e5e7eb55; background:var(--bg); padding:.4rem .6rem; border-radius:.75rem; cursor:grab; font-variant-numeric:tabular-nums }
.actions{ display:flex; gap:.5rem; flex-wrap:wrap; margin-top:.5rem }
.btn{ display:inline-flex; align-items:center; gap:.35rem; padding:.5rem .7rem; border-radius:.75rem; border:1px solid #e5e7eb55; background:var(--bg); cursor:pointer }
.ic{ width:16px; height:16px }

.toast{ margin-top:.5rem; padding:.5rem .75rem; border-radius:.75rem; background:#fee2e2; color:#991b1b; border:1px solid #fecaca }
.toast.ok{ background:#dcfce7; color:#166534; border-color:#bbf7d0 }
</style>

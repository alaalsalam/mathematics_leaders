<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

const T = {
  ar:{ title:'التحدي 5: مخطط مثلث (ضرب)',
       rule:'كل مربع على الضلع يساوي حاصل ضرب العدديْن في الدائرتيْن المجاورتين له. اسحب القيم المفقودة إلى المربعات.',
       bank:'لوحة الأعداد', newQ:'سؤال جديد', reset:'إعادة تعيين', check:'تحقّق',
       correct:'إجابة صحيحة', wrong:'تحقق من القيم', clear:'تفريغ الخلية' },
  en:{ title:'Challenge 5: Triangle product',
       rule:'Each edge-square equals the product of the two adjacent circles. Drag missing values into the squares.',
       bank:'Number bank', newQ:'New puzzle', reset:'Reset', check:'Check',
       correct:'Correct answer', wrong:'Check your values', clear:'Clear cell' }
}
const L = computed(()=> (T[props.lang]?props.lang:'ar'))

/* ===== sounds ===== */
import successUrl from '@/assets/sounds/success2.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong5.mp3'   // تأكد من الاسم الصحيح للملف

const sOK   = typeof Audio !== 'undefined' ? new Audio(successUrl) : null
const sClap = typeof Audio !== 'undefined' ? new Audio(clapUrl)    : null
const sWrong= typeof Audio !== 'undefined' ? new Audio(wrongUrl)   : null

sOK && (sOK.preload = 'auto')
sClap && (sClap.preload = 'auto')
sWrong && (sWrong.preload = 'auto')

// utils
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]]} return x }

// state
const circles = ref([2,3,4])         // [top, left, right]
const squares = ref({ t:0, l:0, r:0 }) // edge squares: top edge between left-right? define: t=top (left-right base), l=left (top-left), r=right (top-right)
const blanks = ref(new Set())        // which of ['t','l','r'] are blank
const answerMap = ref({})            // key -> value
const bankCounts = ref({})           // value -> remaining copies
const solved = ref(false)
const toast = ref(null)

function buildTriangle(){
  // choose distinct circle values 2..9
  const vals = shuffle([2,3,4,5,6,7,8,9]).slice(0,3)
  circles.value = [vals[0], vals[1], vals[2]]
  const [ct, cl, cr] = circles.value   // top, left, right
  // products
  squares.value = {
    l: ct * cl, // left edge (top-left)
    r: ct * cr, // right edge (top-right)
    t: cl * cr  // base edge (left-right)
  }
}

function pickBlanks(){
  const keys = ['l','r','t']
  const k = rndInt(2,3)
  blanks.value = new Set(shuffle(keys).slice(0,k))
}

function rebuildBank(){
  const counts={}
  blanks.value.forEach(k=>{
    const v = squares.value[k]
    counts[v]=(counts[v]||0)+1
  })
  // subtract placed answers
  for(const [k,v] of Object.entries(answerMap.value)){
    counts[v]=(counts[v]||0)-1
  }
  for(const [v,ct] of Object.entries(counts)){ if(ct<=0) delete counts[v] }
  bankCounts.value = counts
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
  buildTriangle()
  pickBlanks()
  rebuildBank()
}

function isFilled(){
  for(const k of blanks.value){ if(answerMap.value[k]==null) return false }
  return true
}
function isCorrect(){
  if(!isFilled()) return false
  for(const k of blanks.value){
    if(answerMap.value[k] !== squares.value[k]) return false
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

// drag & drop
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

const numDir = computed(()=>({direction:'ltr', unicodeBidi:'isolate'}))
onMounted(newPuzzle)
watch(()=>props.lang,()=>{})
</script>

<template>
  <div class="challenge5" :data-theme="props.theme">
    <h2 class="title">{{ T[L].title }}</h2>
    <p class="rule">{{ T[L].rule }}</p>

    <!-- الرسم -->
    <div class="tri-wrap">
      <!-- الروابط -->
      <svg class="links" viewBox="0 0 300 260" preserveAspectRatio="none">
        <line x1="150" y1="40" x2="60"  y2="140" />
        <line x1="150" y1="40" x2="240" y2="140" />
        <line x1="60"  y1="140" x2="240" y2="140" />
      </svg>

      <!-- الدوائر -->
      <div class="circle top" :style="numDir">{{ circles[0] }}</div>
      <div class="circle left" :style="numDir">{{ circles[1] }}</div>
      <div class="circle right" :style="numDir">{{ circles[2] }}</div>

      <!-- المربعات على الأضلاع -->
      <!-- left edge -->
      <div class="square left-sq">
        <template v-if="!blanks.has('l')">
          <span class="num" :style="numDir">{{ squares.l }}</span>
        </template>
        <template v-else>
          <div class="dropzone" @dragover="allowDrop" @drop="onDrop($event,'l')">
            <span v-if="answerMap['l']!=null" class="num" :style="numDir">{{ answerMap['l'] }}</span>
            <span v-else class="placeholder">؟</span>
          </div>
          <button class="clear" @click="clearCell('l')"><Eraser class="ic"/> {{ T[L].clear }}</button>
        </template>
      </div>

      <!-- right edge -->
      <div class="square right-sq">
        <template v-if="!blanks.has('r')">
          <span class="num" :style="numDir">{{ squares.r }}</span>
        </template>
        <template v-else>
          <div class="dropzone" @dragover="allowDrop" @drop="onDrop($event,'r')">
            <span v-if="answerMap['r']!=null" class="num" :style="numDir">{{ answerMap['r'] }}</span>
            <span v-else class="placeholder">؟</span>
          </div>
          <button class="clear" @click="clearCell('r')"><Eraser class="ic"/> {{ T[L].clear }}</button>
        </template>
      </div>

      <!-- base edge -->
      <div class="square base-sq">
        <template v-if="!blanks.has('t')">
          <span class="num" :style="numDir">{{ squares.t }}</span>
        </template>
        <template v-else>
          <div class="dropzone" @dragover="allowDrop" @drop="onDrop($event,'t')">
            <span v-if="answerMap['t']!=null" class="num" :style="numDir">{{ answerMap['t'] }}</span>
            <span v-else class="placeholder">؟</span>
          </div>
          <button class="clear" @click="clearCell('t')"><Eraser class="ic"/> {{ T[L].clear }}</button>
        </template>
      </div>
    </div>

    <!-- البنك -->
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

    <div v-if="solved" class="overlay">
      <div class="card">
        <div class="big">{{ T[L].correct }}</div>
        <button class="btn" @click="newPuzzle">{{ T[L].newQ }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.challenge5{ --bg:var(--c-bg,#fff); --fg:var(--c-fg,#111827); --muted:#6b7280 }
[data-theme="dark"] .challenge5{ --bg:#0b1220; --fg:#e5e7eb; --muted:#9ca3af }

.title{ font-weight:700; margin:0 0 .25rem }
.rule{ color:var(--muted); margin:0 0 1rem }

/* الرسم */
.tri-wrap{
  position:relative;
  width:360px;            /* أوسع من قبل لتباعد الأضلاع */
  height:300px;
  margin:0 auto 1rem;
  background:var(--bg);
  border-radius:1rem;
  box-shadow:0 4px 14px rgba(0,0,0,.06);
  padding:8px;            /* مساحة إضافية من الداخل */
}

.links{ position:absolute; inset:0; pointer-events:none }
.links line{ stroke:#cbd5e1; stroke-width:2 }

.circle{
  position:absolute; width:58px; height:58px; border-radius:9999px;
  background:rgba(234,179,8,.22);
  display:flex; align-items:center; justify-content:center;
  font-weight:700; font-variant-numeric:tabular-nums;
}
.top{   left:151px; top:24px }     /* 180 - 29 */
.left{  left:51px;  top:168px }
.right{ right:51px; top:168px }

.square{
  position:absolute; width:74px; height:60px;
  background:rgba(99,102,241,.08);
  border-radius:.75rem; border:1px dashed #cbd5e1;
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:.25rem;
}
.left-sq{  left:70px;  top:88px }  /* أبعدناها عن الوسط */
.right-sq{ right:70px; top:88px }
.base-sq{  left:143px; bottom:32px } /* (360-74)/2 لتوسيط القاعدة */

.num{ font-variant-numeric:tabular-nums; font-weight:700; font-size:1.15rem }
.placeholder{ color:var(--muted); font-size:1.15rem }
.dropzone{ width:100%; flex:1; display:flex; align-items:center; justify-content:center; }
.clear{ font-size:.75rem; border:none; background:transparent; color:var(--muted); display:flex; align-items:center; gap:.25rem; cursor:pointer }

/* البنك */
.side{ max-width:420px; margin:0 auto }
.bank-title{ font-weight:600; color:var(--muted); margin:.25rem 0 }
.bank-items{ display:flex; flex-wrap:wrap; gap:.5rem }
.chip{ border:1px solid #e5e7eb55; background:var(--bg); padding:.4rem .6rem; border-radius:.75rem; cursor:grab; font-variant-numeric:tabular-nums }
.actions{ display:flex; gap:.5rem; flex-wrap:wrap; margin-top:.5rem }
.btn{ display:inline-flex; align-items:center; gap:.35rem; padding:.5rem .7rem; border-radius:.75rem; border:1px solid #e5e7eb55; background:var(--bg); cursor:pointer }
.ic{ width:16px; height:16px }

.toast{ margin-top:.5rem; padding:.5rem .75rem; border-radius:.75rem; background:#fee2e2; color:#991b1b; border:1px solid #fecaca }
.toast.ok{ background:#dcfce7; color:#166534; border-color:#bbf7d0 }

/* نجاح */
.overlay{ position:fixed; inset:0; background:rgba(0,0,0,.35); display:flex; align-items:center; justify-content:center }
.card{ background:var(--bg); color:var(--fg); padding:1rem 1.25rem; border-radius:1rem; box-shadow:0 10px 30px rgba(0,0,0,.25); display:flex; flex-direction:column; gap:.75rem; align-items:center }
.big{ font-size:1.25rem; font-weight:700 }
</style>


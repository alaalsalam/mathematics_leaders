<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

const T = {
  ar:{
    title:'التحدي 4: أكمل جدول الضرب',
    rule:'جدول ضرب بعناوين صفوف وأعمدة. اسحب القيم الصحيحة من الأسفل إلى الخانات الفارغة.',
    bank:'لوحة الأعداد', newQ:'سؤال جديد', reset:'إعادة تعيين',
    check:'تحقّق', correct:'إجابة صحيحة', wrong:'تحقق من القيم', clear:'تفريغ الخلية'
  },
  en:{
    title:'Challenge 4: Complete the multiplication table',
    rule:'A multiplication table with row/column headers. Drag correct values into the blanks.',
    bank:'Number bank', newQ:'New puzzle', reset:'Reset',
    check:'Check', correct:'Correct', wrong:'Check your values', clear:'Clear cell'
  }
}
const L = computed(()=> (T[props.lang]?props.lang:'ar'))

// أصوات اختيارية
/* ===== sounds ===== */
import successUrl from '@/assets/sounds/success4.mp3'
// import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong4.mp3'   // تأكد من الاسم الصحيح للملف

const sOK   = typeof Audio !== 'undefined' ? new Audio(successUrl) : null
// const sClap = typeof Audio !== 'undefined' ? new Audio(clapUrl)    : null
const sWrong= typeof Audio !== 'undefined' ? new Audio(wrongUrl)   : null

sOK && (sOK.preload = 'auto')
// sClap && (sClap.preload = 'auto')
sWrong && (sWrong.preload = 'auto')


// أدوات عشوائية
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]]} return x }

// الحالة
const n = 3                                    // جدول 3×3
const factorsR = ref([])                       // عناوين الصفوف
const factorsC = ref([])                       // عناوين الأعمدة
const blanks = ref(new Set())                  // مفاتيح الفراغات
const answerMap = ref({})                      // key -> value المُسقَط
const bankCounts = ref({})                     // value -> المتبقي
const solved = ref(false)
const toast = ref(null)

// بناء القيم الصحيحة لكل خانة
function valueAt(r,c){
  if(r===0 && c===0) return '×'
  if(r===0) return factorsC.value[c-1]
  if(c===0) return factorsR.value[r-1]
  return factorsR.value[r-1] * factorsC.value[c-1]
}

// مفاتيح الخانات
const keyH = (r,c)=> (r===0||c===0)?`h:${r},${c}`:`c:${r},${c}`

// اختيار عوامل بدون تكرار من 1..9
function pickFactors(k){
  return shuffle([1,2,3,4,5,6,7,8,9]).slice(0,k).sort((a,b)=>a-b)
}

// اختيار الفراغات
function pickBlanks(){
  const all=[]
  for(let r=0;r<=n;r++) for(let c=0;c<=n;c++){
    if(r===0 && c===0) continue // زاوية × ثابتة
    all.push([r,c])
  }
  // لا نجعل كل الجسم فارغاً؛ نضمن خلية جسم واحدة على الأقل ظاهرة للمساعدة
  const bodyCells = all.filter(([r,c])=> r>0 && c>0)
  const shownHelp = shuffle(bodyCells)[0]
  const candidates = all.filter(([r,c])=> !(r===shownHelp[0] && c===shownHelp[1]))
  const k = rndInt(5, 8) // عدد الفراغات
  const chosen = shuffle(candidates).slice(0,k)
  return new Set(chosen.map(([r,c])=> keyH(r,c)))
}

// تحضير بنك الأعداد بكميات
function rebuildBank(){
  const counts={}
  blanks.value.forEach(k=>{
    const [tag,rc]=k.split(':'); const [r,c]=rc.split(',').map(Number)
    const v = valueAt(r,c)
    counts[v]=(counts[v]||0)+1
  })
  // إعادة احتساب بعد إسقاط إجابات موجودة
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
  factorsR.value = pickFactors(n)
  factorsC.value = pickFactors(n)
  blanks.value = pickBlanks()
  rebuildBank()
}

function isFilled(){
  for(const k of blanks.value){ if(answerMap.value[k]==null) return false }
  return true
}
function isCorrect(){
  if(!isFilled()) return false
  for(const k of blanks.value){
    const [_,rc]=k.split(':'); const [r,c]=rc.split(',').map(Number)
    if(answerMap.value[k] !== valueAt(r,c)) return false
  }
  return true
}

async function addPoint(){
  try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{}
}
async function checkNow(){
  if(!isFilled()){ toast.value = L.value==='ar'?'أكمل كل الخانات':'Fill all blanks'; sWrong&&sWrong.play(); return }
  if(isCorrect()){ solved.value=true; toast.value=T[L.value].correct; sOK&&sOK.play(); await addPoint() }
  else { toast.value=T[L.value].wrong; sWrong&&sWrong.play() }
}
function resetAll(){
  answerMap.value={}
  rebuildBank()
  toast.value=null; solved.value=false
}

// سحب/إفلات مع كميّات
function onDragStart(ev,value){ ev.dataTransfer.setData('text/plain', String(value)) }
function allowDrop(ev){ ev.preventDefault() }
function onDrop(ev,key){
  ev.preventDefault()
  const v = Number(ev.dataTransfer.getData('text/plain'))
  // إن كانت الخلية تحتوي قيمة نعيدها للبنك
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
  <div class="challenge4" :data-theme="props.theme">
    <h2 class="title">{{ T[L].title }}</h2>
    <p class="rule">{{ T[L].rule }}</p>

    <!-- الجدول -->
    <div class="table">
      <div class="row" v-for="r in (n+1)" :key="'r'+r">
        <div
          class="cell header"
          v-for="c in (n+1)"
          :key="'c'+r+'-'+c"
          :class="{ th: r===1 || c===1, corner: r===1 && c===1 }"
        >
          <!-- الزاوية -->
          <template v-if="r===1 && c===1">
            ×
          </template>

          <!-- خلايا غير فارغة -->
          <template v-else-if="!blanks.has((r===1||c===1)?`h:${r-1},${c-1}`:`c:${r-1},${c-1}`)">
            <span class="num" :style="numDir">{{ valueAt(r-1,c-1) }}</span>
          </template>

          <!-- خلايا فارغة -->
          <template v-else>
            <div class="dropzone"
                 @dragover="allowDrop"
                 @drop="onDrop($event, (r===1||c===1)?`h:${r-1},${c-1}`:`c:${r-1},${c-1}`)">
              <span v-if="answerMap[(r===1||c===1)?`h:${r-1},${c-1}`:`c:${r-1},${c-1}`] != null"
                    class="num" :style="numDir">
                {{ answerMap[(r===1||c===1)?`h:${r-1},${c-1}`:`c:${r-1},${c-1}`] }}
              </span>
              <span v-else class="placeholder">؟</span>
            </div>
            <button class="clear" @click="clearCell((r===1||c===1)?`h:${r-1},${c-1}`:`c:${r-1},${c-1}`)">
              <Eraser class="ic"/> {{ T[L].clear }}
            </button>
          </template>
        </div>
      </div>
    </div>

    <!-- البنك -->
    <div class="side">
      <div class="bank-title">{{ T[L].bank }}</div>
      <div class="bank-items">
        <button
          v-for="v in bankList"
          :key="v + '_' + Math.random()"
          class="chip"
          draggable="true"
          @dragstart="onDragStart($event, v)"
          :style="numDir"
        >{{ v }}</button>
      </div>

      <div class="actions">
        <button class="btn" @click="resetAll"><RotateCcw class="ic" /> {{ T[L].reset }}</button>
        <button class="btn" @click="checkNow"><Check class="ic" /> {{ T[L].check }}</button>
        <button class="btn" @click="newPuzzle"><RefreshCw class="ic" /> {{ T[L].newQ }}</button>
      </div>

      <div v-if="toast" class="toast" :class="{ ok: solved }">{{ toast }}</div>
    </div>

    <!-- نجاح -->
    <div v-if="solved" class="overlay">
      <div class="card">
        <div class="big">{{ T[L].correct }}</div>
        <button class="btn" @click="newPuzzle">{{ T[L].newQ }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.challenge4{ --bg:var(--c-bg,#fff); --fg:var(--c-fg,#111827); --muted:#6B7280 }
[data-theme="dark"] .challenge4{ --bg:#0b1220; --fg:#e5e7eb; --muted:#9ca3af }
.title{ font-weight:700; margin:0 0 .25rem } .rule{ color:var(--muted); margin:0 0 1rem }

/* الجدول */
.table{ display:inline-block; background:var(--bg); border-radius:1rem; padding:.75rem; box-shadow:0 4px 14px rgba(0,0,0,.06) }
.row{ display:grid; grid-template-columns: repeat(4, 110px) }
.cell{ border:1px dashed #cbd5e1; min-height:72px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:.25rem; padding:.25rem }
.th{ background:rgba(234,179,8,.12) }
.corner{ background:rgba(234,179,8,.25); font-weight:700 }
.num{ font-variant-numeric:tabular-nums; font-weight:700; font-size:1.15rem }
.placeholder{ color:var(--muted); font-size:1.15rem }
.dropzone{ width:100%; flex:1; display:flex; align-items:center; justify-content:center; background:rgba(99,102,241,.06); border-radius:.5rem }
.clear{ font-size:.75rem; border:none; background:transparent; color:var(--muted); display:flex; align-items:center; gap:.25rem; cursor:pointer }

/* البنك والعمليات */
.side{ margin-top:1rem }
.bank-title{ font-weight:600; color:var(--muted); margin-bottom:.25rem }
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

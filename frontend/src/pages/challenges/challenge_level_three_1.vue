<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

const T = {
  ar:{
    title:'المستوى الثالث – التحدي 1: هرم الضرب',
    rule:'املأ مربعات الهرم بحيث يساوي كل مربع أعلى حاصل ضرب الخليتين تحته. اسحب الأرقام الصحيحة من اللوحة حتى يكتمل الهرم.',
    hint:'تذكّر أن كل خطوة نحو الأعلى هي نتيجة ضرب الخليتين في الأسفل مباشرة.',
    bank:'لوحة الأرقام', newQ:'سؤال جديد', reset:'إعادة تعيين', check:'تحقّق',
    correct:'أحسنت! اكتمل الهرم.', wrong:'تحقّق مرة أخرى، هناك قيمة في غير مكانها.',
    clear:'تفريغ الخلية'
  },
  en:{
    title:'Level 3 – Challenge 1: Multiplication Pyramid',
    rule:'Fill the pyramid so that every cell above equals the product of the two cells directly beneath it. Drag the correct numbers from the bank.',
    hint:'Remember: each step upward is the product of the two numbers underneath.',
    bank:'Number bank', newQ:'New puzzle', reset:'Reset', check:'Check',
    correct:'Great! The pyramid is complete.', wrong:'Something is off. Recheck the placements.',
    clear:'Clear cell'
  }
}
const L = computed(()=> (T[props.lang]?props.lang:'ar'))

/* sounds */
import successUrl from '@/assets/sounds/success3.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong3.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

/* helpers */
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]] } return x }
function keyOf(r,c){ return `${r},${c}` }

/* state */
const rows = ref([])                  // صفوف الهرم من القاعدة للأعلى
const blanks = ref(new Set())         // مفاتيح الخلايا الفارغة
const answerMap = reactive({})        // key -> value المسحوبة
const totalCounts = reactive({})      // العدد الكلي لكل قيمة متاحة
const bankCounts = reactive({})       // العدد المتبقي لكل قيمة
const toast = ref(null)
const solved = ref(false)

const numDir = computed(()=>({ direction:'ltr', unicodeBidi:'isolate' }))
const displayRows = computed(()=> rows.value.map((cells,index)=>({ cells, index })).slice().reverse())

function usageOf(val){
  let used = 0
  for(const k in answerMap){ if(answerMap[k] === val) used++ }
  return used
}

function rebuildBank(){
  const available = {}
  for(const [valStr,total] of Object.entries(totalCounts)){
    const val = Number(valStr)
    const remaining = total - usageOf(val)
    if(remaining > 0) available[val] = remaining
  }
  for(const k in bankCounts){ delete bankCounts[k] }
  for(const [val,ct] of Object.entries(available)) bankCounts[val] = ct
}

function generatePyramid(){
  while(true){
    const base = Array.from({length:4}, ()=> rndInt(2,6))
    const built = [base]
    for(let r=1;r<4;r++){
      const prev = built[r-1]
      const row = []
      for(let c=0;c<prev.length-1;c++) row.push(prev[c] * prev[c+1])
      built.push(row)
    }
    const top = built[3][0]
    if(top <= 50000) return built
  }
}

function newPuzzle(){
  solved.value=false
  toast.value=null
  const built = generatePyramid()
  rows.value = built
  blanks.value = new Set()
  for(const k in answerMap) delete answerMap[k]
  for(let r=1;r<rows.value.length;r++){
    for(let c=0;c<rows.value[r].length;c++) blanks.value.add(keyOf(r,c))
  }
  const totals = {}
  blanks.value.forEach(k=>{
    const [r,c] = k.split(',').map(Number)
    const val = rows.value[r][c]
    totals[val] = (totals[val] || 0) + 1
  })
  for(const k in totalCounts) delete totalCounts[k]
  for(const [val,ct] of Object.entries(totals)) totalCounts[val] = ct
  rebuildBank()
}

function allowDrop(ev){ ev.preventDefault() }
function onDragStart(ev, value){ ev.dataTransfer.setData('text/plain', String(value)) }
function dropTo(key, ev){
  ev.preventDefault()
  if(!blanks.value.has(key)) return
  const raw = ev.dataTransfer.getData('text/plain')
  const val = Number(raw)
  if(Number.isNaN(val) || !totalCounts[val]) return
  const current = answerMap[key]
  if(current === val){ return }
  const used = usageOf(val)
  if(used >= totalCounts[val]) return
  if(current != null) delete answerMap[key]
  answerMap[key] = val
  rebuildBank()
  toast.value=null
}
function clearCell(key){
  if(answerMap[key] != null){
    delete answerMap[key]
    rebuildBank()
  }
}

function isFilled(){
  for(const key of blanks.value){ if(answerMap[key]==null) return false }
  return true
}
function isCorrect(){
  for(const key of blanks.value){
    const [r,c] = key.split(',').map(Number)
    if(answerMap[key] !== rows.value[r][c]) return false
  }
  return true
}

async function addPoint(){
  try{
    await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1', { method:'GET', credentials:'include' })
  }catch{}
}
async function checkNow(){
  if(!isFilled()){ toast.value = L.value==='ar' ? 'أكمل كل الخانات أولاً.' : 'Fill all blanks first.'; sWrong && sWrong.play(); return }
  if(isCorrect()){
    solved.value = true
    toast.value = T[L.value].correct
    sOK && sOK.play(); sClap && sClap.play()
    await addPoint()
  }else{
    toast.value = T[L.value].wrong
    sWrong && sWrong.play()
  }
}
function resetAll(){
  for(const k in answerMap) delete answerMap[k]
  solved.value=false
  toast.value=null
  rebuildBank()
}

const bankList = computed(()=>{
  const items = []
  for(const [val,ct] of Object.entries(bankCounts)){
    for(let i=0;i<ct;i++) items.push(Number(val))
  }
  return shuffle(items)
})

onMounted(newPuzzle)
watch(()=>props.lang,()=>{ if(toast.value) toast.value = null })
</script>

<template>
  <div class="lvl3c1" :data-theme="props.theme">
    <h2 class="title">{{ T[L].title }}</h2>
    <p class="rule">{{ T[L].rule }}</p>
    <p class="hint">{{ T[L].hint }}</p>

    <div class="pyramid" :dir="props.lang==='ar' ? 'rtl' : 'ltr'">
      <div class="p-row" v-for="row in displayRows" :key="row.index">
        <div
          class="brick"
          v-for="(val,cIdx) in row.cells"
          :key="row.index + '-' + cIdx"
        >
          <template v-if="!blanks.has(keyOf(row.index, cIdx))">
            <span class="num" :style="numDir">{{ val }}</span>
          </template>
          <template v-else>
            <div class="dropzone" @dragover="allowDrop" @drop="dropTo(keyOf(row.index, cIdx), $event)">
              <span v-if="answerMap[keyOf(row.index, cIdx)] != null" class="num" :style="numDir">{{ answerMap[keyOf(row.index, cIdx)] }}</span>
              <span v-else class="placeholder">؟</span>
            </div>
            <button class="clear" @click="clearCell(keyOf(row.index, cIdx))"><Eraser class="ic" /> {{ T[L].clear }}</button>
          </template>
        </div>
      </div>
    </div>

    <div class="bank">
      <div class="bank-title">{{ T[L].bank }}</div>
      <div class="bank-items">
        <button
          v-for="(val, idx) in bankList"
          :key="val + '_' + idx"
          class="chip"
          draggable="true"
          @dragstart="onDragStart($event, val)"
          :style="numDir"
        >
          {{ val }}
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
.lvl3c1{ --bg:var(--c-bg,#fff); --fg:var(--c-fg,#111827); --muted:#6b7280 }
[data-theme="dark"] .lvl3c1{ --bg:#0b1220; --fg:#e5e7eb; --muted:#9ca3af }
.title{ font-weight:700; margin:0 0 .25rem }
.rule{ margin:0 0 .35rem; color:var(--muted) }
.hint{ margin:0 0 1rem; color:var(--muted); font-size:.9rem }

.pyramid{ display:flex; flex-direction:column; align-items:center; gap:.65rem; margin-bottom:1.25rem }
.p-row{ display:flex; gap:.65rem; justify-content:center }
.brick{ background:var(--bg); border:1px solid #e5e7ebaa; border-radius:.9rem; padding:.5rem .75rem; min-width:96px; min-height:72px; display:flex; flex-direction:column; align-items:center; justify-content:center; box-shadow:0 4px 12px rgba(0,0,0,.06) }
[data-theme="dark"] .brick{ border-color:#1f2937; box-shadow:0 4px 12px rgba(0,0,0,.3) }

.num{ font-weight:700; font-size:1.2rem; font-variant-numeric:tabular-nums }
.placeholder{ color:#cbd5f5; font-size:1.4rem }
.dropzone{ display:flex; align-items:center; justify-content:center; width:100%; height:100% }
.dropzone:hover{ box-shadow:0 0 0 3px rgba(59,130,246,.22) inset; border-radius:.6rem }
.clear{ margin-top:.45rem; align-self:center; display:inline-flex; gap:.3rem; align-items:center; padding:.3rem .55rem; border-radius:.6rem; border:1px solid #e5e7eb88; background:var(--bg); cursor:pointer; font-size:.75rem }
.ic{ width:16px; height:16px }

.bank{ margin-bottom:1rem }
.bank-title{ font-weight:600; margin-bottom:.5rem }
.bank-items{ display:flex; flex-wrap:wrap; gap:.5rem }
.chip{ padding:.45rem .8rem; border-radius:.8rem; border:1px solid #cbd5f5aa; background:var(--bg); cursor:grab; font-weight:600; font-variant-numeric:tabular-nums }
.chip:active{ cursor:grabbing }

.actions{ display:flex; gap:.6rem; flex-wrap:wrap; margin-bottom:1rem }
.btn{ display:inline-flex; align-items:center; gap:.35rem; padding:.5rem .8rem; border-radius:.75rem; border:1px solid #e5e7eb55; background:var(--bg); cursor:pointer }

.toast{ padding:.6rem .9rem; border-radius:.8rem; border:1px solid #fecaca; background:#fee2e2; color:#991b1b }
.toast.ok{ border-color:#bbf7d0; background:#dcfce7; color:#166534 }
</style>

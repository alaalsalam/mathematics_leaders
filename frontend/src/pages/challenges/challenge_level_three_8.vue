<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{ type:String, default:'ar' }, theme:{ type:String, default:'light' } })

/* i18n */
const copy = {
  ar:{
    title:'المستوى الثالث – التحدي 2: الأرقام المفقودة على البطاقات',
    rule:'أمامك بطاقات ملوّنة بأرقام مفقودة. استخدم المعلومات المعطاة (المجموع، المتوسط، الوسيط، المدى) لتحديد الرقم المناسب لكل بطاقة، ثم اسحبه من لوحة الأعداد أو اكتبه يدويًا.',
    bank:'لوحة الأعداد', newQ:'سؤال جديد', reset:'مسح', check:'تحقّق',
    correct:'أحسنت! الأرقام صحيحة.', wrong:'تحقّق من القيم مرة أخرى.', clear:'تفريغ البطاقة',
    hints:{ sum:'المجموع', mean:'المتوسط الحسابي', median:'الوسيط', range:'المدى' },
    manualPlaceholder:'أدخل رقمًا'
  },
  en:{
    title:'Level 3 – Challenge 2: Missing numbers on the cards',
    rule:'Each coloured card is missing its number. Use the given information (sum, mean, median, range) to deduce the correct value for every card, then drag a number from the bank or type it manually.',
    bank:'Number bank', newQ:'New puzzle', reset:'Clear', check:'Check',
    correct:'Great! All numbers are correct.', wrong:'Something is off – recheck the values.', clear:'Clear card',
    hints:{ sum:'Sum', mean:'Mean', median:'Median', range:'Range' },
    manualPlaceholder:'Type value'
  }
}
const L = computed(() => (copy[props.lang] ? props.lang : 'ar'))
const locale = computed(() => (props.lang === 'ar' ? 'ar-EG' : 'en-US'))
const numDir = computed(()=>({direction:'ltr', unicodeBidi:'isolate'}))

/* sounds */
import successUrl from '@/assets/sounds/success3.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong2.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

/* data */
const colourPalette = ['green','gold','teal','magenta','sky','orange','crimson']
const templates = [
  { numbers:[4,8,12,16,20] },
  { numbers:[5,9,11,13,22] },   // مجموع=60، متوسط=12، وسيط=11، مدى=17
  { numbers:[7,10,12,18,23] },
  { numbers:[6,8,15,19,22] },
  { numbers:[9,11,14,20,26] }
]
const EXTRA_CHOICES = 4

function computeHints(numbers){
  const sorted = numbers.slice().sort((a,b)=>a-b)
  const sum = sorted.reduce((s,n)=>s+n,0)
  const mean = sum / sorted.length
  const median = sorted[Math.floor(sorted.length/2)]
  const range = sorted.at(-1) - sorted[0]
  return { sum, mean, median, range }
}

/* state */
const cards = ref([])                 // [{id,color,value}]
const solution = reactive({})         // id -> value
const blanks = ref(new Set())         // ids
const totalCounts = reactive({})      // solution value counts
const extraCounts = reactive({})      // distractor counts
const bankCounts  = reactive({})      // value -> remaining copies
const answer = reactive({})           // id -> chosen value
const answerSource = reactive({})     // 'bank' | 'manual'
const manualDrafts = reactive({})     // id -> string
const hints = ref({ sum:0, mean:0, median:0, range:0 })
const toast = ref(null)
const solved = ref(false)

function resetReactiveMap(obj){ for (const k of Object.keys(obj)) delete obj[k] }

/* puzzle builder */
function buildPuzzle(){
  const tpl = templates[Math.floor(Math.random()*templates.length)]
  const nums = tpl.numbers.slice()
  const colours = colourPalette.slice(0, nums.length).sort(()=>Math.random()-0.5)
  const arrangement = nums.slice().sort(()=>Math.random()-0.5)

  cards.value = []
  blanks.value = new Set()
  resetReactiveMap(solution); resetReactiveMap(answer); resetReactiveMap(answerSource)
  resetReactiveMap(manualDrafts); resetReactiveMap(totalCounts)
  resetReactiveMap(extraCounts);  resetReactiveMap(bankCounts)

  arrangement.forEach((value, idx) => {
    const id = `card-${idx}`
    cards.value.push({ id, value, color: colours[idx % colours.length] })
    solution[id] = value
    blanks.value.add(id)
    totalCounts[value] = (totalCounts[value] || 0) + 1
  })
  // bank starts with solution counts
  for (const [val, ct] of Object.entries(totalCounts)) bankCounts[val] = ct

  // add distractors without colliding with solutions
  const minVal = Math.min(...nums)
  const maxVal = Math.max(...nums)
  const lower = Math.max(1, minVal - 12)
  const upper = maxVal + 12
  const extras = new Set()
  while(extras.size < EXTRA_CHOICES){
    const c = Math.floor(Math.random() * (upper - lower + 1)) + lower
    if(totalCounts[c]) continue
    extras.add(c)
  }
  extras.forEach(v => { extraCounts[v]=(extraCounts[v]||0)+1; bankCounts[v]=(bankCounts[v]||0)+1 })

  hints.value = computeHints(nums)
  toast.value = null; solved.value = false
}

/* dnd */
function onDragStart(ev, value){ ev.dataTransfer.setData('text/plain', String(value)) }
function allowDrop(ev){ ev.preventDefault() }

function setAnswer(cardId, value, source){
  if(!Number.isFinite(value)) return false

  // return previous bank item if needed
  if(answer[cardId] != null && answerSource[cardId] === 'bank'){
    const prev = answer[cardId]
    bankCounts[prev] = (bankCounts[prev] || 0) + 1
  }

  if(source === 'bank'){
    if((bankCounts[value] || 0) <= 0) return false
    bankCounts[value] = Math.max(0, (bankCounts[value] || 0) - 1)
  }

  answer[cardId] = value
  answerSource[cardId] = source
  manualDrafts[cardId] = String(value)
  toast.value = null; solved.value = false
  return true
}

function onDrop(ev, cardId){
  ev.preventDefault()
  const val = Number(ev.dataTransfer.getData('text/plain'))
  if(Number.isNaN(val)) return
  setAnswer(cardId, val, 'bank')
}

function clearCard(cardId){
  if(answer[cardId] != null && answerSource[cardId] === 'bank'){
    const prev = answer[cardId]
    bankCounts[prev] = (bankCounts[prev] || 0) + 1
  }
  delete answer[cardId]; delete answerSource[cardId]
  manualDrafts[cardId] = ''
  toast.value = null; solved.value = false
}

/* checking */
function isFilled(){ for(const id of blanks.value){ if(answer[id]==null) return false } return true }
function isCorrect(){ for(const id of blanks.value){ if(answer[id]!==solution[id]) return false } return true }

async function addPoint(){
  try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{}
}
async function checkNow(){
  if(!isFilled()){ toast.value = L.value==='ar' ? 'أكمل كل البطاقات أولاً.' : 'Fill every card first.'; sWrong&&sWrong.play(); return }
  if(isCorrect()){ solved.value=true; toast.value=copy[L.value].correct; sOK&&sOK.play(); sClap&&sClap.play(); await addPoint() }
  else{ toast.value=copy[L.value].wrong; sWrong&&sWrong.play() }
}

function resetAll(){
  resetReactiveMap(answer); resetReactiveMap(answerSource); resetReactiveMap(manualDrafts)
  resetReactiveMap(bankCounts)
  for (const [v,ct] of Object.entries(totalCounts)) bankCounts[v]=ct
  for (const [v,ct] of Object.entries(extraCounts)) bankCounts[v]=(bankCounts[v]||0)+ct
  toast.value=null; solved.value=false
}

/* bank computed */
const bankList = computed(()=>{
  const arr=[]
  for(const [v,ct] of Object.entries(bankCounts)){
    for(let i=0;i<ct;i++) arr.push({ value:Number(v), key:`${v}-${i}` })
  }
  // stable order for UX
  return arr.sort((a,b)=>a.value-b.value)
})

/* manual entry */
function onManualInput(cardId, value){ manualDrafts[cardId] = value }
function commitManual(cardId){
  const raw = (manualDrafts[cardId] ?? '').trim()
  if(raw===''){ clearCard(cardId); return }
  const num = Number(raw)
  if(!Number.isFinite(num)) return
  setAnswer(cardId, num, 'manual')
}

/* numerals */
const digitsMap = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩']
function formatDigit(value){
  const s = String(value)
  return props.lang==='ar' ? s.replace(/[0-9]/g, d=>digitsMap[Number(d)]) : s
}
function formatNumber(value, opts={}){ return new Intl.NumberFormat(locale.value, opts).format(value) }

onMounted(buildPuzzle)
watch(()=>props.lang, ()=>{ if(!solved.value) toast.value=null })
</script>

<template>
  <div class="lvl3c2 challenge-surface" :data-theme="props.theme">
    <header class="head">
      <h2 class="title">{{ copy[L].title }}</h2>
      <p class="rule">{{ copy[L].rule }}</p>
    </header>

    <section class="board">
      <div class="cards">
        <div v-for="card in cards" :key="card.id" class="card" :class="'color-' + card.color">
          <div class="drop" @dragover="allowDrop" @drop="onDrop($event, card.id)">
            <span v-if="answer[card.id] != null" class="num" :style="numDir">{{ formatDigit(answer[card.id]) }}</span>
            <span v-else class="placeholder">؟</span>
          </div>
          <input
            class="manual-entry" type="number" inputmode="numeric" :style="numDir"
            :value="manualDrafts[card.id] ?? ''"
            @input="onManualInput(card.id, $event.target.value)"
            @change="commitManual(card.id)" @blur="commitManual(card.id)"
            :placeholder="copy[L].manualPlaceholder"
          />
          <button class="clear" @click="clearCard(card.id)"><Eraser class="ic" /> {{ copy[L].clear }}</button>
        </div>
      </div>

      <aside class="facts">
        <h3>{{ props.lang==='ar' ? 'المعلومات المتاحة' : 'Given facts' }}</h3>
        <ul>
          <li><strong>{{ copy[L].hints.sum }}:</strong> <span :style="numDir">{{ formatNumber(hints.sum) }}</span></li>
          <li><strong>{{ copy[L].hints.mean }}:</strong> <span :style="numDir">{{ formatNumber(hints.mean,{maximumFractionDigits:2}) }}</span></li>
          <li><strong>{{ copy[L].hints.median }}:</strong> <span :style="numDir">{{ formatNumber(hints.median) }}</span></li>
          <li><strong>{{ copy[L].hints.range }}:</strong> <span :style="numDir">{{ formatNumber(hints.range) }}</span></li>
        </ul>
      </aside>
    </section>

    <section class="bank">
      <div class="bank-title">{{ copy[L].bank }}</div>
      <div class="bank-items">
        <button v-for="item in bankList" :key="item.key" class="chip"
                draggable="true" @dragstart="onDragStart($event, item.value)" :style="numDir">
          {{ formatDigit(item.value) }}
        </button>
      </div>
    </section>

    <section class="actions">
      <button class="btn" @click="resetAll"><RotateCcw class="ic" /> {{ copy[L].reset }}</button>
      <button class="btn" @click="checkNow"><Check class="ic" /> {{ copy[L].check }}</button>
      <button class="btn" @click="buildPuzzle"><RefreshCw class="ic" /> {{ copy[L].newQ }}</button>
    </section>

    <transition name="fade">
      <div v-if="toast" class="toast" :class="{ ok: solved }">{{ toast }}</div>
    </transition>
  </div>
</template>

<style scoped>
.lvl3c2{ --fg:#172554; --bg:#f6f7ff; --panel:#ffffff; --bd:#cbd5f5; --accent:#d64c42;
  color:var(--fg); background:var(--bg); padding:24px; border-radius:18px; box-shadow:0 12px 32px rgba(23,37,84,.08) }
[data-theme="dark"] .lvl3c2{ --fg:#e0e7ff; --bg:#0b1220; --panel:#111a2b; --bd:#1e293b }

.head{ margin-bottom:18px }
.title{ margin:0 0 8px; font-size:1.5rem; font-weight:700 }
.rule{ margin:0; opacity:.75; line-height:1.5 }

.board{ display:flex; flex-wrap:wrap; gap:24px; margin-bottom:24px }
.cards{ display:flex; flex-wrap:wrap; gap:16px; flex:2 }
.card{
  width:170px; min-height:170px; border-radius:18px; padding:16px; border:2px solid transparent;
  display:flex; flex-direction:column; gap:12px; background:var(--panel); box-shadow:0 10px 24px rgba(0,0,0,.08)
}
.drop{
  width:100%; height:80px; border:2px dashed rgba(15,23,42,.25); border-radius:12px;
  display:flex; align-items:center; justify-content:center; font-size:1.6rem; font-weight:700; color:var(--fg);
  background:rgba(255,255,255,.55)
}
[data-theme="dark"] .drop{ background:rgba(15,23,42,.45); border-color:rgba(226,232,240,.25) }
.drop:hover{ border-color:rgba(214,76,66,.45); box-shadow:0 0 0 4px rgba(214,76,66,.12) }
.placeholder{ opacity:.45 }
.num{ font-variant-numeric:tabular-nums }

.manual-entry{
  width:100%; padding:.45rem .6rem; border-radius:.6rem; border:1px solid rgba(148,163,184,.35);
  font-size:.95rem; background:rgba(255,255,255,.92); color:inherit
}
.manual-entry:focus{ outline:none; border-color:rgba(15,138,62,.45); box-shadow:0 0 0 3px rgba(15,138,62,.16) }
[data-theme="dark"] .manual-entry{ background:rgba(15,23,42,.8); border-color:rgba(148,163,184,.4); color:var(--fg) }

.clear{
  display:inline-flex; align-items:center; gap:6px; padding:6px 10px; border-radius:999px;
  border:1px solid rgba(15,23,42,.15); background:rgba(255,255,255,.8); cursor:pointer; font-size:.8rem
}
[data-theme="dark"] .clear{ background:rgba(30,41,59,.6); border-color:rgba(148,163,184,.35) }
.ic{ width:16px; height:16px }

.facts{
  flex:1; min-width:220px; background:var(--panel); border-radius:16px; padding:18px; border:1px solid var(--bd);
  box-shadow:0 8px 20px rgba(0,0,0,.05)
}
.facts h3{ margin:0 0 12px; font-size:1.05rem }
.facts ul{ list-style:none; padding:0; margin:0; display:grid; gap:8px }
.facts li{ display:flex; justify-content:space-between; gap:12px; font-variant-numeric:tabular-nums }

.bank{ background:var(--panel); border-radius:16px; padding:18px; border:1px solid var(--bd); margin-bottom:20px }
.bank-title{ font-weight:600; margin-bottom:12px }
.bank-items{ display:flex; gap:10px; flex-wrap:wrap }
.chip{
  padding:8px 14px; border-radius:999px; border:1px solid var(--bd); background:#fff; cursor:grab; font-weight:600;
  box-shadow:0 6px 16px rgba(15,23,42,.12)
}
[data-theme="dark"] .chip{ background:rgba(15,23,42,.6); border-color:rgba(148,163,184,.3) }
.chip:active{ cursor:grabbing }

.actions{ display:flex; flex-wrap:wrap; gap:12px }
.btn{
  display:inline-flex; align-items:center; gap:8px; padding:10px 18px; border-radius:12px;
  border:1px solid var(--bd); background:var(--panel); cursor:pointer; transition:.15s; font-weight:600
}
.btn:hover{ transform:translateY(-1px); box-shadow:0 10px 24px rgba(0,0,0,.08) }

.toast{
  margin-top:18px; padding:12px 18px; border-radius:12px; border:1px solid #fecaca;
  background:#fee2e2; color:#991b1b; font-weight:600; text-align:center
}
.toast.ok{ border-color:#bbf7d0; background:#dcfce7; color:#166534 }

.fade-enter-active,.fade-leave-active{ transition:opacity .2s }
.fade-enter-from,.fade-leave-to{ opacity:0 }

/* card colours */
.color-green{ border-color:#4ade80; background:linear-gradient(160deg,#bbf7d0,#f0fff4) }
.color-gold{ border-color:#facc15; background:linear-gradient(160deg,#fef08a,#fffbe6) }
.color-teal{ border-color:#2dd4bf; background:linear-gradient(160deg,#99f6e4,#ecfeff) }
.color-magenta{ border-color:#f472b6; background:linear-gradient(160deg,#fbcfe8,#fff0f8) }
.color-sky{ border-color:#38bdf8; background:linear-gradient(160deg,#bae6fd,#eff6ff) }
.color-orange{ border-color:#fb923c; background:linear-gradient(160deg,#ffd7aa,#fff7ed) }
.color-crimson{ border-color:#f87171; background:linear-gradient(160deg,#fecaca,#fff1f1) }

@media (max-width: 900px){
  .board{ flex-direction:column }
  .cards{ justify-content:center }
  .card{ width:140px }
}
</style>

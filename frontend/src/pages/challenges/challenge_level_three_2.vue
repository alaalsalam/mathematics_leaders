<!-- <script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{ type:String, default:'ar' }, theme:{ type:String, default:'light' } })

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

/* ===== sounds ===== */
import successUrl from '@/assets/sounds/success3.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong2.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

/* ===== data templates ===== */
const colourPalette = ['green','gold','teal','magenta','sky','orange','crimson']
const templates = [
  { numbers:[4,8,12,16,20] },
  { numbers:[5,9,11,13,22] },
  { numbers:[7,10,12,18,23] },
  { numbers:[6,8,15,19,22] },
  { numbers:[9,11,14,20,26] }
]

const EXTRA_CHOICES = 4

function computeHints(numbers){
  const sorted = numbers.slice().sort((a,b)=>a-b)
  const sum = sorted.reduce((acc,n)=>acc+n,0)
  const mean = sum / sorted.length
  const median = sorted[Math.floor(sorted.length/2)]
  const range = sorted[sorted.length-1] - sorted[0]
  return { sum, mean, median, range }
}

/* ===== state ===== */
const cards = ref([])                 // [{id,color,value}]
const solution = reactive({})         // id -> value
const blanks = ref(new Set())         // ids
const totalCounts = reactive({})      // value -> total copies (handles duplicates)
const extraCounts = reactive({})      // distractor values counts
const bankCounts = reactive({})       // value -> remaining copies
const answer = reactive({})           // id -> chosen value
const answerSource = reactive({})     // id -> 'bank' | 'manual'
const manualDrafts = reactive({})     // id -> string
const hints = ref({ sum:0, mean:0, median:0, range:0 })
const toast = ref(null)
const solved = ref(false)

function resetReactiveMap(obj){ for (const key of Object.keys(obj)) delete obj[key] }

function buildPuzzle(){
  const tpl = templates[Math.floor(Math.random()*templates.length)]
  const nums = tpl.numbers.slice()
  const colours = colourPalette.slice(0, nums.length)
  colours.sort(() => Math.random() - 0.5)
  const arrangement = nums.slice().sort(() => Math.random() - 0.5)

  cards.value = []
  blanks.value = new Set()
  resetReactiveMap(solution)
  resetReactiveMap(answer)
  resetReactiveMap(answerSource)
  resetReactiveMap(manualDrafts)
  resetReactiveMap(totalCounts)
  resetReactiveMap(extraCounts)
  resetReactiveMap(bankCounts)

  arrangement.forEach((value, idx) => {
    const id = `card-${idx}`
    cards.value.push({ id, value, color: colours[idx % colours.length] })
    solution[id] = value
    blanks.value.add(id)
    totalCounts[value] = (totalCounts[value] || 0) + 1
  })
  for (const [val, ct] of Object.entries(totalCounts)) {
    bankCounts[val] = ct
  }

  const minVal = Math.min(...nums)
  const maxVal = Math.max(...nums)
  const lower = Math.max(1, minVal - 12)
  const upper = maxVal + 12
  const extras = new Set()
  while(extras.size < EXTRA_CHOICES){
    const candidate = Math.floor(Math.random() * (upper - lower + 1)) + lower
    if(totalCounts[candidate]) continue
    extras.add(candidate)
  }
  extras.forEach(val => {
    extraCounts[val] = (extraCounts[val] || 0) + 1
    bankCounts[val] = (bankCounts[val] || 0) + 1
  })

  hints.value = computeHints(nums)
  toast.value = null
  solved.value = false
}

function onDragStart(ev, value){ ev.dataTransfer.setData('text/plain', String(value)) }
function allowDrop(ev){ ev.preventDefault() }

function setAnswer(cardId, value, source){
  if(Number.isNaN(value)) return false
  if(answer[cardId] != null && answerSource[cardId] === 'bank'){
    const prev = answer[cardId]
    bankCounts[prev] = (bankCounts[prev] || 0) + 1
  }

  if(source === 'bank'){
    if((bankCounts[value] || 0) <= 0) return false
    bankCounts[value] = (bankCounts[value] || 0) - 1
  }

  answer[cardId] = value
  answerSource[cardId] = source
  manualDrafts[cardId] = String(value)
  toast.value = null
  solved.value = false
  return true
}

function onDrop(ev, cardId){
  ev.preventDefault()
  const raw = ev.dataTransfer.getData('text/plain')
  const val = Number(raw)
  if(Number.isNaN(val)) return
  setAnswer(cardId, val, 'bank')
}

function clearCard(cardId){
  if(answer[cardId] != null && answerSource[cardId] === 'bank'){
    const prev = answer[cardId]
    bankCounts[prev] = (bankCounts[prev] || 0) + 1
  }
  delete answer[cardId]
  delete answerSource[cardId]
  manualDrafts[cardId] = ''
  toast.value = null
  solved.value = false
}

function isFilled(){
  for(const id of blanks.value){ if(answer[id] == null) return false }
  return true
}
// function isCorrect(){
//   for(const id of blanks.value){ if(answer[id] !== solution[id]) return false }
//   return true
// }

function isCorrect(){
  const counts = {}
  for (const id of blanks.value){
    const v = answer[id]
    if (v == null) return false
    counts[v] = (counts[v] || 0) + 1
  }
  for (const [v, ct] of Object.entries(totalCounts)){
    if ((counts[v] || 0) !== ct) return false
  }
  const need = Object.values(totalCounts).reduce((a,b)=>a+b,0)
  const have = Object.values(counts).reduce((a,b)=>a+b,0)
  return have === need
}


async function addPoint(){
  try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{}
}
async function checkNow(){
  if(!isFilled()){
    toast.value = L.value==='ar' ? 'أكمل كل البطاقات أولاً.' : 'Fill every card first.'
    sWrong && sWrong.play()
    return
  }
  if(isCorrect()){
    solved.value = true
    toast.value = copy[L.value].correct
    sOK && sOK.play(); sClap && sClap.play()
    await addPoint()
  } else {
    toast.value = copy[L.value].wrong
    sWrong && sWrong.play()
  }
}
function resetAll(){
  resetReactiveMap(answer)
  resetReactiveMap(answerSource)
  resetReactiveMap(manualDrafts)
  resetReactiveMap(bankCounts)
  for (const [val, ct] of Object.entries(totalCounts)) bankCounts[val] = ct
  for (const [val, ct] of Object.entries(extraCounts)) bankCounts[val] = (bankCounts[val] || 0) + ct
  toast.value = null
  solved.value = false
}

const bankList = computed(() => {
  const arr = []
  for(const [val, count] of Object.entries(bankCounts)){
    for(let i=0;i<count;i++) arr.push({ value:Number(val), key:`${val}-${i}` })
  }
  return arr
})

function onManualInput(cardId, value){ manualDrafts[cardId] = value }
function commitManual(cardId){
  const raw = (manualDrafts[cardId] ?? '').trim()
  if(raw === ''){ clearCard(cardId); return }
  const num = Number(raw)
  if(!Number.isFinite(num)) return
  setAnswer(cardId, num, 'manual')
}

const digitsMap = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩']
function formatDigit(value){
  const str = String(value)
  if(props.lang !== 'ar') return str
  return str.replace(/[0-9]/g, d => digitsMap[Number(d)])
}
function formatNumber(value, options={}){
  return new Intl.NumberFormat(locale.value, options).format(value)
}

onMounted(buildPuzzle)
watch(() => props.lang, () => { if(toast.value && solved.value) return; toast.value = null })
</script>

<template>
  <div class="lvl3c2 challenge-surface" :data-theme="props.theme">
    <header class="head">
      <h2 class="title">{{ copy[L].title }}</h2>
      <p class="rule">{{ copy[L].rule }}</p>
    </header>

    <section class="board">
      <div class="cards">
        <div
          v-for="card in cards"
          :key="card.id"
          class="card"
          :class="'color-' + card.color"
        >
          <div class="drop" @dragover="allowDrop" @drop="onDrop($event, card.id)">
            <span v-if="answer[card.id] != null" class="num">{{ formatDigit(answer[card.id]) }}</span>
            <span v-else class="placeholder">؟</span>
          </div>
          <input
            class="manual-entry"
            type="number"
            inputmode="numeric"
            :value="manualDrafts[card.id] ?? ''"
            @input="onManualInput(card.id, $event.target.value)"
            @change="commitManual(card.id)"
            @blur="commitManual(card.id)"
            :placeholder="copy[L].manualPlaceholder"
          />
          <button class="clear" @click="clearCard(card.id)"><Eraser class="ic" /> {{ copy[L].clear }}</button>
        </div>
      </div>

      <aside class="facts">
        <h3>{{ props.lang==='ar' ? 'المعلومات المتاحة' : 'Given facts' }}</h3>
        <ul>
          <li><strong>{{ copy[L].hints.sum }}:</strong> {{ formatNumber(hints.sum) }}</li>
          <li><strong>{{ copy[L].hints.mean }}:</strong> {{ formatNumber(hints.mean, { maximumFractionDigits:2 }) }}</li>
          <li><strong>{{ copy[L].hints.median }}:</strong> {{ formatNumber(hints.median) }}</li>
          <li><strong>{{ copy[L].hints.range }}:</strong> {{ formatNumber(hints.range) }}</li>
        </ul>
      </aside>
    </section>

    <section class="bank">
      <div class="bank-title">{{ copy[L].bank }}</div>
      <div class="bank-items">
        <button
          v-for="item in bankList"
          :key="item.key"
          class="chip"
          draggable="true"
          @dragstart="onDragStart($event, item.value)"
        >
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
[data-theme="dark"] .lvl3c2{ --fg:#e0e7ff; --bg:#0b1220; --panel:#111a2b; --bd:#1e293b; }

.head{ margin-bottom:18px }
.title{ margin:0 0 8px; font-size:1.5rem; font-weight:700 }
.rule{ margin:0; opacity:.75; line-height:1.5 }

.board{ display:flex; flex-wrap:wrap; gap:24px; margin-bottom:24px }
.cards{ display:flex; flex-wrap:wrap; gap:16px; flex:2 }
.card{ width:170px; min-height:170px; border-radius:18px; padding:16px; box-shadow:0 10px 24px rgba(0,0,0,.08);
  display:flex; flex-direction:column; align-items:stretch; gap:12px; border:2px solid transparent; background:var(--panel) }
.card .drop{ width:100%; height:80px; border:2px dashed rgba(15,23,42,.25); border-radius:12px;
  display:flex; align-items:center; justify-content:center; font-size:1.6rem; font-weight:700; color:var(--fg);
  background:rgba(255,255,255,.55) }
[data-theme="dark"] .card .drop{ background:rgba(15,23,42,.45); border-color:rgba(226,232,240,.25) }
.card .drop:hover{ border-color:rgba(214,76,66,.45); box-shadow:0 0 0 4px rgba(214,76,66,.12) }
.placeholder{ opacity:.45 }
.manual-entry{ width:100%; padding:.45rem .6rem; border-radius:.6rem; border:1px solid rgba(148,163,184,.35); font-size:.95rem; background:rgba(255,255,255,.92); color:inherit; direction:ltr }
.manual-entry:focus{ outline:none; border-color:rgba(15,138,62,.45); box-shadow:0 0 0 3px rgba(15,138,62,.16) }
[data-theme="dark"] .manual-entry{ background:rgba(15,23,42,.8); border-color:rgba(148,163,184,.4); color:var(--fg) }
.clear{ display:inline-flex; align-items:center; gap:6px; padding:6px 10px; border-radius:999px;
  border:1px solid rgba(15,23,42,.15); background:rgba(255,255,255,.8); cursor:pointer; font-size:.8rem }
[data-theme="dark"] .clear{ background:rgba(30,41,59,.6); border-color:rgba(148,163,184,.35) }
.ic{ width:16px; height:16px }

.facts{ flex:1; min-width:220px; background:var(--panel); border-radius:16px; padding:18px; border:1px solid var(--bd);
  box-shadow:0 8px 20px rgba(0,0,0,.05) }
.facts h3{ margin:0 0 12px; font-size:1.05rem }
.facts ul{ list-style:none; padding:0; margin:0; display:grid; gap:8px }
.facts li{ display:flex; justify-content:space-between; gap:12px; font-variant-numeric:tabular-nums }

.bank{ background:var(--panel); border-radius:16px; padding:18px; border:1px solid var(--bd); margin-bottom:20px }
.bank-title{ font-weight:600; margin-bottom:12px }
.bank-items{ display:flex; gap:10px; flex-wrap:wrap }
.chip{ padding:8px 14px; border-radius:999px; border:1px solid var(--bd); background:#fff; cursor:grab; font-weight:600;
  box-shadow:0 6px 16px rgba(15,23,42,.12) }
[data-theme="dark"] .chip{ background:rgba(15,23,42,.6); border-color:rgba(148,163,184,.3) }
.chip:active{ cursor:grabbing }

.actions{ display:flex; flex-wrap:wrap; gap:12px }
.btn{ display:inline-flex; align-items:center; gap:8px; padding:10px 18px; border-radius:12px; border:1px solid var(--bd);
  background:var(--panel); cursor:pointer; transition:.15s; font-weight:600 }
.btn:hover{ transform:translateY(-1px); box-shadow:0 10px 24px rgba(0,0,0,.08) }

.toast{ margin-top:18px; padding:12px 18px; border-radius:12px; border:1px solid #fecaca; background:#fee2e2; color:#991b1b;
  font-weight:600; text-align:center }
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
</style> -->

<script setup>
/* =========================================================
   Level 3 — Challenge 2: Missing numbers on the cards
   Dark-mode pass: stronger contrast, clearer borders/tints,
   and consistent surfaces across light/dark.
   ---------------------------------------------------------
   Notes:
   - Theme tokens drive all colors (see CSS variables below).
   - Drop areas get a visible dashed border + subtle tint in dark.
   - Coloured cards have dark-friendly gradients (no washed-out tones).
   - Inputs, chips, and buttons use panel tokens for clear contrast.
========================================================= */

import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{ type:String, default:'ar' }, theme:{ type:String, default:'light' } })

/* ---------- copy ---------- */
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

/* ---------- sounds (optional) ---------- */
import successUrl from '@/assets/sounds/success3.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong2.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK&&(sOK.preload='auto'); sClap&&(sClap.preload='auto'); sWrong&&(sWrong.preload='auto')

/* ---------- data templates ---------- */
const colourPalette = ['green','gold','teal','magenta','sky','orange','crimson']
const templates = [
  { numbers:[4,8,12,16,20] },
  { numbers:[5,9,11,13,22] },
  { numbers:[7,10,12,18,23] },
  { numbers:[6,8,15,19,22] },
  { numbers:[9,11,14,20,26] }
]

const EXTRA_CHOICES = 4

/* Basic stats for the “Given facts” box */
function computeHints(numbers){
  const sorted = numbers.slice().sort((a,b)=>a-b)
  const sum = sorted.reduce((acc,n)=>acc+n,0)
  const mean = sum / sorted.length
  const median = sorted[Math.floor(sorted.length/2)]
  const range = sorted[sorted.length-1] - sorted[0]
  return { sum, mean, median, range }
}

/* ---------- state ---------- */
const cards = ref([])                 // [{id,color,value}]
const solution = reactive({})         // id -> value
const blanks = ref(new Set())         // ids
const totalCounts = reactive({})      // correct value -> total copies (supports duplicates)
const extraCounts = reactive({})      // distractor value -> count
const bankCounts  = reactive({})      // value -> remaining copies (correct + extras)
const answer = reactive({})           // id -> chosen value
const answerSource = reactive({})     // id -> 'bank' | 'manual'
const manualDrafts = reactive({})     // id -> input string
const hints = ref({ sum:0, mean:0, median:0, range:0 })
const toast = ref(null)
const solved = ref(false)

/* Convenience: wipe a reactive map in-place */
function resetReactiveMap(obj){ for (const key of Object.keys(obj)) delete obj[key] }

/* Build one puzzle instance */
function buildPuzzle(){
  const tpl = templates[Math.floor(Math.random()*templates.length)]
  const nums = tpl.numbers.slice()

  // Shuffle both colours and the card arrangement
  const colours = colourPalette.slice(0, nums.length).sort(() => Math.random() - 0.5)
  const arrangement = nums.slice().sort(() => Math.random() - 0.5)

  // Reset everything
  cards.value = []
  blanks.value = new Set()
  resetReactiveMap(solution); resetReactiveMap(answer); resetReactiveMap(answerSource)
  resetReactiveMap(manualDrafts); resetReactiveMap(totalCounts); resetReactiveMap(extraCounts); resetReactiveMap(bankCounts)

  // Make coloured cards and tally correct counts
  arrangement.forEach((value, idx) => {
    const id = `card-${idx}`
    cards.value.push({ id, value, color: colours[idx % colours.length] })
    solution[id] = value
    blanks.value.add(id)
    totalCounts[value] = (totalCounts[value] || 0) + 1
  })
  // Start bank with required counts
  for (const [val, ct] of Object.entries(totalCounts)) bankCounts[val] = ct

  // Add a few plausible distractors (do not overlap with required values)
  const minVal = Math.min(...nums), maxVal = Math.max(...nums)
  const lower = Math.max(1, minVal - 12), upper = maxVal + 12
  const extras = new Set()
  while(extras.size < EXTRA_CHOICES){
    const candidate = Math.floor(Math.random() * (upper - lower + 1)) + lower
    if(totalCounts[candidate]) continue
    extras.add(candidate)
  }
  extras.forEach(val => {
    extraCounts[val] = (extraCounts[val] || 0) + 1
    bankCounts[val] = (bankCounts[val] || 0) + 1
  })

  // Facts box
  hints.value = computeHints(nums)
  toast.value = null
  solved.value = false
}

/* DnD helpers (with quantity book-keeping) */
function onDragStart(ev, value){ ev.dataTransfer.setData('text/plain', String(value)) }
function allowDrop(ev){ ev.preventDefault() }

function setAnswer(cardId, value, source){
  if(Number.isNaN(value)) return false

  // Return to bank if previous came from bank
  if(answer[cardId] != null && answerSource[cardId] === 'bank'){
    const prev = answer[cardId]
    bankCounts[prev] = (bankCounts[prev] || 0) + 1
  }

  // Consume from bank when dragging
  if(source === 'bank'){
    if((bankCounts[value] || 0) <= 0) return false
    bankCounts[value] = (bankCounts[value] || 0) - 1
  }

  answer[cardId] = value
  answerSource[cardId] = source
  manualDrafts[cardId] = String(value)
  toast.value = null
  solved.value = false
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

/* Validation — compare multiset of chosen values to required multiset */
function isFilled(){ for(const id of blanks.value){ if(answer[id] == null) return false } return true }
function isCorrect(){
  const counts = {}
  for (const id of blanks.value){
    const v = answer[id]
    if (v == null) return false
    counts[v] = (counts[v] || 0) + 1
  }
  for (const [v, ct] of Object.entries(totalCounts)){
    if ((counts[v] || 0) !== ct) return false
  }
  return true
}

/* Evaluate */
async function addPoint(){
  try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{}
}
async function checkNow(){
  if(!isFilled()){
    toast.value = L.value==='ar' ? 'أكمل كل البطاقات أولاً.' : 'Fill every card first.'
    sWrong && sWrong.play(); return
  }
  if(isCorrect()){
    solved.value = true
    toast.value = copy[L.value].correct
    sOK && sOK.play(); sClap && sClap.play()
    await addPoint()
  }else{
    toast.value = copy[L.value].wrong
    sWrong && sWrong.play()
  }
}

/* Reset to initial bank state without changing puzzle */
function resetAll(){
  resetReactiveMap(answer); resetReactiveMap(answerSource); resetReactiveMap(manualDrafts); resetReactiveMap(bankCounts)
  for (const [val, ct] of Object.entries(totalCounts)) bankCounts[val] = ct
  for (const [val, ct] of Object.entries(extraCounts)) bankCounts[val] = (bankCounts[val] || 0) + ct
  toast.value = null; solved.value = false
}

/* Bank list as a flat array for v-for */
const bankList = computed(() => {
  const arr = []
  for(const [val, count] of Object.entries(bankCounts)){
    for(let i=0;i<count;i++) arr.push({ value:Number(val), key:`${val}-${i}` })
  }
  return arr
})

/* Manual typing path (respects bank quantities only when dragged) */
function onManualInput(cardId, value){ manualDrafts[cardId] = value }
function commitManual(cardId){
  const raw = (manualDrafts[cardId] ?? '').trim()
  if(raw === ''){ clearCard(cardId); return }
  const num = Number(raw)
  if(!Number.isFinite(num)) return
  setAnswer(cardId, num, 'manual')
}

/* Localised number formatting helpers */
const digitsMap = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩']
function formatDigit(value){
  const str = String(value)
  if(props.lang !== 'ar') return str
  return str.replace(/[0-9]/g, d => digitsMap[Number(d)])
}
function formatNumber(value, options={}){ return new Intl.NumberFormat(locale.value, options).format(value) }

onMounted(buildPuzzle)
watch(() => props.lang, () => { if(toast.value && solved.value) return; toast.value = null })
</script>

<template>
  <div class="lvl3c2 challenge-surface" :data-theme="props.theme">
    <header class="head">
      <h2 class="title">{{ copy[L].title }}</h2>
      <p class="rule">{{ copy[L].rule }}</p>
    </header>

    <section class="board">
      <div class="cards">
        <div
          v-for="card in cards"
          :key="card.id"
          class="card"
          :class="'color-' + card.color"
        >
          <div class="drop" @dragover="allowDrop" @drop="onDrop($event, card.id)">
            <span v-if="answer[card.id] != null" class="num">{{ formatDigit(answer[card.id]) }}</span>
            <span v-else class="placeholder">؟</span>
          </div>

          <input
            class="manual-entry"
            type="number"
            inputmode="numeric"
            :value="manualDrafts[card.id] ?? ''"
            @input="onManualInput(card.id, $event.target.value)"
            @change="commitManual(card.id)"
            @blur="commitManual(card.id)"
            :placeholder="copy[L].manualPlaceholder"
          />

          <button class="clear" @click="clearCard(card.id)">
            <Eraser class="ic" /> {{ copy[L].clear }}
          </button>
        </div>
      </div>

      <aside class="facts">
        <h3>{{ props.lang==='ar' ? 'المعلومات المتاحة' : 'Given facts' }}</h3>
        <ul>
          <li><strong>{{ copy[L].hints.sum }}:</strong> {{ formatNumber(hints.sum) }}</li>
          <li><strong>{{ copy[L].hints.mean }}:</strong> {{ formatNumber(hints.mean, { maximumFractionDigits:2 }) }}</li>
          <li><strong>{{ copy[L].hints.median }}:</strong> {{ formatNumber(hints.median) }}</li>
          <li><strong>{{ copy[L].hints.range }}:</strong> {{ formatNumber(hints.range) }}</li>
        </ul>
      </aside>
    </section>

    <section class="bank">
      <div class="bank-title">{{ copy[L].bank }}</div>
      <div class="bank-items">
        <button
          v-for="item in bankList"
          :key="item.key"
          class="chip"
          draggable="true"
          @dragstart="onDragStart($event, item.value)"
        >
          {{ formatDigit(item.value) }}
        </button>
      </div>
    </section>

    <section class="actions">
      <button class="btn" @click="resetAll"><RotateCcw class="ic" /> {{ copy[L].reset }}</button>
      <button class="btn primary" @click="checkNow"><Check class="ic" /> {{ copy[L].check }}</button>
      <button class="btn" @click="buildPuzzle"><RefreshCw class="ic" /> {{ copy[L].newQ }}</button>
    </section>

    <transition name="fade">
      <div v-if="toast" class="toast" :class="{ ok: solved }">{{ toast }}</div>
    </transition>
  </div>
</template>

<style scoped>
/* =========================
   Theme tokens
   (Everything reads from these; dark-mode overrides below)
========================= */
.lvl3c2{
  --fg:#172554;
  --muted:#475569;
  --bg:#f6f7ff;

  --panel:#ffffff;
  --panel-bd:#cbd5f5;
  --shadow:0 12px 32px rgba(23,37,84,.08);

  --drop-bg:rgba(15,23,42,.04);
  --drop-bd:rgba(15,23,42,.28);

  --chip-bg:#ffffff;
  --chip-bd:#cbd5f5;

  --btn-bg:#ffffff;
  --btn-bd:#cbd5f5;
  --btn-fg:#172554;
  --btn-primary-bg:#0ea5e9;
  --btn-primary-fg:#ffffff;

  --toast-err-bg:#fee2e2; --toast-err-fg:#991b1b; --toast-err-bd:#fecaca;
  --toast-ok-bg:#dcfce7;  --toast-ok-fg:#166534;  --toast-ok-bd:#bbf7d0;

  color:var(--fg);
  background:var(--bg);
  padding:24px; border-radius:18px; box-shadow:var(--shadow);
}

/* Dark mode: higher contrast panels, tints, and borders */
[data-theme="dark"] .lvl3c2{
  --fg:#e5e7eb;
  --muted:#9ca3af;
  --bg:#0b1220;

  --panel:#0f172a;
  --panel-bd:#334155;
  --shadow:0 14px 36px rgba(0,0,0,.55);

  --drop-bg:rgba(99,102,241,.18);   /* indigo tint clearly visible */
  --drop-bd:#64748b;

  --chip-bg:#111827;
  --chip-bd:#475569;

  --btn-bg:#111827;
  --btn-bd:#475569;
  --btn-fg:#e5e7eb;
  --btn-primary-bg:#38bdf8;
  --btn-primary-fg:#0b1220;

  --toast-err-bg:rgba(248,113,113,.16); --toast-err-fg:#fecaca; --toast-err-bd:rgba(248,113,113,.45);
  --toast-ok-bg:rgba(34,197,94,.22);    --toast-ok-fg:#bbf7d0;  --toast-ok-bd:rgba(34,197,94,.5);
}

/* =========================
   Header
========================= */
.head{ margin-bottom:18px }
.title{ margin:0 0 8px; font-size:1.5rem; font-weight:800 }
.rule{ margin:0; color:var(--muted); line-height:1.5 }

/* =========================
   Layout
========================= */
.board{ display:flex; flex-wrap:wrap; gap:24px; margin-bottom:24px }
.cards{ display:flex; flex-wrap:wrap; gap:16px; flex:2 }
.facts{
  flex:1; min-width:220px; background:var(--panel); border-radius:16px; padding:18px; border:1px solid var(--panel-bd);
  box-shadow:0 8px 20px rgba(0,0,0,.08)
}
.facts h3{ margin:0 0 12px; font-size:1.05rem }
.facts ul{ list-style:none; padding:0; margin:0; display:grid; gap:8px }
.facts li{ display:flex; justify-content:space-between; gap:12px; font-variant-numeric:tabular-nums; color:var(--fg) }

/* =========================
   Cards & drop areas
========================= */
.card{
  width:170px; min-height:170px;
  border-radius:18px; padding:16px;
  display:flex; flex-direction:column; gap:12px;
  background:var(--panel); border:2px solid transparent;
  box-shadow:0 10px 24px rgba(0,0,0,.10)
}
.card .drop{
  width:100%; height:80px; border:2px dashed var(--drop-bd);
  border-radius:12px; display:flex; align-items:center; justify-content:center;
  background:var(--drop-bg); color:var(--fg);
  transition: box-shadow .15s, border-color .15s
}
.card .drop:hover{ border-color:rgba(56,189,248,.55); box-shadow:0 0 0 4px rgba(56,189,248,.20) inset }
.placeholder{ opacity:.55 }

/* Keep digits LTR even in Arabic UI */
.num, .manual-entry{ direction:ltr; unicode-bidi:isolate }

/* Inputs */
.manual-entry{
  width:100%; padding:.45rem .6rem; border-radius:.6rem;
  border:1px solid var(--panel-bd); font-size:.95rem;
  background:var(--panel); color:var(--fg)
}
.manual-entry:focus{ outline:none; border-color:#22c55e; box-shadow:0 0 0 3px rgba(34,197,94,.18) }

/* Clear button on card */
.clear{
  display:inline-flex; align-items:center; gap:6px; padding:6px 10px; border-radius:999px;
  border:1px solid var(--panel-bd); background:var(--panel); color:var(--fg); cursor:pointer; font-size:.8rem
}
.ic{ width:16px; height:16px }

/* =========================
   Bank
========================= */
.bank{ background:var(--panel); border-radius:16px; padding:18px; border:1px solid var(--panel-bd); margin-bottom:20px }
.bank-title{ font-weight:700; margin-bottom:12px; color:var(--muted) }
.bank-items{ display:flex; gap:10px; flex-wrap:wrap }
.chip{
  padding:8px 14px; border-radius:999px; border:1px solid var(--chip-bd); background:var(--chip-bg); color:var(--fg);
  cursor:grab; font-weight:700; box-shadow:0 6px 16px rgba(0,0,0,.12); min-width:44px; text-align:center
}
.chip:active{ cursor:grabbing }

/* =========================
   Actions / toasts
========================= */
.actions{ display:flex; flex-wrap:wrap; gap:12px }
.btn{
  display:inline-flex; align-items:center; gap:8px;
  padding:10px 18px; border-radius:12px;
  border:1px solid var(--btn-bd); background:var(--btn-bg); color:var(--btn-fg);
  cursor:pointer; transition:.15s; font-weight:700
}
.btn:hover{ transform:translateY(-1px); box-shadow:0 10px 24px rgba(0,0,0,.14) }
.btn.primary{ background:var(--btn-primary-bg); color:var(--btn-primary-fg); border-color:transparent }

.toast{
  margin-top:18px; padding:12px 18px; border-radius:12px; text-align:center; font-weight:800;
  border:1px solid var(--toast-err-bd); background:var(--toast-err-bg); color:var(--toast-err-fg)
}
.toast.ok{ border-color:var(--toast-ok-bd); background:var(--toast-ok-bg); color:var(--toast-ok-fg) }

.fade-enter-active,.fade-leave-active{ transition:opacity .2s }
.fade-enter-from,.fade-leave-to{ opacity:0 }

/* =========================
   Card colour frames (light) + dark variants
========================= */
.color-green{ border-color:#4ade80; background:linear-gradient(160deg,rgba(34,197,94,.18), var(--panel)) }
.color-gold{ border-color:#facc15; background:linear-gradient(160deg,rgba(250,204,21,.22), var(--panel)) }
.color-teal{ border-color:#2dd4bf; background:linear-gradient(160deg,rgba(45,212,191,.18), var(--panel)) }
.color-magenta{ border-color:#f472b6; background:linear-gradient(160deg,rgba(244,114,182,.18), var(--panel)) }
.color-sky{ border-color:#38bdf8; background:linear-gradient(160deg,rgba(56,189,248,.20), var(--panel)) }
.color-orange{ border-color:#fb923c; background:linear-gradient(160deg,rgba(251,146,60,.20), var(--panel)) }
.color-crimson{ border-color:#f87171; background:linear-gradient(160deg,rgba(248,113,113,.20), var(--panel)) }

[data-theme="dark"] .lvl3c2 .color-green{ border-color:#22c55e; background:linear-gradient(160deg,rgba(22,163,74,.28), var(--panel)) }
[data-theme="dark"] .lvl3c2 .color-gold{ border-color:#eab308; background:linear-gradient(160deg,rgba(202,138,4,.28), var(--panel)) }
[data-theme="dark"] .lvl3c2 .color-teal{ border-color:#14b8a6; background:linear-gradient(160deg,rgba(13,148,136,.30), var(--panel)) }
[data-theme="dark"] .lvl3c2 .color-magenta{ border-color:#e879f9; background:linear-gradient(160deg,rgba(217,70,239,.28), var(--panel)) }
[data-theme="dark"] .lvl3c2 .color-sky{ border-color:#38bdf8; background:linear-gradient(160deg,rgba(56,189,248,.28), var(--panel)) }
[data-theme="dark"] .lvl3c2 .color-orange{ border-color:#f59e0b; background:linear-gradient(160deg,rgba(234,88,12,.30), var(--panel)) }
[data-theme="dark"] .lvl3c2 .color-crimson{ border-color:#f87171; background:linear-gradient(160deg,rgba(239,68,68,.30), var(--panel)) }

@media (max-width: 900px){
  .board{ flex-direction:column }
  .cards{ justify-content:center }
  .card{ width:150px }
}
</style>

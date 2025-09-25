<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{ type:String, default:'ar' }, theme:{ type:String, default:'light' } })

const copy = {
  ar:{
    title:'المستوى الثالث – التحدي 6: كسور مكافئة',
    intro:'اسحب الأرقام المتاحة وضعها في الخانات بحيث يكون الكسر الاعتيادي مساويًا للقيمة العشرية المعطاة.',
    decimals:'القيمة العشرية', fraction:'الكسر المكافئ', bank:'البطاقات المتاحة',
    check:'تحقّق', reset:'مسح', newQ:'تحدٍ جديد', clear:'تفريغ',
    needAll:'املأ كل الخانات أولًا.', wrong:'القيم غير متكافئة، حاول ترتيبًا مختلفًا.', correct:'أحسنت! الكسور مكافئة.'
  },
  en:{
    title:'Level 3 – Challenge 6: Equivalent Fractions',
    intro:'Drag the available digits into the slots so the fraction equals the given decimal value.',
    decimals:'Decimal value', fraction:'Equivalent fraction', bank:'Available cards',
    check:'Check', reset:'Clear', newQ:'New challenge', clear:'Clear',
    needAll:'Fill every slot first.', wrong:'Values are not equivalent. Try another arrangement.', correct:'Great! They are equivalent.'
  }
}
const L = computed(() => (copy[props.lang] ? props.lang : 'ar'))

import successUrl from '@/assets/sounds/success2.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong2.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

const puzzles = [
  {
    id:'p1',
    decimal:{ slots:['dec1','dec2'], digits:['2','5'] }, // 0.25
    fraction:{ num:{ slots:['num1'], digits:['1'] }, den:{ slots:['den1'], digits:['4'] } },
    digits:['1','2','4','5']
  },
  {
    id:'p2',
    decimal:{ slots:['dec1','dec2'], digits:['7','5'] }, // 0.75
    fraction:{ num:{ slots:['num1'], digits:['3'] }, den:{ slots:['den1'], digits:['4'] } },
    digits:['3','4','5','7']
  },
  {
    id:'p3',
    decimal:{ slots:['dec1'], digits:['6'] }, // 0.6
    fraction:{ num:{ slots:['num1'], digits:['3'] }, den:{ slots:['den1'], digits:['5'] } },
    digits:['3','5','6']
  },
  {
    id:'p4',
    decimal:{ slots:['dec1','dec2'], digits:['3','3'] }, // 0.33 -> 1/3
    fraction:{ num:{ slots:['num1'], digits:['1'] }, den:{ slots:['den1'], digits:['3'] } },
    digits:['1','3']
  }
]

const currentPuzzle = ref(puzzles[0])
const placements = reactive({})
const requirements = reactive({})
const bankCounts = reactive({})
const feedback = ref(null)
const solved = ref(false)

function resetMaps(){
  Object.keys(placements).forEach(k => delete placements[k])
  Object.keys(requirements).forEach(k => delete requirements[k])
  Object.keys(bankCounts).forEach(k => delete bankCounts[k])
}

function initPuzzle(){
  const puzzle = puzzles[Math.floor(Math.random() * puzzles.length)]
  currentPuzzle.value = puzzle
  resetMaps()
  feedback.value = null
  solved.value = false

  // build slots and requirements
  const { decimal, fraction } = puzzle
  decimal.slots.forEach((slot, idx) => {
    placements[slot] = null
    requirements[slot] = decimal.digits[idx]
  })
  fraction.num.slots.forEach((slot, idx) => {
    placements[slot] = null
    requirements[slot] = fraction.num.digits[idx]
  })
  fraction.den.slots.forEach((slot, idx) => {
    placements[slot] = null
    requirements[slot] = fraction.den.digits[idx]
  })

  puzzle.digits.forEach(d => {
    bankCounts[d] = (bankCounts[d] || 0) + 1
  })
}

function allowDrop(ev){ ev.preventDefault() }
function onDragStart(ev, digit){ ev.dataTransfer.setData('text/plain', digit) }

function onDrop(ev, slot){
  ev.preventDefault()
  const digit = ev.dataTransfer.getData('text/plain')
  if(!digit) return
  if((bankCounts[digit] || 0) <= 0 && placements[slot] !== digit) return

  if(placements[slot] != null){
    const prev = placements[slot]
    bankCounts[prev] = (bankCounts[prev] || 0) + 1
  }

  if(placements[slot] !== digit){
    bankCounts[digit] = (bankCounts[digit] || 0) - 1
    if(bankCounts[digit] < 0) bankCounts[digit] = 0
  }

  placements[slot] = digit
  solved.value = false
  feedback.value = null
}

function clearSlot(slot){
  if(placements[slot] != null){
    const digit = placements[slot]
    bankCounts[digit] = (bankCounts[digit] || 0) + 1
    placements[slot] = null
    solved.value = false
    feedback.value = null
  }
}

const bankList = computed(()=>{
  const list=[]
  for(const [digit,count] of Object.entries(bankCounts)){
    for(let i=0;i<count;i++) list.push({ digit, key:`${digit}-${i}` })
  }
  return list
})

function slotsFilled(){
  return Object.keys(requirements).every(key => placements[key] != null)
}

function decimalValue(){
  const digits = currentPuzzle.value.decimal.slots.map(slot => placements[slot])
  const decimalPart = digits.join('')
  return Number(`0.${decimalPart}`)
}

function fractionValue(){
  const { fraction } = currentPuzzle.value
  const numDigits = fraction.num.slots.map(slot => placements[slot]).join('')
  const denDigits = fraction.den.slots.map(slot => placements[slot]).join('')
  const numerator = Number(numDigits)
  const denominator = Number(denDigits)
  if(!denominator) return null
  return numerator / denominator
}

async function addPoint(){
  try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{ method:'GET', credentials:'include' }) }catch{}
}

async function checkSolution(){
  if(!slotsFilled()){
    feedback.value = copy[L.value].needAll
    sWrong && sWrong.play()
    return
  }
  const dec = decimalValue()
  const frac = fractionValue()
  if(frac == null){
    feedback.value = copy[L.value].wrong
    sWrong && sWrong.play()
    return
  }
  if(Math.abs(dec - frac) < 1e-6){
    feedback.value = copy[L.value].correct
    solved.value = true
    sOK && sOK.play(); sClap && sClap.play()
    await addPoint()
  }else{
    feedback.value = copy[L.value].wrong
    sWrong && sWrong.play()
  }
}

function resetSelection(){
  Object.keys(placements).forEach(slot => {
    if(placements[slot] != null){
      const digit = placements[slot]
      bankCounts[digit] = (bankCounts[digit] || 0) + 1
      placements[slot] = null
    }
  })
  solved.value = false
  feedback.value = null
}

onMounted(initPuzzle)
watch(() => props.lang, () => { if(!solved.value) feedback.value = null })
</script>

<template>
  <div class="lvl3c6 challenge-surface" :data-theme="props.theme">
    <header class="head">
      <h2 class="title">{{ copy[L].title }}</h2>
      <p class="intro">{{ copy[L].intro }}</p>
    </header>

    <section class="problem">
      <div class="decimal-card">
        <div class="label">{{ copy[L].decimals }}</div>
        <div class="decimal-display">
          <span class="fixed">0.</span>
          <div class="slots">
            <div
              v-for="slot in currentPuzzle.decimal.slots"
              :key="slot"
              class="slot"
              @dragover="allowDrop"
              @drop="onDrop($event, slot)"
            >
              <span v-if="placements[slot]" class="digit">{{ placements[slot] }}</span>
              <span v-else class="placeholder">?</span>
              <button class="clear" @click="clearSlot(slot)"><Eraser class="ic" /> {{ copy[L].clear }}</button>
            </div>
          </div>
        </div>
      </div>

      <span class="equals">=</span>

      <div class="fraction-card">
        <div class="label">{{ copy[L].fraction }}</div>
        <div class="fraction">
          <div class="row">
            <div
              v-for="slot in currentPuzzle.fraction.num.slots"
              :key="slot"
              class="slot"
              @dragover="allowDrop"
              @drop="onDrop($event, slot)"
            >
              <span v-if="placements[slot]" class="digit">{{ placements[slot] }}</span>
              <span v-else class="placeholder">?</span>
              <button class="clear" @click="clearSlot(slot)"><Eraser class="ic" /> {{ copy[L].clear }}</button>
            </div>
          </div>
          <div class="bar"></div>
          <div class="row">
            <div
              v-for="slot in currentPuzzle.fraction.den.slots"
              :key="slot"
              class="slot"
              @dragover="allowDrop"
              @drop="onDrop($event, slot)"
            >
              <span v-if="placements[slot]" class="digit">{{ placements[slot] }}</span>
              <span v-else class="placeholder">?</span>
              <button class="clear" @click="clearSlot(slot)"><Eraser class="ic" /> {{ copy[L].clear }}</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="controls">
      <button class="btn" @click="checkSolution"><Check class="ic" /> {{ copy[L].check }}</button>
      <button class="btn" @click="resetSelection"><RotateCcw class="ic" /> {{ copy[L].reset }}</button>
      <button class="btn" @click="initPuzzle"><RefreshCw class="ic" /> {{ copy[L].newQ }}</button>
    </section>

    <section class="bank">
      <div class="bank-title">{{ copy[L].bank }}</div>
      <div class="bank-items">
        <button
          v-for="item in bankList"
          :key="item.key"
          class="chip"
          draggable="true"
          @dragstart="onDragStart($event, item.digit)"
        >
          {{ item.digit }}
        </button>
      </div>
    </section>

    <transition name="fade">
      <div v-if="feedback" class="feedback" :class="{ ok: solved }">{{ feedback }}</div>
    </transition>
  </div>
</template>

<style scoped>
.lvl3c6{ --fg:#1f2937; --bg:#f8fafc; --panel:#ffffff; --bd:#c4d4f8; --accent:#2563eb;
  padding:24px; border-radius:18px; background:var(--bg); color:var(--fg); box-shadow:0 14px 32px rgba(37,99,235,.12) }
[data-theme="dark"] .lvl3c6{ --fg:#e2e8f0; --bg:#0f172a; --panel:#111c34; --bd:#1e3a8a; --accent:#60a5fa }

.head{ margin-bottom:20px }
.title{ margin:0 0 10px; font-size:1.55rem; font-weight:700 }
.intro{ margin:0; line-height:1.5; opacity:.85 }

.problem{ display:flex; align-items:center; justify-content:center; gap:24px; flex-wrap:wrap; margin-bottom:22px }
.decimal-card, .fraction-card{ background:var(--panel); border:1px solid var(--bd); border-radius:16px; padding:16px 20px; box-shadow:0 12px 28px rgba(15,23,42,.08); min-width:220px }
.label{ font-weight:700; margin-bottom:12px; text-align:center }
.decimal-display{ display:flex; align-items:center; gap:10px; justify-content:center }
.fixed{ font-size:1.5rem; font-weight:700 }
.slots{ display:flex; gap:10px }
.slot{ min-width:46px; min-height:54px; border-radius:12px; border:2px dashed rgba(37,99,235,.35); display:flex; align-items:center; justify-content:center; position:relative; background:rgba(191,219,254,.35) }
.placeholder{ font-size:1.5rem; color:var(--accent); opacity:.75 }
.digit{ font-size:1.45rem; font-weight:700 }
.clear{ position:absolute; bottom:-30px; left:50%; transform:translateX(-50%); background:transparent; border:none; color:var(--accent); cursor:pointer; font-size:.75rem; display:flex; align-items:center; gap:4px }
.ic{ width:16px; height:16px }

.fraction{ display:flex; flex-direction:column; gap:12px; align-items:center }
.row{ display:flex; gap:10px }
.bar{ width:100%; height:3px; background:var(--accent); border-radius:999px }
.equals{ font-size:1.8rem; font-weight:700; color:var(--accent) }

.controls{ display:flex; gap:12px; flex-wrap:wrap; justify-content:center; margin-bottom:18px }
.btn{ display:inline-flex; align-items:center; gap:8px; padding:10px 18px; border-radius:12px; border:1px solid var(--bd); background:var(--panel); font-weight:700; cursor:pointer; transition:.15s }
.btn:hover{ transform:translateY(-1px); box-shadow:0 12px 24px rgba(15,23,42,.12) }

.bank{ background:var(--panel); border:1px solid var(--bd); border-radius:16px; padding:18px; box-shadow:0 12px 24px rgba(15,23,42,.08) }
.bank-title{ font-weight:700; margin-bottom:12px }
.bank-items{ display:flex; flex-wrap:wrap; gap:10px }
.chip{ padding:9px 14px; border-radius:12px; border:1px solid var(--bd); background:rgba(191,219,254,.45); font-weight:700; cursor:grab; transition:.15s }
.chip:active{ cursor:grabbing }

.feedback{ margin-top:20px; padding:12px 18px; border-radius:12px; border:1px solid #fecaca; background:#fee2e2; color:#b91c1c; font-weight:700; text-align:center }
.feedback.ok{ border-color:#bbf7d0; background:#dcfce7; color:#166534 }
[data-theme="dark"] .feedback{ background:rgba(248,113,113,.18); border-color:rgba(248,113,113,.45); color:#fecaca }
[data-theme="dark"] .feedback.ok{ background:rgba(34,197,94,.22); border-color:rgba(34,197,94,.5); color:#bbf7d0 }

.fade-enter-active,.fade-leave-active{ transition:opacity .2s }
.fade-enter-from,.fade-leave-to{ opacity:0 }

@media (max-width: 720px){
  .slot{ min-width:42px; min-height:48px }
  .clear{ bottom:-26px }
}
</style>

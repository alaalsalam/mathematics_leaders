<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{ type:String, default:'ar' }, theme:{ type:String, default:'light' } })

const copy = {
  ar:{
    title:'المستوى الثالث – التحدي 7: أجزاء الشكل المكافئة',
    intro:'ضع الكسر الصحيح لكل جزء من الشكل الهندسي بحيث يمثّل مساحة الجزء بالكامل.',
    bank:'الكسور المتاحة', assign:'ضع الكسر هنا',
    check:'تحقّق', reset:'مسح الاختيار', newQ:'تحدٍ جديد',
    needAll:'اختر كسرًا لكل جزء أولًا.', wrong:'هناك جزء لا يطابق الكسر المعيَّن له.', correct:'أحسنت! الكسور لكل الأجزاء صحيحة.'
  },
  en:{
    title:'Level 3 – Challenge 7: Fraction Areas',
    intro:'Assign the correct fraction to every highlighted region so it matches the area of that region.',
    bank:'Fraction cards', assign:'Drop fraction',
    check:'Check', reset:'Reset', newQ:'New challenge',
    needAll:'Assign a fraction to every region first.', wrong:'One or more regions have the wrong fraction.', correct:'Great! All regions are correct.'
  }
}
const L = computed(() => (copy[props.lang] ? props.lang : 'ar'))

import successUrl from '@/assets/sounds/success3.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong3.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

const puzzles = [
  {
    id:'p1',
    grid:{ rows:4, cols:4 },
    parts:[
      { id:'A', label:'أ', color:'#d1fae5', fraction:'1/4', cells:[0,1,4,5] },
      { id:'B', label:'ب', color:'#86efac', fraction:'3/4', cells:[2,3,6,7,8,9,10,11,12,13,14,15] },
    ],
    options:['1/4','1/2','3/4','2/3']
  },
  {
    id:'p2',
    grid:{ rows:4, cols:4 },
    parts:[
      { id:'A', label:'أ', color:'#dbeafe', fraction:'1/2', cells:[0,1,4,5,8,9,12,13] },
      { id:'B', label:'ب', color:'#bfdbfe', fraction:'1/4', cells:[2,6,10,14] },
      { id:'C', label:'ج', color:'#93c5fd', fraction:'1/4', cells:[3,7,11,15] }
    ],
    options:['1/2','1/4','1/4','1/3','3/4','1/6']
  }
]

const currentPuzzle = ref(puzzles[0])
const placements = reactive({}) // partId -> fraction string
const bankCounts = reactive({})
const feedback = ref(null)
const solved = ref(false)

function shuffle(arr){
  return arr.slice().sort(()=>Math.random()-0.5)
}

function resetState(){
  Object.keys(placements).forEach(k => delete placements[k])
  Object.keys(bankCounts).forEach(k => delete bankCounts[k])
}

function initPuzzle(){
  const puzzle = puzzles[Math.floor(Math.random()*puzzles.length)]
  currentPuzzle.value = puzzle
  resetState()
  feedback.value = null
  solved.value = false

  puzzle.parts.forEach(part => { placements[part.id] = null })
  puzzle.options.forEach(opt => {
    bankCounts[opt] = (bankCounts[opt] || 0) + 1
  })
}

function allowDrop(ev){ ev.preventDefault() }
function onDragStart(ev, value){ ev.dataTransfer.setData('text/plain', value) }
function onDrop(ev, partId){
  ev.preventDefault()
  const value = ev.dataTransfer.getData('text/plain')
  if(!value) return
  if((bankCounts[value] || 0) <= 0 && placements[partId] !== value) return

  if(placements[partId] != null){
    const prev = placements[partId]
    bankCounts[prev] = (bankCounts[prev] || 0) + 1
  }

  if(placements[partId] !== value){
    bankCounts[value] = (bankCounts[value] || 0) - 1
    if(bankCounts[value] < 0) bankCounts[value] = 0
  }

  placements[partId] = value
  solved.value = false
  feedback.value = null
}
function clearPart(partId){
  if(placements[partId] != null){
    const prev = placements[partId]
    bankCounts[prev] = (bankCounts[prev] || 0) + 1
    placements[partId] = null
    solved.value = false
    feedback.value = null
  }
}

const bankList = computed(()=>{
  const list=[]
  for(const [value,count] of Object.entries(bankCounts)){
    for(let i=0;i<count;i++) list.push({ value, key:`${value}-${i}` })
  }
  return shuffle(list)
})

function allAssigned(){
  return currentPuzzle.value.parts.every(part => placements[part.id] != null)
}

async function addPoint(){
  try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{}
}

async function checkSolution(){
  if(!allAssigned()){
    feedback.value = copy[L.value].needAll
    sWrong && sWrong.play()
    return
  }
  for(const part of currentPuzzle.value.parts){
    if(placements[part.id] !== part.fraction){
      feedback.value = copy[L.value].wrong
      sWrong && sWrong.play()
      return
    }
  }
  feedback.value = copy[L.value].correct
  solved.value = true
  sOK && sOK.play(); sClap && sClap.play()
  await addPoint()
}

function resetSelections(){
  currentPuzzle.value.parts.forEach(part => {
    if(placements[part.id] != null){
      const prev = placements[part.id]
      bankCounts[prev] = (bankCounts[prev] || 0) + 1
      placements[part.id] = null
    }
  })
  feedback.value = null
  solved.value = false
}

const cellParts = computed(()=>{
  const { rows, cols } = currentPuzzle.value.grid
  const total = rows * cols
  const map = Array(total).fill(null)
  currentPuzzle.value.parts.forEach(part => {
    part.cells.forEach(idx => { map[idx] = part })
  })
  return map
})

const gridStyle = computed(()=>{
  const { rows, cols } = currentPuzzle.value.grid
  return {
    gridTemplateRows: `repeat(${rows}, 1fr)`,
    gridTemplateColumns: `repeat(${cols}, 1fr)`
  }
})

onMounted(initPuzzle)
watch(() => props.lang, () => { if(!solved.value) feedback.value = null })
</script>

<template>
  <div class="lvl3c7 challenge-surface" :data-theme="props.theme">
    <header class="head">
      <h2 class="title">{{ copy[L].title }}</h2>
      <p class="intro">{{ copy[L].intro }}</p>
    </header>

    <section class="shape">
      <div class="grid" :style="gridStyle">
        <div
          v-for="(cellPart, idx) in cellParts"
          :key="idx"
          class="cell"
          :style="{ background: cellPart ? cellPart.color : '#f3f4f6' }"
        ></div>
      </div>
    </section>

    <section class="assignments">
      <div v-for="part in currentPuzzle.parts" :key="part.id" class="assignment">
        <div class="label">{{ part.label }}</div>
        <div class="drop" @dragover="allowDrop" @drop="onDrop($event, part.id)">
          <span v-if="placements[part.id]" class="value">{{ placements[part.id] }}</span>
          <span v-else class="placeholder">{{ copy[L].assign }}</span>
        </div>
        <button class="clear" @click="clearPart(part.id)"><Eraser class="ic" /> {{ copy[L].clear }}</button>
      </div>
    </section>

    <section class="controls">
      <button class="btn" @click="checkSolution"><Check class="ic" /> {{ copy[L].check }}</button>
      <button class="btn" @click="resetSelections"><RotateCcw class="ic" /> {{ copy[L].reset }}</button>
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
          @dragstart="onDragStart($event, item.value)"
        >
          {{ item.value }}
        </button>
      </div>
    </section>

    <transition name="fade">
      <div v-if="feedback" class="feedback" :class="{ ok: solved }">{{ feedback }}</div>
    </transition>
  </div>
</template>

<style scoped>
.lvl3c7{ --fg:#111827; --bg:#fefce8; --panel:#ffffff; --bd:#fcd34d; --accent:#f59e0b;
  padding:24px; border-radius:18px; background:var(--bg); color:var(--fg); box-shadow:0 16px 32px rgba(245,158,11,.15) }
[data-theme="dark"] .lvl3c7{ --fg:#f8fafc; --bg:#1f1c14; --panel:#2a2418; --bd:#facc15; --accent:#fbbf24 }

.head{ margin-bottom:20px }
.title{ margin:0 0 10px; font-size:1.6rem; font-weight:700 }
.intro{ margin:0; opacity:.85; line-height:1.5 }

.shape{ display:flex; justify-content:center; margin:22px 0 }
.grid{ width:260px; height:260px; display:grid; border:3px solid var(--bd); border-radius:16px; overflow:hidden; box-shadow:0 12px 28px rgba(15,23,42,.15) }
.cell{ border:1px solid rgba(17,24,39,.08) }

.assignments{ display:flex; flex-wrap:wrap; gap:16px; justify-content:center; margin-bottom:20px }
.assignment{ background:var(--panel); border:1px solid var(--bd); border-radius:14px; padding:12px 14px; box-shadow:0 10px 24px rgba(15,23,42,.1); min-width:160px; display:flex; flex-direction:column; gap:10px; align-items:center }
.label{ font-weight:700; font-size:1.1rem }
.drop{ min-width:120px; min-height:48px; border-radius:10px; border:2px dashed rgba(245,158,11,.45); display:flex; align-items:center; justify-content:center; padding:6px 10px; background:rgba(254,243,199,.6); text-align:center }
.placeholder{ font-size:.9rem; color:var(--accent); opacity:.8 }
.value{ font-size:1.2rem; font-weight:700 }
.clear{ border:none; background:transparent; color:var(--accent); cursor:pointer; display:flex; align-items:center; gap:6px; font-size:.8rem }
.ic{ width:16px; height:16px }

.controls{ display:flex; gap:12px; flex-wrap:wrap; justify-content:center; margin-bottom:18px }
.btn{ display:inline-flex; align-items:center; gap:8px; padding:10px 18px; border-radius:12px; border:1px solid var(--bd); background:var(--panel); font-weight:700; cursor:pointer; transition:.15s }
.btn:hover{ transform:translateY(-1px); box-shadow:0 12px 24px rgba(15,23,42,.12) }

.bank{ background:var(--panel); border:1px solid var(--bd); border-radius:16px; padding:18px; box-shadow:0 12px 24px rgba(15,23,42,.08); margin-bottom:18px }
.bank-title{ font-weight:700; margin-bottom:12px }
.bank-items{ display:flex; flex-wrap:wrap; gap:10px; justify-content:center }
.chip{ padding:9px 14px; border-radius:12px; border:1px solid var(--bd); background:rgba(253,230,138,.6); font-weight:700; cursor:grab; transition:.12s }
.chip:active{ cursor:grabbing }

.feedback{ padding:12px 18px; border-radius:12px; border:1px solid #fecaca; background:#fee2e2; color:#b91c1c; font-weight:700; text-align:center }
.feedback.ok{ border-color:#bbf7d0; background:#dcfce7; color:#166534 }
[data-theme="dark"] .feedback{ background:rgba(248,113,113,.18); border-color:rgba(248,113,113,.45); color:#fecaca }
[data-theme="dark"] .feedback.ok{ background:rgba(34,197,94,.22); border-color:rgba(34,197,94,.5); color:#bbf7d0 }

.fade-enter-active,.fade-leave-active{ transition:opacity .2s }
.fade-enter-from,.fade-leave-to{ opacity:0 }
</style>

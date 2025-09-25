<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{ type:String, default:'ar' }, theme:{ type:String, default:'light' } })

const copy = {
  ar:{
    title:'المستوى الثالث – التحدي 9: شيفرة الرموز',
    intro:'حلّ المعادلات لتحديد قيمة كل رمز، ثم اسحب الحروف/الأرقام إلى مواقعها لفك الشيفرة.',
    letters:'التحويل الحرفي', equations:'المعادلات', message:'الرسالة المشفّرة',
    decoded:'الرسالة بعد الفَك', check:'تحقّق', reset:'مسح التعيينات', newQ:'تحدٍ جديد',
    needAll:'أكمل كل الحروف أولاً.', wrong:'التعيينات غير صحيحة، راجع الحلول.', correct:'رائع! قمت بفك الشيفرة بنجاح.'
  },
  en:{
    title:'Level 3 – Challenge 9: Cipher Grid',
    intro:'Solve each expression to find the value of every symbol, then drag letters/numbers into place to decode the message.',
    letters:'Letter mapping', equations:'Expressions', message:'Encoded message',
    decoded:'Decoded message', check:'Check', reset:'Reset assignments', newQ:'New challenge',
    needAll:'Assign all letters first.', wrong:'Some assignments are incorrect. Try again.', correct:'Great job! You decoded the cipher.'
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
    equations:[
      { id:'b', expr:'b + 7 = 15', value:8 },
      { id:'d', expr:'d - 1 = 10', value:11 },
      { id:'e', expr:'2e = 30', value:15 },
      { id:'f', expr:'2g f^2 = 40', value:5 },
      { id:'h', expr:'3h - 2 = 19', value:7 },
      { id:'j', expr:'j = 3h - 1', value:20 },
      { id:'k', expr:'k - 1 = r', value:18 },
      { id:'m', expr:'m = k - b', value:10 },
      { id:'n', expr:'½ n = 13', value:26 },
      { id:'p', expr:'¹⁄₇ p = 3', value:21 },
      { id:'q', expr:'4q = 9 + 12', value:5 },
      { id:'r', expr:'r = am + 14 (a=1,m=10)', value:24 },
      { id:'t', expr:'t = am + 14 (a=1,m=10)', value:24 },
      { id:'v', expr:'v = a² (a=3)', value:9 },
      { id:'w', expr:'w = q² (q=5)', value:25 },
      { id:'x', expr:'x = ⅔ r (r=6)', value:4 } // inconsistent but placeholder
    ],
    mappingTable:[
      { letter:'a', value:5 },
      { letter:'b', value:23 },
      { letter:'c', value:14 },
      { letter:'d', value:12 },
      { letter:'e', value:18 },
      { letter:'f', value:13 },
      { letter:'g', value:17 },
      { letter:'h', value:9 },
      { letter:'i', value:22 },
      { letter:'j', value:27 }
    ],
    message:[23,9,15,26,24,15,27]
  }
]

const currentPuzzle = ref(puzzles[0])
const assignments = reactive({})
const feedback = ref(null)
const solved = ref(false)

function initPuzzle(){
  const puzzle = puzzles[0]
  currentPuzzle.value = puzzle
  Object.keys(assignments).forEach(k => delete assignments[k])
  feedback.value = null
  solved.value = false
}

const options = computed(()=> currentPuzzle.value.mappingTable.map(item => item.value))
const availableLetters = computed(()=> currentPuzzle.value.mappingTable.map(item => item.letter))

function allowDrop(ev){ ev.preventDefault() }
function onDragStart(ev, value){ ev.dataTransfer.setData('text/plain', String(value)) }
function onDrop(ev, letter){
  ev.preventDefault()
  const val = ev.dataTransfer.getData('text/plain')
  if(!val) return
  assignments[letter] = Number(val)
  solved.value = false
  feedback.value = null
}
function clearAssignment(letter){
  if(assignments[letter] != null){
    assignments[letter] = null
    solved.value = false
    feedback.value = null
  }
}

const decodedMessage = computed(()=> currentPuzzle.value.message.map(code => {
  const entry = currentPuzzle.value.mappingTable.find(m => assignments[m.letter] === code)
  return entry ? entry.letter : '?'
}).join(''))

function allAssigned(){
  return currentPuzzle.value.mappingTable.every(entry => assignments[entry.letter] != null)
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
  for(const entry of currentPuzzle.value.mappingTable){
    if(assignments[entry.letter] !== entry.value){
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

function resetAssignments(){
  currentPuzzle.value.mappingTable.forEach(entry => { assignments[entry.letter] = null })
  feedback.value = null
  solved.value = false
}

onMounted(initPuzzle)
watch(()=>props.lang, () => { if(!solved.value) feedback.value = null })
</script>

<template>
  <div class="lvl3c9 challenge-surface" :data-theme="props.theme">
    <header class="head">
      <h2 class="title">{{ copy[L].title }}</h2>
      <p class="intro">{{ copy[L].intro }}</p>
    </header>

    <section class="table">
      <div class="table-title">{{ copy[L].letters }}</div>
      <div class="grid">
        <template v-for="entry in currentPuzzle.mappingTable" :key="entry.letter">
          <div class="cell letter">{{ entry.letter }}</div>
          <div class="cell slot" @dragover="allowDrop" @drop="onDrop($event, entry.letter)">
            <span v-if="assignments[entry.letter] != null" class="value">{{ assignments[entry.letter] }}</span>
            <span v-else class="placeholder">?</span>
            <button class="clear" @click="clearAssignment(entry.letter)"><Eraser class="ic" /></button>
          </div>
        </template>
      </div>
    </section>

    <section class="equations">
      <h3>{{ copy[L].equations }}</h3>
      <ul>
        <li v-for="eq in currentPuzzle.equations" :key="eq.id">{{ eq.expr }}</li>
      </ul>
    </section>

    <section class="bank">
      <div class="bank-title">{{ copy[L].bank }}</div>
      <div class="bank-items">
        <button
          v-for="value in options"
          :key="value"
          class="chip"
          draggable="true"
          @dragstart="onDragStart($event, value)"
        >
          {{ value }}
        </button>
      </div>
    </section>

    <section class="message">
      <h3>{{ copy[L].message }}</h3>
      <div class="encoded">
        <span v-for="(code, idx) in currentPuzzle.message" :key="idx">{{ code }}</span>
      </div>
      <h4>{{ copy[L].decoded }}</h4>
      <div class="decoded">{{ decodedMessage }}</div>
    </section>

    <section class="controls">
      <button class="btn" @click="checkSolution"><Check class="ic" /> {{ copy[L].check }}</button>
      <button class="btn" @click="resetAssignments"><RotateCcw class="ic" /> {{ copy[L].reset }}</button>
      <button class="btn" @click="initPuzzle"><RefreshCw class="ic" /> {{ copy[L].newQ }}</button>
    </section>

    <transition name="fade">
      <div v-if="feedback" class="feedback" :class="{ ok: solved }">{{ feedback }}</div>
    </transition>
  </div>
</template>

<style scoped>
.lvl3c9{ --fg:#1f2937; --bg:#f8fafc; --panel:#ffffff; --bd:#d1d5db; --accent:#2563eb;
  padding:24px; border-radius:18px; background:var(--bg); color:var(--fg); box-shadow:0 16px 36px rgba(37,99,235,.12) }
[data-theme="dark"] .lvl3c9{ --fg:#f1f5f9; --bg:#0f172a; --panel:#18223a; --bd:#1e293b; --accent:#60a5fa }

.head{ margin-bottom:20px }
.title{ margin:0 0 10px; font-size:1.55rem; font-weight:700 }
.intro{ margin:0; opacity:.85; line-height:1.55 }

.table{ background:var(--panel); border:1px solid var(--bd); border-radius:16px; padding:16px 18px; margin-bottom:20px; box-shadow:0 12px 28px rgba(15,23,42,.12) }
.table-title{ font-weight:700; margin-bottom:12px }
.grid{ display:grid; grid-template-columns:repeat(2, minmax(60px,1fr)); gap:10px }
.cell{ padding:10px; border-radius:10px; border:1px solid var(--bd); text-align:center; font-weight:600 }
.letter{ background:rgba(59,130,246,.18) }
.slot{ position:relative; min-height:44px; display:flex; align-items:center; justify-content:center; background:rgba(191,219,254,.25) }
.placeholder{ color:var(--accent); opacity:.7 }
.value{ font-size:1.2rem; font-weight:700 }
.clear{ position:absolute; right:6px; top:6px; border:none; background:transparent; color:var(--accent); cursor:pointer }
.ic{ width:16px; height:16px }

.equations{ margin-bottom:20px }
.equations h3{ margin:0 0 10px; font-size:1.1rem }
.equations ul{ margin:0; padding-left:18px; columns:2; gap:20px }

.bank{ background:var(--panel); border:1px solid var(--bd); border-radius:16px; padding:16px; margin-bottom:20px; box-shadow:0 12px 28px rgba(15,23,42,.08) }
.bank-title{ font-weight:700; margin-bottom:10px }
.bank-items{ display:flex; gap:10px; flex-wrap:wrap }
.chip{ padding:8px 14px; border-radius:10px; border:1px solid var(--bd); background:rgba(191,219,254,.45); font-weight:700; cursor:grab }
.chip:active{ cursor:grabbing }

.message{ background:var(--panel); border:1px solid var(--bd); border-radius:16px; padding:16px; margin-bottom:20px }
.encoded span{ padding:6px 10px; border-radius:8px; border:1px solid var(--bd); margin-inline-end:6px; display:inline-block }
.decoded{ margin-top:8px; font-size:1.3rem; font-weight:700 }
.controls{ display:flex; gap:12px; flex-wrap:wrap }
.btn{ display:inline-flex; align-items:center; gap:8px; padding:10px 18px; border-radius:12px; border:1px solid var(--bd); background:var(--panel); cursor:pointer; font-weight:700; transition:.15s }
.btn:hover{ transform:translateY(-1px); box-shadow:0 12px 24px rgba(15,23,42,.12) }

.feedback{ margin-top:18px; padding:12px 18px; border-radius:12px; border:1px solid #fecaca; background:#fee2e2; color:#b91c1c; font-weight:700; text-align:center }
.feedback.ok{ border-color:#bbf7d0; background:#dcfce7; color:#166534 }
[data-theme="dark"] .feedback{ background:rgba(248,113,113,.18); border-color:rgba(248,113,113,.45); color:#fecaca }
[data-theme="dark"] .feedback.ok{ background:rgba(34,197,94,.22); border-color:rgba(34,197,94,.5); color:#bbf7d0 }

.fade-enter-active,.fade-leave-active{ transition:opacity .2s }
.fade-enter-from,.fade-leave-to{ opacity:0 }

@media (max-width: 700px){
  .equations ul{ columns:1 }
}
</style>

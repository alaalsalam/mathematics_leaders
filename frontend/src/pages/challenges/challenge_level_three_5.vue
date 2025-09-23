<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

const copy = {
  ar:{
    title:'المستوى الثالث – التحدي 5: بطاقات الكسر المفقود',
    intro:[
      'استخدم البطاقات المرقّمة من ١ إلى ٩ مرة واحدة فقط لتكوين الكسرين بحيث يكون الناتج مساويًا للقيمة المطلوبة.',
      'اسحب الرقم المناسب إلى كل خانة للبسط أو المقام، ثم تحقّق من صحة الناتج.'
    ],
    bank:'البطاقات المتاحة',
    check:'تحقّق', reset:'مسح الاختيار', newQ:'تحدٍ جديد', clear:'تفريغ',
    needAll:'املأ كل الخانات أولًا.', wrong:'المعادلة غير صحيحة، جرّب ترتيبًا آخر.', correct:'أحسنت! أنتجت الكسور الصحيحة.'
  },
  en:{
    title:'Level 3 – Challenge 5: Missing Fraction Cards',
    intro:[
      'Use the cards labelled 1 through 9 exactly once to build two fractions whose sum matches the target.',
      'Drag each digit into the correct numerator or denominator, then check your result.'
    ],
    bank:'Available cards',
    check:'Check', reset:'Reset selection', newQ:'New challenge', clear:'Clear',
    needAll:'Fill every slot first.', wrong:'The equation is not satisfied—try another arrangement.', correct:'Great! The fractions are correct.'
  }
}
const L = computed(()=> (copy[props.lang]?props.lang:'ar'))

/* ===== sounds ===== */
import successUrl from '@/assets/sounds/success3.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong3.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

/* ===== puzzle definitions ===== */
const slotTemplate = {
  n1:['n1a','n1b'],
  d1:['d1a','d1b'],
  n2:['n2a','n2b'],
  d2:['d2a','d2b'],
  res:['res']
}

const puzzles = [
  {
    id:'p1',
    solution:{
      n1:['2','9'],
      d1:['1','6'],
      n2:['5','7'],
      d2:['4','8'],
      res:['3']
    }
  },
  {
    id:'p2',
    solution:{
      n1:['3','9'],
      d1:['2','7'],
      n2:['6','4'],
      d2:['1','8'],
      res:['5']
    }
  },
  {
    id:'p3',
    solution:{
      n1:['5','7'],
      d1:['1','3'],
      n2:['9','4'],
      d2:['2','6'],
      res:['8']
    }
  }
]

const currentPuzzle = ref(puzzles[0])
const placements = reactive({})
const expectedDigits = reactive({})
const bankCounts = reactive({})
const feedback = ref(null)
const solved = ref(false)
const digitsPool = ['1','2','3','4','5','6','7','8','9']

function resetMaps(){
  Object.keys(placements).forEach(k => delete placements[k])
  Object.keys(expectedDigits).forEach(k => delete expectedDigits[k])
  Object.keys(bankCounts).forEach(k => delete bankCounts[k])
}

function initPuzzle(){
  const puzzle = puzzles[Math.floor(Math.random()*puzzles.length)]
  currentPuzzle.value = puzzle
  resetMaps()
  feedback.value = null
  solved.value = false

  digitsPool.forEach(d => {
    bankCounts[d] = 1
  })

  for(const [group, keys] of Object.entries(slotTemplate)){
    const digits = puzzle.solution[group]
    if(!digits) continue
    keys.forEach((key, idx) => {
      placements[key] = null
      expectedDigits[key] = digits[idx]
    })
  }
}

function allowDrop(ev){ ev.preventDefault() }

function onDragStart(ev, digit){ ev.dataTransfer.setData('text/plain', digit) }

function onDrop(ev, key){
  ev.preventDefault()
  const digit = ev.dataTransfer.getData('text/plain')
  if(!digit) return
  if((bankCounts[digit] || 0) <= 0 && placements[key] !== digit) return

  if(placements[key] != null){
    const prev = placements[key]
    bankCounts[prev] = (bankCounts[prev] || 0) + 1
  }

  if(placements[key] !== digit){
    bankCounts[digit] = (bankCounts[digit] || 0) - 1
    if(bankCounts[digit] < 0) bankCounts[digit] = 0
  }

  placements[key] = digit
  feedback.value = null
  solved.value = false
}

function clearSlot(key){
  if(placements[key] != null){
    const digit = placements[key]
    bankCounts[digit] = (bankCounts[digit] || 0) + 1
    placements[key] = null
    feedback.value = null
    solved.value = false
  }
}

const bankList = computed(()=> {
  const list=[]
  for(const [digit,count] of Object.entries(bankCounts)){
    for(let i=0;i<count;i++) list.push({ digit, key:`${digit}-${i}` })
  }
  return list
})

function allFilled(){
  return Object.keys(expectedDigits).every(key => placements[key] != null)
}

function valueOf(group){
  const keys = slotTemplate[group]
  const digits = keys.map(k => placements[k])
  return Number(digits.join(''))
}

async function addPoint(){
  try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{}
}

async function checkSolution(){
  if(!allFilled()){
    feedback.value = copy[L.value].needAll
    sWrong && sWrong.play()
    return
  }
  const n1 = valueOf('n1')
  const d1 = valueOf('d1')
  const n2 = valueOf('n2')
  const d2 = valueOf('d2')
  const res = Number(placements['res'])
  if(!d1 || !d2){
    feedback.value = copy[L.value].wrong
    sWrong && sWrong.play()
    return
  }
  const sum = n1/d1 + n2/d2
  if(Math.abs(sum - res) < 1e-6){
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
  for(const key of Object.keys(placements)){
    if(placements[key] != null){
      const digit = placements[key]
      bankCounts[digit] = (bankCounts[digit] || 0) + 1
      placements[key] = null
    }
  }
  feedback.value = null
  solved.value = false
}

onMounted(initPuzzle)
watch(() => props.lang, () => { if(!solved.value) feedback.value = null })
</script>

<template>
  <div class="lvl3c5" :data-theme="props.theme">
    <header class="head">
      <h2 class="title">{{ copy[L].title }}</h2>
      <p v-for="(line, idx) in copy[L].intro" :key="idx" class="intro">{{ line }}</p>
    </header>

    <section class="equation">
      <div class="fraction">
        <div class="row">
          <div v-for="key in slotTemplate.n1" :key="key" class="slot" @dragover="allowDrop" @drop="onDrop($event, key)">
            <span v-if="placements[key]" class="digit">{{ placements[key] }}</span>
            <span v-else class="placeholder">?</span>
          </div>
        </div>
        <div class="bar"></div>
        <div class="row">
          <div v-for="key in slotTemplate.d1" :key="key" class="slot" @dragover="allowDrop" @drop="onDrop($event, key)">
            <span v-if="placements[key]" class="digit">{{ placements[key] }}</span>
            <span v-else class="placeholder">?</span>
          </div>
        </div>
      </div>

      <span class="op">+</span>

      <div class="fraction">
        <div class="row">
          <div v-for="key in slotTemplate.n2" :key="key" class="slot" @dragover="allowDrop" @drop="onDrop($event, key)">
            <span v-if="placements[key]" class="digit">{{ placements[key] }}</span>
            <span v-else class="placeholder">?</span>
          </div>
        </div>
        <div class="bar"></div>
        <div class="row">
          <div v-for="key in slotTemplate.d2" :key="key" class="slot" @dragover="allowDrop" @drop="onDrop($event, key)">
            <span v-if="placements[key]" class="digit">{{ placements[key] }}</span>
            <span v-else class="placeholder">?</span>
          </div>
        </div>
      </div>

      <span class="op">=</span>

      <div class="target-slot" @dragover="allowDrop" @drop="onDrop($event, 'res')">
        <span v-if="placements.res" class="digit">{{ placements.res }}</span>
        <span v-else class="placeholder">?</span>
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
.lvl3c5{ --fg:#1f2937; --bg:#fffaf3; --panel:#ffffff; --bd:#facc15; --accent:#f59e0b;
  padding:24px; border-radius:18px; color:var(--fg); background:var(--bg); box-shadow:0 16px 36px rgba(245,158,11,.15) }
[data-theme="dark"] .lvl3c5{ --fg:#f1f5f9; --bg:#271c12; --panel:#312310; --bd:#facc15; --accent:#fbbf24 }

.head{ margin-bottom:20px }
.title{ margin:0 0 10px; font-size:1.55rem; font-weight:700 }
.intro{ margin:0 0 6px; line-height:1.55 }

.equation{ display:flex; align-items:center; justify-content:center; gap:18px; margin-bottom:20px; flex-wrap:wrap }
.fraction{ display:flex; flex-direction:column; align-items:center; gap:6px; background:var(--panel); padding:12px 16px; border:2px solid var(--bd); border-radius:16px; box-shadow:0 10px 28px rgba(15,23,42,.1) }
.row{ display:flex; gap:8px }
.slot{ width:44px; height:44px; border-radius:12px; border:2px dashed rgba(245,158,11,.55); display:flex; align-items:center; justify-content:center; background:rgba(253,230,138,.4); cursor:pointer }
.placeholder{ font-size:1.4rem; color:var(--accent); opacity:.8 }
.digit{ font-size:1.35rem; font-weight:700 }
.bar{ width:100%; height:2px; background:var(--bd) }
.target-slot{ width:56px; height:56px; border-radius:14px; border:2px dashed rgba(245,158,11,.6); display:flex; align-items:center; justify-content:center; background:rgba(253,230,138,.35) }
.op{ font-size:1.6rem; font-weight:700; color:var(--accent) }

.controls{ display:flex; gap:12px; flex-wrap:wrap; justify-content:center; margin-bottom:18px }
.btn{ display:inline-flex; align-items:center; gap:8px; padding:10px 18px; border-radius:12px; border:1px solid var(--bd); background:var(--panel); cursor:pointer; font-weight:700; transition:.15s }
.btn:hover{ transform:translateY(-1px); box-shadow:0 12px 24px rgba(15,23,42,.12) }
.ic{ width:18px; height:18px }

.bank{ background:var(--panel); border:1px solid var(--bd); border-radius:16px; padding:18px; box-shadow:0 12px 24px rgba(15,23,42,.08) }
.bank-title{ font-weight:700; margin-bottom:12px }
.bank-items{ display:flex; flex-wrap:wrap; gap:10px }
.chip{ padding:10px 16px; border-radius:12px; border:1px solid var(--bd); background:rgba(253,230,138,.45); font-weight:700; cursor:grab; transition:.12s }
.chip:active{ cursor:grabbing }

.feedback{ margin-top:18px; padding:12px 18px; border-radius:12px; border:1px solid #fecaca; background:#fee2e2; color:#b91c1c; font-weight:700; text-align:center }
.feedback.ok{ border-color:#bbf7d0; background:#dcfce7; color:#166534 }
[data-theme="dark"] .feedback{ background:rgba(248,113,113,.18); border-color:rgba(248,113,113,.45); color:#fecaca }
[data-theme="dark"] .feedback.ok{ background:rgba(34,197,94,.22); border-color:rgba(34,197,94,.5); color:#bbf7d0 }

.fade-enter-active,.fade-leave-active{ transition:opacity .2s }
.fade-enter-from,.fade-leave-to{ opacity:0 }

@media(max-width: 720px){
  .fraction{ padding:10px 12px }
  .slot{ width:40px; height:40px }
  .target-slot{ width:48px; height:48px }
}
</style>

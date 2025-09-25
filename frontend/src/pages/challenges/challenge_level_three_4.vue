<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

const copy = {
  ar:{
    title:'المستوى الثالث – التحدي 4: أزل النقطة الحمراء',
    intro:[
      'هذه المعادلات فرصة للتفكير في العمليات على الأعداد العشرية.',
      'كل نقطة حمراء ● تمثّل رقمًا ناقصًا. اسحب الرقم الملائم من لوحة الأرقام وضعه مكان النقطة حتى تصبح المعادلة صحيحة.'
    ],
    check:'تحقّق', reset:'مسح الكل', newQ:'سؤال جديد',
    incomplete:'أكمل كل الفراغات أولاً.', wrong:'هناك معادلة غير صحيحة، راجع الأرقام.', correct:'أحسنت! جميع المعادلات صحيحة.',
    bank:'لوحة الأرقام', clear:'تفريغ'
  },
  en:{
    title:'Level 3 – Challenge 4: Replace the red dot',
    intro:[
      'These equations focus on decimal operations.',
      'Each red dot ● hides a single digit. Drag the correct digit from the number bank to make every equation true.'
    ],
    check:'Check', reset:'Clear all', newQ:'New puzzle',
    incomplete:'Fill every blank first.', wrong:'One or more equations are incorrect. Try again.', correct:'Great! All equations are valid.',
    bank:'Number bank', clear:'Clear'
  }
}
const L = computed(()=> (copy[props.lang]?props.lang:'ar'))

/* ===== sounds ===== */
import successUrl from '@/assets/sounds/success2.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong2.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

const puzzleBank = [
  {
    id:'p1',
    equations:[
      {
        id:'eqA',
        slots:{ a:8, b:7 },
        order:['a','b'],
        template:{
          ar:['أ. ٩٫٣ × ٠٫', {slot:'a'}, ' = ', {slot:'b'}, '٫٤٤'],
          en:['A. 9.3 × 0.', {slot:'a'}, ' = ', {slot:'b'}, '.44']
        },
        evaluate(values){
          const left = 9.3 * (values.a / 10)
          const right = values.b + 0.44
          return Math.abs(left - right) < 1e-6
        }
      },
      {
        id:'eqB',
        slots:{ c:4, d:9 },
        order:['c','d'],
        template:{
          ar:['ب. ٢٫', {slot:'c'}, ' × ٢٫', {slot:'d'}, ' = ٦٫٩٦'],
          en:['B. 2.', {slot:'c'}, ' × 2.', {slot:'d'}, ' = 6.96']
        },
        evaluate(values){
          const left = (2 + values.c/10) * (2 + values.d/10)
          return Math.abs(left - 6.96) < 1e-6
        }
      },
      {
        id:'eqC',
        slots:{ e:4, f:7 },
        order:['e','f'],
        template:{
          ar:['ج. ', {slot:'e'}, '٫٩ × ٣٫', {slot:'f'}, ' = ١٨٫١٣'],
          en:['C. ', {slot:'e'}, '.9 × 3.', {slot:'f'}, ' = 18.13']
        },
        evaluate(values){
          const left = (values.e + 0.9) * (3 + values.f/10)
          return Math.abs(left - 18.13) < 1e-6
        }
      },
      {
        id:'eqD',
        slots:{ g:7, h:9 },
        order:['g','h'],
        template:{
          ar:['د. ٤٫', {slot:'g'}, ' + ١٫٢٥ = ٥٫', {slot:'h'}, '٥'],
          en:['D. 4.', {slot:'g'}, ' + 1.25 = 5.', {slot:'h'}, '5']
        },
        evaluate(values){
          const left = (4 + values.g/10) + 1.25
          const right = 5 + values.h/10 + 0.05
          return Math.abs(left - right) < 1e-6
        }
      },
    ]
  }
]

const currentPuzzle = ref(puzzleBank[0])
const answers = reactive({})
const totalCounts = reactive({})
const bankCounts = reactive({})
const slotsMeta = ref([])
const feedback = ref(null)
const solved = ref(false)
const digitsMap = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩']

function formatDigit(value){
  if(value == null) return ''
  const str = String(value)
  return props.lang==='ar'
    ? str.replace(/[0-9]/g, d => digitsMap[Number(d)])
    : str
}

function shuffle(arr){
  return arr.slice().sort(()=>Math.random()-0.5)
}

function initPuzzle(){
  const puzzle = puzzleBank[Math.floor(Math.random()*puzzleBank.length)]
  currentPuzzle.value = puzzle
  feedback.value = null
  solved.value = false
  Object.keys(answers).forEach(k => delete answers[k])
  Object.keys(totalCounts).forEach(k => delete totalCounts[k])
  Object.keys(bankCounts).forEach(k => delete bankCounts[k])
  const meta = []

  puzzle.equations.forEach(eq => {
    eq.order.forEach(slotName => {
      const key = `${eq.id}-${slotName}`
      meta.push({ key, eq, slotName })
      answers[key] = null
      const digit = eq.slots[slotName]
      totalCounts[digit] = (totalCounts[digit] || 0) + 1
      bankCounts[digit] = (bankCounts[digit] || 0) + 1
    })
  })
  slotsMeta.value = meta
}

function allowDrop(ev){ ev.preventDefault() }

function onDragStart(ev, value){ ev.dataTransfer.setData('text/plain', String(value)) }

function onDrop(ev, key){
  ev.preventDefault()
  const raw = ev.dataTransfer.getData('text/plain')
  const val = Number(raw)
  if(Number.isNaN(val)) return
  if((bankCounts[val] || 0) <= 0 && answers[key] !== val) return

  if(answers[key] != null){
    const prev = answers[key]
    bankCounts[prev] = (bankCounts[prev] || 0) + 1
  }

  if(answers[key] !== val){
    bankCounts[val] = (bankCounts[val] || 0) - 1
    if(bankCounts[val] < 0) bankCounts[val] = 0
  }

  answers[key] = val
  feedback.value = null
  solved.value = false
}

function clearSlot(key){
  if(answers[key] != null){
    const prev = answers[key]
    bankCounts[prev] = (bankCounts[prev] || 0) + 1
    answers[key] = null
    feedback.value = null
    solved.value = false
  }
}

const bankList = computed(()=>{
  const list = []
  for(const [digit,count] of Object.entries(bankCounts)){
    for(let i=0;i<count;i++) list.push({ value:Number(digit), key:`${digit}-${i}` })
  }
  return shuffle(list)
})

function allFilled(){
  return slotsMeta.value.every(slot => answers[slot.key] != null)
}

async function addPoint(){
  try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{}
}

async function checkAll(){
  if(!allFilled()){
    feedback.value = copy[L.value].incomplete
    sWrong && sWrong.play()
    return
  }
  const { equations } = currentPuzzle.value
  for(const eq of equations){
    const values = {}
    let valid = true
    for(const slotName of eq.order){
      const key = `${eq.id}-${slotName}`
      values[slotName] = answers[key]
      if(values[slotName] == null){ valid = false; break }
    }
    if(!valid || !eq.evaluate(values)){
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

function resetAll(){
  slotsMeta.value.forEach(slot => { if(answers[slot.key]!=null){ const prev=answers[slot.key]; bankCounts[prev]=(bankCounts[prev]||0)+1; answers[slot.key]=null } })
  feedback.value = null
  solved.value = false
}

onMounted(initPuzzle)
watch(() => props.lang, () => { if(!solved.value) feedback.value = null })
</script>

<template>
  <div class="lvl3c4 challenge-surface" :data-theme="props.theme">
    <header class="head">
      <h2 class="title">{{ copy[L].title }}</h2>
      <p v-for="(line,idx) in copy[L].intro" :key="idx" class="intro">{{ line }}</p>
    </header>

    <section class="equations">
      <div v-for="eq in currentPuzzle.equations" :key="eq.id" class="card">
        <div class="expression">
          <span v-for="(token, idx) in (props.lang==='ar' ? eq.template.ar : eq.template.en)" :key="idx">
            <template v-if="typeof token === 'string'">{{ token }}</template>
            <template v-else>
              <span class="slot" @dragover="allowDrop" @drop="onDrop($event, eq.id + '-' + token.slot)">
                <span v-if="answers[eq.id + '-' + token.slot] != null" class="digit">{{ formatDigit(answers[eq.id + '-' + token.slot]) }}</span>
                <span v-else class="placeholder">●</span>
              </span>
              <button class="clear" @click="clearSlot(eq.id + '-' + token.slot)"><Eraser class="ic" /> {{ copy[L].clear }}</button>
            </template>
          </span>
        </div>
      </div>
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
      <button class="btn" @click="checkAll"><Check class="ic" /> {{ copy[L].check }}</button>
      <button class="btn" @click="resetAll"><RotateCcw class="ic" /> {{ copy[L].reset }}</button>
      <button class="btn" @click="initPuzzle"><RefreshCw class="ic" /> {{ copy[L].newQ }}</button>
    </section>

    <transition name="fade">
      <div v-if="feedback" class="feedback" :class="{ ok: solved }">{{ feedback }}</div>
    </transition>
  </div>
</template>

<style scoped>
.lvl3c4{ --fg:#111827; --bg:#fdf5f3; --panel:#ffffff; --bd:#fcd6c3; --accent:#ef4444;
  padding:24px; border-radius:18px; color:var(--fg); background:var(--bg); box-shadow:0 16px 32px rgba(244,114,182,.12) }
[data-theme="dark"] .lvl3c4{ --fg:#f8fafc; --bg:#1b1325; --panel:#201830; --bd:#3b2c4b; --accent:#fb7185 }

.head{ margin-bottom:18px }
.title{ margin:0 0 12px; font-size:1.55rem; font-weight:700 }
.intro{ margin:0 0 6px; line-height:1.6 }

.equations{ display:grid; gap:18px }
.card{ background:var(--panel); border:1px solid var(--bd); border-radius:16px; padding:16px 18px; box-shadow:0 12px 24px rgba(17,24,39,.08) }
.expression{ display:flex; align-items:center; flex-wrap:wrap; gap:10px; font-size:1.15rem; font-weight:600 }
.slot{ min-width:36px; min-height:36px; border-radius:12px; border:2px dashed rgba(239,68,68,.45); display:inline-flex; align-items:center; justify-content:center; background:rgba(254,226,226,.5); padding:4px 8px }
[data-theme="dark"] .slot{ background:rgba(239,68,68,.12); border-color:rgba(248,113,113,.55) }
.digit{ font-size:1.2rem; font-weight:700 }
.placeholder{ color:var(--accent); font-size:1.4rem }
.clear{ border:none; background:transparent; color:var(--accent); cursor:pointer; display:inline-flex; align-items:center; gap:4px; font-size:.8rem }
.ic{ width:16px; height:16px }

.bank{ margin:22px 0; background:var(--panel); border:1px solid var(--bd); border-radius:16px; padding:16px; box-shadow:0 12px 24px rgba(17,24,39,.08) }
.bank-title{ font-weight:700; margin-bottom:12px }
.bank-items{ display:flex; flex-wrap:wrap; gap:10px }
.chip{ padding:8px 14px; border-radius:999px; border:1px solid var(--bd); background:var(--panel); cursor:grab; font-weight:700; box-shadow:0 8px 20px rgba(17,24,39,.08) }
.chip:active{ cursor:grabbing }

.actions{ display:flex; gap:12px; flex-wrap:wrap; margin-bottom:18px }
.btn{ display:inline-flex; align-items:center; gap:8px; padding:10px 18px; border-radius:12px; border:1px solid var(--bd); background:var(--panel); cursor:pointer; font-weight:700; transition:.15s }
.btn:hover{ transform:translateY(-1px); box-shadow:0 12px 24px rgba(17,24,39,.12) }

.feedback{ padding:12px 18px; border-radius:12px; border:1px solid #fecaca; background:#fee2e2; color:#b91c1c; font-weight:700 }
.feedback.ok{ border-color:#bbf7d0; background:#dcfce7; color:#166534 }
[data-theme="dark"] .feedback{ background:rgba(248,113,113,.18); border-color:rgba(248,113,113,.45); color:#fecaca }
[data-theme="dark"] .feedback.ok{ background:rgba(34,197,94,.22); border-color:rgba(34,197,94,.5); color:#bbf7d0 }

.fade-enter-active,.fade-leave-active{ transition:opacity .2s }
.fade-enter-from,.fade-leave-to{ opacity:0 }
</style>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Check, RotateCcw, RefreshCw } from 'lucide-vue-next'

const props = defineProps({ lang:{ type:String, default:'ar' }, theme:{ type:String, default:'light' } })

const copy = {
  ar:{
    title:'المستوى الثاني – التحدي 6: مقارنة الأوزان',
    question:'ما وزن المربع الواحد مقارنة بالمثلث؟',
    newQ:'سؤال جديد', reset:'إعادة تعيين', check:'تحقّق',
    correct:'إجابة صحيحة! أحسنت في مقارنة الأوزان.',
    wrong:'إجابة غير صحيحة. أعد التفكير في المعادلات.',
    pick:'اختر إجابة أولاً.'
  },
  en:{
    title:'Level 2 – Challenge 6: Comparing weights',
    question:'How does the weight of the square compare to the triangle?',
    newQ:'New question', reset:'Reset', check:'Check',
    correct:'Correct! Great job comparing the weights.',
    wrong:'That is incorrect. Revisit the equations.',
    pick:'Select an option first.'
  }
}

const L = computed(()=> (copy[props.lang]?props.lang:'ar'))
/* sounds */
import successUrl from '@/assets/sounds/success2.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong2.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

const digitsMap = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩']

function toArabicNumber(value){
  return String(value).replace(/[0-9]/g, d => digitsMap[Number(d)])
}

function formatNumberByLang(value, lang){
  return lang === 'ar' ? toArabicNumber(value) : String(value)
}

function unitsWord(value, lang){
  if(lang === 'ar'){
    return value <= 2 ? 'وحدة' : 'وحدات'
  }
  return value === 1 ? 'unit' : 'units'
}

const optionTemplates = {
  ar:{
    double:'ضعف وزن المثلث',
    equal:'يساوي وزن المثلث',
    half:'نصف وزن المثلث',
    less:(n) => `أقل بـ${toArabicNumber(n)} ${unitsWord(n,'ar')} من وزن المثلث`,
    more:(n) => `أكثر بـ${toArabicNumber(n)} ${unitsWord(n,'ar')} من وزن المثلث`
  },
  en:{
    double:'Twice the triangle',
    equal:'Equal to the triangle',
    half:'Half the triangle',
    less:(n) => `${n} ${unitsWord(n,'en')} less than the triangle`,
    more:(n) => `${n} ${unitsWord(n,'en')} more than the triangle`
  }
}

function buildOptions(puzzle, lang){
  const magnitude = Math.abs(puzzle.difference)
  const templates = optionTemplates[lang]
  return [
    { id:'a', text:templates.double },
    { id:'b', text:templates.equal },
    { id:'c', text:templates.half },
    { id:'d', text:templates.less(magnitude) },
    { id:'e', text:templates.more(magnitude) }
  ]
}

function buildPremiseLines(puzzle, lang){
  const squareTotal = formatNumberByLang(puzzle.totals.square, lang)
  const triangleTotal = formatNumberByLang(puzzle.totals.triangle, lang)
  if(lang === 'ar'){
    return [
      `وزن كرتان ومربع واحد يساويان ${squareTotal} وحدات.`,
      `وزن كرتان ومثلث واحد يساويان ${triangleTotal} وحدات.`
    ]
  }
  return [
    `Two balls and one square weigh ${squareTotal} units.`,
    `Two balls and one triangle weigh ${triangleTotal} units.`
  ]
}

const puzzleBank = [
  { id:'p1', totals:{ square:8, triangle:6 }, difference:2, correctId:'e' },
  { id:'p2', totals:{ square:10, triangle:7 }, difference:3, correctId:'e' },
  { id:'p3', totals:{ square:9, triangle:11 }, difference:-2, correctId:'d' },
  { id:'p4', totals:{ square:12, triangle:8 }, difference:4, correctId:'e' },
  { id:'p5', totals:{ square:7, triangle:10 }, difference:-3, correctId:'d' }
]

const currentPuzzle = ref(puzzleBank[0])
const lastPuzzleId = ref(null)

const correctId = computed(() => currentPuzzle.value.correctId)
function pickNextPuzzle(){
  if(puzzleBank.length === 1){
    lastPuzzleId.value = puzzleBank[0].id
    return puzzleBank[0]
  }
  let candidate
  do{
    candidate = puzzleBank[Math.floor(Math.random() * puzzleBank.length)]
  }while(candidate.id === lastPuzzleId.value)
  lastPuzzleId.value = candidate.id
  return candidate
}

function shuffle(arr){
  return arr.slice().sort(() => Math.random() - 0.5)
}

const selected = ref(null)
const feedback = ref(null)
const solved = ref(false)
const shuffledOptions = ref(null)

function applyOptions(){
  shuffledOptions.value = shuffle(buildOptions(currentPuzzle.value, L.value))
}

function resetAll(){
  selected.value = null
  feedback.value = null
  solved.value = false
}

async function addPoint(){
  try{
    await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',
      { method:'GET', credentials:'include' })
  }catch{}
}

async function checkAnswer(){
  if(!selected.value){
    feedback.value = copy[L.value].pick
    sWrong && sWrong.play()
    return
  }
  if(selected.value === correctId.value){
    const wasSolved = solved.value
    solved.value = true
    feedback.value = copy[L.value].correct
    sOK && sOK.play(); sClap && sClap.play()
    if(!wasSolved){
      await addPoint()
    }
  } else {
    solved.value = false
    feedback.value = copy[L.value].wrong
    sWrong && sWrong.play()
  }
}

function randomizePrompt(){
  const puzzle = pickNextPuzzle()
  currentPuzzle.value = puzzle
  resetAll()
  applyOptions()
}

watch(() => props.lang, () => {
  resetAll()
  applyOptions()
})

const optionsList = computed(() => shuffledOptions.value || buildOptions(currentPuzzle.value, L.value))

const premiseLines = computed(() => buildPremiseLines(currentPuzzle.value, L.value))

onMounted(() => {
  randomizePrompt()
})
</script>

<template>
  <div class="lvl2c6 challenge-surface" :data-theme="props.theme">
    <header class="head">
      <h2 class="title">{{ copy[L].title }}</h2>
      <p v-for="(line, idx) in premiseLines" :key="idx" class="premise">{{ line }}</p>
      <p class="question">{{ copy[L].question }}</p>
    </header>

    <section class="options">
      <label
        v-for="option in optionsList"
        :key="option.id"
        class="option"
        :class="{ selected: selected === option.id }"
      >
        <input
          type="radio"
          name="weight-comparison"
          :value="option.id"
          v-model="selected"
        />
        <span class="mark"></span>
        <span class="text">{{ option.text }}</span>
      </label>
    </section>

    <section class="actions">
      <button class="btn" @click="checkAnswer"><Check class="ic" /> {{ copy[L].check }}</button>
      <button class="btn" @click="resetAll"><RotateCcw class="ic" /> {{ copy[L].reset }}</button>
      <button class="btn" @click="randomizePrompt"><RefreshCw class="ic" /> {{ copy[L].newQ }}</button>
    </section>

    <transition name="fade">
      <div v-if="feedback" class="feedback" :class="{ ok: solved }">{{ feedback }}</div>
    </transition>
  </div>
</template>

<style scoped>
.lvl2c6{ --fg:#1f2937; --bg:#f8fafc; --panel:#ffffff; --bd:#cbd5f5; --accent:#2563eb;
  padding:24px; border-radius:18px; color:var(--fg); background:linear-gradient(135deg,#eef2ff,#f8fafc);
  box-shadow:0 14px 30px rgba(37,99,235,.12) }
[data-theme="dark"] .lvl2c6{ --fg:#e2e8f0; --bg:#0f172a; --panel:#111c32; --bd:#1d2a44; --accent:#60a5fa;
  background:linear-gradient(135deg,#0f172a,#1e293b) }

.head{ margin-bottom:18px }
.title{ margin:0 0 12px; font-size:1.6rem; font-weight:800 }
.premise{ margin:0 0 6px; line-height:1.6; opacity:.85 }
.question{ margin:10px 0 0; font-size:1.1rem; font-weight:700 }

.options{ display:grid; gap:12px; margin:20px 0 }
.option{ position:relative; display:flex; align-items:center; gap:12px; padding:14px 16px; border-radius:14px;
  border:2px solid transparent; background:var(--panel); box-shadow:0 8px 20px rgba(37,99,235,.08); cursor:pointer;
  transition:.18s }
.option:hover{ transform:translateY(-1px); box-shadow:0 12px 28px rgba(37,99,235,.12) }
.option.selected{ border-color:var(--accent); box-shadow:0 12px 28px rgba(37,99,235,.18) }
.option input{ display:none }
.mark{ width:18px; height:18px; border-radius:50%; border:2px solid var(--accent); display:inline-block; flex-shrink:0; position:relative }
.option.selected .mark::after{ content:''; position:absolute; inset:3px; border-radius:50%; background:var(--accent) }
.text{ font-weight:600; line-height:1.5 }

.actions{ display:flex; flex-wrap:wrap; gap:12px; margin-top:18px }
.btn{ display:inline-flex; align-items:center; gap:8px; padding:10px 20px; border-radius:12px; border:1px solid var(--bd);
  background:var(--panel); cursor:pointer; font-weight:700; transition:.15s }
.btn:hover{ transform:translateY(-1px); box-shadow:0 10px 24px rgba(37,99,235,.12) }
.ic{ width:18px; height:18px }

.feedback{ margin-top:20px; padding:12px 18px; border-radius:12px; border:1px solid #fecaca; background:#fee2e2; color:#b91c1c; font-weight:700 }
.feedback.ok{ border-color:#bbf7d0; background:#dcfce7; color:#166534 }
[data-theme="dark"] .feedback{ background:rgba(248,113,113,.18); border-color:rgba(248,113,113,.45); color:#fecaca }
[data-theme="dark"] .feedback.ok{ background:rgba(34,197,94,.22); border-color:rgba(34,197,94,.5); color:#bbf7d0 }

.fade-enter-active,.fade-leave-active{ transition:opacity .2s }
.fade-enter-from,.fade-leave-to{ opacity:0 }
</style>

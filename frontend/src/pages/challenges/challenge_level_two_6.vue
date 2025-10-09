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

/* numerals */
const digitsMap = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩']
function toArabicNumber(v){ return String(v).replace(/[0-9]/g, d => digitsMap[+d]) }
function formatNumberByLang(v, lang){ return lang==='ar'? toArabicNumber(v): String(v) }
function unitsWord(v, lang){ return lang==='ar' ? (v<=2?'وحدة':'وحدات') : (v===1?'unit':'units') }

/* options */
const optionTemplates = {
  ar:{
    double:'ضعف وزن المثلث',
    equal:'يساوي وزن المثلث',
    half:'نصف وزن المثلث',
    less:n=>`أقل بـ${toArabicNumber(n)} ${unitsWord(n,'ar')} من وزن المثلث`,
    more:n=>`أكثر بـ${toArabicNumber(n)} ${unitsWord(n,'ar')} من وزن المثلث`
  },
  en:{
    double:'Twice the triangle',
    equal:'Equal to the triangle',
    half:'Half the triangle',
    less:n=>`${n} ${unitsWord(n,'en')} less than the triangle`,
    more:n=>`${n} ${unitsWord(n,'en')} more than the triangle`
  }
}
function buildOptions(puzzle, lang){
  const m = Math.abs(puzzle.difference)
  const t = optionTemplates[lang]
  return [
    { id:'a', text:t.double },
    { id:'b', text:t.equal },
    { id:'c', text:t.half },
    { id:'d', text:t.less(m) },
    { id:'e', text:t.more(m) }
  ]
}
function buildPremiseLines(p, lang){
  const s = formatNumberByLang(p.totals.square, lang)
  const t = formatNumberByLang(p.totals.triangle, lang)
  return lang==='ar'
    ? [`وزن كرتان ومربع واحد يساويان ${s} وحدات.`,`وزن كرتان ومثلث واحد يساويان ${t} وحدات.`]
    : [`Two balls and one square weigh ${s} units.`,`Two balls and one triangle weigh ${t} units.`]
}

/* puzzle bank: فرق = square - triangle
   correctId: e إذا square>triangle ، d إذا أقل ، b إذا يساوي */
const puzzleBank = [
  { id:'p1', totals:{square:8, triangle:6}, difference:2, correctId:'e' },
  { id:'p2', totals:{square:10, triangle:7}, difference:3, correctId:'e' },
  { id:'p3', totals:{square:9, triangle:11}, difference:-2, correctId:'d' },
  { id:'p4', totals:{square:12, triangle:8}, difference:4, correctId:'e' },
  { id:'p5', totals:{square:7, triangle:10}, difference:-3, correctId:'d' },
  { id:'p6', totals:{square:14, triangle:9}, difference:5, correctId:'e' },
  { id:'p7', totals:{square:13, triangle:15}, difference:-2, correctId:'d' },
  { id:'p8', totals:{square:11, triangle:11}, difference:0, correctId:'b' },
  { id:'p9', totals:{square:16, triangle:12}, difference:4, correctId:'e' },
  { id:'p10', totals:{square:8, triangle:13}, difference:-5, correctId:'d' },
  { id:'p11', totals:{square:17, triangle:14}, difference:3, correctId:'e' },
  { id:'p12', totals:{square:15, triangle:18}, difference:-3, correctId:'d' },
  { id:'p13', totals:{square:20, triangle:16}, difference:4, correctId:'e' },
  { id:'p14', totals:{square:19, triangle:21}, difference:-2, correctId:'d' },
  { id:'p15', totals:{square:22, triangle:19}, difference:3, correctId:'e' },
  { id:'p16', totals:{square:18, triangle:23}, difference:-5, correctId:'d' },
  { id:'p17', totals:{square:24, triangle:24}, difference:0, correctId:'b' },
  { id:'p18', totals:{square:21, triangle:17}, difference:4, correctId:'e' },
  { id:'p19', totals:{square:12, triangle:14}, difference:-2, correctId:'d' },
  { id:'p20', totals:{square:25, triangle:20}, difference:5, correctId:'e' },
  { id:'p21', totals:{square:26, triangle:22}, difference:4, correctId:'e' },
  { id:'p22', totals:{square:18, triangle:21}, difference:-3, correctId:'d' },
  { id:'p23', totals:{square:23, triangle:23}, difference:0, correctId:'b' },
  { id:'p24', totals:{square:27, triangle:24}, difference:3, correctId:'e' },
  { id:'p25', totals:{square:29, triangle:25}, difference:4, correctId:'e' },
  { id:'p26', totals:{square:20, triangle:26}, difference:-6, correctId:'d' },
  { id:'p27', totals:{square:28, triangle:28}, difference:0, correctId:'b' },
  { id:'p28', totals:{square:30, triangle:27}, difference:3, correctId:'e' },
  { id:'p29', totals:{square:31, triangle:26}, difference:5, correctId:'e' },
  { id:'p30', totals:{square:22, triangle:27}, difference:-5, correctId:'d' },
  { id:'p31', totals:{square:33, triangle:29}, difference:4, correctId:'e' },
  { id:'p32', totals:{square:32, triangle:35}, difference:-3, correctId:'d' },
  { id:'p33', totals:{square:36, triangle:31}, difference:5, correctId:'e' },
  { id:'p34', totals:{square:34, triangle:34}, difference:0, correctId:'b' },
  { id:'p35', totals:{square:37, triangle:33}, difference:4, correctId:'e' },
  { id:'p36', totals:{square:35, triangle:39}, difference:-4, correctId:'d' },
  { id:'p37', totals:{square:40, triangle:36}, difference:4, correctId:'e' },
  { id:'p38', totals:{square:38, triangle:43}, difference:-5, correctId:'d' },
  { id:'p39', totals:{square:42, triangle:37}, difference:5, correctId:'e' },
  { id:'p40', totals:{square:41, triangle:41}, difference:0, correctId:'b' },
  { id:'p41', totals:{square:44, triangle:40}, difference:4, correctId:'e' },
  { id:'p42', totals:{square:39, triangle:45}, difference:-6, correctId:'d' },
  { id:'p43', totals:{square:46, triangle:43}, difference:3, correctId:'e' },
  { id:'p44', totals:{square:47, triangle:42}, difference:5, correctId:'e' },
  { id:'p45', totals:{square:43, triangle:48}, difference:-5, correctId:'d' },
  { id:'p46', totals:{square:50, triangle:46}, difference:4, correctId:'e' },
  { id:'p47', totals:{square:45, triangle:51}, difference:-6, correctId:'d' },
  { id:'p48', totals:{square:52, triangle:49}, difference:3, correctId:'e' },
  { id:'p49', totals:{square:54, triangle:50}, difference:4, correctId:'e' },
  { id:'p50', totals:{square:48, triangle:54}, difference:-6, correctId:'d' },
  { id:'p51', totals:{square:55, triangle:55}, difference:0, correctId:'b' },
  { id:'p52', totals:{square:57, triangle:52}, difference:5, correctId:'e' },
  { id:'p53', totals:{square:53, triangle:58}, difference:-5, correctId:'d' },
  { id:'p54', totals:{square:60, triangle:56}, difference:4, correctId:'e' },
  { id:'p55', totals:{square:59, triangle:62}, difference:-3, correctId:'d' },
  { id:'p56', totals:{square:63, triangle:58}, difference:5, correctId:'e' },
  { id:'p57', totals:{square:62, triangle:62}, difference:0, correctId:'b' },
  { id:'p58', totals:{square:65, triangle:61}, difference:4, correctId:'e' },
  { id:'p59', totals:{square:61, triangle:67}, difference:-6, correctId:'d' },
  { id:'p60', totals:{square:68, triangle:64}, difference:4, correctId:'e' }
]

const currentPuzzle = ref(puzzleBank[0])
const lastPuzzleId  = ref(null)
const correctId = computed(()=> currentPuzzle.value.correctId)

function pickNextPuzzle(){
  if(puzzleBank.length===1){ lastPuzzleId.value = puzzleBank[0].id; return puzzleBank[0] }
  let c
  do{ c = puzzleBank[Math.floor(Math.random()*puzzleBank.length)] }while(c.id===lastPuzzleId.value)
  lastPuzzleId.value = c.id
  return c
}
function shuffle(arr){ return arr.slice().sort(()=>Math.random()-0.5) }

const selected = ref(null)
const feedback = ref(null)
const solved = ref(false)
const shuffledOptions = ref(null)

function applyOptions(){ shuffledOptions.value = shuffle(buildOptions(currentPuzzle.value, L.value)) }
function resetAll(){ selected.value=null; feedback.value=null; solved.value=false }

async function addPoint(){
  try{
    await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',
      { method:'GET', credentials:'include' })
  }catch{}
}

async function checkAnswer(){
  if(!selected.value){ feedback.value = copy[L.value].pick; sWrong&&sWrong.play(); return }
  if(selected.value===correctId.value){
    const wasSolved = solved.value
    solved.value = true
    feedback.value = copy[L.value].correct
    sOK&&sOK.play(); sClap&&sClap.play()
    if(!wasSolved) await addPoint()
  }else{
    solved.value = false
    feedback.value = copy[L.value].wrong
    sWrong&&sWrong.play()
  }
}

function randomizePrompt(){
  const p = pickNextPuzzle()
  currentPuzzle.value = p
  resetAll()
  applyOptions()
}

watch(()=>props.lang, ()=>{ resetAll(); applyOptions() })

const optionsList  = computed(()=> shuffledOptions.value || buildOptions(currentPuzzle.value, L.value))
const premiseLines = computed(()=> buildPremiseLines(currentPuzzle.value, L.value))

onMounted(()=>{ randomizePrompt() })
</script>

<template>
  <div class="lvl2c6 challenge-surface" :data-theme="props.theme">
    <header class="head">
      <h2 class="title">{{ copy[L].title }}</h2>
      <p v-for="(line, idx) in premiseLines" :key="idx" class="premise">{{ line }}</p>
      <p class="question">{{ copy[L].question }}</p>
    </header>

    <section class="options">
      <label v-for="option in optionsList" :key="option.id" class="option" :class="{ selected: selected === option.id }">
        <input type="radio" name="weight-comparison" :value="option.id" v-model="selected" />
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
[data-theme="dark"] .lvl2c6{ --fg:#e2e8f0; --bg:#0f172a; --panel:#111c32; --bd:#1d2a44; --accent:#60a5فا;
  background:linear-gradient(135deg,#0f172a,#1e293b) }

.head{ margin-bottom:18px }
.title{ margin:0 0 12px; font-size:1.6rem; font-weight:800 }
.premise{ margin:0 0 6px; line-height:1.6; opacity:.85 }
.question{ margin:10px 0 0; font-size:1.1rem; font-weight:700 }

.options{ display:grid; gap:12px; margin:20px 0 }
.option{ position:relative; display:flex; align-items:center; gap:12px; padding:14px 16px; border-radius:14px;
  border:2px solid transparent; background:var(--panel); box-shadow:0 8px 20px rgba(37,99,235,.08); cursor:pointer; transition:.18s }
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

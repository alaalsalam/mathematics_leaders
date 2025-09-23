<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { Check, RotateCcw, RefreshCw } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

const copy = {
  ar:{
    title:'المستوى الثالث – التحدي 3: خطوط المجموع العشري',
    rule:'اختر أرقامًا متجاورة على خط مستقيم (أفقي، عمودي أو قطري) بحيث يساوي مجموعها القيمة المطلوبة.',
    targetLabel:'المجموع المطلوب', selected:'المجموع الحالي',
    check:'تحقّق', reset:'إعادة اختيار', newQ:'سؤال جديد',
    needSelection:'اختر خانات أولاً.',
    wrongLine:'يجب أن تكون الخانات المختارة على خط مستقيم ومتجاورة.',
    wrongSum:'المجموع لا يساوي القيمة المطلوبة.',
    correct:'رائع! خط صحيح.',
  },
  en:{
    title:'Level 3 – Challenge 3: Decimal Sum Lines',
    rule:'Pick numbers lying on one straight line (horizontal, vertical, or diagonal) so their sum equals the target.',
    targetLabel:'Target sum', selected:'Current sum',
    check:'Check', reset:'Reset selection', newQ:'New puzzle',
    needSelection:'Select cells first.',
    wrongLine:'Selections must be contiguous on a straight line.',
    wrongSum:'The sum does not match the target.',
    correct:'Great! You found a valid line.',
  }
}
const L = computed(()=> (copy[props.lang]?props.lang:'ar'))

/* sounds */
import successUrl from '@/assets/sounds/success3.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

const puzzles = [
  {
    id: 'p1',
    target: 10,
    grid: [
      [1.2, 0.8, 2.5, 1.3, 0.9],
      [2.1, 3.4, 2.0, 0.6, 1.5],
      [1.8, 2.2, 1.5, 3.0, 1.1],
      [0.5, 1.6, 1.7, 2.0, 3.5],
      [1.4, 1.3, 2.3, 1.8, 2.7],
    ],
    solution: [
      { r:0, c:2 }, { r:1, c:2 }, { r:2, c:2 }, { r:3, c:2 }, { r:4, c:2 }
    ],
  },
  {
    id: 'p2',
    target: 10,
    grid: [
      [0.8, 1.7, 2.1, 0.9, 1.4],
      [2.6, 1.5, 1.9, 1.1, 2.9],
      [1.3, 2.4, 1.2, 2.2, 1.6],
      [0.7, 1.8, 2.5, 1.7, 2.3],
      [1.9, 0.6, 1.8, 2.6, 0.9],
    ],
    solution: [
      { r:1, c:0 }, { r:1, c:1 }, { r:1, c:2 }, { r:1, c:3 }, { r:1, c:4 }
    ],
  },
  {
    id: 'p3',
    target: 10,
    grid: [
      [2.5, 1.1, 0.8, 1.4, 1.2],
      [0.9, 2.0, 1.3, 1.7, 1.0],
      [1.6, 1.2, 1.8, 1.1, 1.3],
      [1.4, 1.9, 1.5, 1.5, 1.8],
      [1.3, 1.4, 0.9, 1.6, 2.2],
    ],
    solution: [
      { r:0, c:0 }, { r:1, c:1 }, { r:2, c:2 }, { r:3, c:3 }, { r:4, c:4 }
    ],
  },
]

const currentPuzzle = ref(puzzles[0])
const selected = ref(new Set())
const solved = ref(false)
const feedback = ref(null)

function coordKey(r,c){ return `${r},${c}` }

function resetSelection(){
  selected.value = new Set()
  solved.value = false
  feedback.value = null
}

function pickPuzzle(){
  const next = puzzles[Math.floor(Math.random()*puzzles.length)]
  currentPuzzle.value = next
  resetSelection()
}

function toggleCell(r,c){
  const key = coordKey(r,c)
  const set = new Set(selected.value)
  if(set.has(key)) set.delete(key)
  else set.add(key)
  selected.value = set
  solved.value = false
  feedback.value = null
}

const selectedList = computed(()=> Array.from(selected.value).map(item => {
  const [r,c] = item.split(',').map(Number)
  return { r, c }
}))

const selectedSum = computed(()=> selectedList.value.reduce((total, cell)=> total + currentPuzzle.value.grid[cell.r][cell.c], 0))

function isLine(cells){
  if(cells.length < 2) return true
  const rows = cells.map(c=>c.r)
  const cols = cells.map(c=>c.c)
  const sameRow = rows.every(r=>r===rows[0])
  const sameCol = cols.every(c=>c===cols[0])
  const diag1 = rows.every((r,idx)=> r - cols[idx] === rows[0] - cols[0])
  const diag2 = rows.every((r,idx)=> r + cols[idx] === rows[0] + cols[0])

  if(!sameRow && !sameCol && !diag1 && !diag2) return false

  const sorted = [...cells]
  if(sameRow){
    sorted.sort((a,b)=> a.c - b.c)
    for(let i=1;i<sorted.length;i++) if(sorted[i].c - sorted[i-1].c !== 1) return false
    return true
  }
  if(sameCol){
    sorted.sort((a,b)=> a.r - b.r)
    for(let i=1;i<sorted.length;i++) if(sorted[i].r - sorted[i-1].r !== 1) return false
    return true
  }
  if(diag1){
    sorted.sort((a,b)=> a.r - b.r)
    for(let i=1;i<sorted.length;i++){
      if(sorted[i].r - sorted[i-1].r !== 1) return false
      if(sorted[i].c - sorted[i-1].c !== 1) return false
    }
    return true
  }
  // diag2
  sorted.sort((a,b)=> a.r - b.r)
  for(let i=1;i<sorted.length;i++){
    if(sorted[i].r - sorted[i-1].r !== 1) return false
    if(sorted[i-1].c - sorted[i].c !== 1) return false
  }
  return true
}

async function addPoint(){
  try{
    await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'})
  }catch{}
}

async function checkLine(){
  if(!selected.size){
    feedback.value = copy[L.value].needSelection
    sWrong && sWrong.play()
    return
  }
  const cells = selectedList.value
  if(!isLine(cells)){
    feedback.value = copy[L.value].wrongLine
    sWrong && sWrong.play()
    return
  }
  const sum = selectedSum.value
  if(Math.abs(sum - currentPuzzle.value.target) > 1e-6){
    feedback.value = copy[L.value].wrongSum
    sWrong && sWrong.play()
    return
  }
  solved.value = true
  feedback.value = copy[L.value].correct
  sOK && sOK.play(); sClap && sClap.play()
  await addPoint()
}

function isSolutionCell(r,c){
  return currentPuzzle.value.solution.some(cell => cell.r===r && cell.c===c)
}
</script>

<template>
  <div class="lvl3c3" :data-theme="props.theme">
    <header class="head">
      <h2 class="title">{{ copy[L].title }}</h2>
      <p class="rule">{{ copy[L].rule }}</p>
    </header>

    <section class="status">
      <div class="chip target">{{ copy[L].targetLabel }}: <strong>{{ currentPuzzle.target.toFixed(1) }}</strong></div>
      <div class="chip sum">{{ copy[L].selected }}: <strong>{{ selectedSum.toFixed(1) }}</strong></div>
    </section>

    <section class="grid">
      <div
        v-for="(row,r) in currentPuzzle.grid"
        :key="r"
        class="row"
      >
        <button
          v-for="(value,c) in row"
          :key="c"
          class="cell"
          :class="{ selected: selected.has(coordKey(r,c)), success: solved && isSolutionCell(r,c) }"
          @click="toggleCell(r,c)"
        >
          {{ value.toFixed(1) }}
        </button>
      </div>
    </section>

    <section class="actions">
      <button class="btn" @click="checkLine"><Check class="ic" /> {{ copy[L].check }}</button>
      <button class="btn" @click="resetSelection"><RotateCcw class="ic" /> {{ copy[L].reset }}</button>
      <button class="btn" @click="pickPuzzle"><RefreshCw class="ic" /> {{ copy[L].newQ }}</button>
    </section>

    <transition name="fade">
      <div v-if="feedback" class="feedback" :class="{ ok: solved }">{{ feedback }}</div>
    </transition>
  </div>
</template>

<style scoped>
.lvl3c3{ --fg:#0f172a; --bg:#f8fafc; --panel:#ffffff; --bd:#dbeafe; --accent:#dc2626;
  padding:24px; border-radius:18px; background:var(--bg); color:var(--fg); box-shadow:0 12px 28px rgba(15,23,42,.08) }
[data-theme="dark"] .lvl3c3{ --fg:#e2e8f0; --bg:#0b1220; --panel:#111a2b; --bd:#1e293b; --accent:#fb7185 }

.head{ margin-bottom:18px }
.title{ margin:0 0 8px; font-size:1.5rem; font-weight:700 }
.rule{ margin:0; opacity:.75 }

.status{ display:flex; gap:12px; flex-wrap:wrap; margin-bottom:20px }
.chip{ padding:8px 14px; border-radius:999px; background:var(--panel); border:1px solid var(--bd);
  box-shadow:0 6px 16px rgba(15,23,42,.08); font-size:.95rem }
.chip strong{ font-weight:700 }

.grid{ display:flex; flex-direction:column; gap:6px; margin-bottom:20px }
.row{ display:grid; grid-template-columns:repeat(auto-fit, minmax(70px,1fr)); gap:6px }
.cell{ padding:16px 0; border-radius:12px; border:1px solid var(--bd); background:var(--panel);
  font-size:1.2rem; font-weight:600; cursor:pointer; transition:.15s; font-variant-numeric:tabular-nums }
.cell:hover{ transform:translateY(-1px); box-shadow:0 10px 24px rgba(15,23,42,.12) }
.cell.selected{ background:rgba(59,130,246,.15); border-color:#60a5fa }
.cell.success{ background:rgba(74,222,128,.18); border-color:#22c55e }

.actions{ display:flex; gap:12px; flex-wrap:wrap; margin-bottom:18px }
.btn{ display:inline-flex; align-items:center; gap:8px; padding:10px 18px; border-radius:12px;
  border:1px solid var(--bd); background:var(--panel); cursor:pointer; transition:.15s; font-weight:600 }
.btn:hover{ transform:translateY(-1px); box-shadow:0 10px 24px rgba(15,23,42,.12) }
.ic{ width:18px; height:18px }

.feedback{ padding:12px 18px; border-radius:12px; border:1px solid #fee2e2; background:#fff1f2; color:#b91c1c; font-weight:600 }
.feedback.ok{ border-color:#bbf7d0; background:#dcfce7; color:#166534 }
[data-theme="dark"] .feedback{ background:rgba(239,68,68,.15); border-color:rgba(239,68,68,.4); color:#fecaca }
[data-theme="dark"] .feedback.ok{ background:rgba(34,197,94,.2); border-color:rgba(34,197,94,.45); color:#bbf7d0 }

.fade-enter-active,.fade-leave-active{ transition:opacity .2s }
.fade-enter-from,.fade-leave-to{ opacity:0 }
</style>

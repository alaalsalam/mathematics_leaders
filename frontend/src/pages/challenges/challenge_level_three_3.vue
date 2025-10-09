<script setup>
import { ref, computed, onMounted } from 'vue'
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

/* --------- helpers: 1-decimal numbers --------- */
function r01(n){ return Math.round(n*10)/10 }
function randDec(min=0.8,max=2.6){ return r01(min + Math.random()*(max-min)) }

/* --------- puzzle generator --------- */
function genLineCells(type){
  // returns array of {r,c} for 5 contiguous cells
  const idx = Math.floor(Math.random()*5)
  if(type==='row') return Array.from({length:5},(_,c)=>({r:idx,c}))
  if(type==='col') return Array.from({length:5},(_,r)=>({r,c:idx}))
  if(type==='diagMain') return Array.from({length:5},(_,i)=>({r:i,c:i}))
  // diag anti
  return Array.from({length:5},(_,i)=>({r:i,c:4-i}))
}

function makePuzzle(id){
  const targetChoices = [9.0,9.3,9.6,9.9,10.0,10.2]  // تنويع أهداف
  const target = targetChoices[Math.floor(Math.random()*targetChoices.length)]
  const grid = Array.from({length:5},()=> Array.from({length:5},()=> randDec()))
  const types = ['row','col','diagMain','diagAnti']
  const type = types[Math.floor(Math.random()*types.length)]
  const solution = genLineCells(type)

  // اختر 4 قيم عشوائية للخط ثم احسب الخامسة لضبط المجموع
  let chosen = solution.map(()=> randDec())
  // اضبط الأربع الأولى واحتفظ بالخامسة للحساب
  const sum4 = r01(chosen.slice(0,4).reduce((a,b)=>a+b,0))
  let last = r01(target - sum4)

  // حاول إبقاء الرقم ضمن حدود معقولة، وإلا أعد التوليد البسيط
  let tries = 0
  while((last < 0.5 || last > 3.0) && tries<20){
    chosen = solution.map(()=> randDec())
    const s4 = r01(chosen.slice(0,4).reduce((a,b)=>a+b,0))
    last = r01(target - s4)
    tries++
  }
  chosen[4] = r01(last)

  // ضع القيم في الشبكة
  solution.forEach((cell,i)=>{ grid[cell.r][cell.c] = chosen[i] })

  return { id, target, grid, solution }
}

function generateMany(n=50){
  const arr = []
  for(let i=1;i<=n;i++) arr.push(makePuzzle('p'+i))
  return arr
}

/* --------- state --------- */
const puzzles = ref(generateMany(50))   // عدّل الرقم كما تريد
const currentPuzzle = ref(puzzles.value[0])
const lastPuzzleId = ref(null)
const selected = ref(new Set())
const solved = ref(false)
const feedback = ref(null)

function coordKey(r,c){ return `${r},${c}` }

function pickNextPuzzle(){
  const list = puzzles.value
  if(list.length===1){ lastPuzzleId.value = list[0].id; return list[0] }
  let candidate
  do{ candidate = list[Math.floor(Math.random()*list.length)] }while(candidate.id===lastPuzzleId.value)
  lastPuzzleId.value = candidate.id
  return candidate
}

function resetSelection(){ selected.value=new Set(); solved.value=false; feedback.value=null }
function pickPuzzle(){ currentPuzzle.value = pickNextPuzzle(); resetSelection() }

function toggleCell(r,c){
  const key = coordKey(r,c)
  const set = new Set(selected.value)
  set.has(key) ? set.delete(key) : set.add(key)
  selected.value = set
  solved.value = false
  feedback.value = null
}

const selectedList = computed(()=> Array.from(selected.value).map(s=>{
  const [r,c] = s.split(',').map(Number); return {r,c}
}))
const selectedSum = computed(()=> r01(selectedList.value.reduce((tot,cell)=> tot + currentPuzzle.value.grid[cell.r][cell.c], 0)))

function isLine(cells){
  if(cells.length<2) return true
  const rows = cells.map(c=>c.r), cols = cells.map(c=>c.c)
  const sameRow = rows.every(r=>r===rows[0])
  const sameCol = cols.every(c=>c===cols[0])
  const diag1 = rows.every((r,i)=> r - cols[i] === rows[0] - cols[0])
  const diag2 = rows.every((r,i)=> r + cols[i] === rows[0] + cols[0])
  if(!sameRow && !sameCol && !diag1 && !diag2) return false
  const sorted = [...cells]
  if(sameRow){ sorted.sort((a,b)=>a.c-b.c); for(let i=1;i<sorted.length;i++) if(sorted[i].c-sorted[i-1].c!==1) return false; return true }
  if(sameCol){ sorted.sort((a,b)=>a.r-b.r); for(let i=1;i<sorted.length;i++) if(sorted[i].r-sorted[i-1].r!==1) return false; return true }
  if(diag1){ sorted.sort((a,b)=>a.r-b.r); for(let i=1;i<sorted.length;i++){ if(sorted[i].r-sorted[i-1].r!==1) return false; if(sorted[i].c-sorted[i-1].c!==1) return false } return true }
  sorted.sort((a,b)=>a.r-b.r); for(let i=1;i<sorted.length;i++){ if(sorted[i].r-sorted[i-1].r!==1) return false; if(sorted[i-1].c-sorted[i].c!==1) return false } return true
}

async function addPoint(){ try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{} }

async function checkLine(){
  if(!selected.value.size){ feedback.value = copy[L.value].needSelection; sWrong&&sWrong.play(); return }
  const cells = selectedList.value
  if(!isLine(cells)){ feedback.value = copy[L.value].wrongLine; sWrong&&sWrong.play(); return }
  if(Math.abs(selectedSum.value - currentPuzzle.value.target) > 1e-6){ feedback.value = copy[L.value].wrongSum; sWrong&&sWrong.play(); return }
  solved.value = true
  feedback.value = copy[L.value].correct
  sOK&&sOK.play(); sClap&&sClap.play()
  await addPoint()
}

function isSolutionCell(r,c){ return currentPuzzle.value.solution.some(cell=>cell.r===r && cell.c===c) }

onMounted(()=>{ pickPuzzle() })
</script>

<template>
  <div class="lvl3c3 challenge-surface" :data-theme="props.theme">
    <header class="head">
      <h2 class="title">{{ copy[L].title }}</h2>
      <p class="rule">{{ copy[L].rule }}</p>
    </header>

    <section class="status">
      <div class="chip target">{{ copy[L].targetLabel }}: <strong>{{ currentPuzzle.target.toFixed(1) }}</strong></div>
      <div class="chip sum">{{ copy[L].selected }}: <strong>{{ selectedSum.toFixed(1) }}</strong></div>
    </section>

    <section class="grid">
      <div v-for="(row,r) in currentPuzzle.grid" :key="r" class="row">
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

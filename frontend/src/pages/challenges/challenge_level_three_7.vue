<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw } from 'lucide-vue-next'

const props = defineProps({ lang:{ type:String, default:'ar' }, theme:{ type:String, default:'light' } })

const copy = {
  ar:{
    title:'المستوى الثالث – التحدي 7: مسار الضرب',
    intro:'ابدأ من النقطة أ ثم اختر نقاطًا متصلة للوصول إلى ب بحيث يكون حاصل ضرب الأرقام على الأضلاع مساويًا للقيمة المطلوبة.',
    target:'القيمة المطلوبة', current:'الحاصل الحالي',
    check:'تحقّق', reset:'مسح آخر نقطة', newQ:'تحدٍ جديد', clearAll:'إعادة المسار',
    needStart:'ابدأ من النقطة أ.', invalid:'يجب اختيار نقطة متصلة.', wrong:'المسار لا يعطي القيمة المطلوبة.', correct:'أحسنت! المسار يعطي القيمة المطلوبة.'
  },
  en:{
    title:'Level 3 – Challenge 7: Multiplication Path',
    intro:'Start at point A and travel along connected nodes to reach B so the product of edge values equals the required target.',
    target:'Target product', current:'Current product',
    check:'Check', reset:'Undo last', newQ:'New challenge', clearAll:'Clear path',
    needStart:'Start from node A.', invalid:'Pick a connected node.', wrong:'Path does not meet the target.', correct:'Great! The path matches the target.'
  }
}
const L = computed(() => (copy[props.lang] ? props.lang : 'ar'))

/* sounds */
import successUrl from '@/assets/sounds/success3.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong3.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

/* ---------------- مولّد ألغاز كثيرة ---------------- */
function rnd(a,b){ return Math.random()*(b-a)+a }
function pick(arr){ return arr[Math.floor(Math.random()*arr.length)] }
function round2(x){ return Math.round(x*100)/100 }

const baseNodes = [
  { id:'A', label:'أ', x:420, y:150, type:'start' },
  { id:'B', label:'ب', x:80,  y:150, type:'end'  },
  { id:'RT', x:340, y:95 },
  { id:'RB', x:340, y:205 },
  { id:'CT', x:260, y:70 },
  { id:'C',  x:260, y:150 },
  { id:'CB', x:260, y:230 },
  { id:'LT', x:180, y:100 },
  { id:'LB', x:180, y:205 }
]

// شبكة وصلات ثابتة كافية لتنوع المسارات
const skeletonEdges = [
  ['A','RT'],['A','RB'],
  ['RT','CT'],['RT','C'],
  ['CT','C'],['CT','CB'],
  ['C','LT'],['C','LB'],['C','CB'],
  ['LT','B'],['LB','B'],
  ['RB','CB']
]

// أشكال مسارات صحيحة محتملة من A إلى B
const pathShapes = [
  ['A','RT','CT','C','LT','B'],
  ['A','RT','C','LT','B'],
  ['A','RB','CB','C','LB','B'],
  ['A','RB','CB','C','LT','B'],
  ['A','RT','CT','CB','C','LB','B']
]

// قيم الأوزان المحتملة
const weightPool = [0.5,0.6,0.8,0.9,1.0,1.1,1.2,1.25,1.3,1.4,1.5,1.6,1.7,1.8,2.0]

function genOnePuzzle(id){
  const nodes = JSON.parse(JSON.stringify(baseNodes))
  const path = pick(pathShapes)

  // امنح أوزانًا لمسار الحل أولًا لتحكم بالهدف
  const w = []
  for(let i=0;i<path.length-1;i++){
    w.push(pick(weightPool))
  }
  const target = round2(w.reduce((a,b)=>a*b,1))

  // ابنِ جدول أوزان لكل ضلع
  const weights = new Map()
  for(let i=0;i<path.length-1;i++){
    const a = path[i], b = path[i+1]
    weights.set(`${a}-${b}`, w[i])
    weights.set(`${b}-${a}`, w[i])
  }
  // بقية الأضلاع أوزان عشوائية
  skeletonEdges.forEach(([u,v])=>{
    if(!weights.has(`${u}-${v}`)){
      const val = pick(weightPool)
      weights.set(`${u}-${v}`, val)
      weights.set(`${v}-${u}`, val)
    }
  })

  // كوّن قائمة الأضلاع بالاتجاهين مرة واحدة
  const edges = []
  const seen = new Set()
  skeletonEdges.forEach(([u,v])=>{
    const k = `${u}|${v}`
    if(seen.has(k)) return
    seen.add(k)
    edges.push({ from:u, to:v, value:weights.get(`${u}-${v}`) })
  })

  return { id, target, start:'A', end:'B', nodes, edges }
}

function generatePuzzles(n=40){
  const arr=[]
  for(let i=1;i<=n;i++) arr.push(genOnePuzzle('p'+i))
  return arr
}

/* ---------------- حالة اللعبة ---------------- */
const puzzles = ref(generatePuzzles(40))
function withCoords(edge, nodes){
  const from = nodes.find(n => n.id === edge.from)
  const to = nodes.find(n => n.id === edge.to)
  return { ...edge, x1: from.x, y1: from.y, x2: to.x, y2: to.y, midX:(from.x+to.x)/2, midY:(from.y+to.y)/2 }
}

const currentPuzzle = ref(puzzles.value[0])
const lastPuzzleId = ref(null)
const path = ref([]) // node ids
const feedback = ref(null)
const solved = ref(false)

const nodes = computed(() => currentPuzzle.value.nodes)
const edges = computed(() => currentPuzzle.value.edges.map(e => withCoords(e, nodes.value)))

const selectedEdges = computed(() => {
  const e = []
  for(let i=0;i<path.value.length-1;i++){
    const a = path.value[i], b = path.value[i+1]
    const edge = edges.value.find(ed => (ed.from===a && ed.to===b) || (ed.from===b && ed.to===a))
    if(edge) e.push(edge)
  }
  return e
})
const product = computed(() => selectedEdges.value.reduce((acc, ed) => acc * ed.value, 1))

function hasEdge(a,b){
  return edges.value.some(ed => (ed.from===a && ed.to===b) || (ed.from===b && ed.to===a))
}

function pickNextPuzzle(){
  const list = puzzles.value
  if(list.length===1){ lastPuzzleId.value=list[0].id; return list[0] }
  let c; do{ c=list[Math.floor(Math.random()*list.length)] }while(c.id===lastPuzzleId.value)
  lastPuzzleId.value=c.id; return c
}

function resetPath(){ path.value=[]; solved.value=false; feedback.value=null }
function undoLast(){ if(path.value.length){ path.value = path.value.slice(0,-1); solved.value=false; feedback.value=null } }

async function addPoint(){ try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{} }

function onNodeClick(node){
  const { start, end } = currentPuzzle.value
  if(!path.value.length){
    if(node.id !== start){ feedback.value = copy[L.value].needStart; sWrong&&sWrong.play(); return }
    path.value=[node.id]; feedback.value=null; return
  }
  const last = path.value[path.value.length-1]
  if(node.id===last) return
  if(!hasEdge(last,node.id)){ feedback.value=copy[L.value].invalid; sWrong&&sWrong.play(); return }
  path.value = path.value.concat(node.id); feedback.value=null
  if(node.id===end) checkPath()
}

async function checkPath(){
  const { end, target } = currentPuzzle.value
  if(path.value[path.value.length-1] !== end){ feedback.value=copy[L.value].wrong; sWrong&&sWrong.play(); return }
  if(Math.abs(product.value - target) < 1e-6){
    feedback.value=copy[L.value].correct; solved.value=true; sOK&&sOK.play(); sClap&&sClap.play(); await addPoint()
  }else{
    feedback.value=copy[L.value].wrong; solved.value=false; sWrong&&sWrong.play()
  }
}

function initPuzzle(){ currentPuzzle.value = pickNextPuzzle(); resetPath() }

onMounted(initPuzzle)
watch(() => props.lang, () => { if(!solved.value) feedback.value = null })
</script>

<template>
  <div class="lvl3c8 challenge-surface" :data-theme="props.theme">
    <header class="head">
      <h2 class="title">{{ copy[L].title }}</h2>
      <p class="intro">{{ copy[L].intro }}</p>
    </header>

    <section class="status">
      <div class="chip">{{ copy[L].target }}: <strong>{{ currentPuzzle.target }}</strong></div>
      <div class="chip">{{ copy[L].current }}: <strong>{{ product.toFixed(3) }}</strong></div>
    </section>

    <section class="graph">
      <svg viewBox="0 0 500 300">
        <g v-for="edge in edges" :key="edge.from + edge.to">
          <line :x1="edge.x1" :y1="edge.y1" :x2="edge.x2" :y2="edge.y2" :class="['edge', { active: selectedEdges.includes(edge) }]" />
          <text :x="edge.midX" :y="edge.midY" class="edge-label">{{ edge.value }}</text>
        </g>
        <g v-for="node in nodes" :key="node.id" class="node" @click="onNodeClick(node)">
          <circle :cx="node.x" :cy="node.y" :r="node.type ? 20 : 12" :class="['point', node.type, { selected: path.includes(node.id) }]" />
          <text :x="node.x" :y="node.y + 4" class="node-label">{{ node.label || '' }}</text>
        </g>
      </svg>
    </section>

    <section class="controls">
      <button class="btn" @click="checkPath"><Check class="ic" /> {{ copy[L].check }}</button>
      <button class="btn" @click="undoLast"><RotateCcw class="ic" /> {{ copy[L].reset }}</button>
      <button class="btn" @click="resetPath"><RefreshCw class="ic" /> {{ copy[L].clearAll }}</button>
      <button class="btn" @click="initPuzzle"><RefreshCw class="ic" /> {{ copy[L].newQ }}</button>
    </section>

    <transition name="fade">
      <div v-if="feedback" class="feedback" :class="{ ok: solved }">{{ feedback }}</div>
    </transition>
  </div>
</template>

<style scoped>
.lvl3c8{ --fg:#111827; --bg:#f0f9ff; --panel:#ffffff; --bd:#bae6fd; --accent:#2563eb;
  padding:24px; border-radius:18px; background:var(--bg); color:var(--fg); box-shadow:0 16px 36px rgba(37,99,235,.12) }
[data-theme="dark"] .lvl3c8{ --fg:#e2e8f0; --bg:#0b1424; --panel:#12203b; --bd:#1d4ed8; --accent:#60a5فا }

.head{ margin-bottom:20px }
.title{ margin:0 0 10px; font-size:1.55rem; font-weight:700 }
.intro{ margin:0; opacity:.85; line-height:1.55 }

.status{ display:flex; gap:12px; flex-wrap:wrap; margin-bottom:18px }
.chip{ padding:8px 14px; border-radius:999px; background:var(--panel); border:1px solid var(--bd); box-shadow:0 6px 16px rgba(15,23,42,.08); font-weight:600 }
.chip strong{ font-weight:700 }

.graph{ background:var(--panel); border:1px solid var(--bd); border-radius:16px; padding:16px; box-shadow:0 12px 28px rgba(15,23,42,.12); margin-bottom:20px }
svg{ width:100%; height:auto }
.edge{ stroke:#3b82f6; stroke-width:4; stroke-linecap:round; opacity:.6; transition:.15s }
.edge.active{ stroke:#2563eb; opacity:1 }
.edge-label{ fill:var(--fg); font-size:12px; text-anchor:middle; dominant-baseline:middle; font-weight:600 }
.node{ cursor:pointer }
.point{ fill:#1d4ed8; stroke:#fff; stroke-width:2; transition:.15s }
.point.start, .point.end{ fill:#fde68a; stroke:#fbbf24; stroke-width:3 }
.point.selected{ stroke:var(--accent); stroke-width:4 }
.node-label{ fill:var(--fg); font-weight:700; font-size:14px; text-anchor:middle }

.controls{ display:flex; gap:12px; flex-wrap:wrap }
.btn{ display:inline-flex; align-items:center; gap:8px; padding:10px 18px; border-radius:12px; border:1px solid var(--bd); background:var(--panel); font-weight:700; cursor:pointer; transition:.15s }
.btn:hover{ transform:translateY(-1px); box-shadow:0 12px 24px rgba(15,23,42,.12) }
.ic{ width:18px; height:18px }

.feedback{ margin-top:18px; padding:12px 18px; border-radius:12px; border:1px solid #fecaca; background:#fee2e2; color:#b91c1c; font-weight:700; text-align:center }
.feedback.ok{ border-color:#bbf7d0; background:#dcfce7; color:#166534 }
[data-theme="dark"] .feedback{ background:rgba(248,113,113,.18); border-color:rgba(248,113,113,.45); color:#fecaca }
[data-theme="dark"] .feedback.ok{ background:rgba(34,197,94,.22); border-color:rgba(34,197,94,.5); color:#bbf7d0 }

.fade-enter-active,.fade-leave-active{ transition:opacity .2s }
.fade-enter-from,.fade-leave-to{ opacity:0 }
</style>

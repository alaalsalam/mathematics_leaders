<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Circle, Square, Triangle, Diamond } from 'lucide-vue-next'

/* ===== props ===== */
const props = defineProps({
  lang:  { type: String, default: 'ar' },
  theme: { type: String, default: 'light' }
})
const lang  = ref(props.lang)
const theme = ref(props.theme)
watch(()=>props.lang,  v=> lang.value  = v)
watch(()=>props.theme, v=> theme.value = v)

/* ===== GET ===== */
async function get(url, params = {}) {
  const qs = new URLSearchParams(params).toString()
  const r  = await fetch(url + (qs ? `?${qs}` : ''), { method:'GET', credentials:'include' })
  const data = await r.json().catch(()=> ({}))
  if(!r.ok) throw data
  return data
}

/* ===== i18n ===== */
const dir  = computed(() => (lang.value === 'ar' ? 'rtl' : 'ltr'))
const T = {
  ar:{title:'التحدي 1: عملية جمع عمودية بأرقام مفقودة (رموز)',subtitle:'اسحب الأرقام وضعها مكان الرموز حتى تكتمل العملية.',digits:'الأرقام',check:'تحقق',reset:'إعادة ضبط',newQ:'سؤال جديد',correctBig:'أحسنت!',correctSub:'حل صحيح 👏 لقد كسبت نقطة.',wrong:'حاول مرة أخرى 🤔'},
  en:{title:'Challenge 1: Column addition with missing (symbol) digits',subtitle:'Drag digits onto symbols until the addition becomes correct.',digits:'Digits',check:'Check',reset:'Reset',newQ:'New Question',correctBig:'Great!',correctSub:'Correct 👏 You earned a point.',wrong:'Try again 🤔'}
}
const t = (k)=>T[lang.value][k]

/* ===== sounds ===== */
import successUrl from '@/assets/sounds/success.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong.mp3'

const sndSuccess = new Audio(successUrl)
const sndClap    = new Audio(clapUrl)
const sndWrong   = new Audio(wrongUrl)

sndSuccess.preload = 'auto'
sndClap.preload    = 'auto'
sndWrong.preload   = 'auto'

/* ===== shapes (lucide) ===== */
const SHAPE_COMP = { circle: Circle, square: Square, triangle: Triangle, diamond: Diamond }
const SHAPE_TYPES = ['circle','square','triangle','diamond']
const shapeComp = t => SHAPE_COMP[t] || Circle

/* ===== utils ===== */
function rndInt(a,b){ return a + Math.floor(Math.random()*(b-a+1)) }
function shuffle(a){ return a.slice().sort(()=>Math.random()-0.5) }

/* ===== state ===== */
const q     = reactive({ aStr:'', bStr:'', sStr:'', hiddenMap:{}, assignMap:{}, usedShapes:[] })
const rowA  = ref([])   // tokens
const rowB  = ref([])
const rowS  = ref([])

/* ===== generate puzzle ===== */
function newPuzzle(){
  // 1) أرقام عشوائية
  const dA = rndInt(2,3), dB = rndInt(2,3)
  const A  = rndInt(10**(dA-1), 10**dA-1)
  const B  = rndInt(10**(dB-1), 10**dB-1)
  const S  = A + B
  q.aStr = String(A); q.bStr = String(B); q.sStr = String(S)

  // 2) اختر الأرقام المخفية فقط من الأرقام الظاهرة فعلاً
  const digitsPresent = Array.from(new Set((q.aStr+q.bStr+q.sStr).split('').map(n=>+n)))
  const howMany       = Math.min(rndInt(2,3), digitsPresent.length)
  const hideDigits    = shuffle(digitsPresent).slice(0, howMany)
  const typesPicked   = shuffle(SHAPE_TYPES).slice(0, howMany)

  q.hiddenMap = {}
  hideDigits.forEach((d,i)=>{ q.hiddenMap[typesPicked[i]] = d })

  // 3) كوّن التوكنز وحدد الأشكال المستخدمة فعلياً
  const used = new Set()
  function tokenize(str){
    return str.split('').map(ch=>{
      const d  = +ch
      const sh = Object.entries(q.hiddenMap).find(([k,v])=>v===d)?.[0]
      if (sh){ used.add(sh); return {t:'shape', v:sh} }
      return {t:'digit', v:ch}
    })
  }
  rowA.value = tokenize(q.aStr)
  rowB.value = tokenize(q.bStr)
  rowS.value = tokenize(q.sStr)

  // 4) لا نعرض إلا الأشكال الموجودة فعلياً
  q.usedShapes = Array.from(used)
  q.assignMap  = Object.fromEntries(q.usedShapes.map(s=>[s,null]))

  // ضمان وجود شكل واحد على الأقل
  if(q.usedShapes.length===0) newPuzzle()
}

/* ===== DnD ===== */
function onDigitDragStart(e, digit){ e.dataTransfer.setData('text/plain', String(digit)) }
function onShapeDrop(e, shape){
  const d = Number(e.dataTransfer.getData('text/plain'))
  if(Number.isNaN(d)) return
  if(Object.values(q.assignMap).includes(d) && q.assignMap[shape]!==d) return
  q.assignMap[shape] = d
  checkNow()
}
function onDragOver(e){ e.preventDefault() }
function resetAssign(){ Object.keys(q.assignMap).forEach(sh=> q.assignMap[sh]=null) }

/* ===== check ===== */
const isFilled = computed(()=> q.usedShapes.every(sh => Number.isInteger(q.assignMap[sh])) )
function makeNumber(tokens){
  return Number(tokens.map(tok => tok.t==='digit' ? tok.v : (q.assignMap[tok.v] ?? '?')).join(''))
}
function isCorrect(){
  if(!isFilled.value) return false
  const A = makeNumber(rowA.value), B = makeNumber(rowB.value), S = makeNumber(rowS.value)
  return !([A,B,S].some(v => String(v).includes('?'))) && (A+B===S)
}

const overlay = reactive({ open:false, good:true })
async function checkNow(){
  if(!isFilled.value) return
  if(isCorrect()){
    try{ sndSuccess.currentTime=0; sndSuccess.play().catch(()=>{}) }catch{}
    try{ sndClap.currentTime=0; sndClap.play().catch(()=>{}) }catch{}
    overlay.open = true; overlay.good = true
    get('/api/method/mathematics_leaders.api.game_points.add_point', { amount: 1 }).catch(()=>{})
  }else{
    try{ sndWrong.currentTime=0; sndWrong.play().catch(()=>{}) }catch{}
    pushToast(t('wrong'),'warn')
  }
}
function nextQuestion(){ overlay.open=false; newPuzzle() }

/* ===== Toast ===== */
const toasts = ref([])
function pushToast(msg,type='ok'){
  const id = Math.random().toString(36).slice(2)
  toasts.value.push({id,msg,type})
  setTimeout(()=> toasts.value = toasts.value.filter(x=>x.id!==id), 1800)
}

/* init */
onMounted(()=> newPuzzle())
</script>

<template>
  <section class="wrap challenge-surface" :dir="dir" :data-theme="theme">
    <header class="hdr">
      <h2>{{ t('title') }}</h2>
      <p class="sub">{{ t('subtitle') }}</p>
    </header>

    <div class="board">
      <!-- فتحات القيم (تظهر فقط للأشكال الموجودة) -->
      <div class="assign" dir="ltr">
        <div v-for="sh in q.usedShapes" :key="sh" class="slot" @drop="onShapeDrop($event, sh)" @dragover="onDragOver">
          <component :is="shapeComp(sh)" class="shape-ico" :size="26" stroke="var(--shape-stroke)" :stroke-width="2" :style="{fill:'var(--shape-fill)'}" />
          <div class="val" :class="{empty: q.assignMap[sh]==null}">
            {{ q.assignMap[sh]==null ? '…' : q.assignMap[sh] }}
          </div>
        </div>
        <div class="actions">
          <button class="ghost" @click="resetAssign">{{ t('reset') }}</button>
          <button class="primary" :disabled="!isFilled" @click="checkNow">{{ t('check') }}</button>
          <button class="ghost" @click="newPuzzle">{{ t('newQ') }}</button>
        </div>
      </div>

      <!-- عملية الجمع: اتجاه LTR ثابت للأرقام -->
      <div class="col-sum" dir="ltr">
        <div class="row">
          <span v-for="(tok,i) in rowA" :key="'a'+i" class="cell" :class="tok.t">
            <span v-if="tok.t==='digit'">{{ tok.v }}</span>
            <component v-else :is="shapeComp(tok.v)" class="shape-ico" :size="26" stroke="var(--shape-stroke)" :stroke-width="2" :style="{fill:'var(--shape-fill)'}" />
          </span>
        </div>
        <div class="row plus"><span>+</span></div>
        <div class="row">
          <span v-for="(tok,i) in rowB" :key="'b'+i" class="cell" :class="tok.t">
            <span v-if="tok.t==='digit'">{{ tok.v }}</span>
            <component v-else :is="shapeComp(tok.v)" class="shape-ico" :size="26" stroke="var(--shape-stroke)" :stroke-width="2" :style="{fill:'var(--shape-fill)'}" />
          </span>
        </div>
        <div class="line"></div>
        <div class="row">
          <span v-for="(tok,i) in rowS" :key="'s'+i" class="cell" :class="tok.t">
            <span v-if="tok.t==='digit'">{{ tok.v }}</span>
            <component v-else :is="shapeComp(tok.v)" class="shape-ico" :size="26" stroke="var(--shape-stroke)" :stroke-width="2" :style="{fill:'var(--shape-fill)'}" />
          </span>
        </div>
      </div>

      <div class="digits" dir="ltr">
        <h4>{{ t('digits') }}</h4>
        <div class="tiles">
          <button v-for="d in 10" :key="d-1" class="tile" draggable="true" @dragstart="onDigitDragStart($event, d-1)">{{ d-1 }}</button>
        </div>
      </div>
    </div>

    <transition name="fade">
      <div v-if="overlay.open" class="overlay">
        <div class="sheet">
          <div class="big">{{ t('correctBig') }}</div>
          <p>{{ t('correctSub') }}</p>
          <button class="primary" @click="nextQuestion">{{ t('newQ') }}</button>
        </div>
      </div>
    </transition>

    <div class="toasts">
      <div v-for="t in toasts" :key="t.id" class="toast" :class="t.type">{{ t.msg }}</div>
    </div>
  </section>
</template>

<style scoped>
/* ألوان افتراضية (فاتح) */
.wrap{
  --shape-fill:#FFC24B; --shape-stroke:#7a2a23;
  --ink:#2b1a1a; --peach:#ffe7db; --accent:#d64c42;
  --panel:#ffffff; --bd:#f1d8cf; --bg:linear-gradient(180deg,#fffaf6,#fff4e9);
  color:var(--ink); background:var(--bg); min-height:100%; padding:24px
}
.wrap[data-theme="dark"]{
  --shape-fill:#ffb84f; --shape-stroke:#ff8c7a;
  --ink:#f7ebe7; --peach:#2a1714; --accent:#ff8c7a;
  --panel:rgba(24,15,13,.85); --bd:#3c2722;
  --bg:linear-gradient(180deg,#1b1412,#241815);
}

.hdr h2{margin:0;font-weight:800;color:#5a261f}
.wrap[data-theme="dark"] .hdr h2{color:#ffc3ba}
.hdr .sub{margin:6px 0 18px;opacity:.75}

.board{display:grid;grid-template-columns:1fr auto 1fr;gap:22px;align-items:start}
.assign,.col-sum,.digits{background:var(--panel);border:1px solid var(--bd);border-radius:14px;box-shadow:0 10px 24px rgba(214,76,66,.10)}
.assign{padding:12px}
.col-sum{padding:18px 22px;min-width:260px}
.digits{padding:12px}

/* ثبّت اتجاه الأرقام */
.assign, .col-sum, .digits, .val, .tile { direction:ltr; unicode-bidi:isolate; }
.cell, .val, .tile { font-variant-numeric: tabular-nums; }

.slot{display:flex;align-items:center;gap:10px;padding:10px;border:1px dashed var(--bd);border-radius:12px;background:#fff;margin-bottom:8px}
.wrap[data-theme="dark"] .slot{background:#2a1a16}
.shape-ico{width:26px;height:26px;filter:drop-shadow(0 2px 4px rgba(0,0,0,.1))}
.val{margin-inline-start:auto;width:40px;height:34px;display:grid;place-items:center;font-weight:800;border-radius:10px;background:#fff4e9;border:1px solid var(--bd)}
.wrap[data-theme="dark"] .val{background:#1c1512}

.actions{display:flex;gap:10px;margin-top:6px}
button{border:none;cursor:pointer;padding:10px 14px;border-radius:12px;font-weight:700}
button.primary{background:var(--accent);color:#fff}
button.primary:disabled{opacity:.5;cursor:not-allowed}
button.ghost{background:#fff;border:1px solid var(--bd)}
.wrap[data-theme="dark"] button.ghost{background:#2a1a16}
button.tile{background:#fff;border:1px solid var(--bd);min-width:44px;height:44px;border-radius:12px;font-weight:800}
.wrap[data-theme="dark"] button.tile{background:#2a1a16}

.row{display:flex;gap:8px;justify-content:flex-end}
.row.plus{padding:6px 0;opacity:.7}
.cell{width:28px;height:28px;display:grid;place-items:center;font-weight:800;font-size:20px}
.line{height:2px;background:#d8b0a8;margin:8px 0 10px}

.digits h4{margin:0 0 10px 0}
.tiles{display:flex;flex-wrap:wrap;gap:8px}

.overlay{position:fixed;inset:0;background:rgba(0,0,0,.25);display:grid;place-items:center;z-index:40}
.sheet{width:min(560px,92vw);background:#fff;border-radius:18px;padding:26px;text-align:center;box-shadow:0 18px 40px rgba(0,0,0,.2)}
.wrap[data-theme="dark"] .sheet{background:#1c1512;color:var(--ink)}
.big{font-size:32px;font-weight:900;color:#4a2019}
.wrap[data-theme="dark"] .big{color:#ffc3ba}

.toasts{position:fixed;bottom:18px;inset-inline:0;display:grid;justify-content:center;gap:8px;z-index:50}
.toast{background:#fff;border:1px solid var(--bd);padding:10px 14px;border-radius:999px;box-shadow:0 8px 20px rgba(0,0,0,.08);font-weight:700}
.toast.warn{color:#7a2a23}
.fade-enter-active,.fade-leave-active{transition:opacity .15s}
.fade-enter-from,.fade-leave-to{opacity:0}

@media (max-width: 900px){
  .board{grid-template-columns:1fr}
  .col-sum{order:-1}
}
</style>

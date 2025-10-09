<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{ type:String, default:'ar' }, theme:{ type:String, default:'light' } })

const copy = {
  ar:{
    title:'المستوى الثالث – التحدي 6: كسر مكافئ ↔ كسر مكافئ',
    intro:'اسحب الأرقام المتاحة وضعها في خانات البسط والمقام لكسرين بحيث يكونان متكافئين.',
    left:'الكسر الأول', right:'الكسر المكافئ', bank:'البطاقات المتاحة',
    check:'تحقّق', reset:'مسح', newQ:'تحدٍ جديد', clear:'تفريغ',
    needAll:'املأ كل الخانات أولًا.', wrong:'الكسران غير متكافئين. جرّب ترتيبًا آخر.', correct:'أحسنت! الكسران متكافئان.'
  },
  en:{
    title:'Level 3 – Challenge 6: Fraction ↔ Equivalent Fraction',
    intro:'Drag digits into numerators and denominators so the two fractions are equivalent.',
    left:'Fraction A', right:'Equivalent Fraction', bank:'Available cards',
    check:'Check', reset:'Clear', newQ:'New challenge', clear:'Clear',
    needAll:'Fill all slots first.', wrong:'Fractions are not equivalent. Try another arrangement.', correct:'Great! The fractions are equivalent.'
  }
}
const L = computed(() => (copy[props.lang] ? props.lang : 'ar'))

/* sounds */
import successUrl from '@/assets/sounds/success2.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong2.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK&&(sOK.preload='auto'); sClap&&(sClap.preload='auto'); sWrong&&(sWrong.preload='auto')

/* ---------- بنك ألغاز: كسرين بكلٍ منهما خانة أو خانتان ---------- */
const P = (id, aNum, aDen, bNum, bDen, digits) => ({
  id,
  left: { num:{slots:['a1','a2'].slice(0, String(aNum).length), digits: String(aNum).split('')},
          den:{slots:['a3','a4'].slice(0, String(aDen).length), digits: String(aDen).split('')} },
  right:{ num:{slots:['b1','b2'].slice(0, String(bNum).length), digits: String(bNum).split('')},
          den:{slots:['b3','b4'].slice(0, String(bDen).length), digits: String(bDen).split('')} },
  digits
})

const puzzles = [
  P('p1', 1, 2, 2, 4, ['1','2','2','4']),
  P('p2', 2, 3, 4, 6, ['2','3','4','6']),
  P('p3', 3, 5, 6,10, ['3','5','6','1','0']),
  P('p4', 4, 7, 8,14, ['4','7','8','1','4']),
  P('p5', 5, 8,10,16, ['5','8','1','0','1','6']),
  P('p6', 3, 4, 9,12, ['3','4','9','1','2']),
  P('p7', 7,10,14,20, ['7','1','0','1','4','2','0']),
  P('p8', 9,12, 3, 4, ['9','1','2','3','4']),
  P('p9', 8, 9,16,18, ['8','9','1','6','1','8']),
  P('p10', 5,12,10,24, ['5','1','2','1','0','2','4']),
  P('p11', 2, 5, 6,15, ['2','5','6','1','5']),
  P('p12', 4, 9,12,27, ['4','9','1','2','2','7'])
]

/* ---------- حالة ---------- */
const currentPuzzle = ref(puzzles[0])
const placements = reactive({})
const requirements = reactive({})
const bankCounts = reactive({})
const feedback = ref(null)
const solved = ref(false)

/* ---------- تهيئة ---------- */
function resetMaps(){
  for(const m of [placements, requirements, bankCounts]) Object.keys(m).forEach(k=>delete m[k])
}
function initPuzzle(){
  const p = puzzles[Math.floor(Math.random()*puzzles.length)]
  currentPuzzle.value = p
  resetMaps(); feedback.value=null; solved.value=false

  ;['left','right'].forEach(side=>{
    const s = p[side]
    s.num.slots.forEach((slot,i)=>{ placements[slot]=null; requirements[slot]=s.num.digits[i] })
    s.den.slots.forEach((slot,i)=>{ placements[slot]=null; requirements[slot]=s.den.digits[i] })
  })
  p.digits.forEach(d=> bankCounts[d]=(bankCounts[d]||0)+1 )
}

/* ---------- DnD ---------- */
function allowDrop(e){ e.preventDefault() }
function onDragStart(e, d){ e.dataTransfer.setData('text/plain', d) }
function onDrop(e, slot){
  e.preventDefault()
  const d = e.dataTransfer.getData('text/plain')
  if(!d) return
  if((bankCounts[d]||0) <= 0 && placements[slot]!==d) return
  if(placements[slot]!=null){ const prev=placements[slot]; bankCounts[prev]=(bankCounts[prev]||0)+1 }
  if(placements[slot]!==d){ bankCounts[d]=(bankCounts[d]||0)-1; if(bankCounts[d]<0) bankCounts[d]=0 }
  placements[slot]=d; solved.value=false; feedback.value=null
}
function clearSlot(slot){
  if(placements[slot]!=null){
    const d=placements[slot]; bankCounts[d]=(bankCounts[d]||0)+1; placements[slot]=null
    solved.value=false; feedback.value=null
  }
}
const bankList = computed(()=>{
  const list=[]; for(const [d,c] of Object.entries(bankCounts)) for(let i=0;i<c;i++) list.push({digit:d,key:`${d}-${i}`})
  return list
})

/* ---------- حساب الكسور والتحقق ---------- */
function slotsFilled(){ return Object.keys(requirements).every(k=>placements[k]!=null) }
function valueFor(slots){ return Number(slots.map(k=>placements[k]).join('')) }
function frac(side){
  const s = currentPuzzle.value[side]
  const num = valueFor(s.num.slots), den = valueFor(s.den.slots)
  if(!den) return null
  return {num, den}
}
async function addPoint(){ try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{} }

async function checkSolution(){
  if(!slotsFilled()){ feedback.value=copy[L.value].needAll; sWrong&&sWrong.play(); return }
  const A = frac('left'), B = frac('right')
  if(!A || !B){ feedback.value=copy[L.value].wrong; sWrong&&sWrong.play(); return }
  const eq = A.num*B.den === B.num*A.den  // ضرب تبادلي دقيق بالأعداد الصحيحة
  if(eq){
    feedback.value=copy[L.value].correct; solved.value=true; sOK&&sOK.play(); sClap&&sClap.play(); await addPoint()
  }else{
    feedback.value=copy[L.value].wrong; sWrong&&sWrong.play()
  }
}

/* ---------- إعادة ضبط ---------- */
function resetSelection(){
  Object.keys(placements).forEach(k=>{
    if(placements[k]!=null){ const d=placements[k]; bankCounts[d]=(bankCounts[d]||0)+1; placements[k]=null }
  })
  solved.value=false; feedback.value=null
}

onMounted(initPuzzle)
watch(()=>props.lang, ()=>{ if(!solved.value) feedback.value=null })
</script>

<template>
  <div class="lvl3c6 challenge-surface" :data-theme="props.theme">
    <header class="head">
      <h2 class="title">{{ copy[L].title }}</h2>
      <p class="intro">{{ copy[L].intro }}</p>
    </header>

    <section class="problem">
      <!-- الكسر الأيسر -->
      <div class="fraction-card">
        <div class="label">{{ copy[L].left }}</div>
        <div class="fraction">
          <div class="row">
            <div v-for="slot in currentPuzzle.left.num.slots" :key="slot" class="slot"
                 @dragover="allowDrop" @drop="onDrop($event, slot)">
              <span v-if="placements[slot]" class="digit">{{ placements[slot] }}</span>
              <span v-else class="placeholder">?</span>
              <button class="clear" @click="clearSlot(slot)"><Eraser class="ic"/> {{ copy[L].clear }}</button>
            </div>
          </div>
          <div class="bar"></div>
          <div class="row">
            <div v-for="slot in currentPuzzle.left.den.slots" :key="slot" class="slot"
                 @dragover="allowDrop" @drop="onDrop($event, slot)">
              <span v-if="placements[slot]" class="digit">{{ placements[slot] }}</span>
              <span v-else class="placeholder">?</span>
              <button class="clear" @click="clearSlot(slot)"><Eraser class="ic"/> {{ copy[L].clear }}</button>
            </div>
          </div>
        </div>
      </div>

      <span class="equals">=</span>

      <!-- الكسر الأيمن -->
      <div class="fraction-card">
        <div class="label">{{ copy[L].right }}</div>
        <div class="fraction">
          <div class="row">
            <div v-for="slot in currentPuzzle.right.num.slots" :key="slot" class="slot"
                 @dragover="allowDrop" @drop="onDrop($event, slot)">
              <span v-if="placements[slot]" class="digit">{{ placements[slot] }}</span>
              <span v-else class="placeholder">?</span>
              <button class="clear" @click="clearSlot(slot)"><Eraser class="ic"/> {{ copy[L].clear }}</button>
            </div>
          </div>
          <div class="bar"></div>
          <div class="row">
            <div v-for="slot in currentPuzzle.right.den.slots" :key="slot" class="slot"
                 @dragover="allowDrop" @drop="onDrop($event, slot)">
              <span v-if="placements[slot]" class="digit">{{ placements[slot] }}</span>
              <span v-else class="placeholder">?</span>
              <button class="clear" @click="clearSlot(slot)"><Eraser class="ic"/> {{ copy[L].clear }}</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="controls">
      <button class="btn" @click="checkSolution"><Check class="ic"/> {{ copy[L].check }}</button>
      <button class="btn" @click="resetSelection"><RotateCcw class="ic"/> {{ copy[L].reset }}</button>
      <button class="btn" @click="initPuzzle"><RefreshCw class="ic"/> {{ copy[L].newQ }}</button>
    </section>

    <section class="bank">
      <div class="bank-title">{{ copy[L].bank }}</div>
      <div class="bank-items">
        <button v-for="item in bankList" :key="item.key" class="chip" draggable="true"
                @dragstart="onDragStart($event, item.digit)">
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
.lvl3c6{ --fg:#1f2937; --bg:#f8fafc; --panel:#ffffff; --bd:#c4d4f8; --accent:#2563eb;
  padding:24px; border-radius:18px; background:var(--bg); color:var(--fg); box-shadow:0 14px 32px rgba(37,99,235,.12) }
[data-theme="dark"] .lvl3c6{ --fg:#e2e8f0; --bg:#0f172a; --panel:#111c34; --bd:#1e3a8a; --accent:#60a5fa }

.head{ margin-bottom:20px }
.title{ margin:0 0 10px; font-size:1.55rem; font-weight:700 }
.intro{ margin:0; line-height:1.5; opacity:.85 }

.problem{ display:flex; align-items:center; justify-content:center; gap:24px; flex-wrap:wrap; margin-bottom:22px }
.fraction-card{ background:var(--panel); border:1px solid var(--bd); border-radius:16px; padding:16px 20px; box-shadow:0 12px 28px rgba(15,23,42,.08); min-width:220px }
.label{ font-weight:700; margin-bottom:12px; text-align:center }

.fraction{ display:flex; flex-direction:column; gap:12px; align-items:center }
.row{ display:flex; gap:10px }
.bar{ width:100%; height:3px; background:var(--accent); border-radius:999px }
.slot{ min-width:46px; min-height:54px; border-radius:12px; border:2px dashed rgba(37,99,235,.35);
  display:flex; align-items:center; justify-content:center; position:relative; background:rgba(191,219,254,.35) }
.placeholder{ font-size:1.5rem; color:var(--accent); opacity:.75 }
.digit{ font-size:1.45rem; font-weight:700 }
.clear{ position:absolute; bottom:-30px; left:50%; transform:translateX(-50%); background:transparent; border:none; color:var(--accent); cursor:pointer; font-size:.75rem; display:flex; align-items:center; gap:4px }
.ic{ width:16px; height:16px }
.equals{ font-size:1.8rem; font-weight:700; color:var(--accent) }

.controls{ display:flex; gap:12px; flex-wrap:wrap; justify-content:center; margin-bottom:18px }
.btn{ display:inline-flex; align-items:center; gap:8px; padding:10px 18px; border-radius:12px; border:1px solid var(--bd); background:var(--panel); font-weight:700; cursor:pointer; transition:.15s }
.btn:hover{ transform:translateY(-1px); box-shadow:0 12px 24px rgba(15,23,42,.12) }

.bank{ background:var(--panel); border:1px solid var(--bd); border-radius:16px; padding:18px; box-shadow:0 12px 24px rgba(15,23,42,.08) }
.bank-title{ font-weight:700; margin-bottom:12px }
.bank-items{ display:flex; flex-wrap:wrap; gap:10px }
.chip{ padding:9px 14px; border-radius:12px; border:1px solid var(--bd); background:rgba(191,219,254,.45); font-weight:700; cursor:grab; transition:.15s }
.chip:active{ cursor:grabbing }

.feedback{ margin-top:20px; padding:12px 18px; border-radius:12px; border:1px solid #fecaca; background:#fee2e2; color:#b91c1c; font-weight:700; text-align:center }
.feedback.ok{ border-color:#bbf7d0; background:#dcfce7; color:#166534 }
[data-theme="dark"] .feedback{ background:rgba(248,113,113,.18); border-color:rgba(248,113,113,.45); color:#fecaca }
[data-theme="dark"] .feedback.ok{ background:rgba(34,197,94,.22); border-color:rgba(34,197,94,.5); color:#bbf7d0 }

.fade-enter-active,.fade-leave-active{ transition:opacity .2s }
.fade-enter-from,.fade-leave-to{ opacity:0 }

@media (max-width: 720px){
  .slot{ min-width:42px; min-height:48px }
  .clear{ bottom:-26px }
}
</style>

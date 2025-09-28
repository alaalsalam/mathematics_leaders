<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

/* ===== copy ===== */
const copy = {
  ar:{
    title:'المستوى الثالث – التحدي 4: أزل النقطة الحمراء',
    intro:[
      'هذه المعادلات للتفكير في العمليات على الأعداد العشرية.',
      'كل نقطة ● تمثل رقمًا واحدًا. اسحب الرقم الصحيح من لوحة الأرقام إلى مكانه حتى تصبح المعادلات صحيحة.'
    ],
    check:'تحقّق', reset:'مسح الكل', newQ:'سؤال جديد',
    incomplete:'أكمل كل الخانات أولًا.', wrong:'هناك معادلة غير صحيحة.', correct:'أحسنت! جميع المعادلات صحيحة.',
    bank:'لوحة الأرقام', clear:'تفريغ'
  },
  en:{
    title:'Level 3 – Challenge 4: Replace the red dot',
    intro:[
      'These equations practice decimal operations.',
      'Each red dot ● hides a single digit. Drag the correct digit from the number bank to make every equation true.'
    ],
    check:'Check', reset:'Clear all', newQ:'New puzzle',
    incomplete:'Fill every blank first.', wrong:'One or more equations are incorrect.', correct:'Great! All equations are valid.',
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

/* ===== number formatting for Arabic clarity ===== */
const digitsMap = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩']
const LRI = '\u2066', PDI = '\u2069', NNBSP = '\u202F' // isolate + thin-space

function toArabicNumber(value, decimals){
  let s = typeof value === 'number'
    ? (decimals!=null ? value.toFixed(decimals) : String(value))
    : String(value)
  const out = s.replace(/[0-9]/g, d => digitsMap[+d]).replace(/\./g, `${NNBSP}٫${NNBSP}`)
  return LRI + out + PDI
}
function formatDigit(value){
  const s = String(value)
  return props.lang==='ar'
    ? (LRI + s.replace(/[0-9]/g, d => digitsMap[+d]) + PDI)
    : s
}

/* ===== equation builders (single-digit slots only) ===== */
/* token types in template:
   - string: printed as-is
   - {num:true,text:string}: numeric literal already formatted
   - {slot:'name'}: droppable slot
*/
function makeEqA({ multiplier, offset, aDigit, bDigit }){
  const multAr = toArabicNumber(multiplier, 1)
  const multEn = multiplier.toFixed(1)
  const offStr = offset.toFixed(2)           // e.g. "0.28"
  const offEnSuffix = offStr.slice(1)        // ".28"
  const offArSuffix = toArabicNumber(offStr).slice(1)
  return {
    id:'eqA',
    slots:{ a:aDigit, b:bDigit },
    order:['a','b'],
    template:{
      ar:['أ. ', {num:true,text:multAr}, ' × ', {num:true,text:'٠'}, '٫', {slot:'a'}, ' = ', {slot:'b'}, {num:true,text:offArSuffix}],
      en:['A. ', {num:true,text:multEn}, ' × 0.', {slot:'a'}, ' = ', {slot:'b'}, offEnSuffix]
    },
    evaluate(v){
      const left  = multiplier * (v.a/10)
      const right = v.b + offset
      return Math.abs(left - right) < 1e-6
    }
  }
}
function makeEqB({ baseLeft, baseRight, cDigit, dDigit, result, decimals = 2 }){
  const blAr = toArabicNumber(baseLeft,0), brAr = toArabicNumber(baseRight,0)
  const blEn = `${baseLeft}`, brEn = `${baseRight}`
  const resEn = decimals!=null ? result.toFixed(decimals) : String(result)
  const resAr = toArabicNumber(resEn)
  return {
    id:'eqB',
    slots:{ c:cDigit, d:dDigit },
    order:['c','d'],
    template:{
      ar:['ب. ', {num:true,text:blAr}, '٫', {slot:'c'}, ' × ', {num:true,text:brAr}, '٫', {slot:'d'}, ' = ', {num:true,text:resAr}],
      en:['B. ', {num:true,text:blEn}, '.', {slot:'c'}, ' × ', {num:true,text:brEn}, '.', {slot:'d'}, ' = ', resEn]
    },
    evaluate(v){
      const left = (baseLeft + v.c/10) * (baseRight + v.d/10)
      return Math.abs(left - result) < 1e-6
    }
  }
}
function makeEqC({ secondBase, eDigit, fDigit, result, decimals = 2 }){
  const sbAr = toArabicNumber(secondBase,0)
  const sbEn = `${secondBase}`
  const resEn = decimals!=null ? result.toFixed(decimals) : String(result)
  const resAr = toArabicNumber(resEn)
  return {
    id:'eqC',
    slots:{ e:eDigit, f:fDigit },
    order:['e','f'],
    template:{
      ar:['ج. ', {slot:'e'}, '٫', {num:true,text:toArabicNumber(9,0).slice(1,-1)}, ' × ', {num:true,text:sbAr}, '٫', {slot:'f'}, ' = ', {num:true,text:resAr}],
      en:['C. ', {slot:'e'}, '.9 × ', {num:true,text:sbEn}, '.', {slot:'f'}, ' = ', resEn]
    },
    evaluate(v){
      const left = (v.e + 0.9) * (secondBase + v.f/10)
      return Math.abs(left - result) < 1e-6
    }
  }
}
function makeEqD({ gDigit, hDigit }){
  return {
    id:'eqD',
    slots:{ g:gDigit, h:hDigit },
    order:['g','h'],
    template:{
      ar:['د. ', {num:true,text:'٤'}, '٫', {slot:'g'}, ' + ', {num:true,text:'١٫٢٥'}, ' = ', {num:true,text:'٥'}, '٫', {slot:'h'}, {num:true,text:'٥'}],
      en:['D. 4.', {slot:'g'}, ' + 1.25 = 5.', {slot:'h'}, '5']
    },
    evaluate(v){
      const left  = (4 + v.g/10) + 1.25
      const right = 5 + v.h/10 + 0.05
      return Math.abs(left - right) < 1e-6
    }
  }
}

/* ===== fixed puzzle bank (all slots are correct single digits) ===== */
const puzzleBank = [
  {
    id:'p1',
    equations:[
      makeEqA({ multiplier:9.3, offset:0.44, aDigit:8, bDigit:7 }),
      makeEqB({ baseLeft:2, baseRight:2, cDigit:4, dDigit:9, result:6.96, decimals:2 }),
      makeEqC({ secondBase:3, eDigit:4, fDigit:7, result:18.13, decimals:2 }),
      makeEqD({ gDigit:7, hDigit:9 })
    ]
  },
  {
    id:'p2',
    equations:[
      makeEqA({ multiplier:8.6, offset:0.16, aDigit:6, bDigit:5 }),
      makeEqB({ baseLeft:2, baseRight:2, cDigit:1, dDigit:6, result:5.46, decimals:2 }),
      makeEqC({ secondBase:3, eDigit:2, fDigit:5, result:10.15, decimals:2 }),
      makeEqD({ gDigit:3, hDigit:5 })
    ]
  },
  {
    id:'p3',
    equations:[
      makeEqA({ multiplier:7.8, offset:0.24, aDigit:8, bDigit:6 }),
      makeEqB({ baseLeft:2, baseRight:2, cDigit:5, dDigit:2, result:5.50, decimals:2 }),
      makeEqC({ secondBase:3, eDigit:3, fDigit:6, result:14.04, decimals:2 }),
      makeEqD({ gDigit:2, hDigit:4 })
    ]
  },
  {
    id:'p4',
    equations:[
      makeEqA({ multiplier:6.4, offset:0.28, aDigit:2, bDigit:1 }),
      makeEqB({ baseLeft:2, baseRight:2, cDigit:8, dDigit:3, result:6.44, decimals:2 }),
      makeEqC({ secondBase:3, eDigit:5, fDigit:2, result:18.88, decimals:2 }),
      makeEqD({ gDigit:4, hDigit:6 })
    ]
  },
  {
    id:'p5',
    equations:[
      makeEqA({ multiplier:6.4, offset:0.12, aDigit:8, bDigit:5 }),
      makeEqB({ baseLeft:2, baseRight:2, cDigit:0, dDigit:9, result:5.80, decimals:2 }),
      makeEqC({ secondBase:3, eDigit:6, fDigit:1, result:21.39, decimals:2 }),
      makeEqD({ gDigit:1, hDigit:3 })
    ]
  }
]

/* ===== state ===== */
const currentPuzzle = ref(puzzleBank[0])
const lastPuzzleId = ref(null)
const answers = reactive({})
const totalCounts = reactive({})
const bankCounts = reactive({})
const slotsMeta = ref([])
const feedback = ref(null)
const solved = ref(false)

/* ===== helpers ===== */
function shuffle(a){ return a.slice().sort(()=>Math.random()-0.5) }
function pickNextPuzzle(){
  if(puzzleBank.length===1){ lastPuzzleId.value=puzzleBank[0].id; return puzzleBank[0] }
  let c
  do{ c = puzzleBank[Math.floor(Math.random()*puzzleBank.length)] }while(c.id===lastPuzzleId.value)
  lastPuzzleId.value = c.id
  return c
}

/* ===== init puzzle, bank = exact correct digits ===== */
function initPuzzle(){
  const puzzle = pickNextPuzzle()
  currentPuzzle.value = puzzle
  feedback.value = null
  solved.value = false

  Object.keys(answers).forEach(k=>delete answers[k])
  Object.keys(totalCounts).forEach(k=>delete totalCounts[k])
  Object.keys(bankCounts).forEach(k=>delete bankCounts[k])

  const meta = []
  puzzle.equations.forEach(eq=>{
    eq.order.forEach(slotName=>{
      const key = `${eq.id}-${slotName}`
      meta.push({ key, eq, slotName })
      answers[key] = null
      const d = eq.slots[slotName]
      totalCounts[d] = (totalCounts[d]||0) + 1
      bankCounts[d]  = (bankCounts[d]||0) + 1
    })
  })
  slotsMeta.value = meta
}

/* ===== DnD ===== */
function allowDrop(ev){ ev.preventDefault() }
function onDragStart(ev, value){ ev.dataTransfer.setData('text/plain', String(value)) }
function onDrop(ev, key){
  ev.preventDefault()
  const val = Number(ev.dataTransfer.getData('text/plain'))
  if(Number.isNaN(val)) return
  if((bankCounts[val]||0) <= 0 && answers[key] !== val) return

  if(answers[key]!=null){
     const prev=answers[key];
    bankCounts[prev]=(bankCounts[prev]||0)+1
   }
  if(answers[key] !== val){
    bankCounts[val] = (bankCounts[val] || 0) - 1;
    if (bankCounts[val] < 0) bankCounts[val] = 0;
  }

  answers[key]=val; feedback.value=null; solved.value=false
}
function clearSlot(key){
  if(answers[key]!=null){
    const prev=answers[key]; bankCounts[prev]=(bankCounts[prev]||0)+1
    answers[key]=null; feedback.value=null; solved.value=false
  }
}
const bankList = computed(()=>{
  const list=[]
  for(const [d,c] of Object.entries(bankCounts)){
    for(let i=0;i<c;i++) list.push({ value:Number(d), key:`${d}-${i}` })
  }
  return shuffle(list)
})

/* ===== check ===== */
function allFilled(){ return slotsMeta.value.every(s=>answers[s.key]!=null) }
async function addPoint(){ try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{} }
async function checkAll(){
  if(!allFilled()){ feedback.value=copy[L.value].incomplete; sWrong&&sWrong.play(); return }
  const { equations } = currentPuzzle.value
  for(const eq of equations){
    const v={}
    for(const name of eq.order){ v[name]=answers[`${eq.id}-${name}`] }
    if(!eq.evaluate(v)){ feedback.value=copy[L.value].wrong; sWrong&&sWrong.play(); return }
  }
  feedback.value=copy[L.value].correct; solved.value=true; sOK&&sOK.play(); sClap&&sClap.play(); await addPoint()
}
function resetAll(){
  slotsMeta.value.forEach(s=>{ if(answers[s.key]!=null){ const prev=answers[s.key]; bankCounts[prev]=(bankCounts[prev]||0)+1; answers[s.key]=null } })
  feedback.value=null; solved.value=false
}

/* ===== lifecycle ===== */
onMounted(initPuzzle)
watch(()=>props.lang, ()=>{ if(!solved.value) feedback.value=null })
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
          <span
            v-for="(token, idx) in (props.lang==='ar' ? eq.template.ar : eq.template.en)"
            :key="idx"
          >
            <template v-if="typeof token==='string'">
              {{ token }}
            </template>
            <template v-else-if="token.num">
              <span class="num" v-html="token.text"></span>
            </template>
            <template v-else>
              <span class="slot" @dragover="allowDrop" @drop="onDrop($event, eq.id + '-' + token.slot)">
                <span v-if="answers[eq.id + '-' + token.slot] != null" class="digit" v-html="formatDigit(answers[eq.id + '-' + token.slot])"></span>
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
          v-html="formatDigit(item.value)"
        />
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
.expression{
  display:flex; align-items:center; flex-wrap:wrap; gap:10px;
  font-size:1.15rem; font-weight:600; direction: rtl;
}
.num,.digit{ direction:ltr; unicode-bidi:isolate; font-variant-numeric:tabular-nums }
.slot{
  min-width:36px; min-height:36px; border-radius:12px; border:2px dashed rgba(239,68,68,.45);
  display:inline-flex; align-items:center; justify-content:center; background:rgba(254,226,226,.5); padding:4px 8px
}
[data-theme="dark"] .slot{ background:rgba(239,68,68,.12); border-color:rgba(248,113,113,.55) }
.placeholder{ color:var(--accent); font-size:1.4rem }
.clear{ border:none; background:transparent; color:var(--accent); cursor:pointer; display:inline-flex; align-items:center; gap:4px; font-size:.8rem }
.ic{ width:16px; height:16px }

.bank{ margin:22px 0; background:var(--panel); border:1px solid var(--bd); border-radius:16px; padding:16px; box-shadow:0 12px 24px rgba(17,24,39,.08) }
.bank-title{ font-weight:700; margin-bottom:12px }
.bank-items{ display:flex; flex-wrap:wrap; gap:10px }
.chip{
  padding:8px 14px; border-radius:999px; border:1px solid var(--bd); background:var(--panel);
  cursor:grab; font-weight:700; box-shadow:0 8px 20px rgba(17,24,39,.08)
}
.chip:active{ cursor:grabbing }

.actions{ display:flex; gap:12px; flex-wrap:wrap; margin-bottom:18px }
.btn{
  display:inline-flex; align-items:center; gap:8px; padding:10px 18px; border-radius:12px;
  border:1px solid var(--bd); background:var(--panel); cursor:pointer; font-weight:700; transition:.15s
}
.btn:hover{ transform:translateY(-1px); box-shadow:0 12px 24px rgba(17,24,39,.12) }

.feedback{ padding:12px 18px; border-radius:12px; border:1px solid #fecaca; background:#fee2e2; color:#b91c1c; font-weight:700 }
.feedback.ok{ border-color:#bbf7d0; background:#dcfce7; color:#166534 }
[data-theme="dark"] .feedback{ background:rgba(248,113,113,.18); border-color:rgba(248,113,113,.45); color:#fecaca }
[data-theme="dark"] .feedback.ok{ background:rgba(34,197,94,.22); border-color:rgba(34,197,94,.5); color:#bbf7d0 }

.fade-enter-active,.fade-leave-active{ transition:opacity .2s }
.fade-enter-from,.fade-leave-to{ opacity:0 }
</style>

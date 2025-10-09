<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

/* ===== نصوص ===== */
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

/* ===== أصوات ===== */
import successUrl from '@/assets/sounds/success2.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong2.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

/* ===== تنسيق الأرقام والفواصل ===== */
const digitsMap = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩']
const LRI = '\u2066', PDI = '\u2069', NNBSP = '\u202F'
function toArabicNumber(value, decimals){
  let s = typeof value === 'number'
    ? (decimals!=null ? value.toFixed(decimals) : String(value))
    : String(value)
  const out = s.replace(/[0-9]/g, d => digitsMap[+d]).replace(/\./g, `${NNBSP}٫${NNBSP}`)
  return LRI + out + PDI
}
function formatDigit(value){
  const s = String(value)
  return props.lang==='ar' ? (LRI + s.replace(/[0-9]/g, d => digitsMap[+d]) + PDI) : s
}
/* فاصل عشري غير قابل للانعكاس */
const sep = computed(()=> (props.lang==='ar' ? (LRI+'٫'+PDI) : '.'))

/* ===== مُنشئات المعادلات (الخانة دائماً بعد الفاصلة) ===== */
/* رموز القالب:
   - string: يظهر كما هو
   - {num:true,text:string}: رقم مُنسَّق
   - {slot:'name'}: خانة قابلة للإسقاط
*/
function makeEqA({ multiplier, aDigit, bDigit, offsetSuffix }){
  //  multiplier × 0.a = b + (0.offsetSuffix)
  const multAr = toArabicNumber(multiplier, 1)
  const multEn = multiplier.toFixed(1)
  const offSuffixEn = '.' + offsetSuffix.padStart(2,'0')      // مثل ".44"
  const offSuffixAr = toArabicNumber(offSuffixEn)              // "٫٤٤"
  return {
    id:'eqA',
    slots:{ a:aDigit, b:bDigit },
    order:['a','b'],
    template:{
      ar:['أ. ', {num:true,text:multAr}, ' × ', {num:true,text:'٠'}, sep.value, {slot:'a'}, ' = ', {slot:'b'}, {num:true,text:offSuffixAr}],
      en:['A. ', {num:true,text:multEn}, ' × 0', sep.value, {slot:'a'}, ' = ', {slot:'b'}, offSuffixEn]
    },
    evaluate(v){
      const left  = multiplier * (v.a/10)
      const right = v.b + Number(offSuffixEn)
      return Math.abs(left - right) < 1e-6
    }
  }
}
function makeEqB({ baseLeft, baseRight, cDigit, dDigit }){
  //  (baseLeft.c) × (baseRight.d) = result
  const blAr = toArabicNumber(baseLeft,0), brAr = toArabicNumber(baseRight,0)
  const blEn = `${baseLeft}`, brEn = `${baseRight}`
  const result = Number(((baseLeft + cDigit/10) * (baseRight + dDigit/10)).toFixed(2))
  const resEn = result.toFixed(2)
  const resAr = toArabicNumber(resEn)
  return {
    id:'eqB',
    slots:{ c:cDigit, d:dDigit },
    order:['c','d'],
    template:{
      ar:['ب. ', {num:true,text:blAr}, sep.value, {slot:'c'}, ' × ', {num:true,text:brAr}, sep.value, {slot:'d'}, ' = ', {num:true,text:resAr}],
      en:['B. ', {num:true,text:blEn}, sep.value, {slot:'c'}, ' × ', {num:true,text:brEn}, sep.value, {slot:'d'}, ' = ', resEn]
    },
    evaluate(v){
      const left = (baseLeft + v.c/10) * (baseRight + v.d/10)
      return Math.abs(left - result) < 1e-6
    }
  }
}
function makeEqC({ secondBase, eDigit, fDigit }){
  //  (e.9) × (secondBase.f) = result
  const sbAr = toArabicNumber(secondBase,0), sbEn = `${secondBase}`
  const result = Number(((eDigit + 0.9) * (secondBase + fDigit/10)).toFixed(2))
  const resEn = result.toFixed(2), resAr = toArabicNumber(resEn)
  return {
    id:'eqC',
    slots:{ e:eDigit, f:fDigit },
    order:['e','f'],
    template:{
      ar:['ج. ', {slot:'e'}, sep.value, {num:true,text:toArabicNumber(9,0)}, ' × ', {num:true,text:sbAr}, sep.value, {slot:'f'}, ' = ', {num:true,text:resAr}],
      en:['C. ', {slot:'e'}, sep.value, '9 × ', {num:true,text:sbEn}, sep.value, {slot:'f'}, ' = ', resEn]
    },
    evaluate(v){
      const left = (v.e + 0.9) * (secondBase + v.f/10)
      return Math.abs(left - result) < 1e-6
    }
  }
}
function makeEqD({ gDigit }){
  //  4.g + 1.25 = 5.h5  =>  h = g + 2
  const hDigit = gDigit + 2
  return {
    id:'eqD',
    slots:{ g:gDigit, h:hDigit },
    order:['g','h'],
    template:{
      ar:['د. ', {num:true,text:'٤'}, sep.value, {slot:'g'}, ' + ', {num:true,text:'١'+sep.value+'٢٥'}, ' = ', {num:true,text:'٥'}, sep.value, {slot:'h'}, {num:true,text:'٥'}],
      en:['D. 4', sep.value, {slot:'g'}, ' + 1', sep.value, '25 = 5', sep.value, {slot:'h'}, '5']
    },
    evaluate(v){
      const left  = (4 + v.g/10) + 1.25
      const right = 5 + v.h/10 + 0.05
      return Math.abs(left - right) < 1e-6
    }
  }
}

/* ===== توليد بنك نماذج كبير ===== */
function randInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function pick(arr){ return arr[Math.floor(Math.random()*arr.length)] }

function genPuzzle(id){
  // Eq A: اختر a,b والمضاعف ثم اضبط لاحقة الكسر
  let a = randInt(1,9), b = randInt(0,9), multiplier = pick([6.4,6.8,7.2,7.6,8.2,8.6,9.0,9.3])
  let off = +(multiplier*(a/10) - b).toFixed(2)
  // إجبار ضمن [0,0.99]
  let tries=0
  while((off<0 || off>=1) && tries<40){
    a = randInt(1,9); b = randInt(0,9); multiplier = pick([6.4,6.8,7.2,7.6,8.2,8.6,9.0,9.3])
    off = +(multiplier*(a/10) - b).toFixed(2)
    tries++
  }
  const offSuffix = String(off.toFixed(2)).split('.')[1] // "44"

  // Eq B
  const c = randInt(0,9), d = randInt(0,9)
  const baseLeft = pick([2,3,4]), baseRight = pick([2,3,4])

  // Eq C
  const e = randInt(1,8), f = randInt(0,9)
  const secondBase = pick([2,3,4])

  // Eq D: اختر g<=7
  const g = randInt(0,7)

  return {
    id,
    equations:[
      makeEqA({ multiplier, aDigit:a, bDigit:b, offsetSuffix:offSuffix }),
      makeEqB({ baseLeft, baseRight, cDigit:c, dDigit:d }),
      makeEqC({ secondBase, eDigit:e, fDigit:f }),
      makeEqD({ gDigit:g })
    ]
  }
}
function generateBank(n=40){
  const arr=[]
  for(let i=1;i<=n;i++) arr.push(genPuzzle('p'+i))
  return arr
}

/* ===== الحالة ===== */
const puzzleBank = ref(generateBank(40))
const currentPuzzle = ref(puzzleBank.value[0])
const lastPuzzleId = ref(null)
const answers = reactive({})
const totalCounts = reactive({})
const bankCounts = reactive({})
const slotsMeta = ref([])
const feedback = ref(null)
const solved = ref(false)

/* ===== أدوات ===== */
function shuffle(a){ return a.slice().sort(()=>Math.random()-0.5) }
function pickNextPuzzle(){
  const list = puzzleBank.value
  if(list.length===1){ lastPuzzleId.value=list[0].id; return list[0] }
  let c; do{ c=list[Math.floor(Math.random()*list.length)] }while(c.id===lastPuzzleId.value)
  lastPuzzleId.value=c.id; return c
}

/* ===== تهيئة اللغز (بنك الأرقام = الأرقام الصحيحة تمامًا) ===== */
function initPuzzle(){
  const puzzle = pickNextPuzzle()
  currentPuzzle.value = puzzle
  feedback.value = null; solved.value = false

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

/* ===== سحب وإفلات ===== */
function allowDrop(ev){ ev.preventDefault() }
function onDragStart(ev, value){ ev.dataTransfer.setData('text/plain', String(value)) }
function onDrop(ev, key){
  ev.preventDefault()
  const val = Number(ev.dataTransfer.getData('text/plain'))
  if(Number.isNaN(val)) return
  if((bankCounts[val]||0) <= 0 && answers[key] !== val) return

  if(answers[key]!=null){
    const prev=answers[key]
    bankCounts[prev]=(bankCounts[prev]||0)+1
  }
  if(answers[key] !== val){
    bankCounts[val] = (bankCounts[val] || 0) - 1
    if (bankCounts[val] < 0) bankCounts[val] = 0
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

/* ===== فحص ===== */
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

/* ===== دورة الحياة ===== */
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
        <div class="expression" :dir="L==='ar' ? 'rtl' : 'ltr'">
          <span
            v-for="(token, idx) in (props.lang==='ar' ? eq.template.ar : eq.template.en)"
            :key="idx"
          >
            <template v-if="typeof token==='string'">
              <span class="txt">{{ token }}</span>
            </template>
            <template v-else-if="token.num">
              <span class="num" v-html="token.text"></span>
            </template>
            <template v-else>
              <!-- خانة بعد الفاصلة دائماً -->
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
  display:flex; align-items:center; flex-wrap:wrap; gap:10px; font-size:1.15rem; font-weight:600;
}
.txt{ direction:inherit }
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

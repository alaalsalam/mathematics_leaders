<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw,
  Scale as ScaleIc, Circle as BallIc, Square as CubeIc, Triangle as PyrIc } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

const T = {
  ar:{
    title:'المستوى الثاني – التحدي 6: رتّب خطوات الحل الصحيح',
    rule:'اسحب البطاقات ورتّبها من ١ إلى ٤ لحل المسألة: كم مكعبًا نضع بدل ثلاث كُرَات ليحدث التعادل؟ (المعطى: كرة = مكعبين).',
    newQ:'سؤال جديد', reset:'إعادة تعيين', check:'تحقّق',
    correct:'ترتيب صحيح', wrong:'ترتيب غير صحيح. عدّل البطاقات.',
    slots:'خطوات الحل', cards:'البطاقات'
  },
  en:{
    title:'Level 2 – Challenge 6: Order the solution steps',
    rule:'Order cards 1→4 to solve: how many cubes balance three balls? (Given: ball = two cubes).',
    newQ:'New puzzle', reset:'Reset', check:'Check',
    correct:'Correct order', wrong:'Incorrect order. Try again.',
    slots:'Solution steps', cards:'Cards'
  }
}
const L = computed(()=> (T[props.lang]?props.lang:'ar'))

/* sounds */
import successUrl from '@/assets/sounds/success2.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong2.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]]} return x }

/* ----- state ----- */
const canonical = ref([])
const bank = ref([])
const slots = ref([null,null,null,null])
const toast = ref(null)
const solved = ref(false)

/* نصوص الخطوات مع رموز */
const stepsWithIcons = () => ([
  { id:'s0',
    textAr:'من المعطى: كتلة الكرة = مكعبين.',
    textEn:'Given: one ball equals two cubes.',
    icons: ['ball','=','cube','cube'] },
  { id:'s1',
    textAr:'كتلة ٣ كرات = ٣ × كتلة الكرة.',
    textEn:'Mass of 3 balls = 3 × ball.',
    icons: ['ball','ball','ball'] },
  { id:'s2',
    textAr:'بالتعويض: بالمكعبات ٣ × ٢ = ٦.',
    textEn:'Substitute: 3 × 2 cubes = 6.',
    icons: ['cube','×','cube','=', '6'] },
  { id:'s3',
    textAr:'نضع ٦ مكعبات فتتعادل الكفتان.',
    textEn:'Put 6 cubes for balance.',
    icons: ['scale','|','cube','cube','cube','cube','cube','cube'] },
])

function buildSteps(){
  const sw = stepsWithIcons()
  canonical.value = [sw[0], sw[1], sw[2], sw[3]]
  bank.value = shuffle(canonical.value.map(s => ({...s})))
  slots.value = [null,null,null,null]
  toast.value = null
  solved.value = false
}

/* DnD */
function onDragStart(ev, cardId){ ev.dataTransfer.setData('text/plain', cardId) }
function allowDrop(ev){ ev.preventDefault() }
function onDrop(ev, idx){
  ev.preventDefault()
  const id = ev.dataTransfer.getData('text/plain')
  const old = slots.value.findIndex(x=>x===id)
  if(old>=0) slots.value[old]=null
  slots.value[idx]=id
  toast.value=null
}
function removeFromSlot(idx){ slots.value[idx]=null }

const allPlaced = computed(()=> slots.value.every(x=>x!==null))
function isCorrect(){
  if(!allPlaced.value) return false
  const byId = Object.fromEntries(canonical.value.map(s=>[s.id,s.id]))
  for(let i=0;i<4;i++){
    if(slots.value[i]!==byId['s'+i]) return false
  }
  return true
}

async function addPoint(){
  try{
    await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',
      {method:'GET', credentials:'include'})
  }catch{}
}
async function checkNow(){
  if(!allPlaced.value){ toast.value = L.value==='ar'?'أكمل جميع الخانات':'Fill all slots'; sWrong&&sWrong.play(); return }
  if(isCorrect()){ solved.value=true; toast.value=T[L.value].correct; sOK&&sOK.play(); sClap&&sClap.play(); await addPoint() }
  else { toast.value=T[L.value].wrong; sWrong&&sWrong.play() }
}
function resetAll(){ slots.value=[null,null,null,null]; toast.value=null; solved.value=false }

onMounted(buildSteps)
watch(()=>props.lang,()=>{})
</script>

<template>
  <div class="lvl2c6" :data-theme="props.theme">
    <h2 class="title">{{ T[L].title }}</h2>
    <p class="rule">{{ T[L].rule }}</p>

    <!-- مشهد زخرفي: ميزان + أشكال -->
    <div class="scene">
      <ScaleIc class="scale" />
      <div class="plate left">
        <BallIc class="sh" />
        <BallIc class="sh" />
        <BallIc class="sh" />
      </div>
      <div class="plate right">
        <span class="qm">؟</span>
      </div>
    </div>

    <!-- خانات الترتيب -->
    <div class="slots">
      <div class="slot" v-for="(s,idx) in slots" :key="idx"
           @dragover="allowDrop" @drop="onDrop($event, idx)">
        <div class="slot-index">{{ idx+1 }}</div>
        <template v-if="slots[idx]">
          <div class="card placed">
            <div class="icons">
              <template v-for="(k,i) in bank.find(c=>c.id===slots[idx]).icons" :key="i">
                <BallIc v-if="k==='ball'" class="ic ball"/>
                <CubeIc v-else-if="k==='cube'" class="ic cube"/>
                <PyrIc  v-else-if="k==='pyr'"  class="ic pyr"/>
                <ScaleIc v-else-if="k==='scale'" class="ic scale2"/>
                <span v-else class="txt">{{ k }}</span>
              </template>
            </div>
            <div class="t">
              {{ props.lang==='ar' ? bank.find(c=>c.id===slots[idx]).textAr
                                   : bank.find(c=>c.id===slots[idx]).textEn }}
            </div>
            <button class="x" @click="removeFromSlot(idx)">×</button>
          </div>
        </template>
        <div v-else class="placeholder">— {{ T[L].slots }} —</div>
      </div>
    </div>

    <!-- بنك البطاقات -->
    <div class="bank">
      <div class="bank-title">{{ T[L].cards }}</div>
      <div class="bank-list">
        <div v-for="c in bank" :key="c.id"
             class="card"
             draggable="true"
             @dragstart="onDragStart($event, c.id)">
          <div class="icons">
            <template v-for="(k,i) in c.icons" :key="i">
              <BallIc v-if="k==='ball'" class="ic ball"/>
              <CubeIc v-else-if="k==='cube'" class="ic cube"/>
              <PyrIc  v-else-if="k==='pyr'"  class="ic pyr"/>
              
              <ScaleIc v-else-if="k==='scale'" class="ic scale2"/>
              <span v-else class="txt">{{ k }}</span>
            </template>
          </div>
          <div class="t">{{ props.lang==='ar' ? c.textAr : c.textEn }}</div>
        </div>
      </div>
    </div>

    <div class="actions">
      <button class="btn" @click="resetAll"><RotateCcw class="icx" /> {{ T[L].reset }}</button>
      <button class="btn" @click="checkNow"><Check class="icx" /> {{ T[L].check }}</button>
      <button class="btn" @click="buildSteps"><RefreshCw class="icx" /> {{ T[L].newQ }}</button>
    </div>

    <div v-if="toast" class="toast" :class="{ ok: solved }">{{ toast }}</div>
  </div>
</template>

<style scoped>
.lvl2c6{ --bg:var(--c-bg,#fff); --fg:var(--c-fg,#111827); --muted:#6b7280 }
[data-theme="dark"] .lvl2c6{ --bg:#0b1220; --fg:#e5e7eb; --muted:#9ca3af }
.title{ font-weight:700; margin:0 0 .25rem }
.rule{ color:var(--muted); margin:0 0 1rem }

/* مشهد الميزان */
.scene{ position:relative; width:520px; height:110px; margin:0 0 1rem; background:var(--bg);
  border-radius:1rem; box-shadow:0 4px 14px rgba(0,0,0,.06) }
.scale{ position:absolute; left:12px; top:10px; width:40px; height:40px; color:#94a3b8 }
.plate{ position:absolute; bottom:14px; width:180px; height:56px; border:2px solid #cbd5e1; border-radius:12px;
  display:flex; align-items:center; justify-content:center; gap:6px; background:rgba(203,213,225,.15) }
.left{ left:16px } .right{ right:16px }
.qm{ font-size:26px; color:#6b7280 }
.sh{ width:22px; height:22px; color:#2563eb }

/* الخانات */
.slots{ display:grid; grid-template-columns: repeat(2, minmax(280px, 1fr)); gap:.75rem; margin-bottom:1rem }
.slot{ border:1px dashed #cbd5e1; background:rgba(99,102,241,.06); border-radius:.9rem; padding:.6rem; min-height:104px; position:relative }
.slot-index{ position:absolute; top:.4rem; inset-inline-start:.5rem; width:28px; height:28px; border-radius:9999px; background:#e5e7eb; color:#111827; display:flex; align-items:center; justify-content:center; font-weight:700 }
.placeholder{ color:var(--muted); text-align:center; padding:1.8rem 0 }

/* البطاقات */
.bank-title{ font-weight:600; color:var(--muted); margin:.25rem 0 }
.bank-list{ display:flex; gap:.5rem; flex-wrap:wrap }
.card{ background:var(--bg); border:1px solid #e5e7ebaa; border-radius:.75rem; padding:.55rem .7rem; cursor:grab; user-select:none; max-width:560px }
.card.placed{ cursor:default; padding-inline-end:2rem; position:relative }
.card .x{ position:absolute; top:.35rem; inset-inline-end:.35rem; border:none; background:transparent; cursor:pointer; color:#9ca3af; font-size:1.1rem }
.icons{ display:flex; align-items:center; gap:6px; margin-bottom:.25rem }
.ic{ width:20px; height:20px }
.ic.ball{ color:#2563eb } .ic.cube{ color:#ef4444 } .ic.pyr{ color:#10b981 } .ic.cyl{ color:#f59e0b } .ic.scale2{ color:#94a3b8 }
.txt{ font-weight:700; color:#475569 }
.t{ color:var(--fg) }

/* أزرار */
.actions{ display:flex; gap:.5rem; flex-wrap:wrap; margin-top:.5rem }
.btn{ display:inline-flex; align-items:center; gap:.35rem; padding:.5rem .7rem; border-radius:.75rem; border:1px solid #e5e7eb55; background:var(--bg); cursor:pointer }
.icx{ width:16px; height:16px }

/* تنبيه */
.toast{ margin-top:.6rem; padding:.55rem .8rem; border-radius:.75rem; background:#fee2e2; color:#991b1b; border:1px solid #fecaca }
.toast.ok{ background:#dcfce7; color:#166534; border-color:#bbf7d0 }
</style>

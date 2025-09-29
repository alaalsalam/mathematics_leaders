<script setup>
/* ================================
   Multiplication Table – Dark/Light polished
   Notes:
   - Strong theme tokens for dark mode contrast
   - Numeric content isolated LTR for RTL UIs
   - Bank uses quantity-aware drag & drop
   - Manual entry limited by bank counts too
================================== */

import { ref, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

/* -------- Props -------- */
const props = defineProps({
  lang:  { type: String, default: 'ar' },
  theme: { type: String, default: 'light' } // 'light' | 'dark'
})

/* -------- Copy -------- */
const T = {
  ar:{
    title:'التحدي 4: أكمل جدول الضرب',
    rule:'جدول ضرب بعناوين صفوف وأعمدة. اسحب القيم الصحيحة من الأسفل إلى الخانات الفارغة.',
    bank:'لوحة الأعداد', newQ:'سؤال جديد', reset:'إعادة تعيين',
    check:'تحقّق', correct:'إجابة صحيحة', wrong:'تحقق من القيم', clear:'تفريغ الخلية'
  },
  en:{
    title:'Challenge 4: Complete the multiplication table',
    rule:'A multiplication table with row/column headers. Drag correct values into the blanks.',
    bank:'Number bank', newQ:'New puzzle', reset:'Reset',
    check:'Check', correct:'Correct', wrong:'Check your values', clear:'Clear cell'
  }
}
const L = computed(() => (T[props.lang] ? props.lang : 'ar'))

/* -------- Sounds (lightweight) -------- */
import successUrl from '@/assets/sounds/success4.mp3'
import wrongUrl   from '@/assets/sounds/wrong4.mp3'
const sOK    = typeof Audio !== 'undefined' ? new Audio(successUrl) : null
const sWrong = typeof Audio !== 'undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sWrong && (sWrong.preload='auto')

/* -------- RNG helpers -------- */
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]] } return x }

/* -------- State -------- */
const n = 3                                // 3x3 body
const factorsR = ref([])                   // row headers
const factorsC = ref([])                   // column headers
const blanks   = ref(new Set())            // keys of empty cells
const answerMap = ref({})                  // key -> value
const manualDrafts = ref({})               // key -> input text
const bankCounts = ref({})                 // value -> remaining copies
const solved = ref(false)
const toast  = ref(null)

/* -------- Value helpers -------- */
// Cell value (including headers)
function valueAt(r,c){
  if(r===0 && c===0) return '×'
  if(r===0) return factorsC.value[c-1]
  if(c===0) return factorsR.value[r-1]
  return factorsR.value[r-1] * factorsC.value[c-1]
}
// Key builder (prefix h: for header, c: for body)
const keyH = (r,c)=> (r===0||c===0)?`h:${r},${c}`:`c:${r},${c}`

/* -------- Puzzle generation -------- */
// Pick distinct factors from 1..9
function pickFactors(k){ return shuffle([1,2,3,4,5,6,7,8,9]).slice(0,k).sort((a,b)=>a-b) }
// Choose blanks; keep at least one body cell visible as a clue
function pickBlanks(){
  const all=[]
  for(let r=0;r<=n;r++) for(let c=0;c<=n;c++){
    if(r===0 && c===0) continue
    all.push([r,c])
  }
  const body = all.filter(([r,c])=>r>0&&c>0)
  const keep = shuffle(body)[0]
  const cand = all.filter(([r,c])=> !(r===keep[0]&&c===keep[1]))
  const k = rndInt(6,8)
  return new Set(shuffle(cand).slice(0,k).map(([r,c])=>keyH(r,c)))
}
// Recompute bank from blanks minus already placed answers
function rebuildBank(){
  const counts={}
  blanks.value.forEach(k=>{
    const [,rc]=k.split(':'); const [r,c]=rc.split(',').map(Number)
    const v=valueAt(r,c); counts[v]=(counts[v]||0)+1
  })
  for(const [k,v] of Object.entries(answerMap.value)){ counts[v]=(counts[v]||0)-1 }
  for(const [v,ct] of Object.entries(counts)){ if(ct<=0) delete counts[v] }
  bankCounts.value=counts
}
const bankList = computed(()=>{
  const out=[]
  for(const [v,ct] of Object.entries(bankCounts.value)) for(let i=0;i<ct;i++) out.push(Number(v))
  return shuffle(out)
})
function newPuzzle(){
  solved.value=false; toast.value=null; answerMap.value={}; manualDrafts.value={}
  factorsR.value = pickFactors(n)
  factorsC.value = pickFactors(n)
  blanks.value   = pickBlanks()
  rebuildBank()
}

/* -------- Validation -------- */
function isFilled(){ for(const k of blanks.value){ if(answerMap.value[k]==null) return false } return true }
function isCorrect(){
  if(!isFilled()) return false
  for(const k of blanks.value){
    const [,rc]=k.split(':'); const [r,c]=rc.split(',').map(Number)
    if(answerMap.value[k] !== valueAt(r,c)) return false
  }
  return true
}
async function addPoint(){ try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{} }
async function checkNow(){
  if(!isFilled()){ toast.value = L.value==='ar'?'أكمل كل الخانات':'Fill all blanks'; sWrong&&sWrong.play(); return }
  if(isCorrect()){ solved.value=true; toast.value=T[L.value].correct; sOK&&sOK.play(); await addPoint() }
  else { toast.value=T[L.value].wrong; sWrong&&sWrong.play() }
}
function resetAll(){ answerMap.value={}; manualDrafts.value={}; rebuildBank(); toast.value=null; solved.value=false }

/* -------- DnD + manual entry (bank-limited) -------- */
function setAnswer(key, value, { fromManual=false } = {}){
  if(Number.isNaN(value)) return
  if(answerMap.value[key]!=null){
    const prev=answerMap.value[key]; bankCounts.value[prev]=(bankCounts.value[prev]||0)+1
  }
  if((bankCounts.value[value]||0)===0) return
  bankCounts.value[value]-=1
  answerMap.value[key]=value
  manualDrafts.value = { ...manualDrafts.value, [key]: String(value) }
  toast.value=null; solved.value=false
}
function onDragStart(ev,value){ ev.dataTransfer.setData('text/plain', String(value)) }
function allowDrop(ev){ ev.preventDefault() }
function onDrop(ev,key){ ev.preventDefault(); const v=Number(ev.dataTransfer.getData('text/plain')); setAnswer(key,v) }
function clearCell(key){
  if(answerMap.value[key]!=null){
    const prev=answerMap.value[key]; bankCounts.value[prev]=(bankCounts.value[prev]||0)+1
    delete answerMap.value[key]
  }
  manualDrafts.value = { ...manualDrafts.value, [key]: '' }
  toast.value=null; solved.value=false
}
function onManualInput(key, value){ manualDrafts.value = { ...manualDrafts.value, [key]: value } }
function commitManual(key){
  const raw=(manualDrafts.value[key]??'').trim()
  if(raw===''){ clearCell(key); return }
  const num=Number(raw); if(!Number.isFinite(num)) return
  setAnswer(key,num,{fromManual:true})
}

/* -------- LTR isolation for numbers in RTL UIs -------- */
const numDir = computed(()=>({ direction:'ltr', unicodeBidi:'isolate' }))

/* -------- Lifecycle -------- */
onMounted(newPuzzle)
watch(() => props.lang, () => { if(!solved.value) toast.value=null })
</script>

<template>
  <div class="challenge4 challenge-surface" :data-theme="props.theme">
    <h2 class="title">{{ T[L].title }}</h2>
    <p class="rule">{{ T[L].rule }}</p>

    <div class="wrap">
      <!-- Table -->
      <div class="table">
        <div class="row" v-for="r in (n+1)" :key="'r'+r">
          <div
            class="cell"
            v-for="c in (n+1)"
            :key="'c'+r+'-'+c"
            :class="{
              head: r===1 || c===1,
              corner: r===1 && c===1,
              body: !(r===1 || c===1)
            }"
          >
            <!-- Corner -->
            <template v-if="r===1 && c===1">×</template>

            <!-- Pre-filled cells -->
            <template v-else-if="!blanks.has((r===1||c===1)?`h:${r-1},${c-1}`:`c:${r-1},${c-1}`)">
              <span class="num" :style="numDir">{{ valueAt(r-1,c-1) }}</span>
            </template>

            <!-- Blanks -->
            <template v-else>
              <div class="dropzone"
                   @dragover="allowDrop"
                   @drop="onDrop($event,(r===1||c===1)?`h:${r-1},${c-1}`:`c:${r-1},${c-1}`)">
                <span
                  v-if="answerMap[(r===1||c===1)?`h:${r-1},${c-1}`:`c:${r-1},${c-1}`] != null"
                  class="num"
                  :style="numDir"
                >
                  {{ answerMap[(r===1||c===1)?`h:${r-1},${c-1}`:`c:${r-1},${c-1}`] }}
                </span>
                <span v-else class="placeholder">؟</span>
              </div>

              <input class="manual-entry" type="number"
                     :value="manualDrafts[(r===1||c===1)?`h:${r-1},${c-1}`:`c:${r-1},${c-1}`] ?? ''"
                     @input="onManualInput((r===1||c===1)?`h:${r-1},${c-1}`:`c:${r-1},${c-1}`, $event.target.value)"
                     @change="commitManual((r===1||c===1)?`h:${r-1},${c-1}`:`c:${r-1},${c-1}`)"
                     @blur="commitManual((r===1||c===1)?`h:${r-1},${c-1}`:`c:${r-1},${c-1}`)"
                     :placeholder="props.lang==='ar' ? 'أدخل رقمًا' : 'Enter value'"/>

              <button class="clear" @click="clearCell((r===1||c===1)?`h:${r-1},${c-1}`:`c:${r-1},${c-1}`)">
                <Eraser class="ic" /> {{ T[L].clear }}
              </button>
            </template>
          </div>
        </div>
      </div>

      <!-- Bank -->
      <div class="side">
        <div class="bank-title">{{ T[L].bank }}</div>
        <div class="bank-items">
          <button
            v-for="v in bankList"
            :key="v + '_' + Math.random()"
            class="chip"
            draggable="true"
            @dragstart="onDragStart($event, v)"
            :style="numDir"
          >
            {{ v }}
          </button>
        </div>

        <div class="actions">
          <button class="btn" @click="resetAll"><RotateCcw class="ic" /> {{ T[L].reset }}</button>
          <button class="btn primary" @click="checkNow"><Check class="ic" /> {{ T[L].check }}</button>
          <button class="btn" @click="newPuzzle"><RefreshCw class="ic" /> {{ T[L].newQ }}</button>
        </div>

        <div v-if="toast" class="toast" :class="{ ok: solved }">{{ toast }}</div>
      </div>
    </div>

    <!-- Success overlay -->
    <div v-if="solved" class="overlay">
      <div class="card">
        <div class="big">{{ T[L].correct }}</div>
        <button class="btn primary" @click="newPuzzle">{{ T[L].newQ }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* =========================
   Theme tokens
   - High contrast in dark mode
   - All surfaces and borders derive from tokens
========================= */
.challenge4{
  --bg: #ffffff;
  --fg: #0b1220;
  --muted: #64748b;

  --panel: #ffffff;
  --panel-bd: #cbd5e1;
  --panel-shadow: 0 6px 22px rgba(2,6,23,.08);

  --head-bg: #fff7e6;             /* header cells */
  --head-bd: #fbbf24;
  --head-fg: #7c2d12;

  --cell-bd: #cbd5e1;
  --cell-bg: #ffffff;

  --drop-bg: rgba(59,130,246,.10);
  --drop-bd: #93c5fd;

  --input-bg: #ffffff;
  --input-bd: #cbd5e1;

  --chip-bg: #ffffff;
  --chip-bd: #cbd5e1;

  --btn-bg: #ffffff;
  --btn-bd: #cbd5e1;
  --btn-fg: #0b1220;

  --btn-primary-bg: #0ea5e9;
  --btn-primary-fg: #ffffff;

  --toast-err-bg: #fee2e2; --toast-err-fg: #991b1b; --toast-err-bd: #fecaca;
  --toast-ok-bg: #dcfce7;  --toast-ok-fg: #166534;  --toast-ok-bd: #bbf7d0;

  --overlay: rgba(2,6,23,.45);
}

[data-theme="dark"] .challenge4{
  --bg: #0b1220;
  --fg: #e5e7eb;
  --muted: #9ca3af;

  --panel: #0f172a;
  --panel-bd: #334155;
  --panel-shadow: 0 10px 28px rgba(0,0,0,.45);

  --head-bg: #3b3a1a;            /* warm but subdued */
  --head-bd: #a16207;
  --head-fg: #fde68a;

  --cell-bd: #475569;
  --cell-bg: #111827;

  --drop-bg: rgba(56,189,248,.20);
  --drop-bd: #38bdf8;

  --input-bg: #111827;
  --input-bd: #475569;

  --chip-bg: #111827;
  --chip-bd: #475569;

  --btn-bg: #111827;
  --btn-bd: #475569;
  --btn-fg: #e5e7eb;

  --btn-primary-bg: #38bdf8;
  --btn-primary-fg: #0b1220;

  --toast-err-bg: rgba(248,113,113,.18); --toast-err-fg: #fecaca; --toast-err-bd: rgba(248,113,113,.45);
  --toast-ok-bg: rgba(34,197,94,.22);    --toast-ok-fg: #bbf7d0;  --toast-ok-bd: rgba(34,197,94,.50);

  --overlay: rgba(0,0,0,.55);
}

/* =========================
   Layout
========================= */
.title{ margin:0 0 .4rem; font-weight:800; color:var(--fg) }
.rule{ margin:0 0 1rem; color:var(--muted) }

.wrap{ display:grid; grid-template-columns:auto 280px; gap:1rem }

/* table */
.table{
  background:var(--panel);
  border:1px solid var(--panel-bd);
  border-radius:12px;
  padding:.75rem;
  box-shadow:var(--panel-shadow);
}
.row{ display:grid; grid-template-columns: repeat(4, 120px); gap:.5rem }
.cell{
  min-height:84px; border-radius:10px; padding:.4rem;
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:.35rem;
  background:var(--cell-bg); border:1.5px dashed var(--cell-bd);
}
.cell.head{ background:var(--head-bg); border-color:var(--head-bd); color:var(--head-fg); font-weight:800 }
.cell.corner{ background:color-mix(in oklab, var(--head-bg) 80%, black 20%); border-color:var(--head-bd) }

.num{ font-variant-numeric:tabular-nums; font-weight:800; font-size:1.1rem; color:var(--fg) }
.placeholder{ color:var(--muted); font-size:1.15rem }

.dropzone{
  width:100%; flex:1; display:flex; align-items:center; justify-content:center;
  background:var(--drop-bg); border:2px dashed var(--drop-bd);
  border-radius:.6rem; transition:border-color .15s, box-shadow .15s;
}
.dropzone:hover{ box-shadow:0 0 0 3px color-mix(in oklab, var(--drop-bd) 40%, transparent) }

.manual-entry{
  width:100%; padding:.5rem .65rem; border-radius:.6rem;
  background:var(--input-bg); border:1px solid var(--input-bd);
  color:var(--fg); font-size:.95rem; direction:ltr;
}
.manual-entry:focus{
  outline:none; border-color:var(--drop-bd);
  box-shadow:0 0 0 3px color-mix(in oklab, var(--drop-bd) 30%, transparent)
}
.clear{ border:none; background:transparent; color:var(--muted); cursor:pointer; display:flex; align-items:center; gap:.35rem; font-size:.85rem }
.ic{ width:16px; height:16px }

/* bank */
.side{ display:flex; flex-direction:column; gap:.75rem }
.bank-title{ font-weight:800; color:var(--muted) }
.bank-items{ display:flex; flex-wrap:wrap; gap:.55rem }
.chip{
  background:var(--chip-bg); border:1px solid var(--chip-bd); color:var(--fg);
  padding:.5rem .7rem; border-radius:.8rem; cursor:grab; min-width:56px; text-align:center;
  font-variant-numeric:tabular-nums; box-shadow:0 6px 16px rgba(0,0,0,.10)
}
.chip:active{ cursor:grabbing }

/* actions */
.actions{ display:flex; gap:.6rem; flex-wrap:wrap }
.btn{
  display:inline-flex; align-items:center; gap:.45rem; padding:.6rem .85rem;
  background:var(--btn-bg); border:1px solid var(--btn-bd); color:var(--btn-fg);
  border-radius:.9rem; cursor:pointer; transition:transform .12s, box-shadow .12s
}
.btn:hover{ transform:translateY(-1px); box-shadow:0 10px 22px rgba(0,0,0,.12) }
.btn.primary{ background:var(--btn-primary-bg); color:var(--btn-primary-fg); border-color:transparent }

/* toast */
.toast{
  padding:.65rem .9rem; border-radius:.9rem; text-align:center; font-weight:800;
  background:var(--toast-err-bg); color:var(--toast-err-fg); border:1px solid var(--toast-err-bd)
}
.toast.ok{ background:var(--toast-ok-bg); color:var(--toast-ok-fg); border-color:var(--toast-ok-bd); margin-top:.35rem }

/* success overlay */
.overlay{ position:fixed; inset:0; background:var(--overlay); display:flex; align-items:center; justify-content:center; z-index:30 }
.card{
  background:var(--panel); border:1px solid var(--panel-bd);
  color:var(--fg); padding:1rem 1.25rem; border-radius:1rem; box-shadow:var(--panel-shadow);
  display:flex; flex-direction:column; gap:.8rem; align-items:center
}
.big{ font-size:1.25rem; font-weight:900 }
</style>

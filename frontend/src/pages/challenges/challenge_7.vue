<script setup>
/* =========================================================
   Level 1 – Challenge 7: Sum Pyramid (Addition Wall)
   Dark-mode fixes:
   - Stronger contrast tokens for panels, cells, borders, text
   - Hover/focus states tuned for dark
   - Chips, inputs, and toasts readable on both themes
   Notes are short and human.
========================================================= */

import { ref, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({
  lang:  { type:String, default:'ar' },
  theme: { type:String, default:'light' } // 'light' | 'dark'
})

/* ---------- copy ---------- */
const T = {
  ar:{ title:'التحدي 7: جدار أعداد (هرم جمع)',
       rule:'كل خانة تساوي مجموع الخليتين اللتين تحتها مباشرة. اسحب القيم المفقودة لإكمال الهرم.',
       bank:'لوحة الأعداد', newQ:'سؤال جديد', reset:'إعادة تعيين', check:'تحقّق',
       correct:'إجابة صحيحة', wrong:'تحقق من القيم', clear:'تفريغ الخلية' },
  en:{ title:'Challenge 7: Sum Pyramid',
       rule:'Each cell equals the sum of the two cells directly below. Drag missing values to complete the pyramid.',
       bank:'Number bank', newQ:'New puzzle', reset:'Reset', check:'Check',
       correct:'Correct answer', wrong:'Check your values', clear:'Clear cell' }
}
const L = computed(()=> (T[props.lang]?props.lang:'ar'))

/* ---------- tiny sounds ---------- */
import successUrl from '@/assets/sounds/success3.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

/* ---------- helpers ---------- */
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]] } return x }

/* ---------- config ---------- */
const EXTRA_CHOICES = 6

/* ---------- state ---------- */
const baseN        = ref(4)               // base width
const rows         = ref([])              // rows[0] = base
const blanks       = ref(new Set())       // "r,c" (r=0 is base)
const answerMap    = ref({})              // placed answers
const manualDrafts = ref({})              // input drafts
const bankCounts   = ref({})              // value -> remaining
const solved       = ref(false)
const toast        = ref(null)

/* keep numerals LTR even in RTL UI */
const numDir = computed(()=>({ direction:'ltr', unicodeBidi:'isolate' }))

/* ---------- build pyramid ---------- */
function buildPyramid(n){
  const rs=[]
  rs[0] = Array.from({length:n}, ()=> rndInt(1,9))
  for(let r=1;r<n;r++){
    rs[r] = Array.from({length:n-r}, (_,c)=> rs[r-1][c] + rs[r-1][c+1])
  }
  return rs
}
const keyOf = (r,c)=>`${r},${c}`

/* choose blanks (keep at least one visible per non-base row) */
function pickBlanks(n){
  const keep = new Set()
  for(let r=1;r<n;r++){
    const idx = rndInt(0, rows.value[r].length-1)
    keep.add(keyOf(r, idx))
  }
  const candidates=[]
  for(let r=1;r<n;r++) for(let c=0;c<rows.value[r].length;c++){
    if(!keep.has(keyOf(r,c))) candidates.push([r,c])
  }
  const k = rndInt(4, 6)
  return new Set(shuffle(candidates).slice(0,k).map(([r,c])=>keyOf(r,c)))
}

/* rebuild number bank with counts + distractors */
function rebuildBank(){
  const counts={}
  blanks.value.forEach(k=>{
    const [r,c]=k.split(',').map(Number)
    const v=rows.value[r][c]
    counts[v]=(counts[v]||0)+1
  })
  for(const v of Object.values(answerMap.value)){
    counts[v]=(counts[v]||0)-1
  }
  for(const [v,ct] of Object.entries(counts)){ if(ct<=0) delete counts[v] }

  // add extras that are not real answers
  const used = new Set(Object.keys(counts).map(Number))
  const real = new Set(rows.value.flat())
  const pool=[]
  for(let v=2; v<=150; v++){
    if(!used.has(v) && !real.has(v)) pool.push(v)
  }
  shuffle(pool).slice(0,EXTRA_CHOICES).forEach(v=>{
    counts[v]=(counts[v]||0)+1
  })

  bankCounts.value = counts
}

/* list bank items honoring counts */
const bankList = computed(()=>{
  const out=[]
  for(const [v,ct] of Object.entries(bankCounts.value)){
    for(let i=0;i<ct;i++) out.push(Number(v))
  }
  return shuffle(out)
})

/* ---------- lifecycle ---------- */
function newPuzzle(){
  solved.value=false; toast.value=null
  answerMap.value={}; manualDrafts.value={}
  rows.value   = buildPyramid(baseN.value)
  blanks.value = pickBlanks(baseN.value)
  rebuildBank()
}
onMounted(newPuzzle)
watch(()=>props.lang,()=>{ if(!solved.value) toast.value=null })

/* ---------- checks ---------- */
function isFilled(){ for(const k of blanks.value){ if(answerMap.value[k]==null) return false } return true }
function isCorrect(){
  if(!isFilled()) return false
  for(const k of blanks.value){
    const [r,c]=k.split(',').map(Number)
    if(answerMap.value[k] !== rows.value[r][c]) return false
  }
  return true
}
async function addPoint(){ try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{} }
async function checkNow(){
  if(!isFilled()){ toast.value = L.value==='ar'?'أكمل كل الخانات':'Fill all blanks'; sWrong&&sWrong.play(); return }
  if(isCorrect()){ solved.value=true; toast.value=T[L.value].correct; sOK&&sOK.play(); sClap&&sClap.play(); await addPoint() }
  else { toast.value=T[L.value].wrong; sWrong&&sWrong.play() }
}
function resetAll(){
  answerMap.value={}; manualDrafts.value={}
  rebuildBank(); toast.value=null; solved.value=false
}

/* ---------- DnD + manual ---------- */
function onDragStart(ev,value){ ev.dataTransfer.setData('text/plain', String(value)) }
function allowDrop(ev){ ev.preventDefault() }
function setAnswer(key, value, { fromManual=false } = {}){
  if(Number.isNaN(value)) return
  if(answerMap.value[key]!=null){
    const old=answerMap.value[key]
    bankCounts.value[old]=(bankCounts.value[old]||0)+1
  }
  if(!fromManual){
    if((bankCounts.value[value]||0)===0) return
  }
  bankCounts.value[value]=(bankCounts.value[value]||0)-1
  if(bankCounts.value[value]<0) bankCounts.value[value]=0
  answerMap.value[key]=value
  manualDrafts.value = { ...manualDrafts.value, [key]: String(value) }
  toast.value=null
}
function onDrop(ev,key){ ev.preventDefault(); const v=Number(ev.dataTransfer.getData('text/plain')); setAnswer(key,v) }
function clearCell(key){
  if(answerMap.value[key]!=null){
    const old=answerMap.value[key]
    bankCounts.value[old]=(bankCounts.value[old]||0)+1
    delete answerMap.value[key]
  }
  manualDrafts.value = { ...manualDrafts.value, [key]: '' }
}
function onManualInput(key, value){ manualDrafts.value = { ...manualDrafts.value, [key]: value } }
function commitManual(key){
  const raw=(manualDrafts.value[key]??'').trim()
  if(raw===''){ clearCell(key); return }
  const num=Number(raw); if(!Number.isFinite(num)) return
  setAnswer(key, num, { fromManual:true })
}
</script>

<template>
  <div class="challenge7 challenge-surface" :data-theme="props.theme">
    <h2 class="title">{{ T[L].title }}</h2>
    <p class="rule">{{ T[L].rule }}</p>

    <!-- pyramid -->
    <div class="pyramid">
      <div class="prow" v-for="(row,r) in rows" :key="'r'+r" :style="{ '--cols': row.length }">
        <div class="cell" v-for="(v,c) in row" :key="r+'-'+c">
          <template v-if="!blanks.has(`${r},${c}`)">
            <span class="num" :style="numDir">{{ v }}</span>
          </template>
          <template v-else>
            <div class="dropzone" @dragover="allowDrop" @drop="onDrop($event, `${r},${c}`)">
              <span v-if="answerMap[`${r},${c}`]!=null" class="num" :style="numDir">{{ answerMap[`${r},${c}`] }}</span>
              <span v-else class="placeholder">؟</span>
            </div>
            <input
              class="manual-entry"
              type="number"
              :value="manualDrafts[`${r},${c}`] ?? ''"
              @input="onManualInput(`${r},${c}`, $event.target.value)"
              @change="commitManual(`${r},${c}`)"
              @blur="commitManual(`${r},${c}`)"
              :placeholder="props.lang==='ar' ? 'أدخل رقمًا' : 'Enter value'"
            />
            <button class="clear" @click="clearCell(`${r},${c}`)"><Eraser class="ic" /> {{ T[L].clear }}</button>
          </template>
        </div>
      </div>
    </div>

    <!-- bank + actions -->
    <div class="side">
      <div class="bank-title">{{ T[L].bank }}</div>
      <div class="bank-items">
        <button
          v-for="v in bankList" :key="v + '_' + Math.random()"
          class="chip" draggable="true"
          @dragstart="onDragStart($event, v)" :style="numDir"
        >{{ v }}</button>
      </div>

      <div class="actions">
        <button class="btn" @click="resetAll"><RotateCcw class="ic" /> {{ T[L].reset }}</button>
        <button class="btn primary" @click="checkNow"><Check class="ic" /> {{ T[L].check }}</button>
        <button class="btn" @click="newPuzzle"><RefreshCw class="ic" /> {{ T[L].newQ }}</button>
      </div>

      <div v-if="toast" class="toast" :class="{ ok: solved }">{{ toast }}</div>
    </div>
  </div>
</template>

<style scoped>
/* =========================
   High-contrast theme tokens
========================= */
.challenge7{
  --bg:#ffffff; --fg:#0b1220; --muted:#64748b;

  --panel:#ffffff; --panel-bd:#cbd5e1; --panel-shadow:0 8px 24px rgba(2,6,23,.08);

  --cell-bg:#f8fafc; --cell-bd:#cbd5e1; --cell-dashed:#93c5fd;
  --cell-hover:rgba(59,130,246,.12);
  --input-bg:#ffffff; --input-bd:#cbd5e1;

  --chip-bg:#ffffff; --chip-bd:#cbd5e1;

  --btn-bg:#ffffff; --btn-bd:#cbd5e1; --btn-fg:#0b1220;
  --btn-primary-bg:#0ea5e9; --btn-primary-fg:#ffffff;

  --toast-err-bg:#fee2e2; --toast-err-fg:#991b1b; --toast-err-bd:#fecaca;
  --toast-ok-bg:#dcfce7;  --toast-ok-fg:#166534;  --toast-ok-bd:#bbf7d0;
}

[data-theme="dark"] .challenge7{
  --bg:#0b1220; --fg:#e5e7eb; --muted:#9ca3af;

  --panel:#0f172a; --panel-bd:#334155; --panel-shadow:0 12px 28px rgba(0,0,0,.5);

  --cell-bg:#111827; --cell-bd:#475569; --cell-dashed:#60a5fa;
  --cell-hover:rgba(56,189,248,.22);
  --input-bg:#0b1220; --input-bd:#475569;

  --chip-bg:#111827; --chip-bd:#475569;

  --btn-bg:#111827; --btn-bd:#475569; --btn-fg:#e5e7eb;
  --btn-primary-bg:#38bdf8; --btn-primary-fg:#0b1220;

  --toast-err-bg:rgba(248,113,113,.18); --toast-err-fg:#fecaca; --toast-err-bd:rgba(248,113,113,.45);
  --toast-ok-bg:rgba(34,197,94,.22);    --toast-ok-fg:#bbf7d0;  --toast-ok-bd:rgba(34,197,94,.50);
}

/* =========================
   Layout
========================= */
.title{ margin:0 0 .35rem; font-weight:800; color:var(--fg) }
.rule{  margin:0 0 1rem; color:var(--muted) }

/* pyramid panel */
.pyramid{
  background:var(--panel);
  border:1px solid var(--panel-bd);
  border-radius:16px;
  box-shadow:var(--panel-shadow);
  padding:14px;
  width:max-content;
  margin-bottom:1rem;
}
.prow{
  display:grid;
  grid-template-columns: repeat(var(--cols), 92px);
  gap:.6rem;
  justify-content:center;
  margin-top:.6rem;
}
.cell{
  min-height:68px;
  background:var(--cell-bg);
  border:1px dashed var(--cell-dashed);
  border-radius:12px;
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:.3rem;
}
.cell:hover{ background:var(--cell-hover) }
.num{ font-variant-numeric:tabular-nums; font-weight:800; font-size:1.15rem; color:var(--fg) }
.placeholder{ color:var(--muted); font-size:1.15rem }
.dropzone{ width:100%; height:100%; display:flex; align-items:center; justify-content:center }

/* input inside cell */
.manual-entry{
  width:100%; padding:.45rem .6rem; border-radius:.6rem;
  background:var(--input-bg); border:1px solid var(--input-bd);
  color:var(--fg); font-size:.95rem; direction:ltr;
}
.manual-entry:focus{ outline:none; box-shadow:0 0 0 3px rgba(56,189,248,.25); border-color:#38bdf8 }
.clear{ font-size:.78rem; border:none; background:transparent; color:var(--muted); display:flex; align-items:center; gap:.25rem; cursor:pointer }
.ic{ width:16px; height:16px }

/* bank + actions */
.side{ max-width:560px }
.bank-title{ font-weight:700; color:var(--muted); margin:.35rem 0 }
.bank-items{ display:flex; flex-wrap:wrap; gap:.5rem }
.chip{
  padding:.45rem .65rem; border-radius:.8rem; font-weight:800;
  background:var(--chip-bg); border:1px solid var(--chip-bd); cursor:grab;
  color:var(--fg); font-variant-numeric:tabular-nums
}

.actions{ display:flex; gap:.6rem; flex-wrap:wrap; margin-top:.6rem }
.btn{
  display:inline-flex; align-items:center; gap:.45rem;
  padding:.6rem .85rem; border-radius:.95rem;
  background:var(--btn-bg); border:1px solid var(--btn-bd); color:var(--btn-fg);
  cursor:pointer; transition:transform .12s, box-shadow .12s
}
.btn:hover{ transform:translateY(-1px); box-shadow:0 10px 22px rgba(0,0,0,.12) }
.btn.primary{ background:var(--btn-primary-bg); color:var(--btn-primary-fg); border-color:transparent }

/* feedback */
.toast{
  margin-top:.6rem; padding:.6rem .9rem; border-radius:.9rem; text-align:center; font-weight:800;
  background:var(--toast-err-bg); color:var(--toast-err-fg); border:1px solid var(--toast-err-bd)
}
.toast.ok{ background:var(--toast-ok-bg); color:var(--toast-ok-fg); border-color:var(--toast-ok-bd) }
</style>

<script setup>
/* =========================================================
   Challenge 6 – Pick 3 cells (distinct rows/cols) to reach target
   Fixes for dark mode:
   - High-contrast theme tokens
   - Cells, hover, picked, and focus states tuned for dark
   - Panel and toast colors adapted
   Code notes are short and human.
========================================================= */

import { ref, computed, onMounted } from 'vue'
import { RefreshCw, RotateCcw, Check } from 'lucide-vue-next'

const props = defineProps({
  lang:  { type: String, default: 'ar' },
  theme: { type: String, default: 'light' } // 'light' | 'dark'
})

/* -------- copy -------- */
const T = {
  ar:{
    title:'التحدي 6: اختر ثلاث خلايا من شبكة بحيث لا تكون في الصف أو العمود نفسه ويكون مجموعها الهدف',
    rule:(n,t)=>`شبكة ${n}×${n}. اختر ثلاث خلايا كلٌّ منها في صف وعمود مختلفين بحيث يساوي مجموعها ${t}.`,
    newQ:'سؤال جديد', reset:'إعادة تعيين', check:'تحقّق',
    correct:'إجابة صحيحة', wrong:'تحقق من القيود أو من المجموع',
    pick3:'اختر ثلاث خلايا'
  },
  en:{
    title:'Challenge 6: Pick 3 cells in different rows and columns to reach the target',
    rule:(n,t)=>`A ${n}×${n} grid. Pick three cells, one per distinct row and column, that sum to ${t}.`,
    newQ:'New puzzle', reset:'Reset', check:'Check',
    correct:'Correct', wrong:'Check constraints or sum',
    pick3:'Pick three cells'
  }
}
const L = computed(() => (T[props.lang] ? props.lang : 'ar'))

/* -------- sounds (tiny) -------- */
import successUrl from '@/assets/sounds/success.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong3.mp3'
const sOK    = typeof Audio !== 'undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio !== 'undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio !== 'undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

/* -------- utils -------- */
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]] } return x }

/* -------- state -------- */
const n = ref(3)          // grid size (3 or 4)
const grid = ref([])      // 2D numbers
const target = ref(0)     // target sum (guaranteed solvable)
const picks = ref([])     // [{r,c}]
const solved = ref(false)
const toast  = ref(null)

/* numbers stay LTR even in RTL UI */
const numDir = computed(() => ({ direction:'ltr', unicodeBidi:'isolate' }))

/* flatten grid for a simple v-for */
const flat = computed(() => grid.value.flatMap((row,r) => row.map((v,c) => ({ v, r, c })) ))

/* recompute current picked sum */
const pickedSum = computed(() => picks.value.reduce((s,p)=> s + grid.value[p.r][p.c], 0))

/* build a puzzle that is guaranteed to have at least one solution */
function newPuzzle(){
  solved.value=false; toast.value=null; picks.value=[]
  n.value = [3,4][rndInt(0,1)]
  grid.value = Array.from({length:n.value}, () => Array.from({length:n.value}, () => rndInt(1,9)))
  const rows = shuffle([...Array(n.value).keys()]).slice(0,3)
  const cols = shuffle([...Array(n.value).keys()]).slice(0,3)
  const perm = shuffle(cols.slice())
  const solution = rows.map((r,i)=>({ r, c: perm[i] }))
  target.value = solution.reduce((s,p)=> s + grid.value[p.r][p.c], 0)
}
onMounted(newPuzzle)

/* interactions */
function resetPicks(){ picks.value=[]; toast.value=null; solved.value=false }
function toggleCell(r,c){
  if(solved.value) return
  const i = picks.value.findIndex(p => p.r===r && p.c===c)
  if(i>=0){ picks.value.splice(i,1); return }
  if(picks.value.length===3) return
  picks.value.push({ r,c })
}
function rowsDistinct(){ return new Set(picks.value.map(p=>p.r)).size === picks.value.length }
function colsDistinct(){ return new Set(picks.value.map(p=>p.c)).size === picks.value.length }

/* checking */
async function addPoint(){ try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{} }
async function checkNow(){
  if(picks.value.length!==3){ toast.value = T[L.value].pick3; sWrong&&sWrong.play(); return }
  if(!rowsDistinct() || !colsDistinct()){ toast.value=T[L.value].wrong; sWrong&&sWrong.play(); return }
  if(pickedSum.value === target.value){
    solved.value=true; toast.value=T[L.value].correct; sOK&&sOK.play(); sClap&&sClap.play(); await addPoint()
  }else{
    toast.value=T[L.value].wrong; sWrong&&sWrong.play()
  }
}
</script>

<template>
  <div class="challenge6 challenge-surface" :data-theme="props.theme">
    <h2 class="title">{{ T[L].title }}</h2>
    <p class="rule">{{ T[L].rule(n, target) }}</p>

    <!-- grid -->
    <div class="grid" :style="{'--n': n}">
      <button
        v-for="cell in flat" :key="cell.r + '-' + cell.c"
        class="cell"
        :class="{ picked: picks.some(p => p.r===cell.r && p.c===cell.c) }"
        :aria-pressed="picks.some(p => p.r===cell.r && p.c===cell.c)"
        @click="toggleCell(cell.r, cell.c)"
        :style="numDir"
      >
        {{ cell.v }}
      </button>
    </div>

    <!-- controls -->
    <div class="panel">
      <div class="actions">
        <button class="btn" @click="resetPicks"><RotateCcw class="ic" /> {{ T[L].reset }}</button>
        <button class="btn primary" @click="checkNow"><Check class="ic" /> {{ T[L].check }}</button>
        <button class="btn" @click="newPuzzle"><RefreshCw class="ic" /> {{ T[L].newQ }}</button>
      </div>
      <div v-if="toast" class="toast" :class="{ ok: solved }">{{ toast }}</div>
    </div>
  </div>
</template>

<style scoped>
/* =========================
   Theme tokens with high contrast
========================= */
.challenge6{
  --bg:#ffffff; --fg:#0b1220; --muted:#64748b;

  --panel:#ffffff; --panel-bd:#cbd5e1; --panel-shadow:0 8px 24px rgba(2,6,23,.08);

  --cell-bg:#ffffff; --cell-bd:#cbd5e1;
  --cell-hover:rgba(59,130,246,.14);
  --cell-picked-bg:rgba(59,130,246,.18);
  --cell-picked-bd:#60a5fa;
  --cell-focus:#38bdf8;

  --btn-bg:#ffffff; --btn-bd:#cbd5e1; --btn-fg:#0b1220;
  --btn-primary-bg:#0ea5e9; --btn-primary-fg:#ffffff;

  --toast-err-bg:#fee2e2; --toast-err-fg:#991b1b; --toast-err-bd:#fecaca;
  --toast-ok-bg:#dcfce7;  --toast-ok-fg:#166534;  --toast-ok-bd:#bbf7d0;
}

[data-theme="dark"] .challenge6{
  --bg:#0b1220; --fg:#e5e7eb; --muted:#9ca3af;

  --panel:#0f172a; --panel-bd:#334155; --panel-shadow:0 12px 28px rgba(0,0,0,.5);

  --cell-bg:#111827; --cell-bd:#475569;
  --cell-hover:rgba(56,189,248,.22);
  --cell-picked-bg:rgba(56,189,248,.26);
  --cell-picked-bd:#38bdf8;
  --cell-focus:#38bdf8;

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

/* grid container */
.grid{
  --gap:.6rem;
  display:grid;
  grid-template-columns: repeat(var(--n), 84px);
  grid-auto-rows: 84px;
  gap:var(--gap);
  background:var(--panel);
  border:1px solid var(--panel-bd);
  border-radius:14px;
  box-shadow:var(--panel-shadow);
  padding:.8rem;
  width:max-content;
}

/* cell button */
.cell{
  border:1px solid var(--cell-bd);
  background:var(--cell-bg);
  color:var(--fg);
  border-radius:12px;
  font-variant-numeric:tabular-nums;
  font-weight:800;
  font-size:1.25rem;
  cursor:pointer;
  display:flex; align-items:center; justify-content:center;
  transition:box-shadow .12s, background .12s, border-color .12s, transform .06s;
}
.cell:hover{ background:var(--cell-hover) }
.cell:focus-visible{
  outline:none;
  box-shadow:0 0 0 3px color-mix(in oklab, var(--cell-focus) 35%, transparent);
  border-color:var(--cell-focus)
}
.cell.picked{
  background:var(--cell-picked-bg);
  border-color:var(--cell-picked-bd);
}

/* actions */
.panel{ display:flex; align-items:center; gap:1rem; flex-wrap:wrap; margin-top:.8rem }
.actions{ display:flex; gap:.6rem; flex-wrap:wrap }
.btn{
  display:inline-flex; align-items:center; gap:.45rem;
  padding:.6rem .85rem; border-radius:.95rem;
  background:var(--btn-bg); border:1px solid var(--btn-bd); color:var(--btn-fg);
  cursor:pointer; transition:transform .12s, box-shadow .12s
}
.btn:hover{ transform:translateY(-1px); box-shadow:0 10px 22px rgba(0,0,0,.12) }
.btn.primary{ background:var(--btn-primary-bg); color:var(--btn-primary-fg); border-color:transparent }
.ic{ width:16px; height:16px }

/* feedback */
.toast{
  padding:.6rem .9rem; border-radius:.9rem; text-align:center; font-weight:800;
  background:var(--toast-err-bg); color:var(--toast-err-fg); border:1px solid var(--toast-err-bd)
}
.toast.ok{ background:var(--toast-ok-bg); color:var(--toast-ok-fg); border-color:var(--toast-ok-bd) }
</style>

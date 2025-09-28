<script setup>
import { ref, computed, onMounted } from 'vue'
import { RefreshCw, RotateCcw, Check } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

const T = {
  ar:{
    title: 'التحدي 6: اختر ثلاث خلايا من شبكة بحيث لا تكون في الصف أو العمود نفسه ويكون مجموعها الهدف',
    rule: (n,target)=> `شبكة ${n}×${n}. اختر ثلاث خلايا كلٌّ منها في صف وعمود مختلفين بحيث يساوي مجموعها ${target}.`,
    newQ:'سؤال جديد', reset:'إعادة تعيين', check:'تحقّق',
    correct:'إجابة صحيحة', wrong:'تحقق من القيود أو من المجموع', picked:'المختار: '
  },
  en:{
    title: 'Challenge 6: Pick 3 cells in different rows and columns to reach the target sum',
    rule: (n,target)=> `A ${n}×${n} grid. Pick three cells, one per distinct row and column, whose sum equals ${target}.`,
    newQ:'New puzzle', reset:'Reset', check:'Check',
    correct:'Correct', wrong:'Check the constraints or the sum', picked:'Picked: '
  }
}
const L = computed(()=> (T[props.lang]?props.lang:'ar'))

/* ===== sounds (approved style) ===== */
import successUrl from '@/assets/sounds/success.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong3.mp3'

const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

/* ===== utils ===== */
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]]} return x }

/* ===== state ===== */
const n = ref(3)
const grid = ref([])             // 2D numbers
const target = ref(0)            // target sum (guaranteed solution exists)
const picks = ref([])            // [{r,c}]
const solved = ref(false)
const toast = ref(null)

const numDir = computed(()=>({direction:'ltr', unicodeBidi:'isolate'}))
const pickedSum = computed(()=> picks.value.reduce((s,p)=> s + grid.value[p.r][p.c], 0))

/* ensure a valid solution exists by constructing it first */
function newPuzzle(){
  solved.value=false; toast.value=null; picks.value=[]
  n.value = [3,4][rndInt(0,1)]
  // fill grid with random 1..9
  grid.value = Array.from({length:n.value}, ()=> Array.from({length:n.value}, ()=> rndInt(1,9)))
  // choose 3 distinct rows and 3 distinct cols
  const rows = shuffle([...Array(n.value).keys()]).slice(0,3)
  const cols = shuffle([...Array(n.value).keys()]).slice(0,3)
  // map 1-1 by permutation
  const permCols = shuffle(cols.slice())
  const solution = rows.map((r,i)=> ({r, c: permCols[i]}))
  target.value = solution.reduce((s,p)=> s + grid.value[p.r][p.c], 0)
}

function resetPicks(){ picks.value=[]; toast.value=null; solved.value=false }

function toggleCell(r,c){
  if(solved.value) return
  const idx = picks.value.findIndex(p=> p.r===r && p.c===c)
  if(idx>=0){ picks.value.splice(idx,1); return }
  if(picks.value.length===3) return
  picks.value.push({r,c})
}

function rowsDistinct(){
  const rs = picks.value.map(p=>p.r); return new Set(rs).size===picks.value.length
}
function colsDistinct(){
  const cs = picks.value.map(p=>p.c); return new Set(cs).size===picks.value.length
}

async function addPoint(){
  try{
    await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',
      { method:'GET', credentials:'include' })
  }catch{}
}
async function checkNow(){
  if(picks.value.length!==3){ toast.value = L.value==='ar' ? 'اختر ثلاث خلايا' : 'Pick three cells'; sWrong&&sWrong.play(); return }
  if(!rowsDistinct() || !colsDistinct()){ toast.value=T[L.value].wrong; sWrong&&sWrong.play(); return }
  if(pickedSum.value===target.value){
    solved.value=true; toast.value=T[L.value].correct; sOK&&sOK.play(); sClap&&sClap.play(); await addPoint()
  }else{
    toast.value=T[L.value].wrong; sWrong&&sWrong.play()
  }
}

onMounted(newPuzzle)
</script>

<template>
  <div class="challenge6 challenge-surface" :data-theme="props.theme">
    <h2 class="title">{{ T[L].title }}</h2>
    <p class="rule">{{ T[L].rule(n, target) }}</p>

    <!-- <div class="grid" :style="{'--n': n}">
      <button
        v-for="(row,r) in grid" :key="'r'+r"
        v-for="(val,c) in row" :key="r+'-'+c"
        class="cell"
        :class="{ picked: picks.some(p=>p.r===r&&p.c===c) }"
        @click="toggleCell(r,c)"
        :style="numDir"
      >{{ val }}</button>
    </div> -->
    <div class="grid" v-for="(row,r) in grid" :key="'r'+r" :style="{'--n': n}">
  <button
    v-for="(val,c) in row" :key="r+'-'+c"
    class="cell"
    :class="{ picked: picks.some(p=>p.r===r && p.c===c) }"
    @click="toggleCell(r,c)"
    :style="numDir"
  >
    {{ val }}
  </button>
</div>


    <div class="panel">
 <!--     <div class="status">
        {{ T[L].picked }} {{ picks.length }} · {{ pickedSum }}
      </div> -->
      <div class="actions">
        <button class="btn" @click="resetPicks"><RotateCcw class="ic" /> {{ T[L].reset }}</button>
        <button class="btn" @click="checkNow"><Check class="ic" /> {{ T[L].check }}</button>
        <button class="btn" @click="newPuzzle"><RefreshCw class="ic" /> {{ T[L].newQ }}</button>
      </div>
      <div v-if="toast" class="toast" :class="{ ok: solved }">{{ toast }}</div>
    </div>
  </div>
</template>

<style scoped>
.challenge6{ --bg:var(--c-bg,#fff); --fg:var(--c-fg,#111827); --muted:#6b7280 }
[data-theme="dark"] .challenge6{ --bg:#0b1220; --fg:#e5e7eb; --muted:#9ca3af }
.title{ font-weight:700; margin:0 0 .25rem }
.rule{ color:var(--muted); margin:0 0 1rem }

.grid{
  --gap: .5rem;
  display:grid;
  grid-template-columns: repeat(var(--n), 78px);
  grid-auto-rows: 78px;
  gap: var(--gap);
  background:var(--bg);
  width:max-content;
  margin:.25rem 0 1rem;
  padding:.6rem;
  border-radius:1rem;
  box-shadow:0 4px 14px rgba(0,0,0,.06);
}
.cell{
  border:1px solid #e5e7ebaa;
  background:var(--bg);
  border-radius:.9rem;
  font-variant-numeric: tabular-nums;
  font-weight:700;
  font-size:1.25rem;
  cursor:pointer;
  display:flex; align-items:center; justify-content:center;
  transition: box-shadow .15s, background .15s, border-color .15s;
}
.cell:hover{ box-shadow:0 0 0 3px rgba(99,102,241,.18) inset }
.cell.picked{
  background: rgba(59,130,246,.12);
  border-color: #93c5fd;
  box-shadow: 0 0 0 3px rgba(59,130,246,.28) inset;
}

.panel{ display:flex; align-items:center; gap:1rem; flex-wrap:wrap }
.status{ color:var(--muted) }
.actions{ display:flex; gap:.5rem; flex-wrap:wrap }
.btn{
  display:inline-flex; align-items:center; gap:.35rem;
  padding:.5rem .7rem; border-radius:.75rem;
  border:1px solid #e5e7eb55; background:var(--bg); cursor:pointer
}
.ic{ width:16px; height:16px }

.toast{
  padding:.5rem .75rem; border-radius:.75rem; background:#fee2e2; color:#991b1b;
  border:1px solid #fecaca
}
.toast.ok{ background:#dcfce7; color:#166534; border-color:#bbf7d0 }
</style>

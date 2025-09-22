<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Check, RotateCcw, RefreshCw, Eraser } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

const T = {
  ar:{
    title:'المستوى الثاني – التحدي 2: أكمل مربعاً سحرياً',
    rule:(M)=>`ضع الأعداد بحيث يكون مجموع كل صف وعمود وقطر مساوياً ${M}. اسحب القيم المفقودة إلى أماكنها. الأعداد جميعها مختلفة.`,
    bank:'لوحة الأعداد', newQ:'سؤال جديد', reset:'إعادة تعيين', check:'تحقّق',
    correct:'إجابة صحيحة', wrong:'تحقق من المجاميع أو التكرار', clear:'تفريغ الخلية'
  },
  en:{
    title:'Level 2 – Challenge 2: Complete a magic square',
    rule:(M)=>`Place numbers so each row, column, and diagonal sums to ${M}. Drag the missing values into place. All numbers are distinct.`,
    bank:'Number bank', newQ:'New puzzle', reset:'Reset', check:'Check',
    correct:'Correct answer', wrong:'Check sums or duplicates', clear:'Clear cell'
  }
}
const L = computed(()=> (T[props.lang]?props.lang:'ar'))

/* ===== sounds (approved style) ===== */
import successUrl from '@/assets/sounds/success2.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong2.mp3'

const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

/* ===== utils ===== */
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]] } return x }

/* ===== Lo Shu base (1..9, magic sum 15) ===== */
const LO_SHU = [
  [8,1,6],
  [3,5,7],
  [4,9,2]
]
function symmetries(mat){
  const rot = m => [[m[2][0],m[1][0],m[0][0]],[m[2][1],m[1][1],m[0][1]],[m[2][2],m[1][2],m[0][2]]]
  const flipH = m => m.map(r=>r.slice().reverse())
  const s = []
  let m = mat
  for(let i=0;i<4;i++){ s.push(m); s.push(flipH(m)); m = rot(m) }
  // remove duplicates by string
  const uniq = []; const seen = new Set()
  for(const k of s){ const t=JSON.stringify(k); if(!seen.has(t)){ uniq.push(k); seen.add(t) } }
  return uniq
}
const SHAPES = symmetries(LO_SHU)

/* ===== state ===== */
const grid = ref([[0,0,0],[0,0,0],[0,0,0]])     // القيم الصحيحة
const M = ref(0)                                 // الثابت السحري
const blanks = ref(new Set())                    // "r,c"
const answerMap = ref({})                        // "r,c" -> value
const bankCounts = ref({})                       // value -> count
const solved = ref(false)
const toast = ref(null)

const numDir = computed(()=>({direction:'ltr', unicodeBidi:'isolate'}))
const keyOf = (r,c)=> `${r},${c}`

/* نبني مربع سحري عام بالقيمة: a + s*L */
function buildMagic(){
  const shape = SHAPES[rndInt(0, SHAPES.length-1)]
  const step = [1,2,3,4,5][rndInt(0,4)]          // فارق بين القيم
  const off  = rndInt(0, 6)                      // إزاحة صغيرة
  const g = Array.from({length:3}, ()=> Array(3).fill(0))
  for(let r=0;r<3;r++) for(let c=0;c<3;c++){
    g[r][c] = off + step*shape[r][c]
  }
  grid.value = g
  M.value = step*15 + 3*off
}

/* نختار فراغات */
function pickBlanks(){
  const all=[]
  for(let r=0;r<3;r++) for(let c=0;c<3;c++) all.push([r,c])
  // اترك 3–4 خلايا ظاهرة كمساعدة
  const keep = shuffle(all).slice(0, rndInt(3,4))
  const keepSet = new Set(keep.map(([r,c])=>keyOf(r,c)))
  const chosen = all.filter(([r,c])=> !keepSet.has(keyOf(r,c)))
  blanks.value = new Set(chosen.map(([r,c])=>keyOf(r,c)))
}

/* بنك الأعداد */
function rebuildBank(){
  const counts={}
  blanks.value.forEach(k=>{
    const [r,c]=k.split(',').map(Number)
    const v=grid.value[r][c]
    counts[v]=(counts[v]||0)+1
  })
  for(const [k,v] of Object.entries(answerMap.value)){
    counts[v]=(counts[v]||0)-1
  }
  for(const [v,ct] of Object.entries(counts)){ if(ct<=0) delete counts[v] }
  bankCounts.value=counts
}
const bankList = computed(()=>{
  const out=[]
  for(const [v,ct] of Object.entries(bankCounts.value)){
    for(let i=0;i<ct;i++) out.push(Number(v))
  }
  return shuffle(out)
})

/* لغز جديد */
function newPuzzle(){
  solved.value=false; toast.value=null; answerMap.value={}
  buildMagic()
  pickBlanks()
  rebuildBank()
}

/* تحقق */
function isFilled(){ for(const k of blanks.value){ if(answerMap.value[k]==null) return false } return true }
function filledMatrix(){
  const m = grid.value.map(r=>r.slice())
  for(const k of blanks.value){
    const [r,c]=k.split(',').map(Number)
    m[r][c]=answerMap.value[k]
  }
  return m
}
function noDuplicates(m){
  const seen=new Set()
  for(const r of m) for(const v of r){
    if(seen.has(v)) return false
    seen.add(v)
  }
  return true
}
function sumsOk(m){
  const s = (a,b,c)=> a+b+c
  for(let i=0;i<3;i++){
    if(s(m[i][0],m[i][1],m[i][2])!==M.value) return false
    if(s(m[0][i],m[1][i],m[2][i])!==M.value) return false
  }
  if(s(m[0][0],m[1][1],m[2][2])!==M.value) return false
  if(s(m[0][2],m[1][1],m[2][0])!==M.value) return false
  return true
}
async function addPoint(){
  try{ await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'}) }catch{}
}
async function checkNow(){
  if(!isFilled()){ toast.value=L.value==='ar'?'أكمل كل الخانات':'Fill all blanks'; sWrong&&sWrong.play(); return }
  const m = filledMatrix()
  if(noDuplicates(m) && sumsOk(m)){
    solved.value=true; toast.value=T[L.value].correct; sOK&&sOK.play(); sClap&&sClap.play(); await addPoint()
  }else{
    toast.value=T[L.value].wrong; sWrong&&sWrong.play()
  }
}
function resetAll(){ answerMap.value={}; rebuildBank(); toast.value=null; solved.value=false }

/* سحب/إفلات */
function onDragStart(ev,value){ ev.dataTransfer.setData('text/plain', String(value)) }
function allowDrop(ev){ ev.preventDefault() }
function onDrop(ev,key){
  ev.preventDefault()
  const v = Number(ev.dataTransfer.getData('text/plain'))
  if(answerMap.value[key]!=null){
    const old=answerMap.value[key]
    bankCounts.value[old]=(bankCounts.value[old]||0)+1
  }
  if((bankCounts.value[v]||0)===0) return
  bankCounts.value[v]-=1
  answerMap.value[key]=v
  toast.value=null
}
function clearCell(key){
  if(answerMap.value[key]!=null){
    const old=answerMap.value[key]
    bankCounts.value[old]=(bankCounts.value[old]||0)+1
    delete answerMap.value[key]
  }
}

onMounted(newPuzzle)
watch(()=>props.lang,()=>{})
</script>

<template>
  <div class="lvl2c2" :data-theme="props.theme">
    <h2 class="title">{{ T[L].title }}</h2>
    <p class="rule">{{ T[L].rule(M) }}</p>

    <div class="board">
      <div class="row" v-for="r in 3" :key="'r'+r">
        <div class="cell" v-for="c in 3" :key="'c'+r+'-'+c">
          <template v-if="!blanks.has(`${r-1},${c-1}`)">
            <span class="num" :style="numDir">{{ grid[r-1][c-1] }}</span>
          </template>
          <template v-else>
            <div class="dropzone" @dragover="allowDrop" @drop="onDrop($event, `${r-1},${c-1}`)">
              <span v-if="answerMap[`${r-1},${c-1}`]!=null" class="num" :style="numDir">
                {{ answerMap[`${r-1},${c-1}`] }}
              </span>
              <span v-else class="placeholder">؟</span>
            </div>
            <button class="clear" @click="clearCell(`${r-1},${c-1}`)"><Eraser class="ic" /> {{ T[L].clear }}</button>
          </template>
        </div>
      </div>
    </div>

    <div class="side">
      <div class="bank-title">{{ T[L].bank }}</div>
      <div class="bank-items">
        <button v-for="v in bankList" :key="v + '_' + Math.random()" class="chip"
                draggable="true" @dragstart="onDragStart($event, v)" :style="numDir">
          {{ v }}
        </button>
      </div>

      <div class="actions">
        <button class="btn" @click="resetAll"><RotateCcw class="ic" /> {{ T[L].reset }}</button>
        <button class="btn" @click="checkNow"><Check class="ic" /> {{ T[L].check }}</button>
        <button class="btn" @click="newPuzzle"><RefreshCw class="ic" /> {{ T[L].newQ }}</button>
      </div>

      <div v-if="toast" class="toast" :class="{ ok: solved }">{{ toast }}</div>
    </div>
  </div>
</template>

<style scoped>
.lvl2c2{ --bg:var(--c-bg,#fff); --fg:var(--c-fg,#111827); --muted:#6b7280 }
[data-theme="dark"] .lvl2c2{ --bg:#0b1220; --fg:#e5e7eb; --muted:#9ca3af }

.title{ font-weight:700; margin:0 0 .25rem }
.rule{ color:var(--muted); margin:0 0 1rem }

/* اللوح */
.board{
  display:inline-block; background:var(--bg);
  padding:1rem; border-radius:1rem; box-shadow:0 4px 14px rgba(0,0,0,.06)
}
.row{ display:grid; grid-template-columns:repeat(3, 96px) }
.cell{
  border:1px dashed #cbd5e1; min-height:88px; display:flex; flex-direction:column;
  align-items:center; justify-content:center; gap:.25rem; padding:.25rem
}
.num{ font-variant-numeric:tabular-nums; font-weight:700; font-size:1.25rem }
.placeholder{ color:var(--muted); font-size:1.25rem }
.dropzone{ width:100%; height:100%; display:flex; align-items:center; justify-content:center; background:rgba(99,102,241,.06); border-radius:.5rem }
.clear{ font-size:.75rem; border:none; background:transparent; color:var(--muted); display:flex; align-items:center; gap:.25rem; cursor:pointer }

/* البنك */
.side{ margin-top:1rem; max-width:520px }
.bank-title{ font-weight:600; color:var(--muted); margin:.25rem 0 }
.bank-items{ display:flex; flex-wrap:wrap; gap:.5rem }
.chip{ border:1px solid #e5e7eb55; background:var(--bg); padding:.4rem .6rem; border-radius:.75rem; cursor:grab; font-variant-numeric:tabular-nums }
.actions{ display:flex; gap:.5rem; flex-wrap:wrap; margin-top:.5rem }
.btn{ display:inline-flex; align-items:center; gap:.35rem; padding:.5rem .7rem; border-radius:.75rem; border:1px solid #e5e7eb55; background:var(--bg); cursor:pointer }
.ic{ width:16px; height:16px }

.toast{ margin-top:.5rem; padding:.5rem .75rem; border-radius:.75rem; background:#fee2e2; color:#991b1b; border:1px solid #fecaca }
.toast.ok{ background:#dcfce7; color:#166534; border-color:#bbf7d0 }
</style>

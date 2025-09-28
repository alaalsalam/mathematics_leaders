<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { RefreshCw, RotateCcw, Check } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

const T = {
  ar:{
    title:'المستوى الثاني – التحدي 4: اختر الإجابة الصحيحة',
    rule:(S,D)=>`ما العددان اللذان حاصل جمعهما ${S} والفرق بينهما ${D}؟ اختر الزوج الصحيح.`,
    choices:'الخيارات',
    newQ:'سؤال جديد', reset:'إعادة تعيين', check:'تحقّق',
    correct:'إجابة صحيحة', wrong:'إجابة غير صحيحة'
  },
  en:{
    title:'Level 2 – Challenge 4: Pick the correct pair',
    rule:(S,D)=>`Which two numbers have sum ${S} and difference ${D}? Pick the correct pair.`,
    choices:'Choices',
    newQ:'New puzzle', reset:'Reset', check:'Check',
    correct:'Correct', wrong:'Incorrect'
  }
}
const L = computed(()=> (T[props.lang]?props.lang:'ar'))

/* ===== sounds (approved style) ===== */
import successUrl from '@/assets/sounds/success4.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong4.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

/* utils */
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]]} return x }

/* state */
const S = ref(0)           // sum
const D = ref(0)           // difference (non-negative)
const solution = ref([0,0])// [big, small]
const options = ref([])    // array of [big, small]
const pick = ref(null)
const toast = ref(null)
const solved = ref(false)

function buildPuzzle(){
  solved.value=false; toast.value=null; pick.value=null
  // choose integers with same parity and S>D
  let a,b
  // pick base numbers 1..60
  a = rndInt(6, 60)
  b = rndInt(1, a-1)
  // ensure parity constraints automatically satisfied by using a,b to derive S,D
  const big = Math.max(a,b), small = Math.min(a,b)
  S.value = big + small
  D.value = big - small
  solution.value = [big, small]

  // build distractors
  const opts = [[big,small]]
  // 1: swap (still correct for difference? swap gives same pair visually إذا عرضنا "الكبير ، الصغير")
  // لتجنّب التطابق، سنعرض دائماً (الكبير، الصغير). إذن نضيف مشتتات أخرى فقط.
  const gen = ()=>{
    // random pair not equal to solution and distinct
    let x = rndInt(1, 65), y = rndInt(1, 65)
    if(x<y) [x,y]=[y,x]
    return [x,y]
  }
  while(opts.length<6){
    let p = gen()
    // avoid having same sum and diff كليهما
    if(p[0]+p[1]===S.value && p[0]-p[1]===D.value) continue
    // sometimes share only sum أو فقط الفرق لإرباك منطقي
    if(rndInt(0,1)===0){ // same sum, wrong diff
      const s = S.value
      const x = rndInt(1, s-1); const y = s-x; const pair=[Math.max(x,y), Math.min(x,y)]
      if(pair[0]-pair[1]!==D.value) p=pair
    }else{ // same diff, wrong sum
      const d = D.value
      const y = rndInt(1, 50); const x = y + d; const pair=[x,y]
      if(pair[0]+pair[1]!==S.value) p=pair
    }
    if(!opts.some(q=> q[0]===p[0] && q[1]===p[1])) opts.push(p)
  }
  options.value = shuffle(opts)
}

async function addPoint(){
  try{
    await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',
      {method:'GET',credentials:'include'})
  }catch{}
}

async function checkNow(){
  if(pick.value==null){ toast.value = L.value==='ar'?'اختر إجابة':'Pick an answer'; sWrong&&sWrong.play(); return }
  const chosen = options.value[pick.value]
  const ok = (chosen[0]+chosen[1]===S.value) && (chosen[0]-chosen[1]===D.value)
  if(ok){ solved.value=true; toast.value=T[L.value].correct; sOK&&sOK.play(); sClap&&sClap.play(); await addPoint() }
  else { toast.value=T[L.value].wrong; sWrong&&sWrong.play() }
}

function resetAll(){ pick.value=null; toast.value=null; solved.value=false }

onMounted(buildPuzzle)
watch(()=>props.lang,()=>{})
</script>

<template>
  <div class="lvl2c4 challenge-surface" :data-theme="props.theme">
    <h2 class="title">{{ T[L].title }}</h2>
    <p class="rule">{{ T[L].rule(S, D) }}</p>

    <div class="choices">
      <div class="choice" v-for="(op, i) in options" :key="i" @click="pick=i" :class="{sel: pick===i}">
        <input type="radio" :checked="pick===i" />
        <span class="pair">{{ op[0] }} ، {{ op[1] }}</span>
        <!-- <small class="hint">({{ op[0] + op[1] }} ، {{ op[0] - op[1] }})</small> -->
      </div>
    </div>

    <div class="actions">
      <button class="btn" @click="resetAll"><RotateCcw class="ic" /> {{ T[L].reset }}</button>
      <button class="btn" @click="checkNow"><Check class="ic" /> {{ T[L].check }}</button>
      <button class="btn" @click="buildPuzzle"><RefreshCw class="ic" /> {{ T[L].newQ }}</button>
    </div>

    <div v-if="toast" class="toast" :class="{ ok: solved }">{{ toast }}</div>
  </div>
</template>

<style scoped>
.lvl2c4{ --bg:var(--c-bg,#fff); --fg:var(--c-fg,#111827); --muted:#6b7280 }
[data-theme="dark"] .lvl2c4{ --bg:#0b1220; --fg:#e5e7eb; --muted:#9ca3af }
.title{ font-weight:700; margin:0 0 .25rem }
.rule{ color:var(--muted); margin:0 0 1rem }

.choices{
  display:grid; gap:.5rem;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  margin-bottom:.75rem;
}
.choice{
  display:flex; align-items:center; gap:.5rem;
  padding:.55rem .7rem; border-radius:.75rem;
  border:1px solid #e5e7ebaa; background:var(--bg);
  cursor:pointer;
}
.choice.sel{ box-shadow:0 0 0 3px rgba(59,130,246,.25) inset; border-color:#93c5fd }
.pair{ font-variant-numeric:tabular-nums; font-weight:700 }
.hint{ color:var(--muted) } /* يعرض (المجموع، الفرق) للتحقق الذهني */

.actions{ display:flex; gap:.5rem; flex-wrap:wrap; margin-top:.5rem }
.btn{
  display:inline-flex; align-items:center; gap:.35rem;
  padding:.5rem .7rem; border-radius:.75rem; border:1px solid #e5e7eb55;
  background:var(--bg); cursor:pointer
}
.ic{ width:16px; height:16px }

.toast{ margin-top:.6rem; padding:.55rem .8rem; border-radius:.75rem; background:#fee2e2; color:#991b1b; border:1px solid #fecaca }
.toast.ok{ background:#dcfce7; color:#166534; border-color:#bbf7d0 }
</style>

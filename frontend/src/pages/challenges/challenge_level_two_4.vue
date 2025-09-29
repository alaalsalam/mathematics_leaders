<script setup>
/* =========================================================
   Level 2 — Challenge 4: Pick the correct pair (Sum & Diff)
   Dark-mode pass
   ---------------------------------------------------------
   - Keeps your game logic unchanged.
   - Adds strong theme tokens and high-contrast styles.
   - Clear selected/hover states + accessible focus rings.
   - Radios are purely decorative; click the whole card.
========================================================= */

import { ref, computed, onMounted, watch } from 'vue'
import { RefreshCw, RotateCcw, Check } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

/* --------- copy --------- */
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

/* --------- sounds (optional) --------- */
import successUrl from '@/assets/sounds/success4.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong4.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK&&(sOK.preload='auto'); sClap&&(sClap.preload='auto'); sWrong&&(sWrong.preload='auto')

/* --------- utils --------- */
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]]} return x }

/* --------- state --------- */
const S = ref(0)
const D = ref(0)
const solution = ref([0,0])   // [big, small]
const options = ref([])       // [[b,s], ...]
const pick = ref(null)
const toast = ref(null)
const solved = ref(false)

/* Build a consistent puzzle with realistic distractors */
function buildPuzzle(){
  solved.value=false; toast.value=null; pick.value=null

  // Pick two positive integers and derive S,D so parity is consistent.
  const a = rndInt(6, 60)
  const b = rndInt(1, a-1)
  const big = Math.max(a,b), small = Math.min(a,b)

  S.value = big + small
  D.value = big - small
  solution.value = [big, small]

  // Build distractors: some share only sum, others only diff.
  const opts = [[big, small]]

  const mkSameSum = () => {
    const s = S.value
    const x = rndInt(1, s-1); const y = s-x
    const p = [Math.max(x,y), Math.min(x,y)]
    return (p[0]-p[1]===D.value) ? mkSameSum() : p
  }
  const mkSameDiff = () => {
    const d = D.value
    const y = rndInt(1, 60); const x = y + d
    const p = [x,y]
    return (p[0]+p[1]===S.value) ? mkSameDiff() : p
  }

  while(opts.length<6){
    const p = (Math.random()<0.5) ? mkSameSum() : mkSameDiff()
    if(!opts.some(q=>q[0]===p[0] && q[1]===p[1])) opts.push(p)
  }
  options.value = shuffle(opts)
}

async function addPoint(){
  try{
    await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'})
  }catch{}
}

async function checkNow(){
  if(pick.value==null){ toast.value = L.value==='ar'?'اختر إجابة':'Pick an answer'; sWrong&&sWrong.play(); return }
  const [x,y] = options.value[pick.value]
  const ok = (x+y===S.value) && (x-y===D.value)
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

    <div class="choices" role="list">
      <button
        v-for="(op,i) in options"
        :key="i"
        class="choice"
        :class="{ sel: pick===i }"
        @click="pick=i"
        role="listitem"
      >
        <!-- decorative radio -->
        <span class="dot" aria-hidden="true"></span>
        <span class="pair" :style="{direction:'ltr', unicodeBidi:'isolate'}">{{ op[0] }} , {{ op[1] }}</span>
      </button>
    </div>

    <div class="actions">
      <button class="btn" @click="resetAll"><RotateCcw class="ic" /> {{ T[L].reset }}</button>
      <button class="btn primary" @click="checkNow"><Check class="ic" /> {{ T[L].check }}</button>
      <button class="btn" @click="buildPuzzle"><RefreshCw class="ic" /> {{ T[L].newQ }}</button>
    </div>

    <div v-if="toast" class="toast" :class="{ ok: solved }">{{ toast }}</div>
  </div>
</template>

<style scoped>
/* =========================
   Theme tokens (high contrast)
========================= */
.lvl2c4{
  --bg:#ffffff; --fg:#0b1220; --muted:#64748b;

  --panel:#ffffff; --panel-bd:#cbd5e1; --panel-shadow:0 8px 24px rgba(2,6,23,.08);

  --card-bg:#ffffff; --card-bd:#cbd5e1; --card-ring:#38bdf8; --card-sel:#0ea5e9;
  --dot-bg:#e2e8f0; --dot-active:#0ea5e9;

  --btn-bg:#ffffff; --btn-bd:#cbd5e1; --btn-fg:#0b1220;
  --btn-primary-bg:#0ea5e9; --btn-primary-fg:#ffffff;

  --toast-err-bg:#fee2e2; --toast-err-fg:#991b1b; --toast-err-bd:#fecaca;
  --toast-ok-bg:#dcfce7;  --toast-ok-fg:#166534;  --toast-ok-bd:#bbf7d0;
}

[data-theme="dark"] .lvl2c4{
  --bg:#0b1220; --fg:#e5e7eb; --muted:#9ca3af;

  --panel:#0f172a; --panel-bd:#334155; --panel-shadow:0 12px 28px rgba(0,0,0,.55);

  --card-bg:#111827; --card-bd:#475569; --card-ring:#38bdf8; --card-sel:#38bdf8;
  --dot-bg:#334155; --dot-active:#38bdf8;

  --btn-bg:#111827; --btn-bd:#475569; --btn-fg:#e5e7eb;
  --btn-primary-bg:#38bdf8; --btn-primary-fg:#0b1220;

  --toast-err-bg:rgba(248,113,113,.18); --toast-err-fg:#fecaca; --toast-err-bd:rgba(248,113,113,.45);
  --toast-ok-bg:rgba(34,197,94,.22);    --toast-ok-fg:#bbf7d0;  --toast-ok-bd:rgba(34,197,94,.5);
}

/* =========================
   Layout & text
========================= */
.title{ font-weight:800; margin:0 0 .35rem; color:var(--fg) }
.rule{ color:var(--muted); margin:0 0 1rem }

/* Choices grid */
.choices{
  display:grid; gap:.6rem;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  margin-bottom:.9rem;
}
.choice{
  display:flex; align-items:center; gap:.6rem;
  padding:.7rem .9rem; border-radius:14px;
  background:var(--card-bg); color:var(--fg);
  border:1px solid var(--card-bd);
  box-shadow:var(--panel-shadow);
  cursor:pointer;
  transition:box-shadow .15s, transform .1s, border-color .15s;
}
.choice:hover{ transform:translateY(-1px); box-shadow:0 14px 26px rgba(0,0,0,.18) }
.choice:focus-visible{ outline:none; box-shadow:0 0 0 3px color-mix(in oklab, var(--card-ring) 35%, transparent) inset }
.choice.sel{
  border-color:var(--card-sel);
  box-shadow:0 0 0 3px color-mix(in oklab, var(--card-sel) 35%, transparent) inset;
}

/* Decorative radio dot */
.dot{
  width:18px; height:18px; border-radius:999px;
  background:var(--dot-bg); position:relative; flex:0 0 18px;
}
.choice.sel .dot::after{
  content:""; position:absolute; inset:3px; border-radius:999px; background:var(--dot-active);
}

.pair{ font-variant-numeric:tabular-nums; font-weight:800 }

/* Actions */
.actions{ display:flex; gap:.6rem; flex-wrap:wrap }
.btn{
  display:inline-flex; align-items:center; gap:.45rem;
  padding:.55rem .85rem; border-radius:.9rem;
  border:1px solid var(--btn-bd); background:var(--btn-bg); color:var(--btn-fg);
  cursor:pointer; transition:transform .1s, box-shadow .1s
}
.btn:hover{ transform:translateY(-1px); box-shadow:0 10px 22px rgba(0,0,0,.14) }
.btn.primary{ background:var(--btn-primary-bg); color:var(--btn-primary-fg); border-color:transparent }
.ic{ width:16px; height:16px }

/* Toasts */
.toast{
  margin-top:.6rem; padding:.6rem .9rem; border-radius:.9rem; font-weight:800; text-align:center;
  background:var(--toast-err-bg); color:var(--toast-err-fg); border:1px solid var(--toast-err-bd)
}
.toast.ok{ background:var(--toast-ok-bg); color:var(--toast-ok-fg); border-color:var(--toast-ok-bd) }
</style>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RefreshCw, RotateCcw, Check } from 'lucide-vue-next'

const props = defineProps({ lang:{type:String,default:'ar'}, theme:{type:String,default:'light'} })

const T = {
  ar:{
    title: 'التحدي 1 (المستوى الثاني): كوّن جملة عددية تستعمل 1،2،3،4،5 دون تكرار',
    rule: (t)=> `اكتب تعبيراً حسابياً يستخدم الأرقام ١،٢،٣،٤،٥ كلٌّ مرة واحدة فقط ويكون ناتجه ${t}. يمكن استعمال + - × ÷ والأقواس، ولا يُسمح بأي أرقام أخرى أو تكرار.`,
    inputPH: 'اكتب التعبير هنا… مثل: (5*4)*(3+2)*1',
    keys: 'لوحة المفاتيح',
    newQ:'سؤال جديد', reset:'مسح', check:'تحقّق',
    correct:'إجابة صحيحة', wrong:'تحقق من الشروط أو من النتيجة',
    used: 'استخدام الأرقام:',
    note: 'تلميح: يمكنك دائماً استعمال ×1 دون تغيير النتيجة.'
  },
  en:{
    title: 'Level 2 – Challenge 1: Build an expression with 1..5 once each',
    rule: (t)=> `Write an expression that uses digits 1,2,3,4,5 exactly once and evaluates to ${t}. Allowed: + - * / and parentheses. No other digits or repeats.`,
    inputPH: 'Type expression… e.g., (5*4)*(3+2)*1',
    keys: 'Keypad',
    newQ:'New puzzle', reset:'Clear', check:'Check',
    correct:'Correct', wrong:'Check constraints or value',
    used: 'Digits usage:',
    note: 'Hint: multiplying by 1 keeps the value unchanged.'
  }
}
const L = computed(()=> (T[props.lang]?props.lang:'ar'))

/* ===== sounds (approved style) ===== */
import successUrl from '@/assets/sounds/success2.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/oh_no.mp3'

const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

/* ===== random helpers ===== */
function rndInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ const x=a.slice(); for(let i=x.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [x[i],x[j]]=[x[j],x[i]] } return x }

/* ===== state ===== */
const expr = ref('')
const target = ref(0)
const toast = ref(null)
const solved = ref(false)

const digits = [1,2,3,4,5]
const ops = ['+','-','*','/','(',')']

/* build guaranteed-solvable target:
   we form E = (a op1 b) op2 (c op3 d) then optionally *1 or +1
   where {a,b,c,d} is a permutation of {2,3,4,5} and '1' remains available. */
function buildTarget(){
  const nums = shuffle([2,3,4,5])
  const [a,b,c,d] = nums
  const pick = arr => arr[rndInt(0,arr.length-1)]
  const op1 = pick(['+','-','*','/'])
  const op2 = pick(['+','-','*','/'])
  const op3 = pick(['+','-','*','/'])
  // build safely using Function
  const val = (x)=>{
    try{ return Function(`return (${x});`)() }catch{ return null }
  }
  let e = `( ${a} ${op1} ${b} ) ${op2} ( ${c} ${op3} ${d} )`
  let v = val(e)
  // if invalid (division by zero or non-integer not required), retry a few times
  let tries=0
  while((v==null || !isFinite(v)) && tries<20){
    return buildTarget()
  }
  // randomly decide to multiply by 1 or leave as-is but attach *1 so digit 1 is used
  if(Math.random()<0.7){
    e = `(${e}) * 1`
    v = val(e)
  }else{
    // if we didn't use *1, add +1 and then subtract 1 using grouping to still use digit 1 once:
    // ((...)+1) - 1  == original value
    e = `((${e}) + 1) - 1`
    v = val(e)
  }
  target.value = v
  // reset input
  expr.value = ''
  toast.value = null
  solved.value = false
  // we don't show the internal expression to اللاعب
}

/* keypad helpers */
function addToken(t){ expr.value += t }
function backspace(){ expr.value = expr.value.slice(0,-1) }
function clearAll(){ expr.value=''; toast.value=null; solved.value=false }

/* validators */
const usage = computed(()=>{
  const u = {1:0,2:0,3:0,4:0,5:0}
  for(const ch of expr.value){
    if('12345'.includes(ch)) u[ch]++
  }
  return u
})
function onlyAllowedChars(s){
  return /^[\d\+\-\*\/\(\)\s]*$/.test(s)
}
function usesExactDigits(){
  // forbid any digit other than 1..5
  if(/[06789]/.test(expr.value)) return false
  const u = usage.value
  return digits.every(d => u[d]===1)
}
function safeEval(s){
  try{
    // prevent dangerous tokens
    if(!onlyAllowedChars(s)) return null
    // replace '÷' or '×' if user pasted them
    s = s.replace(/×/g,'*').replace(/÷/g,'/')
    // block consecutive digits that create multi-digit numbers not from 1..5
    // allow numbers 1..5 and parentheses/ops/spaces
    if(/\b(?![1-5]\b)\d+\b/.test(s)) return null
    return Function(`"use strict"; return (${s});`)()
  }catch{ return null }
}
async function checkNow(){
  const v = safeEval(expr.value)
  if(v==null || !isFinite(v) || !usesExactDigits()){
    toast.value = T[L.value].wrong
    sWrong && sWrong.play()
    return
  }
  if(Math.abs(v - target.value) < 1e-9){
    solved.value = true
    toast.value = T[L.value].correct
    sOK && sOK.play(); sClap && sClap.play()
    try{
      await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',{method:'GET',credentials:'include'})
    }catch{}
  }else{
    toast.value = T[L.value].wrong
    sWrong && sWrong.play()
  }
}

onMounted(buildTarget)
</script>

<template>
  <div class="lvl2c1 challenge-surface" :data-theme="props.theme">
    <h2 class="title">{{ T[L].title }}</h2>
    <p class="rule">{{ T[L].rule(target) }}</p>

    <div class="panel">
      <input
        class="expr"
        :placeholder="T[L].inputPH"
        v-model="expr"
        dir="ltr"
        inputmode="numeric"
        autocomplete="off"
        spellcheck="false"
      />

      <div class="usage">
        {{ T[L].used }}
        <span v-for="d in digits" :key="d" class="u"
              :class="{ok: usage[d]===1, bad: usage[d]>1}">
          {{ d }}: {{ usage[d] }}
        </span>
      </div>

      <div class="keypad">
        <div class="label">{{ T[L].keys }}</div>
        <div class="row">
          <button class="k" v-for="d in digits" :key="'d'+d" @click="addToken(String(d))">{{ d }}</button>
          <button class="k" v-for="o in ops" :key="'o'+o" @click="addToken(o)">{{ o }}</button>
          <button class="k wide" @click="backspace">⌫</button>
        </div>
      </div>

      <div class="actions">
        <button class="btn" @click="clearAll"><RotateCcw class="ic" /> {{ T[L].reset }}</button>
        <button class="btn" @click="checkNow"><Check class="ic" /> {{ T[L].check }}</button>
        <button class="btn" @click="buildTarget"><RefreshCw class="ic" /> {{ T[L].newQ }}</button>
      </div>

      <div class="hint">{{ T[L].note }}</div>
      <div v-if="toast" class="toast" :class="{ ok: solved }">{{ toast }}</div>
    </div>
  </div>
</template>

<style scoped>
.lvl2c1{ --bg:var(--c-bg,#fff); --fg:var(--c-fg,#111827); --muted:#6b7280 }
[data-theme="dark"] .lvl2c1{ --bg:#0b1220; --fg:#e5e7eb; --muted:#9ca3af }

.title{ font-weight:700; margin:0 0 .25rem }
.rule{ color:var(--muted); margin:0 0 1rem }

.panel{
  background:var(--bg); border-radius:1rem; padding:1rem;
  box-shadow:0 4px 14px rgba(0,0,0,.06); max-width:720px
}
.expr{
  width:100%; padding:.6rem .75rem; border-radius:.75rem;
  border:1px solid #e5e7ebaa; background:var(--bg); color:var(--fg);
  font-size:1.1rem; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}
.usage{ margin:.5rem 0; color:var(--muted); display:flex; gap:.6rem; flex-wrap:wrap }
.u{ padding:.15rem .45rem; border-radius:.5rem; border:1px solid #e5e7ebaa; background:var(--bg) }
.u.ok{ background:#dcfce7; color:#166534; border-color:#bbf7d0 }
.u.bad{ background:#fee2e2; color:#991b1b; border-color:#fecaca }

.keypad{ margin-top:.5rem }
.keypad .label{ color:var(--muted); margin-bottom:.25rem }
.keypad .row{ display:flex; flex-wrap:wrap; gap:.4rem }
.k{
  padding:.45rem .6rem; border-radius:.6rem; border:1px solid #e5e7ebaa;
  background:var(--bg); cursor:pointer; min-width:40px
}
.k.wide{ min-width:64px }

.actions{ display:flex; gap:.5rem; flex-wrap:wrap; margin-top:.6rem }
.btn{
  display:inline-flex; align-items:center; gap:.35rem;
  padding:.5rem .7rem; border-radius:.75rem; border:1px solid #e5e7eb55;
  background:var(--bg); cursor:pointer
}
.ic{ width:16px; height:16px }

.hint{ color:var(--muted); margin-top:.5rem; font-size:.9rem }

.toast{ margin-top:.6rem; padding:.55rem .8rem; border-radius:.75rem;
        background:#fee2e2; color:#991b1b; border:1px solid #fecaca }
.toast.ok{ background:#dcfce7; color:#166534; border-color:#bbf7d0 }
</style>

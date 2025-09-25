<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Check, RotateCcw, RefreshCw } from 'lucide-vue-next'

const props = defineProps({ lang:{ type:String, default:'ar' }, theme:{ type:String, default:'light' } })

const copy = {
  ar:{
    title:'المستوى الثاني – التحدي 6: مقارنة الأوزان',
    premise:{
      line1:'وزن كرتان ومربع واحد يساويان ٨ وحدات.',
      line2:'وزن كرتان ومثلث واحد يساويان ٦ وحدات.',
      question:'ما وزن المربع الواحد مقارنة بالمثلث؟'
    },
    options:[
      { id:'a', text:'ضعف وزن المثلث' },
      { id:'b', text:'يساوي وزن المثلث' },
      { id:'c', text:'نصف وزن المثلث' },
      { id:'d', text:'أقل بـ٢ وحدة من وزن المثلث' },
      { id:'e', text:'أكثر بـ٢ وحدة من وزن المثلث' }
    ],
    newQ:'سؤال جديد', reset:'إعادة تعيين', check:'تحقّق',
    correct:'إجابة صحيحة! المربع أثقل من المثلث بوحدتين.',
    wrong:'إجابة غير صحيحة. أعد التفكير في المعادلات.',
    pick:'اختر إجابة أولاً.'
  },
  en:{
    title:'Level 2 – Challenge 6: Comparing weights',
    premise:{
      line1:'Two balls and one square weigh 8 units.',
      line2:'Two balls and one triangle weigh 6 units.',
      question:'How does the weight of the square compare to the triangle?'
    },
    options:[
      { id:'a', text:'Twice the triangle' },
      { id:'b', text:'Equal to the triangle' },
      { id:'c', text:'Half the triangle' },
      { id:'d', text:'2 units less than the triangle' },
      { id:'e', text:'2 units more than the triangle' }
    ],
    newQ:'New question', reset:'Reset', check:'Check',
    correct:'Correct! The square is heavier by 2 units.',
    wrong:'That is incorrect. Revisit the equations.',
    pick:'Select an option first.'
  }
}

const L = computed(()=> (copy[props.lang]?props.lang:'ar'))
const CORRECT_ID = 'e'

/* sounds */
import successUrl from '@/assets/sounds/success2.mp3'
import clapUrl    from '@/assets/sounds/clap.mp3'
import wrongUrl   from '@/assets/sounds/wrong2.mp3'
const sOK    = typeof Audio!=='undefined' ? new Audio(successUrl) : null
const sClap  = typeof Audio!=='undefined' ? new Audio(clapUrl)    : null
const sWrong = typeof Audio!=='undefined' ? new Audio(wrongUrl)   : null
sOK && (sOK.preload='auto'); sClap && (sClap.preload='auto'); sWrong && (sWrong.preload='auto')

const selected = ref(null)
const feedback = ref(null)
const solved = ref(false)
const shuffledOptions = ref(null)

function resetAll(){
  selected.value = null
  feedback.value = null
  solved.value = false
}

async function addPoint(){
  try{
    await fetch('/api/method/mathematics_leaders.api.game_points.add_point?amount=1',
      { method:'GET', credentials:'include' })
  }catch{}
}

async function checkAnswer(){
  if(!selected.value){
    feedback.value = copy[L.value].pick
    sWrong && sWrong.play()
    return
  }
  if(selected.value === CORRECT_ID){
    const wasSolved = solved.value
    solved.value = true
    feedback.value = copy[L.value].correct
    sOK && sOK.play(); sClap && sClap.play()
    if(!wasSolved){
      await addPoint()
    }
  } else {
    solved.value = false
    feedback.value = copy[L.value].wrong
    sWrong && sWrong.play()
  }
}

function randomizePrompt(){
  shuffledOptions.value = copy[L.value].options.slice().sort(() => Math.random() - 0.5)
  resetAll()
}

watch(() => props.lang, () => {
  shuffledOptions.value = null
  resetAll()
  randomizePrompt()
})

const optionsList = computed(() => shuffledOptions.value || copy[L.value].options)

onMounted(() => {
  randomizePrompt()
})
</script>

<template>
  <div class="lvl2c6 challenge-surface" :data-theme="props.theme">
    <header class="head">
      <h2 class="title">{{ copy[L].title }}</h2>
      <p class="premise">{{ copy[L].premise.line1 }}</p>
      <p class="premise">{{ copy[L].premise.line2 }}</p>
      <p class="question">{{ copy[L].premise.question }}</p>
    </header>

    <section class="options">
      <label
        v-for="option in optionsList"
        :key="option.id"
        class="option"
        :class="{ selected: selected === option.id }"
      >
        <input
          type="radio"
          name="weight-comparison"
          :value="option.id"
          v-model="selected"
        />
        <span class="mark"></span>
        <span class="text">{{ option.text }}</span>
      </label>
    </section>

    <section class="actions">
      <button class="btn" @click="checkAnswer"><Check class="ic" /> {{ copy[L].check }}</button>
      <button class="btn" @click="resetAll"><RotateCcw class="ic" /> {{ copy[L].reset }}</button>
      <button class="btn" @click="randomizePrompt"><RefreshCw class="ic" /> {{ copy[L].newQ }}</button>
    </section>

    <transition name="fade">
      <div v-if="feedback" class="feedback" :class="{ ok: solved }">{{ feedback }}</div>
    </transition>
  </div>
</template>

<style scoped>
.lvl2c6{ --fg:#1f2937; --bg:#f8fafc; --panel:#ffffff; --bd:#cbd5f5; --accent:#2563eb;
  padding:24px; border-radius:18px; color:var(--fg); background:linear-gradient(135deg,#eef2ff,#f8fafc);
  box-shadow:0 14px 30px rgba(37,99,235,.12) }
[data-theme="dark"] .lvl2c6{ --fg:#e2e8f0; --bg:#0f172a; --panel:#111c32; --bd:#1d2a44; --accent:#60a5fa;
  background:linear-gradient(135deg,#0f172a,#1e293b) }

.head{ margin-bottom:18px }
.title{ margin:0 0 12px; font-size:1.6rem; font-weight:800 }
.premise{ margin:0 0 6px; line-height:1.6; opacity:.85 }
.question{ margin:10px 0 0; font-size:1.1rem; font-weight:700 }

.options{ display:grid; gap:12px; margin:20px 0 }
.option{ position:relative; display:flex; align-items:center; gap:12px; padding:14px 16px; border-radius:14px;
  border:2px solid transparent; background:var(--panel); box-shadow:0 8px 20px rgba(37,99,235,.08); cursor:pointer;
  transition:.18s }
.option:hover{ transform:translateY(-1px); box-shadow:0 12px 28px rgba(37,99,235,.12) }
.option.selected{ border-color:var(--accent); box-shadow:0 12px 28px rgba(37,99,235,.18) }
.option input{ display:none }
.mark{ width:18px; height:18px; border-radius:50%; border:2px solid var(--accent); display:inline-block; flex-shrink:0; position:relative }
.option.selected .mark::after{ content:''; position:absolute; inset:3px; border-radius:50%; background:var(--accent) }
.text{ font-weight:600; line-height:1.5 }

.actions{ display:flex; flex-wrap:wrap; gap:12px; margin-top:18px }
.btn{ display:inline-flex; align-items:center; gap:8px; padding:10px 20px; border-radius:12px; border:1px solid var(--bd);
  background:var(--panel); cursor:pointer; font-weight:700; transition:.15s }
.btn:hover{ transform:translateY(-1px); box-shadow:0 10px 24px rgba(37,99,235,.12) }
.ic{ width:18px; height:18px }

.feedback{ margin-top:20px; padding:12px 18px; border-radius:12px; border:1px solid #fecaca; background:#fee2e2; color:#b91c1c; font-weight:700 }
.feedback.ok{ border-color:#bbf7d0; background:#dcfce7; color:#166534 }
[data-theme="dark"] .feedback{ background:rgba(248,113,113,.18); border-color:rgba(248,113,113,.45); color:#fecaca }
[data-theme="dark"] .feedback.ok{ background:rgba(34,197,94,.22); border-color:rgba(34,197,94,.5); color:#bbf7d0 }

.fade-enter-active,.fade-leave-active{ transition:opacity .2s }
.fade-enter-from,.fade-leave-to{ opacity:0 }
</style>

<!-- <script setup>
import { ref, computed, watch, onMounted } from 'vue'

/* ===================== اللغة ===================== */
const lang = ref(localStorage.getItem('ml_lang') || 'ar')
const dir  = computed(() => (lang.value === 'ar' ? 'rtl' : 'ltr'))
const t = (k)=>({
  en:{signin:'Sign In',signup:'Create Account',username:'Username',password:'Password',confirm:'Confirm Password',
      login:'Login',register:'Signup',toSignup:'Create account',toSignin:'Back to login',forgot:'Forgot password?'},
  ar:{signin:'تسجيل الدخول',signup:'إنشاء حساب',username:'اسم المستخدم',password:'كلمة المرور',confirm:'تأكيد كلمة المرور',
      login:'دخول',register:'تسجيل',toSignup:'إنشاء حساب',toSignin:'العودة لتسجيل الدخول',forgot:'نسيت كلمة المرور؟'}
}[lang.value][k])

function toggleLang(){ lang.value = lang.value==='ar' ? 'en' : 'ar' }
watch(lang, v => {
  localStorage.setItem('ml_lang', v)
  document.documentElement.dir = dir.value
  document.documentElement.lang = v
})
onMounted(() => {
  document.documentElement.dir  = dir.value
  document.documentElement.lang = lang.value
})

/* ===================== حالة الواجهة ===================== */
const showSignup  = ref(false)
const inForm      = ref({ username:'', password:'' })
const upForm      = ref({ username:'', password:'', confirm:'' })
const submitting  = ref(false)
const notice      = ref(null)

/* ===================== صور الخلفية والأوراق ===================== */
const bgUrl    = new URL('../assets/images/bg.jpg',    import.meta.url).href
const girlUrl  = new URL('../assets/images/girl.png',  import.meta.url).href
const treesUrl = new URL('../assets/images/trees.png', import.meta.url).href
const leaf01   = new URL('../assets/images/leaf_1.png',  import.meta.url).href
const leaf02   = new URL('../assets/images/leaf_2.png',  import.meta.url).href
const leaf03   = new URL('../assets/images/leaf_3.png',  import.meta.url).href
const leaf04   = new URL('../assets/images/leaf_4.png',  import.meta.url).href
const leaf01_  = new URL('../assets/images/leaf_1_.png', import.meta.url).href
const leaf02_  = new URL('../assets/images/leaf_2_.png', import.meta.url).href
const leaf03_  = new URL('../assets/images/leaf_3_.png', import.meta.url).href
const leaf04_  = new URL('../assets/images/leaf_4_.png', import.meta.url).href
const leafImgs = [leaf01, leaf02, leaf03, leaf04, leaf01_, leaf02_, leaf03_, leaf04_]

/* ===================== أدوات HTTP ===================== */
/* استخدم نفس الأصل. ترك BASE فارغًا يعني استعمال المسار النسبي */
const BASE = ''  // أو: const BASE = window.location.origin

async function get(url, params = {}) {
  const qs = new URLSearchParams(params).toString()
  const r  = await fetch(BASE + url + (qs ? `?${qs}` : ''), {
    method: 'GET',
    credentials: 'include',
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw data
  return data
}

function extractErr(e){
  if (typeof e === 'string') return e
  if (e?._server_messages){
    try {
      const list  = JSON.parse(e._server_messages)
      const first = list?.[0] && JSON.parse(list[0])
      return first?.message || first?._error_message || 'Invalid Request'
    } catch {}
  }
  return e?.message || e?.exc || 'Invalid Request'
}

function goHome(profile){
  const payload = profile || { username: inForm.value.username }
  localStorage.setItem('ml_profile', JSON.stringify({ ...payload, language: lang.value }))
  window.location.href = '/math-leaders-games/#/home'
}

/* ===================== إرسال النماذج ===================== */
async function submit(){
  submitting.value = true
  notice.value = null
  try{
    if (showSignup.value){
      if(!upForm.value.username || !upForm.value.password || !upForm.value.confirm){
        throw {message: lang.value==='ar'?'الرجاء ملء كل الحقول.':'Please fill all fields.'}
      }
      if(upForm.value.password !== upForm.value.confirm){
        throw {message: lang.value==='ar'?'كلمتا المرور غير متطابقتين.':'Passwords do not match.'}
      }

      // إنشاء لاعب جديد داخل Game Users فقط (GET لتفادي CSRF)
      const res = await get('/api/method/mathematics_leaders.api.signup_and_login.signup_user', {
        username: upForm.value.username,
        password: upForm.value.password,
        language: lang.value
      })
      goHome(res?.message?.profile || { username: inForm.value.username })

      inForm.value.username = upForm.value.username
      inForm.value.password = ''
      showSignup.value = false
      notice.value = lang.value==='ar'
        ? 'تم إنشاء الحساب. ادخل بياناتك لتسجيل الدخول.'
        : 'Account created. Please log in.'
    } else {
      // تحقق الدخول على Game Users فقط (بدون جلسة فرابي)
      const loginRes = await get('/api/method/mathematics_leaders.api.signup_and_login.verify_login', {
        username: inForm.value.username,
        password: inForm.value.password
      })

      // نجاح — الانتقال للواجهة
      // window.location.href = '/math-leaders-games/#/'
      goHome(loginRes?.message?.profile || { username: upForm.value.username })
      // goHome(res?.message?.profile || { username: inForm.value.username })

    }
  } catch (err){
    notice.value = extractErr(err)
  } finally {
    submitting.value = false
  }
}
</script> -->
<script setup>
import { ref, computed, watch, onMounted } from 'vue'

/* ===================== اللغة ===================== */
const lang = ref(localStorage.getItem('ml_lang') || 'ar')
const dir  = computed(() => (lang.value === 'ar' ? 'rtl' : 'ltr'))
const t = (k)=>({
  en:{signin:'Sign In',signup:'Create Account',username:'Username',password:'Password',confirm:'Confirm Password',
      login:'Login',register:'Signup',toSignup:'Create account',toSignin:'Back to login',forgot:'Forgot password?'},
  ar:{signin:'تسجيل الدخول',signup:'إنشاء حساب',username:'اسم المستخدم',password:'كلمة المرور',confirm:'تأكيد كلمة المرور',
      login:'دخول',register:'تسجيل',toSignup:'إنشاء حساب',toSignin:'العودة لتسجيل الدخول',forgot:'نسيت كلمة المرور؟'}
}[lang.value][k])

function toggleLang(){ lang.value = lang.value==='ar' ? 'en' : 'ar' }
watch(lang, v => {
  localStorage.setItem('ml_lang', v)
  document.documentElement.dir = dir.value
  document.documentElement.lang = v
})
onMounted(() => {
  document.documentElement.dir  = dir.value
  document.documentElement.lang = lang.value
})

/* ===================== حالة الواجهة ===================== */
const showSignup  = ref(false)
const inForm      = ref({ username:'', password:'' })
const upForm      = ref({ username:'', password:'', confirm:'' })
const submitting  = ref(false)
const notice      = ref(null)

/* ===================== صور الخلفية والأوراق ===================== */
const bgUrl    = new URL('../assets/images/bg.jpg',    import.meta.url).href
const girlUrl  = new URL('../assets/images/girl.png',  import.meta.url).href
const treesUrl = new URL('../assets/images/trees.png', import.meta.url).href
const leaf01   = new URL('../assets/images/leaf_1.png',  import.meta.url).href
const leaf02   = new URL('../assets/images/leaf_2.png',  import.meta.url).href
const leaf03   = new URL('../assets/images/leaf_3.png',  import.meta.url).href
const leaf04   = new URL('../assets/images/leaf_4.png',  import.meta.url).href
const leaf01_  = new URL('../assets/images/leaf_1_.png', import.meta.url).href
const leaf02_  = new URL('../assets/images/leaf_2_.png', import.meta.url).href
const leaf03_  = new URL('../assets/images/leaf_3_.png', import.meta.url).href
const leaf04_  = new URL('../assets/images/leaf_4_.png', import.meta.url).href
const leafImgs = [leaf01, leaf02, leaf03, leaf04, leaf01_, leaf02_, leaf03_, leaf04_]

/* ===================== أدوات HTTP ===================== */
/* استخدم نفس الأصل. ترك BASE فارغًا يعني استعمال المسارات النسبية */
const BASE = ''  // أو: const BASE = window.location.origin

async function get(url, params = {}) {
  const qs = new URLSearchParams(params).toString()
  const r  = await fetch(BASE + url + (qs ? `?${qs}` : ''), {
    method: 'GET',
    credentials: 'include',
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw data
  return data
}

function extractErr(e){
  if (typeof e === 'string') return e
  if (e?._server_messages){
    try {
      const list  = JSON.parse(e._server_messages)
      const first = list?.[0] && JSON.parse(list[0])
      return first?.message || first?._error_message || 'Invalid Request'
    } catch {}
  }
  return e?.message || e?.exc || 'Invalid Request'
}

function goHome(profile){
  const payload = profile || { username: inForm.value.username }
  localStorage.setItem('ml_profile', JSON.stringify({ ...payload, language: lang.value }))
  window.location.href = '/math-leaders-games/#/home'
}

/* ===================== إرسال النماذج ===================== */
async function submit(){
  submitting.value = true
  notice.value = null
  try{
    if (showSignup.value){
      if(!upForm.value.username || !upForm.value.password || !upForm.value.confirm){
        throw {message: lang.value==='ar'?'الرجاء ملء كل الحقول.':'Please fill all fields.'}
      }
      if(upForm.value.password !== upForm.value.confirm){
        throw {message: lang.value==='ar'?'كلمتا المرور غير متطابقتين.':'Passwords do not match.'}
      }

      // 1) إنشاء حساب (User + Game Users)
      await get('/api/method/mathematics_leaders.api.signup_and_login.signup_user', {
        username: upForm.value.username,
        password: upForm.value.password,
        language: lang.value
      })

      // 2) تسجيل الدخول لإنشاء جلسة نظام (sid) – لاحظ usr/pwd
      const loginRes = await get('/api/method/mathematics_leaders.api.signup_and_login.verify_login', {
        usr: upForm.value.username,
        pwd: upForm.value.password
      })

      goHome(loginRes?.message?.profile || { username: upForm.value.username })
    } else {
      // تسجيل الدخول بجلسة نظام
      const loginRes = await get('/api/method/mathematics_leaders.api.signup_and_login.verify_login', {
        usr: inForm.value.username,
        pwd: inForm.value.password
      })
      goHome(loginRes?.message?.profile || { username: inForm.value.username })
    }
  } catch (err){
    notice.value = extractErr(err)
  } finally {
    submitting.value = false
  }
}
</script>



<template>
  <section :dir="dir">
    <!-- زر تغيير اللغة (ورقة SVG) -->
    <button class="lang-leaf" :aria-label="lang==='ar'?'Switch to English':'التبديل للعربية'" @click="toggleLang">
      <svg viewBox="0 0 200 200" class="leaf-svg" aria-hidden="true">
        <defs>
          <linearGradient id="mlgLeafGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#ff7a59"/><stop offset="70%" stop-color="#d64c42"/><stop offset="100%" stop-color="#8f2c24"/>
          </linearGradient>
        </defs>
        <path d="M100 10 C150 20,185 60,175 105 C165 150,120 185,75 185 C40 185,15 150,25 115 C35 80,60 60,100 10 Z" fill="url(#mlgLeafGrad)"/>
        <path d="M100 25 L85 165" stroke="rgba(255,255,255,.75)" stroke-width="6" stroke-linecap="round"/>
      </svg>
      <span class="leaf-label">{{ lang==='ar'?'EN':'ع' }}</span>
    </button>

    <!-- أوراق متساقطة -->
    <div class="leaves">
      <div class="set">
        <div class="leaf" v-for="(src,i) in leafImgs" :key="i">
          <img :src="src" alt="" />
        </div>
      </div>
    </div>

    <!-- الخلفيات -->
    <img :src="bgUrl"    class="bg"    alt="" />
    <img :src="girlUrl"  class="girl"  alt="" />
    <img :src="treesUrl" class="trees" alt="" />

    <!-- البطاقة -->
    <div class="auth-wrapper" :class="{'animate-signIn': showSignup, 'animate-signUp': !showSignup}">
      <!-- Signup -->
      <div class="form-panel sign-up">
        <form @submit.prevent="submit">
          <h2>{{ t('signup') }}</h2>
          <div class="inputBox"><input v-model="upForm.username" type="text"     :placeholder="t('username')" /></div>
          <div class="inputBox"><input v-model="upForm.password" type="password" :placeholder="t('password')" /></div>
          <div class="inputBox"><input v-model="upForm.confirm"  type="password" :placeholder="t('confirm')" /></div>
          <div class="inputBox"><input :disabled="submitting" id="btn" type="submit" :value="t('register')" /></div>
          <div class="group"><a href="#" @click.prevent="showSignup=false">{{ t('toSignin') }}</a></div>
          <p v-if="notice" class="note">{{ notice }}</p>
        </form>
      </div>

      <!-- Login -->
      <div class="form-panel sign-in">
        <form @submit.prevent="submit">
          <h2>{{ t('signin') }}</h2>
          <div class="inputBox"><input v-model="inForm.username" type="text"     :placeholder="t('username')" /></div>
          <div class="inputBox"><input v-model="inForm.password" type="password" :placeholder="t('password')" /></div>
          <div class="forgot"><a href="#">{{ t('forgot') }}</a></div>
          <div class="inputBox"><input :disabled="submitting" id="btn" type="submit" :value="t('login')" /></div>
          <div class="group"><a href="#" @click.prevent="showSignup=true">{{ t('toSignup') }}</a></div>
          <p v-if="notice" class="note">{{ notice }}</p>
        </form>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* المشهد */
/* position:relative; */
section{display:flex;justify-content:center;align-items:center;width:100%;height:100vh;overflow:hidden;background:#fff;}
.bg,.trees{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;pointer-events:none;}
.trees{z-index:100}
.girl{position:absolute;scale:.65;pointer-events:none;animation:animateGirl 10s linear infinite;}
@keyframes animateGirl{0%{transform:translateX(calc(100% + 100vw));}
50%{transform:translateX(calc(-100% - 100vw));}
50.01%{transform:translateX(calc(-100% - 100vw)) rotateY(180deg);}
100%{transform:translateX(calc(100% + 100vw)) rotateY(180deg);}}

/* زر اللغة */
.lang-leaf{position:absolute;top:14px;right:14px;z-index:220;width:64px;height:64px;padding:0;border:none;background:transparent;cursor:pointer}
.lang-leaf .leaf-svg{width:100%;height:100%;filter:drop-shadow(0 8px 14px rgba(0,0,0,.25))}
.lang-leaf .leaf-label{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px;color:#fff;text-shadow:0 2px 4px rgba(0,0,0,.35)}

/* أوراق */
.leaves{position:absolute;inset:0;overflow:hidden;display:flex;justify-content:center;align-items:center;z-index:1;pointer-events:none}
.leaves .set{position:absolute;inset:0;pointer-events:none}
.leaf{position:absolute;display:block}
.leaf:nth-child(1){left:20%;animation:leafAnim 20s linear infinite}
.leaf:nth-child(2){left:50%;animation:leafAnim 14s linear infinite}
.leaf:nth-child(3){left:70%;animation:leafAnim 12s linear infinite}
.leaf:nth-child(4){left:5%; animation:leafAnim 15s linear infinite}
.leaf:nth-child(5){left:85%;animation:leafAnim 18s linear infinite}
.leaf:nth-child(6){left:90%;animation:leafAnim 12s linear infinite}
.leaf:nth-child(7){left:15%;animation:leafAnim 14s linear infinite}
.leaf:nth-child(8){left:60%;animation:leafAnim 15s linear infinite}
@keyframes leafAnim{
  0%{opacity:0;top:-10%;transform:translateX(20px) rotate(0deg)}
  10%{opacity:1}
  20%{transform:translateX(-20px) rotate(45deg)}
  40%{transform:translateX(-20px) rotate(90deg)}
  60%{transform:translateX(20px) rotate(180deg)}
  80%{transform:translateX(-20px) rotate(45deg)}
  100%{top:110%;transform:translateX(20px) rotate(225deg)}
}
.leaf img{display:block;filter:drop-shadow(0 3px 6px rgba(0,0,0,.25))}

/* البطاقة */
.auth-wrapper{position:relative;--panel-w:520px;width:var(--panel-w);height:560px;z-index:150;--content-w:96%}
.form-panel{position:absolute;inset:0;display:flex;justify-content:center;align-items:center;background:linear-gradient(180deg,rgba(255,255,255,.28),rgba(255,255,255,.18));backdrop-filter:blur(15px);border:1px solid rgba(255,255,255,.7);border-radius:20px;box-shadow:0 25px 50px rgba(0,0,0,.12)}
.form-panel h2{margin-bottom:10px;font-size:1.9rem;font-weight:700;color:#8f2c24;text-align:center}
.inputBox{position:relative;width:var(--content-w);margin:10px auto}
.inputBox input{width:100%;padding:14px 16px;border-radius:12px;border:none;background:#fff;color:#8f2c24;outline:none;box-shadow:0 0 0 1px rgba(0,0,0,.06) inset;font-size:1rem}
#btn{background:#8f2c24;color:#fff;cursor:pointer;font-size:1.05rem;font-weight:700;transition:.2s;border-radius:12px}
#btn:hover{background:#d64c42}
.group{width:var(--content-w);margin:6px auto 0;display:flex;justify-content:space-between}
.group a{color:#8f2c24;font-weight:600;text-decoration:none}
.group a:last-child{text-decoration:underline}
.forgot{width:var(--content-w);margin:2px auto 6px;text-align:end}
.note{text-align:center;color:#8f2c24;font-weight:600;margin-top:6px}

/* أنيميشن التبديل */
.auth-wrapper.animate-signUp .form-panel.sign-in{transform:rotate(7deg);animation:animRotate .7s ease-in-out forwards;animation-delay:.3s}
.auth-wrapper.animate-signIn .form-panel.sign-in{animation:animSignIn 1.5s ease-in-out forwards}
@keyframes animSignIn{0%{transform:translateX(0)}50%{transform:translateX(calc(var(--panel-w) * -1))}100%{transform:translateX(0) rotate(7deg)}}
.form-panel.sign-up{transform:rotate(7deg)}
.auth-wrapper.animate-signIn .form-panel.sign-up{animation:animRotate .7s ease-in-out forwards;animation-delay:.3s}
@keyframes animRotate{0%{transform:rotate(7deg)}100%{transform:rotate(0);z-index:1}}
.auth-wrapper.animate-signUp .form-panel.sign-up{animation:animSignUp 1.5s ease-in-out forwards}
@keyframes animSignUp{0%{transform:translateX(0);z-index:1}50%{transform:translateX(var(--panel-w))}100%{transform:translateX(0) rotate(7deg)}}
@media(max-width:720px){.auth-wrapper{width:92vw;--panel-w:92vw;height:560px}}
</style>

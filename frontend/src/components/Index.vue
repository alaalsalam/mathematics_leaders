<script setup>
import { ref, computed, watch, onMounted } from 'vue'

/* استيراد الصور حتى يبنيها Vite ويولّد لها مسارات صحيحة */
import leaf01 from '@/assets/images/leaf_1.png'
import leaf02 from '@/assets/images/leaf_2.png'
import leaf03 from '@/assets/images/leaf_3.png'
import leaf04 from '@/assets/images/leaf_4.png'
import leaf01_ from '@/assets/images/leaf_1_.png'
import leaf02_ from '@/assets/images/leaf_2_.png'
import leaf03_ from '@/assets/images/leaf_3_.png'
import leaf04_ from '@/assets/images/leaf_4_.png'
import bgImg   from '@/assets/images/bg.jpg'
import girlImg from '@/assets/images/girl.png'
import treesImg from '@/assets/images/trees.png'

/* مصفوفة الأوراق (تتكرر 8 عناصر مثل قبل) */
const leafImgs = [leaf01, leaf02, leaf03, leaf04, leaf01_, leaf02_, leaf03_, leaf04_]

/* اللغة */
const lang = ref(localStorage.getItem('ml_lang') || 'ar')
const dir  = computed(() => (lang.value === 'ar' ? 'rtl' : 'ltr'))
const dict = {
  en:{signin:'Sign In',signup:'Create Account',username:'Username',name:'Full name',email:'Email',password:'Password',confirm:'Confirm password',login:'Login',register:'Signup',forgot:'Forget Password',toSignup:'Signup',toSignin:'Back to login',langShort:'EN'},
  ar:{signin:'تسجيل الدخول',signup:'إنشاء حساب',username:'اسم المستخدم',name:'الاسم الكامل',email:'البريد الإلكتروني',password:'كلمة المرور',confirm:'تأكيد كلمة المرور',login:'دخول',register:'تسجيل',forgot:'نسيت كلمة المرور',toSignup:'إنشاء حساب',toSignin:'العودة لتسجيل الدخول',langShort:'ع'}
}
const t = (k)=>dict[lang.value][k]
function toggleLang(){ lang.value = lang.value==='ar'?'en':'ar' }
watch(lang,v=>{
  localStorage.setItem('ml_lang',v)
  document.documentElement.setAttribute('dir',dir.value)
  document.documentElement.setAttribute('lang',v)
})
onMounted(()=>{
  document.documentElement.setAttribute('dir',dir.value)
  document.documentElement.setAttribute('lang',lang.value)
})

/* تبديل النماذج + أنيميشن */
const showSignup   = ref(false)
const wrapperClass = computed(()=>({
  'auth-wrapper': true,
  'animate-signIn': showSignup.value,
  'animate-signUp': !showSignup.value,
}))

/* نماذج */
const inForm = ref({ username:'', password:'' })
const upForm = ref({ username:'', name:'', email:'', password:'', confirm:'' })
const submitting = ref(false)
async function submit(){
  submitting.value = true
  try{
    if(showSignup.value){
      // TODO: signup API
    }else{
      // TODO: login API
    }
  }finally{ submitting.value = false }
}
</script>

<template>
  <section :dir="dir">
    <!-- زر اللغة (ورقة شجر SVG) -->
    <button class="lang-leaf" :aria-label="lang==='ar'?'Switch to English':'التبديل للعربية'" @click="toggleLang">
      <svg viewBox="0 0 200 200" class="leaf-svg" aria-hidden="true">
        <defs>
          <linearGradient id="mlgLeafGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#ff7a59"/><stop offset="70%" stop-color="#d64c42"/><stop offset="100%" stop-color="#8f2c24"/>
          </linearGradient>
          <radialGradient id="mlgLeafShine" cx="30%" cy="25%" r="60%">
            <stop offset="0%" stop-color="rgba(255,255,255,.55)"/><stop offset="100%" stop-color="rgba(255,255,255,0)"/>
          </radialGradient>
        </defs>
        <path d="M100 10 C150 20, 185 60, 175 105 C165 150, 120 185, 75 185 C40 185, 15 150, 25 115 C35 80, 60 60, 100 10 Z" fill="url(#mlgLeafGrad)"/>
        <path d="M100 25 L85 165" stroke="rgba(255,255,255,.75)" stroke-width="6" stroke-linecap="round"/>
        <path d="M92 70 L70 90 M95 95 L75 115 M98 120 L78 140" stroke="rgba(255,255,255,.55)" stroke-width="5" stroke-linecap="round"/>
        <ellipse cx="70" cy="45" rx="38" ry="22" fill="url(#mlgLeafShine)"/>
      </svg>
      <span class="leaf-label">{{ lang==='ar'?'EN':'AR' }}</span>
    </button>

    <!-- أوراق الشجر المتساقطة (الصور الآن مربوطة بالاستيراد) -->
    <div class="leaves">
      <div class="set">
        <div class="leaf" v-for="(src,i) in leafImgs" :key="i">
          <img :src="src" alt="" />
        </div>
      </div>
    </div>

    <!-- الخلفيات (مربوطة بالاستيراد لضمان عدم 404) -->
    <img :src="bgImg"    class="bg"    alt="" />
    <img :src="girlImg"  class="girl"  alt="" />
    <img :src="treesImg" class="trees" alt="" />

    <!-- البوكس أصغر + الحقول بعرض شبه كامل للبوكس -->
    <div :class="wrapperClass">
      <!-- Sign up -->
      <div class="form-panel sign-up">
        <form @submit.prevent="submit">
          <h2>{{ t('signup') }}</h2>
          <div class="inputBox"><input v-model="upForm.username" type="text"     :placeholder="t('username')" /></div>
          <div class="inputBox"><input v-model="upForm.name"     type="text"     :placeholder="t('name')" /></div>
          <div class="inputBox"><input v-model="upForm.email"    type="email"    :placeholder="t('email')" /></div>
          <div class="inputBox"><input v-model="upForm.password" type="password" :placeholder="t('password')" /></div>
          <div class="inputBox"><input v-model="upForm.confirm"  type="password" :placeholder="t('confirm')" /></div>
          <div class="inputBox"><input :disabled="submitting" id="btn" type="submit" :value="t('register')" /></div>
          <div class="group"><a href="#" @click.prevent="showSignup=false">{{ t('toSignin') }}</a></div>
        </form>
      </div>

      <!-- Sign in -->
      <div class="form-panel sign-in">
        <form @submit.prevent="submit">
          <h2>{{ t('signin') }}</h2>
          <div class="inputBox"><input v-model="inForm.username" type="text"     :placeholder="t('username')" /></div>
          <div class="inputBox"><input v-model="inForm.password" type="password" :placeholder="t('password')" /></div>
          <div class="forgot"><a href="#">{{ t('forgot') }}</a></div>
          <div class="inputBox"><input :disabled="submitting" id="btn" type="submit" :value="t('login')" /></div>
          <div class="group"><a href="#" @click.prevent="showSignup=true">{{ t('toSignup') }}</a></div>
        </form>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* المشهد */
section{position:relative;display:flex;justify-content:center;align-items:center;width:100%;height:100vh;overflow:hidden;background:#fff;}
.bg,.trees{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;pointer-events:none;}
.trees{z-index:100}
.girl{position:absolute;scale:.65;pointer-events:none;animation:animateGirl 10s linear infinite;}
@keyframes animateGirl{
  0%{transform:translateX(calc(100% + 100vw));}
  50%{transform:translateX(calc(-100% - 100vw));}
  50.01%{transform:translateX(calc(-100% - 100vw)) rotateY(180deg);}
  100%{transform:translateX(calc(100% + 100vw)) rotateY(180deg);}
}

/* زر اللغة (ورقة) */
.lang-leaf{position:absolute;top:14px;right:14px;z-index:220;width:64px;height:64px;padding:0;border:none;background:transparent;cursor:pointer;}
.lang-leaf .leaf-svg{width:100%;height:100%;filter:drop-shadow(0 8px 14px rgba(0,0,0,.25));transform-origin:50% 60%;animation:leafSway 3.6s ease-in-out infinite;transition:transform .2s, filter .2s;}
.lang-leaf:hover .leaf-svg{transform:scale(1.06) rotate(1deg);filter:drop-shadow(0 10px 18px rgba(0,0,0,.32));}
@keyframes leafSway{0%{transform:rotate(-4deg)}50%{transform:rotate(4deg)}100%{transform:rotate(-4deg)}}
.lang-leaf .leaf-label{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px;color:#fff;text-shadow:0 2px 4px rgba(0,0,0,.35);pointer-events:none;}

/* أوراق متساقطة */
.leaves{position:absolute;inset:0;overflow:hidden;display:flex;justify-content:center;align-items:center;z-index:1;pointer-events:none;}
.leaves .set{position:absolute;inset:0;pointer-events:none;}
.leaf{position:absolute;display:block;}
.leaf:nth-child(1){left:20%;animation:leafAnim 20s linear infinite;}
.leaf:nth-child(2){left:50%;animation:leafAnim 14s linear infinite;}
.leaf:nth-child(3){left:70%;animation:leafAnim 12s linear infinite;}
.leaf:nth-child(4){left:5%; animation:leafAnim 15s linear infinite;}
.leaf:nth-child(5){left:85%;animation:leafAnim 18s linear infinite;}
.leaf:nth-child(6){left:90%;animation:leafAnim 12s linear infinite;}
.leaf:nth-child(7){left:15%;animation:leafAnim 14s linear infinite;}
.leaf:nth-child(8){left:60%;animation:leafAnim 15s linear infinite;}
@keyframes leafAnim{
  0%{opacity:0;top:-10%;transform:translateX(20px) rotate(0deg);}
  10%{opacity:1;}
  20%{transform:translateX(-20px) rotate(45deg);}
  40%{transform:translateX(-20px) rotate(90deg);}
  60%{transform:translateX(20px) rotate(180deg);}
  80%{transform:translateX(-20px) rotate(45deg);}
  100%{top:110%;transform:translateX(20px) rotate(225deg);}
}
.leaf img{display:block;filter:drop-shadow(0 3px 6px rgba(0,0,0,.25))}

/* البوكس أصغر والحقول بعرض شبه كامل */
.auth-wrapper{
  position:relative;
  --panel-w: 520px;       /* عرض البوكس */
  width: var(--panel-w);
  height: 560px;
  z-index:150;
  --content-w: 96%;       /* عرض الحقول بالنسبة للبوكس */
}
.form-panel{
  position:absolute; inset:0; display:flex; justify-content:center; align-items:center;
  background:linear-gradient(180deg, rgba(255,255,255,.28), rgba(255,255,255,.18));
  backdrop-filter: blur(15px);
  border:1px solid rgba(255,255,255,.7); border-radius:20px;
  box-shadow:0 25px 50px rgba(0,0,0,.12);
}
.form-panel h2{margin-bottom:10px;font-size:1.9rem;font-weight:700;color:#8f2c24;text-align:center}
.inputBox{position:relative; width: var(--content-w); margin: 10px auto;}
.inputBox input{
  width:100%; padding: 14px 16px; border-radius:12px; border:none; background:#fff; color:#8f2c24;
  outline:none; box-shadow:0 0 0 1px rgba(0,0,0,.06) inset; font-size:1rem;
}
.inputBox input::placeholder{color:#8f2c24;opacity:.7}
#btn{background:#8f2c24;color:#fff;cursor:pointer;font-size:1.05rem;font-weight:700;transition:.2s;border-radius:12px}
#btn:hover{background:#d64c42}
.group{width: var(--content-w); margin: 6px auto 0; display:flex; justify-content:space-between}
.group a{color:#8f2c24;font-weight:600;text-decoration:none}
.group a:last-child{text-decoration:underline}
.forgot{width: var(--content-w); margin: 2px auto 6px; text-align:end}

/* حركات التبديل */
.auth-wrapper.animate-signUp .form-panel.sign-in{transform:rotate(7deg);animation:animRotate .7s ease-in-out forwards;animation-delay:.3s}
.auth-wrapper.animate-signIn .form-panel.sign-in{animation:animSignIn 1.5s ease-in-out forwards}
@keyframes animSignIn{0%{transform:translateX(0)}50%{transform:translateX(calc(var(--panel-w) * -1))}100%{transform:translateX(0) rotate(7deg)}}
.form-panel.sign-up{transform:rotate(7deg)}
.auth-wrapper.animate-signIn .form-panel.sign-up{animation:animRotate .7s ease-in-out forwards;animation-delay:.3s}
@keyframes animRotate{0%{transform:rotate(7deg)}100%{transform:rotate(0);z-index:1}}
.auth-wrapper.animate-signUp .form-panel.sign-up{animation:animSignUp 1.5s ease-in-out forwards}
@keyframes animSignUp{0%{transform:translateX(0);z-index:1}50%{transform:translateX(var(--panel-w))}100%{transform:translateX(0) rotate(7deg)}}

/* تجاوبية */
@media (max-width: 720px){
  .auth-wrapper{ width: 92vw; --panel-w: 92vw; height: 560px }
}
</style>

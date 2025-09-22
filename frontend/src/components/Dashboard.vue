<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
/* أيقونات lucide */
import {
  Target, Trophy, Settings, LogOut, ChevronDown, Globe, Sun, Moon,
  Hand, UserCircle2, ChevronLeft, Menu
} from 'lucide-vue-next'
import Challenge1 from '@/pages/challenges/challenge_1.vue'   // غيّر المسار حسب بنية مشروعك
import Challenge2 from '@/pages/challenges/challenge_2.vue'
import Challenge3 from '@/pages/challenges/challenge_3.vue'
import Challenge4 from '@/pages/challenges/challenge_4.vue'
import Challenge5 from '@/pages/challenges/challenge_5.vue'
import Challenge6 from '@/pages/challenges/challenge_6.vue'
import Challenge7 from '@/pages/challenges/challenge_7.vue'
import challenge_level_two_1 from '@/pages/challenges/challenge_level_two_1.vue'
import challenge_level_two_2 from '@/pages/challenges/challenge_level_two_2.vue'
import challenge_level_two_3 from '@/pages/challenges/challenge_level_two_3.vue'
import challenge_level_two_4 from '@/pages/challenges/challenge_level_two_4.vue'
import challenge_level_two_5 from '@/pages/challenges/challenge_level_two_5.vue'
import challenge_level_two_6 from '@/pages/challenges/challenge_level_two_6.vue'
import challenge_level_two_7 from '@/pages/challenges/challenge_level_two_7.vue'
import challenge_level_two_8 from '@/pages/challenges/challenge_level_two_8.vue'
import challenge_level_two_9 from '@/pages/challenges/challenge_level_two_9.vue'
const router = useRouter()

/* ================= اللغة ================= */
const lang = ref(localStorage.getItem('ml_lang') || 'ar')
const dir  = computed(() => (lang.value === 'ar' ? 'rtl' : 'ltr'))
const T = {
  ar: {
    challenges:'المستوى الأول', challenges2:'المستوى الثاني', myScores:'درجاتي', settings:'الإعدادات', logout:'خروج',
    hello:'مرحبًا', sub:'اختر تحديًا وابدأ اللعب!', challenge:'التحدي',
    brand:'زعماء الرياضيات'
  },
  en: {
    challenges:'Level One', challenges2:'Level Two', myScores:'My Scores', settings:'Settings', logout:'Log out',
    hello:'Hello', sub:'Pick a challenge and start!', challenge:'Challenge',
    brand:'Math Leaders'
  }
}
const t = (k)=>T[lang.value][k]
watch(lang, v=>{
  localStorage.setItem('ml_lang', v)
  document.documentElement.dir = dir.value
  document.documentElement.lang = v
})

/* ================= الثيم ================= */
const theme = ref(localStorage.getItem('ml_theme') || 'light')
watch(theme, v=>{
  localStorage.setItem('ml_theme', v)
})

/* ================= GET helper ================= */
async function get(url, params = {}) {
  const qs = new URLSearchParams(params).toString()
  const r  = await fetch(url + (qs ? `?${qs}` : ''), {
    method: 'GET',
    credentials: 'include',
  })
  const data = await r.json().catch(()=> ({}))
  if (!r.ok) throw data
  return data
}

/* ================= المستخدم/الحماية ================= */
const username = ref('player')
const fullName = ref('')

async function fetchMe(){
  try {
    const data = await get('/api/method/mathematics_leaders.api.get_my_details.get_me')
    const msg  = data?.message
    if (!msg?.ok) { router.replace('/'); return }
    const prof = msg.profile || {}
    username.value = prof.username || 'player'
    fullName.value = prof.full_name || ''
    if (prof.language && !localStorage.getItem('ml_lang')) lang.value = prof.language
  } catch {
    router.replace('/')
  }
}

/* ================= تنقّل وقائمة ================= */
const openChallenges   = ref(true)
const profileOpen      = ref(false)
const sidebarCollapsed = ref(false)

function toggleSidebar(){
  sidebarCollapsed.value = !sidebarCollapsed.value
}
// function gotoChallenge(i){ router.push(`/challenge/${i}`) }
function goto(path){ router.push(path) }
async function logout(){
  await get('/api/method/logout')
  router.replace('/')
}

/* ================= تهيئة ================= */
onMounted(()=>{
  document.documentElement.dir  = dir.value
  document.documentElement.lang = lang.value
  fetchMe()
})


const activeView = ref('none') // 'none' أو 'challenge1'

function gotoChallenge(i) {
  // بدل الراوت، اعرض الصفحة داخل المحتوى
  // activeView.value = (i === 1) ? 'challenge1' : 'none'
  activeView.value = i === 1 ? 'challenge1'
                   : i === 2 ? 'challenge2'
                   : i === 3 ? 'challenge3'
                   : i === 4 ? 'challenge4'
                   : i === 5 ? 'challenge5'
                   : i === 6 ? 'challenge6'
                   : i === 7 ? 'challenge7'
                   : 'none'

}

const activeView2 = ref('none') // 'none' أو 'challenge1'

function gotoChallenge2(i) {
  // بدل الراوت، اعرض الصفحة داخل المحتوى
  // activeView.value = (i === 1) ? 'challenge1' : 'none'
  activeView2.value = i === 1 ? 'challenge_level_two_1'
                   : i === 2 ? 'challenge_level_two_2'
                   : i === 3 ? 'challenge_level_two_3'
                   : i === 4 ? 'challenge_level_two_4'
                   : i === 5 ? 'challenge_level_two_5'
                   : i === 6 ? 'challenge_level_two_6'
                   : i === 7 ? 'challenge_level_two_7'
                   : i === 8 ? 'challenge_level_two_8'
                    : i === 9 ? 'challenge_level_two_9'
                   : 'none'

}

/* شعار */
const logoUrl = new URL('../assets/images/logo3.jpeg', import.meta.url).href
</script>

<template>
  <!-- أربط الثيم هنا ليُفعّل متغيرات CSS -->
  <div class="shell" :dir="dir" :data-theme="theme">
    
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="brand" :title="t('brand')">
        <img class="logo" :src="logoUrl" alt="ML logo" />
        <span class="brand-name" v-show="!sidebarCollapsed">{{ t('brand') }}</span>
      </div>

      <nav class="menu">
        <div class="menu-group">
          <button class="menu-item" @click="openChallenges=!openChallenges" :disabled="sidebarCollapsed">
            <Target class="mi" />
            <span class="mt" v-show="!sidebarCollapsed">{{ t('challenges') }}</span>
            <ChevronDown class="chev" :class="{rot: openChallenges}" v-show="!sidebarCollapsed" />
          </button>
          <transition name="fade">
            <ul v-if="openChallenges && !sidebarCollapsed" class="submenu">
              <li v-for="i in 7" :key="i">
                <a href="javascript:;" @click="gotoChallenge(i)">
                  {{ t('challenge') }} {{ i }}
                </a>
              </li>
            </ul>
          </transition>
          <!-- <button class="menu-item" @click="openChallenges=!openChallenges" :disabled="sidebarCollapsed">
            <Target class="mi" />
            <span class="mt" v-show="!sidebarCollapsed">{{ t('challenges2') }}</span>
            <ChevronDown class="chev" :class="{rot: openChallenges}" v-show="!sidebarCollapsed" />
          </button>
          <transition name="fade">
            <ul v-if="openChallenges && !sidebarCollapsed" class="submenu">
              <li v-for="i = 8 in 16" :key="i">
                <a href="javascript:;" @click="gotoChallenge(i)">
                  {{ t('challenge') }} {{ i - 7 }}
                </a>
              </li>
            </ul>
          </transition> -->
        </div>

        <button class="menu-item" @click="goto('/scores')" :title="t('myScores')">
          <Trophy class="mi" />
          <span class="mt" v-show="!sidebarCollapsed">{{ t('myScores') }}</span>
        </button>

        <button class="menu-item" @click="goto('/settings')" :title="t('settings')">
          <Settings class="mi" />
          <span class="mt" v-show="!sidebarCollapsed">{{ t('settings') }}</span>
        </button>

        <button class="menu-item danger" @click="logout" :title="t('logout')">
          <LogOut class="mi" />
          <span class="mt" v-show="!sidebarCollapsed">{{ t('logout') }}</span>
        </button>
      </nav>
    </aside>

    <!-- Main -->
    <main class="main">
      <header class="topbar">
        <div class="left">
          <button class="pill ghost toggle" @click="toggleSidebar" :aria-label="sidebarCollapsed ? 'Open sidebar' : 'Collapse sidebar'">
            <Menu v-if="sidebarCollapsed" />
            <ChevronLeft v-else :style="{ transform: dir==='rtl' ? 'scaleX(-1)' : '' }" />
          </button>

          <div class="welcome">
            <Hand class="wave" />
            <strong>{{ T[lang].hello }} {{ fullName || username }}</strong>
            <small>— {{ t('sub') }}</small>
          </div>
        </div>

        <div class="right">
          <button class="pill ghost" title="Language" @click="lang = (lang==='ar'?'en':'ar')">
            <Globe style="margin-inline-end:6px" /> {{ lang==='ar' ? 'EN' : 'ع' }}
          </button>
          <button class="pill ghost" title="Theme" @click="theme = (theme==='light'?'dark':'light')">
            <Sun v-if="theme==='light'" /> <Moon v-else />
          </button>

          <div class="avatar" @click="profileOpen=!profileOpen">
            <UserCircle2 class="avatar-ico" />
            <span class="name">{{ fullName || username }}</span>
            <ChevronDown class="chev" :class="{rot: profileOpen}" />

            <transition name="fade">
              <ul v-if="profileOpen" class="dropdown">
                <li><a href="javascript:;" @click="goto('/settings')"><Settings /> <span> {{ T[lang].settings }}</span></a></li>
                <li><a href="javascript:;" class="danger" @click="logout"><LogOut /> <span> {{ T[lang].logout }}</span></a></li>
              </ul>
            </transition>
          </div>
        </div>
      </header>

      <section class="content">
  <Challenge1
    v-if="activeView==='challenge1'"
    :lang="lang"
    :dir="dir"
    :theme="theme"
  />
  <Challenge2
    v-else-if="activeView==='challenge2'"
    :lang="lang"
    :dir="dir"
    :theme="theme"
  />
  <Challenge3
    v-else-if="activeView==='challenge3'"
    :lang="lang"
    :dir="dir"
    :theme="theme"
  />
  <Challenge4
    v-else-if="activeView==='challenge4'"
    :lang="lang"
    :dir="dir"
    :theme="theme"
  />
  <Challenge5
    v-else-if="activeView==='challenge5'"
    :lang="lang"
    :dir="dir"
    :theme="theme"
  />
  <Challenge6
    v-else-if="activeView==='challenge6'"
    :lang="lang"
    :dir="dir"
    :theme="theme"
  />
  <Challenge7
    v-else-if="activeView==='challenge7'"
    :lang="lang"
    :dir="dir"
    :theme="theme"
  />
  <challenge_level_two_1
    v-else-if="activeView2==='challenge_level_two_1'"
    :lang="lang"
    :dir="dir"
    :theme="theme"
  />
  <challenge_level_two_2
    v-else-if="activeView2==='challenge_level_two_2'"
    :lang="lang"
    :dir="dir"
    :theme="theme"
  />
  <challenge_level_two_3
    v-else-if="activeView2==='challenge_level_two_3'"
    :lang="lang"
    :dir="dir"
    :theme="theme"
  />
  <challenge_level_two_4
    v-else-if="activeView2==='challenge_level_two_4'"
    :lang="lang"
    :dir="dir"
    :theme="theme"
  />
  <challenge_level_two_5
    v-else-if="activeView2==='challenge_level_two_5'"
    :lang="lang"
    :dir="dir"
    :theme="theme"
  />
  <challenge_level_two_6
    v-else-if="activeView2==='challenge_level_two_6'"
    :lang="lang"
    :dir="dir"
    :theme="theme"
  />
  <challenge_level_two_7
    v-else-if="activeView2==='challenge_level_two_7'"
    :lang="lang"
    :dir="dir"
    :theme="theme"
  />
  <challenge_level_two_8
    v-else-if="activeView2==='challenge_level_two_8'"
    :lang="lang"
    :dir="dir"
    :theme="theme"
  />
  <challenge_level_two_9
    v-else-if="activeView2==='challenge_level_two_9'"
    :lang="lang"
    :dir="dir"
    :theme="theme"
  />
  
  <template v-else>
    <div class="cards"> المستوى الاول
      <div class="card" @click="gotoChallenge(1)">
        <h3>{{ T[lang].challenge }} 1</h3>
        <p>Numbers • Patterns • Fun</p>
      </div>
      <div class="card" @click="gotoChallenge(2)">
        <h3>{{ T[lang].challenge }} 2</h3>
        <p>Shapes • Logic • Puzzles</p>
      </div>
      <div class="card" @click="gotoChallenge(3)">
        <h3>{{ T[lang].challenge }} 3</h3>
        <p>Shapes • Logic • Puzzles</p>
      </div>
      <div class="card" @click="gotoChallenge(4)">
        <h3>{{ T[lang].challenge }} 4</h3>
        <p>Shapes • Logic • Puzzles</p>
      </div>
      <div class="card" @click="gotoChallenge(5)">
        <h3>{{ T[lang].challenge }} 5</h3>
        <p>Shapes • Logic • Puzzles</p>
      </div>
      <div class="card" @click="gotoChallenge(6)">
        <h3>{{ T[lang].challenge }} 6</h3>
        <p>Shapes • Logic • Puzzles</p>
      </div>
      <div class="card" @click="gotoChallenge(7)">
        <h3>{{ T[lang].challenge }} 7</h3>
        <p>Shapes • Logic • Puzzles</p>
      </div>
    </div>
    <div class="cards"> المستوى الثاني
      <div class="card" @click="gotoChallenge2(1)">
        <h3>{{ T[lang].challenge }} 1</h3>
        <p>Numbers • Patterns • Fun</p>
      </div>
      <div class="card" @click="gotoChallenge2(2)">
        <h3>{{ T[lang].challenge }} 2</h3>
        <p>Shapes • Logic • Puzzles</p>
      </div>
      <div class="card" @click="gotoChallenge2(3)">
        <h3>{{ T[lang].challenge }} 3</h3>
        <p>Shapes • Logic • Puzzles</p>
      </div>
      <div class="card" @click="gotoChallenge2(4)">
        <h3>{{ T[lang].challenge }} 4</h3>
        <p>Shapes • Logic • Puzzles</p>
      </div>
      <div class="card" @click="gotoChallenge2(5)">
        <h3>{{ T[lang].challenge }} 5</h3>
        <p>Shapes • Logic • Puzzles</p>
      </div>
      <div class="card" @click="gotoChallenge2(6)">
        <h3>{{ T[lang].challenge }} 6</h3>
        <p>Shapes • Logic • Puzzles</p>
      </div>
      <div class="card" @click="gotoChallenge2(7)">
        <h3>{{ T[lang].challenge }} 7</h3>
        <p>Shapes • Logic • Puzzles</p>
      </div>
      <div class="card" @click="gotoChallenge2(8)">
        <h3>{{ T[lang].challenge }} 2</h3>
        <p>Shapes • Logic • Puzzles</p>
      </div>
      <div class="card" @click="gotoChallenge2(9)">
        <h3>{{ T[lang].challenge }} 9</h3>
        <p>Shapes • Logic • Puzzles</p>
      </div>
    </div>
  </template>
</section>

    </main>
  </div>
</template>

<style scoped>
/* لوحة الألوان — تُطبَّق على .shell */
.shell{
  /* Light */
  --primary:#8f2c24;
  --accent:#d64c42;
  --peach:#ffe7db;
  --sand:#fff4e9;
  --ink:#2b1a1a;

  --bg:linear-gradient(180deg,#fffaf6,#fff4e9);
  --fg:var(--ink);
  --side-bg:rgba(255,255,255,.92);
  --bd:#f1d8cf;
  --hover:rgba(214,76,66,.08);
  --glass:rgba(255,255,255,.75);
  --pill-bg:#fff;
  --shadow:0 10px 28px rgba(214,76,66,.12);

  min-height:100vh;
  background:var(--bg);
  color:var(--fg);
  display:flex;
  transition:background .2s,color .2s;
}
/* Dark */
.shell[data-theme="dark"]{
  --primary:#ffb4a3;
  --accent:#ff8c7a;
  --peach:#2a1714;
  --sand:#1c1512;
  --ink:#f7ebe7;

  --bg:linear-gradient(180deg,#1b1412,#241815);
  --fg:var(--ink);
  --side-bg:rgba(24,15,13,.88);
  --bd:#3c2722;
  --hover:rgba(255,140,122,.12);
  --glass:rgba(24,15,13,.55);
  --pill-bg:#2a1a16;
  --shadow:0 10px 28px rgba(0,0,0,.35);
}

/* Sidebar */
.sidebar{
  width:270px;background:var(--side-bg);backdrop-filter: blur(8px) saturate(1.08);
  border-inline-end:1px solid var(--bd);display:flex;flex-direction:column;gap:16px;
  padding:16px 12px;position:sticky;top:0;height:100vh;transition:width .18s ease
}
.sidebar.collapsed{ width:80px; }
.brand{
  display:flex;align-items:center;gap:12px;padding:6px 10px;margin-bottom:6px
}
.logo{
  width:40px;height:40px;border-radius:12px;object-fit:cover;box-shadow:var(--shadow)
}
.brand-name{font-weight:800;letter-spacing:.2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

.menu{display:flex;flex-direction:column;gap:6px}
.menu-group{border-radius:14px;background:var(--glass);box-shadow:var(--shadow);padding:6px;border:1px solid var(--bd)}
.menu-item{
  width:100%;display:flex;align-items:center;gap:12px;padding:11px 12px;border-radius:12px;
  border:none;background:transparent;color:inherit;text-align:start;cursor:pointer;transition:.15s
}
.menu-item:hover{background:var(--hover)}
.menu-item.danger:hover{background:rgba(255,0,0,.06)}
.mi{width:22px;height:22px}
.mt{flex:1}
.chev{opacity:.6;transition:transform .2s}
.chev.rot{transform:rotate(180deg)}
.submenu{padding:6px 6px 6px 42px;display:grid;gap:6px}
.submenu a{display:block;padding:8px 10px;border-radius:9px;text-decoration:none;color:inherit}
.submenu a:hover{background:var(--hover)}

/* Main */
.main{flex:1;display:flex;flex-direction:column;min-width:0}
.topbar{
  display:flex;align-items:center;justify-content:space-between;padding:14px 20px;
  border-bottom:1px solid var(--bd);backdrop-filter: blur(6px) saturate(1.05)
}
.left{display:flex;align-items:center;gap:10px}
.welcome{display:flex;align-items:center;gap:10px;font-size:18px}
.welcome small{opacity:.7}
.wave{width:22px;height:22px;color: #ffccba}
.right{display:flex;align-items:center;gap:10px}

.pill{
  border:1px solid var(--bd);background:var(--pill-bg);color:inherit;border-radius:999px;
  padding:8px 12px;cursor:pointer;transition:.15s;display:inline-flex;align-items:center;gap:8px
}
.pill.ghost{background:transparent}
.pill:hover{transform:translateY(-1px);background:var(--hover)}
.toggle svg{width:20px;height:20px}

.avatar{
  position:relative;display:flex;align-items:center;gap:10px;padding:6px 10px;border-radius:999px;
  background:var(--pill-bg);border:1px solid var(--bd);cursor:pointer
}
.avatar-ico{width:24px;height:24px}
.avatar .name{max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dropdown{
  position:absolute;inset-inline-end:0;top:calc(100% + 6px);min-width:200px;background:var(--side-bg);
  border:1px solid var(--bd);border-radius:12px;box-shadow:var(--shadow);padding:6px;z-index:10
}
.dropdown li a{display:flex;align-items:center;gap:8px;padding:10px;border-radius:8px;color:inherit;text-decoration:none}
.dropdown li a:hover{background:var(--hover)}
.dropdown .danger{color:#c03}

/* محتوى */
.content{padding:24px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}
.card{
  background:var(--glass);border:1px solid var(--bd);border-radius:16px;padding:18px;
  box-shadow:var(--shadow);cursor:pointer;transition:.15s
}
.card:hover{transform:translateY(-2px)}

/* Animations */
.fade-enter-active,.fade-leave-active{transition:opacity .15s}
.fade-enter-from,.fade-leave-to{opacity:0}

/* استجابة */
@media (max-width: 900px){
  .sidebar{position:fixed;inset-block:0;inset-inline-start:0;z-index:30}
  .main{margin-inline-start:270px}
  .sidebar.collapsed + .main{ margin-inline-start:80px; }
}
</style>

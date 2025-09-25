<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { Image as ImageIcon, Upload, Check, KeyRound, RefreshCw, ShieldCheck, Sparkles, Loader2 } from 'lucide-vue-next'
import { useGameScore } from '@/composables/useGameScore'
import { emitToast } from '@/utils/toastBus'

const store = useGameScore()

const detectLang = () => {
  const doc = (document.documentElement.lang || '').toLowerCase()
  if (doc.startsWith('en')) return 'en'
  const stored = (localStorage.getItem('ml_lang') || '').toLowerCase()
  return stored.startsWith('en') ? 'en' : 'ar'
}
const detectTheme = () => localStorage.getItem('ml_theme') || 'light'

const lang = ref(detectLang())
const theme = ref(detectTheme())
const isRTL = computed(() => lang.value === 'ar')

const strings = computed(() => lang.value === 'ar'
  ? {
      title: 'إعدادات الحساب',
      avatarTitle: 'صورة البروفايل',
      avatarHint: 'ارفع صورة مربعة بدقة جيدة (حتى 2 م.ب).',
      chooseFile: 'اختر صورة',
      cancel: 'إزالة التحديد',
      upload: 'حفظ الصورة',
      loading: 'جارٍ الرفع...',
      changeSuccess: 'تم تحديث الصورة بنجاح.',
      changeError: 'تعذر تحديث الصورة، حاول لاحقًا.',
      passwordTitle: 'تغيير كلمة المرور',
      formHint: 'استخدم كلمة مرور قوية تجمع بين الأحرف والأرقام والرموز.',
      currentPassword: 'كلمة المرور الحالية',
      newPassword: 'كلمة المرور الجديدة',
      confirmPassword: 'تأكيد كلمة المرور',
      verify: 'تحقّق',
      verified: 'تم التحقق من كلمة المرور.',
      verifyError: 'تحقق من كلمة المرور الحالية أولًا.',
      savePassword: 'حفظ كلمة المرور',
      reset: 'إعادة التعيين',
      passwordSuccess: 'تم تغيير كلمة المرور بنجاح.',
      passwordError: 'تعذر تغيير كلمة المرور، تحقق من البيانات.',
      selectImageFirst: 'اختر صورة أولًا.',
      notImage: 'الملف ليس صورة.',
      tooLarge: 'حجم الصورة يتجاوز 2 م.ب.',
      missingPlayer: 'تعذر إيجاد ملف اللاعب.',
    }
  : {
      title: 'Account settings',
      avatarTitle: 'Profile picture',
      avatarHint: 'Upload a crisp square image (up to 2 MB).',
      chooseFile: 'Choose image',
      cancel: 'Remove selection',
      upload: 'Save avatar',
      loading: 'Uploading...',
      changeSuccess: 'Profile picture updated successfully.',
      changeError: 'We could not update your picture. Try again later.',
      passwordTitle: 'Change password',
      formHint: 'Use a strong password that mixes letters, numbers, and symbols.',
      currentPassword: 'Current password',
      newPassword: 'New password',
      confirmPassword: 'Confirm password',
      verify: 'Verify',
      verified: 'Password verified.',
      verifyError: 'Verify your current password first.',
      savePassword: 'Save password',
      reset: 'Reset form',
      passwordSuccess: 'Password updated successfully.',
      passwordError: 'Unable to change password. Check your entries.',
      selectImageFirst: 'Select an image first.',
      notImage: 'The selected file is not an image.',
      tooLarge: 'Image size exceeds 2 MB.',
      missingPlayer: 'Unable to identify player record.',
    })

const avatarFile = ref(null)
const avatarPreview = ref('')
const avatarStatus = reactive({ loading: false, message: '', error: '' })

const passwordForm = reactive({ current: '', next: '', confirm: '' })
const verifyState = reactive({ loading: false, verified: false, message: '', error: '' })
const passwordStatus = reactive({ loading: false, message: '', error: '' })

const displayName = computed(() => store.username.value || 'Player')
const fallbackInitial = computed(() => displayName.value.trim().charAt(0).toUpperCase() || 'P')
const avatarUrl = computed(() => avatarPreview.value || store.profileImage.value || null)

function handleFileChange(event) {
  avatarStatus.message = ''
  avatarStatus.error = ''
  const file = event.target.files?.[0]
  if (!file) {
    clearSelection()
    return
  }
  if (!file.type.startsWith('image/')) {
    avatarStatus.error = strings.value.notImage
    return
  }
  if (file.size > 2 * 1024 * 1024) {
    avatarStatus.error = strings.value.tooLarge
    return
  }
  if (avatarPreview.value) URL.revokeObjectURL(avatarPreview.value)
  avatarFile.value = file
  avatarPreview.value = URL.createObjectURL(file)
}

function clearSelection() {
  if (avatarPreview.value) URL.revokeObjectURL(avatarPreview.value)
  avatarFile.value = null
  avatarPreview.value = ''
  avatarStatus.message = ''
  avatarStatus.error = ''
}

async function uploadAvatar() {
  if (!avatarFile.value) {
    avatarStatus.error = strings.value.selectImageFirst
    return
  }
  if (!store.gameUserName.value) await store.refresh(true)
  const docname = store.gameUserName.value
  if (!docname) {
    avatarStatus.error = strings.value.missingPlayer
    return
  }
  avatarStatus.loading = true
  avatarStatus.error = ''
  avatarStatus.message = ''
  try {
    const fd = new FormData()
    fd.append('file', avatarFile.value)
    fd.append('filename', avatarFile.value.name)
    fd.append('is_private', '0')
    fd.append('attached_to_doctype', 'Game Users')
    fd.append('attached_to_name', docname)

    const uploadRes = await fetch('/api/method/upload_file', {
      method: 'POST',
      credentials: 'include',
      body: fd,
    })
    const uploadData = await uploadRes.json()
    if (!uploadRes.ok || !uploadData?.message?.file_url) {
      throw new Error(uploadData?._server_messages || uploadData?.message || 'Upload failed')
    }
    const fileUrl = uploadData.message.file_url
    const saveRes = await fetch('/api/method/mathematics_leaders.api.profile.set_profile_image', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_url: fileUrl }),
    })
    const saveData = await saveRes.json()
    if (!saveRes.ok || !saveData?.message?.ok) {
      throw new Error(saveData?.message || 'Unable to store profile image')
    }
    avatarStatus.message = strings.value.changeSuccess
    emitToast({ message: strings.value.changeSuccess, type: 'success' })
    await store.refresh(true)
    clearSelection()
  } catch (err) {
    avatarStatus.error = err instanceof Error ? err.message : strings.value.changeError
    emitToast({ message: avatarStatus.error, type: 'danger' })
  } finally {
    avatarStatus.loading = false
  }
}

async function verifyCurrent() {
  verifyState.loading = true
  verifyState.error = ''
  verifyState.message = ''
  try {
    if (!passwordForm.current) {
      throw new Error(strings.value.verifyError)
    }
    const res = await fetch('/api/method/mathematics_leaders.api.profile.verify_current_password', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ current_password: passwordForm.current }),
    })
    const data = await res.json()
    if (!res.ok || !data?.message?.ok) {
      throw new Error(data?.message || strings.value.verifyError)
    }
    verifyState.verified = true
    verifyState.message = strings.value.verified
    passwordStatus.error = ''
  } catch (err) {
    verifyState.verified = false
    verifyState.error = err instanceof Error ? err.message : strings.value.verifyError
  } finally {
    verifyState.loading = false
  }
}

async function updatePassword() {
  if (!verifyState.verified) {
    verifyState.error = strings.value.verifyError
    return
  }
  passwordStatus.loading = true
  passwordStatus.message = ''
  passwordStatus.error = ''
  const { current, next, confirm } = passwordForm
  try {
    if (!current || !next || !confirm) {
      throw new Error(lang.value === 'ar' ? 'املأ كل الحقول.' : 'Fill in every field.')
    }
    if (next !== confirm) {
      throw new Error(lang.value === 'ar' ? 'كلمتا المرور غير متطابقتين.' : 'Passwords do not match.')
    }
    if (next.length < 8) {
      throw new Error(lang.value === 'ar' ? 'كلمة المرور يجب أن تكون 8 أحرف على الأقل.' : 'Password must be at least 8 characters.')
    }
    const res = await fetch('/api/method/mathematics_leaders.api.profile.change_password', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ current_password: current, new_password: next }),
    })
    const data = await res.json()
    if (!res.ok || !data?.message?.ok) {
      throw new Error(data?.message || strings.value.passwordError)
    }
    passwordStatus.message = strings.value.passwordSuccess
    emitToast({ message: strings.value.passwordSuccess, type: 'success' })
    passwordForm.current = ''
    passwordForm.next = ''
    passwordForm.confirm = ''
    verifyState.verified = false
    verifyState.message = ''
  } catch (err) {
    passwordStatus.error = err instanceof Error ? err.message : strings.value.passwordError
    emitToast({ message: passwordStatus.error, type: 'danger' })
  } finally {
    passwordStatus.loading = false
  }
}

function resetPasswordForm() {
  passwordForm.current = ''
  passwordForm.next = ''
  passwordForm.confirm = ''
  verifyState.loading = false
  verifyState.verified = false
  verifyState.message = ''
  verifyState.error = ''
  passwordStatus.loading = false
  passwordStatus.message = ''
  passwordStatus.error = ''
}

let langObserver = null
let themeObserver = null
let storageHandler = null

onMounted(() => {
  if (store.score.value == null) store.refresh(true)

  const updateLang = () => { lang.value = detectLang() }
  const updateTheme = () => { theme.value = detectTheme() }

  langObserver = new MutationObserver(updateLang)
  langObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] })

  themeObserver = new MutationObserver(updateTheme)
  themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })

  storageHandler = () => {
    updateLang()
    updateTheme()
  }
  window.addEventListener('storage', storageHandler)
})

onUnmounted(() => {
  if (avatarPreview.value) URL.revokeObjectURL(avatarPreview.value)
  if (langObserver) langObserver.disconnect()
  if (themeObserver) themeObserver.disconnect()
  if (storageHandler) window.removeEventListener('storage', storageHandler)
})
</script>

<template>
  <div class="settings" :dir="isRTL ? 'rtl' : 'ltr'" :data-theme="theme">
    <header class="settings__header">
      <Sparkles class="heading-icon" />
      <h1 class="page-title">{{ strings.title }}</h1>
    </header>

    <div class="settings__grid">
      <section class="settings-card profile-card">
        <header class="card-header">
          <div class="title">
            <ImageIcon class="icon" />
            <div>
              <h2>{{ strings.avatarTitle }}</h2>
              <p>{{ strings.avatarHint }}</p>
            </div>
          </div>
        </header>
        <div class="card-body">
          <div class="avatar-stack">
            <div class="avatar-orbit">
              <div class="avatar-ring">
                <img v-if="avatarUrl" :src="avatarUrl" alt="avatar preview" />
                <span v-else>{{ fallbackInitial }}</span>
              </div>
            </div>
            <span class="display-name">{{ displayName }}</span>
          </div>

          <div class="controls">
            <label class="btn ghost" data-ripple>
              <Upload class="icon" />
              <span>{{ strings.chooseFile }}</span>
              <input type="file" accept="image/*" @change="handleFileChange" hidden />
            </label>
            <button v-if="avatarFile" type="button" class="btn subtle" data-ripple @click="clearSelection">{{ strings.cancel }}</button>
            <button type="button" class="btn solid" data-ripple :disabled="avatarStatus.loading" @click="uploadAvatar">
              <Loader2 v-if="avatarStatus.loading" class="icon spinner" />
              <ImageIcon v-else class="icon" />
              <span>{{ avatarStatus.loading ? strings.loading : strings.upload }}</span>
            </button>
          </div>

          <transition name="fade-slide" mode="out-in">
            <p v-if="avatarStatus.message" key="avatar-ok" class="status success">
              <ShieldCheck class="icon" />
              <span>{{ avatarStatus.message }}</span>
            </p>
          </transition>
          <transition name="fade-slide" mode="out-in">
            <p v-if="avatarStatus.error" key="avatar-err" class="status error">{{ avatarStatus.error }}</p>
          </transition>
        </div>
      </section>

      <section class="settings-card password-card">
        <header class="card-header">
          <div class="title">
            <KeyRound class="icon" />
            <div>
              <h2>{{ strings.passwordTitle }}</h2>
              <p>{{ strings.formHint }}</p>
            </div>
          </div>
        </header>

        <form class="card-body password-form" @submit.prevent="updatePassword">
          <div class="verify-block">
            <label>
              <span>{{ strings.currentPassword }}</span>
              <input type="password" v-model="passwordForm.current" autocomplete="current-password" />
            </label>
            <button type="button" class="btn solid" data-ripple :disabled="verifyState.loading" @click="verifyCurrent">
              <Loader2 v-if="verifyState.loading" class="icon spinner" />
              <Check v-else class="icon" />
              <span>{{ verifyState.loading ? strings.loading : strings.verify }}</span>
            </button>
            <transition name="fade-slide" mode="out-in">
              <p v-if="verifyState.message" key="verify-ok" class="status success">
                <ShieldCheck class="icon" />
                <span>{{ verifyState.message }}</span>
              </p>
            </transition>
            <transition name="fade-slide" mode="out-in">
              <p v-if="verifyState.error" key="verify-err" class="status error">{{ verifyState.error }}</p>
            </transition>
          </div>

          <transition name="panel-grow">
            <div v-if="verifyState.verified" class="password-fields">
              <label>
                <span>{{ strings.newPassword }}</span>
                <input type="password" v-model="passwordForm.next" autocomplete="new-password" required />
              </label>
              <label>
                <span>{{ strings.confirmPassword }}</span>
                <input type="password" v-model="passwordForm.confirm" autocomplete="new-password" required />
              </label>
              <div class="form-actions">
                <button class="btn success" data-ripple type="submit" :disabled="passwordStatus.loading">
                  <Loader2 v-if="passwordStatus.loading" class="icon spinner" />
                  <Check v-else class="icon" />
                  <span>{{ passwordStatus.loading ? strings.loading : strings.savePassword }}</span>
                </button>
                <button type="button" class="btn subtle" data-ripple @click="resetPasswordForm">
                  <RefreshCw class="icon" />
                  <span>{{ strings.reset }}</span>
                </button>
              </div>
              <transition name="fade-slide" mode="out-in">
                <p v-if="passwordStatus.message" key="pass-ok" class="status success">
                  <ShieldCheck class="icon" />
                  <span>{{ passwordStatus.message }}</span>
                </p>
              </transition>
              <transition name="fade-slide" mode="out-in">
                <p v-if="passwordStatus.error" key="pass-err" class="status error">{{ passwordStatus.error }}</p>
              </transition>
            </div>
          </transition>
        </form>
      </section>
    </div>
  </div>
</template>

<style scoped>
.settings{
  display:flex;
  flex-direction:column;
  gap:28px;
  width:min(1100px,100%);
  margin:0 auto;
  padding:24px 20px 48px;
}
.settings__header{display:flex;align-items:center;gap:12px}
.heading-icon{width:24px;height:24px;color:#c8a03b;filter:drop-shadow(0 6px 12px rgba(200,160,59,0.35))}
.page-title{margin:0;font-size:2rem;font-weight:800}

.settings__grid{
  display:grid;
  gap:24px;
  grid-template-columns:repeat(auto-fit,minmax(320px,1fr));
}

.settings-card{
  position:relative;
  display:flex;
  flex-direction:column;
  gap:18px;
  padding:24px 26px;
  border-radius:30px;
  background:linear-gradient(140deg,rgba(15,138,62,0.1),rgba(200,160,59,0.14));
  border:1px solid rgba(200,160,59,0.22);
  box-shadow:0 30px 60px rgba(15,138,62,0.18);
  overflow:hidden;
}
.settings-card::after{
  content:"";
  position:absolute;
  inset:auto -30% -40% 0;
  height:160px;
  background:linear-gradient(140deg,rgba(200,160,59,0.25),transparent);
  opacity:.4;
}
[data-theme="dark"] .settings-card{
  background:linear-gradient(140deg,rgba(15,138,62,0.28),rgba(21,32,43,0.82));
  border-color:rgba(200,160,59,0.32);
  box-shadow:0 32px 70px rgba(0,0,0,0.55);
}

.card-header{position:relative;z-index:1;display:flex;flex-direction:column;gap:12px}
.card-header .title{display:flex;align-items:flex-start;gap:14px}
.card-header .icon{width:28px;height:28px;color:#0f8a3e}
.card-header h2{margin:0;font-size:1.4rem;font-weight:700}
.card-header p{margin:4px 0 0;color:rgba(17,24,39,0.65)}
[data-theme="dark"] .card-header .icon{color:#f4d67c}
[data-theme="dark"] .card-header p{color:rgba(255,255,255,0.65)}

.card-body{position:relative;z-index:1;display:flex;flex-direction:column;gap:20px}

.avatar-stack{display:flex;align-items:center;gap:18px}
.avatar-orbit{position:relative;width:120px;height:120px;display:flex;align-items:center;justify-content:center}
.avatar-orbit::after{
  content:"";
  position:absolute;
  inset:-6px;
  border-radius:50%;
  background:radial-gradient(circle,rgba(200,160,59,0.4),transparent 65%);
  filter:blur(12px);
  opacity:.65;
}
.avatar-ring{
  position:relative;
  width:104px;
  height:104px;
  border-radius:50%;
  display:flex;
  align-items:center;
  justify-content:center;
  background:linear-gradient(135deg,rgba(255,255,255,0.9),rgba(248,238,212,0.9));
  border:3px solid rgba(200,160,59,0.55);
  box-shadow:0 18px 36px rgba(15,138,62,0.22);
  overflow:hidden;
  font-size:2.8rem;
  font-weight:800;
  color:#0f8a3e;
}
.avatar-ring img{width:100%;height:100%;object-fit:cover}
[data-theme="dark"] .avatar-ring{background:linear-gradient(135deg,rgba(27,32,38,0.95),rgba(18,21,24,0.92));color:#f4d67c}

.display-name{font-size:1.3rem;font-weight:700}

.controls{display:flex;gap:12px;flex-wrap:wrap}
.btn{
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding:10px 16px;
  border-radius:14px;
  font-weight:600;
  cursor:pointer;
  border:1px solid transparent;
  transition:transform .2s ease, box-shadow .2s ease, background .2s ease;
}
.btn .icon{width:18px;height:18px}
.btn .spinner{animation:spin .9s linear infinite}
.btn:disabled{opacity:.6;cursor:not-allowed}
.btn:hover:not(:disabled){transform:translateY(-2px)}

.btn.ghost{background:rgba(15,138,62,0.12);border-color:rgba(15,138,62,0.18);color:#0f8a3e}
.btn.ghost:hover{box-shadow:0 14px 28px rgba(15,138,62,0.18)}
.btn.solid{background:linear-gradient(135deg,#c8a03b,#0f8a3e);color:#fff;box-shadow:0 16px 36px rgba(15,138,62,0.22)}
.btn.solid:hover{box-shadow:0 22px 44px rgba(15,138,62,0.28)}
.btn.subtle{background:rgba(255,255,255,0.55);border-color:rgba(200,160,59,0.28);color:#7a5a13}
.btn.success{background:linear-gradient(135deg,#22c55e,#0f8a3e);color:#fff;border-color:rgba(34,197,94,0.4);box-shadow:0 16px 34px rgba(34,197,94,0.25)}
[data-theme="dark"] .btn.subtle{background:rgba(21,32,43,0.7);color:#f4d67c}
[data-theme="dark"] .btn.ghost{background:rgba(200,160,59,0.22);color:#f4d67c}

.status{display:flex;align-items:center;gap:8px;font-weight:600}
.status.success{color:#0f8a3e}
.status.error{color:#dc2626}
[data-theme="dark"] .status.success{color:#f4d67c}

.password-form{display:flex;flex-direction:column;gap:18px}
.verify-block{display:flex;flex-direction:column;gap:12px;background:rgba(255,255,255,0.38);padding:16px 18px;border-radius:20px;border:1px solid rgba(200,160,59,0.18)}
.verify-block label{display:flex;flex-direction:column;gap:6px;font-weight:600}
.verify-block input{border-radius:12px;border:1px solid rgba(17,24,39,0.18);padding:10px 12px;font-size:1rem}
.verify-block input:focus{outline:none;border-color:#0f8a3e;box-shadow:0 0 0 3px rgba(15,138,62,0.18)}
[data-theme="dark"] .verify-block{background:rgba(21,32,43,0.72);border-color:rgba(200,160,59,0.28)}
[data-theme="dark"] .verify-block input{background:rgba(12,18,20,0.92);color:#f4f4f4;border-color:rgba(200,160,59,0.25)}

.password-fields{display:flex;flex-direction:column;gap:16px;padding:8px 0}
.password-fields label{display:flex;flex-direction:column;gap:6px;font-weight:600}
.password-fields input{border-radius:12px;border:1px solid rgba(17,24,39,0.18);padding:10px 12px;font-size:1rem}
.password-fields input:focus{outline:none;border-color:#0f8a3e;box-shadow:0 0 0 3px rgba(15,138,62,0.18)}

.form-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:4px}

.fade-slide-enter-active,.fade-slide-leave-active{transition:opacity .25s ease, transform .25s ease}
.fade-slide-enter-from,.fade-slide-leave-to{opacity:0;transform:translateY(6px)}

.panel-grow-enter-active,.panel-grow-leave-active{transition:opacity .28s ease, transform .28s ease}
.panel-grow-enter-from,.panel-grow-leave-to{opacity:0;transform:scale(.95)}

@keyframes spin{to{transform:rotate(360deg)}}

@media (max-width: 720px){
  .settings{padding:20px 16px 36px}
  .settings-card{padding:20px}
  .avatar-stack{flex-direction:column;align-items:flex-start}
  .avatar-orbit{width:108px;height:108px}
  .avatar-ring{width:92px;height:92px}
}
</style>

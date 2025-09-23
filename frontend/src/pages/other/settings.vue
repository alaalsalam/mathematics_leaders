<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { Image as ImageIcon, Upload, Check, KeyRound, RefreshCw } from 'lucide-vue-next'
import { useGameScore } from '@/composables/useGameScore'

const store = useGameScore()

const detectLang = () => {
  const doc = (document.documentElement.lang || '').toLowerCase()
  if (doc.startsWith('en')) return 'en'
  const stored = (localStorage.getItem('ml_lang') || '').toLowerCase()
  return stored.startsWith('en') ? 'en' : 'ar'
}
const lang = ref(detectLang())

const strings = computed(() => ({
  ar: {
    title: 'إعدادات الحساب',
    avatarTitle: 'صورة البروفايل',
    avatarHint: 'ارفع صورة مربعة للحصول على أفضل نتيجة. الحد الأقصى 2 ميغابايت.',
    upload: 'رفع صورة',
    changeSuccess: 'تم تحديث صورة البروفايل.',
    changeError: 'تعذر تحديث صورة البروفايل، حاول لاحقًا.',
    passwordTitle: 'تغيير كلمة المرور',
    currentPassword: 'كلمة المرور الحالية',
    newPassword: 'كلمة المرور الجديدة',
    confirmPassword: 'تأكيد كلمة المرور',
    savePassword: 'حفظ كلمة المرور',
    passwordSuccess: 'تم تغيير كلمة المرور بنجاح.',
    passwordError: 'تعذر تغيير كلمة المرور، تحقق من البيانات.',
    chooseFile: 'اختر ملفًا',
    cancel: 'إزالة التحديد',
    loading: 'جاري الحفظ...',
    verify: 'تحقّق',
    reset: 'إعادة التعيين',
    reset: 'إعادة التعيين',
    formHint: 'استخدم كلمة مرور قوية تتكون من أحرف وأرقام ورموز.',
  },
  en: {
    title: 'Account Settings',
    avatarTitle: 'Profile picture',
    avatarHint: 'Upload a square image for the best result. Max 2 MB.',
    upload: 'Upload image',
    changeSuccess: 'Profile picture updated successfully.',
    changeError: 'We could not update your profile picture. Try again later.',
    passwordTitle: 'Change password',
    currentPassword: 'Current password',
    newPassword: 'New password',
    confirmPassword: 'Confirm password',
    savePassword: 'Save password',
    passwordSuccess: 'Password updated successfully.',
    passwordError: 'Unable to update password. Verify your entries.',
    chooseFile: 'Choose file',
    cancel: 'Remove selection',
    loading: 'Saving...',
    verify: 'Verify',
    reset: 'Reset',
    reset: 'Reset',
    formHint: 'Use a strong password mixing letters, numbers, and symbols.',
  },
}[lang.value]))

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
    avatarStatus.error = lang.value === 'ar' ? 'الملف ليس صورة.' : 'The selected file is not an image.'
    return
  }
  if (file.size > 2 * 1024 * 1024) {
    avatarStatus.error = lang.value === 'ar' ? 'حجم الصورة يتجاوز 2 ميغابايت.' : 'Image size exceeds 2 MB.'
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
    avatarStatus.error = lang.value === 'ar' ? 'اختر صورة أولًا.' : 'Select an image first.'
    return
  }
  if (!store.gameUserName.value) await store.refresh(true)
  const docname = store.gameUserName.value
  if (!docname) {
    avatarStatus.error = lang.value === 'ar' ? 'لا يمكن إيجاد ملف اللاعب.' : 'Unable to identify player record.'
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
    await store.refresh(true)
    clearSelection()
  } catch (err) {
    avatarStatus.error = err instanceof Error ? err.message : strings.value.changeError
  } finally {
    avatarStatus.loading = false
  }
}

async function updatePassword() {
  if (!verifyState.verified) {
    verifyState.error = lang.value === 'ar' ? 'تحقق من كلمة المرور الحالية أولاً.' : 'Verify your current password first.'
    return
  }
  passwordStatus.loading = true
  passwordStatus.error = ''
  passwordStatus.message = ''
  const { current, next, confirm } = passwordForm
  try {
    if (!current || !next || !confirm) {
      throw new Error(lang.value === 'ar' ? 'املأ كل الحقول.' : 'Please fill in all fields.')
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
    passwordForm.current = ''
    passwordForm.next = ''
    passwordForm.confirm = ''
    verifyState.verified = false
    verifyState.message = ''
  } catch (err) {
    passwordStatus.error = err instanceof Error ? err.message : strings.value.passwordError
  } finally {
    passwordStatus.loading = false
  }
}

async function verifyCurrent() {
  verifyState.loading = true
  verifyState.error = ''
  verifyState.message = ''
  try {
    if (!passwordForm.current) {
      throw new Error(lang.value === 'ar' ? 'أدخل كلمة المرور الحالية.' : 'Enter your current password.')
    }
    const res = await fetch('/api/method/mathematics_leaders.api.profile.verify_current_password', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ current_password: passwordForm.current }),
    })
    const data = await res.json()
    if (!res.ok || !data?.message?.ok) {
      throw new Error(data?.message || (lang.value === 'ar' ? 'كلمة المرور الحالية غير صحيحة.' : 'Current password is incorrect.'))
    }
    verifyState.verified = true
    verifyState.message = lang.value === 'ar' ? 'تم التحقق من كلمة المرور.' : 'Password verified.'
    passwordStatus.error = ''
  } catch (err) {
    verifyState.error = err instanceof Error ? err.message : (lang.value === 'ar' ? 'تعذر التحقق.' : 'Verification failed.')
    verifyState.verified = false
  } finally {
    verifyState.loading = false
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

onMounted(() => {
  if (store.score.value == null) store.refresh(true)
  const update = () => { lang.value = detectLang() }
  const observer = new MutationObserver(update)
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] })
  window.addEventListener('storage', update)
  onUnmounted(() => {
    observer.disconnect()
    window.removeEventListener('storage', update)
  })
})

onUnmounted(() => {
  if (avatarPreview.value) URL.revokeObjectURL(avatarPreview.value)
})
</script>

<template>
  <div class="settings" :data-theme="lang">
    <h1 class="page-title">{{ strings.title }}</h1>

    <section class="card">
      <header>
        <ImageIcon class="icon" />
        <div>
          <h2>{{ strings.avatarTitle }}</h2>
          <p>{{ strings.avatarHint }}</p>
        </div>
      </header>
      <div class="body">
        <div class="avatar-preview">
          <div class="preview-shell">
            <img v-if="avatarUrl" :src="avatarUrl" alt="avatar preview" />
            <span v-else>{{ fallbackInitial }}</span>
          </div>
          <span class="name">{{ displayName }}</span>
        </div>
        <div class="actions">
          <label class="upload-btn">
            <Upload class="icon" />
            <span>{{ strings.chooseFile }}</span>
            <input type="file" accept="image/*" @change="handleFileChange" hidden />
          </label>
          <button v-if="avatarFile" class="ghost" @click="clearSelection">{{ strings.cancel }}</button>
          <button class="solid" :disabled="avatarStatus.loading" @click="uploadAvatar">
            <ImageIcon class="icon" />
            <span>{{ avatarStatus.loading ? strings.loading : strings.upload }}</span>
          </button>
        </div>
        <p v-if="avatarStatus.message" class="success">{{ avatarStatus.message }}</p>
        <p v-if="avatarStatus.error" class="error">{{ avatarStatus.error }}</p>
      </div>
    </section>

    <section class="card">
      <header>
        <KeyRound class="icon" />
        <div>
          <h2>{{ strings.passwordTitle }}</h2>
          <p>{{ strings.formHint }}</p>
        </div>
      </header>
      <form class="body form" @submit.prevent="updatePassword">
        <div class="verify-block">
          <label>
            <span>{{ strings.currentPassword }}</span>
            <input type="password" v-model="passwordForm.current" autocomplete="current-password" />
          </label>
          <div class="verify-actions">
            <button type="button" class="solid" :disabled="verifyState.loading" @click="verifyCurrent">
              <Check class="icon" />
              <span>{{ verifyState.loading ? strings.loading : strings.verify }}</span>
            </button>
          </div>
          <p v-if="verifyState.message" class="success">{{ verifyState.message }}</p>
          <p v-if="verifyState.error" class="error">{{ verifyState.error }}</p>
        </div>

        <template v-if="verifyState.verified">
          <label>
            <span>{{ strings.newPassword }}</span>
            <input type="password" v-model="passwordForm.next" autocomplete="new-password" required />
          </label>
          <label>
            <span>{{ strings.confirmPassword }}</span>
            <input type="password" v-model="passwordForm.confirm" autocomplete="new-password" required />
          </label>
          <div class="form-actions">
            <button class="solid" type="submit" :disabled="passwordStatus.loading">
              <Check class="icon" />
              <span>{{ passwordStatus.loading ? strings.loading : strings.savePassword }}</span>
            </button>
            <button type="button" class="ghost" @click="resetPasswordForm">
              <RefreshCw class="icon" />
              <span>{{ strings.reset }}</span>
            </button>
          </div>
          <p v-if="passwordStatus.message" class="success">{{ passwordStatus.message }}</p>
          <p v-if="passwordStatus.error" class="error">{{ passwordStatus.error }}</p>
        </template>
      </form>
    </section>
  </div>
</template>

<style scoped>
.settings{ display:flex; flex-direction:column; gap:20px; padding:0; width:100% }
.page-title{ margin:0; font-size:1.8rem; font-weight:800; color:#1f2937 }

.card{ background:var(--panel,#fff); border-radius:20px; padding:20px 22px; box-shadow:0 16px 32px rgba(15,23,42,.12); display:flex; flex-direction:column; gap:18px }
.card header{ display:flex; gap:14px; align-items:flex-start }
.card header .icon{ width:28px; height:28px; color:#2563eb }
.card header h2{ margin:0; font-size:1.3rem; font-weight:700 }
.card header p{ margin:4px 0 0; color:rgba(17,24,39,.65) }

.body{ display:flex; flex-direction:column; gap:18px }
.avatar-preview{ display:flex; align-items:center; gap:16px }
.preview-shell{ width:96px; height:96px; border-radius:24px; background:linear-gradient(135deg,#1d4ed8,#22c55e); color:#fff; font-size:2.4rem; font-weight:700; display:flex; align-items:center; justify-content:center; overflow:hidden; box-shadow:0 12px 20px rgba(37,99,235,.25) }
.preview-shell img{ width:100%; height:100%; object-fit:cover }
.avatar-preview .name{ font-size:1.2rem; font-weight:600 }

.actions{ display:flex; gap:12px; flex-wrap:wrap }
.upload-btn,.solid,.ghost{ display:inline-flex; align-items:center; gap:8px; border-radius:12px; padding:10px 16px; cursor:pointer; transition:.2s; border:1px solid transparent }
.upload-btn{ background:rgba(37,99,235,.1); color:#1d4ed8; border-color:rgba(37,99,235,.15) }
.upload-btn:hover{ background:rgba(37,99,235,.18) }
.solid{ background:#2563eb; color:#fff }
.solid:disabled{ opacity:.6; cursor:wait }
.ghost{ background:transparent; color:#1f2937; border-color:rgba(17,24,39,.15) }
.ghost:hover{ background:rgba(17,24,39,.05) }

.success{ color:#047857; font-weight:600 }
.error{ color:#b91c1c; font-weight:600 }

.form{ display:flex; flex-direction:column; gap:16px }
.form label{ display:flex; flex-direction:column; gap:8px; font-weight:600 }
.form input{ border-radius:10px; border:1px solid rgba(17,24,39,.15); padding:10px 12px; font-size:1rem }
.form input:focus{ outline:none; border-color:#2563eb; box-shadow:0 0 0 3px rgba(37,99,235,.15) }
.verify-block{ display:flex; flex-direction:column; gap:12px; background:rgba(37,99,235,.05); padding:12px 14px; border-radius:14px }
.verify-actions{ display:flex; gap:12px }
.verify-actions .solid{ background:#2563eb; border-color:#1d4ed8 }
.form-actions{ display:flex; gap:12px; flex-wrap:wrap }
.form-actions .solid{ background:#22c55e; border-color:#16a34a }
.form-actions .ghost{ color:#1d4ed8; border-color:rgba(37,99,235,.2) }

@media(max-width:720px){
  .avatar-preview{ flex-direction:column; align-items:flex-start }
  .preview-shell{ width:84px; height:84px }
}
</style>

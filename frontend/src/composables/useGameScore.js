import { ref } from 'vue'
import { emitToast } from '@/utils/toastBus'

const score = ref(null)
const rank = ref(null)
const totalPlayers = ref(null)
const bestScore = ref(null)
const loading = ref(false)
const error = ref(null)
const lastUpdated = ref(0)
const profileImage = ref(null)
const username = ref(null)
const gameUserName = ref(null)

async function fetchScore(force = false) {
  const now = Date.now()
  if (!force && score.value !== null && now - lastUpdated.value < 60_000) {
    return
  }
  if (loading.value) return

  loading.value = true
  error.value = null
  try {
    const res = await fetch('/api/method/mathematics_leaders.api.game_points.get_points', {
      method: 'GET',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    })
    const data = await res.json()
    if (!res.ok || !data?.message?.ok) {
      throw new Error(data?.message || 'Unable to load score')
    }
    const payload = data.message
    score.value = Number(payload.points || 0)
    rank.value = payload.rank || 1
    totalPlayers.value = payload.players || 1
    bestScore.value = Number(payload.best || payload.points || 0)
    profileImage.value = payload.profile_image || null
    username.value = payload.username || null
    gameUserName.value = payload.game_user_name || null
    lastUpdated.value = now
  } catch (err) {
    error.value = err instanceof Error ? err.message : String(err)
    emitToast({ message: error.value, type: 'danger' })
  } finally {
    loading.value = false
  }
}

export function useGameScore() {
  return {
    score,
    rank,
    totalPlayers,
    bestScore,
    loading,
    error,
    lastUpdated,
    profileImage,
    username,
    gameUserName,
    refresh: fetchScore,
  }
}

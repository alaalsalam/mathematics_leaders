const EVENT_NAME = 'ml-toast'

export function emitToast({ message, type = 'info', duration = 2600 } = {}) {
  if (!message) return
  window.dispatchEvent(new CustomEvent(EVENT_NAME, {
    detail: {
      message,
      type,
      duration,
      id: crypto.randomUUID?.() || Math.random().toString(36).slice(2),
      timestamp: Date.now(),
    },
  }))
}

export function onToast(listener) {
  window.addEventListener(EVENT_NAME, listener)
  return () => window.removeEventListener(EVENT_NAME, listener)
}

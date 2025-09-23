import { createRouter, createWebHashHistory } from 'vue-router'
import Login from '@/components/Index.vue'
import Home from '@/components/Dashboard.vue'
const router = createRouter({
  history: createWebHashHistory('/math-leaders-games/'),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: Login },
    { path: '/home', component: Home },
    { path: '/scores', component: () => import('@/pages/other/ScoresView.vue') },
    { path: '/settings', component: () => import('@/pages/other/SettingsView.vue') },
  ],
})

export default router

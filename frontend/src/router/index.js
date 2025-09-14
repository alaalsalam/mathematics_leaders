import { createRouter, createWebHashHistory } from 'vue-router'
import Index from '@/components/Index.vue'
import Login from '@/components/Index.vue' // أو صفحة Login إن عندك واحدة منفصلة

export default createRouter({
  history: createWebHashHistory('/assets/math-leaders-games/'),
  routes: [
    { path: '/', component: Index },
    { path: '/login', component: Login },
  ],
})

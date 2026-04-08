import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import WeekView from '@/views/WeekView.vue'
import QuestionView from '@/views/QuestionView.vue'
import CheckInView from '@/views/CheckInView.vue'
import QueryPage from '@/views/QueryPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',              name: 'home',      component: HomeView },
    { path: '/week/:id',      name: 'week',      component: WeekView,      props: true },
    { path: '/question/:dayId', name: 'question', component: QuestionView, props: true },
    { path: '/checkin/:dayId',  name: 'checkin',  component: CheckInView,  props: true },
    { path: '/nl2sql',          name: 'nl2sql',   component: QueryPage },
  ],
})

export default router

import { createRouter, createWebHashHistory } from 'vue-router'
import SectionWaterFall from '../views/SectionWaterFall.vue'
import Roadmap from '../views/Roadmap.vue'
import Home from '../views/Home.vue'
import Detail from '../views/DetailPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/section',
    name: 'Section',
    component: SectionWaterFall
  },
  {
    path: '/roadmap',
    name: 'Roadmap',
    component: Roadmap
  },
  {
    path: '/detail',
    name: 'Detail',
    component: Detail
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router

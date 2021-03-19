import { createRouter, createWebHashHistory } from 'vue-router'
import SectionWaterFall from '../views/SectionWaterFall.vue'
import Home from '../views/Home.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/section',
    name: 'Section',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: SectionWaterFall
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router

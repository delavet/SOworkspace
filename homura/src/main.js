import {
  createApp
} from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import naive from 'naive-ui'

createApp(App).use(naive).use(store).use(router).mount('#app')

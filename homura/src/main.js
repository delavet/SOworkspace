import {
  createApp
} from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import naive from 'naive-ui'
import axios from 'axios'
import VueAxios from 'vue-axios'
import './index.css'

axios.defaults.baseURL = 'http://8.136.235.136:3001/api'

createApp(App).use(naive).use(store).use(router).use(VueAxios, axios).mount('#app')

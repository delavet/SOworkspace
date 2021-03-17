import {
  createStore
} from 'vuex'
import axios from 'axios'

axios.defaults.baseURL = 'http://localhost:3001/api'

export default createStore({
  state: {
    hello_world: ''
  },
  mutations: {
    set_hello: (state, payload) => {
      state.hello_world = payload
    }
  },
  actions: {
    async hello_homura ({
      commit
    }) {
      const res = await axios.get('/hello')
      commit('set_hello', res.data)
    }
  },
  modules: {}
})

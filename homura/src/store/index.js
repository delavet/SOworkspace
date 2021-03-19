import {
  createStore
} from 'vuex'
import axios from 'axios'

axios.defaults.baseURL = 'http://localhost:3001/api'

export default createStore({
  state: {
    hello: '',
    current_section_id: '30',
    current_submap: {
      nodes: [],
      edges: []
    },
    current_show_detail_node: ''
  },
  mutations: {
    set_hello: (state, payload) => {
      state.hello = payload
    },
    set_current_section_id: (state, payload) => {
      state.current_section_id = payload
      console.log(state.current_section_id)
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

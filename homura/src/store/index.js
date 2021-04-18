import {
  createStore
} from 'vuex'
import axios from 'axios'

axios.defaults.baseURL = 'http://8.136.235.136:3001/api'

export default createStore({
  state: {
    en: false,
    hello: '',
    doc_name: 'javadoc',
    current_section_id: '0',
    current_submap: {
      nodes: [],
      edges: []
    },
    refresh_map: false,
    current_show_detail_threads: '',
    current_show_detail_node: '11863', // 当前重点展示的结点，是被选中的结点，一开始就是center node，后面随着用户选择会变
    current_show_detail_api_name: '...',
    current_map_center_node: '11863', // 整个submap的中心节点，除非图换了不然一直都是那一个结点
    current_map_center_node_item: undefined,
    current_show_detail_node_item: undefined,
    show_community_map: true,
    show_current_detail_node: true
  },
  mutations: {
    set_language: (state, payload) => {
      if (payload === 'en') {
        state.en = true
      } else {
        state.en = false
      }
    },
    set_hello: (state, payload) => {
      state.hello = payload
    },
    set_current_section_id: (state, payload) => {
      state.current_section_id = payload
      // .log(state.current_section_id)
    },
    set_current_submap: (state, payload) => {
      state.current_submap = payload
    },
    set_current_center_node: (state, payload) => {
      state.current_map_center_node = payload
      state.current_show_detail_node = payload
    },
    set_show_detail_node: (state, payload) => {
      state.current_show_detail_node = payload
    },
    set_show_detail_api_name: (state, payload) => {
      state.current_show_detail_api_name = payload
    },
    switch_map_show_mode: (state) => {
      state.show_community_map = !state.show_community_map
    },
    set_map_show_mode: (state, payload) => {
      state.show_community_map = payload
    },
    set_show_current_detail_mode: (state, payload) => {
      state.show_current_detail_node = payload
    },
    set_current_show_detail_threads: (state, payload) => {
      state.current_show_detail_threads = payload
    },
    set_refresh_map: (state, payload) => {
      state.refresh_map = payload
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

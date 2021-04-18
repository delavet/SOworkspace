<template>
  <div class="search-home">
    <n-layout style="{background-color:rgba(0,0,0,0)}">
      <n-layout-header>
        <div id="search-space">
          <n-auto-complete
            id="search-input"
            v-model:value="searchValue"
            size="large"
            :placeholder="en?'input any word you think out, we will complete the rest :-)':'输入你能想到的任何词，我们总能找到点什么（大概'"
          />
          <n-button circle @click="onSearchClick">
            <template #icon>
              <n-icon><search /></n-icon>
            </template>
          </n-button>
        </div>
      </n-layout-header>
      <n-layout id = "result-layout">
        <n-card
          id="result-card"
          :title="en?'Search Result':'搜索结果'"
          size = "huge"
          :bordered="false">
          <n-list>
            <n-list-item v-for="item in literal_items" :key="item.id">
              <template #suffix>
                <n-button @click="onViewClick(item)">{{en?"browse in Roadmap":"在路线图中查看"}}</n-button>
              </template>
              <n-thing :title="item.name" :description="item.description">
              </n-thing>
            </n-list-item>
          </n-list>
        </n-card>
      </n-layout>
    </n-layout>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { Search, TrashOutline } from '@vicons/ionicons5'
import { mapState, mapMutations } from 'vuex'
import { useMessage } from 'naive-ui'

let loadingMessage = null

export default defineComponent({
  components: {
    Search
  },
  created () {
    const message = useMessage()
    this.messageBox = message
  },
  data () {
    return {
      searchValue: '',
      messageBox: undefined,
      literal_items: []
    }
  },
  methods: {
    async onSearchClick () {
      if (this.searchValue === '') {
        return
      }
      loadingMessage = this.messageBox.loading('loading thread info', { duration: 5000 })
      const paramObj = {
        query: this.searchValue
      }
      const literalRes = await this.$http.post(this.loadUrl, paramObj)
      const literalData = literalRes.data.data
      this.literal_items = literalData
      if (loadingMessage) {
        loadingMessage.destroy()
        loadingMessage = null
      }
      this.messageBox.success('thread info list loaded', { duration: 500 })
    },
    onViewClick (item) {
      this.set_id(item.id)
      this.set_section_id('')
      this.update_map(TrashOutline)
      this.set_show_map(false)
      this.$router.push('/roadmap')
    },
    ...mapMutations({
      set_id: 'set_current_center_node',
      set_section_id: 'set_current_section_id',
      set_show_map: 'set_map_show_mode',
      update_map: 'set_refresh_map'
    })
  },
  computed: {
    searchOptions () {
      return ['没做完', '是真的', '别想了'].map((suffix) => {
        const prefix = this.searchValue.split('@')[0]
        return {
          label: prefix + suffix,
          value: prefix + suffix
        }
      })
    },
    loadUrl () {
      return '/search/' + this.docName
    },
    loadConceptUrl () {
      return '/searchByConcept/' + this.docName
    },
    ...mapState({
      docName: 'doc_name',
      en: 'en'
    })
  }
})
</script>

<style scoped>
.search-home {
  text-align: center;
  width: 100%;
  height: 100%;
  background-size: cover;
}

#search-space {
  display: flex;
  justify-content: center;
  margin: 20px;
}

#search-input {
  width: 450px;
  display: inline-block;
  margin-right: 20px;
}

#result-content {
  overflow: scroll;
}

#result-layout {
  justify-content: center;
  display: flex;
  flex-direction: row;
}

#result-card {
  overflow: auto;
  margin: 20px;
  border-radius: 15px;
  box-shadow: 0 2px 10px 2px rgba(0, 0, 0, .08);
  height: 100%;
  max-width:708px;
  word-break: break-all;
}
</style>

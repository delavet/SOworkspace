<template>
  <div class="search-home">
    <n-layout>
      <n-layout-header>
        <div id="search-space">
          <n-auto-complete
            id="search-input"
            :options="searchOptions"
            v-model:value="searchValue"
            size="large"
            placeholder="input any word you think out, we will complete the rest :-)"
          />
          <n-button circle @click="onSearchClick">
            <template #icon>
              <n-icon><search /></n-icon>
            </template>
          </n-button>
        </div>
      </n-layout-header>
      <n-layout>
        <n-grid :cols="2">
          <n-grid-item>
            <n-space vertical>
              <n-h2>
                Literal Search Result
              </n-h2>
              <n-list borderd>
                <n-list-item v-for="item in literal_items" :key="item.id">
                  <n-thing>
                    <template #header>
                      {{item.name}}
                    </template>
                    <template #description>
                      {{item.description}}
                    </template>
                  </n-thing>
                </n-list-item>
              </n-list>
            </n-space>
          </n-grid-item>
          <n-grid-item>
            <n-space vertical>
              <n-h2>
                Conceptual Search Result
              </n-h2>
              <n-list borderd>
                <n-list-item v-for="item in concept_items" :key="item.id">
                  <n-thing>
                    <template #header>
                      {{item.name}}
                    </template>
                    <template #description>
                      {{item.description}}
                    </template>
                  </n-thing>
                </n-list-item>
              </n-list>
            </n-space>
          </n-grid-item>
        </n-grid>
      </n-layout>
    </n-layout>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { Search } from '@vicons/ionicons5'
import { mapState } from 'vuex'
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
      literal_items: [],
      concept_items: []
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
      const literalRes = await this.$http.post(this.loadLiteralUrl, paramObj)
      const conceptRes = await this.$http.post(this.loadConceptUrl, paramObj)
      const literalData = literalRes.data.data
      const conceptData = conceptRes.data.data
      this.literal_items = literalData
      this.concept_items = conceptData
      if (loadingMessage) {
        loadingMessage.destroy()
        loadingMessage = null
      }
      this.messageBox.success('thread info list loaded', { duration: 500 })
    }
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
    loadLiteralUrl () {
      return '/searchByLiteral/' + this.docName
    },
    loadConceptUrl () {
      return '/searchByConcept/' + this.docName
    },
    ...mapState({
      docName: 'doc_name'
    })
  }
})
</script>

<style scoped>
.search-home {
  text-align: center;
  background: url("../assets/HOMURA.jpg");
  width: 100%;
  height: 100%;
  background-size: cover;
}

#search-space {
  display: flex;
  justify-content: center;
}

#search-input {
  width: 450px;
  display: inline-block;
  margin-right: 20px;
}

</style>

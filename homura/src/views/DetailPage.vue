<template>
    <div id="detail-root-container">
      <n-grid :cols="3">
        <n-grid-item>
          <n-layout>
            <n-layout-content style="height:90vh; overflow: auto;">
              <n-list bordered>
                <n-list-item v-for="item in items" :key="item.Id">
                  <template #suffix>
                    <n-button @click="onViewClick(item)">view it</n-button>
                  </template>
                  <n-thing :title="item.Title" :description="item.Tags"></n-thing>
                </n-list-item>
              </n-list>
            </n-layout-content>
            <n-layout-footer style="height: 10vh; justify-content: center; display: flex; flex-direction: column;  align-items: center; ">
              <n-pagination v-model:page="page" :page-count="100"
              @update:page="updatePage"
              show-quick-jumper/>
            </n-layout-footer>
          </n-layout>
        </n-grid-item>
        <n-grid-item span = "2">
          <n-card class="pane-root-component"
            :title="threadTitle"
            :segmented="{content: 'soft'}"
            size="huge"
            :bordered="false"
            style="{width: 100%; height:100vh; overflow: auto;}">
            <div
              class="markdown-body"
              v-html="threadHtml">
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>
    </div>
</template>

<script>
import { defineComponent } from 'vue'
import { mapState } from 'vuex'
import { useMessage } from 'naive-ui'

let loadingMessage = null

export default defineComponent({
  data () {
    return {
      page: 1,
      items: [],
      messageBox: undefined,
      threadTitle: '',
      threadHtml: ''
    }
  },
  created () {
    const message = useMessage()
    this.messageBox = message
  },
  mounted () {
    this.loadThread()
  },
  methods: {
    async loadThread () {
      loadingMessage = this.messageBox.loading('loading thread info', { duration: 5000 })
      const paramObj = {
        apiId: this.current_api,
        page: this.page - 1,
        limit: 20
      }
      const res = await this.$http.get(this.loadUrl, {
        params: paramObj
      })
      const datas = res.data.data
      this.items = datas
      if (loadingMessage) {
        loadingMessage.destroy()
        loadingMessage = null
      }
      this.messageBox.success('thread info list loaded', { duration: 500 })
    },
    async loadThreadDetailHtml (threadId) {
      loadingMessage = this.messageBox.loading('loading thread', { duration: 5000 })
      const res = await this.$http.get(this.loadHtmlUrl, {
        params: {
          threadId: threadId
        }
      })
      const datas = res.data.data
      this.threadTitle = datas.title
      this.threadHtml = datas.html
      if (loadingMessage) {
        loadingMessage.destroy()
        loadingMessage = null
      }
      this.messageBox.success('thread loaded', { duration: 500 })
    },
    onViewClick (item) {
      debugger
      this.loadThreadDetailHtml(item.Id)
    },
    updatePage (page) {
      this.loadThread()
    }
  },
  computed: {
    loadUrl () {
      return '/getThreadInfo/' + this.docName
    },
    loadHtmlUrl () {
      return '/getThreadHtml/' + this.docName
    },
    ...mapState({
      current_api: 'current_show_detail_node',
      docName: 'doc_name'
    })
  }
})
</script>

<style>
#detail-root-container {
    width: 100%;
    height: 100%;
}
</style>

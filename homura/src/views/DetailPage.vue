<template>
    <div id="detail-root-container">
      <n-layout>
        <n-layout-header bordered id="detail-page-header">
          <n-space size="large" align="baseline">
            <n-h1>Discussions about <n-gradient-text type="info"> {{apiName}} </n-gradient-text></n-h1>
            <n-tooltip trigger="hover">
              <template #trigger>
                <n-button ghost circle size="small" @click="showModal = true"><n-icon size="20"><help-icon/></n-icon></n-button>
              </template>
              How to learn these threads?
            </n-tooltip>
          </n-space>
        </n-layout-header>
        <n-layout>
          <n-grid :cols="3">
            <n-grid-item>
              <n-layout>
                <n-layout style="height:86vh; overflow: auto;">
                  <n-list bordered>
                    <n-list-item v-for="item in items" :key="item.Id">
                      <template #suffix>
                        <n-button @click="onViewClick(item)">view it</n-button>
                      </template>
                      <n-thing :title="item.Title" :description="item.Tags"></n-thing>
                    </n-list-item>
                  </n-list>
                </n-layout>
                <n-layout-footer style="height: 7vh; justify-content: center; display: flex; flex-direction: column;  align-items: center; ">
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
                style="{width: 100%; height:93vh; overflow: auto;}">
                <div
                  class="markdown-body"
                  v-html="threadHtml">
                </div>
              </n-card>
            </n-grid-item>
          </n-grid>
        </n-layout>
      </n-layout>
      <n-modal v-model:show="showModal">
        <n-card style="width: 600px;" title="How to learn these threads?" :bordered="false" size="huge">
          <p>Once you select an API to learn its related Stack Overflow threads in the <n-gradient-text type="danger">Roadmap</n-gradient-text>, you will be navigated to this page. This page lists every SO thread which is related to the current API being learned. Feel free to learn these knowleges and paste something to your note! :-)</p>
        </n-card>
      </n-modal>
    </div>
</template>

<script>
import { defineComponent } from 'vue'
import { mapState } from 'vuex'
import { useMessage } from 'naive-ui'
import { Help as HelpIcon } from '@vicons/ionicons5'

let loadingMessage = null

export default defineComponent({
  data () {
    return {
      page: 1,
      items: [],
      messageBox: undefined,
      threadTitle: '',
      threadHtml: '',
      showModal: false
    }
  },
  components: {
    HelpIcon
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
      docName: 'doc_name',
      apiName: 'current_show_detail_api_name'
    })
  }
})
</script>

<style>
#detail-root-container {
    width: 100%;
    height: 100%;
}

#detail-page-header {
  height: 7vh;
  justify-content: center;
  display: flex;
  flex-direction: column;
  align-items: left;
  padding-top: 20px;
  padding-left: 25px;
}
</style>

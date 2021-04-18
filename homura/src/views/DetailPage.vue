<template>
    <div id="detail-root-container">
      <n-layout>
        <n-layout-header bordered id="detail-page-header">
          <n-space size="large" align="baseline">
            <n-h1 v-if="en">Discussions about <n-gradient-text type="info"> {{apiName}} </n-gradient-text></n-h1>
            <n-h1 v-else>有关<n-gradient-text type="info">{{apiName}}</n-gradient-text>，Stack Overflow上所有的讨论纪录</n-h1>
            <n-tooltip trigger="hover">
              <template #trigger>
                <n-button ghost circle size="small" @click="showModal = true"><n-icon size="20"><help-icon/></n-icon></n-button>
              </template>
              {{en?"How to learn these threads?":"这些讨论是什么"}}
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
        <n-card style="width: 600px;" :title="en ? 'How to learn these threads?' : '这些讨论是干什么的？'" :bordered="false" size="huge">
          <p v-if="en">Once you select an API to learn its related Stack Overflow threads in the <n-gradient-text type="danger">Roadmap</n-gradient-text>, you will be navigated to this page. This page lists every SO thread which is related to the current API being learned. Feel free to learn these knowleges and paste something to your note! :-)</p>
          <p v-else>当您在<n-gradient-text type="danger">路线图</n-gradient-text>页面选择学习某个API时，您就会被导航到本页面。本页面包含了所有有关当前学习API的讨论纪录。这些都是开发者们在真实开发过程中积累的API使用经验。希望能够在学习上帮到您，复制点什么到你的note吧！:-)</p>
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
  activated () {
    this.loadThread()
  },
  methods: {
    async loadThread () {
      loadingMessage = this.messageBox.loading('loading thread info', { duration: 5000 })
      let res = {}
      console.log(this.show_detail_mode)
      if (this.show_detail_mode) {
        const paramObj = {
          apiId: this.current_api,
          page: this.page - 1,
          limit: 20
        }
        res = await this.$http.get(this.loadUrl, {
          params: paramObj
        })
      } else {
        const paramObj = {
          threads: this.current_threads,
          page: this.page - 1,
          limit: 10
        }
        res = await this.$http.post(this.acquireUril, paramObj)
      }
      debugger
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
    acquireUril () {
      return '/acquireThreadInfos/' + this.docName
    },
    loadHtmlUrl () {
      return '/getThreadHtml/' + this.docName
    },
    ...mapState({
      current_api: 'current_show_detail_node',
      docName: 'doc_name',
      apiName: 'current_show_detail_api_name',
      show_detail_mode: 'show_current_detail_node',
      current_threads: 'current_show_detail_threads',
      en: 'en'
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

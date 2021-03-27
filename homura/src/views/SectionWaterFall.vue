<template>
  <n-layout>
    <n-layout-header bordered id="header">
      <n-space id="head-space" size="large" align="baseline">
        <n-h1>Exploring Learning Entries</n-h1>
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button ghost circle size="small" @click="showModal = true"><n-icon size="20"><help-icon/></n-icon></n-button>
          </template>
          What is learning entry?
        </n-tooltip>
      </n-space>
    </n-layout-header>
    <n-layout style="height: 93vh;">
      <div class="waterfall-container" @scroll="handleScroll">
        <n-modal v-model:show="showModal">
          <n-card style="width: 600px;" title="What is learning entry?" :bordered="false" size="huge">
            内容
            <template #footer> 尾部 </template>
          </n-card>
        </n-modal>
        <div class="waterfall-content">
          <div class="piping" ref="piping0">
          </div>
          <div class="piping" ref="piping1">
          </div>
          <div class="piping" ref="piping2">
          </div>
          <div class="piping" ref="piping3">
          </div>
        </div>
      </div>
    </n-layout>
  </n-layout>
</template>

<script>
import { defineComponent, createApp } from 'vue'
import SectionCard from './SectionCard'
import store from '../store'
import router from '../router'
import { useMessage } from 'naive-ui'
import { Help as HelpIcon } from '@vicons/ionicons5'
import { mapState } from 'vuex'

const loadLimit = 20
let WFmaxContentHeight = 0
let loadingMessage = null

export default defineComponent({
  data () {
    return {
      loadEnabled: true,
      currentPage: 0,
      loadOver: false,
      messageBox: undefined,
      showModal: false
    }
  },
  components: {
    HelpIcon
  },
  async created () {
    const message = useMessage()
    this.messageBox = message
    loadingMessage = message.loading('loading learning entry data', { duration: 5000 })
    await this.fetchSections()
  },
  methods: {
    async fetchSections () {
      const that = this
      const limit = loadLimit
      const url = this.loadUrl
      const res = await this.$http.get(url,
        {
          params: {
            page: this.currentPage ? this.currentPage : 0,
            limit: limit
          }
        })
      const datas = res.data.data
      if (datas.length === 0) {
        this.loadOver = true
        this.currentPage--
        return
      }
      datas.forEach((data, i) => {
        const arr = [
          that.$refs.piping0.offsetHeight,
          that.$refs.piping1.offsetHeight,
          that.$refs.piping2.offsetHeight,
          that.$refs.piping3.offsetHeight
        ]
        const min = arr.indexOf(Math.min.apply(Math, arr))
        const app = createApp(SectionCard, {
          id: data.section_id,
          apis: data.apis,
          threadTitle: data.thread_info.Title
        }).use(store).use(router)
        const appHost = document.createElement('div')
        this.$refs[`piping${min}`].appendChild(appHost)
        app.mount(appHost)
      })
      if (loadingMessage) {
        loadingMessage.destroy()
        loadingMessage = null
      }
      this.messageBox.success('learning entry data loaded', { duration: 500 })
    },
    handleScroll (e) {
      // scrollTop + offsetHeight = scrollHeight
      // if (this.loadOver) return
      const scrollContainer = e.currentTarget
      if (scrollContainer.scrollHeight > WFmaxContentHeight + 10) {
        WFmaxContentHeight = scrollContainer.scrollHeight
        this.loadEnabled = true
      }
      if (scrollContainer.scrollTop + scrollContainer.offsetHeight >= scrollContainer.scrollHeight - 10 && this.loadEnabled) {
        this.currentPage++
        this.loadEnabled = false
        this.fetchSections()
      }
    }
  },
  computed: {
    loadUrl () {
      return '/getLearnSections/' + this.docName
    },
    ...mapState({
      docName: 'doc_name'
    })
  }
})
</script>

<style>
.waterfall-container {
  height: 100%;
  overflow: auto;
  display: flex;
  justify-content: center;
}

.waterfall-content {
  margin: auto;
  width: 1240px;
  display: flex;
  align-items: flex-start;
}

.waterfall-content .piping {
  width: 25%;
  padding: 10px;
  padding-bottom: 0px;
}

.card {
  padding: 10px;
  word-break: break-all;
  width: 290px;
  border-radius: 5px;
  box-shadow: 0px 0px 5px #888888;
  margin-bottom: 20px;
}

.section-id {
  text-align: center;
}

#header {
  height: 7vh;
  justify-content: center;
  display: flex;
  flex-direction: column;
  align-items: left;
  padding-top: 20px;
  padding-left: 25px;
}

</style>

<template>
  <n-layout>
    <n-layout-header bordered id="header">
      <n-space id="head-space" size="large" align="baseline">
        <n-h1>{{en?"Exploring Learning Entries":"学习入口推荐"}}</n-h1>
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button ghost circle size="small" @click="showModal = true"><n-icon size="20"><help-icon/></n-icon></n-button>
          </template>
          {{en?"What is a learning entry?":"什么是学习入口？"}}
        </n-tooltip>
      </n-space>
    </n-layout-header>
    <n-layout style="height: 93vh;">
      <div class="waterfall-container" @scroll="handleScroll">
        <n-modal v-model:show="showModal">
          <n-card style="width: 600px;" :title="en?'What is a learning entry?':'什么是学习入口？'" :bordered="false" size="huge">
            <p v-if="en">A learning entry is a set of APIs which we guess you may be interested in <n-gradient-text type="danger"> :) </n-gradient-text> This set of APIs are frequently discussed together in the <n-gradient-text type="danger"> Stack Overflow (SO) </n-gradient-text> due to our analysis on SO</p>
            <p v-else>一个学习入口是指一组我们推荐给您学习的java API<n-gradient-text type="danger"> :-) </n-gradient-text> 我们通过分析<n-gradient-text type="danger"> Stack Overflow (SO) </n-gradient-text>中关于API的讨论纪录为您推荐这些API，确保一组学习入口中的API是常用的、且彼此之间有着密切关系（经常被拿来在一起讨论）的。</p>
            <p v-if="en">If you are a start learner, who don't know where to start learning this <n-gradient-text type="danger">HUGE AMOUNT</n-gradient-text> of APIS. You can view these learning entries as your please and find a learning entry to start viewing these APIs</p>
            <p v-else>如果您是个java初学者，面对javadoc中数量庞大的API、不知道从哪开始学起，您可以尝试看看这些学习入口中为您推荐的API</p>
            <p v-if="en">However, viewing API names may not give you a deep impression about what these APIs are exactly talking about. Therefore, we append every learning entry a set of <n-gradient-text type="danger">popular questions</n-gradient-text> from SO that talk about these APIs, which could give you a better view. Hopeing these popular questions can help you find your interest better :)</p>
            <p v-else>为了让初学者也能一眼就看出来每个学习入口中的API主要是干什么用的，我们为每个学习入口打上了<n-gradient-text type="danger">主题标签</n-gradient-text>、来展示和这组API最相关的一些主题词汇，同时也附加了一个在SO社区中对这些API进行讨论的颇具代表性的问题。希望能够帮您快速开始 :-)</p>
            <n-gradient-text :size="24" type="danger">{{en?"BE AWARE":"注意事项"}}</n-gradient-text>
            <p v-if="en">If you are an experienced developer about this SDK, you may refer to the <n-gradient-text type="danger">search feature</n-gradient-text> we provided in <router-link class="link" to="/roadmap"><n-gradient-text type="info">here</n-gradient-text></router-link>.</p>
            <p v-else>如果您觉得这些API您都会的不行，您可能已经是个有点基础的学习者了，您可以尝试我们提供的<router-link class="link" to="/roadmap"><n-gradient-text type="info">搜索功能</n-gradient-text></router-link>来找找看和自己感兴趣主题相关的API。</p>
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
import { defineComponent, createApp, h } from 'vue'
import SectionCard from './SectionCard'
import store from '../store'
import router from '../router'
import { useMessage, useNotification, NAvatar } from 'naive-ui'
import { Help as HelpIcon } from '@vicons/ionicons5'
import { mapState } from 'vuex'

const loadLimit = 20
let WFmaxContentHeight = 0
let loadingMessage = null
let showed = false

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
  mounted () {
    const notification = useNotification()
    if (!showed) {
      showed = true
      notification.create({
        title: this.en ? 'Hint' : '提示',
        description: this.en ? 'About The Learning Entries' : '有关于学习入口的说明',
        content: this.en
          ? `A Learning Entries is a set of APIs which we guess you may be interested in.
  This set of APIs are frequently discussed together in the Stack Overflow (SO) Community, which means they have close relationships.
  Through these entries, you can have a quick start and get a knowledge of how the SDK is used in the real development environment.
  Watch detail through the left Help button :-)
        `
          : `学习入口是指一组我们向初学者的您推荐、您可能会乐于学习的一组API。
我们分析了每个API在Stack Overflow中的讨论纪录，确保向您推荐的API是常用的、并且彼此之间有着紧密的联系。
通过这些学习入口，您可以在初学阶段快速寻找您的学习目标，并得到尽可能多有关实际开发时使用API的知识。
您可以使用左侧的"?"按钮来查看详细说明 :-)
        `,
        avatar: () =>
          h(NAvatar, {
            size: 'small',
            round: true,
            src: 'https://07akioni.oss-cn-beijing.aliyuncs.com/07akioni.jpeg'
          })
      })
    }
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
          threadTitle: data.thread_info.Title,
          tags: data.tags
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
      docName: 'doc_name',
      en: 'en'
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

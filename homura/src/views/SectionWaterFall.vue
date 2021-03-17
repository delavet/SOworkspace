<template>
  <div class="waterfall-container" @scroll="handleScroll">
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
</template>

<script>
import { defineComponent, createApp } from 'vue'
import SectionCard from './SectionCard'
import store from '../store'

const loadLimit = 20
let WFmaxContentHeight = 0

export default defineComponent({
  data () {
    return {
      loadEnabled: true,
      currentPage: 0,
      loadOver: false,
      docName: 'javadoc'
    }
  },
  async created () {
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
        }).use(store)
        // let html =
        // `<div class="card">
        //   <h2 class="section-id"> Section` + data.section_id + `</h2>
        //   <h4> Related APIs:</h4>
        //   <ul>`
        // for (let j = 0; j < data.apis.length; j++) {
        //   html += '<li>' + data.apis[j] + '</li>'
        // }
        // html += `</ul>
        //   <h4> Popular threads:</h4>
        //   <div>` + data.thread_info.Title + `</div>
        // `
        // html += '</div>'
        const appHost = document.createElement('div')
        this.$refs[`piping${min}`].appendChild(appHost)
        app.mount(appHost)
      })
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
    }
  }
})
</script>

<style>
.waterfall-container {
  height: 100vh;
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

</style>

<template>
  <n-card class="pane-root-component"
    :title="apiName"
    :segmented="{content: 'soft', action: 'hard'}"
    size="huge"
    :bordered="false"
    style="{max-width:708px; word-break: break-all;}">
    <template #header-extra>
      <n-space style="{margin: 10px;}">
        <n-tooltip placement="top-start" trigger="hover">
          <template #trigger>
            <n-button circle type="primary" @click="onClick">
              <template #icon>
                <n-icon><book-icon /></n-icon>
              </template>
            </n-button>
          </template>
          {{en?"Learn about all SO threads talking about this API":"学习Stack Overflow上有关此API的讨论纪录"}}
        </n-tooltip>
        <n-tooltip placement="top-start" trigger="hover">
          <template #trigger>
            <n-button circle type="info" @click="onClick2">
              <template #icon>
                <n-icon><navi-icon /></n-icon>
              </template>
            </n-button>
          </template>
          {{en?"Show relationships and related APIs around this API":"将此API重新设为中心，查看与它关系密切的API以及它们之间的关系"}}
        </n-tooltip>
      </n-space>
    </template>
    <div
      ref="descriptionContent"
      id="description-content"
      class="markdown-body"
      v-html="apiHtml">
    </div>
    <!--template #action>
      <n-space>
        <n-button type="info" round size="large">learn details</n-button>
        <n-button type="primary" round size="large">show submap</n-button>
      </n-space>
    </-template-->
  </n-card>
</template>

<script>
import { defineComponent } from 'vue'
import { mapState, mapMutations } from 'vuex'
import { BookOutline as BookIcon, NavigateOutline as NaviIcon } from '@vicons/ionicons5'

export default defineComponent({
  name: 'APIDetailPane',
  components: {
    BookIcon,
    NaviIcon
  },
  data () {
    return {
      showSpin: false,
      apiHtml: '',
      apiName: ''
    }
  },
  watch: {
    current_show_detail_node: async function (val, oldVal) {
      if (val === '') return
      this.showSpin = true
      console.log('watching ' + val)
      const res = await this.$http.get(this.loadUrl, {
        params: {
          apiId: val
        }
      })
      const apiDescriptionData = res.data.data
      this.apiName = apiDescriptionData.api_name
      this.apiHtml = `
        ${apiDescriptionData.api_html}
      `
      this.showSpin = false
    }
  },
  methods: {
    onClick () {
      this.set_api_name(this.apiName)
      this.$emit('show-threads')
    },
    onClick2 () {
      this.set_center_node(this.current_show_detail_node)
      this.$emit('show-extend-submap')
    },
    ...mapMutations({
      set_api_name: 'set_show_detail_api_name',
      set_center_node: 'set_current_center_node'
    })
  },
  computed: {
    loadUrl () {
      return '/getAPIDescription/' + this.docName
    },
    ...mapState({
      current_show_detail_node: 'current_show_detail_node',
      docName: 'doc_name',
      en: 'en'
    })
  }
})
</script>

<style scoped>

.pane-root-component {
  height: 100%;
}

#decription-content {
  margin: 10px;
  overflow: scroll;
}
</style>

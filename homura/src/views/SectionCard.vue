<template>
  <n-card style="margin-bottom: 16px;" class="section-card" @click="handleClick">
    <template #header>
      {{en ? "Section" : "学习入口：编号"}} {{ id }}
    </template>
    <n-h4>{{en ? "Related API" : "包含API概览"}}</n-h4>
    <n-text code v-for="api in apis" :key="api" style="white-space: normal; word-break: break-all; margin-bottom: 6px;">{{ api }}</n-text>
    <n-h4>{{en ? "Tags" : "标签"}} </n-h4>
    <n-space >
      <n-tag v-for="tag in tags" :key="tag" type="info">{{tag}}</n-tag>
    </n-space>
    <n-h4>{{en ? "Popular Discussion" : "有关的代表性问题"}} </n-h4>
    {{ threadTitle }}
  </n-card>
</template>

<script>
import { defineComponent } from 'vue'
import { NCard, NH4, NText, NSpace, NTag } from 'naive-ui'
import { mapMutations, mapState } from 'vuex'

export default defineComponent({
  name: 'SectionCard',
  components: {
    NCard,
    NH4,
    NText,
    NSpace,
    NTag
  },
  props: {
    id: String,
    apis: Array,
    threadTitle: String,
    tags: Array
  },
  methods: {
    handleClick () {
      this.set_id(this.id)
      this.set_current_center_node('')
      this.set_show_map(true)
      this.update_map(true)
      this.$router.push('/roadmap')
    },
    ...mapMutations({
      set_id: 'set_current_section_id',
      set_show_map: 'set_map_show_mode',
      set_current_center_node: 'set_current_center_node',
      update_map: 'set_refresh_map'
    })
  },
  computed: {
    ...mapState({
      en: 'en'
    })
  }
})
</script>

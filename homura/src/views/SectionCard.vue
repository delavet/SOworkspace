<template>
  <n-card style="margin-bottom: 16px;" class="section-card" @click="handleClick">
    <template #header>
      Section {{ id }}
    </template>
    <n-h4>Related API</n-h4>
    <n-text code v-for="api in apis" :key="api" style="white-space: normal; word-break: break-all; margin-bottom: 6px;">{{ api }}</n-text>
    <n-h4>Tags</n-h4>
    <n-space v-for="tag in tags" :key="tag">
      <n-tag type="info">{{tag}}</n-tag>
    </n-space>
    <n-h4>Popular Discussion</n-h4>
    {{ threadTitle }}
  </n-card>
</template>

<script>
import { defineComponent } from 'vue'
import { NCard, NH4, NText, NSpace, NTag } from 'naive-ui'
import { mapMutations } from 'vuex'

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
      this.set_show_map(true)
      this.$router.push('/roadmap')
    },
    ...mapMutations({
      set_id: 'set_current_section_id',
      set_show_map: 'set_map_show_mode'
    })
  }
})
</script>

<template>
  <n-card style="margin-bottom: 16px;" class="section-card" @click="handleClick">
    <template #header>
      Section {{ id }}
    </template>
    <n-h4>Related API</n-h4>
    <n-text code v-for="api in apis" :key="api" style="white-space: normal; word-break: break-all; margin-bottom: 6px;">{{ api }}</n-text>
    <n-h4>Popular Thread</n-h4>
    {{ threadTitle }}
  </n-card>
</template>

<script>
import { defineComponent } from 'vue'
import { NCard, NH4, NText } from 'naive-ui'
import { mapMutations } from 'vuex'

export default defineComponent({
  name: 'SectionCard',
  components: {
    NCard,
    NH4,
    NText
  },
  props: {
    id: String,
    apis: Array,
    threadTitle: String
  },
  methods: {
    handleClick () {
      this.set_id(this.id)
    },
    ...mapMutations({
      set_id: 'set_current_section_id'
    })
  }
})
</script>

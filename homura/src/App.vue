<template>
  <n-layout style="height: 100vh;">
    <n-layout-sider
      style="z-index: 1;"
      bordered
      show-trigger
      collapse-mode="width"
      :collapsed-width="80"
      :width="280"
      :collapsed="collapsed"
      @collapse="collapsed = true"
      @expand="collapsed = false"
    >
      <n-menu
        :collapsed="collapsed"
        :collapsed-width="80"
        :collapsed-icon-size="36"
        :items="menuItems"
        @update:value="callback"
      />
    </n-layout-sider>
    <n-layout class="content" >
      <router-view />
    </n-layout>
  </n-layout>
</template>

<script>
import { defineComponent, h } from 'vue'
import { NIcon } from 'naive-ui'
import { mapActions, mapState } from 'vuex'
import {
  BookOutline as BookIcon
} from '@vicons/ionicons5'

function renderIcon (icon) {
  return () => h(NIcon, null, { default: () => h(icon) })
}

const menuItems = [
  {
    label: '且听风吟',
    key: 'hear-the-wind-sing',
    icon: renderIcon(BookIcon)
  },
  {
    label: '寻羊冒险记',
    key: 'a-wild-sheep-chase',
    disabled: true,
    icon: renderIcon(BookIcon)
  }
]

export default defineComponent({
  data () {
    return {
      collapsed: true,
      menuItems
    }
  },
  methods: {
    callback (value, item) {
      console.log(value, item)
      this.$router.push('/about')
    },
    handleScroll (e) {
      console.log(e.currentTarget)
      const scrollContainer = e.currentTarget
      console.log('scrollTop', scrollContainer.scrollTop)
      console.log('scrollHeight', scrollContainer.scrollHeight)
      console.log('offsetHeight', scrollContainer.offsetHeight)
    },
    ...mapActions({
      onCoolClick: 'hello_homura'
    })
  },
  computed: {
    ...mapState({
      coolButtonText: 'hello'
    })
  }
})
</script>

<style>
</style>

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
        @update:value="menuCallback"
      />
    </n-layout-sider>
    <n-layout class="app-content">
      <n-message-provider>
        <router-view />
      </n-message-provider>
    </n-layout>
  </n-layout>
</template>

<script>
import { defineComponent, h } from 'vue'
import { NIcon } from 'naive-ui'
import { mapActions, mapState } from 'vuex'
import {
  Home as HomeIcon,
  Bulb as BulbIcon,
  Map as MapIcon
} from '@vicons/ionicons5'

function renderIcon (icon) {
  return () => h(NIcon, null, { default: () => h(icon) })
}

const menuItems = [
  {
    label: 'Home Page',
    key: 'home',
    icon: renderIcon(HomeIcon)
  },
  {
    label: 'Learning Entries',
    key: 'section',
    icon: renderIcon(BulbIcon)
  },
  {
    label: 'Learning Roadmap',
    key: 'roadmap',
    icon: renderIcon(MapIcon)
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
    menuCallback (value, item) {
      if (value === 'home') {
        this.$router.push('/')
      } else if (value === 'section') {
        this.$router.push('/section')
      } else if (value === 'roadmap') {
        this.$router.push('/roadmap')
      }
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

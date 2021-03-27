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
          <n-notification-provider>
            <router-view />
          </n-notification-provider>
        </n-message-provider>
    </n-layout>
  </n-layout>
</template>

<script>
import { defineComponent, h } from 'vue'
import { NIcon } from 'naive-ui'
import { mapActions, mapState } from 'vuex'
import {
  HomeOutline as HomeIcon,
  BulbOutline as BulbIcon,
  MapOutline as MapIcon,
  BookOutline as BookIcon,
  SearchOutline as SearchIcon
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
    label: 'Search Page',
    key: 'search',
    icon: renderIcon(SearchIcon)
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
  },
  {
    label: 'view SO threads about API',
    key: 'detail',
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
    menuCallback (value, item) {
      if (value === 'home') {
        this.$router.push('/')
      } else if (value === 'search') {
        this.$router.push('/search')
      } else if (value === 'section') {
        this.$router.push('/section')
      } else if (value === 'roadmap') {
        this.$router.push('/roadmap')
      } else if (value === 'detail') {
        this.$router.push('/detail')
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

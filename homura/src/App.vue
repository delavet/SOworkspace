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
    <n-layout class="content">
      <div id="nav">
        <n-button @click="onCoolClick">{{coolButtonText}}</n-button>
        <router-link to="/">Home</router-link> |
        <router-link to="/about">About</router-link>
      </div>
      <router-view/>
    </n-layout>
  </n-layout>
</template>

<script>
import { defineComponent, h } from 'vue'
import { NIcon } from 'naive-ui'
import { mapActions, mapState } from 'vuex'
import {
  BookOutline as BookIcon,
  PersonOutline as PersonIcon,
  WineOutline as WineIcon
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
    label: '1973年的弹珠玩具',
    key: 'pinball-1973',
    icon: renderIcon(BookIcon),
    disabled: true,
    children: [
      {
        label: '鼠',
        key: 'rat'
      }
    ]
  },
  {
    label: '寻羊冒险记',
    key: 'a-wild-sheep-chase',
    disabled: true,
    icon: renderIcon(BookIcon)
  },
  {
    label: '舞，舞，舞',
    key: 'dance-dance-dance',
    icon: renderIcon(BookIcon),
    children: [
      {
        type: 'group',
        label: '人物',
        key: 'people',
        children: [
          {
            label: '叙事者',
            key: 'narrator',
            icon: renderIcon(PersonIcon)
          },
          {
            label: '羊男',
            key: 'sheep-man',
            icon: renderIcon(PersonIcon)
          }
        ]
      },
      {
        label: '饮品',
        key: 'beverage',
        icon: renderIcon(WineIcon),
        children: [
          {
            label: '威士忌',
            key: 'whisky'
          }
        ]
      },
      {
        label: '食物',
        key: 'food',
        children: [
          {
            label: '三明治',
            key: 'sandwich'
          }
        ]
      },
      {
        label: '过去增多，未来减少',
        key: 'the-past-increases-the-future-recedes'
      }
    ]
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
    ...mapActions({
      onCoolClick: 'hello_homura'
    })
  },
  computed: {
    ...mapState({
      coolButtonText: 'hello_world'
    })
  }
})
</script>

<style>
#nav{
  padding: 24px;
}
.content{
  padding: 24px;
}
</style>

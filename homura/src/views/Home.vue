<template>
  <div class="home">
    <n-tooltip trigger="hover">
      <template #trigger>
        <n-button ghost circle size="small" @click="showModal = true" id="home-help-btn"><n-icon size="15"><help-icon/></n-icon></n-button>
      </template>
      {{en? "How can this service help me learn java APIs?": "这东西如何帮助我学习java API？"}}
    </n-tooltip>
    <n-dropdown @select="handleLangSelect" trigger="click" :options="langOptions">
      <n-button :keyboard="false" id="lang-choose">{{en?"choose language":"选择语言"}}</n-button>
    </n-dropdown>
    <n-space vertical>
      <h1
        id="project-name"
        ref="name"
        @mouseenter="projectNameMouseEnter"
        @mouseleave="projectNameMouseLeave">
        PROJECT {{heroine}}
      </h1>
      <n-h6>{{en?"A":"一个"}} JAVADOC API {{en?" learning assistant system ":"学习助手服务"}}</n-h6>
      <p id="section-nav" class="home-p">{{en?"Start learn! From recommended ":"如果你是小白、不知从哪开始学，可以看看我们推荐的"}}<router-link class="link" to="/section"><n-gradient-text type="info">{{en?"learning entries":"学习入口"}}
</n-gradient-text></router-link></p>
      <h2 class="home-h">{{en?"OR":"如果你想自己看看"}}</h2>
      <p class="home-p">{{en?"":"可以用任何你想到的词来"}}<router-link class="link" to="/search"><n-gradient-text type="info">{{en?"Search APIs":"搜索API"}}</n-gradient-text></router-link>{{en?" you're interested in":""}}</p>
      <!--div id="search-space">
        <n-auto-complete
          id="search-input"
          :options="searchOptions"
          v-model:value="searchValue"
          size="large"
          placeholder="input any word you think out, we will complete the rest :-)"
        />
        <n-button circle @click="onSearchClick">
          <template #icon>
            <n-icon><search /></n-icon>
          </template>
        </n-button>
      </div!-->
    </n-space>
    <n-modal v-model:show="showModal">
      <n-card style="max-width: 1200px;" :title="en?'How to use this service to learn java API':'我怎么用这个服务学习java API？'" :bordered="false" size="huge">
        <n-steps :current="current" status="process">
          <n-step :title="en?'Find an API to learn':'首先寻找要学习的API'">
            <div class="n-step-description">
              <p v-if="en">Choose one API to start your learn journey~ If you are a complete novice, don't know where to start, you can browse some popular <router-link class="link" to="/section"><n-gradient-text type="info">Learning Entries</n-gradient-text></router-link> we prepare for you and find out what you interested in.</p>
              <p v-else>万事开头难！要学习API文档中的海量API，第一步就必须要先选择几个API来学起来。如果你真的是个新手，觉得API太多头大、不知从哪开始，不妨看看我们推荐的<router-link class="link" to="/section"><n-gradient-text type="info">学习入口</n-gradient-text></router-link>；每个学习入口都包含几个API，这些API涉及java的不同主题、非常常用而且开发者们很关注它们。</p>
              <p v-if="en">Or, you can search for java APIs with any keywords you come up with in the <router-link class="link" to="/search"><n-gradient-text type="info">Search Page</n-gradient-text></router-link> to find out APIs which meet your need</p>
              <p v-else>或者如果你有一些java基础，想了解一下自己感兴趣的一些领域（比如网络通信、多线程、IO等），你可以访问我们的<router-link class="link" to="/search"><n-gradient-text type="info">搜索页面</n-gradient-text></router-link>。在这里可以用你想得到的各种关键词搜索到你可能有兴趣的API，保证比javadoc的搜索靠谱（大概</p>
              <n-button
                v-if="current === 1"
                @click="handleButtonClick"
              >
                {{en?"Next":"下一步"}}
              </n-button>
            </div>
          </n-step>
          <n-step :title="en?'Learn the API you choose in the Roadmap':'在路线图中学习你选择的API'">
            <div class="n-step-description">
              <p v-if="!en">API学习从来都不是单打独斗，实际开发中、往往需要配合使用一系列的API来完成你的编程任务。在学习中，围绕一个具体的主题、学习<n-gradient-text type="error">一组</n-gradient-text>关系密切的API、理解它们之间的关系、往往效率更高。</p>
              <p v-if="en">The API you choose in the first step are set as the center API of our <router-link class="link" to="/roadmap"><n-gradient-text type="info">Roadmap</n-gradient-text></router-link>. Through the Roadmap, you can browse the relationships between the API you choose and all other APIs which are related to it. You can also navigate in the Roadmap to continue learning other related APIs. <router-link class="link" to="/roadmap"><n-gradient-text type="info">Check it Out!</n-gradient-text></router-link></p>
              <p v-else>我们的服务使用<router-link class="link" to="/roadmap"><n-gradient-text type="info">API路线图</n-gradient-text></router-link>来帮你快速找到和所选API关系密切的一系列API。API路线图是一张以图结构组织起来的API的网，图中的结点就是各个API，结点间以边相连，边上标注了API之间的关系。通过路线图，你能够浏览所有API之间的关系、轻易找出应该重点学习的API，并在路线图上规划自己的学习路径。</p>
              <n-button
                v-if="current === 2"
                @click="handleButtonClick"
              >
                {{en?"Next":"下一步"}}
              </n-button>
            </div>
          </n-step>
          <n-step :title="en?'Learn Stack Overflow threads about the API':'在最著名的开发者社区Stack Overflow中学习API知识！'">
            <div class="n-step-description">
              <p v-if="en">While navigating in the Roadmap,you can further browse popular Stack Overflow threads which are talking about the current API you learn. These valuable threads can help you better learn the API in the real development scenario. Good Luck. :-) <router-link class="link" to="/detail"><n-gradient-text type="info">Try it out</n-gradient-text></router-link></p>
              <p v-else>Stack Overflow是世界最知名的开发者Q&A社区，其中包含了大量开发者针对API在实际开发场景下的讨论，有很大的学习价值。对每个API，我们都收集了几乎全部在Stack Overflow社区中对其进行的讨论，您可以在通过路线图查看API的同时对所有该API相关的讨论进行学习。相信这对你了解API的使用方法有很大帮助，祝你好运！:-)</p>
              <n-button
                v-if="current === 3"
                @click="handleButtonClick"
              >
                {{en?"Understand":"明白了"}}
              </n-button>
            </div>
          </n-step>
        </n-steps>
      </n-card>
    </n-modal>
  </div>
</template>

<script>
// @ is an alias to /src
import { defineComponent } from 'vue'
import { mapState, mapMutations } from 'vuex'
import { Help as HelpIcon } from '@vicons/ionicons5'

let showed = false

export default defineComponent({
  name: 'Home',
  components: {
    HelpIcon
  },
  data () {
    return {
      searchValue: '',
      heroine: 'HOMURA',
      current: 1,
      showModal: false,
      langOptions: [
        {
          label: '中文',
          key: 'zh'
        },
        {
          label: 'English',
          key: 'en'
        }
      ]
    }
  },
  mounted () {
    if (!showed) {
      showed = true
      this.showModal = true
    }
  },
  methods: {
    handleLangSelect (key) {
      this.set_language(key)
    },
    projectNameMouseEnter () {
      this.heroine = this.en ? 'HIKARI' : '光'
      this.$refs.name.style.color = '#FCA04C'
    },
    projectNameMouseLeave () {
      this.heroine = this.en ? 'HOMURA' : '焰'
      this.$refs.name.style.color = '#F1394B'
    },
    handleButtonClick () {
      if (this.current === 3) {
        this.showModal = false
      } else {
        this.current = (this.current % 3) + 1
      }
    },
    ...mapMutations({
      set_language: 'set_language'
    })
  },
  computed: {
    searchOptions () {
      return ['没做完', '是真的', '别想了'].map((suffix) => {
        const prefix = this.searchValue.split('@')[0]
        return {
          label: prefix + suffix,
          value: prefix + suffix
        }
      })
    },
    ...mapState({
      en: 'en'
    })
  }
})
</script>

<style scope>
.home {
  text-align: center;
  background: url("../assets/HOMURA.jpg");
  width: 100%;
  height: 100%;
  background-size: cover;
}

#project-name {
  margin-top: 50px;
  color: #F1394B;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  font-weight: 900;
  font-size: 500%;
}

#section-nav .link {
  font-weight: bold;
  color: #2c3e50;
}

#section-nav a.router-link-exact-active {
  color: #42b983;
}

#search-space {
  display: flex;
  justify-content: center;
}

#search-input {
  width: 450px;
  display: inline-block;
  margin-right: 20px;
}

#home-help-btn {
  position: absolute;
  top: 0;
  left: 0;
  margin: 20px;
}

#lang-choose {
  position: absolute;
  top: 0;
  right: 0;
  margin: 20px;
}

.home-p {
  font-size: x-large;
  font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  font-weight: bolder;
}

.home-h {
  font-size: xx-large;
  font-weight: 900;
}
</style>

<template>
  <div class="home">
    <n-tooltip trigger="hover">
      <template #trigger>
        <n-button ghost circle size="small" @click="showModal = true" id="home-help-btn"><n-icon size="15"><help-icon/></n-icon></n-button>
      </template>
      What are these maps?
    </n-tooltip>
    <n-space vertical>
      <h1
        id="project-name"
        ref="name"
        @mouseenter="projectNameMouseEnter"
        @mouseleave="projectNameMouseLeave">
        PROJECT {{heroine}}
      </h1>
      <n-h6>A <n-gradient-text type="warning"> JAVADOC </n-gradient-text> API <n-gradient-text type="success"> learning assistant system </n-gradient-text></n-h6>
      <p id="section-nav" class="home-p">Start learn! From recommended <router-link class="link" to="/section"><n-gradient-text type="info">learning entries</n-gradient-text></router-link></p>
      <h2 class="home-h">OR</h2>
      <p class="home-p"><router-link class="link" to="/search"><n-gradient-text type="info">Search APIs</n-gradient-text></router-link> you're interested in</p>
      <div id="search-space">
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
      </div>
    </n-space>
    <n-modal v-model:show="showModal">
      <n-card style="max-width: 1200px; height:400px;" title="How to use this service?" :bordered="false" size="huge">
        <n-steps :current="current" status="process">
          <n-step title="Find an API to learn">
            <div class="n-step-description">
              <p>Choose one API to start your learn journey~ If you are a complete novice, don't know where to start, you can browse some popular <router-link class="link" to="/section"><n-gradient-text type="info">Learning Entries</n-gradient-text></router-link> we prepare for you and find out what you interested in.</p>
              <p>Or, you can search for java APIs with any keywords you come up with in the <router-link class="link" to="/search"><n-gradient-text type="info">Search Page</n-gradient-text></router-link> to find out APIs which meet your need</p>
              <n-button
                v-if="current === 1"
                @click="handleButtonClick"
              >
                Next
              </n-button>
            </div>
          </n-step>
          <n-step title="Learn the API you choose in the Roadmap">
            <div class="n-step-description">
              <p>The API you choose in the first step are set as the center API of our <router-link class="link" to="/roadmap"><n-gradient-text type="info">Roadmap</n-gradient-text></router-link>. Through the Roadmap, you can browse the relationships between the API you choose and all other APIs which are related to it. You can also navigate in the Roadmap to continue learning other related APIs. <router-link class="link" to="/roadmap"><n-gradient-text type="info">Check it Out!</n-gradient-text></router-link></p>
              <n-button
                v-if="current === 2"
                @click="handleButtonClick"
              >
                Next
              </n-button>
            </div>
          </n-step>
          <n-step title="Learn Stack Overflow threads about the API">
            <div class="n-step-description">
              <p>While navigating in the Roadmap,you can further browse popular Stack Overflow threads which are talking about the current API you learn. These valuable threads can help you better learn the API in the real development scenario. Good Luck. :-) <router-link class="link" to="/detail"><n-gradient-text type="info">Try it out</n-gradient-text></router-link></p>
              <n-button
                v-if="current === 3"
                @click="handleButtonClick"
              >
                Next
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
import { Search, Help as HelpIcon } from '@vicons/ionicons5'

export default defineComponent({
  name: 'Home',
  components: {
    Search,
    HelpIcon
  },
  data () {
    return {
      searchValue: '',
      heroine: 'HOMURA',
      current: 1,
      showModal: true
    }
  },
  methods: {
    onSearchClick () {

    },
    projectNameMouseEnter () {
      this.heroine = 'HIKARI'
      this.$refs.name.style.color = '#FCA04C'
    },
    projectNameMouseLeave () {
      this.heroine = 'HOMURA'
      this.$refs.name.style.color = '#F1394B'
    },
    handleButtonClick () {
      this.current = (this.current % 3) + 1
    }
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
    }
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

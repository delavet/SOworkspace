<template>
  <div class="home">
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
      <p class="home-p">Search APIs you're interested in</p>
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
  </div>
</template>

<script>
// @ is an alias to /src
import { defineComponent } from 'vue'
import { Search } from '@vicons/ionicons5'

export default defineComponent({
  name: 'Home',
  components: {
    Search
  },
  data () {
    return {
      searchValue: '',
      heroine: 'HOMURA'
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

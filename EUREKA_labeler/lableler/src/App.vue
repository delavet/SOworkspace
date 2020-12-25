<template>
  <div id="app" @mousedown="onAppMouseDown" @mouseup="onMouseUp">
    <div v-if="tokens && tokens.length > 0">
      <Token v-for="token in tokens" 
        :text="token.text"
        :key="token.index"
        :index="Number(token.index)"
        :flag="token.flag"
        @down="onMouseDown"
        @enter="onEnteringNewToken"/>
    </div>
    <!-- 否则，标签只是被初始化了，但是没有数据 -->
    <el-button 
      id="btn3"
      v-else-if="tokens"
      @click="handinDatasetClick"
    >没有数据了，交货了
    </el-button>
    <!-- 标签容器还没被初始化 -->
    <div v-else>数据加载中...</div>
    <div id="btn_father">
      <el-button v-if="tokens && tokens.length > 0" id="btn" @click="onClick">搞定了</el-button>
      <el-divider></el-divider>
      <el-row type="flex"
        class="row_bg">
        <el-col>
          <el-button
            id="btn_early_terminate"
            @click="handinDatasetClick"
          >爷不干了，吐了，提前收工了</el-button>
        </el-col>
        <el-col :span="1">
          <el-divider direction="vertical"></el-divider>
        </el-col>
        <el-col>爷要从第</el-col>
        <el-col>
          <el-input
            id="in"
            v-model="start_index_input"
            placeholder="1-1000"
          >
          </el-input>
        </el-col>
        <el-col>
          个开始标
        </el-col>
        <el-col><el-button
          id="btn_jump_through"
          @click="jumpThroughClick"
        >确认</el-button></el-col>

      </el-row>
      <el-divider></el-divider>
      <el-select  
        v-model="value"
        placeholder="请选择"
        :disabled="selectDisabled"
        @change="datasetChange">
        <el-option
          v-for="item in options"
          :key="item.value"
          :label="item.label"
          :value="item.value">
        </el-option>
      </el-select>
      <el-button id="btn2" @click="datasetSelected">选这个数据集标</el-button>
    </div>
  </div>
</template>

<script>
import Token from './components/Token.vue'
import { O, I, tag_types, parseData, generateDataBack, saveObject } from './util/Util'

var tracing = false;
var cur_dataset = undefined;
var cur_dataset_filename = undefined
var cur_dataset_length = 0
var cur_label_index = -1
var refined_dataset = undefined


export default {
  name: 'App',
  components: {
    Token
  },
  created() {
    for (let i = 0; i <= 62; i++) {
      this.options.push({
        label: `ner_data_${i}.json`,
        value: `ner_data_${i}.json`
      })
    }
    //this.$http.get('../static/ner_data_0.json')
    //this.tokens = parseData(data)
  },
  methods: {
    onAppMouseDown() {
      console.log("appmousedown")
      tracing = true
    },
    onMouseDown(token_index) {
      tracing = true
      console.log("mousedown")
      this.tokens[token_index].flag = 1 - this.tokens[token_index].flag
    },
    onMouseUp() {
      console.log("mouseup")
      tracing = false
    },
    onEnteringNewToken(token_index) {
      console.log("entering "+token_index)
      if (tracing) {
        this.tokens[token_index].flag = 1 - this.tokens[token_index].flag
      }
    },
    onClick() {
      refined_dataset.push(
        generateDataBack(this.tokens)
      )
      cur_label_index++
      if (cur_label_index >= cur_dataset_length) {
        this.tokens = []
      }
      else {
        this.tokens = parseData(cur_dataset[cur_label_index])
      }
      /*
      saveObject(
        generateDataBack(this.tokens),
        'test.json'
      )*/
    },
    datasetChange(value) {
      cur_dataset_filename = value
    },
    async datasetSelected() {
      this.selectDisabled = true
      
      let res = await this.$http.get(`/static/${cur_dataset_filename}`)
      cur_dataset = res.data
      refined_dataset = []
      cur_dataset_length = cur_dataset.length
      cur_label_index = 0
      this.tokens = parseData(cur_dataset[cur_label_index])
    }, 
    handinDatasetClick() {
      saveObject(refined_dataset, cur_dataset_filename)
      this.selectDisabled = false
      this.$alert(`本次标了${refined_dataset.length}个，太棒！`)
    },
    jumpThroughClick() {
      if (cur_dataset_length <= 0) return
      if (refined_dataset.length > 0) return
      if (this.start_index_input >= cur_dataset_length) {
        this.start_index_input = cur_dataset_length - 1
      }
      refined_dataset = []
      cur_label_index = this.start_index_input
      this.tokens = parseData(cur_dataset[cur_label_index])
    }
  },
  data() {
    return {
      tokens: undefined,
      options: [],
      selectDisabled : false,
      start_index_input : '1'
    }
  }
}
</script>

<style>
#app {
  align-content: center;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-top: 60px;
  padding: 30px;
}

#btn {
  margin-top: 30px;
  align-self: center;
}

#btn_father {
  text-align: center;
}

#in {
  width: auto;
  float: left;
}
</style>

<template>
  <div
    id="app"
    @mousedown="onAppMouseDown"
    @mouseup="onMouseUp"
  >
    <div v-if="tokens && tokens.length > 0">
      <Token
        v-for="token in tokens"
        :key="token.index"
        :text="token.text"
        :index="Number(token.index)"
        :flag="token.flag"
        @down="onMouseDown"
        @enter="onEnteringNewToken"
      />
    </div>
    <!-- 否则，标签只是被初始化了，但是没有数据 -->
    <el-button
      v-else-if="tokens"
      id="btn3"
      @click="handinDatasetClick"
    >
      没有数据了，交货了
    </el-button>
    <!-- 标签容器还没被初始化 -->
    <div v-else>
      数据加载中...
    </div>
    <div id="btn_father">
      <el-button
        v-if="tokens && tokens.length > 0"
        id="btn"
        @click="onClick"
      >
        搞定了,当前序号（从0开始）：<span v-text="cur_index"></span>
      </el-button>
      <el-divider />
      <div class="row">
        <el-button
          id="btn_early_terminate"
          @click="handinDatasetClick"
        >
          爷不干了，吐了，提前收工了
        </el-button>
        <div style="flex-grow: 1" />
        <span>爷要从第</span>
        <el-input
          id="in"
          v-model="start_index_input"
          placeholder="1-1000"
        />
        <span>个开始标</span>
        <el-button
          id="btn_jump_through"
          @click="jumpThroughClick"
        >
          确认
        </el-button>
      </div>
      <el-divider />
      <el-select
        v-model="value"
        placeholder="请选择"
        :disabled="selectDisabled"
        @change="datasetChange"
      >
        <el-option
          v-for="item in options"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-button
        id="btn2"
        @click="datasetSelected"
      >
        选这个数据集标
      </el-button>
    </div>
  </div>
</template>

<script>
import Token from "./components/Token.vue";
import {
  O,
  I,
  tag_types,
  parseData,
  generateDataBack,
  saveObject,
} from "./util/Util";

var tracing = false;
var cur_dataset = undefined;
var cur_dataset_filename = undefined;
var cur_dataset_length = 0;
var cur_label_index = 0;
var refined_dataset = undefined;
var unchanged_mentions = undefined;
var cur_label_stat = {
  initPoint: -1,
  start: -1,
  end: -1,
}

export default {
  name: "App",
  components: {
    Token,
  },
  data() {
    return {
      tokens: undefined,
      value: null,
      /*
      options: Array(63)
        .fill()
        .map((_, i) => ({
          label: `ner_data_${i}.json`,
          value: `ner_data_${i}.json`,
        })),*/
      options: [],
      selectDisabled: false,
      start_index_input: "1",
      cur_index: -1,
    };
  },
  created() {
    //this.$http.get('../static/ner_data_0.json')
    //this.tokens = parseData(data)
    const opt = require.context('../public/static', false, /.json$/).keys()
    for (let o of opt) {
      this.options.push({
        "label": o.slice(2),
        "value": o.slice(2)
      })
    }
  },
  methods: {
    onAppMouseDown() {
      //console.log("appmousedown");
      tracing = true;
    },
    onMouseDown(token_index) {
      tracing = true;
      //console.log("mousedown");
      cur_label_stat.initPoint = token_index;
      cur_label_stat.start = token_index;
      cur_label_stat.end = token_index;
      this.tokens[token_index].flag = 1 - this.tokens[token_index].flag;
    },
    onMouseUp() {
      //console.log("mouseup");
      cur_label_stat.initPoint = -1;
      cur_label_stat.start = -1;
      cur_label_stat.end = -1;
      tracing = false;
    },
    onEnteringNewToken(token_index) {
      
      //console.log("entering " + token_index);
      if (tracing) {
        if (cur_label_stat.initPoint == -1) {
          cur_label_stat.initPoint = token_index;
          cur_label_stat.start = token_index;
          cur_label_stat.end = token_index;
          this.tokens[token_index].flag = 1 - this.tokens[token_index].flag;
          return;
        }
        let new_start = token_index >= cur_label_stat.initPoint ? cur_label_stat.initPoint : token_index;
        let new_end = token_index >= cur_label_stat.initPoint ? token_index : cur_label_stat.initPoint;
        let new_is_positive = new_end != cur_label_stat.initPoint;
        let old_is_positive = cur_label_stat.end != cur_label_stat.initPoint;
        if (new_is_positive && old_is_positive) {
          for (let i = Math.max(new_end, cur_label_stat.end); i > Math.min(new_end, cur_label_stat.end); i--) {
            this.tokens[i].flag = 1 - this.tokens[i].flag;
          }
        }
        else if (new_is_positive && !old_is_positive) {
          for (let i = cur_label_stat.start; i < cur_label_stat.initPoint; i++) {
            this.tokens[i].flag = 1 - this.tokens[i].flag;
          }
          for (let i = cur_label_stat.initPoint + 1; i<= new_end; i++) {
            this.tokens[i].flag = 1 - this.tokens[i].flag;
          }
        }
        else if (!new_is_positive && old_is_positive) {
          for (let i = cur_label_stat.end; i > cur_label_stat.initPoint; i--) {
            this.tokens[i].flag = 1 - this.tokens[i].flag;
          }
          for (let i = cur_label_stat.initPoint - 1; i >= new_start; i--) {
            this.tokens[i].flag = 1 - this.tokens[i].flag;
          }
        }
        else if (!new_is_positive && !old_is_positive) {
          for (let i = Math.min(new_start, cur_label_stat.start); i < Math.max(new_start, cur_label_stat.start); i++) {
            this.tokens[i].flag = 1 - this.tokens[i].flag;
          }
        }
        cur_label_stat.start = new_start;
        cur_label_stat.end = new_end;
      }
    },
    onClick() {
      //debugger
      let new_data = generateDataBack(this.tokens);
      let new_apis = Object.keys(new_data['label']['api'])
      let old_apis = Object.keys(cur_dataset[cur_label_index]['label']['api'])
      let unchanged = new_apis.filter(x => old_apis.includes(x));
      unchanged_mentions.push(...unchanged)
      refined_dataset.push(new_data);
      cur_label_index++;
      this.cur_index = cur_label_index;
      if (cur_label_index >= cur_dataset_length) {
        this.tokens = [];
      } else {
        this.tokens = parseData(cur_dataset[cur_label_index]);
      }
      /*
      saveObject(
        generateDataBack(this.tokens),
        'test.json'
      )*/
    },
    datasetChange(value) {
      cur_dataset_filename = value;
    },
    async datasetSelected() {
      this.selectDisabled = true;
      let res = await this.$http.get(`/static/${cur_dataset_filename}`);
      cur_dataset = res.data;
      refined_dataset = [];
      unchanged_mentions = [];
      cur_dataset_length = cur_dataset.length;
      cur_label_index = 0;
      this.tokens = parseData(cur_dataset[cur_label_index]);
    },
    handinDatasetClick() {
      saveObject(refined_dataset, cur_dataset_filename);
      saveObject(Array.from(new Set(unchanged_mentions)), 'nel_gt_apis.json');
      this.selectDisabled = false;
      this.$alert(`本次标了${refined_dataset.length}个，太棒！`);
    },
    jumpThroughClick() {
      if (cur_dataset_length <= 0) return;
      if (refined_dataset.length > 0) return;
      if (this.start_index_input >= cur_dataset_length) {
        this.start_index_input = cur_dataset_length - 1;
      }
      refined_dataset = [];
      cur_label_index = this.start_index_input;
      this.tokens = parseData(cur_dataset[cur_label_index]);
    },
  },
};
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

.row {
  display: flex;
  align-items: center;
}

.row > * {
  flex: 0;
  white-space: nowrap;
}

.row > *:not(:first-child) {
  margin-left: 8px;
}
</style>

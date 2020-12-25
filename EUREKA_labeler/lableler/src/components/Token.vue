<!-- Token.vue -->
<template>
    <div class="token"
        @mousedown="onMouseDown"
        @mouseenter="onMouseEnter"
        >
        <el-tag 
            class="tag"
            :color="tag_types[flag]"
            >{{text}}</el-tag>
    </div>
</template>
<script>
import { O, I, parseData } from '../util/Util.js'

export default {
    name: "token",
    props: {
        index: Number,
        // 标签内容
        text: String,
        flag: Number
    },
    created() {
        this.tag_types = ["white", "#D6FFA5"]
    },
    methods: {
        onMouseDown() {
            this.$emit("down", this.index);
        },
        onMouseEnter() {
            this.$emit("enter", this.index);
        }
    }
}
</script>
<style scoped>
    .token {
        display: inline-block;
        padding: 0px;
        -webkit-user-select:none;
        -moz-user-select:none;
        -ms-user-select:none;
        user-select:none;
        
    }
    .tag {
        font-size: 150%;
        height: 30px;
        padding-left: 0px;
        padding-right: 0px;
        min-width: 8px;
        border-radius: 0px;
    }
    
</style>
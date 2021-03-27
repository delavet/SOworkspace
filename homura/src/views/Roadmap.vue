<template>
<div id="roadmap-root-container">
  <div id="roadmap-container"></div>
  <div id="api-detail-pane">
    <api-detail-pane @show-extend-submap="this.updateSubmap" @show-threads="this.showThreads"/>
  </div>
  <n-card id="bread-pane" size="small" hoverable=true :segmented="{action: 'hard'}">
    <n-breadcrumb>
      <n-breadcrumb-item v-for="item in items" :key="item.id" @click="onBreadClick(item)">
        <n-icon><api-icon/></n-icon>
        {{item.name}}
      </n-breadcrumb-item>
    </n-breadcrumb>
    <template #action>
      <n-space align="baseline" style="display:flex;">
        <n-button-group>
          <n-button ghost :disabled="!community" @click="onConceptBtnClick">
            Show Concept Map
          </n-button>
          <n-button ghost :disabled="community" @click="onCommunityBtnClick">
            Show Community Map
          </n-button>
        </n-button-group>
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button ghost circle size="small" @click="showModal = true"><n-icon size="15"><help-icon/></n-icon></n-button>
          </template>
          What are these maps?
        </n-tooltip>
      </n-space>
    </template>
  </n-card>
  <n-modal v-model:show="showModal">
    <n-card style="width: 600px;" title="What are these fxxking maps?" :bordered="false" size="huge">
      <p>A learning entry is a set of APIs which we guess you may be interested in <n-gradient-text type="danger"> :) </n-gradient-text> This set of APIs are frequently discussed together in the <n-gradient-text type="danger"> Stack Overflow (SO) </n-gradient-text> due to our analysis on SO</p>
      <p>If you are a start learner, who don't know where to start learning this <n-gradient-text type="danger">HUGE AMOUNT</n-gradient-text> of APIS. You can view these learning entries as your please and find a learning entry to start viewing these APIs</p>
      <p>However, viewing API names may not give you a deep impression about what these APIs are exactly talking about. Therefore, we append every learning entry a set of <n-gradient-text type="danger">popular questions</n-gradient-text> from SO that talk about these APIs, which could give you a better view. Hopeing these popular questions can help you find your interest better :)</p>
      <n-gradient-text :size="24" type="danger">BE AWARE</n-gradient-text>
      <p>If you are an experienced developer about this SDK, you may refer to the <n-gradient-text type="danger">search function</n-gradient-text> we provided in <router-link class="link" to="/roadmap"><n-gradient-text type="info">here</n-gradient-text></router-link>.</p>
    </n-card>
  </n-modal>
</div>
</template>

<script>
import { defineComponent, h } from 'vue'
import { mapMutations, mapState } from 'vuex'
import { ChevronForwardCircleOutline as ApiIcon, Help as HelpIcon } from '@vicons/ionicons5'
import { useNotification, useMessage, NAvatar } from 'naive-ui'
import ApiDetailPane from '../components/ApiDetailPane.vue'
import G6 from '@antv/g6'

let localCurrentGraph = null

export default defineComponent({
  name: 'Roadmap',
  components: {
    ApiDetailPane,
    ApiIcon,
    HelpIcon
  },
  data () {
    return {
      showDetail: false,
      items: [],
      selectedApiBreadIndex: 0,
      community: true,
      showModal: false
    }
  },
  mounted () {
    console.log('mounted')
    this.community = this.show_community_map
    debugger
    const message = useMessage()
    const notification = useNotification()
    notification.create({
      title: "Wouldn't it be Nice",
      description: 'From the Beach Boys',
      content: `Wouldn't it be nice if we were older
Then we wouldn't have to wait so long
And wouldn't it be nice to live together
In the kind of world where we belong
You know its gonna make it that much better
When we can say goodnight and stay together
Wouldn't it be nice if we could wake up
In the morning when the day is new
And after having spent the day together
Hold each other close the whole night through`,
      meta: '2019-5-27 15:11',
      avatar: () =>
        h(NAvatar, {
          size: 'small',
          round: true,
          src: 'https://07akioni.oss-cn-beijing.aliyuncs.com/07akioni.jpeg'
        }),
      onAfterLeave: () => {
        message.success("Wouldn't it be Nice")
      }
    })
    this.initGraph()
  },
  methods: {
    async getGraphData () {
      const paramObj = {}
      if (this.current_show_detail_node !== '') {
        paramObj.apiId = this.current_show_detail_node
      }
      if (this.current_section_id !== '') {
        paramObj.sectionId = this.current_section_id
      }
      console.log('requesting graph data, param:')
      console.log(paramObj)
      const graphData = await this.$http.get(this.loadUrl, {
        params: paramObj
      })
      const datas = graphData.data.data
      datas.nodes.forEach(data => {
        data.labelCfg = { position: 'bottom' }
        data.size = data.isCenter ? 80 : 36
        if (data.isCenter) {
          this.set_current_center_node(data.id)
          this.items.push({
            id: data.id,
            name: data.label
          })
          this.selectedApiBreadIndex = 0
        }
        let imgSrc = ''
        switch (data.Ntype) {
          case 'METHOD':
            imgSrc = '/function.svg'
            break
          case 'CLASS':
            imgSrc = '/class.svg'
            break
          case 'INTERFACE':
            imgSrc = '/interface.svg'
            break
          case 'PACKAGE':
            imgSrc = '/package.svg'
            break
          case 'EXCEPTION':
            imgSrc = '/exception.svg'
            break
          case 'MODULE':
            imgSrc = '/module.svg'
            break
          case 'ERROR':
            imgSrc = '/error.svg'
            break
          case 'FIELD':
            imgSrc = '/field.svg'
            break
          default:
            imgSrc = '/object.svg'
        }
        data.img = imgSrc
        data.type = 'image'
        data.style = {
          cursor: 'grab',
          shadowBlur: 10,
          shadowColor: 'grey',
          shadowOffsetX: 2,
          shadowOffsetY: 2
        }
        data.labelCfg = {
          style: {
            fontSize: 15,
            fontWeight: 'bolder'
          }
        }
      })
      return datas
    },
    async updateSubmap () {
      this.items = []
      const data = await this.getGraphData()
      // this.current_submap.read(data)
      localCurrentGraph.changeData(data)
      // this.current_submap.changeData(data)
      // this.current_submap.refresh()
    },
    async initGraph () {
      /*
      G6.registerNode('APInode', {
        draw (cfg, group) {
          const {
            Ntype,
            label,
            isCenter
          } = cfg
          const size = isCenter ? 80 : 40
          if (isCenter) {
            this.current_show_detail_node = cfg.id
            console.log(this.current_show_detail_node)
          }
          let imgSrc = ''
          switch (Ntype) {
            case 'METHOD':
              imgSrc = '/function.png'
              break
            case 'CLASS':
              imgSrc = '/class.png'
              break
            case 'INTERFACE':
              imgSrc = '/interface.png'
              break
            case 'PACKAGE':
              imgSrc = '/package.png'
              break
            case 'EXCEPTION':
              imgSrc = '/exception.png'
              break
            case 'MODULE':
              imgSrc = '/module.png'
              break
            default:
              imgSrc = '/class.png'
          }
          console.log(imgSrc)
          const keyShape = group.addShape('dom', {
            attrs: {
              width: size + 30,
              height: size + 50,
              html: `
              <div style="background-color: #fff; border: 2px solid #5B8FF9; border-radius: 5px; justify-content: center; display: flex; flex-direction: column; flex-wrap: wrap; align-items: center; padding-top: 5px;">
                <div>
                  <img alt="img" src="${imgSrc}" style="height: ${size - 5}px; width: ${size - 5}px; -webkit-user-drag: none;"/>
                </div>
                <div style="width: ${size + 25}px; height: auto; font-size: $2px; text-align: center; word-break: break-all;">${label}</div>
              </div>
              `
            },
            name: 'dom-shape',
            draggable: true
          })
          return keyShape
        }
      }) */
      const width = document.getElementById('roadmap-root-container').scrollWidth
      const height = document.getElementById('roadmap-root-container').scrollHeight
      // eslint-disable-next-line new-cap
      const grid = new G6.Grid({
        img: 'PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAwIDEwIEwgNDAgMTAgTSAxMCAwIEwgMTAgNDAgTSAwIDIwIEwgNDAgMjAgTSAyMCAwIEwgMjAgNDAgTSAwIDMwIEwgNDAgMzAgTSAzMCAwIEwgMzAgNDAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2UwZTBlMCIgb3BhY2l0eT0iMC4yIiBzdHJva2Utd2lkdGg9IjEiLz48cGF0aCBkPSJNIDQwIDAgTCAwIDAgMCA0MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZTBlMGUwIiBzdHJva2Utd2lkdGg9IjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4='
      })
      const graph = new G6.Graph({
        container: 'roadmap-container',
        renderer: 'svg',
        width: width,
        height: height,
        linkCenter: false,
        plugins: [grid],
        animate: true,
        modes: {
          default: [
            'drag-node',
            'drag-canvas',
            {
              type: 'tooltip',
              formatText (model) {
                return `
                <h3>${model.apiShortName}</h3>
                <p>${model.desctiption}</p>
                `
              },
              offset: 10
            },
            'zoom-canvas',
            'click-select'
          ]
        },
        defaultEdge: {
          size: 1,
          color: '#e2e2e2',
          style: {
            lineWidth: 2,
            stroke: '#b5b5b5',
            lineAppendWidth: 10,
            userSelect: 'none'
          }
        },
        edgeStateStyles: {
          hover: {
            stroke: '#F1394B',
            lineDash: [5, 10, 15]
          }
        },
        nodeStateStyles: {
          selected: {
            shadowColor: '#F1394B',
            shadowBlur: 10,
            fillOpacity: 0.7
          }
        },
        layout: {
          type: 'force',
          preventOverlap: true,
          linkDistance: 150,
          edgeStrength: 5,
          nodeSpacing: 100
        }
      })

      const graphData = await this.getGraphData()
      graph.read(graphData)
      // graph.focusItem(this.current_show_detail_node, true)
      graph.translate(-500, 0)

      graph.on('edge:mouseenter', (evt) => {
        const { item } = evt
        graph.setItemState(item, 'hover', true)
      })

      graph.on('edge:mouseleave', (evt) => {
        const { item } = evt
        graph.setItemState(item, 'hover', false)
      })
      const that = this
      graph.on('nodeselectchange', (evt) => {
        console.log('nodeselectchange!')
        if (evt.select) {
          // .clearItemStates(that.current_show_detail_node, 'selected')
          // graph.setItemState(evt.target, 'selected', true)
          that.set_show_detail_node(evt.target._cfg.id)
          this.items.push({
            id: evt.target._cfg.id,
            name: evt.target._cfg.model.label
          })
        } else {
          // graph.clearItemStates(that.current_show_detail_node, 'selected')
          if (that.items.length > 1) {
            that.items.pop()
            that.set_show_detail_node(that.items[that.items.length - 1].id)
          }
        }
      })
      localCurrentGraph = graph
      console.log(localCurrentGraph === graph)
      this.set_current_submap(graph)
    },
    showThreads () {
      this.$router.push('/detail')
    },
    onCommunityBtnClick () {
      this.community = true
      this.set_map_show_mode(true)
      this.set_current_center_node(this.current_map_center_node)
      this.updateSubmap()
    },
    onConceptBtnClick () {
      this.community = false
      this.set_map_show_mode(false)
      this.set_current_center_node(this.current_map_center_node)
      this.updateSubmap()
    },
    handleSwitch (value) {
      debugger
      this.community = value
      this.set_map_show_mode(value)
      this.set_current_center_node(this.current_map_center_node)
      this.updateSubmap()
    },
    onBreadClick (item) {
      this.current_submap.clearItemStates(this.current_show_detail_node, 'selected')
      this.set_show_detail_node(item.id)
      this.current_submap.setItemState(item.id, 'selected', true)
      while (this.items[this.items.length - 1].id !== item.id) {
        this.items.pop()
      }
    },
    ...mapMutations({
      set_current_section_id: 'set_current_section_id',
      set_current_submap: 'set_current_submap',
      set_current_center_node: 'set_current_center_node',
      set_show_detail_node: 'set_show_detail_node',
      switch_map_show_mode: 'switch_map_show_mode',
      set_map_show_mode: 'set_map_show_mode'
    })
  },
  computed: {
    loadUrl () {
      return (this.community ? '/getCommunitySubmap/' : '/getConceptSubmap/') + this.docName
    },
    ...mapState({
      current_submap: 'current_submap',
      current_show_detail_node: 'current_show_detail_node',
      current_section_id: 'current_section_id',
      current_map_center_node: 'current_map_center_node',
      show_community_map: 'show_community_map',
      docName: 'doc_name'
    })
  }
})
</script>

<style>
#roadmap-root-container {
  width: 100%;
  height: 100%;
}

#roadmap-container {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: none;
}

#api-detail-pane {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  margin: 20px;
  overflow: auto;
  border-radius: 15px;
  box-shadow: 0 2px 10px 2px rgba(0, 0, 0, .08);
  width: 708px;
  height: auto;
  background-color: #fff;
}

#bread-pane {
  position: absolute;
  top: 0;
  left: 0;
  margin: 20px;
  width: auto;
  max-width: 600px;
  overflow: auto;
}

.g6-tooltip {
  padding: 0px 3px;
  color: #444;
  background-color: rgba(255, 255, 255, 0.9);
  border: 2px solid #000;
  box-shadow: 0 2px 10px 2px rgba(0, 0, 0, .08);
  border-radius: 10px;
  word-break: break-all;
  width: 308px;
}
</style>

<template>
<div id="roadmap-root-container">
  <div id="roadmap-container"></div>
  <div id="api-detail-pane">

  </div>
</div>
</template>

<script>
import { defineComponent } from 'vue'
import { mapState } from 'vuex'
import G6 from '@antv/g6'
export default defineComponent({
  name: 'Roadmap',
  data () {
    return {
      showDetail: false,
      docName: 'javadoc'
    }
  },
  mounted () {
    console.log('mounted')
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

      const graphData = await this.$http.get(this.loadUrl, {
        params: paramObj
      })
      const datas = graphData.data.data
      datas.nodes.forEach(data => {
        data.labelCfg = { position: 'bottom' }
        data.size = data.isCenter ? 80 : 36
        let imgSrc = ''
        switch (data.Ntype) {
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
        data.img = imgSrc
        data.type = 'image'
        data.style = {
          cursor: 'grab',
          shadowBlur: 2,
          fill: 'white'
        }
        data.labelCfg = {
          style: {
            fontSize: 15
          }
        }
      })
      return datas
    },
    async initGraph () {
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
      })
      const width = document.getElementById('roadmap-root-container').scrollWidth
      const height = document.getElementById('roadmap-root-container').scrollHeight
      const graph = new G6.Graph({
        container: 'roadmap-container',
        renderer: 'svg',
        width: width,
        height: height,
        linkCenter: false,
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
            }
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
      /*
      function refreshDragedNodePosition (e) {
        console.log(e)
        const model = e.item.get('model')
        model.fx = e.x
        model.fy = e.y
      }

      graph.on('node:dragstart', function (e) {
        graph.layout()
        refreshDragedNodePosition(e)
      })

      graph.on('node:drag', function (e) {
        refreshDragedNodePosition(e)
      })

      graph.on('node:dragend', function (e) {
        e.item.get('model').fx = null
        e.item.get('model').fy = null
      }) */

      this.current_submap = graph
    }
  },
  computed: {
    loadUrl () {
      return '/getCommunitySubmap/' + this.docName
    },
    ...mapState({
      current_submap: 'current_submap',
      current_show_detail_node: 'current_show_detail_node',
      current_section_id: 'current_section_id'
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
  margin: 50px;
  overflow: auto;
  border-radius: 15px;
  box-shadow: 0 2px 10px 2px rgba(0, 0, 0, .08);
  width: 508px;
  height: auto;
  background-color: #fff;
}

.g6-tooltip {
  padding: 6px;
  color: #444;
  background-color: rgba(255, 255, 255, 0.9);
  border: 2px solid #000;
  box-shadow: #444;
  border-radius: 10px;
  word-break: break-all;
}
</style>

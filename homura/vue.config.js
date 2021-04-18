module.exports = {
  devServer: {
    open: true,
    proxy: {
      '/api': {
        target: 'http://8.136.235.136:3001', // 接口域名
        changeOrigin: true, // 是否跨域
        ws: true, // 是否代理 websockets
        pathRewrite: { // 路径重置
          '^/api': ''
        }
      }
    }
  }
}

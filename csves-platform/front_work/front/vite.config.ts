import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // 允许局域网访问
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://10.12.65.218:8000', // Flask 后端的 IP
        changeOrigin: true,
      },
    },
  },
})


 

// import { defineConfig } from 'vite'
// import react from '@vitejs/plugin-react'

// // https://vite.dev/config/
// export default defineConfig({
//   plugins: [react()],
//   server: {
//     host: '0.0.0.0', // 允许外部访问
//     port: 5173, // 开发服务器端口
//     proxy: {
//       // 代理所有以 /api 开头的请求到后端
//       '/api': {
//         target: 'http://localhost:8000', // 您的后端运行在8000端口
//         changeOrigin: true,
//         rewrite: (path) => path.replace(/^\/api/, '')
//       }
//     }
//   }
// })


/*import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
})*/

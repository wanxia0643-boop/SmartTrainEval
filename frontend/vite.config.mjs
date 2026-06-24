import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  server: {
    host: "127.0.0.1",
    port: 5173,
    proxy: {
      // 前端 /api/** 代理到后端 /api/v1/**（FastAPI 运行在 8000）
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, "/api/v1"),
      },
    },
  },
  plugins: [vue()],
});

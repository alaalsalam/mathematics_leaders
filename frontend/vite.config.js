// apps/mathematics_leaders/frontend/vite.config.js
import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import path from "path"
import fs from "fs"

// اقرأ منفذ الويب من bench أثناء التطوير
function getCommonSiteConfig() {
  let currentDir = path.resolve(".")
  while (currentDir !== "/") {
    if (fs.existsSync(path.join(currentDir, "sites")) && fs.existsSync(path.join(currentDir, "apps"))) {
      const p = path.join(currentDir, "sites", "common_site_config.json")
      return fs.existsSync(p) ? JSON.parse(fs.readFileSync(p)) : null
    }
    currentDir = path.resolve(currentDir, "..")
  }
  return null
}

function getProxyOptions() {
  const cfg = getCommonSiteConfig()
  const port = cfg ? cfg.webserver_port : 8000
  return {
    "^/(app|login|api|assets|files|private)": {
      target: `http://127.0.0.1:${port}`,
      ws: true,
      router(req) {
        const site = req.headers.host.split(":")[0]
        return `http://${site}:${port}`
      }
    }
  }
}

export default defineConfig({
  base: "/assets/mathematics_leaders/frontend/",

  server: {
    port: 8080,
    proxy: getProxyOptions()
  },

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src")
    }
  },

  plugins: [vue()],

  build: {
    outDir: "../mathematics_leaders/public/frontend", // ينسخها bench إلى sites/assets/
    emptyOutDir: true,
    target: "es2019",
    sourcemap: true,

    // أسماء ثابتة حتى تربطها مباشرة من صفحة www
    assetsDir: "",
    rollupOptions: {
      output: {
        entryFileNames: "js/platform.js",
        chunkFileNames: "js/[name].js",
        assetFileNames: (a) => {
          const n = a.name || ""
          if (n.endsWith(".css")) return "css/platform.css"
          return "assets/[name][extname]"
        },
        manualChunks: {
          vue: ["vue", "vue-router", "pinia"]
        }
      }
    },

    commonjsOptions: {
      include: [/node_modules/, /tailwind.config.js/]
    }
  },

  optimizeDeps: {
    include: [
      "tailwind.config.js"
    ]
  }
})

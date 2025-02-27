import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  // Load environment variables
  const env = loadEnv(mode, process.cwd(), "VITE");

  return {
    plugins: [react()],
    server: {
      host: "localhost",
      port: Number(env.VITE_PORT) || 5173, // Use port from .env, fallback to 5173
      open: true,
      strictPort: true,
      watch: {
        usePolling: true, // Ensures HMR works in Docker/WSL
      },
    },
    define: {
      "process.env": env, // Make env variables available in the app
    },
    build: {
      outDir: "dist",
      sourcemap: true,
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (id.includes("node_modules")) {
              return "vendor";
            }
          },
        },
      },
    },
  };
});

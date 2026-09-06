import { defineConfig, transformWithEsbuild } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [
    {
      name: "treat-js-files-as-jsx",
      enforce: "pre",
      async transform(code, id) {
        if (!/\/src\/.*\.js$/.test(id)) return null;
        return transformWithEsbuild(code, id, { loader: "jsx", jsx: "automatic" });
      },
    },
    react(),
  ],
  optimizeDeps: {
    esbuildOptions: { loader: { ".js": "jsx" } },
  },
  server: { port: 3000 },
  preview: { port: 3000 },
  test: {
    environment: "jsdom",
    setupFiles: "./src/setupTests.js",
  },
});

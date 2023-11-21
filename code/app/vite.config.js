import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: "/",
  build: {
    outDir: "build",
    assetsDir: "",
    assetsInlineLimit: 0,
    minify: "terser",
  },
  server: {
    port: process.env.REACT_APP_PORT,
  },
});
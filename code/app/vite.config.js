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
	https: {
		key: process.env.SSL_KEY_PATH || './cert/key.pem',
		cert: process.env.SSL_CERT_PATH || './cert/cert.pem',
	},
  },
});

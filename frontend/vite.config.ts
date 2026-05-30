import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  server: { port: 5173, host: "0.0.0.0" },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/tests/setup.ts"],
    // Playwright specs run separately via `npm run e2e`.
    exclude: ["node_modules/**", "dist/**", "e2e/**"],
  },
});

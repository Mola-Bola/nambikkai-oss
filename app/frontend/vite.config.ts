import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Localhost only (ADR 001) — the dev server refuses off-device connections,
// and /api proxies to the FastAPI backend on 8787.
export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: Number(process.env.PORT ?? 5173),
    strictPort: true,
    proxy: {
      "/api": `http://127.0.0.1:${process.env.NAMBIKKAI_API_PORT ?? 8787}`,
    },
  },
});

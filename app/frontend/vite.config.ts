import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Localhost only (ADR 001) — the dev server refuses off-device connections,
// and /api proxies to the FastAPI backend.
//
// The backend requires a per-session token (see app/backend/security.py). We
// inject it here, in the Node process, reading the file the backend writes at
// startup. The browser never sees the token, so a malicious page that resolves
// to 127.0.0.1 can't replay it.
const TOKEN_PATH = resolve(__dirname, "../../data/.session-token");

function sessionToken(): string {
  try {
    return readFileSync(TOKEN_PATH, "utf-8").trim();
  } catch {
    return ""; // backend not up yet; the request will 401 and the UI says so
  }
}

export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: Number(process.env.PORT ?? 5173),
    strictPort: true,
    proxy: {
      "/api": {
        target: `http://127.0.0.1:${process.env.NAMBIKKAI_API_PORT ?? 8787}`,
        configure: (proxy) => {
          // Read per-request: the backend may restart and re-mint the token.
          proxy.on("proxyReq", (proxyReq) => {
            proxyReq.setHeader("x-nambikkai-token", sessionToken());
          });
        },
      },
    },
  },
});

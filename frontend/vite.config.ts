import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

const srcPath = fileURLToPath(new URL("./src", import.meta.url));
const repoRootPath = fileURLToPath(new URL("..", import.meta.url));

/** The version shown by the shell's version badge; the fleet takes it from the build. */
function readAppVersion(): string {
  const manifest = JSON.parse(
    readFileSync(fileURLToPath(new URL("./package.json", import.meta.url)), "utf8"),
  ) as { version?: string };
  return manifest.version ?? "0.0.0";
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiBaseUrl = process.env.VITE_API_BASE_URL ?? env.VITE_API_BASE_URL ?? "/api/v1";
  const apiProxyTarget =
    process.env.VITE_API_PROXY_TARGET ?? env.VITE_API_PROXY_TARGET ?? "http://localhost:8001";
  const frontendPort = Number(process.env.FRONTEND_PORT ?? env.FRONTEND_PORT ?? "5174");

  return {
    plugins: [react(), tailwindcss()],
    define: {
      __APP_VERSION__: JSON.stringify(readAppVersion()),
    },
    resolve: {
      alias: {
        "@": path.resolve(srcPath),
      },
    },
    server: {
      host: "0.0.0.0",
      port: frontendPort,
      fs: {
        allow: [repoRootPath],
      },
      proxy: apiBaseUrl.startsWith("/")
        ? {
            "/api": {
              target: apiProxyTarget,
              changeOrigin: true,
            },
          }
        : undefined,
    },
  };
});

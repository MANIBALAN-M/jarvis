/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_JARVIS_API_URL?: string;
  readonly VITE_JARVIS_WS_URL?: string;
  readonly VITE_JARVIS_API_AUTH_TOKEN?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

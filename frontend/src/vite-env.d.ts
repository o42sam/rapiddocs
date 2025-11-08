/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  readonly VITE_MAX_FILE_SIZE?: string
  readonly VITE_SUPPORTED_FORMATS?: string
  readonly PROD?: boolean
  readonly DEV?: boolean
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

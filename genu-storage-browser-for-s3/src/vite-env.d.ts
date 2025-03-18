/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_APP_AUTH_USER_POOL_ID: string;
    readonly VITE_APP_AUTH_AWS_REGION: string;
    readonly VITE_APP_AUTH_USER_POOL_CLIENT_ID: string;
    readonly VITE_APP_AUTH_IDENTITY_POOL_ID: string;
    readonly VITE_APP_STORAGE_AWS_REGION: string;
    readonly VITE_APP_STORAGE_BUCKET_NAME: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}


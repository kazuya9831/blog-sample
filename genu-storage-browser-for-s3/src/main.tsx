import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import { Amplify } from "aws-amplify";
import { Authenticator } from '@aws-amplify/ui-react'; // Authenticatorをインポート
import "@aws-amplify/ui-react-storage/styles.css";
import {
  createAmplifyAuthAdapter,
  createStorageBrowser,
} from '@aws-amplify/ui-react-storage/browser';

Amplify.configure({
  "auth": {
      "user_pool_id": import.meta.env.VITE_APP_AUTH_USER_POOL_ID,
      "aws_region": import.meta.env.VITE_APP_AUTH_AWS_REGION,
      "user_pool_client_id": import.meta.env.VITE_APP_AUTH_USER_POOL_CLIENT_ID,
      "identity_pool_id": import.meta.env.VITE_APP_AUTH_IDENTITY_POOL_ID
  },
  "storage": {
      "aws_region": import.meta.env.VITE_APP_STORAGE_AWS_REGION,
      "bucket_name": import.meta.env.VITE_APP_STORAGE_BUCKET_NAME,
      "buckets": [{
          "name": "storage1",
          "bucket_name": import.meta.env.VITE_APP_STORAGE_BUCKET_NAME,
          "aws_region": import.meta.env.VITE_APP_STORAGE_AWS_REGION,
          "paths": {
              "docs/*": {
                  "authenticated": [
                      "read",
                      "get",
                      "list",
                      "write",
                      "delete"
                  ]
              }
          }
      }]
  },
  "version": "1.2"
}
);

export const { StorageBrowser } = createStorageBrowser({
  config: createAmplifyAuthAdapter(),
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
      <Authenticator>
          <StorageBrowser />
      </Authenticator>
  </React.StrictMode>
);

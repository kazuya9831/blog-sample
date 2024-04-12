import os

import jwt

COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
AWS_REGION = os.environ.get("AWS_REGION")


class InvalidTokenError(Exception):
    """トークン検証エラー用のカスタム例外クラス"""

    pass


class CognitoTokenParser:
    def __init__(self, access_token):
        self.cognito_user_pool_id = COGNITO_USER_POOL_ID
        self.cognito_client_id = COGNITO_CLIENT_ID
        self.region = AWS_REGION
        self.access_token = access_token
        self._decode_access_token()
        self._additional_validate_token()

    def _decode_access_token(self):
        """トークンをデコードする関数"""
        issusr = f"https://cognito-idp.{self.region}.amazonaws.com/{self.cognito_user_pool_id}"

        jwks_url = f"{issusr}/.well-known/jwks.json"
        jwks_client = jwt.PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(self.access_token)

        self._token = jwt.decode(
            self.access_token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=issusr,
        )

    def _additional_validate_token(self):
        """トークンの追加検証を行う関数

        Cognitoの推奨に従い、client_idとtoken_useの検証を追加で行う
        """
        if self._token["client_id"] != self.cognito_client_id:
            raise InvalidTokenError("Invalid client_id")

        if self._token["token_use"] != "access":
            raise InvalidTokenError("Invalid token_use")

    def get_token(self):
        """デコードしたトークンを返す関数"""
        return self._token

    def get_username(self):
        """トークンからユーザー情報を取得する関数"""
        return self._token["username"]

    def get_group_ids(self):
        """トークンからGroupを取得する関数"""
        return self._token["cognito:groups"]

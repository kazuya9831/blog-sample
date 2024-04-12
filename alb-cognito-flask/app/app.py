import json

import jwt
from flask import Flask, jsonify, render_template, request
from lib.alb_token_parser import decode_alb_token
from lib.cognito_token_parser import CognitoTokenParser

app = Flask(__name__)


def parse_string_to_json(string):
    return json.dumps(string, indent=4)


def decode_access_token(access_token):
    auth = CognitoTokenParser(access_token)
    decode_access_token = auth.get_token()

    return decode_access_token


def decode_oidc_data(oidc_data):
    return decode_alb_token(oidc_data)


def parse_header_value_to_json(detail_headers, header_key):

    header_value = request.headers.get(header_key)
    header_value_json = json.loads(header_value)
    detail_headers[header_key] = parse_string_to_json(header_value_json)

    return detail_headers


@app.route("/", methods=["GET", "POST"])
def index():

    # ヘッダーからアクセストークンとOIDCデータを取得
    access_token = request.headers.get("X-Amzn-Oidc-Accesstoken")
    oidc_data = request.headers.get("X-Amzn-Oidc-Data")

    # access_tokenとoidc_dataがない場合があるようで、この処理がないと正しく動作しない
    if access_token is None or oidc_data is None:
        return jsonify({"error": "Access token is missing"}), 401

    # ヘッダー検証なしにデコードする場合
    # decode_access_token = jwt.decode(access_token, options={"verify_signature": False})
    # decode_oidc_data = jwt.decode(oidc_data, options={"verify_signature": False})

    # ヘッダー検証しつつ、デコードする場合
    decoded_access_token = decode_access_token(access_token)
    decoded_oidc_data = decode_oidc_data(oidc_data)

    # Webに表示したいデータを整形
    detail_headers = {}
    detail_headers["X-Amzn-Oidc-Accesstoken"] = access_token
    # Webで見やすいようにJSON形式に整形
    detail_headers["decode_access_token"] = parse_string_to_json(decoded_access_token)
    detail_headers["username_from_access_token"] = decoded_access_token["username"]
    detail_headers["group_ids_from_access_token"] = decoded_access_token[
        "cognito:groups"
    ]

    detail_headers["X-Amzn-Oidc-Data"] = oidc_data
    # Webで見やすいようにJSON形式に整形
    detail_headers["decode_oidc_data"] = parse_string_to_json(decoded_oidc_data)
    detail_headers["username_from_oidc_data"] = decoded_oidc_data["username"]

    # detail_headers = parse_header_value_to_json(detail_headers, "X-Amzn-Lambda-Context")
    # detail_headers = parse_header_value_to_json(
    #     detail_headers, "X-Amzn-Request-Context"
    # )

    return render_template("index.html", detail_headers=detail_headers)

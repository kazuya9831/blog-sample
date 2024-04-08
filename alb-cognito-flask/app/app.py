
from flask import Flask, render_template, request, jsonify
from lib.parse_jwt import CognitoTokenParser
import jwt
import json

app = Flask(__name__)


def get_user_info(access_token):
    auth = CognitoTokenParser(access_token)

    return {"username": auth.get_username(), "group_ids": auth.get_group_ids()}


def json_pretty(data):
    return json.dumps(data, indent=4)


@app.route("/", methods=["GET", "POST"])
def index():

    access_token = request.headers.get("X-Amzn-Oidc-Accesstoken")
    oidc_data = request.headers.get("X-Amzn-Oidc-Data")
    if access_token is None or oidc_data is None:
        return jsonify({"error": "Access token is missing"}), 401

    decode_access_token = jwt.decode(request.headers.get("X-Amzn-Oidc-Accesstoken"), options={"verify_signature": False})
    decode_oidc_data = jwt.decode(request.headers.get("X-Amzn-Oidc-Data"), options={"verify_signature": False})
    # return render_template("index.html", user_info=a)
    detail_headers = {}
    
    detail_headers["X-Amzn-Oidc-Accesstoken"] = request.headers.get("X-Amzn-Oidc-Accesstoken")
    detail_headers["decode_access_token"] = json.dumps(decode_access_token, indent=4)
    
    detail_headers["X-Amzn-Oidc-Data"] = request.headers.get("X-Amzn-Oidc-Data")
    detail_headers["decode_oidc_data"] = json.dumps(decode_oidc_data, indent=4)
    b = json.loads(request.headers.get("X-Amzn-Lambda-Context"))
    detail_headers["X-Amzn-Lambda-Context"] = json.dumps(b, indent=4)
    a = json.loads(request.headers.get("X-Amzn-Request-Context"))
    detail_headers["X-Amzn-Request-Context"] = json.dumps(a, indent=4)
    
    return render_template("index.html", detail_headers=detail_headers)

import base64
import json
import os

import jwt
import requests

AWS_REGION = os.environ.get("AWS_REGION")


def decode_alb_token(encoded_jwt):

    jwt_headers = encoded_jwt.split(".")[0]
    decoded_jwt_headers = base64.b64decode(jwt_headers)
    decoded_jwt_headers = decoded_jwt_headers.decode("utf-8")
    decoded_json = json.loads(decoded_jwt_headers)
    kid = decoded_json["kid"]

    # Step 2: Get the public key from regional endpoint
    url = f"https://public-keys.auth.elb.{AWS_REGION}.amazonaws.com/{kid}"
    req = requests.get(url)
    pub_key = req.text

    return jwt.decode(encoded_jwt, pub_key, algorithms=["ES256"])

import base64
import hashlib
import io
import json
import os
import uuid

import boto3
from flask import Flask, render_template, request

app = Flask(__name__)

# パラメータの設定
AURORA_RESOURCE_ARN = os.environ["AURORA_RESOURCE_ARN"]
DATABASE_NAME = "images"
SECRET_ARN = os.environ["SECRET_ARN"]
IMAGES_S3_BUCKET = os.environ["IMAGES_S3_BUCKET"]
IMAGE_BASE_URL = os.environ["IMAGE_BASE_URL"]

rds_data_client = boto3.client("rds-data")

EXCECUTE_STATEMENT_OPTION = {
    "resourceArn": AURORA_RESOURCE_ARN,
    "secretArn": SECRET_ARN,
    "database": DATABASE_NAME,
}


def generate_embeddings(input_image):
    bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-west-2")
    model_id = "amazon.titan-embed-image-v1"
    output_embedding_length = 1024

    body = json.dumps(
        {
            "inputImage": input_image,
            "embeddingConfig": {"outputEmbeddingLength": output_embedding_length},
        }
    )

    accept = "application/json"
    content_type = "application/json"

    response = bedrock.invoke_model(
        body=body, modelId=model_id, accept=accept, contentType=content_type
    )

    response_body = json.loads(response.get("body").read())

    finish_reason = response_body.get("message")

    if finish_reason is not None:
        raise ValueError(f"Embeddings generation error: {finish_reason}")

    return response_body["embedding"]


def generate_uuid_from_filename(filename):
    hash_object = hashlib.sha1(filename.encode())
    hash_hex = hash_object.hexdigest()

    uuid_generated = uuid.UUID(hash_hex[:32])

    return uuid_generated


def insert_data_into_rds(file_name, embedding, image_path):
    rds_data_client.execute_statement(
        **EXCECUTE_STATEMENT_OPTION,
        sql=f"""
INSERT INTO bedrock_integration.bedrock_kb (id, title, embedding,image_path)
VALUES (
    '{generate_uuid_from_filename(file_name)}',
    '{file_name}',
    ARRAY{embedding}::vector,
    '{image_path}'
)
ON CONFLICT (id)
DO UPDATE SET
    title = EXCLUDED.title,
    embedding = EXCLUDED.embedding,
    image_path = EXCLUDED.image_path;
""",
    )


def search_image(embedding):

    response = rds_data_client.execute_statement(
        **EXCECUTE_STATEMENT_OPTION,
        sql=f"""
SELECT id, title, image_path, embedding, (1 - (embedding <=> '{embedding}'::vector)) AS similarity
FROM bedrock_integration.bedrock_kb
ORDER BY embedding <=> '{embedding}'::vector
LIMIT 5;
""",
    )

    return response["records"]


def upload_to_s3(file_name, content_type, file_content):
    s3_client = boto3.client("s3")
    s3_client.upload_fileobj(
        io.BytesIO(file_content),
        IMAGES_S3_BUCKET,
        f"images/{file_name}",
        ExtraArgs={"ContentType": content_type},
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/insert", methods=["GET", "POST"])
def insert():
    if request.method == "POST":
        file = request.files["file"]
        file_name = file.filename
        content_type = file.content_type
        file_content = file.read()
        if file:
            upload_to_s3(file_name, content_type, file_content)
            input_image = base64.b64encode(file_content).decode("utf8")
            embedding = generate_embeddings(input_image)
            image_path = f"{IMAGE_BASE_URL}/{file_name}"
            insert_data_into_rds(file_name, embedding, image_path)
            return render_template("insert.html")
    return render_template("insert.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        file = request.files["file"]
        file_content = file.read()
        if file:
            input_image = base64.b64encode(file_content).decode("utf8")
            embedding = generate_embeddings(input_image)
            search_results = search_image(embedding)
            results = []
            for result in search_results:
                file_name = result[1]["stringValue"]
                image_path = result[2]["stringValue"]
                similarity = f'{result[4]["doubleValue"]:.2f}'
                results.append(
                    {
                        "file_name": file_name,
                        "image_path": image_path,
                        "similarity": similarity,
                    }
                )
            return render_template(
                "search.html", results=results, image_data=input_image
            )
    return render_template("search.html")


if __name__ == "__main__":
    app.run(debug=True)

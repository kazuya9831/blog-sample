import io
import json
import os
import time
from datetime import timedelta

import boto3
from flask import Flask, redirect, render_template, request

app = Flask(__name__)

bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
modelId = "anthropic.claude-3-5-sonnet-20240620-v1:0"


S3_BUCKET = os.environ.get("S3_BUCKET")


# AWSクライアントの初期化
s3_client = boto3.client("s3")
transcribe = boto3.client("transcribe")


# S3にファイルをアップロード
def upload_to_s3(file_name, file_content, content_type):
    """S3にファイルをアップロードする"""
    s3_client.upload_fileobj(
        io.BytesIO(file_content),
        S3_BUCKET,
        file_name,
        ExtraArgs={"ContentType": content_type},
    )


def start_transcription_job(job_name, job_uri, s3_output_key):
    """Transcribeジョブを開始する"""
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": job_uri},
        MediaFormat="wav",
        LanguageCode="ja-JP",  # 言語コードを指定
        OutputBucketName=S3_BUCKET,
        OutputKey=s3_output_key,
    )


def wait_for_transcription_job(job_name):
    """Transcribeジョブの完了を待つ"""
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status["TranscriptionJob"]["TranscriptionJobStatus"] in [
            "COMPLETED",
            "FAILED",
        ]:
            return status
        print("Transcription job is still in progress...")
        time.sleep(10)


def query_generative_ai(prompt):
    """生成AIにクエリを投げる"""
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
            # "stop_sequences": [stop_sequences],
        }
    )

    response = bedrock_runtime.invoke_model(body=body, modelId=modelId)

    answer = response["body"].read().decode("utf-8")
    answer = json.loads(answer)["content"][0]["text"]

    return answer


def get_talk_script():
    """S3からトークスクリプトを取得する"""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key="talk_script.txt")
        talk_script = response["Body"].read().decode("utf-8")
        return talk_script
    except s3_client.exceptions.NoSuchKey:
        return ""


@app.route("/")
def index():
    """トップページを表示する関数"""
    talk_script = get_talk_script()
    return render_template("index.html", talk_script=talk_script)


def transcript_audio(id, audio_file_name):
    """音声ファイルを文字起こしする"""

    job_name = f"transcription_job_{id}"

    job_uri = f"s3://{S3_BUCKET}/{audio_file_name}"
    transcrjption_s3_output_key = f"{id}/{job_name}.json"  # 結果のS3キー

    start_transcription_job(job_name, job_uri, transcrjption_s3_output_key)
    status = wait_for_transcription_job(job_name)
    if status["TranscriptionJob"]["TranscriptionJobStatus"] != "COMPLETED":
        return "Transcribeジョブが失敗しました"

    result = s3_client.get_object(Bucket=S3_BUCKET, Key=transcrjption_s3_output_key)
    transcript = json.loads(result["Body"].read().decode("utf-8"))
    transcription = transcript["results"]["transcripts"][0]["transcript"]

    return transcription


def evaluate_transcription_and_talk_script(talk_script, transcription):

    prompt = f"""
あなたはスタッフがトークスクリプト通りに発音できているか確認する担当者です。
ユーザーから音声データを文字起こしした文章を受け取るため、トークスクリプトと比較し、フィードバックしてください。

<トークスクリプト>
{talk_script}
</トークスクリプト>

Human:
{transcription}
"""

    return query_generative_ai(prompt)


@app.route("/upload", methods=["POST"])
def upload_file():

    file = request.files["audio_file"]

    if not file:
        return "ファイルがアップロードされていません"

    talk_script = get_talk_script()
    # 日付生成してIDにする
    id = time.strftime("%Y-%m-%d_%H-%M-%S")
    audio_file_name = f"{id}/{file.filename}"
    audio_file_content = file.read()
    audio_file_content_type = file.content_type

    upload_to_s3(audio_file_name, audio_file_content, audio_file_content_type)
    transcription_result = transcript_audio(id, audio_file_name)

    evaluation_result = evaluate_transcription_and_talk_script(
        talk_script, transcription_result
    )

    result_content = f"""

## トークスクリプト
{talk_script}

## 文字起こし結果
{transcription_result}

## 生成AIによる評価結果
{evaluation_result}
"""

    upload_to_s3(f"{id}/result.txt", result_content.encode("utf-8"), "text/plain")

    return render_template(
        "result.html",
        talk_script=talk_script,
        transcription_result=transcription_result,
        evaluation_result=evaluation_result,
    )


@app.route("/results")
def list_results():
    """結果ファイルの一覧を表示する関数"""
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
    objects = []
    if "Contents" in response:
        for obj in response["Contents"]:
            if "result.txt" not in obj["Key"]:
                continue
            object_key = obj["Key"]
            last_modified = obj["LastModified"] + timedelta(hours=9)
            objects.append({"key": object_key, "last_modified": last_modified})
        return render_template("file_list.html", objects=objects)

    return render_template("file_list.html")


@app.route("/results/<path:file_path>", methods=["GET"])
def display_result(file_path):
    """結果ファイルの内容を表示する関数"""

    response = s3_client.get_object(Bucket=S3_BUCKET, Key=file_path)
    file_content = response["Body"].read().decode("utf-8")

    return render_template(
        "file_content.html", file_path=file_path, file_content=file_content
    )


@app.route("/talk_script/edit", methods=["POST"])
def edit_talk_script():
    """トークスクリプトを編集する関数"""
    new_content = request.form["text"]
    s3_client.put_object(Body=new_content, Bucket=S3_BUCKET, Key="talk_script.txt")

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

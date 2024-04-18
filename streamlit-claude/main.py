import json
from uuid import uuid4 as uuid

import boto3
import streamlit as st

ss = st.session_state

bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"


def generate_answer():
    """チャットボットの回答を生成する関数"""
    input_data = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": ss["chat_messages"],
            "max_tokens": 4096,
            "temperature": 0,
            "stop_sequences": [],
        }
    )

    response = bedrock_runtime.invoke_model_with_response_stream(
        accept="application/json",
        body=input_data,
        contentType="application/json",
        modelId=MODEL_ID,
    )

    for event in response.get("body"):
        chunk = json.loads(event["chunk"]["bytes"])
        if (
            chunk["type"] == "content_block_delta"
            and chunk["delta"]["type"] == "text_delta"
        ):
            yield chunk["delta"]["text"]


def chatbot_handler(user_messages_ph, bot_messages_ph):
    """ユーザーがメッセージを送信した際に動くハンドラー関数"""

    user_messages = ss.user_messages
    ss["chat_messages"].append({"role": "user", "content": user_messages})

    user_messages_ph.chat_message("user").write(user_messages)
    bot_messages = bot_messages_ph.chat_message("assistant").write_stream(
        generate_answer()
    )

    ss["chat_messages"].append({"role": "assistant", "content": bot_messages})


def display_chat_messages():
    """過去の質問と回答を表示する関数"""
    for entry in ss["chat_messages"]:
        st.chat_message(entry["role"]).write(entry["content"])


def main():
    """メイン関数"""

    st.title("📝サンプルアプリ")

    if "session_id" not in ss:
        ss["session_id"] = str(uuid())

    if "chat_messages" not in ss:
        ss["chat_messages"] = []

    display_chat_messages()

    user_messages_ph = st.empty()
    bot_messages_ph = st.empty()

    st.button("チャットのクリア", on_click=lambda: ss.clear())
    st.chat_input(
        placeholder="メッセージを入力してください",
        key="user_messages",
        args=(user_messages_ph, bot_messages_ph),
        on_submit=chatbot_handler,
    )


if __name__ == "__main__":
    main()

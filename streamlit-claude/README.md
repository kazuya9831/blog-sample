

* streamlitの起動

```
streamlit run main.py
```

* 補足


スクリプトの以下を修正することで利用するリージョンの変更が可能。

```
bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
```

スクリプトの以下を変更することで利用するモデルを変更可能。

```
MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
```

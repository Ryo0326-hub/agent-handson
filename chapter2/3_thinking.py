import boto3
from dotenv import load_dotenv 

load_dotenv()

client = boto3.client("bedrock-runtime")

# Converse API を　実行
response = client.converse(
    modelId="arn:aws:bedrock:us-west-2:591570009439:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    messages=[{
        "role": "user",
        "content": [{
            "text": "こんにちは"
        }]
    }],

    additionalModelRequestFields={
        "thinking": {
            "type": "enabled",
            "budget_tokens": 1024
        },
    },
)

#思考プロセスと最終回答を表示
for content in response["output"]["message"]["content"]:
    if "reasoningContent" in content:
        print("<thinking>")
        print(content["reasoningContent"]["reasoningText"]["text"])
        print("</thinking>")
    elif "text" in content:
        print(content["text"])


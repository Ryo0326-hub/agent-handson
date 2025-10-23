#ライブラリimport 
import boto3
from dotenv import load_dotenv

# .env　ファイルから環境変数を読み込む
load_dotenv()

# Bedrock 呼び出し用のAPIクライアントを作成
client = boto3.client("bedrock-runtime")

# Converse APIを実行
response = client.converse(
    modelId="arn:aws:bedrock:us-west-2:591570009439:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0", # モデルARN
    messages=[{
        "role": "user",
        "content": [{
            "text": "こんにちは" #入力メッセージ
        }]
    }]
)

# 実行結果のテキストだけを画面に表示
print(response["output"]["message"]["content"][0]["text"])
import boto3
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()

client = boto3.client("bedrock-runtime", region_name="us-west-2")

user_input = "2025年7月の祝日はいつ？"
llm = "arn:aws:bedrock:us-west-2:591570009439:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0"

def get_japanese_holidays(year: int):
    url = f"https://holidays-jp.github.io/api/v1/{year}/date.json"
    with urllib.request.urlopen(url) as response:
        data = response.read()
        holidays = json.loads(data)
    return holidays

tools = [{
    "toolSpec": {
        "name": "get_japanese_holidays",
        "description": "指定された年の日本の祝日一覧を取得します",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "祝日を取得したい年（例：2024）"}
                },
                "required": ["year"]
            }
        }
    }
}]

def extract_texts(content_blocks):
    texts = []
    for b in content_blocks:
        if "text" in b:
            texts.append(b["text"])
    return "\n".join(texts)

def find_tool_use(content_blocks):
    for b in content_blocks:
        if "toolUse" in b:
            return b["toolUse"]
    return None

#=========================================
# 1回目の推論
#=========================================
print("「推論1回目」")
print("ユーザーの入力: ", user_input)

response = client.converse(
    modelId=llm,
    messages=[{
        "role": "user",
        "content": [{"text": user_input}]
    }],
    toolConfig={"tools": tools}
)

message = response["output"]["message"]
first_text = extract_texts(message["content"])  # テキストが無い場合は空文字
if first_text:
    print("LLMの回答: ", first_text)

tool_use = find_tool_use(message["content"])
if tool_use:
    print("ツール要求: ", tool_use)

#====================================
# 2回目の推論（ツール実行あり）
#====================================
if tool_use:
    year = tool_use["input"]["year"]
    holidays = get_japanese_holidays(year)
    tool_result = {
        "year": year,
        "holidays": holidays,
        "count": len(holidays)
    }
    print("[アプリから直後、ツール実行して結果を取得]")
    print(tool_result)
    print()

    messages = [
        {"role": "user", "content": [{"text": user_input}]},
        {"role": "assistant", "content": message["content"]},  # 1回目応答の生ブロックを渡す
        {"role": "user", "content": [{
            "toolResult": {
                "toolUseId": tool_use["toolUseId"],
                "content": [{"json": tool_result}]
            }
        }]}
    ]

    final_response = client.converse(
        modelId=llm,
        messages=messages,
        toolConfig={"tools": tools}
    )

    final_message = final_response["output"]["message"]
    final_text = extract_texts(final_message["content"])
    print("[推論2回目]")
    print("LLMの回答：", final_text if final_text else "(テキスト応答なし)")
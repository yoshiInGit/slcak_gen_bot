
import json
from gemini import extract_json_from_string, gemini_invoke


# タスクルーター
def task_router_prompt(message_str, events_str):
    
    return f"""
## タスク
あなたの役割は、ユーザーが送信したメッセージの内容に基づいて、事前に定義されたタスクリストから最も適切なイベントを選択することです。

## タスクデータ
タスクは以下のJSON形式で提供されています：
```json
{events_str}

```

## 選択プロセス
1. ユーザーのメッセージを解析し、目的、関心などの主要な情報を抽出してください
2. 抽出した情報をイベントリストの各イベントと照合します
3. 最も関連性の高いイベントを選択します
4. 選択したイベントのIDのみを返します

## 出力形式
選択したイベントのIDのみを次の形式で返してください：
```
event_1
```

## ユーザーメッセージ
{message_str}
"""

def taskRouter(message_str, events_json):
    gemini_prompt = task_router_prompt(message_str, json.dumps(events_json))
    response = gemini_invoke(gemini_prompt)
    return response.strip()  # 余分な空白を削除



# タスクの実行
def task_execute_prompt(user_message, task_instruction):
    return f"""
あなたはチャットボットアシスタントとして以下のユーザーメッセージについて指示に従ったタスクを実行して

ただし、普通のマークダウンを使うことは禁止されてます。以下ルールに従って、出力を装飾して。
<rule>
# Slackでのマークダウンのルール

## 基本的な書式設定

**太字**
- 書き方: `*太字*` または `**太字**`

*斜体*
- 書き方: `_斜体_` または `*斜体*`

~~取り消し線~~
- 書き方: `~取り消し線~`

`コード`
- 書き方: `` `コード` ``

```
コードブロック
```
- 書き方: ````コードブロック````

> 引用
- 書き方: `> 引用文`

## リスト

箇条書きリスト:
- 書き方: `• 項目1` または `- 項目1`

番号付きリスト:
1. 書き方: `1. 項目1`

## リンク

[リンクテキスト](https://example.com)
- 書き方: `<https://example.com>` または `[リンクテキスト](https://example.com)`

## その他の機能

### メンション
- ユーザーメンション: `@ユーザー名`
- チャンネルメンション: `#チャンネル名`
- 全員へのメンション: `@here` または `@channel`

### 絵文字
- 通常の絵文字: `:smile:` → 😄
- カスタム絵文字: `:カスタム絵文字名:`

### 区切り線
- 書き方: `---` または `***` または `___`
</rule>

## 指示
{task_instruction}

## ユーザーメッセージ
{user_message}
"""
def task_execute(user_message, task_instruction):
    gemini_prompt = task_execute_prompt(user_message, task_instruction)
    response = gemini_invoke(gemini_prompt)
    return response


# タスクの作成
def task_create_prompt(user_message):
    return f"""
AIにタスクを実行させるためのjsonデータを作成しようと思っています。ユーザーメッセージに従って、指定したjsonデータを作成してください。

# json形式
{{
 "name" : str,
 "description": str,
 "example_message":str[],
"instruction": str
}}

## 説明
- name : タスクの簡単な名前
- description: タスクの内容についての説明。タスクの発動条件を詳しく、様々可能性を想定して定義する。特に他のタスクと発動条件を区別きるようにする。
- example_message: このタスクを発動する具体的なユーザーからのメッセージの例
- instruction: AIに渡す、タスクを実行するためのプロンプト。プロンプトにはユーザーメッセージが自動的に渡される予定です。具体的なユーザーメッセージメッセージについてはここで記述しないこと。

## 例
```
{{
    "name": "アイデアだし",
    "description": "ユーザーが「○○のアイデア出して」と言ったら、アイデアを10個出すイベントです。",
    "example_message" : ["企業のアイデアを出して"、"業務効率化のアイデアをだして"],
    "instruction":"ユーザーメッセージに求められているアイデアを10個だして"
    }}
```
```
{{
    "name": "ポジティブ変換",
    "description": "ユーザーがネガティブなメッセージを書いていたとき、それをポジティブに変換する",
    "example_message" : ["失敗してつらい"、"将来が不安"],
    "instruction":"ユーザーメッセージをポジティブなものに変換して"
    }}
```

# ユーザーメッセージ
{user_message}


Assistant:json形成で一つだけ出力します。
"""

def create_task(user_message):
    gemini_prompt = task_create_prompt(user_message)
    response = gemini_invoke(gemini_prompt)
    
    task_json_none = extract_json_from_string(response)
    if task_json_none is None:
        print("タスクのjsonデータの生成に失敗しました")
    
    return task_json_none
    


if __name__ == "__main__":
    print(create_task("アイデアだし")) # テスト用のユーザーメッセージを指定

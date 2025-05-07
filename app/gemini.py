from google import genai
import os
from dotenv import load_dotenv
import re
import json


load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_KEY"))


def gemini_invoke(prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=prompt
    )    
    return response.text


def extract_json_from_string(text):
    # JSONブロックを正規表現で抽出
    # ```json と ``` の間にあるテキストを取得
    json_pattern = r'```json\n([\s\S]*?)\n```'
    match = re.search(json_pattern, text)
    
    if match:
        json_text = match.group(1)
        try:
            # 抽出したJSONテキストをパース
            json_data = json.loads(json_text)
            return json_data
        except json.JSONDecodeError as e:
            print(f"JSONのパースに失敗しました: {e}")
            return None
    else:
        print("JSONブロックが見つかりませんでした")
        return None

if __name__ == "__main__":
    prompt = "What is the capital of Japan?"
    response = gemini_invoke(prompt)
    print(response)

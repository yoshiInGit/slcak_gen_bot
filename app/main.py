import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from logic import logic_v1

# .env ファイルをロード
load_dotenv()

bot_token = os.getenv("SLACK_BOT_TOKEN")
app_token = os.getenv("SLACK_APP_TOKEN")

# Initializes your app with your bot token and socket mode handler
app = App(token=bot_token)

# メンションに反応
@app.event("app_mention")
def handle_mention(event, say):
    user_message = event["text"]
    
    res = logic_v1(user_message)

    say(
        text=res,
        thread_ts=event["ts"],  # スレッドに返信する場合は、スレッドのタイムスタンプを指定
    )

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, app_token).start()

import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack.utils import is_dm

load_dotenv()

app_token = os.getenv("SLACK_APP_TOKEN")
bot_token = os.getenv("SLACK_BOT_TOKEN")
app = App(token=bot_token)

@app.event("message")
def handle_message_events(message, say):
  if (is_dm(message)):
    say("Test message")
  return

def run_bot():
  SocketModeHandler(app, app_token).start()
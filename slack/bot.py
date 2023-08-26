import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack.utils import is_dm
from slack.response import response_using_llm

load_dotenv()

app_token = os.getenv("SLACK_APP_TOKEN")
bot_token = os.getenv("SLACK_BOT_TOKEN")
app = App(token=bot_token)

@app.event("message")
def handle_message_events(event, ack):
  if (is_dm(event)):
    response_using_llm(event, ack, app)
  return

user_reactions = {}

@app.event("reaction_added")
def handle_reaction(event, say):
  user_id = event["user"]
  reaction = event["reaction"]
  user_name = app.client.users_info(
    user=user_id
  )['user']['profile']['real_name']

  if user_id not in user_reactions:
    user_reactions[user_id] = reaction
    if reaction == '+1':
      response_text = f"Thank you {user_name} for your valued feedback!"
    elif reaction == '-1':
      response_text = f"Thank you {user_name} for your valued feedback!"
    say(response_text)
  else:
    response_text = f"Hi {user_name}, looks like you've already provided a feedback!"
    say(response_text)

def run_bot():
  SocketModeHandler(app, app_token).start()
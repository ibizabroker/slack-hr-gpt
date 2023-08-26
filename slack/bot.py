import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack.utils import is_dm
from slack.response import response_using_llm
from supabase_connect.wrapper import write_user_feedback

load_dotenv()

app_token = os.getenv("SLACK_APP_TOKEN")
bot_token = os.getenv("SLACK_BOT_TOKEN")
app = App(token=bot_token)

class SharedData:
  def __init__(self):
    self.user_query = None
    self.actual_output = None

shared_data = SharedData()
user_reactions = {}

@app.event("message")
def handle_message_events(event, ack):
  if (is_dm(event)):
    shared_data.user_query, shared_data.actual_output = response_using_llm(event, ack, app)
  return

@app.event("app_mention")
def handle_mention(event, ack):
  shared_data.user_query, shared_data.actual_output = response_using_llm(event, ack, app)

@app.event("reaction_added")
def handle_reaction(event, say):
  user_id = event["user"]
  message_id = event["item"]["ts"]
  reaction = event["reaction"]
  user_name = app.client.users_info(
    user=user_id
  )['user']['profile']['real_name']
  reaction_key = (user_id, message_id)

  actual_output_lines = shared_data.actual_output.strip().split("\n")
  actual_output_new_lines = actual_output_lines[:-3]
  actual_output_without_source = "\n".join(actual_output_new_lines)

  if reaction_key not in user_reactions:
    user_reactions[reaction_key] = reaction
    if reaction == '+1':
      write_user_feedback(
        user_name=user_name, 
        user_query=shared_data.user_query, 
        actual_output=actual_output_without_source, 
        reaction=reaction
      )

      response_text = f"Thank you {user_name} for your valued feedback!"
    elif reaction == '-1':
      write_user_feedback(
        user_name=user_name, 
        user_query=shared_data.user_query, 
        actual_output=actual_output_without_source,
        reaction=reaction
      )

      response_text = f"We're sorry {user_name}, to hear that the response wasn't satisfactory. Your feedback will help us improve our model!"
    say(response_text)
  else:
    response_text = f"Hi {user_name}, looks like you've already provided a feedback!"
    say(response_text)

def run_bot():
  SocketModeHandler(app, app_token).start()
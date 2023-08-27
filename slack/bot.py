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
        expected_output="",
        reaction=reaction
      )

      response_text = f"Thank you {user_name} for your valued feedback!"
      say(response_text)
    elif reaction == '-1':
      blocks = [
        {
          "dispatch_action": True,
          "type": "input",
          "element": {
            "type": "plain_text_input",
            "action_id": "plain_text_input-action",
          },
          "label": {
            "type": "plain_text",
            "text": "Enter the expected output:",
            "emoji": False,
          },
        }
      ]

      say(blocks=blocks)
  else:
    response_text = f"Hi {user_name}, looks like you've already provided a feedback!"
    say(response_text)

@app.action("plain_text_input-action")
def handle_input_submission(ack, body, respond):
  ack()

  user_id = body["user"]["id"]
  user_name = app.client.users_info(
    user=user_id
  )['user']['profile']['real_name']
  user_input = body["actions"][0]["value"]

  actual_output_lines = shared_data.actual_output.strip().split("\n")
  actual_output_new_lines = actual_output_lines[:-3]
  actual_output_without_source = "\n".join(actual_output_new_lines)

  write_user_feedback(
    user_name=user_name,
    user_query=shared_data.user_query,
    actual_output=actual_output_without_source,
    expected_output=user_input,
    reaction="-1"
  )

  thank_you_message = {
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": f"Thank you {user_name} for your valued feedback!",
        },
      }
    ]
  }

  respond(thank_you_message)

def run_bot():
  SocketModeHandler(app, app_token).start()
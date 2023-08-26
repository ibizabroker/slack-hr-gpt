from llm.llm import get_response
from slack.utils import send_message_and_get_message_id

def response_using_llm(event, ack, app):
  channel = event["channel"]

  ack()
  ack_message_id = send_message_and_get_message_id(
    app=app, 
    channel=channel, 
    message="Processing..."
  )

  user_query = event["text"]

  response = get_response(
    input=user_query
  )

  blocks = [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": response
      }
    }
  ]

  app.client.chat_update(
    channel=channel,
    text=response,
    ts=ack_message_id,
    blocks=blocks
  )

  app.client.reactions_add(
    channel=channel,
    timestamp=ack_message_id,
    name='thumbsup'
  )

  app.client.reactions_add(
    channel=channel,
    timestamp=ack_message_id,
    name='thumbsdown'
  )
def is_dm(message) -> bool:
  channel_type = message["channel_type"]
  if channel_type != "im":
    return False
  return True

def send_message_and_get_message_id(app, channel, message: str):
  response = app.client.chat_postMessage(
    channel=channel,
    text=message
  )
  if response["ok"]:
    message_id = response["message"]["ts"]
    return message_id
  else:
    return ("Failed to send the message.")
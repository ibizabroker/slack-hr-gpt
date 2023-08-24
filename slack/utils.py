def is_dm(message) -> bool:
  channel_type = message["channel_type"]
  if channel_type != "im":
    return False
  return True
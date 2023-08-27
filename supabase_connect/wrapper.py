import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def write_user_feedback(user_name: str, user_query: str, actual_output: str, expected_output: str, reaction: str):
  supabase.table('hr-gpt-feedback').insert(
    {
      "user_name": user_name,
      "user_query": user_query,
      "actual_output": actual_output,
      "expected_output": expected_output,
      "reaction": reaction
    }
  ).execute()
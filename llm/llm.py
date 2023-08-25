import os
import pinecone
from langchain.vectorstores.pinecone import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from llm.chain import get_conversation_chain
from dotenv import load_dotenv

load_dotenv()

def load_chain():
  embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY")
  )

  pinecone_api_key=os.getenv("PINECONE_API_KEY")
  pinecone_env_key=os.getenv("PINECONE_ENV_KEY")

  pinecone.init(
    api_key=pinecone_api_key,
    environment=pinecone_env_key
  )
  index_name = "hr-data"

  vectordb = Pinecone.from_existing_index(index_name, embeddings)

  return get_conversation_chain(vectordb)

def get_response(input):
  chain_result = None

  chain = load_chain()
  chain_result = chain({
    "question": input
  })
  chat_history = chain_result['chat_history']
  output = ''

  for i, message in enumerate(reversed(chat_history)):
    if i % 2 == 0:
      output = message.content

  return output
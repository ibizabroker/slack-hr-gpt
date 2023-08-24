import os
import pinecone
from langchain.vectorstores.pinecone import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFDirectoryLoader
from dotenv import load_dotenv

load_dotenv()

def main():
  pdfs = PyPDFDirectoryLoader('../pdfs/')
  data = pdfs.load()

  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=100
  )

  docs = text_splitter.split_documents(data)

  embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv('OPENAI_API_KEY')
  )

  pinecone_api_key=os.getenv('PINECONE_API_KEY')
  pinecone_env_key=os.getenv('PINECONE_ENV_KEY')

  pinecone.init(
    api_key=pinecone_api_key, 
    environment=pinecone_env_key
  )
  index_name = "hr-data"

  vectordb = Pinecone.from_documents(docs, embeddings, index_name=index_name)
  print("Data ingested.")

  return vectordb

if __name__ == '__main__':
  main()
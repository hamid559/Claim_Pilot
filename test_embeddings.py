import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

vector = embeddings.embed_query(
    "Phone screen damaged accidentally"
)

print("Embedding dimension:", len(vector))
print("First 5 values:", vector[:5])
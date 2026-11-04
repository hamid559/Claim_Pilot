from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite"
)

response = llm.invoke(
    "Classify this query as SIMPLE or COMPLEX. "
    "Query: What documents are required for a phone damage claim? "
    "Reply with only SIMPLE or COMPLEX."
)

print(response.content)
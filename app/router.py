from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI


router_llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite"
)


def classify_query(query: str) -> str:
    prompt = f"""
Classify the following insurance assistant query as exactly one of:

SIMPLE
COMPLEX

SIMPLE:
- Single policy lookup
- Straightforward question
- No claim ID
- No multi-step reasoning

COMPLEX:
- Contains a claim ID
- Requires claim lookup
- Requires eligibility assessment
- Requires reasoning across multiple policy sections
- Requires multiple tools

Query:
{query}

Return ONLY:
SIMPLE
or
COMPLEX
"""

    response = router_llm.invoke(prompt)

    content = response.content

    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                content = item.get("text", "")
                break

    return content.strip().upper()
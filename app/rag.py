import re
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

load_dotenv()


POLICY_PATH = Path("data/policies/mobile_protection_policy.txt")


def load_policy():
    """Load the insurance policy."""

    return POLICY_PATH.read_text(encoding="utf-8")


def create_policy_chunks():
    text = load_policy()

    sections = re.split(
        r"(?=SECTION \d+|^\d+\.\d+)",
        text,
        flags=re.MULTILINE
    )

    sections = [
        section.strip()
        for section in sections
        if section.strip()
    ]

    return [
        Document(page_content=section)
        for section in sections
    ]


def create_vector_store():
    """Create FAISS vector store from policy chunks."""

    chunks = create_policy_chunks()

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001"
    )

    return FAISS.from_documents(
        chunks,
        embeddings,
    )


def create_retriever():
    """Create policy retriever."""

    vector_store = create_vector_store()

    return vector_store.as_retriever(
        search_kwargs={"k": 2}
    )


def answer_policy_question(query):
    """Answer a user question using retrieved policy evidence."""

    retriever = create_retriever()

    documents = retriever.invoke(query)

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite"
    )

    prompt = f"""
You are ClaimPilot, an insurance claims assistant.

Answer the user's question using ONLY the policy
evidence provided below.

IMPORTANT RULES:

1. Do not invent policy rules.
2. Do not use outside knowledge.
3. If the evidence is insufficient, say that the claim
   requires human review.
4. Clearly distinguish between covered and excluded cases.
5. Give the relevant policy section in the answer.
6. Keep the answer concise and professional.

POLICY EVIDENCE:
----------------
{context}
----------------

USER QUESTION:
{query}

Provide:

Answer:
<your answer>

Policy basis:
<relevant policy section(s)>

Confidence:
HIGH / MEDIUM / LOW
"""

    response = llm.invoke(prompt)

    content = response.content

    if isinstance(content, list):
        text_parts = []

        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))

        content = "\n".join(text_parts)

    return content, documents
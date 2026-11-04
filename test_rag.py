from app.rag import create_retriever


retriever = create_retriever()

query = "Is accidental screen damage covered?"

documents = retriever.invoke(query)

print("\n===== RETRIEVED POLICY CLAUSES =====\n")

for i, doc in enumerate(documents, start=1):
    print(f"--- RESULT {i} ---")
    print(doc.page_content)
    print()
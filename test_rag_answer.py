from app.rag import answer_policy_question


query = "Is accidental screen damage covered?"

answer, documents = answer_policy_question(query)

print("\n==============================")
print("CLAIMPILOT ANSWER")
print("==============================\n")

print(answer)

print("\n==============================")
print("RETRIEVED SOURCES")
print("==============================\n")

for i, document in enumerate(documents, start=1):
    print(f"[Source {i}]")
    print(document.page_content[:500])
    print()
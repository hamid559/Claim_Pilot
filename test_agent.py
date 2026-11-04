from app.agent import workflow


query = """
Analyze claim CLM001.

Tell me:
1. What happened?
2. Is the customer potentially eligible?
3. What policy evidence supports this?
4. What documents are required?
"""


result = workflow.invoke({
    "messages": [
        {
            "role": "user",
            "content": query
        }
    ]
})


print("\nFINAL ANSWER:\n")

final_message = result["messages"][-1]

content = final_message.content

if isinstance(content, list):
    text_parts = []

    for item in content:
        if isinstance(item, dict) and item.get("type") == "text":
            text_parts.append(item.get("text", ""))

    content = "\n".join(text_parts)

print(content)
from app.router import classify_query
from app.rag import answer_policy_question
from app.agent import workflow


def run_claimpilot(query: str):
    route = classify_query(query)

    if route == "SIMPLE":
        answer, documents = answer_policy_question(query)

        return {
            "route": "SIMPLE",
            "answer": answer,
            "sources": [
                doc.page_content for doc in documents
            ]
        }

    else:
        result = workflow.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ]
        })

        messages = result["messages"]

        # Get the final AI response
        final_message = messages[-1]

        content = final_message.content

        if isinstance(content, list):
            text_parts = []

            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))

            content = "\n".join(text_parts)

        return {
            "route": "COMPLEX",
            "answer": content,
            "sources": []
        }
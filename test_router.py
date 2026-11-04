from app.router import classify_query


queries = [
    "What documents are required for a damage claim?",
    "Is accidental screen damage covered?",
    "Analyze claim CLM001 and determine whether the customer is potentially eligible.",
    "Check CLM003 and explain why it may or may not qualify.",
]


for query in queries:

    result = classify_query(query)

    print("\nQuery:", query)
    print("Route:", result)
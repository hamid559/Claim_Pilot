from app.pipeline import run_claimpilot


queries = [
    "Is accidental screen damage covered?",
    "What documents are required for a damage claim?",
    "Analyze claim CLM001 and determine whether the customer is potentially eligible.",
    "Check CLM003 and explain why it may or may not qualify."
]


for query in queries:
    print("\n" + "=" * 70)
    print("QUERY:", query)

    result = run_claimpilot(query)

    print("ROUTE:", result["route"])
    print("\nANSWER:")
    print(result["answer"])
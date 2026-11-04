import time
import re

from app.rag import create_retriever
from app.tools import check_eligibility


# --------------------------------------------------
# 1. Golden retrieval dataset
# --------------------------------------------------

RETRIEVAL_DATASET = [
    {
        "question": "Is accidental screen damage covered?",
        "expected_sections": ["2.1"],
    },
    {
        "question": "Are cosmetic scratches covered?",
        "expected_sections": ["2.3"],
    },
    {
        "question": "What documents are required for a damage claim?",
        "expected_sections": ["5.1"],
    },
    {
        "question": "Are lost or stolen devices covered?",
        "expected_sections": ["4.4"],
    },
    {
        "question": "Is liquid damage covered?",
        "expected_sections": ["3.1", "3.2"],
    },
    {
        "question": "What happens if the protection plan is inactive?",
        "expected_sections": ["1.2"],
    },
]


# --------------------------------------------------
# 2. Extract section numbers
# --------------------------------------------------

def extract_sections(text):
    """
    Extract policy section numbers such as:
    2.1, 2.3, 5.1, 4.4
    """

    return set(re.findall(r"\b\d+\.\d+\b", text))


# --------------------------------------------------
# 3. Retrieval metrics
# --------------------------------------------------

def evaluate_retrieval():

    retriever = create_retriever()

    precisions = []
    recalls = []
    reciprocal_ranks = []

    print("\n" + "=" * 70)
    print("RAG RETRIEVAL EVALUATION")
    print("=" * 70)

    for item in RETRIEVAL_DATASET:

        question = item["question"]
        expected = set(item["expected_sections"])

        start = time.perf_counter()

        documents = retriever.invoke(question)

        latency = time.perf_counter() - start

        retrieved_sections = []

        for doc in documents:
            sections = extract_sections(doc.page_content)
            retrieved_sections.append(sections)

        # Flatten all retrieved sections
        all_retrieved = set()

        for sections in retrieved_sections:
            all_retrieved.update(sections)

        # Relevant retrieved sections
        relevant = expected.intersection(all_retrieved)

        # Precision
        if len(all_retrieved) > 0:
            precision = len(relevant) / len(all_retrieved)
        else:
            precision = 0

        # Recall
        recall = len(relevant) / len(expected)

        # MRR
        reciprocal_rank = 0

        for rank, sections in enumerate(retrieved_sections, start=1):

            if expected.intersection(sections):
                reciprocal_rank = 1 / rank
                break

        precisions.append(precision)
        recalls.append(recall)
        reciprocal_ranks.append(reciprocal_rank)

        print(f"\nQuestion: {question}")
        print(f"Expected: {sorted(expected)}")
        print(f"Retrieved: {sorted(all_retrieved)}")
        print(f"Precision: {precision:.2f}")
        print(f"Recall: {recall:.2f}")
        print(f"MRR: {reciprocal_rank:.2f}")
        print(f"Latency: {latency:.3f}s")

    avg_precision = sum(precisions) / len(precisions)
    avg_recall = sum(recalls) / len(recalls)
    avg_mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)

    print("\n" + "-" * 70)
    print("OVERALL RESULTS")
    print("-" * 70)

    print(f"Precision@K : {avg_precision:.3f}")
    print(f"Recall@K    : {avg_recall:.3f}")
    print(f"MRR         : {avg_mrr:.3f}")


# --------------------------------------------------
# 4. Eligibility evaluation
# --------------------------------------------------

ELIGIBILITY_DATASET = [
    {
        "claim": "CLM001",
        "plan_status": "ACTIVE",
        "incident": "Accidental drop",
        "damage": "Cracked screen",
        "expected": "POTENTIALLY ELIGIBLE",
    },
    {
        "claim": "CLM002",
        "plan_status": "ACTIVE",
        "incident": "Accidental drop",
        "damage": "Minor scratches",
        "expected": "NOT ELIGIBLE",
    },
    {
        "claim": "CLM003",
        "plan_status": "INACTIVE",
        "incident": "Accidental drop",
        "damage": "Cracked screen",
        "expected": "NOT ELIGIBLE",
    },
]


def evaluate_eligibility():

    correct = 0

    print("\n" + "=" * 70)
    print("ELIGIBILITY TOOL EVALUATION")
    print("=" * 70)

    for item in ELIGIBILITY_DATASET:

        start = time.perf_counter()

        result = check_eligibility.invoke({
            "plan_status": item["plan_status"],
            "incident": item["incident"],
            "damage": item["damage"],
        })

        latency = time.perf_counter() - start

        # Tool returns text containing the decision
        if item["expected"] in result:
            correct += 1
            status = "PASS"
        else:
            status = "FAIL"

        print(f"\nClaim: {item['claim']}")
        print(f"Expected: {item['expected']}")
        print(f"Result: {result}")
        print(f"Status: {status}")
        print(f"Latency: {latency:.6f}s")

    accuracy = correct / len(ELIGIBILITY_DATASET)

    print("\n" + "-" * 70)
    print(f"Eligibility Accuracy: {accuracy:.3f}")
    print("-" * 70)


# --------------------------------------------------
# 5. Run evaluation
# --------------------------------------------------

if __name__ == "__main__":

    evaluate_retrieval()

    evaluate_eligibility()
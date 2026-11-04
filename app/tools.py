import sqlite3

from langchain_core.tools import tool

from app.database import get_connection
from app.rag import create_retriever


@tool
def search_policy(query: str) -> str:
    """
    Search the insurance policy for relevant coverage rules,
    exclusions, eligibility requirements, and claim requirements.
    """

    retriever = create_retriever()

    documents = retriever.invoke(query)

    if not documents:
        return "No relevant policy information was found."

    results = []

    for i, document in enumerate(documents, start=1):
        results.append(
            f"[Policy Source {i}]\n{document.page_content}"
        )

    return "\n\n".join(results)


@tool
def lookup_claim(claim_id: str) -> str:
    """
    Look up a claim and its associated customer information
    from the claims database.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            c.claim_id,
            c.customer_id,
            c.device,
            c.incident,
            c.damage,
            c.claim_status,
            cu.name,
            cu.plan_type,
            cu.plan_status,
            cu.enrollment_date
        FROM claims c
        JOIN customers cu
            ON c.customer_id = cu.customer_id
        WHERE c.claim_id = ?
        """,
        (claim_id,),
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return f"No claim found with ID {claim_id}."

    return f"""
Claim ID: {row[0]}
Customer ID: {row[1]}
Device: {row[2]}
Incident: {row[3]}
Damage: {row[4]}
Claim Status: {row[5]}

Customer Name: {row[6]}
Plan Type: {row[7]}
Plan Status: {row[8]}
Enrollment Date: {row[9]}
"""


@tool
def check_eligibility(
    plan_status: str,
    incident: str,
    damage: str,
) -> str:
    """
    Perform a deterministic first-pass eligibility assessment
    using the policy rules represented in the system.
    """

    reasons = []

    if plan_status.upper() != "ACTIVE":
        return (
            "NOT ELIGIBLE: The customer does not have an active "
            "protection plan."
        )

    incident_lower = incident.lower()
    damage_lower = damage.lower()

    if "drop" in incident_lower and "crack" in damage_lower:
        reasons.append(
            "Accidental drop with cracked screen matches "
            "the accidental physical damage category."
        )

    if "scratch" in damage_lower or "dent" in damage_lower:
        return (
            "NOT ELIGIBLE: The reported damage appears to be "
            "cosmetic damage, which is excluded."
        )

    if not reasons:
        return (
            "REQUIRES HUMAN REVIEW: The available deterministic "
            "rules do not establish eligibility."
        )

    return (
        "POTENTIALLY ELIGIBLE: "
        + " ".join(reasons)
        + " Final determination should be based on the "
          "applicable policy evidence."
    )
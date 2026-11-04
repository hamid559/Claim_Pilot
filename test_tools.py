from app.tools import (
    search_policy,
    lookup_claim,
    check_eligibility,
)


print("\n==============================")
print("TEST 1 — POLICY SEARCH")
print("==============================\n")

policy_result = search_policy.invoke(
    "Is accidental screen damage covered?"
)

print(policy_result)


print("\n==============================")
print("TEST 2 — CLAIM LOOKUP")
print("==============================\n")

claim_result = lookup_claim.invoke(
    "CLM001"
)

print(claim_result)


print("\n==============================")
print("TEST 3 — ELIGIBILITY")
print("==============================\n")

eligibility_result = check_eligibility.invoke(
    {
        "plan_status": "ACTIVE",
        "incident": "Accidental drop",
        "damage": "Cracked screen",
    }
)

print(eligibility_result)
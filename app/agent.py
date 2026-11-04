from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.tools import (
    search_policy,
    lookup_claim,
    check_eligibility,
)


# --------------------------------------------------
# 1. Agent state
# --------------------------------------------------

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# --------------------------------------------------
# 2. LLM
# --------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite"
)


# --------------------------------------------------
# 3. Tools
# --------------------------------------------------

tools = [
    search_policy,
    lookup_claim,
    check_eligibility,
]

llm_with_tools = llm.bind_tools(tools)


# --------------------------------------------------
# 4. Agent node
# --------------------------------------------------

def agent_node(state: AgentState):

    system_instruction = """
You are ClaimPilot, an AI insurance claims assistant.

Your job is to help insurance employees analyze customer
claims using approved policy information and structured
claim data.

AVAILABLE TOOLS:

1. search_policy
   Search the insurance policy for coverage rules,
   exclusions, eligibility requirements, and claim
   requirements.

2. lookup_claim
   Retrieve customer and claim information.

3. check_eligibility
   Perform a deterministic first-pass eligibility check.

WORKFLOW:

When a claim ID is provided:

1. Look up the claim.
2. Check the customer's plan status.
3. Search the policy for the relevant coverage rule.
4. Use the eligibility tool when enough information exists.
5. Produce a concise final assessment.

RULES:

- Never invent policy rules.
- Never use outside knowledge.
- Use policy evidence for coverage decisions.
- Use the database for customer and claim facts.
- Use deterministic eligibility results when available.
- If policy evidence is insufficient or conflicting,
  recommend human review.
- Do not say a claim is definitively approved unless
  the available evidence explicitly supports approval.
- "Potentially eligible" means the available evidence
  supports coverage but final claim approval requires
  normal claims review.

FINAL RESPONSE FORMAT:

Claim:
<claim ID>

Assessment:
<POTENTIALLY ELIGIBLE / NOT ELIGIBLE / HUMAN REVIEW>

Incident:
<brief description>

Reason:
<2-4 sentences explaining the decision>

Required Documents:
<bullet list if available>

Policy Sources:
<list the relevant policy section numbers and names>

Do not print raw tool outputs in the final response.
Do not repeat the entire policy.
"""

    messages = state["messages"]

    response = llm_with_tools.invoke(
        [
            HumanMessage(content=system_instruction)
        ] + messages
    )

    return {
        "messages": [response]
    }


# --------------------------------------------------
# 5. Decide whether to call a tool
# --------------------------------------------------

def should_continue(state: AgentState):

    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return END


# --------------------------------------------------
# 6. Build graph
# --------------------------------------------------

workflow = StateGraph(AgentState)

workflow.add_node(
    "agent",
    agent_node
)

workflow.add_node(
    "tools",
    ToolNode(tools)
)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END,
    },
)

workflow.add_edge(
    "tools",
    "agent"
)

workflow = workflow.compile()
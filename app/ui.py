import streamlit as st

from app.pipeline import run_claimpilot


st.set_page_config(
    page_title="ClaimPilot",
    page_icon="🛡️",
    layout="wide"
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🛡️ ClaimPilot")
st.subheader("Agentic RAG Insurance Claims Assistant")

st.write(
    "Analyze insurance claims using policy evidence, "
    "structured claim data, and deterministic eligibility checks."
)


# --------------------------------------------------
# Example queries
# --------------------------------------------------

st.markdown("### Try an example")

examples = [
    "Is accidental screen damage covered?",
    "What documents are required for a damage claim?",
    "Analyze claim CLM001 and determine whether the customer is potentially eligible.",
    "Check CLM003 and explain why it may or may not qualify."
]

selected_example = st.selectbox(
    "Example queries",
    ["Select a query"] + examples
)


# --------------------------------------------------
# User input
# --------------------------------------------------

query = st.text_area(
    "Ask ClaimPilot",
    value="" if selected_example == "Select a query" else selected_example,
    height=100,
    placeholder="Example: Analyze claim CLM001..."
)


# --------------------------------------------------
# Run
# --------------------------------------------------

if st.button("Analyze", type="primary"):

    if not query.strip():
        st.warning("Please enter a question.")
        st.stop()

    with st.spinner("ClaimPilot is analyzing..."):

        try:
            result = run_claimpilot(query)

        except Exception as e:
            st.error(
                "ClaimPilot could not process this request. "
                "Check the terminal for details."
            )
            st.stop()


    # --------------------------------------------------
    # Route
    # --------------------------------------------------

    route = result["route"]

    if route == "SIMPLE":
        st.info("🔎 Route: SIMPLE RAG")

    else:
        st.info("🤖 Route: COMPLEX AGENT")


    # --------------------------------------------------
    # Answer
    # --------------------------------------------------

    st.markdown("## Assessment")

    st.markdown(result["answer"])


    # --------------------------------------------------
    # Sources
    # --------------------------------------------------

    sources = result.get("sources", [])

    if sources:

        st.markdown("## Policy Evidence")

        for i, source in enumerate(sources, start=1):

            with st.expander(f"Policy Source {i}"):

                st.write(source)
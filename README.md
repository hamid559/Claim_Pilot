# 🛡️ ClaimPilot — Agentic RAG Insurance Claims Assistant

> An AI-powered insurance claims assistant that combines **LLM-based query routing, Retrieval-Augmented Generation (RAG), LangGraph agentic workflows, structured claim data, and deterministic eligibility checks**.

---

## 📌 Overview

**ClaimPilot** is an insurance claims assistant designed to help analyze policy questions and customer claims using a combination of:

* **Google Gemini** for language understanding and reasoning
* **FAISS** for semantic policy retrieval
* **LangGraph** for multi-step agentic workflows
* **SQLite** for structured customer and claim data
* **Deterministic eligibility rules** for first-pass claim assessment

The system uses a **two-stage architecture**:

1. A Gemini-based router classifies the query as either `SIMPLE` or `COMPLEX`.
2. Simple queries are handled through a direct RAG pipeline, while complex queries are passed to a LangGraph agent that can use specialized tools.

---

# 🏗️ Architecture

```text
                         ┌───────────────┐
                         │   User Query  │
                         └───────┬───────┘
                                 │
                                 ▼
                     ┌──────────────────────┐
                     │    Gemini Router      │
                     │  SIMPLE / COMPLEX    │
                     └──────────┬───────────┘
                                │
                  ┌─────────────┴─────────────┐
                  │                           │
               SIMPLE                      COMPLEX
                  │                           │
                  ▼                           ▼
        ┌──────────────────┐        ┌──────────────────┐
        │    Direct RAG    │        │    LangGraph     │
        │                  │        │      Agent       │
        └────────┬─────────┘        └────────┬─────────┘
                 │                           │
                 ▼                    ┌──────┼───────┐
        ┌──────────────────┐          │      │       │
        │ FAISS Retriever  │          ▼      ▼       ▼
        └────────┬─────────┘       Policy  Claim  Eligibility
                 │                 Search  Lookup    Tool
                 ▼                    │      │       │
        ┌──────────────────┐           └──────┼───────┘
        │ Gemini Response  │                  │
        └────────┬─────────┘                  ▼
                 │                    ┌──────────────────┐
                 │                    │ Gemini Reasoning │
                 │                    └────────┬─────────┘
                 │                             │
                 └──────────────┬──────────────┘
                                ▼
                         Final Assessment
```

---

# 🔄 How ClaimPilot Works

## Step 1 — Query Classification

Every incoming query first passes through the Gemini-based router.

The router classifies the query as:

```text
SIMPLE
```

or

```text
COMPLEX
```

### SIMPLE queries

A query is considered simple when it involves:

* A single policy lookup
* A straightforward question
* No claim ID
* No multi-step reasoning

Example:

```text
Is accidental screen damage covered?
```

### COMPLEX queries

A query is considered complex when it:

* Contains a claim ID
* Requires claim lookup
* Requires eligibility assessment
* Requires reasoning across multiple policy sections
* Requires multiple tools

Example:

```text
Analyze claim CLM001 and determine whether the customer is potentially eligible.
```

---

# 🔎 SIMPLE Route — Direct RAG

Simple policy questions bypass the agentic workflow and are answered using a dedicated RAG pipeline.

```text
User Query
    ↓
Google Gemini Embedding
    ↓
FAISS Similarity Search
    ↓
Top 4 Policy Sections
    ↓
Gemini
    ↓
Answer + Policy Basis + Confidence
```

## Policy Processing

ClaimPilot loads the policy document:

```text
data/policies/mobile_protection_policy.txt
```

The policy is divided into sections using section-number patterns.

Each section is converted into a LangChain `Document`.

These documents are embedded using:

```text
gemini-embedding-001
```

and indexed in a FAISS vector store.

The retriever returns the **top 4 relevant documents**.

---

## Grounded Answer Generation

The retrieved policy sections are passed to Gemini with instructions to:

* Use only the provided policy evidence
* Avoid outside knowledge
* Avoid inventing policy rules
* Distinguish covered and excluded cases
* Include relevant policy sections
* Provide a confidence level

The response follows this structure:

```text
Answer:
...

Policy basis:
...

Confidence:
HIGH / MEDIUM / LOW
```

---

# 🤖 COMPLEX Route — Agentic Workflow

Complex queries are handled by a **LangGraph-based agent**.

The workflow is:

```text
                         User Query
                             │
                             ▼
                     ┌───────────────┐
                     │ Gemini Agent  │
                     └───────┬───────┘
                             │
                       Tool required?
                         /        \
                       Yes         No
                       │            │
                       ▼            ▼
                  ┌─────────┐     END
                  │ ToolNode│
                  └────┬────┘
                       │
                       ▼
                 Tool Result
                       │
                       ▼
                 Gemini Agent
                       │
                 Tool required?
                    /      \
                  Yes       No
                  │          │
                  └─────┐    ▼
                        │   END
                        ▼
                    Final Answer
```

LangGraph allows the agent to repeatedly alternate between reasoning and tool execution until it has enough information to produce the final response.

---

# 🧰 Agent Tools

ClaimPilot provides three specialized tools.

## 1. `search_policy`

Searches the insurance policy for:

* Coverage rules
* Exclusions
* Eligibility requirements
* Claim requirements

It uses the same FAISS-based policy retriever used by the simple RAG pipeline.

---

## 2. `lookup_claim`

Retrieves structured claim and customer information from SQLite.

The database contains:

### Customer information

* Customer ID
* Name
* Plan type
* Plan status
* Enrollment date

### Claim information

* Claim ID
* Customer ID
* Device
* Incident
* Damage
* Claim status

The customer and claim tables are joined using the customer ID.

---

## 3. `check_eligibility`

Performs a **deterministic first-pass eligibility assessment**.

The current rules include:

### Inactive plan

```text
NOT ELIGIBLE
```

if the customer's protection plan is not active.

### Accidental drop + cracked screen

```text
POTENTIALLY ELIGIBLE
```

when the plan is active and the incident/damage combination matches the implemented accidental physical damage rule.

### Cosmetic damage

```text
NOT ELIGIBLE
```

for reported scratches or dents.

### Unhandled cases

```text
REQUIRES HUMAN REVIEW
```

when the deterministic rules cannot establish eligibility.

> **Important:** `POTENTIALLY ELIGIBLE` is not a final approval. Final claim determination requires normal claims review.

---

# 🧠 Complex Claim Analysis

For a query containing a claim ID, the agent is instructed to follow this workflow:

```text
Claim ID
   ↓
Look up claim
   ↓
Check customer / plan status
   ↓
Search relevant policy
   ↓
Run eligibility tool when sufficient information exists
   ↓
Combine evidence
   ↓
Generate final assessment
```

The agent is instructed to:

* Never invent policy rules
* Never use outside knowledge
* Use the database for claim/customer facts
* Use policy retrieval for coverage decisions
* Use deterministic eligibility results when available
* Recommend human review when evidence is insufficient or conflicting
* Avoid claiming definitive approval without supporting evidence

---

# 📊 Evaluation

ClaimPilot includes a dedicated evaluation module for measuring both **retrieval quality** and **eligibility-tool correctness**.

---

## 🔎 RAG Retrieval Evaluation

The retrieval evaluation uses a manually created golden dataset containing **6 policy questions**.

Examples include:

```text
Is accidental screen damage covered?
Are cosmetic scratches covered?
What documents are required for a damage claim?
Are lost or stolen devices covered?
Is liquid damage covered?
What happens if the protection plan is inactive?
```

Expected policy section numbers are defined for each question.

The evaluation calculates:

* Precision@K
* Recall@K
* Mean Reciprocal Rank (MRR)
* Retrieval latency

### Results

| Metric      |     Score |
| ----------- | --------: |
| Precision@K | **0.583** |
| Recall@K    | **1.000** |
| MRR         | **1.000** |

These results are based on the project's six-query evaluation dataset and the section-matching methodology implemented in `evaluation.py`.

---

# ✅ Eligibility Tool Evaluation

The deterministic eligibility tool is evaluated using three representative claims:

| Claim  | Scenario                                         | Expected             |
| ------ | ------------------------------------------------ | -------------------- |
| CLM001 | Active plan + accidental drop + cracked screen   | POTENTIALLY ELIGIBLE |
| CLM002 | Active plan + accidental drop + scratches        | NOT ELIGIBLE         |
| CLM003 | Inactive plan + accidental drop + cracked screen | NOT ELIGIBLE         |

The evaluation checks whether the tool output contains the expected decision and measures execution latency.

### Evaluation Result

```text
Eligibility Accuracy: 1.000
```

This corresponds to **3/3 correct results** on the included evaluation cases.

---

# 🗄️ Database

ClaimPilot uses SQLite for structured claim and customer information.

Database location:

```text
data/claims.db
```

The database contains two tables:

```text
customers
    │
    └── customer_id
             │
             ▼
          claims
```

### `customers`

```text
customer_id
name
plan_type
plan_status
enrollment_date
```

### `claims`

```text
claim_id
customer_id
device
incident
damage
claim_status
```

The project includes seed data for three sample claims:

```text
CLM001
CLM002
CLM003
```

---

# 📁 Project Structure

```text
ClaimPilot/
│
├── app/
│   ├── agent.py          # LangGraph agent and tool-calling workflow
│   ├── database.py       # SQLite database setup and seed data
│   ├── evaluation.py     # RAG and eligibility evaluation
│   ├── pipeline.py       # Main SIMPLE / COMPLEX routing pipeline
│   ├── rag.py            # Policy loading, embeddings, FAISS and RAG
│   ├── router.py         # Gemini-based query classifier
│   ├── tools.py          # Policy, claim and eligibility tools
│   └── ui.py             # Streamlit interface
│
├── data/
│   ├── policies/
│   │   └── mobile_protection_policy.txt
│   │
│   └── claims.db
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# 🛠️ Tech Stack

## Generative AI

* Google Gemini
* LangChain
* LangGraph

## Retrieval

* FAISS
* Google Gemini Embeddings
* Retrieval-Augmented Generation (RAG)

## Backend / Data

* Python
* SQLite
* SQL

## Application

* Streamlit

## Document Processing

* LangChain text splitters
* Regular-expression based policy section parsing

## Evaluation

* Python
* Retrieval metrics
* Deterministic tool evaluation
* Latency measurement

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/PrateekJha14/ClaimPilot.git
cd ClaimPilot
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
```

The application uses Google Gemini for:

* Query classification
* Policy answer generation
* Agent reasoning
* Policy embeddings

**Never commit your API key to GitHub.**

---

# 🗄️ Initialize the Database

Before running the application, initialize and seed the SQLite database:

```bash
python -m app.database
```

This creates:

```text
data/claims.db
```

and populates it with the sample customer and claim data.

---

# ▶️ Run ClaimPilot

Launch the Streamlit application:

```bash
streamlit run app/ui.py
```

The application provides:

* Example queries
* User query input
* Route display
* Final assessment
* Policy evidence for SIMPLE RAG queries

---

# 🧪 Run Evaluations

Run the complete evaluation module:

```bash
python -m app.evaluation
```

This evaluates:

1. RAG retrieval performance
2. Eligibility-tool accuracy

The evaluation also reports retrieval/tool latency.

---

# 💡 Example Queries

### Simple policy query

```text
Is accidental screen damage covered?
```

Expected route:

```text
SIMPLE RAG
```

---

### Policy requirements

```text
What documents are required for a damage claim?
```

Expected route:

```text
SIMPLE RAG
```

---

### Complex claim analysis

```text
Analyze claim CLM001 and determine whether the customer is potentially eligible.
```

Expected route:

```text
COMPLEX AGENT
```

The agent can combine:

```text
Claim Database
       +
Policy Retrieval
       +
Eligibility Tool
       ↓
Final Assessment
```

---

# 🎯 Design Principles

### 1. Route simple queries efficiently

Straightforward policy questions do not need a full agentic workflow, so ClaimPilot handles them through direct RAG.

### 2. Use agentic reasoning for complex cases

Queries requiring claim information, multiple tools, or multi-step reasoning are handled using LangGraph.

### 3. Ground policy decisions in retrieved evidence

The system instructs the LLM to rely on the provided policy evidence rather than external knowledge.

### 4. Keep deterministic logic separate from LLM reasoning

Eligibility rules are implemented as a dedicated tool instead of asking the LLM to make the rule-based decision itself.

### 5. Escalate uncertain cases

When available evidence is insufficient or conflicting, the system can recommend human review instead of forcing a definitive decision.

---

# ⚠️ Limitations

ClaimPilot is a **prototype / educational project** and is not intended to make autonomous real-world insurance claim decisions.

Current limitations include:

* Uses a single sample mobile protection policy
* Uses synthetic/sample claim and customer data
* Eligibility rules cover only the scenarios implemented in `check_eligibility`
* LLM-based routing can potentially misclassify a query
* LLM responses can still contain errors
* Policy retrieval depends on the quality of the underlying embeddings and retrieved sections
* No production insurance-system integration
* No production authentication or authorization
* No human review interface beyond the recommendation generated by the assistant

---

# 🔮 Future Improvements

* [ ] Add more insurance policy documents
* [ ] Support multiple insurance products
* [ ] Add hybrid keyword + vector retrieval
* [ ] Add reranking for retrieved policy sections
* [ ] Add policy/document citations in the UI
* [ ] Expand deterministic eligibility rules
* [ ] Add human-in-the-loop claim review
* [ ] Add claim-document upload
* [ ] Add OCR for scanned documents
* [ ] Add production database support such as PostgreSQL
* [ ] Add authentication and role-based access control
* [ ] Add monitoring and observability
* [ ] Containerize with Docker
* [ ] Deploy the application
* [ ] Expand the automated evaluation dataset

---

# 📌 Why Agentic RAG?

A conventional RAG system generally follows:

```text
User Query
    ↓
Retrieve Documents
    ↓
Generate Answer
```

ClaimPilot uses a more structured architecture:

```text
                     User Query
                         │
                         ▼
                 Gemini Query Router
                         │
                ┌────────┴────────┐
                │                 │
             SIMPLE            COMPLEX
                │                 │
                ▼                 ▼
             Direct          LangGraph
               RAG             Agent
                │                 │
                │          ┌──────┼──────┐
                │          ▼      ▼      ▼
                │       Policy  Claim  Eligibility
                │       Search  Lookup    Tool
                │          │      │      │
                │          └──────┼──────┘
                │                 │
                │                 ▼
                │          Gemini Reasoning
                │                 │
                └────────┬────────┘
                         ▼
                  Final Response
```

This allows ClaimPilot to use **simple retrieval for straightforward questions** while reserving **agentic tool-based reasoning for more complex claim-analysis tasks**.

---

# 👨‍💻 Author

**Prateek Jha**

B.Tech — Chemical Engineering
Indian Institute of Technology Patna

GitHub: [@PrateekJha14](https://github.com/PrateekJha14)

---

# ⭐ Technologies Used

* [Google Gemini](https://ai.google.dev/)
* [LangChain](https://www.langchain.com/)
* [LangGraph](https://www.langchain.com/langgraph)
* [FAISS](https://github.com/facebookresearch/faiss)
* [Streamlit](https://streamlit.io/)
* [SQLite](https://www.sqlite.org/)

---

## 📄 License

This project is intended for educational and research purposes.

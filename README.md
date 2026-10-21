# banking-genai-agentic-aws

A production-grade **multi-agent banking platform on AWS Bedrock** — automating
four enterprise banking workflows:

  1. Loan Approval Automation      (LangGraph ReAct + HITL)
  2. Fraud Investigation           (CrewAI multi-agent)
  3. AML / KYC Compliance Q&A      (Hybrid RAG with citations)
  4. Customer Support Agent        (LangGraph + streaming)

Built on **AWS Bedrock + Bedrock AgentCore**, **LangGraph**, **CrewAI**,
**AutoGen**, **Semantic Kernel**, **DSPy**, **OpenAI AgentKit**,
**MCP (2026-07-28 spec)**, and **A2A v1.0** — with production guardrails,
observability, and evaluation built in from day one.

---

## Architecture (high level)

    ┌──────────────────────────────────────────────────────────┐
    │  FastAPI (api/main.py)                                   │
    │  /loan/approve · /fraud/investigate · /rag/query         │
    │  /support/chat                                           │
    └──────────────────────────────────────────────────────────┘
                            │
                            ▼
    ┌──────────────────────────────────────────────────────────┐
    │  Agent Mesh (6 frameworks)                               │
    │                                                          │
    │  • LangGraph     — stateful supervisor (Loan, Support)   │
    │  • CrewAI        — role-based crew (Fraud)               │
    │  • AutoGen       — debate + self-correct (Risk Review)   │
    │  • Semantic K.   — enterprise plugin orchestration       │
    │  • DSPy          — compiled & optimized RAG (AML/KYC)    │
    │  • AgentKit      — visual workflow + Connector Registry  │
    └──────────────────────────────────────────────────────────┘
                            │
                            ▼
    ┌──────────────────────────────────────────────────────────┐
    │  Protocols                                               │
    │  • MCP (2026-07-28 spec) — agent ↔ tools                 │
    │  • A2A (v1.0)            — agent ↔ agent                 │
    └──────────────────────────────────────────────────────────┘
                            │
                            ▼
    ┌──────────────────────────────────────────────────────────┐
    │  Tools (5 banking tools)                                 │
    │  retrieve_docs · classify_risk · forecast_sales          │
    │  get_sentiment · generate_recovery                       │
    └──────────────────────────────────────────────────────────┘
                            │
                            ▼
    ┌──────────────────────────────────────────────────────────┐
    │  AWS Services                                            │
    │  Bedrock · AgentCore · OpenSearch · SageMaker ·          │
    │  Guardrails · CloudWatch · Secrets Manager               │
    └──────────────────────────────────────────────────────────┘

---

## 4 Banking Use Cases

| # | Use case | Agent pattern | Frameworks | Primary AWS services |
|---|----------|---------------|------------|----------------------|
| 1 | **Loan Approval** | LangGraph supervisor + HITL | LangGraph, Semantic Kernel | Bedrock, AgentCore Runtime+Memory, SageMaker, Guardrails |
| 2 | **Fraud Investigation** | CrewAI 3-role crew + AutoGen debate | CrewAI, AutoGen | Bedrock, AgentCore Gateway, OpenSearch, MCP |
| 3 | **AML/KYC Q&A** | DSPy-compiled RAG pipeline | DSPy, LangChain | Bedrock KB, OpenSearch, Titan Embeddings, Guardrails |
| 4 | **Customer Support** | LangGraph ReAct + streaming + AgentKit UI | LangGraph, AgentKit, ChatKit | Bedrock, AgentCore Memory, CloudWatch |

---

## Agentic Framework Matrix

| Framework | Role in this platform | Use case |
|-----------|----------------------|----------|
| **LangGraph** | Stateful supervisor with checkpoints, HITL interrupts, resumable graphs | Loan Approval, Customer Support |
| **CrewAI** | Role-based crew (Analyst, Investigator, Evidence Assembler) with delegation | Fraud Investigation |
| **AutoGen** | Multi-agent debate (Bull vs Bear vs Judge) + self-correcting code loops | Risk Review, Compliance edge cases |
| **Semantic Kernel** | Enterprise plugin orchestration — C#/.NET, planner, function calling | Cross-system banking orchestration |
| **DSPy** | Programmatic prompt optimization — compilers auto-tune prompts and RAG pipelines | AML/KYC RAG |
| **OpenAI AgentKit** | Visual workflow builder, Connector Registry, ChatKit UI, Guardrails library | Customer Support interface |
| **MCP** | Agent ↔ tool protocol (2026-07-28 spec: stateless core, OAuth hardening) | All agents |
| **A2A v1.0** | Agent ↔ agent protocol — AgentCard discovery, task delegation | Multi-agent delegation |

---

## Protocol Deep Dive

### MCP (Model Context Protocol) — 2026-07-28 Spec

MCP has become the industry standard for connecting AI agents to applications,
surpassing 400M monthly SDK downloads.

Key changes in the 2026-07-28 spec:

  - Stateless core — moves from bidirectional stateful to request/response;
    servers can now deploy on serverless and edge infrastructure
  - Standardized extensions — MCP Apps and Tasks ship under a versioned
    extensions framework
  - Auth hardening — aligns with production OAuth 2.0 and OIDC for enterprise
    identity systems like Entra or Okta
  - MCP Server Cards — HTTP server discovery standardized (SEP-2127)
  - Tasks Extension — long-running work formalized (SEP-2663)

### A2A (Agent-to-Agent) — v1.0

A2A v1.0 shipped March 2026 and joined the Agentic AI Foundation (AAIF) in
August 2026, alongside MCP.

Key characteristics:

  - Agent Cards — structured discovery metadata for capabilities and endpoints
  - Task lifecycle — 9 states (COMPLETED, FAILED, CANCELED, REJECTED,
    INPUT_REQUIRED, AUTH_REQUIRED, SUBMITTED, WORKING, UNSPECIFIED)
  - Three delivery modes — polling, streaming (SSE), push notifications
  - Framework-agnostic — agents built with different frameworks can communicate
  - Production support — Google Cloud, Azure AI Foundry, and AWS Bedrock
    AgentCore all host A2A servers

The distinction:

  - MCP standardizes how agents connect to tools and data.
  - A2A standardizes how agents communicate with each other.

---

## Project Structure

    banking-genai-agentic-aws/
    ├── config/              # Pydantic settings + constants
    ├── data/                # Banking policy corpus + golden sets
    ├── ingestion/           # S3/local loaders + token-aware chunker
    ├── embeddings/          # Bedrock Titan Embeddings wrapper
    ├── vectorstore/         # OpenSearch Serverless client
    ├── retrieval/           # Hybrid (BM25 + dense) + rerank
    ├── llm/                 # Bedrock Converse + multi-provider router
    ├── guardrails/          # Bedrock Guardrails + PII masking
    ├── agents/              # LangGraph + CrewAI + AutoGen + SK + DSPy
    ├── protocols/           # MCP server + A2A agent card + delegation
    ├── agentkit/            # AgentKit visual workflows + ChatKit UI
    ├── evaluation/          # RAGAS + LLM-as-judge + DSPy metrics
    ├── observability/       # CloudWatch + LangSmith + OpenTelemetry
    ├── api/                 # FastAPI endpoints
    ├── infra/               # Terraform + IAM
    ├── tests/               # pytest suite
    └── scripts/             # ingest / build index / demo

---

## Setup

    # 1. Clone and enter
    git clone <repo> banking-genai-agentic-aws
    cd banking-genai-agentic-aws

    # 2. Create virtual environment
    python -m venv .venv
    source .venv/bin/activate          # Windows: .venv\Scripts\activate

    # 3. Install dependencies
    pip install -r requirements.txt

    # 4. Configure environment
    cp .env.example .env
    # Edit .env and set AWS credentials + Bedrock model IDs

    # 5. Ingest banking policy corpus
    make ingest

    # 6. Run end-to-end demo
    make demo

---

## Design Principles

1. Provider-agnostic LLM layer — BaseLLM contract; swap Bedrock for
   OpenAI/Claude/Ollama without touching agent code.

2. Framework-per-job — LangGraph for stateful supervisors, CrewAI for
   role-based crews, AutoGen for debate, DSPy for optimized RAG,
   AgentKit for UI, Semantic Kernel for enterprise plugins.

3. Protocol-first — MCP for tools, A2A for agent delegation. No custom
   wire formats.

4. Ground everything — every RAG answer cites its source chunk ID.

5. Human-in-the-Loop by default — anything above Rs 5L (loans) pauses for
   officer approval via LangGraph interrupt.

6. Least-privilege tools — each agent has a scoped IAM role and a whitelist
   of callable tools.

7. Measure before you ship — RAGAS + LLM-as-judge golden set runs in CI.

8. Optimize prompts programmatically — DSPy compilers replace manual
   prompt engineering.

9. Observable at every step — LangSmith traces + CloudWatch metrics for
   every agent run.

---

## License

Personal R&D · Portfolio project · Synthetic data only
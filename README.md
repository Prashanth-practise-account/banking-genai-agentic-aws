# Banking GenAI Agentic AWS

A multi-use-case banking AI platform built using Generative AI, agentic workflows, document processing, and Retrieval-Augmented Generation (RAG).

## Use Cases

### 1. Loan Approval Automation

Automates the initial processing of loan applications by accepting applicant details and supporting documents, extracting information, and converting unstructured document content into structured data.

**Key Features**
- FastAPI endpoint for loan application submission and document uploads.
- PDF text extraction using `pypdf`.
- Image text extraction using Tesseract OCR and Pillow.
- Qwen 3 4B integration through Ollama and LangChain.
- LLM-based structured document extraction into JSON.
- Support for processing multiple uploaded documents.
- Loan application state modeling using Python `TypedDict`.

**Workflow**

```text
Applicant Details + Documents
            |
            v
       FastAPI API
            |
            v
    Document Extraction
            |
            v
     Qwen 3 4B (Ollama)
            |
            v
    Structured JSON Data
            |
            v
 Verification and Eligibility
```

### 2. Customer Support Agent

Provides AI-powered responses to customer banking queries using an agentic workflow.

**Example Query**

```text
Customer: Why was I charged ₹500 last week?
```

**Expected Workflow**

1. The agent receives the customer's question.
2. The agent determines which information is required.
3. It calls the relevant tools, such as transaction-history lookup.
4. It retrieves relevant banking policy information when needed.
5. The LLM generates a response using the retrieved information.

**Example Response**

```text
Your ₹500 charge was the annual debit card fee.
This is charged once per year under the applicable
banking policy. Would you like to know about
available fee-waiver options?
```

**Technologies:** LangGraph, LangChain, Ollama, and tool-based agent workflows.

### 3. AML / KYC Compliance Q&A

Helps users answer Anti-Money Laundering (AML) and Know Your Customer (KYC) compliance questions by retrieving relevant information from banking policy documents and regulatory PDFs.

**Example Query**

```text
What are the KYC requirements for cash transactions above ₹10 lakh?
```

**Workflow**

1. Load banking policy documents and regulatory PDFs.
2. Split documents into smaller text chunks.
3. Generate embeddings for document retrieval.
4. Retrieve relevant passages using hybrid search.
5. Use the retrieved context to generate a grounded answer.
6. Use DSPy to optimize the RAG pipeline where configured.

**Technologies:** DSPy, Hybrid RAG, Amazon Titan Embeddings, OpenSearch, and an LLM.

## Technology Stack

| Component | Technologies |
|---|---|
| Backend API | FastAPI, Uvicorn |
| LLM | Qwen 3 4B, Ollama |
| LLM Integration | LangChain |
| Agent Workflows | LangGraph |
| Document Processing | pypdf, Pillow, Tesseract OCR |
| Compliance Q&A | DSPy, Hybrid RAG |
| Embeddings | Amazon Titan Embeddings |
| Vector Search | OpenSearch |
| Frontend | Streamlit |
| Language | Python |

## Project Structure

```text
banking-genai-agentic-aws/
├── config/
├── data/
├── ingestion/
├── embeddings/
├── vectorstore/
├── retrieval/
├── llm/
├── guardrails/
├── agents/
├── protocols/
├── agentkit/
├── evaluation/
├── observability/
├── api/
├── infra/
├── tests/
├── scripts/
└── frontend.py
```

*The exact folder and file names may differ depending on the current project structure.*

## Setup and Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd banking-genai-agentic-aws
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn streamlit requests python-multipart
pip install langchain langchain-ollama pypdf pillow pytesseract
```

Install any additional dependencies required by the Customer Support Agent and AML / KYC Compliance Q&A components.

### 4. Set up Ollama

Install Ollama, then download the model:

```bash
ollama pull qwen3:4b
```

Make sure Ollama is running before starting the application.

For image OCR, install Tesseract OCR separately on Windows.

## Running the Application

### Step 1: Start the FastAPI backend

Open a terminal in the project root and activate the virtual environment.

If the FastAPI application is defined in `ingestion/app.py`, run:

```bash
uvicorn ingestion.app:app --reload
```

If your application is defined in `api/main.py`, use:

```bash
uvicorn api.main:app --reload
```

Open Swagger UI to test the API:

http://127.0.0.1:8000/docs

### Step 2: Start the Streamlit frontend

Open a **second terminal** in the project root and activate the same virtual environment.

If your frontend file is named `frontend.py`, run:

```bash
streamlit run frontend.py
```

If your frontend file has a different name, replace `frontend.py` with the actual filename.

### Step 3: Use the application

1. Open the local URL displayed in the Streamlit terminal, usually `http://localhost:8501`.
2. Select the required banking use case.
3. Enter the required information or upload supporting documents.
4. Submit the request and review the response.

Ensure the frontend sends requests to the correct FastAPI backend URL and endpoint.

## License

Personal R&D · Portfolio project · Synthetic data only.

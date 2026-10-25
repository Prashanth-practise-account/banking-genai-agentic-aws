import json
from typing import List
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse


from agents.DocumentAgent import DocumentAgent
from scripts.customer_support import CustomerSuppertAgent
from KYCCompilencer import Compilencer

from DesignNodes import graph_app
from langgraph.types import Command

from config.supprt_chat import SupportChatRequest
from config.RagQuery import RagQuery

app = FastAPI()
compilencer = Compilencer()
hybrid_search = compilencer.HybridSearch()

@app.post("/loan/approval")
async def loan_approval(
    application_id: str = Form(...),
    applicant_name: str = Form(...),
    date_of_birth: str = Form(...),
    pan_number: str = Form(...),
    mobile_number: str = Form(...),
    employment_type: str = Form(...),
    credit_score: int = Form(...),
    purpose: str = Form(...),
    monthly_salary: float = Form(...),
    existing_emis: float = Form(...),
    loan_amount: float = Form(...),
    interest_rate: float = Form(...),
    tenure_months: int = Form(...),
    upload_document: List[UploadFile] = File(...),
):
    application_data = {
        "application_id": application_id,
        "applicant_name": applicant_name,
        "date_of_birth": date_of_birth,
        "pan_number": pan_number,
        "mobile_number": mobile_number,
        "employment_type": employment_type,
        "credit_score": credit_score,
        "purpose": purpose,
        "monthly_salary": monthly_salary,
        "existing_emis": existing_emis,
        "loan_amount": loan_amount,
        "interest_rate": interest_rate,
        "tenure_months": tenure_months,
    }

    # Extract text from uploaded documents
    document_agent = DocumentAgent()
    documents = []

    for file in upload_document:
        extracted_text = document_agent.document_parsing(file.file)
        documents.append(extracted_text)

    all_document_text = "\n".join(documents)

    # Prepare initial graph state
    initial_state = {
        "application": {
            **application_data,
            "monthly_net_salary": monthly_salary,
            "existing_monthly_emis": existing_emis,
            "requested_loan_amount": loan_amount,
            "annual_interest_rate": interest_rate,
            "tenure_years": tenure_months / 12,
        },
        "documents_text": all_document_text,
    }

    config = {
        "configurable": {
            "thread_id": application_id
        }
    }

    # Run the LangGraph workflow
    result = graph_app.invoke(initial_state, config=config)

    # Initialize officer details
    officer_name = None
    officer_reason = None

    print("=" * 60)

    # Check whether the graph requires officer review
    if result.get("__interrupt__"):
        print("\nOfficer review:")
        print(result["__interrupt__"][0].value)
        print("=" * 60)

        decision = input(
            "Officer Decision: Enter APPROVE or REJECT: "
        ).strip().upper()

        if decision == "REJECTED":
            decision = "REJECT"

        if decision not in ["APPROVE", "REJECT"]:
            raise HTTPException(
                status_code=400,
                detail="Enter APPROVE or REJECT"
            )

        officer_name = input("Enter your Officer Name: ").strip()
        officer_reason = input("Enter the reason: ").strip()

        if not officer_name or not officer_reason:
            raise HTTPException(
                status_code=400,
                detail="Officer name and reason are required"
            )

        # Resume the interrupted graph
        result = graph_app.invoke(
            Command(
                resume={
                    "decision": decision,
                    "officer_name": officer_name,
                    "officer_reason": officer_reason,
                }
            ),
            config=config,
        )

    # Include officer details in the API response
    result["officer_name"] = officer_name
    result["officer_reason"] = officer_reason

    print("=" * 60)
    print("Officer Name:", officer_name)
    print("Officer Reason:", officer_reason)

    return result

@app.post("/fraud/investigate")
def fraud_investigate():
    pass

@app.post("/rag/query")
def rag_query(request: RagQuery):
    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Please enter a KYC compliance question."
        )

    try:
        result = compilencer.search(query, hybrid_search)

        llm_response = compilencer.generate_asnwer(
            result,
            query
        )

        answer = llm_response.content

        def generate():
            for word in answer.split():
                yield word + " "

        return StreamingResponse(
            generate(),
            media_type="text/plain; charset=utf-8"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"KYC RAG processing failed: {str(e)}"
        )


@app.post("/support/chat")
def support_chat(request: SupportChatRequest):
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    try:
        agent = CustomerSuppertAgent(
            query=request.message
        )

        answer = agent.customer_support()

        def generate():
            for word in answer.split():
                yield word + " "

        return StreamingResponse(
            generate(),
            media_type="text/plain; charset=utf-8"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Customer support failed: {str(e)}"
        )

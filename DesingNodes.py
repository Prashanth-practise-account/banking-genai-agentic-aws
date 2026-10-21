
import json
import re

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver

from agents.DocumentAgent import DocumentAgent
from agents.VerificationAgent import VerficationAgent
from agents.EligibilityAgent import EligibilityAgent
from retrieval.retrieval import retrieve_policy
from config.AgentState import LoanState


graph = StateGraph(LoanState)

document_agent = DocumentAgent()
verification_agent = VerficationAgent()
eligibility_agent = EligibilityAgent()


def document_node(state: LoanState) -> dict:
   
    application = state.get("application", {})

    if not application:
        result = {
            "status": "REVIEW_REQUIRED",
            "reason": "Application data is missing."
        }
    else:
        result = {
            "status": "EXTRACTED",
            "reason": "Using supplied synthetic structured application data."
        }

    print("\n[DocumentAgent]")
    print(json.dumps(result, indent=2))

    return {"document_result": result}

def verification_node(state: LoanState) -> dict:
    result = verification_agent.verfy_application(
        state["application"],
        state.get("salary_slips", []),
        state.get("bank_statement", [])
    )

    failures = []

    for key, values in result.items():
        for value in values:
            text = str(value).lower()

            if any(phrase in text for phrase in [
                "not present",
                "not matched",
                "not found",
                "could not be verified"
            ]):
                failures.append(f"{key}: {value}")

    status = "REVIEW_REQUIRED" if failures else "PASS"

    verification_result = {
        "status": status,
        "details": result,
        "failures": failures
    }

    print("\n[VerificationAgent]")
    print(json.dumps(verification_result, indent=2))

    return {"verification_result": verification_result}


def eligibility_node(state: LoanState) -> dict:
    application = state["application"]

    emi = eligibility_agent.calculateEMI(
        application["requested_loan_amount"],
        application["annual_interest_rate"],
        application["tenure_years"]
    )

    result = eligibility_agent.FOIR(
        application["existing_monthly_emis"],
        emi,
        application["monthly_net_salary"]
    )

    eligibility_result = {
        "proposed_emi": round(emi, 2),
        **result
    }

    print("\n[EligibilityAgent]")
    print(json.dumps(eligibility_result, indent=2))

    return {"eligibility_result": eligibility_result}

def policy_rag_node(state: LoanState) -> dict:
    application = state["application"]

    query = (
        "What is the maximum personal loan amount under this policy? "
        f"The requested loan amount is "
        f"{application['requested_loan_amount']} rupees. "
        "Return the loan amount policy and its maximum amount."
    )

    policies = retrieve_policy(query, top_k=3)

    maximum_amount = None

    for policy in policies:
        policy_text = policy.get("policy_text", "")

        if "maximum personal loan amount" in policy_text.lower():
            match = re.search(
                r"maximum personal loan amount.*?"
                r"Rs\.?\s*([\d,]+)",
                policy_text,
                flags=re.IGNORECASE | re.DOTALL
            )

            if match:
                maximum_amount = int(
                    match.group(1).replace(",", "")
                )
                break

    policy_result = {
        "status": "RETRIEVED" if maximum_amount is not None else "NOT_FOUND",
        "maximum_personal_loan_amount": maximum_amount,
        "retrieved_policies": policies
    }

    print("\n[PolicyRag]")
    print(json.dumps(policy_result, indent=2))

    return {"policy_result": policy_result}



def supervisor_node(state: LoanState) -> dict:
    application = state.get("application", {})
    document = state.get("document_result", {})
    verification = state.get("verification_result", {})
    eligibility = state.get("eligibility_result", {})
    policy = state.get("policy_result", {})

    loan_amount = application.get("requested_loan_amount", 0)
    maximum_amount = policy.get("maximum_personal_loan_amount")

    if document.get("status") != "EXTRACTED":
        action = "HITL"
        reason = "Document extraction is incomplete."

    elif verification.get("status") != "PASS":
        action = "HITL"
        reason = "Document verification requires human review."

    elif policy.get("status") != "RETRIEVED" or maximum_amount is None:
        action = "HITL"
        reason = "The maximum loan amount policy was not retrieved."

    elif loan_amount >= maximum_amount:
        action = "HITL"
        reason = "Requested loan amount reached or exceeded the policy threshold."

    elif eligibility.get("affordability_check") != "PASS":
        action = "HITL"
        reason = "Eligibility or affordability requires review."

    else:
        action = "DIRECT_RESULT"
        reason = "Implemented checks passed and loan amount is below the policy threshold."

    print("\n[Supervisor]")
    print(json.dumps({
        "next_action": action,
        "routing_reason": reason
    }, indent=2))

    return {
        "next_action": action,
        "routing_reason": reason
    }

def human_review_node(state: LoanState) -> dict:
    application = state.get("application", {})
    policy = state.get("policy_result", {})
    verification = state.get("verification_result", {})
    eligibility = state.get("eligibility_result", {})

    review_request = {
        "application_id": application.get("application_id"),
        "requested_loan_amount": application.get("requested_loan_amount"),
        "maximum_policy_amount": policy.get(
            "maximum_personal_loan_amount"
        ),
        "routing_reason": state.get("routing_reason"),
        "verification_failures": verification.get("failures", []),
        "eligibility_result": eligibility,
        "allowed_actions": ["APPROVE", "REJECT", "REQUEST_DOCUMENTS"]
    }

    print("\n[HITL] Waiting for human review")
    print(json.dumps(review_request, indent=2))

    response = interrupt(review_request)

    action = (
        response.get("action")
        if isinstance(response, dict)
        else None
    )

    if action not in ["APPROVE", "REJECT", "REQUEST_DOCUMENTS"]:
        final_status = "REVIEW_PENDING"
        reason = "A valid human review action is required."

    elif action == "REJECT":
        final_status = "REJECTED_BY_REVIEWER"
        reason = "The human reviewer rejected the application."

    elif action == "REQUEST_DOCUMENTS":
        final_status = "DOCUMENTS_REQUIRED"
        reason = "Additional documents are required."

    elif (
        policy.get("maximum_personal_loan_amount") is not None
        and application.get("requested_loan_amount", 0)
        > policy["maximum_personal_loan_amount"]
    ):
        # A reviewer cannot override the hard policy maximum.
        final_status = "POLICY_LIMIT_EXCEEDED"
        reason = "Requested amount exceeds the policy maximum."

    elif verification.get("status") != "PASS":
        final_status = "REVIEW_COMPLETED_PENDING_VERIFICATION"
        reason = (
            "Human review was recorded, but verification issues "
            "must be resolved before a lending decision."
        )

    elif eligibility.get("affordability_check") != "PASS":
        final_status = "REVIEW_COMPLETED_PENDING_ELIGIBILITY"
        reason = "Eligibility checks must be resolved before a lending decision."

    else:
        final_status = "HUMAN_REVIEW_APPROVED"
        reason = "Human review was approved; remaining lending controls still apply."

    final_decision = {
        "application_id": application.get("application_id"),
        "status": final_status,
        "requested_loan_amount": application.get("requested_loan_amount"),
        "maximum_policy_amount": policy.get(
            "maximum_personal_loan_amount"
        ),
        "reviewer_action": action,
        "reviewer": (
            response.get("reviewer", "UNKNOWN")
            if isinstance(response, dict)
            else "UNKNOWN"
        ),
        "comments": (
            response.get("comments", "")
            if isinstance(response, dict)
            else ""
        ),
        "reason": reason
    }

    print("\n[HITL Result]")
    print(json.dumps(final_decision, indent=2))

    return {
        "human_review_result": (
            response if isinstance(response, dict) else {}
        ),
        "final_decision": final_decision
    }

def direct_result_node(state: LoanState) -> dict:
    application = state["application"]
    policy = state["policy_result"]
    eligibility = state["eligibility_result"]

    verification = state.get("verification_result", {})

    if verification.get("status") != "PASS":
        status = "REVIEW_REQUIRED"
        reason = "Verification did not pass."
    elif eligibility.get("affordability_check") != "PASS":
        status = "REVIEW_REQUIRED"
        reason = "Affordability check did not pass."
    else:
        status = "ELIGIBILITY_CHECKS_PASSED"
        reason = (
            "The requested amount is below the retrieved policy maximum "
            "and the implemented checks passed. This is not final loan approval."
        )

    final_decision = {
        "application_id": application.get("application_id"),
        "status": status,
        "requested_loan_amount": application.get("requested_loan_amount"),
        "maximum_policy_amount": policy.get(
            "maximum_personal_loan_amount"
        ),
        "proposed_emi": eligibility.get("proposed_emi"),
        "foir_percentage": eligibility.get("foir_percentage"),
        "reason": reason
    }

    print("\n[Direct Result]")
    print(json.dumps(final_decision, indent=2))

    return {"final_decision": final_decision}


graph.add_node("DocumentAgent", document_node)
graph.add_node("VerificationAgent", verification_node)
graph.add_node("EligibilityAgent", eligibility_node)
graph.add_node("PolicyRag", policy_rag_node)
graph.add_node("Supervisor", supervisor_node)
graph.add_node("HITL", human_review_node)
graph.add_node("DirectResult", direct_result_node)


graph.add_edge(START, "DocumentAgent")
graph.add_edge("DocumentAgent", "VerificationAgent")
graph.add_edge("VerificationAgent", "EligibilityAgent")
graph.add_edge("EligibilityAgent", "PolicyRag")
graph.add_edge("PolicyRag", "Supervisor")


def route_after_supervisor(state: LoanState) -> str:
    if state.get("next_action") == "HITL":
        return "HITL"

    return "DIRECT_RESULT"


graph.add_conditional_edges(
    "Supervisor",
    route_after_supervisor,
    {
        "HITL": "HITL",
        "DIRECT_RESULT": "DirectResult"
    }
)

graph.add_edge("HITL", END)
graph.add_edge("DirectResult", END)


checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

if __name__ == "__main__":

    application = {
        "application_id": "APP-1001",
        "applicant_name": "Ravi Kumar",
        "employment_type": "Salaried",
        "employer_name": "ABC Technologies Pvt Ltd",
        "monthly_net_salary": 85000,
        "existing_monthly_emis": 12000,
        "requested_loan_amount": 800000,
        "annual_interest_rate": 8.5,
        "tenure_years": 5,
        "loan_purpose": "Home renovation",
        "identity_document_status": "uploaded",
        "salary_slips_uploaded": 6,
        "bank_statement_months": 6,
        "credit_score": 750
    }

    salary_slips = [
        {
            "month": "2026-04",
            "employee_name": "Ravi Kumar",
            "employer": "ABC Technologies Pvt Ltd",
            "net_salary": 85000
        },
        {
            "month": "2026-05",
            "employee_name": "Ravi Kumar",
            "employer": "ABC Technologies Pvt Ltd",
            "net_salary": 85000
        },
        {
            "month": "2026-06",
            "employee_name": "Ravi Kumar",
            "employer": "ABC Technologies Pvt Ltd",
            "net_salary": 85000
        }
    ]

    bank_statement = [
        {
            "date": "2026-04-01",
            "description": "ABC TECHNOLOGIES SALARY",
            "credit": 85000,
            "debit": 0
        },
        {
            "date": "2026-04-05",
            "description": "RENT PAYMENT",
            "credit": 0,
            "debit": 15000
        },
        {
            "date": "2026-04-10",
            "description": "EXISTING LOAN EMI",
            "credit": 0,
            "debit": 12000
        },
        {
            "date": "2026-05-01",
            "description": "ABC TECHNOLOGIES SALARY",
            "credit": 85000,
            "debit": 0
        }
    ]

    initial_state = {
        "application": application,
        "documents": [],
        "salary_slips": salary_slips,
        "bank_statement": bank_statement
    }

    config = {
        "configurable": {
            "thread_id": application["application_id"]
        }
    }

    print("\n========== INPUT APPLICATION ==========")
    print(json.dumps(initial_state, indent=2))

    for update in app.stream(
        initial_state,
        config=config,
        stream_mode="updates"
    ):
        print("\n========== GRAPH UPDATE ==========")
        print(json.dumps(update, indent=2, default=str))

    snapshot = app.get_state(config)

    if snapshot.next:
        print("\nWorkflow paused. Enter human review details.")

        action = input(
            "Action (APPROVE / REJECT / REQUEST_DOCUMENTS): "
        ).strip().upper()

        reviewer = input("Reviewer name: ").strip()
        comments = input("Comments: ").strip()

        human_response = {
            "action": action,
            "reviewer": reviewer,
            "comments": comments
        }

        print("\n========== RESUMING WORKFLOW ==========")

        for update in app.stream(
            Command(resume=human_response),
            config=config,
            stream_mode="updates"
        ):
            print(json.dumps(update, indent=2, default=str))

    final_state = app.get_state(config).values
    print("\n========== FINAL DECISION JSON ==========")
    print(
        json.dumps(
            final_state.get("final_decision", {
                "status": "REVIEW_PENDING",
                "reason": "No final decision was produced."
            }),
            indent=2
        )
    )

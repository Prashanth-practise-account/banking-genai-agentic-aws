from config.AgentState import LoanState
from agents.DocumentAgent import DocumentAgent
from agents.VerificationAgent import VerficationAgent
from agents.EligibilityAgent import EligibilityAgent
from retrieval.retrieval import retrieve_policy
from agents.DecisionNode import DecisionNode,HITL

def document_node(state:LoanState):
    agent1 = DocumentAgent()
    document_text = state.get("documents_text","")
    structured_output = agent1.structured_document(document_text=document_text)
    return {
        "structured_documents": structured_output
    }

def verification_node(state: LoanState):
    application = state["application"]

    agent2 = VerficationAgent().verify_application(
        state,
        state.get("structured_documents", {})
    )

    return {
        "verification_result": agent2
    }

def eligibility_node(state: LoanState):
    application = state["application"]

    existing_emi = application["existing_emis"]
    loan_amount = application["loan_amount"]
    interest_rate = application["interest_rate"]
    tenure_years = 5
    monthly_salary = application["monthly_salary"]

    agent = EligibilityAgent()

    proposed_emi = agent.calculateEMI(
        loan_amount,
        interest_rate,
        tenure_years
    )

    foir = agent.FOIR(
        existing_emi,
        proposed_emi,
        monthly_salary
    )
    foir_percentage = foir["foir_percentage"]
    return {
        "eligibility_result": {
            "existing_emi": existing_emi,
            "proposed_emi": round(proposed_emi, 2),
            "net_salary": monthly_salary,
            "foir": foir_percentage,
            "foir_percent": f"{foir_percentage:.2f}%",
            "foir_threshold": foir["foir_threshold"],
            "affordability_check": foir["affordability_check"],
            "reason": foir["reason"],
            "eligible": foir["affordability_check"] == "PASS",
        }
    }

def policy_rag_node(state: LoanState):
    results = retrieve_policy(
        "What is the maximum personal loan amount and "
        "minimum credit score required?",
        top_k=3,
    )
    policies = []
    for result in results:
        policies.append({
            "policy_id": result.get("policy_id"),
            "chunk_id": result.get("chunk_id"),
            "source": result.get("source"),
            "policy_text": result.get("policy_text"),
        })
    return {
        "policy_results":policies
    }


def decision_node(state: LoanState):
    decision_agent = DecisionNode(state=state)
    updated_state = {
        **state,
        **decision_agent
    }
    if decision_agent["next_action"] == "HITL":
        human_review = HITL(state=state)
        print(human_review)
        return {
            **decision_agent,
            **human_review
        }
    
    return decision_agent

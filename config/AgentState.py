
from typing import TypedDict, Any


class LoanState(TypedDict, total=False):
    application: dict
    documents: list
    salary_slips: list
    bank_statement: list

    document_result: dict
    verification_result: dict
    eligibility_result: dict
    policy_result: list

    next_action: str
    routing_reason: str
    human_review_result: dict
    final_decision: dict

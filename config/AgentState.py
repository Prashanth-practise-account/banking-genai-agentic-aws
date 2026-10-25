
from typing import TypedDict, Any



from typing import TypedDict, Any


class LoanState(TypedDict, total=False):
    application: dict
    documents_text: str

    structured_documents: dict[str, Any]
    verification_result: Any
    eligibility_result: dict
    policy_results: list
    status: str
    next_action: str
    reason: str

    final_decision: dict

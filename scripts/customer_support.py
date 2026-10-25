from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

class CustomerSuppertAgent:
    def __init__(self,query):
        self.query = query
    def customer_support(self):
        agent = create_react_agent(
            model=ChatOllama(
                model="qwen2.5:7b",
                temperature=0,
                num_predict=1000,
                timeout=30
            ),
            tools=[get_recent_transaction, fee_policy],
        )
        response = agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": self.query}
                ]
            },
        )

        return response["messages"][-1].content
@tool
def get_recent_transaction():
    """Retrieve synthetic banking transaction records for customer support."""
    transactions = [
    {
        "transaction_id": "TXN-1001",
        "customer_id": "CUST-1001",
        "account_id": "ACC-1001",
        "date": "2026-10-10",
        "description": "Annual Debit Card Fee",
        "transaction_type": "DEBIT",
        "amount": 500,
        "currency": "INR",
        "status": "POSTED",
        "reference": "DC-ANNUAL-2026"
    },
    {
        "transaction_id": "TXN-1002",
        "customer_id": "CUST-1001",
        "account_id": "ACC-1001",
        "date": "2026-10-12",
        "description": "Grocery Store Payment",
        "transaction_type": "DEBIT",
        "amount": 1200,
        "currency": "INR",
        "status": "POSTED",
        "reference": "POS-20261012"
    },
    {
        "transaction_id": "TXN-1003",
        "customer_id": "CUST-1001",
        "account_id": "ACC-1001",
        "date": "2026-10-15",
        "description": "Salary Credit",
        "transaction_type": "CREDIT",
        "amount": 85000,
        "currency": "INR",
        "status": "POSTED",
        "reference": "SAL-202610"
    },
    {
        "transaction_id": "TXN-1004",
        "customer_id": "CUST-1001",
        "account_id": "ACC-1001",
        "date": "2026-10-18",
        "description": "Restaurant Payment",
        "transaction_type": "DEBIT",
        "amount": 750,
        "currency": "INR",
        "status": "POSTED",
        "reference": "POS-20261018"
    },
    {
        "transaction_id": "TXN-2001",
        "customer_id": "CUST-2001",
        "account_id": "ACC-2001",
        "date": "2026-10-10",
        "description": "Annual Debit Card Fee",
        "transaction_type": "DEBIT",
        "amount": 500,
        "currency": "INR",
        "status": "POSTED",
        "reference": "DC-ANNUAL-2026"
    }
]   
    return transactions

@tool
def fee_policy():
    """Retrieve the synthetic banking fee policy, including annual debit card fees."""
    return """
    # Synthetic Banking Fee Policy

**Policy ID:** CARD-FEE-005  
**Policy Section:** 5.2  
**Policy Title:** Annual Debit Card Fee  
**Effective Date:** 2026-01-01  
**Document Type:** Retail Banking Fee Schedule

## Section 5.2 — Annual Debit Card Fee

1. The bank charges an annual debit card fee of ₹500 for eligible debit card products.
2. The annual fee is charged once per annual billing cycle, according to the customer's card agreement.
3. The fee may appear in the transaction history with a description such as "Annual Debit Card Fee".
4. The fee amount and billing date depend on the card product and the applicable customer agreement.
5. Fee waiver eligibility depends on the bank's applicable account terms and waiver rules. Customers must be checked against those rules before a waiver is promised.
6. If a customer disputes a fee, the support agent must verify the transaction record and the applicable card agreement before explaining the charge.
7. If the transaction description, amount, or applicable policy is unclear, the case must be referred for further review.

## Example

A posted transaction of ₹500 with the description "Annual Debit Card Fee" may correspond to the annual debit card fee described in Section 5.2.

The support agent must confirm the customer's transaction and applicable card terms before stating that the charge is valid.

**Note:** This is synthetic policy data created for development and testing. It is not an actual bank policy.
    """

if __name__ == "__main__":
    query = "Why was I charged ₹500 last week?"
    support = CustomerSuppertAgent(query=query)
    answer = support.customer_support()
    print(answer)
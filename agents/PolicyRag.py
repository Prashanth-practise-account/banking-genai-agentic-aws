from langchain_core.documents import Document   
from langchain_text_splitters import RecursiveCharacterTextSplitter


class PolicyRag:
    def __init__(self,chunk_size=900,chunk_overlap=200):
        self.policy_document = """
            Policy ID: BANK-PL-2026-001
            Version: 1.0
            Effective Date: 2026-01-01
            Document Type: Synthetic Banking Policy
            Purpose: Development and testing of a Loan Approval RAG Agent

            1. Credit Score Policy
            The applicant must have a minimum credit score of 700 to meet
            the standard credit-score requirement. Applications with a
            credit score below 700 must be referred for additional review
            and must not be automatically approved.

            2. Monthly Income Policy
            The applicant must have a minimum verified monthly net salary
            of Rs. 25000. Salary information must be supported by salary
            slips and corresponding bank statement entries. If the
            declared salary differs from the verified salary, the
            application must be referred for review.

            3. Employment Policy
            A salaried applicant must demonstrate at least 12 months of
            employment history. The employer name on the application
            should match the employer information on the salary slips.
            Missing employment information must be marked as requiring
            verification.

            4. Required Documents Policy
            The applicant must provide six months of salary slips and six
            months of bank statements. The applicant's name and employer
            information should be consistent across the submitted
            documents. Missing or inconsistent documents must be flagged
            for manual review.

            5. Salary Credit Verification Policy
            Salary credits should be identifiable in the applicant's bank
            statements. The salary amount and credit frequency must be
            compared with the salary slips. Missing expected salary credits
            or unexplained differences must be referred for review.

            6. Existing Financial Obligations Policy
            Existing monthly loan repayments and other eligible financial
            obligations must be considered when calculating the Fixed
            Obligations to Income Ratio (FOIR).

            FOIR (%) = (Total eligible monthly financial obligations /
            Verified monthly net income) * 100

            For this synthetic policy, the standard maximum FOIR is 40%.
            Applications exceeding this threshold must be referred for
            additional review under the example policy.

            7. Loan Amount Policy
            The maximum personal loan amount under this synthetic policy
            is Rs. 2500000. The final eligible amount depends on verified
            income, existing obligations, applicable interest rate,
            repayment tenure, and other relevant policy requirements.

            8. Loan Tenure Policy
            The maximum repayment tenure under this synthetic policy is
            60 months. The requested tenure must be checked against this
            limit. Requests outside the permitted range must be referred
            for review.

            9. Document Discrepancy Policy
            If the applicant's name, employer, salary, or bank salary
            credits cannot be verified, the system must not assume that
            the information is correct. The application must be marked as
            requiring review until sufficient evidence is available.

            10. Human Review Policy
            Applications with missing mandatory documents, inconsistent
            financial information, unresolved verification failures, or
            policy exceptions must be routed to an authorized human
            reviewer.

            Human review is not equivalent to loan approval. The reviewer
            must examine the evidence and record the outcome.

            11. Policy Retrieval and Evidence Requirements
            The Policy RAG Agent must retrieve relevant policy sections
            for each policy-related question. Each response should include
            the policy ID, section title, retrieved text, and source
            metadata.

            If the available policy documents do not contain the answer,
            the agent must state that the policy information is unavailable
            rather than inventing a rule.

            12. Final Decision Responsibility
            The Policy RAG Agent retrieves and explains policy requirements.
            It does not independently approve or reject a loan.

            The final decision workflow must consider policy results,
            document verification, financial eligibility, unresolved
            exceptions, and required human approvals.
            """
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=["\n\n", "\n", ". ", " ", ""])

    def chunking(self):
        document = Document(page_content=self.policy_document,
            metadata={
                "policy_id": "BANK-PL-2026-001",
                "source": "personal_loan_policy.txt",
                "document_type": "synthetic_policy"
            }
        )
        chunks = self.splitter.split_documents([document])

        for index, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = f"POL-CHUNK-{index + 1:03d}"

        print(f"Total chunks created: {len(chunks)}")
        return chunks
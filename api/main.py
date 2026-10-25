
import streamlit as st
import requests
import uuid


class BankingApp:

    def __init__(self):
        self.loan_api = "http://localhost:8000/loan/approval"
        self.support_api = "http://localhost:8000/support/chat"
        self.kyc_api = "http://localhost:8000/rag/query"

        if "application_id" not in st.session_state:
            st.session_state.application_id = (
                "APP-" + str(uuid.uuid4())[:8].upper()
            )

        if "active_tab" not in st.session_state:
            st.session_state.active_tab = "loan"

    def apply_styles(self):
        st.markdown("""
        <style>
        .stApp {
            background-color: #0b0f19;
            color: #F9FAFB;
        }

        h1, h2, h3, h4, p, label {
            color: #F9FAFB !important;
        }

        div[data-testid="stForm"] {
            background-color: #141b2d;
            padding: 25px;
            border-radius: 15px;
            border: 1px solid #29344d;
        }

        div.stButton > button,
        div[data-testid="stFormSubmitButton"] button {
            background-color: #2563eb;
            color: white;
            border-radius: 8px;
            border: none;
        }

        input, textarea {
            color: #000000 !important;
            background-color: #FFFFFF !important;
        }

        input::placeholder,
        textarea::placeholder {
            color: #6B7280 !important;
        }

        div[data-baseweb="select"] div {
            color: #000000 !important;
        }

        hr {
            border-color: #334155;
        }
        </style>
        """, unsafe_allow_html=True)

    def navigation(self):
        st.title("🏦 Banking AI System")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🏦 Loan Approval", use_container_width=True):
                st.session_state.active_tab = "loan"

        with col2:
            if st.button("💬 Customer Support", use_container_width=True):
                st.session_state.active_tab = "support"

        with col3:
            if st.button("📋 KYC Compliance", use_container_width=True):
                st.session_state.active_tab = "kyc"

        st.divider()

    def loan_page(self):
        application_id = st.session_state.application_id
        data = None

        with st.form("loan_application"):
            st.header("Applicant Details")

            col1, col2 = st.columns(2)

            with col1:
                st.text_input(
                    "Application ID",
                    value=application_id,
                    disabled=True
                )
                applicant_name = st.text_input("Applicant Name")
                date_of_birth = st.date_input("Date of Birth")
                pan_number = st.text_input("PAN Number", max_chars=10)

            with col2:
                credit_score = st.number_input(
                    "Credit Score", 300, 900, 750
                )
                purpose = st.selectbox(
                    "Loan Purpose",
                    [
                        "Home renovation",
                        "Personal expenses",
                        "Education",
                        "Medical expenses",
                        "Other"
                    ]
                )
                mobile_number = st.text_input(
                    "Mobile Number", max_chars=10
                )
                employment_type = st.selectbox(
                    "Employment Type",
                    ["Salaried", "Self-employed", "Business"]
                )

            st.header("Financial Details")

            col1, col2 = st.columns(2)

            with col1:
                monthly_salary = st.number_input(
                    "Monthly Net Salary (₹)",
                    min_value=0,
                    value=85000,
                    step=5000
                )
                existing_emis = st.number_input(
                    "Existing Monthly EMIs (₹)",
                    min_value=0,
                    value=0,
                    step=1000
                )

            with col2:
                loan_amount = st.number_input(
                    "Requested Loan Amount (₹)",
                    min_value=10000,
                    value=800000,
                    step=50000
                )
                interest_rate = st.number_input(
                    "Annual Interest Rate (%)",
                    min_value=0.1,
                    max_value=40.0,
                    value=8.5,
                    step=0.5
                )

            tenure_months = st.selectbox(
                "Loan Tenure",
                [12, 24, 36, 48, 60],
                index=4,
                format_func=lambda m: f"{m} months ({m // 12} years)"
            )

            st.header("Document Verification")

            identity_proof = st.file_uploader(
                "Identity Proof",
                type=["pdf", "png", "jpg", "jpeg"]
            )

            salary_slips = st.file_uploader(
                "Salary Slips",
                type=["pdf", "png", "jpg", "jpeg"],
                accept_multiple_files=True
            )

            bank_statements = st.file_uploader(
                "Bank Statements",
                type=["pdf", "png", "jpg", "jpeg"],
                accept_multiple_files=True
            )

            st.header("Consent and Declaration")

            consent_bureau = st.checkbox(
                "I consent to a credit bureau check."
            )
            consent_terms = st.checkbox(
                "I accept the Terms and Conditions."
            )

            submitted = st.form_submit_button(
                "Submit Loan Application",
                use_container_width=True
            )

        if submitted:
            if not applicant_name.strip():
                st.warning("Please enter the applicant name.")

            elif not consent_bureau or not consent_terms:
                st.warning("Please accept both consent checkboxes.")

            elif (
                identity_proof is None
                and not salary_slips
                and not bank_statements
            ):
                st.warning("Please upload at least one document.")

            else:
                application = {
                    "application_id": application_id,
                    "applicant_name": applicant_name,
                    "date_of_birth": str(date_of_birth),
                    "pan_number": pan_number,
                    "mobile_number": mobile_number,
                    "employment_type": employment_type,
                    "credit_score": int(credit_score),
                    "purpose": purpose,
                    "monthly_salary": monthly_salary,
                    "existing_emis": existing_emis,
                    "loan_amount": loan_amount,
                    "interest_rate": interest_rate,
                    "tenure_months": tenure_months
                }

                files = []

                if identity_proof:
                    files.append((
                        "upload_document",
                        (
                            identity_proof.name,
                            identity_proof.getvalue(),
                            identity_proof.type
                        )
                    ))

                for uploaded_file in salary_slips or []:
                    files.append((
                        "upload_document",
                        (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type
                        )
                    ))

                for uploaded_file in bank_statements or []:
                    files.append((
                        "upload_document",
                        (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type
                        )
                    ))

                with st.spinner("Processing loan application..."):
                    try:
                        response = requests.post(
                            self.loan_api,
                            data=application,
                            files=files,
                            timeout=600
                        )

                        response.raise_for_status()
                        data = response.json()
                        self.show_loan_result(data)

                    except requests.exceptions.ConnectionError:
                        st.error(
                            "Cannot connect to FastAPI. "
                            "Check whether the backend is running."
                        )

                    except requests.exceptions.Timeout:
                        st.error("The loan API request timed out.")

                    except requests.exceptions.RequestException as error:
                        st.error(f"API request failed: {error}")

                    except ValueError as error:
                        st.error(f"Invalid API response: {error}")

        if data is not None:
            self.show_application_status(
                data, application_id, applicant_name, loan_amount
            )

    def show_loan_result(self, data):
        if data.get("status") == "WAITING_FOR_OFFICER":
            st.warning("Application requires officer review.")
            st.json(data.get("review", {}))
            return

        st.success("Loan application processed")

        st.header("Document Extraction")
        st.json(data.get("structured_documents", {}))

        st.header("Verification Results")
        st.json(data.get("verification_result", {}))

        st.header("Eligibility Results")

        eligibility = data.get("eligibility_result") or {}

        col1, col2, col3 = st.columns(3)

        existing_emi = eligibility.get("existing_emi")
        proposed_emi = eligibility.get("proposed_emi")
        salary = eligibility.get("net_salary")

        col1.metric(
            "Existing EMI",
            f"₹{existing_emi:,.2f}"
            if isinstance(existing_emi, (int, float))
            else "N/A"
        )

        col2.metric(
            "Proposed EMI",
            f"₹{proposed_emi:,.2f}"
            if isinstance(proposed_emi, (int, float))
            else "N/A"
        )

        col3.metric(
            "Monthly Salary",
            f"₹{salary:,.2f}"
            if isinstance(salary, (int, float))
            else "N/A"
        )

        st.metric("FOIR", eligibility.get("foir_percent", "N/A"))

        if eligibility.get("eligible") is True:
            st.success("Eligibility checks passed")
        elif eligibility.get("eligible") is False:
            st.error("Eligibility checks failed because FOIR >40%")
        else:
            st.info("Eligibility has not been determined")

        st.header("Retrieved Policy Clauses")

        policies = data.get("policy_results", [])

        if policies:
            for index, policy in enumerate(policies, 1):
                title = (
                    f"Policy {index}: "
                    f"{policy.get('policy_id', 'N/A')}"
                )

                with st.expander(title):
                    st.write("Source:", policy.get("source", "N/A"))
                    st.write("Chunk ID:", policy.get("chunk_id", "N/A"))
                    st.write("Policy text:", policy.get("policy_text", "N/A"))
        else:
            st.info("No policy results were returned.")

        with st.expander("Raw API Response"):
            st.json(data)

    def show_application_status(
        self, data, application_id, applicant_name, loan_amount
    ):
        st.divider()
        st.header("Loan Application Status")

        st.write("Application ID:", application_id)
        st.write("Applicant Name:", applicant_name)
        st.metric("Requested Loan Amount", f"₹{loan_amount:,.2f}")

        eligibility = data.get("eligibility_result") or {}
        proposed_emi = eligibility.get("proposed_emi")

        if isinstance(proposed_emi, (int, float)):
            st.metric("Proposed Monthly EMI", f"₹{proposed_emi:,.2f}")

        status = data.get("status", "PENDING")
        decision = data.get("human_decision") or status

        if status == "WAITING_FOR_OFFICER":
            st.warning("Pending Officer Review")
        elif decision == "APPROVED":
            st.success("Loan Approved")
        elif decision in ("REJECTED", "REJECTED_BY_OFFICER"):
            st.error("Loan Not Approved")
        elif status == "ELIGIBILITY_CHECKS_PASSED":
            st.success("Eligibility Checks Passed")
            st.info("This is not a final loan approval.")
        else:
            st.info("Application Under Review")

        st.write("Application Status:", status)
        st.write(
            "Reason:",
            data.get("reason", "Final decision is not available yet.")
        )
        st.write("Officer Name:", data.get("officer_name", "Not available"))
        st.write("Officer Reason:", data.get("officer_reason", "Not provided"))

    def support_page(self):
        st.header("💬 Customer Support")

        if "support_messages" not in st.session_state:
            st.session_state.support_messages = []

        for message in st.session_state.support_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        query = st.chat_input("Type your question here...")

        if query:
            st.session_state.support_messages.append({
                "role": "user",
                "content": query
            })

            with st.chat_message("user"):
                st.markdown(query)

            answer = self.send_chat_request(
                self.support_api,
                {
                    "message": query,
                    "customer_id": st.session_state.application_id
                }
            )

            with st.chat_message("assistant"):
                st.markdown(answer)

            st.session_state.support_messages.append({
                "role": "assistant",
                "content": answer
            })

        if st.session_state.support_messages:
            if st.button("Clear Support Chat"):
                st.session_state.support_messages = []
                st.rerun()

    def kyc_page(self):
        st.header("📋 KYC Compliance Assistant")

        st.write(
            "Ask a compliance question to search policy documents "
            "and receive an answer."
        )

        if "kyc_messages" not in st.session_state:
            st.session_state.kyc_messages = []

        for message in st.session_state.kyc_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        query = st.chat_input("Type your KYC question...")

        if query:
            st.session_state.kyc_messages.append({
                "role": "user",
                "content": query
            })

            with st.chat_message("user"):
                st.markdown(query)

            answer = self.send_chat_request(
                self.kyc_api,
                {
                    "query": query,
                    "applicant_name": "N/A"
                }
            )

            with st.chat_message("assistant"):
                st.markdown(answer)

            st.session_state.kyc_messages.append({
                "role": "assistant",
                "content": answer
            })

        if st.session_state.kyc_messages:
            if st.button("Clear KYC Chat"):
                st.session_state.kyc_messages = []
                st.rerun()

    def send_chat_request(self, url, payload):
        answer = ""

        try:
            with requests.post(
                url,
                json=payload,
                stream=True,
                timeout=120
            ) as response:
                response.raise_for_status()

                answer_box = st.empty()

                for chunk in response.iter_content(
                    chunk_size=None,
                    decode_unicode=True
                ):
                    if chunk:
                        answer += (
                            chunk if isinstance(chunk, str)
                            else chunk.decode("utf-8")
                        )
                        answer_box.markdown(answer)

            return answer or "The server returned an empty response."

        except requests.exceptions.RequestException as error:
            return f"Could not connect to the backend: {error}"

    def run(self):
        self.apply_styles()
        self.navigation()

        active_tab = st.session_state.active_tab

        if active_tab == "loan":
            self.loan_page()
        elif active_tab == "support":
            self.support_page()
        elif active_tab == "kyc":
            self.kyc_page()


if __name__ == "__main__":
    st.set_page_config(
        layout="wide",
        page_title="Banking AI System"
    )

    app = BankingApp()
    app.run()

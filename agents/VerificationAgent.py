
class VerficationAgent:

    def verfy_application(self, application, salary_slip, bank_statement):

        result = {
            "documents": [],
            "Document_Name": [],
            "Document_Employer": [],
            "Document_Salary": [],
            "Bank_Salary": [],
            "Existing_EMI": []
        }

        if len(salary_slip) != 6 or application["bank_statement_months"] != 6:
            result["documents"].append(
                "All required documents are not present"
            )
        else:
            result["documents"].append("Documents are present")

        for slip in salary_slip:
            if application["applicant_name"] == slip["employee_name"]:
                result["Document_Name"].append(
                    f'{slip["month"]}: Name is matched'
                )
            else:
                result["Document_Name"].append(
                    f'{slip["month"]}: Name is not matched'
                )

        for slip in salary_slip:
            if application["employer_name"] == slip["employer"]:
                result["Document_Employer"].append(
                    f'{slip["month"]}: Employer is matched'
                )
            else:
                result["Document_Employer"].append(
                    f'{slip["month"]}: Employer is not matched'
                )

        for slip in salary_slip:
            if application["monthly_net_salary"] == slip["net_salary"]:
                result["Document_Salary"].append(
                    f'{slip["month"]}: Salary is verified'
                )
            else:
                result["Document_Salary"].append(
                    f'{slip["month"]}: Salary is not matched'
                )

        salary_credits = [
            transaction
            for transaction in bank_statement
            if "SALARY" in transaction["description"].upper()
            and transaction["credit"] > 0
        ]

        for transaction in salary_credits:
            if transaction["credit"] == application["monthly_net_salary"]:
                result["Bank_Salary"].append(
                    f'{transaction["date"]}: Salary credit is verified'
                )
            else:
                result["Bank_Salary"].append(
                    f'{transaction["date"]}: Salary credit is not matched'
                )

        if not salary_credits:
            result["Bank_Salary"].append("No salary credits found")

        emi_found = any(
            "EMI" in transaction["description"].upper()
            and transaction["debit"] == application["existing_monthly_emis"]
            for transaction in bank_statement
        )

        if emi_found:
            result["Existing_EMI"].append("Existing EMI is verified")
        else:
            result["Existing_EMI"].append(
                "Existing EMI could not be verified"
            )

        return result


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

    salary_slip = [
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

    agent = VerficationAgent()

    verify = agent.verfy_application(
        application, salary_slip, bank_statement
    )

    for key, value in verify.items():
        print(f"{key}: {value}")

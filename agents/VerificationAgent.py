import json
import os
import calendar
from datetime import datetime
from collections import defaultdict

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_filepath = os.path.join(base_dir, "data", "structured_output.json")

class VerficationAgent:
    def verify_application(self, state, customer_document):
        application_name = state['application'].get("applicant_name", "")

        verify = {
            "Document_check": [],
            "Application_Name": "",
            "emi_existing": [],
            "Transaction_Flagging": [],
            "salary_slip": []
        }

        if (len(customer_document.get("salaryslip", [])) >= 6 and len(customer_document.get("bankstatement", [])) >= 1):
            salaryslip_month = []

            for slip in customer_document.get("salaryslip", []):
                salaryslip_month.append(slip.get("salary_month"))

            salaryslip_month.sort(
                key=lambda month: datetime.strptime(month, "%Y-%m")
            )
            missing_months = []

            for i in range(1, len(salaryslip_month)):
                previous = datetime.strptime(salaryslip_month[i - 1], "%Y-%m")
                current = datetime.strptime(salaryslip_month[i], "%Y-%m")

                year = previous.year
                month = previous.month + 1

                if month > 12:
                    month = 1
                    year += 1

                while (year, month) < (current.year, current.month):
                    missing_months.append(
                        f"{calendar.month_name[month]} {year}"
                    )

                    month += 1
                    if month > 12:
                        month = 1
                        year += 1

            if len(missing_months) == 0:
                verify["Document_check"].append({
                    "check": "document_completeness",
                    "passed": True,
                    "detail": "6 salary slips and 6 months of bank statements present"
                })
            elif len(missing_months) > 0:
                verify["Document_check"].append({
                    "check": "document_completeness",
                    "passed": False,
                    "detail": f"missing Documents are: {missing_months}"
                })

        salary_statement_name = []

        bank_statement = customer_document.get("bankstatement", [])

        account_holder_name = (
            bank_statement[0].get("account_holder_name", "")
            if bank_statement
            else ""
        )

        identifier = customer_document.get("identifier") or []
        pancard_name = (
            identifier[0].get("full_name", "")
            if len(identifier) > 0 and isinstance(identifier[0], dict)
            else ""
        )

        aadhar_name = (
            identifier[1].get("full_name", "")
            if len(identifier) > 1 and isinstance(identifier[1], dict)
            else ""
        )

        for slip in customer_document.get("salaryslip", []):
            salary_statement_name.append(slip.get("employee_name", ""))

        name = []

        for saal in salary_statement_name:
            if application_name.strip().casefold() == saal.strip().casefold():
                name.append("true")
            else:
                name.append("false")

        for person_name in [
            account_holder_name,
            pancard_name,
            aadhar_name
        ]:
            if (
                application_name.strip().casefold()
                == person_name.strip().casefold()
            ):
                name.append("true")
            else:
                name.append("false")

        if all(result == "true" for result in name):
            verify['Application_Name'] = {
                "check": "name_consistency",
                "passed": True,
                "detail": (
                    f"Application='{application_name}', "
                    f"Salary slips={salary_statement_name}, "
                    f"Bank='{account_holder_name}', "
                    f"PAN='{pancard_name}', "
                    f"Aadhaar='{aadhar_name}' — match"
                )
            }
        else:
            verify['Application_Name'] = {
                "check": "name_consistency",
                "passed": False,
                "detail": (
                    f"Application='{application_name}', "
                    f"Salary slips={salary_statement_name}, "
                    f"Bank='{account_holder_name}', "
                    f"PAN='{pancard_name}', "
                    f"Aadhaar='{aadhar_name}' — mismatch"
                )
            }

        bank_statement = customer_document.get('bankstatement', [])

        for statement in bank_statement:
            for transaction in statement.get('transactions', []):
                if transaction.get("possible_emi_or_loan_payment") is True:
                    verify['emi_existing'].append(
                        {
                            "transaction_date": transaction.get('transaction_date', ""),
                            "description": transaction.get('description', ""),
                            "credit_amt": transaction.get('credit_amount', ""),
                            "balance": transaction.get('balance', ""),
                            "debt": transaction.get('debit_amount', ""),
                            "transaction_category": transaction.get("transaction_category", ""),
                        }
                    )

        for statement in bank_statement:
            for transaction in statement.get('transactions', []):
                if transaction.get("transaction_category", "") == "unknown":
                    verify['Transaction_Flagging'].append(
                        {
                            "transaction_date": transaction.get('transaction_date', ""),
                            "description": transaction.get('description', ""),
                            "credit_amt": transaction.get('credit_amount', ""),
                            "balance": transaction.get('balance', ""),
                            "transaction_category": transaction.get("transaction_category", ""),
                            "Flag": "Needs clarification"
                        }
                    )

        salary_slips = customer_document.get('salaryslip', [])

        if salary_slips:
            salary_by_month = {}

            for slip in salary_slips:
                month = slip.get('salary_month', '')
                salary = slip.get('net_salary', 0)

                salary_by_month[month] = salary

            salaries = list(salary_by_month.values())
            first_salary = salaries[0]

            salary_match = all(
                abs(salary - first_salary) <= first_salary * 0.01
                for salary in salaries
            )

            if salary_match:
                verify['salary_slip'].append(
                    {
                        "check": "salary_consistency",
                        "passed": True,
                        "detail": (
                            f"All {len(salaries)} months: "
                            f"₹{first_salary:,.0f} (0% variance)"
                        )
                    }
                )

            else:
                salary_details = ", ".join(
                    f"{month}="
                    f"₹{salary:,.0f}"
                    for month, salary in salary_by_month.items()
                )

                lowest_salary = min(salaries)
                drop_percentage = (
                    (first_salary - lowest_salary) / first_salary * 100
                    if first_salary > 0 else 0
                )

                lowest_month = next(
                    month for month, salary in salary_by_month.items()
                    if salary == lowest_salary
                )

                verify['salary_slip'].append(
                    {
                        "check": "salary_consistency",
                        "passed": False,
                        "detail": (
                            f"{salary_details} — "
                            f"{drop_percentage:.0f}% drop in {lowest_month}"
                        )
                    }
                )

        return verify
        
if __name__ == "__main__":
    with open(json_filepath, "r", encoding="utf-8") as structure_data:
        app = json.load(structure_data)

    agent = VerficationAgent()
    verify = agent.verify_application({
            "application": {
        "application_name": "Ravi Kumar"
    }
    }, app)
    print(verify)
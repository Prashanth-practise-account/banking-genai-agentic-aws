
class EligibilityAgent:

    def calculateEMI(self, loan_amount, annual_interest_rate, tenure_years):

        def MonthlyIntrestRate(anualintrestrate):
            r = anualintrestrate / (12 * 100)
            return r

        def proposedmonthlyemi(p, n, r):
            if r == 0:
                emi = p / n
            else:
                emi = p * r * (1 + r) ** n / ((1 + r) ** n - 1)
            return emi

        r = MonthlyIntrestRate(annual_interest_rate)
        n = tenure_years * 12

        emi = proposedmonthlyemi(loan_amount, n, r)
        return emi

    def FOIR(self, existing_emi, proposed_emi, monthly_net_salary):
        
        foir = ((existing_emi + proposed_emi) / monthly_net_salary) * 100

        foir_threshold = 40
        eligible = foir <= foir_threshold

        return {
            "foir_percentage": round(foir, 2),
            "foir_threshold": foir_threshold,
            "affordability_check": (
                "PASS" if eligible else "FAIL"
            ),
            "reason": (
                "FOIR is within the synthetic policy limit."
                if eligible
                else "FOIR exceeds the synthetic policy limit."
            )
        }


if __name__ == "__main__":

    application = {
        "application_id": "APP-1001",
        "applicant_name": "Ravi Kumar",
        "monthly_net_salary": 85000,
        "existing_monthly_emis": 12000,
        "requested_loan_amount": 800000,
        "annual_interest_rate": 8.5,
        "tenure_years": 5
    }

    agent = EligibilityAgent()

    proposed_emi = agent.calculateEMI(
        application["requested_loan_amount"],
        application["annual_interest_rate"],
        application["tenure_years"]
    )

    result = agent.FOIR(
        application["existing_monthly_emis"],
        proposed_emi,
        application["monthly_net_salary"]
    )

    print("Application ID:", application["application_id"])
    print("Applicant:", application["applicant_name"])
    print("Monthly Salary:", application["monthly_net_salary"])
    print("Existing EMI:", application["existing_monthly_emis"])
    print("Proposed EMI:", round(proposed_emi, 2))

    for key, value in result.items():
        print(f"{key}: {value}")

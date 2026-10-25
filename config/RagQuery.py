from pydantic import BaseModel

class RagQuery(BaseModel):
    query: str
    applicant_name: str = "N/A"
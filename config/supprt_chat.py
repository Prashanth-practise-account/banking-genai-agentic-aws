from pydantic import BaseModel

class SupportChatRequest(BaseModel):
    message: str
    customer_id: str
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email_or_phone: str
    password: str

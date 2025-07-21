from pydantic import BaseModel, EmailStr

# These DTOs for the 
class CandidateResponse(BaseModel):
    email: EmailStr
    full_name: str
    phone: str | None = None
    skills: list[str] | None = None
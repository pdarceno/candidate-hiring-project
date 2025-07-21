from pydantic import BaseModel, EmailStr
from uuid import UUID

class CandidateCreate(BaseModel):
    email: EmailStr
    full_name: str
    phone: str | None = None
    skills: list[str] | None = None

class CandidateUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    skills: list[str] | None = None

class CandidateResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    phone: str | None = None
    skills: list[str] | None = None
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


class CandidateResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    phone: str | None = None
    skills: list[str] | None = None
from pydantic import BaseModel
from uuid import UUID

class ApplicationCreate(BaseModel):
    job_title: str
    candidate_id: UUID

class ApplicationUpdate(BaseModel):
    status: str

class ApplicationResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    job_title: str
    status: str
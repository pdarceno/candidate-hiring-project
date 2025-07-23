from pydantic import BaseModel, ConfigDict
from ..entities.application import ApplicationStatus
from uuid import UUID

class ApplicationCreate(BaseModel):
    candidate_id: UUID
    job_title: str
    status: ApplicationStatus

class ApplicationUpdate(BaseModel):
    status: ApplicationStatus

class ApplicationResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    job_title: str
    status: ApplicationStatus

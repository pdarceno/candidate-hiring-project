from pydantic import BaseModel
from uuid import UUID

class ApplicationResponse(BaseModel):
    job_id: UUID
    candidate_id: UUID
    status: str
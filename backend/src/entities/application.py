from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from enum import Enum as PyEnum
from ..database.core import Base

class ApplicationStatus(PyEnum):
    APPLIED = "APPLIED"
    INTERVIEWING = "INTERVIEWING"
    REJECTED = "REJECTED"
    HIRED = "HIRED"


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False, index=True)
    job_title = Column(String, nullable=False, index=True)
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.APPLIED, index=True)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())


    def __repr__(self):
        return f"<Application(candidate_id='{self.candidate_id}', job_title='{self.job_title}', status='{self.status.name}')>"

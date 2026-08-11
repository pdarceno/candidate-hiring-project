from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid
from ..database.core import Base 

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    skills = Column(JSON, nullable=True)
    profile_links = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Candidate(email='{self.email}', full_name='{self.full_name}', phone='{self.phone}', skills='{self.skills}', profile_links='{self.profile_links}', created_at='{self.created_at}')>"
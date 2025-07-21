from uuid import UUID
from sqlalchemy.orm import Session
from . import model
from ..entities.candidate import Candidate
from ..local_exceptions import ApplicationNotFoundError, CandidateNotFoundError, ApplicationAlreadyExistsError
import logging

def apply_to_job(db: Session, candidate_id: UUID, application_data: model.ApplicationResponse) -> model.ApplicationResponse:
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        logging.warning(f"Candidate not found with ID: {candidate_id}")
        raise CandidateNotFoundError(candidate_id)

    new_application = model.ApplicationResponse(
        candidate_id=candidate_id,
        job_id=application_data.job_id,
        status=application_data.status,
        applied_at=application_data.applied_at
    )
    
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    logging.info(f"Application created for candidate ID: {candidate_id}")
    return new_application

def list_applications_for_candidate(db: Session, candidate_id: UUID) -> list[model.ApplicationResponse]:
    applications = db.query(model.ApplicationResponse).filter(model.ApplicationResponse.candidate_id == candidate_id).all()
    logging.info(f"Listing applications for candidate ID: {candidate_id}")
    return applications

def update_application_status(db: Session, application_id: UUID, status_update: model.ApplicationResponse) -> model.ApplicationResponse:
    application = db.query(model.ApplicationResponse).filter(model.ApplicationResponse.id == application_id).first()
    if not application:
        logging.warning(f"Application not found with ID: {application_id}")
        raise ApplicationNotFoundError(application_id)

    application.status = status_update.status
    db.commit()
    db.refresh(application)
    logging.info(f"Application status updated for ID: {application_id}")
    return application
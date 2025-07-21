from uuid import UUID
from sqlalchemy.orm import Session
from . import model
from ..entities.candidate import Candidate
from ..entities.application import Application, ApplicationStatus
from ..local_exceptions import ApplicationNotFoundError, CandidateNotFoundError, ApplicationAlreadyExistsError
import logging

def apply_to_job(db: Session, application_data: model.ApplicationCreate) -> model.ApplicationResponse:
    candidate = db.query(Candidate).filter(Candidate.id == application_data.candidate_id).first()
    if not candidate:
        logging.warning(f"Candidate not found with ID: {application_data.candidate_id}")
        raise CandidateNotFoundError(application_data.candidate_id)

    new_application = Application(
        candidate_id=application_data.candidate_id,
        job_title=application_data.job_title,
        status=ApplicationStatus.APPLIED
    )
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    logging.info(f"Application created for candidate ID: {application_data.candidate_id}")
    return model.ApplicationResponse(
        id=new_application.id,
        candidate_id=new_application.candidate_id,
        job_title=new_application.job_title,
        status=new_application.status
    )

def list_applications_for_candidate(db: Session, candidate_id: UUID) -> list[model.ApplicationResponse]:
    applications = db.query(Application).filter(Application.candidate_id == candidate_id).all()
    logging.info(f"Listing applications for candidate ID: {candidate_id}")
    return [
        model.ApplicationResponse(
            id=a.id,
            candidate_id=a.candidate_id,
            job_title=a.job_title,
            status=a.status
        ) for a in applications
    ]

def update_application_status(db: Session, application_id: UUID, status_update: model.ApplicationUpdate) -> model.ApplicationResponse:
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        logging.warning(f"Application not found with ID: {application_id}")
        raise ApplicationNotFoundError(application_id)

    application.status = status_update.status
    db.commit()
    db.refresh(application)
    return model.ApplicationResponse(
        id=application.id,
        candidate_id=application.candidate_id,
        job_title=application.job_title,
        status=application.status
    )
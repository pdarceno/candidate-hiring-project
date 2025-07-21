from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import model
from ..entities.candidate import Candidate
from ..entities.application import Application, ApplicationStatus
from ..local_exceptions import ApplicationNotFoundError, CandidateNotFoundError, ApplicationAlreadyExistsError
import logging

async def apply_to_job(db: AsyncSession, application_data: model.ApplicationCreate) -> model.ApplicationResponse:
    result = await db.execute(select(Candidate).where(Candidate.id == application_data.candidate_id))
    candidate = result.scalar_one_or_none()
    if not candidate:
        logging.warning(f"Candidate not found with ID: {application_data.candidate_id}")
        raise CandidateNotFoundError(application_data.candidate_id)

    existing_app = await db.execute(
        select(Application).where(
            Application.candidate_id == application_data.candidate_id,
            Application.job_title == application_data.job_title
        )
    )
    if existing_app.scalar_one_or_none():
        raise ApplicationAlreadyExistsError(application_data.candidate_id, application_data.job_title)
    
    try:
        new_application = Application(
            candidate_id=application_data.candidate_id,
            job_title=application_data.job_title,
            status=ApplicationStatus.APPLIED
        )
        db.add(new_application)
        await db.commit()
        await db.refresh(new_application)
        logging.info(f"Application created for candidate ID: {application_data.candidate_id}")
        return model.ApplicationResponse(
            id=new_application.id,
            candidate_id=new_application.candidate_id,
            job_title=new_application.job_title,
            status=new_application.status
        )
    except Exception as e:
        logging.error(f"Error applying to job: {e}")
        await db.rollback()
        raise ApplicationNotFoundError(application_data.candidate_id) from e

async def list_applications_for_candidate(db: AsyncSession, candidate_id: UUID) -> list[model.ApplicationResponse]:
    try:
        result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
        if not result.scalar_one_or_none():
            raise CandidateNotFoundError(candidate_id)
        result = await db.execute(select(Application).where(Application.candidate_id == candidate_id))
        applications = result.scalars().all()
        
        logging.info(f"Found {len(applications)} applications for candidate ID: {candidate_id}")
        return [
            model.ApplicationResponse(
                id=a.id,
                candidate_id=a.candidate_id,
                job_title=a.job_title,
                status=a.status
            ) for a in applications
        ]
    except Exception as e:
        logging.error(f"Error listing applications for candidate {candidate_id}: {e}")
        raise

async def update_application_status(db: AsyncSession, application_id: UUID, status_update: model.ApplicationUpdate) -> model.ApplicationResponse:
    try:
        result = await db.execute(select(Application).where(Application.id == application_id))
        application = result.scalar_one_or_none()
        if not application:
            logging.warning(f"Application not found with ID: {application_id}")
            raise ApplicationNotFoundError(application_id)

        application.status = status_update.status
        await db.commit()
        await db.refresh(application)
        return model.ApplicationResponse(
            id=application.id,
            candidate_id=application.candidate_id,
            job_title=application.job_title,
            status=application.status
        )
    except Exception as e:
        logging.error(f"Error updating application status: {e}")
        await db.rollback()
        raise ApplicationNotFoundError(application_id) from e
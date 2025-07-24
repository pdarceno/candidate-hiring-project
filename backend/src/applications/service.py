from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import model
from ..entities.candidate import Candidate
from ..entities.application import Application, ApplicationStatus
from ..local_exceptions import ApplicationNotFoundError, CandidateNotFoundError, ApplicationAlreadyExistsError
from ..caching.service import cache_service
import logging
import os

redis_cache_ttl = int(os.getenv('REDIS_CACHE_TTL'))
redis_cache_list_ttl = int(os.getenv('REDIS_CACHE_LIST_TTL'))

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
        
        application_response = model.ApplicationResponse(
            id=new_application.id,
            candidate_id=new_application.candidate_id,
            job_title=new_application.job_title,
            status=new_application.status
        )
        
        cache_key = f"application:{new_application.id}"
        cache_service.set(cache_key, application_response.model_dump(), ttl=redis_cache_ttl)
        
        cache_service.clear_pattern(f"applications:candidate:{application_data.candidate_id}:*")
        
        logging.info(f"Application created and cached for candidate ID: {application_data.candidate_id}")
        return application_response
    except Exception as e:
        logging.error(f"Error applying to job: {e}")
        await db.rollback()
        raise

async def list_applications_for_candidate(db: AsyncSession, candidate_id: UUID, status: ApplicationStatus = ApplicationStatus.APPLIED) -> list[model.ApplicationResponse]:
    cache_key = f"applications:candidate:{candidate_id}:status:{status.value if status else 'all'}"
    cached_applications = cache_service.get(cache_key)
    
    if cached_applications:
        logging.info(f"Cache hit for applications list (candidate={candidate_id}, status={status})")
        return [model.ApplicationResponse(**app) for app in cached_applications]
    
    logging.info(f"Cache miss for applications list, querying database")
    try:
        result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
        if not result.scalar_one_or_none():
            raise CandidateNotFoundError(candidate_id)

        query = select(Application).where(Application.candidate_id == candidate_id)
        if status:
            query = query.where(Application.status == status)

        result = await db.execute(query)
        applications = result.scalars().all()

        application_responses = [
            model.ApplicationResponse(
                id=a.id,
                candidate_id=a.candidate_id,
                job_title=a.job_title,
                status=a.status
            ) for a in applications
        ]
        
        applications_data = [app.model_dump() for app in application_responses]
        cache_service.set(cache_key, applications_data, ttl=redis_cache_list_ttl)

        logging.info(f"Found and cached {len(applications)} applications for candidate ID: {candidate_id} with status: {status}")
        return application_responses
    except Exception as e:
        logging.error(f"Database error listing applications for candidate {candidate_id}: {e}")
        raise

async def update_application_status(db: AsyncSession, application_id: UUID, status_update: model.ApplicationUpdate) -> model.ApplicationResponse:
    try:
        result = await db.execute(select(Application).where(Application.id == application_id))
        application = result.scalar_one_or_none()
        if not application:
            logging.warning(f"Application not found with ID: {application_id}")
            raise ApplicationNotFoundError(application_id)

        application.status = ApplicationStatus(status_update.status)
        await db.commit()
        await db.refresh(application)
        
        application_response = model.ApplicationResponse(
            id=application.id,
            candidate_id=application.candidate_id,
            job_title=application.job_title,
            status=application.status
        )
        
        cache_key = f"application:{application_id}"
        cache_service.delete(cache_key)
        
        cache_service.clear_pattern(f"applications:candidate:{application.candidate_id}:*")
        
        cache_service.set(cache_key, application_response.model_dump(), ttl=redis_cache_ttl)
        
        logging.info(f"Application status updated and cache invalidated for ID: {application_id}")
        return application_response
    except Exception as e:
        logging.error(f"Database error updating application status: {e}")
        await db.rollback()
        raise
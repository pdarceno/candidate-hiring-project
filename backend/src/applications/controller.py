from fastapi import APIRouter, status
from uuid import UUID
from ..database.core import DBSession
from . import model
from . import service
from ..auth.service import CurrentUser
from ..entities.application import ApplicationStatus

router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)

@router.post("/", response_model=model.ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_to_job(application_data: model.ApplicationCreate, db: DBSession, _: CurrentUser):
    return await service.apply_to_job(db, application_data)

@router.get("/candidate/{candidate_id}", response_model=list[model.ApplicationResponse])
async def list_applications_for_candidate(candidate_id: UUID, db: DBSession, _: CurrentUser, status: ApplicationStatus = ApplicationStatus.APPLIED):
    return await service.list_applications_for_candidate(db, candidate_id, status=status)

@router.patch("/{application_id}", response_model=model.ApplicationResponse)
async def update_application_status(application_id: UUID, status_update: model.ApplicationUpdate, db: DBSession, _: CurrentUser):
    return await service.update_application_status(db, application_id, status_update)
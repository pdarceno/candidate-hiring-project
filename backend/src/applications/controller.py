from fastapi import APIRouter, status
from uuid import UUID
from ..database.core import DBSession
from . import model
from . import service
from ..auth.service import CurrentUser

router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)

@router.post("/", response_model=model.ApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_to_job(application_data: model.ApplicationResponse, db: DBSession, candidate_id: UUID, _: CurrentUser):
    return service.apply_to_job(db, candidate_id, application_data)

@router.get("/candidate/{candidate_id}", response_model=list[model.ApplicationResponse])
def list_applications_for_candidate(candidate_id: UUID, db: DBSession, _: CurrentUser):
    return service.list_applications_for_candidate(db, candidate_id)

@router.patch("/{application_id}", response_model=model.ApplicationResponse)
def update_application_status(application_id: UUID, status_update: model.ApplicationResponse, db: DBSession, _: CurrentUser):
    return service.update_application_status(db, application_id, status_update)
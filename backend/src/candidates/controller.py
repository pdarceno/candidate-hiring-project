
from fastapi import APIRouter, status
from uuid import UUID
from ..database.core import DBSession
from . import model
from . import service
from ..auth.service import CurrentUser

router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"]
)

@router.post("/", response_model=model.CandidateResponse, status_code=status.HTTP_201_CREATED)
def create_candidate(candidate: model.CandidateCreate, db: DBSession, _: CurrentUser):
    return service.create_candidate(db, candidate)

@router.get("/{candidate_id}", response_model=model.CandidateResponse)
def get_candidate(candidate_id: UUID, db: DBSession, _: CurrentUser):
    return service.get_candidate_by_id(db, candidate_id)

@router.get("/", response_model=list[model.CandidateResponse])
def get_candidates(skip: int = 0, limit: int = 20, skill: str | None = None, db: DBSession = None, _: CurrentUser = None):
    return service.get_candidates(db, skip, limit, skill)

@router.put("/{candidate_id}", response_model=model.CandidateResponse)
def update_candidate(candidate_id: UUID, candidate: model.CandidateUpdate, db: DBSession, _: CurrentUser):
    return service.update_candidate(db, candidate_id, candidate)
from fastapi import APIRouter, Depends, status, HTTPException, Query, File, UploadFile
from uuid import UUID
from typing import Optional
from ..database.core import DBSession
from . import model
from . import service
from ..auth.service import CurrentUser
from ..entities.task import TaskType
from ..queues.redis_config import get_redis_connection
from ..queues.tasks import CandidateTaskProcessor

router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"]
)

redis_con = get_redis_connection()
task_processor = CandidateTaskProcessor(redis_con)

@router.post("/", response_model=model.CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(candidate: model.CandidateCreate, db: DBSession, _: CurrentUser):
    return await service.create_candidate(db, candidate)

@router.get("/{candidate_id}", response_model=model.CandidateResponse)
async def get_candidate(candidate_id: UUID, db: DBSession, _: CurrentUser):
    return await service.get_candidate_by_id(db, candidate_id)

@router.get("/", response_model=list[model.CandidateResponse])
async def get_candidates(offset: int = 0, limit: int = 20, skill: str | None = None, db: DBSession = None, _: CurrentUser = None):
    return await service.get_candidates(db, offset, limit, skill)

@router.put("/{candidate_id}", response_model=model.CandidateResponse)
async def update_candidate(candidate_id: UUID, candidate: model.CandidateUpdate, db: DBSession = None, _: CurrentUser = None):
    return await service.update_candidate(db, candidate_id, candidate)

@router.post("/{candidate_id}/resume-parsing", status_code=status.HTTP_202_ACCEPTED)
async def enqueue_resume_parsing(candidate_id: UUID, file: UploadFile = File(...), db: DBSession = None, _: CurrentUser = None):
    await service.enqueue_resume_parsing_task_with_file(db, candidate_id, file, task_processor)
    return {"message": "Resume parsing task enqueued successfully."}

@router.post("/{candidate_id}/profile-enrichment", status_code=status.HTTP_202_ACCEPTED)
async def enqueue_profile_enrichment(candidate_id: UUID, file: UploadFile = File(...), db: DBSession = None, _: CurrentUser = None):
    await service.enqueue_profile_enrichment_task_with_file(db, candidate_id, file, task_processor)
    return {"message": "Profile enrichment task enqueued successfully."}

@router.get("/queue/metrics")
async def get_queue_metrics(_: CurrentUser):
    """Get queue processing metrics"""
    return service.get_queue_metrics(task_processor)
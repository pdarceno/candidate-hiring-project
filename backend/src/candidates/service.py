import asyncio
from uuid import UUID
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import model
from ..entities.task import TaskType
from ..entities.candidate import Candidate
from ..local_exceptions import CandidateNotFoundError, CandidateAlreadyExistsError
from ..queues.tasks import CandidateTaskProcessor
from ..caching.service import cache_service
import logging
from PyPDF2 import PdfReader
from docx import Document
import os

redis_cache_ttl = int(os.getenv('REDIS_CACHE_TTL'))
redis_cache_list_ttl = int(os.getenv('REDIS_CACHE_LIST_TTL'))

async def create_candidate(db: AsyncSession, candidate: model.CandidateCreate) -> model.CandidateResponse:
    result = await db.execute(select(Candidate).where(Candidate.email == candidate.email))
    existing_candidate = result.scalar_one_or_none()
    if existing_candidate:
        logging.warning(f"Candidate with email {candidate.email} already exists.")
        raise CandidateAlreadyExistsError(email=candidate.email)
    try:
        new_candidate = Candidate(
            full_name=candidate.full_name,
            email=candidate.email,
            phone=candidate.phone,
            skills=candidate.skills
        )
        db.add(new_candidate)
        await db.commit()
        await db.refresh(new_candidate)
        
        candidate_response = model.CandidateResponse(
            id=new_candidate.id,
            email=new_candidate.email,
            full_name=new_candidate.full_name,
            phone=new_candidate.phone,
            skills=new_candidate.skills
        )
        
        cache_key = f"candidate:{new_candidate.id}"
        cache_service.set(cache_key, candidate_response.model_dump(), ttl=redis_cache_ttl)
        
        cache_service.clear_pattern("candidates:*")
        
        logging.info(f"Candidate created and cached with ID: {new_candidate.id}")
        return candidate_response
    except Exception as e:
        logging.error(f"Error creating candidate: {e}")
        await db.rollback()
        raise

async def get_candidate_by_id(db: AsyncSession, candidate_id: UUID) -> model.CandidateResponse:
    
    cache_key = f"candidate:{candidate_id}"
    cached_candidate = cache_service.get(cache_key)
    
    if cached_candidate:
        logging.info(f"Cache hit for candidate {candidate_id}")
        return model.CandidateResponse(**cached_candidate)
    
    logging.info(f"Cache miss for candidate {candidate_id}, querying database")
    try:
        result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
        candidate = result.scalar_one_or_none()
        if not candidate:
            logging.warning(f"Candidate not found with ID: {candidate_id}")
            raise CandidateNotFoundError(candidate_id)
        
        candidate_response = model.CandidateResponse(
            id=candidate.id,
            email=candidate.email,
            full_name=candidate.full_name,
            phone=candidate.phone,
            skills=candidate.skills
        )
        
        cache_service.set(cache_key, candidate_response.model_dump(), ttl=redis_cache_ttl)
        logging.info(f"Successfully retrieved and cached candidate with ID: {candidate_id}")
        
        return candidate_response
    except Exception as e:
        logging.error(f"Database error retrieving candidate {candidate_id}: {e}")
        raise

async def get_candidates(db: AsyncSession, offset: int = 0, limit: int = 20, skill: str | None = None) -> list[model.CandidateResponse]:
    cache_key = f"candidates:offset:{offset}:limit:{limit}:skill:{skill or 'none'}"
    cached_candidates = cache_service.get(cache_key)
    
    if cached_candidates:
        logging.info(f"Cache hit for candidates list (offset={offset}, limit={limit}, skill={skill})")
        return [model.CandidateResponse(**candidate) for candidate in cached_candidates]
    
    logging.info(f"Cache miss for candidates list, querying database")
    try:
        stmt = select(Candidate)
        if skill:
            stmt = stmt.where(Candidate.skills.contains([skill]))
            
        stmt = stmt.offset(offset).limit(limit)
        result = await db.execute(stmt)
        candidates = result.scalars().all()
        
        candidate_responses = [model.CandidateResponse(
            id=c.id,
            email=c.email,
            full_name=c.full_name,
            phone=c.phone,
            skills=c.skills
        ) for c in candidates]
        
        candidates_data = [candidate.model_dump() for candidate in candidate_responses]
        cache_service.set(cache_key, candidates_data, ttl=redis_cache_list_ttl)
        
        logging.info(f"Retrieved and cached {len(candidates)} candidates from the database.")
        return candidate_responses
    except Exception as e:
        logging.error(f"Error retrieving candidates: {e}")
        raise

async def update_candidate(db: AsyncSession, candidate_id: UUID, candidate_data: model.CandidateUpdate) -> model.CandidateResponse:
    try:
        result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
        candidate = result.scalar_one_or_none()
        if not candidate:
            logging.warning(f"Candidate not found with ID: {candidate_id}")
            raise CandidateNotFoundError(candidate_id)

        for key, value in candidate_data.model_dump(exclude_unset=True).items():
            setattr(candidate, key, value)

        await db.commit()
        await db.refresh(candidate)
        
        candidate_response = model.CandidateResponse(
            id=candidate.id,
            email=candidate.email,
            full_name=candidate.full_name,
            phone=candidate.phone,
            skills=candidate.skills
        )
        
        cache_key = f"candidate:{candidate_id}"
        cache_service.delete(cache_key)
        
        cache_service.clear_pattern("candidates:*")
        
        cache_service.set(cache_key, candidate_response.model_dump(), ttl=redis_cache_ttl)
        
        logging.info(f"Candidate updated and cache invalidated for ID: {candidate.id}")
        return candidate_response
    except Exception as e:
        logging.error(f"Error updating candidate: {e}")
        await db.rollback()
        raise

async def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from an uploaded file (PDF or Word)."""
    if file.content_type == "application/pdf":
        pdf_reader = PdfReader(file.file)
        return "\n".join(page.extract_text() for page in pdf_reader.pages)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file.file)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    else:
        raise ValueError("Unsupported file type. Only PDF and Word documents are allowed.")

async def enqueue_resume_parsing_task_with_file(db: AsyncSession, candidate_id: UUID, file: UploadFile, task_processor: CandidateTaskProcessor):
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise CandidateNotFoundError(candidate_id=candidate_id)

    resume_content = await extract_text_from_file(file)
    payload = {"resume_content": resume_content}
    task_processor.enqueue_task(candidate_id, TaskType.RESUME_PARSING, payload)
    logging.info(f"Enqueued resume parsing task for candidate {candidate_id}")

async def enqueue_profile_enrichment_task_with_file(db: AsyncSession, candidate_id: UUID, file: UploadFile, task_processor: CandidateTaskProcessor):
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise CandidateNotFoundError(candidate_id=candidate_id)

    enrichment_request = await extract_text_from_file(file)
    payload = {"enrichment_request": enrichment_request}
    task_processor.enqueue_task(candidate_id, TaskType.EXTERNAL_ENRICHMENT, payload)
    logging.info(f"Enqueued profile enrichment task for candidate {candidate_id}")

def get_queue_metrics(task_processor):
    return task_processor.get_metrics()

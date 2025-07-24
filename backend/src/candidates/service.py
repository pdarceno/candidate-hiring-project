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
import logging
from PyPDF2 import PdfReader
from docx import Document

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
        logging.info(f"Candidate created with ID: {new_candidate.id}")
        return model.CandidateResponse(
            id=new_candidate.id,
            email=new_candidate.email,
            full_name=new_candidate.full_name,
            phone=new_candidate.phone,
            skills=new_candidate.skills
        )
    except Exception as e:
        logging.error(f"Error creating candidate: {e}")
        await db.rollback()
        raise

async def get_candidate_by_id(db: AsyncSession, candidate_id: UUID) -> model.CandidateResponse:
    try:
        result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
        candidate = result.scalar_one_or_none()
        if not candidate:
            logging.warning(f"Candidate not found with ID: {candidate_id}")
            raise CandidateNotFoundError(candidate_id)
        logging.info(f"Successfully retrieved candidate with ID: {candidate_id}")
        return model.CandidateResponse(
            id=candidate.id,
            email=candidate.email,
            full_name=candidate.full_name,
            phone=candidate.phone,
            skills=candidate.skills
        )
    except Exception as e:
        logging.error(f"Database error retrieving candidate {candidate_id}: {e}")
        raise

async def get_candidates(db: AsyncSession, offset: int = 0, limit: int = 20, skill: str | None = None) -> list[model.CandidateResponse]:
    try:
        stmt = select(Candidate)
        if skill:
            stmt = stmt.where(Candidate.skills.contains([skill]))
            
        stmt = stmt.offset(offset).limit(limit)
        result = await db.execute(stmt)
        candidates = result.scalars().all()
        logging.info(f"Retrieved {len(candidates)} candidates from the database.")
        return [model.CandidateResponse(
            id=c.id,
            email=c.email,
            full_name=c.full_name,
            phone=c.phone,
            skills=c.skills
        ) for c in candidates]
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
        logging.info(f"Candidate updated with ID: {candidate.id}")
        return model.CandidateResponse(
            id=candidate.id,
            email=candidate.email,
            full_name=candidate.full_name,
            phone=candidate.phone,
            skills=candidate.skills
        )
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

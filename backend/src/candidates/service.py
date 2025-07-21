from uuid import UUID
from sqlalchemy.orm import Session
from . import model
from ..entities.candidate import Candidate
from ..local_exceptions import CandidateNotFoundError, CandidateAlreadyExistsError
import logging

def create_candidate(db: Session, candidate: model.CandidateCreate) -> model.CandidateResponse:
    existing_candidate = db.query(Candidate).filter(Candidate.email == candidate.email).first()
    if existing_candidate:
        logging.warning(f"Candidate with email {candidate.email} already exists.")
        raise CandidateAlreadyExistsError(email=candidate.email)

    new_candidate = Candidate(
        full_name=candidate.full_name,
        email=candidate.email,
        phone=candidate.phone,
        skills=candidate.skills
    )
    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    logging.info(f"Candidate created with ID: {new_candidate.id}")
    return model.CandidateResponse(
        id=new_candidate.id,
        email=new_candidate.email,
        full_name=new_candidate.full_name,
        phone=new_candidate.phone,
        skills=new_candidate.skills
    )

def get_candidate_by_id(db: Session, candidate_id: UUID) -> model.CandidateResponse:
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
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

def get_candidates(db: Session, offset: int = 0, limit: int = 20, skill: str | None = None) -> list[model.CandidateResponse]:
    query = db.query(Candidate)
    if skill:
        query = query.filter(Candidate.skills.contains([skill]))
    candidates = query.offset(offset).limit(limit).all()
    logging.info(f"Retrieved {len(candidates)} candidates from the database.")
    return [
        model.CandidateResponse(
            id=c.id,
            email=c.email,
            full_name=c.full_name,
            phone=c.phone,
            skills=c.skills
        ) for c in candidates
    ]

def update_candidate(db: Session, candidate_id: UUID, candidate_data: model.CandidateUpdate) -> model.CandidateResponse:
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        logging.warning(f"Candidate not found with ID: {candidate_id}")
        raise CandidateNotFoundError(candidate_id)

    for key, value in candidate_data.dict(exclude_unset=True).items():
        setattr(candidate, key, value)

    db.commit()
    db.refresh(candidate)
    logging.info(f"Candidate updated with ID: {candidate.id}")
    return model.CandidateResponse(
        id=candidate.id,
        email=candidate.email,
        full_name=candidate.full_name,
        phone=candidate.phone,
        skills=candidate.skills
    )


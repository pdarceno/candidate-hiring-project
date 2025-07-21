from uuid import UUID
from sqlalchemy.orm import Session
from . import model
from ..entities.candidate import Candidate
from ..local_exceptions import CandidateNotFoundError, CandidateAlreadyExistsError
import logging

def create_candidate(db: Session, candidate: model.CandidateResponse) -> model.CandidateResponse:
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
    return new_candidate

def get_candidate_by_id(db: Session, candidate_id: UUID) -> model.CandidateResponse:
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        logging.warning(f"Candidate not found with ID: {candidate_id}")
        raise CandidateNotFoundError(candidate_id)
    logging.info(f"Successfully retrieved candidate with ID: {candidate_id}")
    return candidate

def get_candidates(db: Session, offset: int = 0, limit: int = 20) -> list[model.CandidateResponse]:
    candidates = db.query(Candidate).offset(offset).limit(limit).all()
    logging.info(f"Retrieved {len(candidates)} candidates from the database.")
    return candidates

def update_candidate(db: Session, candidate_id: UUID, candidate_data: model.CandidateResponse) -> model.CandidateResponse:
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        logging.warning(f"Candidate not found with ID: {candidate_id}")
        raise CandidateNotFoundError(candidate_id)

    for key, value in candidate_data.dict(exclude_unset=True).items():
        setattr(candidate, key, value)

    db.commit()
    db.refresh(candidate)
    logging.info(f"Candidate updated with ID: {candidate.id}")
    return candidate


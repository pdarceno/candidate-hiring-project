from fastapi import HTTPException

class AuthenticationError(HTTPException):
    def __init__(self, message: str = "Could not validate user"):
        super().__init__(status_code=401, detail=message)

class CandidateError(HTTPException):
    """Base exception for candidate-related errors"""
    pass

class CandidateNotFoundError(CandidateError):
    def __init__(self, candidate_id=None):
        message = "Candidate not found" if candidate_id is None else f"Candidate with id {candidate_id} not found"
        super().__init__(status_code=404, detail=message)

class CandidateAlreadyExistsError(CandidateError):
    def __init__(self, email: str):
        super().__init__(status_code=400, detail=f"Candidate with email {email} already exists")
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
    
class ApplicationError(HTTPException):
    """Base exception for application-related errors"""
    pass

class ApplicationNotFoundError(ApplicationError):
    def __init__(self, application_id=None):
        message = "Application not found" if application_id is None else f"Application with id {application_id} not found"
        super().__init__(status_code=404, detail=message)

class ApplicationAlreadyExistsError(ApplicationError):
    def __init__(self, candidate_id: str, job_id: str):
        super().__init__(status_code=400, detail=f"Application already exists for candidate {candidate_id} and job {job_id}")
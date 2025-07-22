import pytest
from uuid import uuid4
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from src.candidates.model import CandidateCreate, CandidateUpdate, CandidateResponse
from src.local_exceptions import CandidateNotFoundError, CandidateAlreadyExistsError
import logging

@pytest.mark.asyncio
async def test_get_single_candidate(async_client: AsyncClient, valid_token: str, single_candidate):
    """Test fetching a single candidate by ID."""
    candidate_id = single_candidate.id  # Get the candidate ID from the fixture
    headers = {"Authorization": f"Bearer {valid_token}"}

    response = await async_client.get(f"/candidates/{candidate_id}", headers=headers)
    logging.info(f"Response status: {response.status_code}")
    logging.info(f"Response: {response.json()}")

    assert response.status_code == 200
    candidate_response = CandidateResponse(**response.json())  # Use DTO for validation
    assert candidate_response.id == candidate_id

@pytest.mark.asyncio
async def test_get_paged_candidates(async_client: AsyncClient, valid_token: str, multiple_candidates):
    """Test fetching all candidates."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    response = await async_client.get("/candidates/?offset=0&limit=40", headers=headers)
    logging.info(f"Response test_get_paged_candidates status: {response.status_code}")
    logging.info(f"Response test_get_paged_candidates: {response.json()}")

    assert response.status_code == 200
    candidates = [CandidateResponse(**candidate) for candidate in response.json()]
    assert len(candidates) == 40

@pytest.mark.asyncio
async def test_get_all_candidates(async_client: AsyncClient, valid_token: str, multiple_candidates):
    """Test fetching all candidates."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    response = await async_client.get("/candidates/", headers=headers)
    logging.info(f"Response test_get_all_candidates status: {response.status_code}")
    logging.info(f"Response test_get_all_candidates: {response.json()}")

    assert response.status_code == 200
    candidates = [CandidateResponse(**candidate) for candidate in response.json()]  # Use DTO for validation
    assert len(candidates) == 20

@pytest.mark.asyncio
async def test_get_candidate_not_found(async_client: AsyncClient, valid_token):
    """Test fetching a non-existent candidate."""
    headers = {"Authorization": f"Bearer {valid_token}"}
    non_existent_id = uuid4()
    response = await async_client.get(f"/candidates/{non_existent_id}", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == CandidateNotFoundError(non_existent_id).detail

@pytest.mark.asyncio
async def test_create_candidate(async_client: AsyncClient, valid_token):
    """Test creating a new candidate."""
    headers = {"Authorization": f"Bearer {valid_token}"}
    candidate_data = CandidateCreate(
        full_name="John Doe",
        phone="1234567890",
        email="john.doe@example.com",
        skills=["Python", "FastAPI"]
    )
    response = await async_client.post("/candidates/", json=jsonable_encoder(candidate_data), headers=headers)
    assert response.status_code == 201
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_create_candidate_already_exists(async_client: AsyncClient, valid_token, single_candidate):
    """Test creating a candidate that already exists."""
    headers = {"Authorization": f"Bearer {valid_token}"}
    candidate_data = CandidateCreate(
        full_name=single_candidate.full_name,
        phone=single_candidate.phone,
        email=single_candidate.email,
        skills=single_candidate.skills
    )
    response = await async_client.post("/candidates/", json=jsonable_encoder(candidate_data), headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"] == CandidateAlreadyExistsError(single_candidate.email).detail


@pytest.mark.asyncio
async def test_create_candidate_missing_fields(async_client: AsyncClient, valid_token):
    """Test creating a candidate with missing fields."""
    headers = {"Authorization": f"Bearer {valid_token}"}
    candidate_data = CandidateCreate(
        full_name="John Doe",
        email="john.doe@example.com",
    )
    response = await async_client.post("/candidates/", json=jsonable_encoder(candidate_data), headers=headers)
    assert response.status_code == 201
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_update_candidate(async_client: AsyncClient, valid_token, multiple_candidates):
    """Test updating an existing candidate."""
    headers = {"Authorization": f"Bearer {valid_token}"}
    candidate_id = multiple_candidates[0].id
    candidate_update_data = CandidateUpdate(
        full_name="John Smith",
        email="john.smith@example.com",
        skills=["Python", "Django"]
    )
    response = await async_client.put(f"/candidates/{candidate_id}", json=jsonable_encoder(candidate_update_data), headers=headers)
    assert response.status_code == 200
    assert response.json()["full_name"] == "John Smith"

@pytest.mark.asyncio
async def test_update_candidate_not_found(async_client: AsyncClient, valid_token):
    """Test updating a non-existent candidate."""
    headers = {"Authorization": f"Bearer {valid_token}"}
    non_existent_id = uuid4()
    candidate_update_data = CandidateUpdate(
        full_name="John Smith",
        email="john.smith@example.com",
        skills=["Python", "Django"]
    )
    response = await async_client.put(f"/candidates/{non_existent_id}", json=jsonable_encoder(candidate_update_data), headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == CandidateNotFoundError(non_existent_id).detail
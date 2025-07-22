import pytest
from httpx import AsyncClient
import logging

@pytest.mark.asyncio
async def test_get_candidates(async_client: AsyncClient, valid_token: str, prepopulate_data):
    """Test fetching a candidate by ID."""
    
    headers = {"Authorization": f"Bearer {valid_token}"}
    
    response = await async_client.get("/candidates/", headers=headers)
    logging.info(f"Response testgetcandidates status: {response.status_code}")
    logging.info(f"Response testgetcandidates: {response.json()}")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

# @pytest.mark.asyncio
# async def test_get_candidate_not_found(async_client: AsyncClient, valid_token):
#     """Test fetching a non-existent candidate."""
#     headers = {"Authorization": f"Bearer {valid_token}"}
#     response = await async_client.get("/candidates/999", headers=headers)
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Candidate not found"

# @pytest.mark.asyncio
# async def test_create_candidate(async_client: AsyncClient, valid_token):
#     """Test creating a new candidate."""
#     headers = {"Authorization": f"Bearer {valid_token}"}
#     response = await async_client.post("/candidates", json={
#         "name": "John Doe",
#         "email": "john.doe@example.com",
#         "skills": ["Python", "FastAPI"]
#     }, headers=headers)
#     assert response.status_code == 201
#     assert "id" in response.json()

# @pytest.mark.asyncio
# async def test_create_candidate_missing_fields(async_client: AsyncClient, valid_token):
#     """Test creating a candidate with missing fields."""
#     headers = {"Authorization": f"Bearer {valid_token}"}
#     response = await async_client.post("/candidates", json={
#         "name": "John Doe"
#         # Missing email and skills
#     }, headers=headers)
#     assert response.status_code == 422

# @pytest.mark.asyncio
# async def test_update_candidate(async_client: AsyncClient, valid_token):
#     """Test updating an existing candidate."""
#     headers = {"Authorization": f"Bearer {valid_token}"}
#     response = await async_client.put("/candidates/1", json={
#         "name": "John Smith",
#         "email": "john.smith@example.com",
#         "skills": ["Python", "Django"]
#     }, headers=headers)
#     assert response.status_code == 200
#     assert response.json()["name"] == "John Smith"

# @pytest.mark.asyncio
# async def test_update_candidate_not_found(async_client: AsyncClient, valid_token):
#     """Test updating a non-existent candidate."""
#     headers = {"Authorization": f"Bearer {valid_token}"}
#     response = await async_client.put("/candidates/999", json={
#         "name": "Jane Doe",
#         "email": "jane.doe@example.com",
#         "skills": ["Java", "Spring"]
#     }, headers=headers)
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Candidate not found"

# @pytest.mark.asyncio
# async def test_delete_candidate(async_client: AsyncClient, valid_token):
#     """Test deleting a candidate by ID."""
#     headers = {"Authorization": f"Bearer {valid_token}"}
#     response = await async_client.delete("/candidates/1", headers=headers)
#     assert response.status_code == 204

# @pytest.mark.asyncio
# async def test_delete_candidate_not_found(async_client: AsyncClient, valid_token):
#     """Test deleting a non-existent candidate."""
#     headers = {"Authorization": f"Bearer {valid_token}"}
#     response = await async_client.delete("/candidates/999", headers=headers)
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Candidate not found"

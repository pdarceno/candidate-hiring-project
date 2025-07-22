import pytest
from fastapi.encoders import jsonable_encoder
from uuid import uuid4
from httpx import AsyncClient
from src.applications.model import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from src.local_exceptions import ApplicationNotFoundError, ApplicationAlreadyExistsError
from src.entities.application import ApplicationStatus
import logging

@pytest.mark.asyncio
async def test_get_single_application(async_client: AsyncClient, valid_token: str, single_application):
    """Test fetching a single application by candidate ID."""
    application_id = single_application.id  # Get the application ID from the fixture
    candidate_id = single_application.candidate_id  # Get the candidate ID from the fixture
    headers = {"Authorization": f"Bearer {valid_token}"}

    response = await async_client.get(f"/applications/candidate/{candidate_id}", headers=headers)
    logging.info(f"Response status: {response.status_code}")
    logging.info(f"Response: {response.json()}")

    assert response.status_code == 200
    applications = [ApplicationResponse(**application) for application in response.json()]
    assert len(applications) == 1
    assert applications[0].id == application_id
    assert applications[0].candidate_id == candidate_id

@pytest.mark.asyncio
async def test_get_multiple_applications(async_client: AsyncClient, valid_token: str, multiple_applications):
    """Test fetching all applications by candidate ID."""
    headers = {"Authorization": f"Bearer {valid_token}"}

    candidate_id = multiple_applications[0].candidate_id  # Use the first candidate ID

    response = await async_client.get(f"/applications/candidate/{candidate_id}", headers=headers)
    logging.info(f"Response testgetapplications status: {response.status_code}")
    logging.info(f"Response testgetapplications: {response.json()}")

    assert response.status_code == 200
    applications = [ApplicationResponse(**application) for application in response.json()]
    assert all(app.id in [app.id for app in applications] for app in multiple_applications)
    assert all(app.candidate_id == candidate_id for app in applications)
    assert len(applications) == len(multiple_applications)

@pytest.mark.asyncio
async def test_get_filtered_applications(async_client: AsyncClient, valid_token: str, single_candidate, multiple_applications):
    """Test fetching applications with a specific status."""
    headers = {"Authorization": f"Bearer {valid_token}"}
    candidate_id = single_candidate.id  # Use the single candidate ID

    response = await async_client.get(f"/applications/candidate/{candidate_id}?status={ApplicationStatus.APPLIED.value}", headers=headers)
    logging.info(f"Response status: {response.status_code}")
    logging.info(f"Response: {response.json()}")

    assert response.status_code == 200
    applications = [ApplicationResponse(**application) for application in response.json()]
    assert len(applications) == 100
    assert applications[0].candidate_id == candidate_id
    assert applications[0].status == ApplicationStatus.APPLIED

@pytest.mark.asyncio
async def test_create_application(async_client: AsyncClient, valid_token, single_candidate):
    """Test creating a new application."""
    headers = {"Authorization": f"Bearer {valid_token}"}
    application_data = ApplicationCreate(
        candidate_id=single_candidate.id,
        job_title="Software Engineer",
        status=ApplicationStatus.APPLIED
    )
    response = await async_client.post("/applications/", json=jsonable_encoder(application_data), headers=headers)
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["candidate_id"] == str(single_candidate.id)
    assert response.json()["job_title"] == "Software Engineer"
    assert response.json()["status"] == ApplicationStatus.APPLIED.value

@pytest.mark.asyncio
async def test_create_application_already_exists(async_client: AsyncClient, valid_token, single_application):
    """Test creating an application that already exists."""
    headers = {"Authorization": f"Bearer {valid_token}"}
    application_data = ApplicationCreate(
        candidate_id=single_application.candidate_id,
        job_title=single_application.job_title,
        status=single_application.status
    )
    response = await async_client.post("/applications/", json=jsonable_encoder(application_data), headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"] == ApplicationAlreadyExistsError(
        candidate_id=single_application.candidate_id,
        job_title=single_application.job_title
    ).detail
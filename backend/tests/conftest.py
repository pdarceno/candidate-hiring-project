import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database.core import get_db, Base
from src.entities.candidate import Candidate
from src.entities.application import Application, ApplicationStatus
from uuid import UUID, uuid4
import tempfile
import logging
import os


@pytest.fixture(scope="session")
def test_engine() -> create_async_engine:
    """Create a test database engine."""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db_path = temp_db.name
    temp_db.close()
    
    # Use async engine if your app uses async
    engine = create_async_engine(f"sqlite+aiosqlite:///{temp_db_path}", echo=True)
    
    yield engine
    
    engine.sync_engine.dispose()
    try:
        os.unlink(temp_db_path)
    except PermissionError:
        pass

@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh async database session for each test."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    TestingSessionLocal = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
def override_get_db(db_session) -> callable:
    """Override the get_db dependency to use test database."""
    async def _override_get_db():
        yield db_session
    
    return _override_get_db

@pytest_asyncio.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing FastAPI endpoints."""
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def valid_token(async_client: AsyncClient) -> str:
    """Fixture to retrieve a valid token."""
    response = await async_client.post("/auth/login", data={
        "username": "admin@example.com",
        "password": "admin"
    })
    
    token = response.json()["access_token"]
    return token

@pytest_asyncio.fixture
async def prepopulate_data(db_session):
    """Prepopulate the test database with a candidate and application."""
    # Create a candidate
    candidate = Candidate(id=uuid4(), full_name="Prosy Arceno", email="prosy.arceno@gmail.com", skills=["Python", "FastAPI"])
    db_session.add(candidate)

    logging.info(f"Prepopulated candidate: {candidate.full_name} with ID: {candidate.id}")

    # Create an application
    application = Application(id=uuid4(), candidate_id=candidate.id, job_title="Software Engineer", status=ApplicationStatus.APPLIED)
    db_session.add(application)

    logging.info(f"Prepopulated application for candidate ID: {application.candidate_id} with job title: {application.job_title}")

    await db_session.commit()
    yield
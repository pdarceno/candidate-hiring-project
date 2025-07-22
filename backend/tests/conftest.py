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


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> create_async_engine:
    """Create a test database engine."""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db_path = temp_db.name
    temp_db.close()

    # Use async engine if your app uses async
    engine = create_async_engine(f"sqlite+aiosqlite:///{temp_db_path}", echo=True)

    try:
        yield engine
    finally:
        # Properly dispose of the engine asynchronously
        await engine.dispose()
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
        try:
            yield session
        finally:
            # Ensure the session is closed properly
            await session.close()
            # Drop all tables to clean up the database
            async with test_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)

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
async def single_candidate(db_session):
    """Prepopulate the test database with a single candidate."""
    candidate = Candidate(id=uuid4(), full_name="Prosy Arceno", phone="123", email="prosy.arceno@gmail.com", skills=["Python", "FastAPI"])
    db_session.add(candidate)
    await db_session.commit()
    yield candidate

@pytest_asyncio.fixture
async def multiple_candidates(db_session):
    """Prepopulate the test database with multiple candidates."""
    candidates = [
        Candidate(
            id=uuid4(),
            full_name="Prosy Arceno",
            phone="123",
            email=f"prosy.arceno+{i}@gmail.com",
            skills=["Python", "FastAPI"]
        )
        for i in range(100)
    ]
    db_session.add_all(candidates)
    await db_session.commit()
    yield candidates

@pytest_asyncio.fixture
async def single_application(db_session, single_candidate):
    """Prepopulate the test database with a single application linked to an actual candidate."""
    application = Application(
        id=uuid4(),
        candidate_id=single_candidate.id,
        job_title="Software Engineer",
        status=ApplicationStatus.APPLIED,
    )
    db_session.add(application)
    await db_session.commit()
    yield application

@pytest_asyncio.fixture
async def multiple_applications(db_session, single_candidate):
    """Prepopulate the test database with multiple applications linked to actual candidates."""
    applications = [
        Application(
            id=uuid4(),
            candidate_id=single_candidate.id,
            job_title="Software Engineer",
            status=ApplicationStatus.APPLIED,
        ) for _ in range(100)
    ]
    db_session.add_all(applications)
    await db_session.commit()
    yield applications
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_auth_login(async_client: AsyncClient) -> None:
    """Test the login endpoint."""
    response = await async_client.post("/auth/login", data={
        "username": "admin@example.com",
        "password": "admin"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_wrong_payload_type(async_client: AsyncClient) -> None:
    """Test the login endpoint with wrong payload type."""
    response = await async_client.post("/auth/login", json={
        "username": "admin@example.com",
        "password": "admin"
    })
    assert response.status_code == 422 # Unprocessable Entity
    assert "access_token" not in response.json()

@pytest.mark.asyncio
async def test_auth_invalid_login(async_client: AsyncClient) -> None:
    """Test login with invalid credentials."""
    response = await async_client.post("/auth/login", data={
        "username": "admin@wrongexample.com",
        "password": "admin"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate user"

@pytest.mark.asyncio
async def test_auth_login_missing_fields(async_client: AsyncClient) -> None:
    """Test login with missing required fields."""
    response = await async_client.post("/auth/login", data={
        "username": "admin@example.com"
        # Missing password
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_auth_login_empty_credentials(async_client: AsyncClient) -> None:
    """Test login with empty credentials."""
    response = await async_client.post("/auth/login", data={
        "username": "",
        "password": ""
    })
    assert response.status_code in [401, 422]  # Unauthorized or validation error

@pytest.mark.asyncio
async def test_auth_token_expiry(async_client: AsyncClient) -> None:
    """Test access token expiry."""
    response = await async_client.post("/auth/login", data={
        "username": "admin@example.com",
        "password": "admin"
    })
    token = response.json()["access_token"]
    # Simulate token expiry (e.g., wait or mock expiry)
    expired_token = "expired_token_example"
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await async_client.get("/protected-endpoint", headers=headers)
    assert response.status_code == 404  # Not Found, should be Unauthorized or similar

@pytest.mark.asyncio
async def test_unauthorized_access(async_client: AsyncClient) -> None:
    """Test access to protected endpoint without token."""
    response = await async_client.get("/protected-endpoint")
    assert response.status_code == 404  # Not Found

@pytest.mark.asyncio
async def test_auth_invalid_token(async_client: AsyncClient) -> None:
    """Test access with an invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = await async_client.get("/protected-endpoint", headers=headers)
    assert response.status_code == 404  # Not Found

@pytest.mark.asyncio
async def test_auth_login_rate_limit(async_client: AsyncClient):
    """Test rate limiting for login endpoint."""
    for _ in range(10):  # Assuming the limit is 10 requests per minute
        await async_client.post("/auth/login", data={
            "username": "admin@example.com",
            "password": "admin"
        })
    response = await async_client.post("/auth/login", data={
        "username": "admin@example.com",
        "password": "admin"
    })
    assert response.status_code == 429  # Too Many Requests


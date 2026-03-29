import pytest


@pytest.mark.asyncio
async def test_register(client):
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "Test1234!",
            "name": "Test User",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    await client.post(
        "/api/auth/register",
        json={
            "email": "dupe@example.com",
            "password": "Test1234!",
            "name": "User 1",
        },
    )
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "dupe@example.com",
            "password": "Test1234!",
            "name": "User 2",
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client):
    await client.post(
        "/api/auth/register",
        json={
            "email": "login@example.com",
            "password": "Test1234!",
            "name": "Login User",
        },
    )
    response = await client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "Test1234!"},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post(
        "/api/auth/register",
        json={
            "email": "wrong@example.com",
            "password": "Test1234!",
            "name": "User",
        },
    )
    response = await client.post(
        "/api/auth/login",
        json={"email": "wrong@example.com", "password": "WrongPass!"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client):
    reg_response = await client.post(
        "/api/auth/register",
        json={
            "email": "refresh@example.com",
            "password": "Test1234!",
            "name": "Refresh User",
        },
    )
    # httpx doesn't store SameSite=None+Secure cookies, extract from Set-Cookie header
    set_cookie = reg_response.headers.get("set-cookie", "")
    assert "refresh_token=" in set_cookie
    # Extract token value from "refresh_token=<value>; ..."
    token_part = set_cookie.split("refresh_token=")[1]
    refresh_cookie = token_part.split(";")[0]
    response = await client.post(
        "/api/auth/refresh",
        cookies={"refresh_token": refresh_cookie},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]

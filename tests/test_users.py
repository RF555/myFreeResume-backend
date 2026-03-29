import pytest


@pytest.mark.asyncio
async def test_get_profile(client):
    reg = await client.post(
        "/api/auth/register",
        json={"email": "profile@example.com", "password": "Test1234!", "name": "Profile User"},
    )
    token = reg.json()["access_token"]
    response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "profile@example.com"
    assert data["name"] == "Profile User"


@pytest.mark.asyncio
async def test_update_profile(client):
    reg = await client.post(
        "/api/auth/register",
        json={"email": "update@example.com", "password": "Test1234!", "name": "Old Name"},
    )
    token = reg.json()["access_token"]
    response = await client.put(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "New Name"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"

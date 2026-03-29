import pytest


async def _register_and_get_token(client, email):
    reg = await client.post(
        "/api/auth/register",
        json={"email": email, "password": "Test1234!", "name": "Test"},
    )
    return reg.json()["access_token"]


@pytest.mark.asyncio
async def test_create_job_type(client):
    token = await _register_and_get_token(client, "jt1@example.com")
    response = await client.post(
        "/api/job-types",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Frontend Developer"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Frontend Developer"


@pytest.mark.asyncio
async def test_list_job_types(client):
    token = await _register_and_get_token(client, "jt2@example.com")
    await client.post(
        "/api/job-types",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Backend Developer"},
    )
    response = await client.get(
        "/api/job-types",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_update_job_type(client):
    token = await _register_and_get_token(client, "jt3@example.com")
    create_resp = await client.post(
        "/api/job-types",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Old Name"},
    )
    jt_id = create_resp.json()["id"]
    response = await client.put(
        f"/api/job-types/{jt_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "New Name"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_job_type(client):
    token = await _register_and_get_token(client, "jt4@example.com")
    create_resp = await client.post(
        "/api/job-types",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "To Delete"},
    )
    jt_id = create_resp.json()["id"]
    response = await client.delete(
        f"/api/job-types/{jt_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_cannot_access_other_users_job_type(client):
    token1 = await _register_and_get_token(client, "jt5a@example.com")
    token2 = await _register_and_get_token(client, "jt5b@example.com")
    create_resp = await client.post(
        "/api/job-types",
        headers={"Authorization": f"Bearer {token1}"},
        json={"name": "Private"},
    )
    jt_id = create_resp.json()["id"]
    response = await client.put(
        f"/api/job-types/{jt_id}",
        headers={"Authorization": f"Bearer {token2}"},
        json={"name": "Hacked"},
    )
    assert response.status_code == 404

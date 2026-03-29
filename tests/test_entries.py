import pytest


async def _setup(client, email):
    reg = await client.post(
        "/api/auth/register",
        json={"email": email, "password": "Test1234!", "name": "Test"},
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    jt = await client.post("/api/job-types", headers=headers, json={"name": "Frontend Dev"})
    return headers, jt.json()["id"]


@pytest.mark.asyncio
async def test_create_entry(client):
    headers, jt_id = await _setup(client, "entry1@example.com")
    response = await client.post(
        f"/api/job-types/{jt_id}/entries",
        headers=headers,
        json={"company_name": "Google"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["company_name"] == "Google"
    assert data["resume"]["name"] == ""
    assert data["cover_letter"]["addressee_name"] == ""


@pytest.mark.asyncio
async def test_update_entry(client):
    headers, jt_id = await _setup(client, "entry2@example.com")
    create_resp = await client.post(
        f"/api/job-types/{jt_id}/entries", headers=headers, json={"company_name": "Meta"},
    )
    entry_id = create_resp.json()["id"]
    response = await client.put(
        f"/api/entries/{entry_id}",
        headers=headers,
        json={
            "resume": {
                "name": "John Doe",
                "professional_title": "Frontend Developer",
                "summary": "Experienced developer",
                "contact": {"email": "john@example.com"},
                "skill_highlights": ["React", "TypeScript"],
            }
        },
    )
    assert response.status_code == 200
    assert response.json()["resume"]["name"] == "John Doe"
    assert response.json()["resume"]["skill_highlights"] == ["React", "TypeScript"]


@pytest.mark.asyncio
async def test_clone_entry_same_job_type(client):
    headers, jt_id = await _setup(client, "entry3@example.com")
    create_resp = await client.post(
        f"/api/job-types/{jt_id}/entries", headers=headers, json={"company_name": "Google"},
    )
    entry_id = create_resp.json()["id"]
    await client.put(
        f"/api/entries/{entry_id}",
        headers=headers,
        json={"resume": {"name": "Jane Doe", "skill_highlights": ["Python"]}},
    )
    response = await client.post(
        f"/api/entries/{entry_id}/clone",
        headers=headers,
        json={"job_type_id": jt_id, "company_name": "Meta"},
    )
    assert response.status_code == 201
    clone = response.json()
    assert clone["company_name"] == "Meta"
    assert clone["resume"]["name"] == "Jane Doe"
    assert clone["id"] != entry_id


@pytest.mark.asyncio
async def test_delete_entry(client):
    headers, jt_id = await _setup(client, "entry4@example.com")
    create_resp = await client.post(
        f"/api/job-types/{jt_id}/entries", headers=headers, json={"company_name": "Amazon"},
    )
    entry_id = create_resp.json()["id"]
    response = await client.delete(f"/api/entries/{entry_id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_entries(client):
    headers, jt_id = await _setup(client, "entry5@example.com")
    await client.post(
        f"/api/job-types/{jt_id}/entries", headers=headers, json={"company_name": "Co1"},
    )
    await client.post(
        f"/api/job-types/{jt_id}/entries", headers=headers, json={"company_name": "Co2"},
    )
    response = await client.get(f"/api/job-types/{jt_id}/entries", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2

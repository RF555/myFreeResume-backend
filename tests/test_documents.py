import pytest


async def _create_entry_with_data(client, email):
    reg = await client.post(
        "/api/auth/register",
        json={"email": email, "password": "Test1234!", "name": "Test"},
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    jt = await client.post("/api/job-types", headers=headers, json={"name": "Dev"})
    jt_id = jt.json()["id"]

    entry = await client.post(
        f"/api/job-types/{jt_id}/entries", headers=headers, json={"company_name": "TestCo"},
    )
    entry_id = entry.json()["id"]

    await client.put(
        f"/api/entries/{entry_id}",
        headers=headers,
        json={
            "resume": {
                "name": "John Doe",
                "professional_title": "Engineer",
                "contact": {"email": "john@example.com"},
                "skill_highlights": ["Python"],
            },
            "cover_letter": {
                "addressee_name": "HR Manager",
                "addressee_company": "TestCo",
                "body_paragraphs": ["I am interested in this position."],
                "closing": "Best regards",
            },
        },
    )
    return headers, entry_id


@pytest.mark.asyncio
async def test_download_resume(client):
    headers, entry_id = await _create_entry_with_data(client, "doc1@example.com")
    response = await client.get(
        f"/api/entries/{entry_id}/download/resume", headers=headers,
    )
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_download_cover_letter(client):
    headers, entry_id = await _create_entry_with_data(client, "doc2@example.com")
    response = await client.get(
        f"/api/entries/{entry_id}/download/cover-letter", headers=headers,
    )
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers["content-type"]

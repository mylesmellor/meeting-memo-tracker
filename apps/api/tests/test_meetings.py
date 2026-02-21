"""Integration tests for /api/v1/meetings/* endpoints."""
import pytest
from httpx import AsyncClient

BASE = "/api/v1/meetings"


@pytest.fixture
def meeting_payload() -> dict:
    # Use "home" category — "work" requires a team_id
    return {"title": "Team Standup", "category": "home", "tags": ["daily"]}


# ── create ───────────────────────────────────────────────────────────────────


async def test_create_meeting_success(auth_client: AsyncClient, meeting_payload: dict):
    response = await auth_client.post(f"{BASE}/", json=meeting_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Team Standup"
    assert data["category"] == "home"
    assert data["tags"] == ["daily"]
    assert data["status"] == "draft"


async def test_create_meeting_unauthenticated(client: AsyncClient, meeting_payload: dict):
    response = await client.post(f"{BASE}/", json=meeting_payload)
    assert response.status_code == 401


# ── list ─────────────────────────────────────────────────────────────────────


async def test_list_meetings_empty(auth_client: AsyncClient):
    response = await auth_client.get(f"{BASE}/")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["items"] == []


async def test_list_meetings_after_create(auth_client: AsyncClient, meeting_payload: dict):
    await auth_client.post(f"{BASE}/", json=meeting_payload)
    response = await auth_client.get(f"{BASE}/")
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Team Standup"


async def test_list_meetings_with_category_filter(auth_client: AsyncClient):
    await auth_client.post(f"{BASE}/", json={"title": "Home Meeting", "category": "home"})
    await auth_client.post(f"{BASE}/", json={"title": "Private Meeting", "category": "private"})

    response = await auth_client.get(f"{BASE}/?category=home")
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["category"] == "home"


async def test_list_meetings_search_query_returns_200(auth_client: AsyncClient, meeting_payload: dict):
    """Search endpoint should work (TSVECTOR populated on generate; empty = no results)."""
    await auth_client.post(f"{BASE}/", json=meeting_payload)
    response = await auth_client.get(f"{BASE}/?q=standup")
    assert response.status_code == 200


# ── get by id ────────────────────────────────────────────────────────────────


async def test_get_meeting_by_id(auth_client: AsyncClient, meeting_payload: dict):
    create_r = await auth_client.post(f"{BASE}/", json=meeting_payload)
    meeting_id = create_r.json()["id"]

    response = await auth_client.get(f"{BASE}/{meeting_id}")
    assert response.status_code == 200
    assert response.json()["id"] == meeting_id


async def test_get_meeting_404_for_nonexistent(auth_client: AsyncClient):
    response = await auth_client.get(f"{BASE}/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


async def test_get_meeting_404_for_other_org(client: AsyncClient, user_data: dict):
    """A meeting created by org A should not be visible to org B."""
    # Register org A and create a meeting
    await client.post("/api/v1/auth/register", json=user_data)
    create_r = await client.post(
        f"{BASE}/", json={"title": "Org A Meeting", "category": "home"}
    )
    meeting_id = create_r.json()["id"]

    # Register org B and try to fetch org A's meeting
    org_b_data = {
        "name": "Org B User",
        "email": "orgb@example.com",
        "password": "pass1234",
        "org_name": "Org B",
    }
    await client.post("/api/v1/auth/logout")
    await client.post("/api/v1/auth/register", json=org_b_data)
    response = await client.get(f"{BASE}/{meeting_id}")
    assert response.status_code == 404


# ── update ───────────────────────────────────────────────────────────────────


async def test_update_meeting_title(auth_client: AsyncClient, meeting_payload: dict):
    create_r = await auth_client.post(f"{BASE}/", json=meeting_payload)
    meeting_id = create_r.json()["id"]

    response = await auth_client.patch(f"{BASE}/{meeting_id}", json={"title": "Updated Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


async def test_update_meeting_tags(auth_client: AsyncClient, meeting_payload: dict):
    create_r = await auth_client.post(f"{BASE}/", json=meeting_payload)
    meeting_id = create_r.json()["id"]

    response = await auth_client.patch(f"{BASE}/{meeting_id}", json={"tags": ["updated", "tags"]})
    assert response.status_code == 200
    assert response.json()["tags"] == ["updated", "tags"]


# ── delete ───────────────────────────────────────────────────────────────────


async def test_delete_meeting(auth_client: AsyncClient, meeting_payload: dict):
    create_r = await auth_client.post(f"{BASE}/", json=meeting_payload)
    meeting_id = create_r.json()["id"]

    delete_r = await auth_client.delete(f"{BASE}/{meeting_id}")
    assert delete_r.status_code == 204

    get_r = await auth_client.get(f"{BASE}/{meeting_id}")
    assert get_r.status_code == 404


# ── transcript ───────────────────────────────────────────────────────────────


async def test_paste_transcript_text(auth_client: AsyncClient, meeting_payload: dict):
    create_r = await auth_client.post(f"{BASE}/", json=meeting_payload)
    meeting_id = create_r.json()["id"]

    response = await auth_client.post(
        f"{BASE}/{meeting_id}/transcript",
        json={"text": "Alice: Let's review the sprint goals. Bob: Agreed."},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Transcript saved"


async def test_paste_transcript_stores_text(auth_client: AsyncClient, meeting_payload: dict):
    create_r = await auth_client.post(f"{BASE}/", json=meeting_payload)
    meeting_id = create_r.json()["id"]

    transcript = "Meeting transcript content here."
    await auth_client.post(
        f"{BASE}/{meeting_id}/transcript",
        json={"text": transcript},
    )

    get_r = await auth_client.get(f"{BASE}/{meeting_id}")
    assert get_r.json()["transcript_text"] == transcript

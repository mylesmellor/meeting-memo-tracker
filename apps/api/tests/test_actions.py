"""Integration tests for /api/v1/actions/* endpoints."""
from datetime import date, timedelta

import pytest
from httpx import AsyncClient

BASE_ACTIONS = "/api/v1/actions"
BASE_MEETINGS = "/api/v1/meetings"


@pytest.fixture
async def meeting_id(auth_client: AsyncClient) -> str:
    """Create a meeting and return its ID."""
    response = await auth_client.post(
        f"{BASE_MEETINGS}/",
        json={"title": "Action Test Meeting", "category": "home"},
    )
    assert response.status_code == 200
    return response.json()["id"]


# ── create ───────────────────────────────────────────────────────────────────


async def test_create_action_success(auth_client: AsyncClient, meeting_id: str):
    response = await auth_client.post(
        f"{BASE_ACTIONS}/",
        json={"meeting_id": meeting_id, "description": "Write unit tests", "owner_text": "Alice"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Write unit tests"
    assert data["owner_text"] == "Alice"
    assert data["status"] == "todo"
    assert data["priority"] == "medium"


async def test_create_action_missing_meeting_returns_404(auth_client: AsyncClient):
    response = await auth_client.post(
        f"{BASE_ACTIONS}/",
        json={
            "meeting_id": "00000000-0000-0000-0000-000000000000",
            "description": "Orphan action",
        },
    )
    assert response.status_code == 404


# ── list ─────────────────────────────────────────────────────────────────────


async def test_list_actions_empty(auth_client: AsyncClient):
    response = await auth_client.get(f"{BASE_ACTIONS}/")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["items"] == []


async def test_list_actions_after_create(auth_client: AsyncClient, meeting_id: str):
    await auth_client.post(
        f"{BASE_ACTIONS}/",
        json={"meeting_id": meeting_id, "description": "Listed action"},
    )
    response = await auth_client.get(f"{BASE_ACTIONS}/")
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["description"] == "Listed action"


# ── get by id ────────────────────────────────────────────────────────────────


async def test_get_action_by_id(auth_client: AsyncClient, meeting_id: str):
    create_r = await auth_client.post(
        f"{BASE_ACTIONS}/",
        json={"meeting_id": meeting_id, "description": "Fetch me"},
    )
    action_id = create_r.json()["id"]

    response = await auth_client.get(f"{BASE_ACTIONS}/{action_id}")
    assert response.status_code == 200
    assert response.json()["id"] == action_id


async def test_get_action_404_nonexistent(auth_client: AsyncClient):
    response = await auth_client.get(f"{BASE_ACTIONS}/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


# ── patch status ─────────────────────────────────────────────────────────────


async def test_patch_action_status(auth_client: AsyncClient, meeting_id: str):
    create_r = await auth_client.post(
        f"{BASE_ACTIONS}/",
        json={"meeting_id": meeting_id, "description": "In progress task"},
    )
    action_id = create_r.json()["id"]

    response = await auth_client.patch(f"{BASE_ACTIONS}/{action_id}", json={"status": "doing"})
    assert response.status_code == 200
    assert response.json()["status"] == "doing"


async def test_patch_action_to_done(auth_client: AsyncClient, meeting_id: str):
    create_r = await auth_client.post(
        f"{BASE_ACTIONS}/",
        json={"meeting_id": meeting_id, "description": "Finish me"},
    )
    action_id = create_r.json()["id"]

    response = await auth_client.patch(f"{BASE_ACTIONS}/{action_id}", json={"status": "done"})
    assert response.status_code == 200
    assert response.json()["status"] == "done"


# ── delete ───────────────────────────────────────────────────────────────────


async def test_delete_action(auth_client: AsyncClient, meeting_id: str):
    create_r = await auth_client.post(
        f"{BASE_ACTIONS}/",
        json={"meeting_id": meeting_id, "description": "Delete me"},
    )
    action_id = create_r.json()["id"]

    delete_r = await auth_client.delete(f"{BASE_ACTIONS}/{action_id}")
    assert delete_r.status_code == 204

    get_r = await auth_client.get(f"{BASE_ACTIONS}/{action_id}")
    assert get_r.status_code == 404


# ── filters ──────────────────────────────────────────────────────────────────


async def test_filter_overdue_actions(auth_client: AsyncClient, meeting_id: str):
    past_date = (date.today() - timedelta(days=1)).isoformat()
    future_date = (date.today() + timedelta(days=5)).isoformat()

    await auth_client.post(
        f"{BASE_ACTIONS}/",
        json={"meeting_id": meeting_id, "description": "Overdue task", "due_date": past_date},
    )
    await auth_client.post(
        f"{BASE_ACTIONS}/",
        json={"meeting_id": meeting_id, "description": "Future task", "due_date": future_date},
    )

    response = await auth_client.get(f"{BASE_ACTIONS}/?overdue=true")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["description"] == "Overdue task"


async def test_overdue_filter_excludes_done_actions(auth_client: AsyncClient, meeting_id: str):
    """Completed actions should not appear in the overdue list."""
    past_date = (date.today() - timedelta(days=2)).isoformat()
    create_r = await auth_client.post(
        f"{BASE_ACTIONS}/",
        json={"meeting_id": meeting_id, "description": "Done overdue", "due_date": past_date},
    )
    action_id = create_r.json()["id"]
    await auth_client.patch(f"{BASE_ACTIONS}/{action_id}", json={"status": "done"})

    response = await auth_client.get(f"{BASE_ACTIONS}/?overdue=true")
    assert response.json()["total"] == 0


async def test_filter_due_this_week(auth_client: AsyncClient, meeting_id: str):
    soon_date = (date.today() + timedelta(days=3)).isoformat()
    far_date = (date.today() + timedelta(days=14)).isoformat()

    await auth_client.post(
        f"{BASE_ACTIONS}/",
        json={"meeting_id": meeting_id, "description": "Due soon", "due_date": soon_date},
    )
    await auth_client.post(
        f"{BASE_ACTIONS}/",
        json={"meeting_id": meeting_id, "description": "Due later", "due_date": far_date},
    )

    response = await auth_client.get(f"{BASE_ACTIONS}/?due_this_week=true")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["description"] == "Due soon"


async def test_filter_by_status(auth_client: AsyncClient, meeting_id: str):
    create_r = await auth_client.post(
        f"{BASE_ACTIONS}/",
        json={"meeting_id": meeting_id, "description": "Blocked task"},
    )
    action_id = create_r.json()["id"]
    await auth_client.patch(f"{BASE_ACTIONS}/{action_id}", json={"status": "blocked"})

    # Should appear in blocked filter
    blocked_r = await auth_client.get(f"{BASE_ACTIONS}/?status=blocked")
    assert blocked_r.json()["total"] == 1

    # Should not appear in todo filter
    todo_r = await auth_client.get(f"{BASE_ACTIONS}/?status=todo")
    assert todo_r.json()["total"] == 0

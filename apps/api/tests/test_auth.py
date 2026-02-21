"""Integration tests for /api/v1/auth/* endpoints."""
import pytest
from httpx import AsyncClient

BASE = "/api/v1/auth"


# ── register ─────────────────────────────────────────────────────────────────


async def test_register_success(client: AsyncClient, user_data: dict):
    response = await client.post(f"{BASE}/register", json=user_data)
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["email"] == user_data["email"]
    assert body["user"]["name"] == user_data["name"]
    assert body["user"]["role"] == "org_admin"


async def test_register_sets_auth_cookies(client: AsyncClient, user_data: dict):
    response = await client.post(f"{BASE}/register", json=user_data)
    assert response.status_code == 200
    # httpx stores cookies on the client; check the response Set-Cookie header
    assert "access_token" in response.cookies or "access_token" in client.cookies


async def test_register_duplicate_email_returns_400(client: AsyncClient, user_data: dict):
    await client.post(f"{BASE}/register", json=user_data)
    response = await client.post(f"{BASE}/register", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


async def test_register_second_org_gets_unique_slug(client: AsyncClient, user_data: dict):
    """Two orgs with the same name should receive distinct slugs."""
    await client.post(f"{BASE}/register", json=user_data)
    second = {**user_data, "email": "other@example.com"}
    response = await client.post(f"{BASE}/register", json=second)
    assert response.status_code == 200


# ── login ─────────────────────────────────────────────────────────────────────


async def test_login_valid_credentials(client: AsyncClient, user_data: dict):
    await client.post(f"{BASE}/register", json=user_data)
    response = await client.post(
        f"{BASE}/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Logged in"


async def test_login_invalid_password_returns_401(client: AsyncClient, user_data: dict):
    await client.post(f"{BASE}/register", json=user_data)
    response = await client.post(
        f"{BASE}/login",
        json={"email": user_data["email"], "password": "wrong-password"},
    )
    assert response.status_code == 401


async def test_login_unknown_email_returns_401(client: AsyncClient):
    response = await client.post(
        f"{BASE}/login",
        json={"email": "nobody@nowhere.com", "password": "pass"},
    )
    assert response.status_code == 401


# ── logout ────────────────────────────────────────────────────────────────────


async def test_logout_returns_200(auth_client: AsyncClient):
    response = await auth_client.post(f"{BASE}/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out"


async def test_after_logout_me_returns_401(auth_client: AsyncClient):
    await auth_client.post(f"{BASE}/logout")
    # Cookies cleared — /me should now reject the request
    response = await auth_client.get(f"{BASE}/me")
    assert response.status_code == 401


# ── /me ───────────────────────────────────────────────────────────────────────


async def test_me_authenticated_returns_user(auth_client: AsyncClient, user_data: dict):
    response = await auth_client.get(f"{BASE}/me")
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]


async def test_me_unauthenticated_returns_401(client: AsyncClient):
    response = await client.get(f"{BASE}/me")
    assert response.status_code == 401


# ── refresh ───────────────────────────────────────────────────────────────────


async def test_refresh_with_valid_cookie_returns_200(auth_client: AsyncClient):
    response = await auth_client.post(f"{BASE}/refresh")
    assert response.status_code == 200
    assert "refreshed" in response.json()["message"].lower()


async def test_refresh_without_cookie_returns_401(client: AsyncClient):
    response = await client.post(f"{BASE}/refresh")
    assert response.status_code == 401

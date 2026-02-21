"""
Test configuration and shared fixtures.

Prerequisites
-------------
The test database must exist before running tests:

    docker compose -f infra/docker-compose.yml exec db \
        psql -U appuser -c "CREATE DATABASE meetingmemo_test;"

Run tests inside the API container (recommended):

    docker compose -f infra/docker-compose.yml exec api python -m pytest tests/ -v

Or locally with PYTHONPATH set:

    cd apps/api
    TEST_DATABASE_URL=postgresql+asyncpg://appuser:apppassword@localhost:5432/meetingmemo_test \
        python -m pytest tests/ -v
"""
import os
from typing import AsyncGenerator

# ---------------------------------------------------------------------------
# Set env vars *before* any app module is imported so that pydantic-settings
# picks them up when it instantiates `Settings` at import time.
# ---------------------------------------------------------------------------
_test_db_url = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://appuser:apppassword@localhost:5432/meetingmemo_test",
)
os.environ.setdefault("DATABASE_URL", _test_db_url)
os.environ.setdefault(
    "DATABASE_URL_SYNC",
    _test_db_url.replace("+asyncpg", "+psycopg2"),
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-do-not-use-in-production")
os.environ.setdefault("OPENAI_API_KEY", "test-key-not-real")

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.deps import get_db
from app.db.base import Base
from app.main import app

TEST_DB_URL: str = os.environ["DATABASE_URL"]


# ---------------------------------------------------------------------------
# Session-scoped engine — tables created once per pytest session
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
async def engine():
    """Create test engine; drop + recreate all tables for a clean slate."""
    test_engine = create_async_engine(TEST_DB_URL, echo=False, pool_pre_ping=True)
    async with test_engine.begin() as conn:
        # Drop everything left from a previous run, then rebuild.
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


# ---------------------------------------------------------------------------
# Function-scoped session — each test gets its own DB session
# ---------------------------------------------------------------------------


@pytest.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Function-scoped DB session.  Cleanup runs in teardown so only tests that
    actually use DB fixtures trigger a connection (pure unit tests stay fast).
    """
    TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with TestSession() as s:
        yield s
    # Wipe all data written during this test (CASCADE handles child tables)
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE organisations CASCADE"))


# ---------------------------------------------------------------------------
# HTTP client — overrides get_db with the test session
# ---------------------------------------------------------------------------


@pytest.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Shared user helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def user_data() -> dict:
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpass123",
        "org_name": "Test Org",
    }


@pytest.fixture
async def registered_user(client: AsyncClient, user_data: dict):
    """Register a user and return (client, user_data). Cookies are set on client."""
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200, response.text
    return client, user_data


@pytest.fixture
async def auth_client(registered_user) -> AsyncClient:
    """Return an AsyncClient that is already authenticated."""
    client, _ = registered_user
    return client

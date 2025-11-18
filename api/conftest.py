"""Pytest configuration and fixtures for the Betzenstein Booking API."""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app


# Use test database (same credentials as dev database from Docker Compose)
TEST_DATABASE_URL = "postgresql+asyncpg://betzenstein:dev_password@localhost:5432/btznstn_test"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a transactional database session for tests.

    Each test gets a fresh session that rolls back at the end,
    ensuring test isolation.
    """
    # Create test engine
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Provide session to test
    async with async_session() as session:
        # Override the dependency
        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db

        yield session

        # Rollback any uncommitted changes
        await session.rollback()

        # Clean up override
        app.dependency_overrides.clear()

    # Dispose engine
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async HTTP client for API testing.

    Depends on db_session to ensure the dependency override is active.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

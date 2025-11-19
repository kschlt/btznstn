"""Pytest configuration and fixtures for the Betzenstein Booking API."""

import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app


# Test database URL - supports both local dev and CI environments
# CI uses DATABASE_URL env var (set in GitHub Actions)
# Local dev uses default Docker Compose credentials
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://betzenstein:dev_password@localhost:5432/btznstn_test",
)


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


# ============================================================================
# Scenario Fixtures
# ============================================================================
# These fixtures provide pre-created test data for common scenarios.
# Use these instead of manually creating bookings + approvals in every test.


@pytest_asyncio.fixture
async def booking_with_approvals(db_session: AsyncSession):
    """
    Create a Pending booking with 3 NoResponse approvals.

    This is the default state after creating a booking (BR-003).
    All 3 approvers have NoResponse decision.

    Returns:
        Booking instance with approvals and timeline events loaded

    Example:
        >>> async def test_something(booking_with_approvals, client):
        ...     response = await client.get(f"/api/v1/bookings/{booking_with_approvals.id}")
        ...     assert response.status_code == 200
    """
    from tests.fixtures.factories import make_booking, make_approval, make_timeline_event
    from app.models.enums import AffiliationEnum, DecisionEnum

    # Create booking
    booking = make_booking()
    db_session.add(booking)
    await db_session.flush()  # Get booking.id

    # Create 3 NoResponse approvals (BR-003)
    approvals = [
        make_approval(booking_id=booking.id, party=AffiliationEnum.INGEBORG),
        make_approval(booking_id=booking.id, party=AffiliationEnum.CORNELIA),
        make_approval(booking_id=booking.id, party=AffiliationEnum.ANGELIKA),
    ]
    db_session.add_all(approvals)

    # Create timeline event
    timeline_event = make_timeline_event(
        booking_id=booking.id,
        when=booking.created_at,
        actor=booking.requester_first_name,
        event_type="Created",
    )
    db_session.add(timeline_event)

    await db_session.commit()
    await db_session.refresh(booking)

    return booking


@pytest_asyncio.fixture
async def confirmed_booking(db_session: AsyncSession):
    """
    Create a Confirmed booking with all 3 approvals approved.

    This represents a booking that has been fully approved by all parties.

    Returns:
        Booking instance with status=Confirmed and all approvals approved

    Example:
        >>> async def test_confirmed_booking(confirmed_booking, client):
        ...     # Booking already confirmed
        ...     assert confirmed_booking.status == StatusEnum.CONFIRMED
    """
    from tests.fixtures.factories import make_booking, make_approval, make_timeline_event, get_now
    from app.models.enums import AffiliationEnum, DecisionEnum, StatusEnum

    now = get_now()

    # Create Confirmed booking
    booking = make_booking(status=StatusEnum.CONFIRMED)
    db_session.add(booking)
    await db_session.flush()

    # Create 3 Approved approvals
    approvals = [
        make_approval(
            booking_id=booking.id,
            party=party,
            decision=DecisionEnum.APPROVED,
            decided_at=now,
        )
        for party in [
            AffiliationEnum.INGEBORG,
            AffiliationEnum.CORNELIA,
            AffiliationEnum.ANGELIKA,
        ]
    ]
    db_session.add_all(approvals)

    # Create timeline events
    created_event = make_timeline_event(
        booking_id=booking.id,
        when=booking.created_at,
        actor=booking.requester_first_name,
        event_type="Created",
    )
    db_session.add(created_event)

    # Add approval events
    for party in [AffiliationEnum.INGEBORG, AffiliationEnum.CORNELIA, AffiliationEnum.ANGELIKA]:
        approval_event = make_timeline_event(
            booking_id=booking.id,
            when=now,
            actor=party.value,
            event_type="Approved",
            note=f"{party.value} party",
        )
        db_session.add(approval_event)

    await db_session.commit()
    await db_session.refresh(booking)

    return booking


@pytest_asyncio.fixture
async def denied_booking(db_session: AsyncSession):
    """
    Create a Denied booking with at least one denial.

    This represents a booking that was denied by at least one approver (BR-004).

    Returns:
        Booking instance with status=Denied

    Example:
        >>> async def test_denied_not_public(denied_booking, client):
        ...     # Denied booking returns 404 without token
        ...     response = await client.get(f"/api/v1/bookings/{denied_booking.id}")
        ...     assert response.status_code == 404
    """
    from tests.fixtures.factories import make_booking, make_approval, make_timeline_event, get_now
    from app.models.enums import AffiliationEnum, DecisionEnum, StatusEnum

    now = get_now()

    # Create Denied booking
    booking = make_booking(status=StatusEnum.DENIED)
    db_session.add(booking)
    await db_session.flush()

    # Create approvals: 1 Denied, 2 NoResponse
    approvals = [
        make_approval(
            booking_id=booking.id,
            party=AffiliationEnum.INGEBORG,
            decision=DecisionEnum.DENIED,
            decided_at=now,
            comment="Cannot accommodate this request",
        ),
        make_approval(
            booking_id=booking.id,
            party=AffiliationEnum.CORNELIA,
            decision=DecisionEnum.NO_RESPONSE,
        ),
        make_approval(
            booking_id=booking.id,
            party=AffiliationEnum.ANGELIKA,
            decision=DecisionEnum.NO_RESPONSE,
        ),
    ]
    db_session.add_all(approvals)

    # Create timeline events
    created_event = make_timeline_event(
        booking_id=booking.id,
        when=booking.created_at,
        actor=booking.requester_first_name,
        event_type="Created",
    )
    db_session.add(created_event)

    denied_event = make_timeline_event(
        booking_id=booking.id,
        when=now,
        actor="Ingeborg",
        event_type="Denied",
        note="Ingeborg party",
    )
    db_session.add(denied_event)

    await db_session.commit()
    await db_session.refresh(booking)

    return booking

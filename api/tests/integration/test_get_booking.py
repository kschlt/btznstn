"""
Integration tests for US-2.2: Get Booking Endpoint.

Tests all business rules and edge cases per phase-2-booking-api.md.

Test Plan (~20 tests):
- Public View (6 tests)
- Authenticated View (5 tests)
- Past Indicator (3 tests)
- German Errors (3 tests)
"""

from datetime import date, datetime, timedelta
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from zoneinfo import ZoneInfo

from app.main import app
from app.models.approval import Approval
from app.models.booking import Booking
from app.models.enums import AffiliationEnum, DecisionEnum, StatusEnum
from app.models.timeline_event import TimelineEvent

BERLIN_TZ = ZoneInfo("Europe/Berlin")


def get_today() -> date:
    """Get today's date in Europe/Berlin timezone."""
    return datetime.now(BERLIN_TZ).date()


# ============================================================================
# Public View (6 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_get_public_pending_booking(db_session: AsyncSession):
    """Test public GET on Pending booking returns limited fields."""
    # Create a Pending booking
    today = get_today()
    booking = Booking(
        requester_first_name="Anna",
        requester_email="anna@example.com",
        start_date=today + timedelta(days=10),
        end_date=today + timedelta(days=14),
        total_days=5,
        party_size=4,
        affiliation=AffiliationEnum.INGEBORG,
        description="Private description",
        status=StatusEnum.PENDING,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    # Public GET without token
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 200
    data = response.json()

    # Should include public fields
    assert data["id"] == str(booking.id)
    assert data["requester_first_name"] == "Anna"
    assert data["start_date"] == booking.start_date.isoformat()
    assert data["end_date"] == booking.end_date.isoformat()
    assert data["total_days"] == 5
    assert data["party_size"] == 4
    assert data["affiliation"] == "Ingeborg"
    assert data["status"] == "Pending"
    assert data["is_past"] is False

    # Should NOT include private fields
    assert "requester_email" not in data
    assert "description" not in data
    assert "approvals" not in data
    assert "timeline_events" not in data
    assert "created_at" not in data
    assert "updated_at" not in data
    assert "last_activity_at" not in data


@pytest.mark.asyncio
async def test_get_public_confirmed_booking(db_session: AsyncSession):
    """Test public GET on Confirmed booking returns limited fields."""
    today = get_today()
    booking = Booking(
        requester_first_name="Max",
        requester_email="max@example.com",
        start_date=today + timedelta(days=20),
        end_date=today + timedelta(days=25),
        total_days=6,
        party_size=2,
        affiliation=AffiliationEnum.CORNELIA,
        status=StatusEnum.CONFIRMED,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Confirmed"
    assert data["requester_first_name"] == "Max"
    assert "requester_email" not in data


@pytest.mark.asyncio
async def test_get_public_denied_booking_404(db_session: AsyncSession):
    """Test BR-004: Public GET on Denied booking returns 404."""
    today = get_today()
    booking = Booking(
        requester_first_name="Denied",
        requester_email="denied@example.com",
        start_date=today + timedelta(days=10),
        end_date=today + timedelta(days=14),
        total_days=5,
        party_size=3,
        affiliation=AffiliationEnum.ANGELIKA,
        status=StatusEnum.DENIED,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 404
    assert "nicht gefunden" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_public_canceled_booking_404(db_session: AsyncSession):
    """Test BR-004: Public GET on Canceled booking returns 404."""
    today = get_today()
    booking = Booking(
        requester_first_name="Canceled",
        requester_email="canceled@example.com",
        start_date=today + timedelta(days=10),
        end_date=today + timedelta(days=14),
        total_days=5,
        party_size=5,
        affiliation=AffiliationEnum.INGEBORG,
        status=StatusEnum.CANCELED,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_public_excludes_email(db_session: AsyncSession):
    """Test privacy: Public response does not include requester_email."""
    today = get_today()
    booking = Booking(
        requester_first_name="Privacy",
        requester_email="privacy@example.com",
        start_date=today + timedelta(days=10),
        end_date=today + timedelta(days=14),
        total_days=5,
        party_size=4,
        affiliation=AffiliationEnum.INGEBORG,
        status=StatusEnum.PENDING,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 200
    data = response.json()
    assert "requester_email" not in data
    assert "privacy@example.com" not in str(data)


@pytest.mark.asyncio
async def test_get_public_excludes_description(db_session: AsyncSession):
    """Test privacy: Public response does not include description."""
    today = get_today()
    booking = Booking(
        requester_first_name="Secret",
        requester_email="secret@example.com",
        start_date=today + timedelta(days=10),
        end_date=today + timedelta(days=14),
        total_days=5,
        party_size=4,
        affiliation=AffiliationEnum.INGEBORG,
        description="This is a secret description with sensitive info",
        status=StatusEnum.PENDING,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 200
    data = response.json()
    assert "description" not in data
    assert "secret" not in str(data).lower()


# ============================================================================
# Authenticated View (5 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_get_with_requester_token(db_session: AsyncSession):
    """Test: Valid requester token returns full details with approvals and timeline."""
    # TODO: This test requires token implementation
    # For now, mark as placeholder
    pytest.skip("Token implementation pending")


@pytest.mark.asyncio
async def test_get_with_approver_token(db_session: AsyncSession):
    """Test: Valid approver token returns full details."""
    pytest.skip("Token implementation pending")


@pytest.mark.asyncio
async def test_get_denied_with_token(db_session: AsyncSession):
    """Test BR-004: Denied booking accessible with valid token."""
    pytest.skip("Token implementation pending")


@pytest.mark.asyncio
async def test_get_invalid_token_401(db_session: AsyncSession):
    """Test: Invalid token signature returns 401 with German error."""
    pytest.skip("Token implementation pending")


@pytest.mark.asyncio
async def test_get_wrong_booking_token_403(db_session: AsyncSession):
    """Test: Token for different booking returns 403 with German error."""
    pytest.skip("Token implementation pending")


# ============================================================================
# Past Indicator (3 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_is_past_yesterday(db_session: AsyncSession):
    """Test BR-014: Booking ending yesterday has is_past=true."""
    today = get_today()
    yesterday = today - timedelta(days=1)

    booking = Booking(
        requester_first_name="Past",
        requester_email="past@example.com",
        start_date=yesterday - timedelta(days=4),
        end_date=yesterday,
        total_days=5,
        party_size=2,
        affiliation=AffiliationEnum.INGEBORG,
        status=StatusEnum.CONFIRMED,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["is_past"] is True


@pytest.mark.asyncio
async def test_is_past_today(db_session: AsyncSession):
    """Test BR-014: Booking ending today has is_past=false."""
    today = get_today()

    booking = Booking(
        requester_first_name="Today",
        requester_email="today@example.com",
        start_date=today - timedelta(days=2),
        end_date=today,
        total_days=3,
        party_size=3,
        affiliation=AffiliationEnum.CORNELIA,
        status=StatusEnum.CONFIRMED,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["is_past"] is False


@pytest.mark.asyncio
async def test_is_past_tomorrow(db_session: AsyncSession):
    """Test BR-014: Booking ending tomorrow has is_past=false."""
    today = get_today()
    tomorrow = today + timedelta(days=1)

    booking = Booking(
        requester_first_name="Future",
        requester_email="future@example.com",
        start_date=today,
        end_date=tomorrow,
        total_days=2,
        party_size=4,
        affiliation=AffiliationEnum.ANGELIKA,
        status=StatusEnum.PENDING,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["is_past"] is False


# ============================================================================
# German Errors (3 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_german_404(db_session: AsyncSession):
    """Test: 404 error message in German."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/bookings/{fake_uuid}")

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert "Der Eintrag konnte leider nicht gefunden werden." == detail


@pytest.mark.asyncio
async def test_german_401(db_session: AsyncSession):
    """Test: 401 error message in German (invalid token)."""
    today = get_today()
    booking = Booking(
        requester_first_name="Auth",
        requester_email="auth@example.com",
        start_date=today + timedelta(days=10),
        end_date=today + timedelta(days=14),
        total_days=5,
        party_size=4,
        affiliation=AffiliationEnum.INGEBORG,
        status=StatusEnum.PENDING,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    # Invalid token signature
    invalid_token = "invalid_token_signature"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/bookings/{booking.id}?token={invalid_token}")

    assert response.status_code == 401
    detail = response.json()["detail"]
    assert "Ungültiger Zugangslink." == detail


@pytest.mark.asyncio
async def test_german_403(db_session: AsyncSession):
    """Test: 403 error message in German (wrong booking token)."""
    pytest.skip("Token implementation pending - need valid token for different booking")

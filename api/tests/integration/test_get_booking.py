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
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from zoneinfo import ZoneInfo

from app.core.tokens import generate_token
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
async def test_get_public_pending_booking(db_session: AsyncSession, client: AsyncClient):
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
async def test_get_public_confirmed_booking(db_session: AsyncSession, client: AsyncClient):
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

    response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Confirmed"
    assert data["requester_first_name"] == "Max"
    assert "requester_email" not in data


@pytest.mark.asyncio
async def test_get_public_denied_booking_404(db_session: AsyncSession, client: AsyncClient):
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

    response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 404
    assert "nicht gefunden" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_public_canceled_booking_404(db_session: AsyncSession, client: AsyncClient):
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

    response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_public_excludes_email(db_session: AsyncSession, client: AsyncClient):
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

    response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 200
    data = response.json()
    assert "requester_email" not in data
    assert "privacy@example.com" not in str(data)


@pytest.mark.asyncio
async def test_get_public_excludes_description(db_session: AsyncSession, client: AsyncClient):
    """Test privacy: Public response does not include description."""
    today = get_today()
    booking = Booking(
        requester_first_name="TestUser",
        requester_email="test@example.com",
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

    response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 200
    data = response.json()
    assert "description" not in data
    # Ensure the actual description text is not leaked
    assert "secret description with sensitive info" not in str(data).lower()


# ============================================================================
# Authenticated View (5 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_get_with_requester_token(db_session: AsyncSession, client: AsyncClient):
    """Test: Valid requester token returns full details with approvals and timeline."""
    today = get_today()

    # Create booking with approvals and timeline
    booking = Booking(
        requester_first_name="TokenUser",
        requester_email="token@example.com",
        start_date=today + timedelta(days=10),
        end_date=today + timedelta(days=14),
        total_days=5,
        party_size=4,
        affiliation=AffiliationEnum.INGEBORG,
        description="Secret details",
        status=StatusEnum.PENDING,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    # Create approvals
    for party in [AffiliationEnum.INGEBORG, AffiliationEnum.CORNELIA, AffiliationEnum.ANGELIKA]:
        approval = Approval(
            booking_id=booking.id,
            party=party,
            decision=DecisionEnum.NO_RESPONSE,
            decided_at=None,
            comment=None,
        )
        db_session.add(approval)

    # Create timeline event
    timeline_event = TimelineEvent(
        booking_id=booking.id,
        when=booking.created_at,
        actor=booking.requester_first_name,
        event_type="Created",
        note=None,
    )
    db_session.add(timeline_event)

    # Flush and commit to ensure approvals and timeline are persisted
    await db_session.flush()
    await db_session.commit()

    # Refresh booking to load relationships
    await db_session.refresh(booking, ["approvals", "timeline_events"])

    # Generate requester token
    token = generate_token({
        "email": "token@example.com",
        "role": "requester",
        "booking_id": str(booking.id),
    })

    # GET with token
    response = await client.get(f"/api/v1/bookings/{booking.id}?token={token}")

    assert response.status_code == 200
    data = response.json()

    # Should include all fields
    assert data["id"] == str(booking.id)
    assert data["requester_first_name"] == "TokenUser"
    assert data["description"] == "Secret details"
    assert data["is_past"] is False

    # Should include approvals
    assert "approvals" in data
    assert len(data["approvals"]) == 3

    # Should include timeline_events
    assert "timeline_events" in data
    assert len(data["timeline_events"]) == 1
    assert data["timeline_events"][0]["event_type"] == "Created"


@pytest.mark.asyncio
async def test_get_with_approver_token(db_session: AsyncSession, client: AsyncClient):
    """Test: Valid approver token returns full details."""
    today = get_today()

    booking = Booking(
        requester_first_name="ApproverTest",
        requester_email="requester@example.com",
        start_date=today + timedelta(days=10),
        end_date=today + timedelta(days=14),
        total_days=5,
        party_size=3,
        affiliation=AffiliationEnum.CORNELIA,
        status=StatusEnum.PENDING,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    # Generate approver token (Ingeborg)
    token = generate_token({
        "email": "ingeborg@example.com",
        "role": "approver",
        "party": "Ingeborg",
        "booking_id": str(booking.id),
    })

    response = await client.get(f"/api/v1/bookings/{booking.id}?token={token}")

    assert response.status_code == 200
    data = response.json()
    assert "approvals" in data


@pytest.mark.asyncio
async def test_get_denied_with_token(db_session: AsyncSession, client: AsyncClient):
    """Test BR-004: Denied booking accessible with valid token."""
    today = get_today()

    # Create Denied booking
    booking = Booking(
        requester_first_name="DeniedToken",
        requester_email="denied@example.com",
        start_date=today + timedelta(days=10),
        end_date=today + timedelta(days=14),
        total_days=5,
        party_size=2,
        affiliation=AffiliationEnum.ANGELIKA,
        status=StatusEnum.DENIED,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    # Without token should return 404
    response_no_token = await client.get(f"/api/v1/bookings/{booking.id}")
    assert response_no_token.status_code == 404

    # With valid requester token should return 200
    token = generate_token({
        "email": "denied@example.com",
        "role": "requester",
        "booking_id": str(booking.id),
    })

    response_with_token = await client.get(f"/api/v1/bookings/{booking.id}?token={token}")

    assert response_with_token.status_code == 200
    data = response_with_token.json()
    assert data["status"] == "Denied"


@pytest.mark.asyncio
async def test_get_invalid_token_401(db_session: AsyncSession, client: AsyncClient):
    """Test: Invalid token signature returns 401 with German error."""
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

    response = await client.get(f"/api/v1/bookings/{booking.id}?token={invalid_token}")

    assert response.status_code == 401
    detail = response.json()["detail"]
    assert "Ungültiger Zugangslink." == detail


@pytest.mark.asyncio
async def test_get_wrong_booking_token_403(db_session: AsyncSession, client: AsyncClient):
    """Test: Token for different booking returns 403 with German error."""
    today = get_today()

    # Create two bookings
    booking1 = Booking(
        requester_first_name="User1",
        requester_email="user1@example.com",
        start_date=today + timedelta(days=10),
        end_date=today + timedelta(days=14),
        total_days=5,
        party_size=2,
        affiliation=AffiliationEnum.INGEBORG,
        status=StatusEnum.PENDING,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    booking2 = Booking(
        requester_first_name="User2",
        requester_email="user2@example.com",
        start_date=today + timedelta(days=20),
        end_date=today + timedelta(days=24),
        total_days=5,
        party_size=3,
        affiliation=AffiliationEnum.CORNELIA,
        status=StatusEnum.PENDING,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    db_session.add(booking1)
    db_session.add(booking2)
    await db_session.commit()
    await db_session.refresh(booking1)
    await db_session.refresh(booking2)

    # Generate token for booking1
    token_for_booking1 = generate_token({
        "email": "user1@example.com",
        "role": "requester",
        "booking_id": str(booking1.id),
    })

    # Try to access booking2 with booking1's token
    response = await client.get(f"/api/v1/bookings/{booking2.id}?token={token_for_booking1}")

    assert response.status_code == 403
    detail = response.json()["detail"]
    assert "Du hast keinen Zugriff auf diesen Eintrag." == detail


# ============================================================================
# Past Indicator (3 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_is_past_yesterday(db_session: AsyncSession, client: AsyncClient):
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

    response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["is_past"] is True


@pytest.mark.asyncio
async def test_is_past_today(db_session: AsyncSession, client: AsyncClient):
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

    response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["is_past"] is False


@pytest.mark.asyncio
async def test_is_past_tomorrow(db_session: AsyncSession, client: AsyncClient):
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

    response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["is_past"] is False


# ============================================================================
# German Errors (3 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_german_404(db_session: AsyncSession, client: AsyncClient):
    """Test: 404 error message in German."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"

    response = await client.get(f"/api/v1/bookings/{fake_uuid}")

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert "Der Eintrag konnte leider nicht gefunden werden." == detail


@pytest.mark.asyncio
async def test_german_401(db_session: AsyncSession, client: AsyncClient):
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

    response = await client.get(f"/api/v1/bookings/{booking.id}?token={invalid_token}")

    assert response.status_code == 401
    detail = response.json()["detail"]
    assert "Ungültiger Zugangslink." == detail


@pytest.mark.asyncio
async def test_german_403(db_session: AsyncSession, client: AsyncClient):
    """Test: 403 error message in German (wrong booking token)."""
    # This is covered by test_get_wrong_booking_token_403
    # which already validates the German 403 message
    today = get_today()

    # Create two bookings
    booking1 = Booking(
        requester_first_name="User1",
        requester_email="user1@example.com",
        start_date=today + timedelta(days=10),
        end_date=today + timedelta(days=14),
        total_days=5,
        party_size=2,
        affiliation=AffiliationEnum.INGEBORG,
        status=StatusEnum.PENDING,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    booking2 = Booking(
        requester_first_name="User2",
        requester_email="user2@example.com",
        start_date=today + timedelta(days=20),
        end_date=today + timedelta(days=24),
        total_days=5,
        party_size=3,
        affiliation=AffiliationEnum.CORNELIA,
        status=StatusEnum.PENDING,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    db_session.add(booking1)
    db_session.add(booking2)
    await db_session.commit()
    await db_session.refresh(booking1)
    await db_session.refresh(booking2)

    # Generate token for booking1
    token_for_booking1 = generate_token({
        "email": "user1@example.com",
        "role": "requester",
        "booking_id": str(booking1.id),
    })

    # Try to access booking2 with booking1's token
    response = await client.get(f"/api/v1/bookings/{booking2.id}?token={token_for_booking1}")

    assert response.status_code == 403
    detail = response.json()["detail"]
    assert "Du hast keinen Zugriff auf diesen Eintrag." == detail

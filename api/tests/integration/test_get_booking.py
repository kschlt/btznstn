"""
Integration tests for US-2.2: Get Booking Endpoint.

Tests all business rules and edge cases per phase-2-booking-api.md.

Test Plan (~20 tests):
- Public View (6 tests)
- Authenticated View (5 tests)
- Past Indicator (3 tests)
- German Errors (3 tests)
"""

from datetime import timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tokens import generate_token
from app.models.enums import AffiliationEnum, DecisionEnum, StatusEnum
from tests.fixtures.factories import make_approval, make_booking, make_timeline_event
from tests.utils import get_today


# ============================================================================
# Public View (6 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_get_public_pending_booking(db_session: AsyncSession, client: AsyncClient):
    """Test public GET on Pending booking returns limited fields."""
    # Create a Pending booking
    booking = make_booking(
        requester_first_name="Anna",
        description="Private description",
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
    booking = make_booking(
        requester_first_name="Max",
        requester_email="max@example.com",
        start_date=today + timedelta(days=20),
        end_date=today + timedelta(days=25),
        party_size=2,
        affiliation=AffiliationEnum.CORNELIA,
        status=StatusEnum.CONFIRMED,
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
    booking = make_booking(
        requester_first_name="Denied",
        requester_email="denied@example.com",
        party_size=3,
        affiliation=AffiliationEnum.ANGELIKA,
        status=StatusEnum.DENIED,
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
    booking = make_booking(
        requester_first_name="Canceled",
        requester_email="canceled@example.com",
        party_size=5,
        status=StatusEnum.CANCELED,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_public_excludes_email(db_session: AsyncSession, client: AsyncClient):
    """Test privacy: Public response does not include requester_email."""
    booking = make_booking(
        requester_first_name="Privacy",
        requester_email="privacy@example.com",
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
    booking = make_booking(
        requester_first_name="TestUser",
        description="This is a secret description with sensitive info",
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
    # Create booking with approvals and timeline
    booking = make_booking(
        requester_first_name="TokenUser",
        requester_email="token@example.com",
        description="Secret details",
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    # Create approvals
    for party in [AffiliationEnum.INGEBORG, AffiliationEnum.CORNELIA, AffiliationEnum.ANGELIKA]:
        approval = make_approval(
            booking_id=booking.id,
            party=party,
        )
        db_session.add(approval)

    # Create timeline event
    timeline_event = make_timeline_event(
        booking_id=booking.id,
        when=booking.created_at,
        actor=booking.requester_first_name,
        event_type="Created",
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
    booking = make_booking(
        requester_first_name="ApproverTest",
        requester_email="requester@example.com",
        party_size=3,
        affiliation=AffiliationEnum.CORNELIA,
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
    # Create Denied booking
    booking = make_booking(
        requester_first_name="DeniedToken",
        requester_email="denied@example.com",
        party_size=2,
        affiliation=AffiliationEnum.ANGELIKA,
        status=StatusEnum.DENIED,
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
    booking = make_booking(
        requester_first_name="Auth",
        requester_email="auth@example.com",
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
    booking1 = make_booking(
        requester_first_name="User1",
        requester_email="user1@example.com",
        party_size=2,
    )
    booking2 = make_booking(
        requester_first_name="User2",
        requester_email="user2@example.com",
        start_date=today + timedelta(days=20),
        end_date=today + timedelta(days=24),
        party_size=3,
        affiliation=AffiliationEnum.CORNELIA,
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

    booking = make_booking(
        requester_first_name="Past",
        requester_email="past@example.com",
        start_date=yesterday - timedelta(days=4),
        end_date=yesterday,
        party_size=2,
        status=StatusEnum.CONFIRMED,
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

    booking = make_booking(
        requester_first_name="Today",
        requester_email="today@example.com",
        start_date=today - timedelta(days=2),
        end_date=today,
        party_size=3,
        affiliation=AffiliationEnum.CORNELIA,
        status=StatusEnum.CONFIRMED,
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

    booking = make_booking(
        requester_first_name="Future",
        requester_email="future@example.com",
        start_date=today,
        end_date=tomorrow,
        affiliation=AffiliationEnum.ANGELIKA,
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
    booking = make_booking(
        requester_first_name="Auth",
        requester_email="auth@example.com",
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
    booking1 = make_booking(
        requester_first_name="User1",
        requester_email="user1@example.com",
        party_size=2,
    )
    booking2 = make_booking(
        requester_first_name="User2",
        requester_email="user2@example.com",
        start_date=today + timedelta(days=20),
        end_date=today + timedelta(days=24),
        party_size=3,
        affiliation=AffiliationEnum.CORNELIA,
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

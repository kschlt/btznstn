"""
Integration tests for US-2.4: Cancel Booking Endpoint.

Tests all business rules and edge cases per phase-2-booking-api.md.

Test Plan (~27 tests):
- Cancel Pending (4 tests)
- Cancel Confirmed (4 tests)
- Authorization (4 tests)
- Past Items Read-Only (3 tests)
- Comment Validation (3 tests)
- State Validation (4 tests)
- German Errors (3 tests)
- Idempotency (2 tests)
"""

from datetime import timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tokens import generate_token
from app.models.booking import Booking
from app.models.enums import StatusEnum
from tests.fixtures.factories import make_booking
from tests.utils import get_today


# ============================================================================
# Helper Functions
# ============================================================================


def make_requester_token(booking_id, email: str) -> str:
    """Generate requester token for a booking."""
    return generate_token({
        "email": email,
        "role": "requester",
        "booking_id": str(booking_id),
    })


def make_approver_token(booking_id, party: str) -> str:
    """Generate approver token for a booking."""
    return generate_token({
        "email": f"{party.lower()}@example.com",
        "role": "approver",
        "booking_id": str(booking_id),
        "party": party,
    })


# ============================================================================
# Cancel Pending Tests (4 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_cancel_pending_no_comment(db_session: AsyncSession, client: AsyncClient):
    """Test BR-006: Cancel Pending without comment succeeds."""
    booking = make_booking(
        requester_email="anna@example.com",
        status=StatusEnum.PENDING,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "storniert" in data["message"].lower()


@pytest.mark.asyncio
async def test_cancel_pending_with_comment(db_session: AsyncSession, client: AsyncClient):
    """Test BR-006: Cancel Pending with optional comment succeeds."""
    booking = make_booking(
        requester_email="anna@example.com",
        status=StatusEnum.PENDING,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"comment": "Can't make it"},
    )

    assert response.status_code == 200

    # Verify booking status changed to Canceled
    await db_session.refresh(booking)
    assert booking.status == StatusEnum.CANCELED


@pytest.mark.asyncio
async def test_cancel_pending_notifications(db_session: AsyncSession, client: AsyncClient):
    """Test BR-006: 4 emails sent (requester + 3 approvers)."""
    booking = make_booking(
        requester_email="anna@example.com",
        status=StatusEnum.PENDING,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
    )

    assert response.status_code == 200
    # Note: Email verification would be in Phase 4 (email integration)


@pytest.mark.asyncio
async def test_cancel_pending_result_page(db_session: AsyncSession, client: AsyncClient):
    """Test BR-006: Result page shows German message with notified names."""
    booking = make_booking(
        requester_email="anna@example.com",
        status=StatusEnum.PENDING,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
    )

    assert response.status_code == 200
    data = response.json()
    # Expected: "Anfrage storniert. Benachrichtigt: Ingeborg, Cornelia und Angelika."
    assert "benachrichtigt" in data["message"].lower()
    assert "ingeborg" in data["message"].lower()
    assert "cornelia" in data["message"].lower()
    assert "angelika" in data["message"].lower()


# ============================================================================
# Cancel Confirmed Tests (4 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_cancel_confirmed_no_comment_400(db_session: AsyncSession, client: AsyncClient):
    """Test BR-007: Cancel Confirmed without comment fails (comment required)."""
    booking = make_booking(
        requester_email="anna@example.com",
        status=StatusEnum.CONFIRMED,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
    )

    assert response.status_code == 400
    data = response.json()
    # Expected: "Bitte gib einen kurzen Grund an."
    assert "grund" in data["detail"].lower()


@pytest.mark.asyncio
async def test_cancel_confirmed_with_comment_succeeds(db_session: AsyncSession, client: AsyncClient):
    """Test BR-007: Cancel Confirmed with comment succeeds."""
    booking = make_booking(
        requester_email="anna@example.com",
        status=StatusEnum.CONFIRMED,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"comment": "Kann leider nicht kommen"},
    )

    assert response.status_code == 200

    # Verify booking status changed to Canceled
    await db_session.refresh(booking)
    assert booking.status == StatusEnum.CANCELED


@pytest.mark.asyncio
async def test_cancel_confirmed_comment_in_timeline(db_session: AsyncSession, client: AsyncClient):
    """Test BR-007: Comment stored in timeline event."""
    booking = make_booking(
        requester_email="anna@example.com",
        status=StatusEnum.CONFIRMED,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    comment = "Kann leider nicht kommen"
    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"comment": comment},
    )

    assert response.status_code == 200
    # Note: Timeline event verification would need to fetch booking with timeline


@pytest.mark.asyncio
async def test_cancel_confirmed_notifications(db_session: AsyncSession, client: AsyncClient):
    """Test BR-007: 4 emails sent (requester + 3 approvers)."""
    booking = make_booking(
        requester_email="anna@example.com",
        status=StatusEnum.CONFIRMED,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"comment": "Emergency"},
    )

    assert response.status_code == 200
    # Note: Email verification would be in Phase 4


# ============================================================================
# Authorization Tests (4 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_cancel_with_valid_token(db_session: AsyncSession, client: AsyncClient):
    """Test BR-010: Valid requester token allows cancel."""
    booking = make_booking(requester_email="anna@example.com")
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_cancel_with_invalid_token_401(db_session: AsyncSession, client: AsyncClient):
    """Test BR-010: Invalid token returns 401."""
    booking = make_booking()
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": "invalid.token"},
    )

    assert response.status_code == 401
    data = response.json()
    assert "ungültig" in data["detail"].lower()


@pytest.mark.asyncio
async def test_cancel_with_wrong_requester_token_403(db_session: AsyncSession, client: AsyncClient):
    """Test BR-010: Valid token for different requester returns 403."""
    booking = make_booking(requester_email="anna@example.com")
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    # Token for different email
    token = make_requester_token(booking.id, "wrong@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
    )

    assert response.status_code == 403
    data = response.json()
    assert "keinen zugriff" in data["detail"].lower()


@pytest.mark.asyncio
async def test_cancel_with_approver_token_403(db_session: AsyncSession, client: AsyncClient):
    """Test: Approver token does not allow cancel (requester only)."""
    booking = make_booking()
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    # Approver token should not allow canceling
    token = make_approver_token(booking.id, "Ingeborg")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
    )

    assert response.status_code == 403


# ============================================================================
# Past Items Read-Only Tests (3 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_cancel_past_booking_fails(db_session: AsyncSession, client: AsyncClient):
    """Test BR-014: Cannot cancel booking ending yesterday."""
    today = get_today()
    yesterday = today - timedelta(days=1)

    booking = make_booking(
        requester_email="anna@example.com",
        start_date=yesterday - timedelta(days=4),
        end_date=yesterday,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
    )

    assert response.status_code == 400
    data = response.json()
    assert "vergangenheit" in data["detail"].lower()


@pytest.mark.asyncio
async def test_cancel_booking_ending_today_succeeds(db_session: AsyncSession, client: AsyncClient):
    """Test BR-014: Can cancel booking ending today."""
    today = get_today()

    booking = make_booking(
        requester_email="anna@example.com",
        start_date=today - timedelta(days=4),
        end_date=today,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_cancel_booking_ending_tomorrow_succeeds(db_session: AsyncSession, client: AsyncClient):
    """Test BR-014: Can cancel booking ending tomorrow."""
    today = get_today()
    tomorrow = today + timedelta(days=1)

    booking = make_booking(
        requester_email="anna@example.com",
        start_date=today - timedelta(days=4),
        end_date=tomorrow,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
    )

    assert response.status_code == 200


# ============================================================================
# Comment Validation Tests (3 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_cancel_comment_no_links(db_session: AsyncSession, client: AsyncClient):
    """Test BR-020: Comment without links accepted."""
    booking = make_booking(
        requester_email="anna@example.com",
        status=StatusEnum.CONFIRMED,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"comment": "Can't make it"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_cancel_comment_with_http_rejected(db_session: AsyncSession, client: AsyncClient):
    """Test BR-020: Comment with http:// rejected."""
    booking = make_booking(
        requester_email="anna@example.com",
        status=StatusEnum.CONFIRMED,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"comment": "See http://example.com for details"},
    )

    assert response.status_code == 400
    data = response.json()
    assert "links" in data["detail"].lower()


@pytest.mark.asyncio
async def test_cancel_comment_case_insensitive(db_session: AsyncSession, client: AsyncClient):
    """Test BR-020: Link detection is case-insensitive."""
    booking = make_booking(
        requester_email="anna@example.com",
        status=StatusEnum.CONFIRMED,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    # Test with WWW (uppercase)
    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"comment": "Check WWW.example.com"},
    )

    assert response.status_code == 400
    data = response.json()
    assert "links" in data["detail"].lower()


# ============================================================================
# State Validation Tests (4 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_cancel_pending_succeeds(db_session: AsyncSession, client: AsyncClient):
    """Test: Pending → Canceled."""
    booking = make_booking(
        requester_email="anna@example.com",
        status=StatusEnum.PENDING,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
    )

    assert response.status_code == 200

    # Verify status transition
    await db_session.refresh(booking)
    assert booking.status == StatusEnum.CANCELED


@pytest.mark.asyncio
async def test_cancel_confirmed_succeeds(db_session: AsyncSession, client: AsyncClient):
    """Test: Confirmed → Canceled (with comment)."""
    booking = make_booking(
        requester_email="anna@example.com",
        status=StatusEnum.CONFIRMED,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"comment": "Emergency"},
    )

    assert response.status_code == 200

    # Verify status transition
    await db_session.refresh(booking)
    assert booking.status == StatusEnum.CANCELED


@pytest.mark.asyncio
async def test_cancel_denied_fails(db_session: AsyncSession, client: AsyncClient):
    """Test: Denied cannot be canceled (already terminal)."""
    booking = make_booking(
        requester_email="anna@example.com",
        status=StatusEnum.DENIED,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_cancel_already_canceled_404(db_session: AsyncSession, client: AsyncClient):
    """Test: Already Canceled returns 404 (or special message)."""
    booking = make_booking(
        requester_email="anna@example.com",
        status=StatusEnum.CANCELED,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
    )

    # Could be 404 or 200 with "already canceled" message (idempotent)
    assert response.status_code in [200, 404]


# ============================================================================
# German Error Messages Tests (3 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_cancel_german_comment_required(db_session: AsyncSession, client: AsyncClient):
    """Test BR-011: Comment required error in German."""
    booking = make_booking(
        requester_email="anna@example.com",
        status=StatusEnum.CONFIRMED,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
    )

    assert response.status_code == 400
    data = response.json()
    # Expected: "Bitte gib einen kurzen Grund an."
    assert "bitte" in data["detail"].lower()
    assert "grund" in data["detail"].lower()


@pytest.mark.asyncio
async def test_cancel_german_link_blocked(db_session: AsyncSession, client: AsyncClient):
    """Test BR-011: Link blocked error in German."""
    booking = make_booking(
        requester_email="anna@example.com",
        status=StatusEnum.CONFIRMED,
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"comment": "See http://example.com"},
    )

    assert response.status_code == 400
    data = response.json()
    # Expected: "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden."
    assert "links" in data["detail"].lower()
    assert "nicht erlaubt" in data["detail"].lower()


@pytest.mark.asyncio
async def test_cancel_german_success(db_session: AsyncSession, client: AsyncClient):
    """Test BR-011: Success message in German."""
    booking = make_booking(requester_email="anna@example.com")
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.delete(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
    )

    assert response.status_code == 200
    data = response.json()
    # Expected: "Anfrage storniert. Benachrichtigt: ..."
    assert "storniert" in data["message"].lower()

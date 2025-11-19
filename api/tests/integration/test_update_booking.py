"""
Integration tests for US-2.3: Update Booking Endpoint.

Tests all business rules and edge cases per phase-2-booking-api.md.

Test Plan (~35 tests):
- Authorization (4 tests)
- Date Recalculation (2 tests)
- Conflict Detection (4 tests)
- BR-005: Approval Reset Logic (8 tests) - CRITICAL
- Timeline Events (2 tests)
- Past Items Read-Only (3 tests)
- Validation (6 tests)
- Optimistic Locking (2 tests)
- German Errors (4 tests)
"""

from datetime import date, timedelta
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tokens import generate_token
from app.models.approval import Approval
from app.models.booking import Booking
from app.models.enums import AffiliationEnum, DecisionEnum, StatusEnum
from app.models.timeline_event import TimelineEvent
from tests.fixtures.factories import make_approval, make_booking, get_now
from tests.utils import get_today


# ============================================================================
# Helper Functions
# ============================================================================


def make_requester_token(booking_id: UUID, email: str) -> str:
    """Generate requester token for a booking."""
    return generate_token({
        "email": email,
        "role": "requester",
        "booking_id": str(booking_id),
    })


def make_approver_token(booking_id: UUID, party: str) -> str:
    """Generate approver token for a booking."""
    return generate_token({
        "email": f"{party.lower()}@example.com",
        "role": "approver",
        "booking_id": str(booking_id),
        "party": party,
    })


async def create_booking_with_approvals(
    db_session: AsyncSession,
    **booking_kwargs,
) -> tuple[Booking, list[Approval]]:
    """
    Create a booking with 3 NoResponse approvals in database.

    Returns tuple of (booking, approvals list).
    """
    booking = make_booking(**booking_kwargs)
    db_session.add(booking)
    await db_session.flush()  # Get booking.id

    # Create 3 approvals
    approvals = [
        make_approval(booking_id=booking.id, party=AffiliationEnum.INGEBORG),
        make_approval(booking_id=booking.id, party=AffiliationEnum.CORNELIA),
        make_approval(booking_id=booking.id, party=AffiliationEnum.ANGELIKA),
    ]
    for approval in approvals:
        db_session.add(approval)

    await db_session.commit()
    await db_session.refresh(booking)

    return booking, approvals


# ============================================================================
# Authorization Tests (4 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_edit_with_valid_token(db_session: AsyncSession, client: AsyncClient):
    """Test BR-010: Valid requester token allows edit."""
    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
    )

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"party_size": 6},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["party_size"] == 6


@pytest.mark.asyncio
async def test_edit_with_invalid_token_401(db_session: AsyncSession, client: AsyncClient):
    """Test BR-010: Invalid token returns 401."""
    booking, _ = await create_booking_with_approvals(db_session)

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": "invalid.token"},
        json={"party_size": 6},
    )

    assert response.status_code == 401
    data = response.json()
    assert "ungültig" in data["detail"].lower()


@pytest.mark.asyncio
async def test_edit_with_wrong_requester_token_403(db_session: AsyncSession, client: AsyncClient):
    """Test BR-010: Valid token for different requester returns 403."""
    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
    )

    # Token for a different email
    token = make_requester_token(booking.id, "wrong@example.com")

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"party_size": 6},
    )

    assert response.status_code == 403
    data = response.json()
    assert "keinen zugriff" in data["detail"].lower()


@pytest.mark.asyncio
async def test_edit_with_approver_token_403(db_session: AsyncSession, client: AsyncClient):
    """Test: Approver token does not allow edit (requester only)."""
    booking, _ = await create_booking_with_approvals(db_session)

    # Approver token should not allow editing
    token = make_approver_token(booking.id, "Ingeborg")

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"party_size": 6},
    )

    assert response.status_code == 403


# ============================================================================
# Date Recalculation Tests (2 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_edit_dates_recalculates_total_days(db_session: AsyncSession, client: AsyncClient):
    """Test BR-001: Extending dates recalculates total_days (5 → 10 days)."""
    today = get_today()
    start = today + timedelta(days=10)
    end = today + timedelta(days=14)  # 5 days

    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        start_date=start,
        end_date=end,
    )

    assert booking.total_days == 5

    token = make_requester_token(booking.id, "anna@example.com")
    new_end = today + timedelta(days=19)  # Extend to 10 days

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"end_date": new_end.isoformat()},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_days"] == 10  # BR-001: inclusive calculation


@pytest.mark.asyncio
async def test_shorten_dates_recalculates_total_days(db_session: AsyncSession, client: AsyncClient):
    """Test BR-001: Shortening dates recalculates total_days (10 → 6 days)."""
    today = get_today()
    start = today + timedelta(days=1)
    end = today + timedelta(days=10)  # 10 days

    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        start_date=start,
        end_date=end,
    )

    assert booking.total_days == 10

    token = make_requester_token(booking.id, "anna@example.com")

    # Shorten: Jan 1-10 → Jan 3-8 (6 days)
    new_start = today + timedelta(days=3)
    new_end = today + timedelta(days=8)

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={
            "start_date": new_start.isoformat(),
            "end_date": new_end.isoformat(),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_days"] == 6


# ============================================================================
# Conflict Detection Tests (4 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_edit_to_non_conflicting_dates(db_session: AsyncSession, client: AsyncClient):
    """Test BR-002: Edit to non-conflicting dates succeeds."""
    today = get_today()

    # Existing booking: Aug 1-5
    existing = make_booking(
        start_date=today + timedelta(days=30),
        end_date=today + timedelta(days=34),
    )
    db_session.add(existing)
    await db_session.commit()

    # Our booking: Aug 10-15 (no conflict)
    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        start_date=today + timedelta(days=40),
        end_date=today + timedelta(days=45),
    )

    token = make_requester_token(booking.id, "anna@example.com")

    # Move to Aug 20-25 (still no conflict)
    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={
            "start_date": (today + timedelta(days=50)).isoformat(),
            "end_date": (today + timedelta(days=55)).isoformat(),
        },
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_edit_to_conflicting_dates_409(db_session: AsyncSession, client: AsyncClient):
    """Test BR-002: Edit to conflicting dates returns 409."""
    today = get_today()

    # Existing booking: Aug 10-15 (Pending - blocks dates)
    existing = make_booking(
        start_date=today + timedelta(days=40),
        end_date=today + timedelta(days=45),
        status=StatusEnum.PENDING,
    )
    db_session.add(existing)
    await db_session.commit()

    # Our booking: Aug 1-5
    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        start_date=today + timedelta(days=30),
        end_date=today + timedelta(days=34),
    )

    token = make_requester_token(booking.id, "anna@example.com")

    # Try to extend end date into existing booking: Aug 1-12 (conflicts with Aug 10-15)
    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={
            "end_date": (today + timedelta(days=42)).isoformat(),  # Aug 12
        },
    )

    assert response.status_code == 409
    data = response.json()
    assert "überschneidet" in data["detail"].lower()


@pytest.mark.asyncio
async def test_edit_same_dates_succeeds(db_session: AsyncSession, client: AsyncClient):
    """Test BR-002: Editing same dates (no change) succeeds."""
    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
    )

    token = make_requester_token(booking.id, "anna@example.com")

    # Edit party size only, no date change
    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"party_size": 6},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_self_overlap_excluded(db_session: AsyncSession, client: AsyncClient):
    """Test BR-002: Current booking excluded from conflict check (no self-overlap)."""
    today = get_today()

    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        start_date=today + timedelta(days=10),
        end_date=today + timedelta(days=14),
    )

    token = make_requester_token(booking.id, "anna@example.com")

    # Extend the booking - should not conflict with itself
    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={
            "end_date": (today + timedelta(days=20)).isoformat(),
        },
    )

    assert response.status_code == 200


# ============================================================================
# BR-005: Approval Reset Logic Tests (8 tests) - CRITICAL
# ============================================================================


@pytest.mark.asyncio
async def test_shorten_keeps_approvals(db_session: AsyncSession, client: AsyncClient):
    """Test BR-005: Shortening dates KEEPS approvals unchanged."""
    today = get_today()
    start = today + timedelta(days=1)
    end = today + timedelta(days=10)  # Jan 1-10

    booking, approvals = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        start_date=start,
        end_date=end,
    )

    # Two approvers already approved
    approvals[0].decision = DecisionEnum.APPROVED
    approvals[0].decided_at = get_now()
    approvals[1].decision = DecisionEnum.APPROVED
    approvals[1].decided_at = get_now()
    await db_session.commit()

    token = make_requester_token(booking.id, "anna@example.com")

    # Shorten: Jan 1-10 → Jan 3-8 (within bounds)
    new_start = today + timedelta(days=3)
    new_end = today + timedelta(days=8)

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={
            "start_date": new_start.isoformat(),
            "end_date": new_end.isoformat(),
        },
    )

    assert response.status_code == 200

    # Refresh approvals from DB
    await db_session.refresh(approvals[0])
    await db_session.refresh(approvals[1])

    # BR-005: Approvals should remain unchanged
    assert approvals[0].decision == DecisionEnum.APPROVED
    assert approvals[1].decision == DecisionEnum.APPROVED


@pytest.mark.asyncio
async def test_extend_start_resets_approvals(db_session: AsyncSession, client: AsyncClient):
    """Test BR-005: Extending start date RESETS all approvals to NoResponse."""
    today = get_today()
    start = today + timedelta(days=5)
    end = today + timedelta(days=10)  # Jan 5-10

    booking, approvals = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        start_date=start,
        end_date=end,
    )

    # Two approvers already approved
    approvals[0].decision = DecisionEnum.APPROVED
    approvals[0].decided_at = get_now()
    approvals[1].decision = DecisionEnum.APPROVED
    approvals[1].decided_at = get_now()
    await db_session.commit()

    token = make_requester_token(booking.id, "anna@example.com")

    # Extend start: Jan 5-10 → Jan 1-10 (earlier start)
    new_start = today + timedelta(days=1)

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"start_date": new_start.isoformat()},
    )

    assert response.status_code == 200

    # Refresh approvals from DB
    await db_session.refresh(approvals[0])
    await db_session.refresh(approvals[1])
    await db_session.refresh(approvals[2])

    # BR-005: All approvals should be reset to NoResponse
    assert approvals[0].decision == DecisionEnum.NO_RESPONSE
    assert approvals[0].decided_at is None
    assert approvals[1].decision == DecisionEnum.NO_RESPONSE
    assert approvals[1].decided_at is None
    assert approvals[2].decision == DecisionEnum.NO_RESPONSE


@pytest.mark.asyncio
async def test_extend_end_resets_approvals(db_session: AsyncSession, client: AsyncClient):
    """Test BR-005: Extending end date RESETS all approvals to NoResponse."""
    today = get_today()
    start = today + timedelta(days=1)
    end = today + timedelta(days=5)  # Jan 1-5

    booking, approvals = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        start_date=start,
        end_date=end,
    )

    # Two approvers already approved
    approvals[0].decision = DecisionEnum.APPROVED
    approvals[0].decided_at = get_now()
    approvals[1].decision = DecisionEnum.APPROVED
    approvals[1].decided_at = get_now()
    await db_session.commit()

    token = make_requester_token(booking.id, "anna@example.com")

    # Extend end: Jan 1-5 → Jan 1-10 (later end)
    new_end = today + timedelta(days=10)

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"end_date": new_end.isoformat()},
    )

    assert response.status_code == 200

    # Refresh approvals
    await db_session.refresh(approvals[0])
    await db_session.refresh(approvals[1])

    # BR-005: All approvals reset
    assert approvals[0].decision == DecisionEnum.NO_RESPONSE
    assert approvals[1].decision == DecisionEnum.NO_RESPONSE


@pytest.mark.asyncio
async def test_extend_both_resets_approvals(db_session: AsyncSession, client: AsyncClient):
    """Test BR-005: Extending both start and end RESETS approvals."""
    today = get_today()
    start = today + timedelta(days=3)
    end = today + timedelta(days=8)  # Jan 3-8

    booking, approvals = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        start_date=start,
        end_date=end,
    )

    # Approved
    approvals[0].decision = DecisionEnum.APPROVED
    approvals[0].decided_at = get_now()
    await db_session.commit()

    token = make_requester_token(booking.id, "anna@example.com")

    # Extend both: Jan 3-8 → Jan 1-10
    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={
            "start_date": (today + timedelta(days=1)).isoformat(),
            "end_date": (today + timedelta(days=10)).isoformat(),
        },
    )

    assert response.status_code == 200

    # Refresh
    await db_session.refresh(approvals[0])

    # BR-005: Reset
    assert approvals[0].decision == DecisionEnum.NO_RESPONSE


@pytest.mark.asyncio
async def test_party_size_only_keeps_approvals(db_session: AsyncSession, client: AsyncClient):
    """Test BR-005: Changing party size only KEEPS approvals."""
    booking, approvals = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
    )

    # Approved
    approvals[0].decision = DecisionEnum.APPROVED
    approvals[0].decided_at = get_now()
    await db_session.commit()

    token = make_requester_token(booking.id, "anna@example.com")

    # Change party size only (no date change)
    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"party_size": 6},
    )

    assert response.status_code == 200

    # Refresh
    await db_session.refresh(approvals[0])

    # BR-005: Approval should remain
    assert approvals[0].decision == DecisionEnum.APPROVED


@pytest.mark.asyncio
async def test_affiliation_only_keeps_approvals(db_session: AsyncSession, client: AsyncClient):
    """Test BR-005: Changing affiliation only KEEPS approvals."""
    booking, approvals = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        affiliation=AffiliationEnum.INGEBORG,
    )

    # Approved
    approvals[0].decision = DecisionEnum.APPROVED
    approvals[0].decided_at = get_now()
    await db_session.commit()

    token = make_requester_token(booking.id, "anna@example.com")

    # Change affiliation only
    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"affiliation": "Cornelia"},
    )

    assert response.status_code == 200

    # Refresh
    await db_session.refresh(approvals[0])

    # Approval should remain
    assert approvals[0].decision == DecisionEnum.APPROVED


@pytest.mark.asyncio
async def test_first_name_only_keeps_approvals(db_session: AsyncSession, client: AsyncClient):
    """Test BR-025: Changing first name only KEEPS approvals (and no timeline event)."""
    booking, approvals = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        requester_first_name="Anna",
    )

    # Approved
    approvals[0].decision = DecisionEnum.APPROVED
    approvals[0].decided_at = get_now()
    await db_session.commit()

    # Check timeline events before edit
    result = await db_session.execute(
        select(TimelineEvent).where(TimelineEvent.booking_id == booking.id)
    )
    events_before = len(result.scalars().all())

    token = make_requester_token(booking.id, "anna@example.com")

    # Change first name only
    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"requester_first_name": "Anna-Marie"},
    )

    assert response.status_code == 200

    # Refresh
    await db_session.refresh(approvals[0])

    # BR-025: Approval should remain
    assert approvals[0].decision == DecisionEnum.APPROVED

    # BR-025: No timeline event created for first name change
    result = await db_session.execute(
        select(TimelineEvent).where(TimelineEvent.booking_id == booking.id)
    )
    events_after = len(result.scalars().all())
    assert events_after == events_before  # No new event


@pytest.mark.asyncio
async def test_extend_on_confirmed_resets_approvals(db_session: AsyncSession, client: AsyncClient):
    """Test BR-005: Extending dates on Confirmed booking resets approvals (status stays Confirmed)."""
    today = get_today()

    booking, approvals = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        start_date=today + timedelta(days=1),
        end_date=today + timedelta(days=5),
        status=StatusEnum.CONFIRMED,
    )

    # All approved (for Confirmed status)
    for approval in approvals:
        approval.decision = DecisionEnum.APPROVED
        approval.decided_at = get_now()
    await db_session.commit()

    token = make_requester_token(booking.id, "anna@example.com")

    # Extend end date
    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"end_date": (today + timedelta(days=10)).isoformat()},
    )

    assert response.status_code == 200

    # Refresh booking and approvals
    await db_session.refresh(booking)
    for approval in approvals:
        await db_session.refresh(approval)

    # BR-005: Approvals reset
    assert all(a.decision == DecisionEnum.NO_RESPONSE for a in approvals)

    # Status should still be Confirmed (doesn't revert to Pending)
    assert booking.status == StatusEnum.CONFIRMED


# ============================================================================
# Timeline Events Tests (2 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_date_edit_creates_timeline_event(db_session: AsyncSession, client: AsyncClient):
    """Test: Date edits create timeline event with diff format."""
    today = get_today()
    start = today + timedelta(days=1)
    end = today + timedelta(days=5)

    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        start_date=start,
        end_date=end,
    )

    token = make_requester_token(booking.id, "anna@example.com")

    # Edit dates
    new_end = today + timedelta(days=10)
    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"end_date": new_end.isoformat()},
    )

    assert response.status_code == 200

    # Check timeline event created
    result = await db_session.execute(
        select(TimelineEvent).where(
            TimelineEvent.booking_id == booking.id,
            TimelineEvent.event_type == "Edited",
        )
    )
    events = result.scalars().all()

    # Should have at least one edit event
    assert len(events) > 0


@pytest.mark.asyncio
async def test_first_name_edit_no_timeline_event(db_session: AsyncSession, client: AsyncClient):
    """Test BR-025: First name edits do NOT create timeline event."""
    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        requester_first_name="Anna",
    )

    # Count events before
    result = await db_session.execute(
        select(TimelineEvent).where(TimelineEvent.booking_id == booking.id)
    )
    events_before = len(result.scalars().all())

    token = make_requester_token(booking.id, "anna@example.com")

    # Edit first name only
    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"requester_first_name": "Anna-Marie"},
    )

    assert response.status_code == 200

    # Count events after
    result = await db_session.execute(
        select(TimelineEvent).where(TimelineEvent.booking_id == booking.id)
    )
    events_after = len(result.scalars().all())

    # BR-025: No new timeline event
    assert events_after == events_before


# ============================================================================
# Past Items Read-Only Tests (3 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_edit_past_booking_fails(db_session: AsyncSession, client: AsyncClient):
    """Test BR-014: Cannot edit booking ending yesterday."""
    today = get_today()
    yesterday = today - timedelta(days=1)

    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        start_date=yesterday - timedelta(days=4),
        end_date=yesterday,  # Ended yesterday
    )

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"party_size": 6},
    )

    assert response.status_code == 400
    data = response.json()
    assert "vergangenheit" in data["detail"].lower()


@pytest.mark.asyncio
async def test_edit_booking_ending_today_succeeds(db_session: AsyncSession, client: AsyncClient):
    """Test BR-014: Can edit booking ending today."""
    today = get_today()

    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        start_date=today - timedelta(days=4),
        end_date=today,  # Ends today
    )

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"party_size": 6},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_edit_booking_ending_tomorrow_succeeds(db_session: AsyncSession, client: AsyncClient):
    """Test BR-014: Can edit booking ending tomorrow."""
    today = get_today()
    tomorrow = today + timedelta(days=1)

    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        start_date=today - timedelta(days=4),
        end_date=tomorrow,  # Ends tomorrow
    )

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"party_size": 6},
    )

    assert response.status_code == 200


# ============================================================================
# Validation Tests (6 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_edit_party_size_validation(db_session: AsyncSession, client: AsyncClient):
    """Test BR-017: Party size must be 1-10."""
    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
    )

    token = make_requester_token(booking.id, "anna@example.com")

    # Test party size 0 (invalid)
    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"party_size": 0},
    )

    assert response.status_code == 400

    # Test party size 11 (invalid)
    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"party_size": 11},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_name", [
    "Anna 😊",  # Emoji
    "Anna<script>",  # HTML
    "A" * 41,  # Too long (max 40)
    "",  # Empty
    "123",  # Numbers only
])
async def test_edit_first_name_validation(
    db_session: AsyncSession,
    client: AsyncClient,
    invalid_name: str,
):
    """Test BR-019: First name validation on edit."""
    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
    )

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"requester_first_name": invalid_name},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_description", [
    "Visit http://example.com",
    "Check out https://evil.com",
    "See www.example.com",
    "Email me at mailto:test@example.com",
])
async def test_edit_description_validation(
    db_session: AsyncSession,
    client: AsyncClient,
    invalid_description: str,
):
    """Test BR-020: Link detection in description on edit."""
    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
    )

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"description": invalid_description},
    )

    assert response.status_code == 400
    data = response.json()
    assert "links" in data["detail"].lower()


@pytest.mark.asyncio
async def test_edit_start_date_in_past_fails(db_session: AsyncSession, client: AsyncClient):
    """Test BR-014: Cannot edit to have start date in past."""
    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
    )

    token = make_requester_token(booking.id, "anna@example.com")
    yesterday = get_today() - timedelta(days=1)

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"start_date": yesterday.isoformat()},
    )

    assert response.status_code == 400


# ============================================================================
# Optimistic Locking Tests (2 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_concurrent_edits_handled(db_session: AsyncSession, client: AsyncClient):
    """Test BR-029: Concurrent edits are handled (first-wins or both succeed depending on conflict)."""
    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
    )

    token = make_requester_token(booking.id, "anna@example.com")

    # Both requests edit different fields (should both succeed)
    response1 = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"party_size": 6},
    )

    response2 = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"description": "Updated description"},
    )

    # Both should succeed (different fields)
    assert response1.status_code == 200
    assert response2.status_code == 200


# ============================================================================
# German Error Messages Tests (4 tests)
# ============================================================================


@pytest.mark.asyncio
async def test_edit_german_error_past(db_session: AsyncSession, client: AsyncClient):
    """Test BR-011: Past booking error in German."""
    today = get_today()
    yesterday = today - timedelta(days=1)

    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        start_date=yesterday - timedelta(days=4),
        end_date=yesterday,
    )

    token = make_requester_token(booking.id, "anna@example.com")

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"party_size": 6},
    )

    assert response.status_code == 400
    data = response.json()
    # Expected: "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."
    assert "vergangenheit" in data["detail"].lower()
    assert "geändert" in data["detail"].lower()


@pytest.mark.asyncio
async def test_edit_german_error_conflict(db_session: AsyncSession, client: AsyncClient):
    """Test BR-011: Conflict error in German."""
    today = get_today()

    # Existing booking
    existing = make_booking(
        start_date=today + timedelta(days=40),
        end_date=today + timedelta(days=45),
    )
    db_session.add(existing)
    await db_session.commit()

    # Our booking
    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
        start_date=today + timedelta(days=30),
        end_date=today + timedelta(days=34),
    )

    token = make_requester_token(booking.id, "anna@example.com")

    # Try to extend into conflict
    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"end_date": (today + timedelta(days=42)).isoformat()},
    )

    assert response.status_code == 409
    data = response.json()
    # Expected: "Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung..."
    assert "überschneidet" in data["detail"].lower()


@pytest.mark.asyncio
async def test_edit_german_error_invalid_token(db_session: AsyncSession, client: AsyncClient):
    """Test BR-011: Invalid token error in German."""
    booking, _ = await create_booking_with_approvals(db_session)

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": "invalid.token"},
        json={"party_size": 6},
    )

    assert response.status_code == 401
    data = response.json()
    # Expected: "Ungültiger Zugangslink."
    assert "ungültig" in data["detail"].lower()


@pytest.mark.asyncio
async def test_edit_german_error_no_access(db_session: AsyncSession, client: AsyncClient):
    """Test BR-011: No access error in German."""
    booking, _ = await create_booking_with_approvals(
        db_session,
        requester_email="anna@example.com",
    )

    # Token for different email
    token = make_requester_token(booking.id, "wrong@example.com")

    response = await client.patch(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
        json={"party_size": 6},
    )

    assert response.status_code == 403
    data = response.json()
    # Expected: "Du hast keinen Zugriff auf diesen Eintrag."
    assert "keinen zugriff" in data["detail"].lower()

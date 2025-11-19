"""Test data factories for creating model instances.

Factory functions provide a clean, DRY way to create test data.
All factories use sensible defaults that can be overridden.

Usage:
    from tests.fixtures.factories import make_booking, make_approval

    # Use defaults
    booking = make_booking()

    # Override specific fields
    booking = make_booking(
        requester_first_name="Anna",
        party_size=6,
        status=StatusEnum.CONFIRMED,
    )
"""

from datetime import date, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from app.models.approval import Approval
from app.models.booking import Booking
from app.models.enums import AffiliationEnum, DecisionEnum, StatusEnum
from app.models.timeline_event import TimelineEvent

BERLIN_TZ = ZoneInfo("Europe/Berlin")


def get_today() -> date:
    """Get today's date in Europe/Berlin timezone."""
    return datetime.now(BERLIN_TZ).date()


def get_now() -> datetime:
    """Get current datetime in Europe/Berlin timezone (naive)."""
    return datetime.now(BERLIN_TZ).replace(tzinfo=None)


def make_booking(
    *,
    requester_first_name: str = "Test User",
    requester_email: str = "test@example.com",
    start_date: date | None = None,
    end_date: date | None = None,
    party_size: int = 4,
    affiliation: AffiliationEnum = AffiliationEnum.INGEBORG,
    description: str | None = None,
    status: StatusEnum = StatusEnum.PENDING,
    **kwargs: Any,
) -> Booking:
    """
    Create a Booking instance with sensible defaults.

    By default, creates a future booking (10-14 days from now) in Pending status.
    All fields can be overridden via keyword arguments.

    Args:
        requester_first_name: Requester's first name (default: "Test User")
        requester_email: Requester's email (default: "test@example.com")
        start_date: Start date (default: today + 10 days)
        end_date: End date (default: today + 14 days, i.e., 5 days total)
        party_size: Number of people (default: 4)
        affiliation: Visual affiliation (default: INGEBORG)
        description: Optional description (default: None)
        status: Booking status (default: PENDING)
        **kwargs: Additional fields (created_at, updated_at, last_activity_at)

    Returns:
        Booking instance (not yet added to database)

    Example:
        >>> # Simple booking with defaults
        >>> booking = make_booking()
        >>> db_session.add(booking)
        >>> await db_session.commit()

        >>> # Custom booking
        >>> booking = make_booking(
        ...     requester_first_name="Anna",
        ...     party_size=6,
        ...     status=StatusEnum.CONFIRMED,
        ...     description="Team retreat"
        ... )

        >>> # Specific dates
        >>> booking = make_booking(
        ...     start_date=date(2025, 8, 1),
        ...     end_date=date(2025, 8, 5),
        ... )
    """
    today = get_today()

    # Default dates: 10-14 days from now (5 day booking)
    if start_date is None:
        start_date = today + timedelta(days=10)
    if end_date is None:
        end_date = start_date + timedelta(days=4)

    # Calculate total days (BR-001: inclusive end date)
    total_days = (end_date - start_date).days + 1

    # Default timestamps
    now = get_now()

    return Booking(
        requester_first_name=requester_first_name,
        requester_email=requester_email,
        start_date=start_date,
        end_date=end_date,
        total_days=total_days,
        party_size=party_size,
        affiliation=affiliation,
        description=description,
        status=status,
        created_at=kwargs.get("created_at", now),
        updated_at=kwargs.get("updated_at", now),
        last_activity_at=kwargs.get("last_activity_at", now),
    )


def make_approval(
    *,
    booking_id: UUID | str | None = None,
    party: AffiliationEnum = AffiliationEnum.INGEBORG,
    decision: DecisionEnum = DecisionEnum.NO_RESPONSE,
    decided_at: datetime | None = None,
    comment: str | None = None,
) -> Approval:
    """
    Create an Approval instance with sensible defaults.

    By default, creates a NoResponse approval.
    For approved/denied approvals, set decided_at explicitly.

    Args:
        booking_id: UUID of the booking (default: random UUID)
        party: Approver party (default: INGEBORG)
        decision: Approval decision (default: NO_RESPONSE)
        decided_at: When decision was made (default: None for NoResponse)
        comment: Optional comment from approver (default: None)

    Returns:
        Approval instance (not yet added to database)

    Example:
        >>> # NoResponse approval (default)
        >>> approval = make_approval(booking_id=booking.id)

        >>> # Approved approval
        >>> approval = make_approval(
        ...     booking_id=booking.id,
        ...     party=AffiliationEnum.CORNELIA,
        ...     decision=DecisionEnum.APPROVED,
        ...     decided_at=get_now(),
        ... )

        >>> # Denied approval with comment
        >>> approval = make_approval(
        ...     booking_id=booking.id,
        ...     party=AffiliationEnum.ANGELIKA,
        ...     decision=DecisionEnum.DENIED,
        ...     decided_at=get_now(),
        ...     comment="Conflicts with another event"
        ... )
    """
    # Convert string booking_id to UUID if needed
    if isinstance(booking_id, str):
        booking_id = UUID(booking_id)
    elif booking_id is None:
        booking_id = uuid4()

    return Approval(
        booking_id=booking_id,
        party=party,
        decision=decision,
        decided_at=decided_at,
        comment=comment,
    )


def make_timeline_event(
    *,
    booking_id: UUID | str | None = None,
    when: datetime | None = None,
    actor: str = "System",
    event_type: str = "Created",
    note: str | None = None,
) -> TimelineEvent:
    """
    Create a TimelineEvent instance with sensible defaults.

    Args:
        booking_id: UUID of the booking (default: random UUID)
        when: When the event occurred (default: current time)
        actor: Who performed the action (default: "System")
        event_type: Type of event (default: "Created")
        note: Optional note about the event (default: None)

    Returns:
        TimelineEvent instance (not yet added to database)

    Example:
        >>> # Created event
        >>> event = make_timeline_event(
        ...     booking_id=booking.id,
        ...     actor=booking.requester_first_name,
        ... )

        >>> # Self-approval event
        >>> event = make_timeline_event(
        ...     booking_id=booking.id,
        ...     actor="Ingeborg",
        ...     event_type="SelfApproved",
        ...     note="Ingeborg (self-approval)"
        ... )

        >>> # Approval event
        >>> event = make_timeline_event(
        ...     booking_id=booking.id,
        ...     when=get_now(),
        ...     actor="Cornelia",
        ...     event_type="Approved",
        ...     note="Cornelia party"
        ... )
    """
    # Convert string booking_id to UUID if needed
    if isinstance(booking_id, str):
        booking_id = UUID(booking_id)
    elif booking_id is None:
        booking_id = uuid4()

    # Default to current time
    if when is None:
        when = get_now()

    return TimelineEvent(
        booking_id=booking_id,
        when=when,
        actor=actor,
        event_type=event_type,
        note=note,
    )


# Convenience function for creating a booking with all 3 approvals
def make_booking_with_approvals(
    *,
    booking_kwargs: dict[str, Any] | None = None,
    approval_decisions: dict[AffiliationEnum, DecisionEnum] | None = None,
) -> tuple[Booking, list[Approval]]:
    """
    Create a booking with 3 approval records.

    This is a convenience function that creates both the booking and its approvals.
    Useful for tests that need to verify approval logic.

    Args:
        booking_kwargs: Keyword arguments to pass to make_booking()
        approval_decisions: Dict mapping party to decision (default: all NO_RESPONSE)

    Returns:
        Tuple of (booking, list of 3 approvals)

    Example:
        >>> # Booking with all NoResponse approvals
        >>> booking, approvals = make_booking_with_approvals()

        >>> # Booking with mixed decisions
        >>> booking, approvals = make_booking_with_approvals(
        ...     booking_kwargs={"requester_first_name": "Anna"},
        ...     approval_decisions={
        ...         AffiliationEnum.INGEBORG: DecisionEnum.APPROVED,
        ...         AffiliationEnum.CORNELIA: DecisionEnum.APPROVED,
        ...         AffiliationEnum.ANGELIKA: DecisionEnum.NO_RESPONSE,
        ...     }
        ... )

    Note:
        This function does NOT add the booking/approvals to the database.
        You must still call db_session.add() and commit().
    """
    if booking_kwargs is None:
        booking_kwargs = {}

    if approval_decisions is None:
        approval_decisions = {
            AffiliationEnum.INGEBORG: DecisionEnum.NO_RESPONSE,
            AffiliationEnum.CORNELIA: DecisionEnum.NO_RESPONSE,
            AffiliationEnum.ANGELIKA: DecisionEnum.NO_RESPONSE,
        }

    # Create booking
    booking = make_booking(**booking_kwargs)

    # Note: booking.id will be None until flushed to database
    # Approvals should be created after flush/commit

    # Create approvals (will need to set booking_id after flush)
    approvals = [
        make_approval(
            party=party,
            decision=decision,
            decided_at=get_now() if decision != DecisionEnum.NO_RESPONSE else None,
        )
        for party, decision in approval_decisions.items()
    ]

    return booking, approvals

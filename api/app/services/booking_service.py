"""Booking business logic service."""

from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval import Approval
from app.models.booking import Booking
from app.models.enums import AffiliationEnum, DecisionEnum, StatusEnum
from app.models.timeline_event import TimelineEvent
from app.repositories.approval_repository import ApprovalRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.timeline_repository import TimelineRepository
from app.schemas.booking import BookingCreate

BERLIN_TZ = ZoneInfo("Europe/Berlin")

# Fixed approver emails per BR-003
APPROVER_EMAILS = {
    AffiliationEnum.INGEBORG: "ingeborg@example.com",
    AffiliationEnum.CORNELIA: "cornelia@example.com",
    AffiliationEnum.ANGELIKA: "angelika@example.com",
}


class BookingService:
    """Service for booking business logic."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with database session."""
        self.session = session
        self.booking_repo = BookingRepository(session)
        self.approval_repo = ApprovalRepository(session)
        self.timeline_repo = TimelineRepository(session)

    async def create_booking(self, booking_data: BookingCreate) -> Booking:
        """
        Create a new booking with 3 approvals.

        Business Rules:
        - BR-001: Calculate total_days = (end_date - start_date) + 1
        - BR-002: Check conflicts with Pending/Confirmed bookings
        - BR-003: Create 3 approval records (Ingeborg, Cornelia, Angelika)
        - BR-015: Self-approval if requester is an approver
        - BR-029: Transaction ensures first-write-wins

        Args:
            booking_data: Validated booking creation data

        Returns:
            Created booking with approvals

        Raises:
            ValueError: If date conflicts exist
        """
        # BR-001: Calculate total_days (inclusive end date)
        total_days = (booking_data.end_date - booking_data.start_date).days + 1

        # BR-002: Check conflicts with Pending/Confirmed bookings
        conflicts = await self.booking_repo.check_conflicts(
            start_date=booking_data.start_date,
            end_date=booking_data.end_date,
        )

        if conflicts:
            conflict = conflicts[0]
            status_map = {
                StatusEnum.PENDING: "Ausstehend",
                StatusEnum.CONFIRMED: "Bestätigt",
            }
            status_german = status_map.get(conflict.status, str(conflict.status.value))
            raise ValueError(
                f"Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung "
                f"({conflict.requester_first_name} – {status_german})."
            )

        # Create booking entity
        # Note: timestamps are timezone-naive but implicitly Europe/Berlin
        now = datetime.now(BERLIN_TZ).replace(tzinfo=None)
        booking = Booking(
            requester_first_name=booking_data.requester_first_name,
            requester_email=booking_data.requester_email,
            start_date=booking_data.start_date,
            end_date=booking_data.end_date,
            total_days=total_days,
            party_size=booking_data.party_size,
            affiliation=booking_data.affiliation,
            description=booking_data.description,
            status=StatusEnum.PENDING,
            created_at=now,
            updated_at=now,
            last_activity_at=now,
        )

        # Save booking (generates ID)
        booking = await self.booking_repo.create(booking)

        # BR-003: Create 3 approval records
        # BR-015: Auto-approve if requester is an approver
        requester_email = booking_data.requester_email.lower()

        for party, approver_email in APPROVER_EMAILS.items():
            # Check for self-approval
            is_self_approval = requester_email == approver_email.lower()

            approval = Approval(
                booking_id=booking.id,
                party=party,
                decision=DecisionEnum.APPROVED if is_self_approval else DecisionEnum.NO_RESPONSE,
                decided_at=now if is_self_approval else None,
                comment=None,
            )

            await self.approval_repo.create(approval)

            # Create timeline event for self-approval
            if is_self_approval:
                timeline_event = TimelineEvent(
                    booking_id=booking.id,
                    when=now,
                    actor=booking.requester_first_name,
                    event_type="SelfApproved",
                    note=f"{party.value} (self-approval)",
                )
                await self.timeline_repo.create(timeline_event)

        # Create initial timeline event
        timeline_event = TimelineEvent(
            booking_id=booking.id,
            when=booking.created_at,
            actor=booking.requester_first_name,
            event_type="Created",
            note=None,
        )
        await self.timeline_repo.create(timeline_event)

        # Commit transaction
        await self.session.commit()

        # Reload with approvals
        reloaded_booking = await self.booking_repo.get_with_approvals(booking.id)
        if reloaded_booking is None:
            raise RuntimeError("Booking not found after creation")

        return reloaded_booking

    async def get_booking(self, booking_id: UUID) -> Booking | None:
        """
        Get booking by ID with approvals and timeline events.

        Args:
            booking_id: UUID of the booking

        Returns:
            Booking with related data, or None if not found
        """
        return await self.booking_repo.get_with_approvals(booking_id)

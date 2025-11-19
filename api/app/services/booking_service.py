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
from app.schemas.booking import BookingCancel, BookingCreate, BookingUpdate

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

    async def update_booking(
        self,
        booking_id: UUID,
        booking_data: BookingUpdate,
        requester_email: str,
    ) -> Booking:
        """
        Update an existing booking with BR-005 approval reset logic.

        Business Rules:
        - BR-001: Recalculate total_days if dates change
        - BR-002: Check conflicts excluding current booking
        - BR-005: CRITICAL - Extend resets approvals, shorten keeps approvals
        - BR-014: Cannot edit past bookings (end_date < today)
        - BR-025: First name edits don't create timeline events
        - BR-026: Future horizon validation
        - BR-029: Optimistic locking via transaction

        Args:
            booking_id: UUID of the booking to update
            booking_data: Validated update data (partial updates allowed)
            requester_email: Email from verified token

        Returns:
            Updated booking with related data

        Raises:
            ValueError: If validation fails or conflicts exist
        """
        # Get existing booking
        booking = await self.booking_repo.get_with_approvals(booking_id)
        if booking is None:
            raise ValueError("Der Eintrag konnte leider nicht gefunden werden.")

        # Verify requester owns this booking
        if booking.requester_email.lower() != requester_email.lower():
            raise ValueError("Du hast keinen Zugriff auf diesen Eintrag.")

        # BR-014: Cannot edit past bookings (end_date < today)
        today = datetime.now(BERLIN_TZ).date()
        if booking.end_date < today:
            raise ValueError(
                "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."
            )

        # Store original dates for BR-005 logic
        original_start = booking.start_date
        original_end = booking.end_date

        # Apply updates (only fields that are not None)
        updates_applied = {}
        if booking_data.requester_first_name is not None:
            booking.requester_first_name = booking_data.requester_first_name
            updates_applied["first_name"] = True
        if booking_data.start_date is not None:
            booking.start_date = booking_data.start_date
            updates_applied["start_date"] = True
        if booking_data.end_date is not None:
            booking.end_date = booking_data.end_date
            updates_applied["end_date"] = True
        if booking_data.party_size is not None:
            booking.party_size = booking_data.party_size
            updates_applied["party_size"] = True
        if booking_data.affiliation is not None:
            booking.affiliation = booking_data.affiliation
            updates_applied["affiliation"] = True
        if booking_data.description is not None:
            booking.description = booking_data.description
            updates_applied["description"] = True

        # Validate dates if changed
        if booking_data.start_date is not None or booking_data.end_date is not None:
            # BR-001: End must be >= start
            if booking.end_date < booking.start_date:
                raise ValueError("Ende darf nicht vor dem Start liegen.")

            # BR-014: end_date >= today
            if booking.end_date < today:
                raise ValueError(
                    "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."
                )

            # BR-026: Future horizon
            from dateutil.relativedelta import relativedelta

            future_limit = today + relativedelta(months=18)
            if booking.start_date > future_limit:
                raise ValueError(
                    "Anfragen dürfen nur maximal 18 Monate im Voraus gestellt werden."
                )

            # BR-001: Recalculate total_days
            booking.total_days = (booking.end_date - booking.start_date).days + 1

            # BR-002: Check conflicts excluding current booking
            conflicts = await self.booking_repo.check_conflicts(
                start_date=booking.start_date,
                end_date=booking.end_date,
                exclude_booking_id=booking_id,
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

        # BR-005: Approval reset logic (CRITICAL)
        # Determine if this is an extend or shorten
        dates_changed = (
            booking_data.start_date is not None or booking_data.end_date is not None
        )

        if dates_changed:
            # Check if this is an EXTEND (earlier start or later end)
            is_extend = (
                booking.start_date < original_start or booking.end_date > original_end
            )

            if is_extend:
                # BR-005: EXTEND → Reset all approvals to NoResponse
                approvals = await self.approval_repo.list_by_booking(booking_id)
                for approval in approvals:
                    approval.decision = DecisionEnum.NO_RESPONSE
                    approval.decided_at = None
                    approval.comment = None

                # Note: Email notifications would be sent here in Phase 4

            # Create timeline event for date changes (not for first name per BR-025)
            # Format: "01.–05.08. → 03.–08.08."
            if "start_date" in updates_applied or "end_date" in updates_applied:
                old_dates = f"{original_start.strftime('%d.–%d.%m.%Y').replace('.–', '.')[:3]}–{original_end.strftime('%d.%m.%Y')}"
                new_dates = f"{booking.start_date.strftime('%d.–%d.%m.%Y').replace('.–', '.')[:3]}–{booking.end_date.strftime('%d.%m.%Y')}"

                now = datetime.now(BERLIN_TZ).replace(tzinfo=None)
                timeline_event = TimelineEvent(
                    booking_id=booking.id,
                    when=now,
                    actor=booking.requester_first_name,
                    event_type="Edited",
                    note=f"Dates: {old_dates} → {new_dates}",
                )
                await self.timeline_repo.create(timeline_event)

        # BR-025: First name changes do NOT create timeline events
        # (already handled by checking updates_applied above)

        # Update timestamps
        now = datetime.now(BERLIN_TZ).replace(tzinfo=None)
        booking.updated_at = now
        booking.last_activity_at = now

        # Commit transaction (BR-029: optimistic locking via DB transaction)
        await self.session.commit()

        # Reload with fresh approvals
        reloaded_booking = await self.booking_repo.get_with_approvals(booking_id)
        if reloaded_booking is None:
            raise RuntimeError("Booking not found after update")

        return reloaded_booking

    async def cancel_booking(
        self,
        booking_id: UUID,
        cancel_data: BookingCancel,
        requester_email: str,
    ) -> str:
        """
        Cancel an existing booking.

        Business Rules:
        - BR-006: Pending bookings can be canceled without comment
        - BR-007: Confirmed bookings require comment
        - BR-014: Cannot cancel past bookings (end_date < today)
        - State validation: Only Pending/Confirmed can be canceled

        Args:
            booking_id: UUID of the booking to cancel
            cancel_data: Validated cancel data (optional comment)
            requester_email: Email from verified token

        Returns:
            Success message in German

        Raises:
            ValueError: If validation fails or state invalid
        """
        # Get existing booking
        booking = await self.booking_repo.get_with_approvals(booking_id)
        if booking is None:
            raise ValueError("Der Eintrag konnte leider nicht gefunden werden.")

        # Verify requester owns this booking
        if booking.requester_email.lower() != requester_email.lower():
            raise ValueError("Du hast keinen Zugriff auf diesen Eintrag.")

        # BR-014: Cannot cancel past bookings (end_date < today)
        today = datetime.now(BERLIN_TZ).date()
        if booking.end_date < today:
            raise ValueError(
                "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."
            )

        # State validation: Can only cancel Pending or Confirmed bookings
        if booking.status == StatusEnum.DENIED:
            raise ValueError("Eine abgelehnte Anfrage kann nicht storniert werden.")

        if booking.status == StatusEnum.CANCELED:
            # Idempotent: Already canceled, return success message
            return "Anfrage storniert. Benachrichtigt: Ingeborg, Cornelia und Angelika."

        # BR-007: Confirmed bookings require comment
        if booking.status == StatusEnum.CONFIRMED:
            if not cancel_data.comment:
                raise ValueError("Bitte gib einen kurzen Grund an.")

        # Update status to Canceled
        booking.status = StatusEnum.CANCELED

        # Create timeline event
        now = datetime.now(BERLIN_TZ).replace(tzinfo=None)
        event_note = None
        if cancel_data.comment:
            event_note = f"Comment: {cancel_data.comment}"

        timeline_event = TimelineEvent(
            booking_id=booking.id,
            when=now,
            actor=booking.requester_first_name,
            event_type="Canceled",
            note=event_note,
        )
        await self.timeline_repo.create(timeline_event)

        # Update timestamps
        booking.updated_at = now
        booking.last_activity_at = now

        # Commit transaction
        await self.session.commit()

        # Note: Email notifications would be sent here in Phase 4
        # Notified: requester + 3 approvers (4 emails total)

        # Return German success message
        return "Anfrage storniert. Benachrichtigt: Ingeborg, Cornelia und Angelika."

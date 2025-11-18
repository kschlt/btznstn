"""Booking repository for data access."""

from calendar import monthrange
from collections.abc import Sequence
from datetime import date
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.booking import Booking
from app.models.enums import StatusEnum


class BookingRepository:
    """Repository for booking data access operations."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self.session = session

    async def create(self, booking: Booking) -> Booking:
        """
        Create a new booking.

        Args:
            booking: Booking instance to create

        Returns:
            Created booking with ID
        """
        self.session.add(booking)
        await self.session.flush()
        await self.session.refresh(booking)
        return booking

    async def get(self, booking_id: UUID) -> Booking | None:
        """
        Get booking by ID.

        Args:
            booking_id: Booking UUID

        Returns:
            Booking if found, None otherwise
        """
        result = await self.session.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        return result.scalar_one_or_none()

    async def get_with_approvals(self, booking_id: UUID) -> Booking | None:
        """
        Get booking with approvals and timeline events eagerly loaded.

        Args:
            booking_id: Booking UUID

        Returns:
            Booking with approvals and timeline events loaded, None if not found
        """
        result = await self.session.execute(
            select(Booking)
            .where(Booking.id == booking_id)
            .options(
                selectinload(Booking.approvals),
                selectinload(Booking.timeline_events),
            )
        )
        return result.scalar_one_or_none()

    async def update(self, booking: Booking) -> Booking:
        """
        Update an existing booking.

        Args:
            booking: Booking instance with updated fields

        Returns:
            Updated booking
        """
        await self.session.flush()
        await self.session.refresh(booking)
        return booking

    async def delete(self, booking: Booking) -> None:
        """
        Delete a booking (cascades to approvals and timeline events).

        Args:
            booking: Booking to delete
        """
        await self.session.delete(booking)
        await self.session.flush()

    async def list_for_calendar(
        self, month: int, year: int
    ) -> Sequence[Booking]:
        """
        List bookings that overlap with the specified month.

        A booking overlaps with the month if:
        - booking.start_date <= month_end AND booking.end_date >= month_start

        Only returns Pending and Confirmed bookings (BR-004: Denied not public).
        Eager loads approvals to avoid N+1 queries.
        Orders by start_date.

        Args:
            month: Month number (1-12)
            year: Year

        Returns:
            List of bookings that overlap with the calendar month
        """
        # Get first and last day of month
        month_start = date(year, month, 1)
        _, last_day = monthrange(year, month)
        month_end = date(year, month, last_day)

        result = await self.session.execute(
            select(Booking)
            .where(
                and_(
                    Booking.status.in_([StatusEnum.PENDING, StatusEnum.CONFIRMED]),
                    Booking.start_date <= month_end,  # Starts on or before month end
                    Booking.end_date >= month_start,  # Ends on or after month start
                )
            )
            .options(selectinload(Booking.approvals))  # Avoid N+1 queries
            .order_by(Booking.start_date)
        )
        return result.scalars().all()

    async def check_conflicts(
        self,
        start_date: date,
        end_date: date,
        exclude_booking_id: UUID | None = None,
    ) -> Sequence[Booking]:
        """
        Check for date range conflicts (BR-002: No overlaps with Pending/Confirmed).

        Uses GiST index on daterange for performance.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            exclude_booking_id: Optional booking ID to exclude (for edits)

        Returns:
            List of conflicting bookings
        """
        # Build base query for conflicting bookings
        # Only Pending and Confirmed bookings block dates (BR-004)
        query = select(Booking).where(
            and_(
                Booking.status.in_([StatusEnum.PENDING, StatusEnum.CONFIRMED]),
                # Date range overlap: (start1 <= end2) AND (end1 >= start2)
                Booking.start_date <= end_date,
                Booking.end_date >= start_date,
            )
        )

        # Exclude specific booking (for edit operations)
        if exclude_booking_id is not None:
            query = query.where(Booking.id != exclude_booking_id)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_by_requester_email(
        self, email: str, limit: int = 50
    ) -> Sequence[Booking]:
        """
        List bookings by requester email.

        Per BR-023: Sorted by LastActivityAt desc (most recent activity first).

        Args:
            email: Requester email address
            limit: Maximum number of bookings to return

        Returns:
            List of bookings for the requester, sorted by last activity
        """
        result = await self.session.execute(
            select(Booking)
            .where(Booking.requester_email == email)
            .order_by(Booking.last_activity_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

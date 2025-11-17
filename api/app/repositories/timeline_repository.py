"""Timeline event repository for data access."""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.timeline_event import TimelineEvent


class TimelineRepository:
    """Repository for timeline event data access operations."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self.session = session

    async def create(self, event: TimelineEvent) -> TimelineEvent:
        """
        Create a new timeline event.

        Args:
            event: TimelineEvent instance to create

        Returns:
            Created event with ID
        """
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def get(self, event_id: UUID) -> TimelineEvent | None:
        """
        Get timeline event by ID.

        Args:
            event_id: Event UUID

        Returns:
            Event if found, None otherwise
        """
        result = await self.session.execute(
            select(TimelineEvent).where(TimelineEvent.id == event_id)
        )
        return result.scalar_one_or_none()

    async def list_by_booking(
        self, booking_id: UUID, limit: int | None = None
    ) -> Sequence[TimelineEvent]:
        """
        List timeline events for a booking.

        Args:
            booking_id: Booking UUID
            limit: Optional maximum number of events to return

        Returns:
            List of timeline events, ordered by when (newest first)
        """
        query = (
            select(TimelineEvent)
            .where(TimelineEvent.booking_id == booking_id)
            .order_by(TimelineEvent.when.desc())
        )

        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

"""Approval repository for data access."""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.approval import Approval
from app.models.booking import Booking
from app.models.enums import AffiliationEnum, DecisionEnum, StatusEnum


class ApprovalRepository:
    """Repository for approval data access operations."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self.session = session

    async def create(self, approval: Approval) -> Approval:
        """
        Create a new approval.

        Args:
            approval: Approval instance to create

        Returns:
            Created approval with ID
        """
        self.session.add(approval)
        await self.session.flush()
        await self.session.refresh(approval)
        return approval

    async def get(self, approval_id: UUID) -> Approval | None:
        """
        Get approval by ID.

        Args:
            approval_id: Approval UUID

        Returns:
            Approval if found, None otherwise
        """
        result = await self.session.execute(
            select(Approval).where(Approval.id == approval_id)
        )
        return result.scalar_one_or_none()

    async def get_by_booking_and_party(
        self, booking_id: UUID, party: AffiliationEnum
    ) -> Approval | None:
        """
        Get approval for specific booking and party.

        Args:
            booking_id: Booking UUID
            party: Approver party (Ingeborg, Cornelia, or Angelika)

        Returns:
            Approval if found, None otherwise
        """
        result = await self.session.execute(
            select(Approval).where(
                Approval.booking_id == booking_id, Approval.party == party
            )
        )
        return result.scalar_one_or_none()

    async def list_by_booking(self, booking_id: UUID) -> Sequence[Approval]:
        """
        List all approvals for a booking.

        Args:
            booking_id: Booking UUID

        Returns:
            List of approvals (always 3 per booking)
        """
        result = await self.session.execute(
            select(Approval)
            .where(Approval.booking_id == booking_id)
            .order_by(Approval.party)
        )
        return result.scalars().all()

    async def update(self, approval: Approval) -> Approval:
        """
        Update an existing approval.

        Args:
            approval: Approval instance with updated fields

        Returns:
            Updated approval
        """
        await self.session.flush()
        await self.session.refresh(approval)
        return approval

    async def list_pending_for_party(
        self, party: AffiliationEnum, limit: int = 50
    ) -> Sequence[Booking]:
        """
        List pending bookings where this party has NoResponse decision.

        Per BR-023: Outstanding items are:
        - Items where this approver = NoResponse
        - Status = Pending
        - Sorted by LastActivityAt desc (most recent activity first)

        Args:
            party: Approver party
            limit: Maximum number to return

        Returns:
            List of bookings awaiting this party's decision
        """
        result = await self.session.execute(
            select(Booking)
            .join(Approval)
            .where(
                and_(
                    Approval.party == party,
                    Approval.decision == DecisionEnum.NO_RESPONSE,
                    Booking.status == StatusEnum.PENDING,
                )
            )
            .options(selectinload(Booking.approvals))  # Eager load approvals
            .order_by(Booking.last_activity_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def list_history_for_party(
        self, party: AffiliationEnum, limit: int = 100
    ) -> Sequence[Booking]:
        """
        List all bookings involving this party (history view).

        Per BR-023: History includes:
        - All items involving this approver
        - All statuses (Pending, Confirmed, Denied, Canceled)
        - Sorted by LastActivityAt desc
        - Read-only view

        Args:
            party: Approver party
            limit: Maximum number to return

        Returns:
            List of all bookings this party has been involved with
        """
        result = await self.session.execute(
            select(Booking)
            .join(Approval)
            .where(Approval.party == party)
            .options(selectinload(Booking.approvals))  # Eager load approvals
            .order_by(Booking.last_activity_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

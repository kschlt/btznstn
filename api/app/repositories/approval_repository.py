"""Approval repository for data access."""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval import Approval
from app.models.enums import AffiliationEnum, DecisionEnum


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
    ) -> Sequence[Approval]:
        """
        List pending approvals for a specific party.

        Args:
            party: Approver party
            limit: Maximum number to return

        Returns:
            List of approvals awaiting decision
        """
        result = await self.session.execute(
            select(Approval)
            .where(
                Approval.party == party,
                Approval.decision == DecisionEnum.NO_RESPONSE,
            )
            .order_by(Approval.id.desc())
            .limit(limit)
        )
        return result.scalars().all()

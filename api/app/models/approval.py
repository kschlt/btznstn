"""Approval model."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import AffiliationEnum, DecisionEnum

if TYPE_CHECKING:
    from app.models.booking import Booking


class Approval(Base):
    """
    Approval decision for a booking.

    Each booking has exactly 3 approval records (one per party: Ingeborg, Cornelia, Angelika).
    """

    __tablename__ = "approvals"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Foreign key to booking (CASCADE delete)
    booking_id: Mapped[UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False
    )

    # Party (approver)
    party: Mapped[AffiliationEnum] = mapped_column(nullable=False)

    # Decision
    decision: Mapped[DecisionEnum] = mapped_column(
        nullable=False, default=DecisionEnum.NO_RESPONSE
    )

    # Comment (required if decision = Denied)
    comment: Mapped[str | None] = mapped_column(nullable=True)

    # Timestamp when decision was made
    decided_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationship
    booking: Mapped["Booking"] = relationship(back_populates="approvals")

    # Constraints
    __table_args__ = (
        UniqueConstraint("booking_id", "party", name="uq_booking_party"),
        Index("idx_approvals_booking", "booking_id"),
        Index("idx_approvals_decision", "decision"),
        Index("idx_approvals_party_decision", "party", "decision"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Approval(id={self.id}, "
            f"party={self.party.value}, "
            f"decision={self.decision.value})>"
        )

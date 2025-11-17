"""Timeline event model."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.booking import Booking


class TimelineEvent(Base):
    """
    Timeline event for audit log.

    Tracks all actions performed on a booking.
    """

    __tablename__ = "timeline_events"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Foreign key to booking (CASCADE delete)
    booking_id: Mapped[UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False
    )

    # Event details
    when: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    actor: Mapped[str] = mapped_column(String(50), nullable=False)  # "Requester" or party name
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "Submitted", etc.
    note: Mapped[str | None] = mapped_column(Text(), nullable=True)  # Optional context

    # Relationship
    booking: Mapped["Booking"] = relationship(back_populates="timeline_events")

    # Constraints
    __table_args__ = (
        Index("idx_timeline_booking", "booking_id"),
        Index("idx_timeline_when", "when", postgresql_ops={"when": "DESC"}),
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<TimelineEvent(id={self.id}, "
            f"event_type={self.event_type}, "
            f"actor={self.actor})>"
        )

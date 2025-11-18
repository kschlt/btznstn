"""Booking model."""

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import AffiliationEnum, StatusEnum

if TYPE_CHECKING:
    from app.models.approval import Approval
    from app.models.timeline_event import TimelineEvent


class Booking(Base):
    """
    Booking/Request entity.

    Represents a whole-day booking request requiring approval from three parties.
    """

    __tablename__ = "bookings"

    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Dates (inclusive end date per BR-001)
    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)
    total_days: Mapped[int] = mapped_column(nullable=False)

    # Party details
    party_size: Mapped[int] = mapped_column(nullable=False)
    affiliation: Mapped[AffiliationEnum] = mapped_column(nullable=False)

    # Requester details (email is not unique - same person can have multiple bookings)
    requester_first_name: Mapped[str] = mapped_column(String(40), nullable=False)
    requester_email: Mapped[str] = mapped_column(String(254), nullable=False)

    # Optional description
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Status
    status: Mapped[StatusEnum] = mapped_column(
        nullable=False, default=StatusEnum.PENDING
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    # Relationships
    approvals: Mapped[list["Approval"]] = relationship(
        back_populates="booking", cascade="all, delete-orphan", lazy="selectin"
    )
    timeline_events: Mapped[list["TimelineEvent"]] = relationship(
        back_populates="booking", cascade="all, delete-orphan", lazy="select"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="check_end_after_start"),
        CheckConstraint(
            "party_size >= 1 AND party_size <= 10", name="check_party_size_range"
        ),
        # Indexes
        Index("idx_bookings_status", "status"),
        Index("idx_bookings_requester_email", "requester_email"),
        Index(
            "idx_bookings_last_activity",
            "last_activity_at",
            postgresql_ops={"last_activity_at": "DESC"},
        ),
        # GiST index for date range overlap detection (BR-002, BR-029)
        Index(
            "idx_bookings_date_range",
            func.daterange(start_date, end_date, "[]"),
            postgresql_using="gist",
        ),
    )

    def compute_total_days(self) -> int:
        """
        Calculate total days between start and end date (inclusive).

        Per BR-001: End date is inclusive, so Jan 1-3 covers 3 days (1, 2, 3).

        Returns:
            int: Number of days (end - start + 1)
        """
        return (self.end_date - self.start_date).days + 1

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Booking(id={self.id}, "
            f"{self.start_date.strftime('%Y-%m-%d')}-{self.end_date.strftime('%Y-%m-%d')}, "
            f"status={self.status.value})>"
        )

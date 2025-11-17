"""Approver party model."""

from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import AffiliationEnum


class ApproverParty(Base):
    """
    Approver party configuration.

    Seed data for the three fixed approvers (BR-003).
    Email addresses can be updated in the database for flexibility.
    """

    __tablename__ = "approver_parties"

    # Primary key (enum value)
    party: Mapped[AffiliationEnum] = mapped_column(primary_key=True)

    # Email address (unique, can be updated)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)

    # Notification enabled flag
    notification_enabled: Mapped[bool] = mapped_column(
        nullable=False, default=True, server_default="true"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<ApproverParty(party={self.party.value}, email={self.email})>"

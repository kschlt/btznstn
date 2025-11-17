"""Database enums for the booking system."""

import enum


class AffiliationEnum(str, enum.Enum):
    """Affiliation/party enum (BR-003: Three fixed approvers)."""

    INGEBORG = "Ingeborg"
    CORNELIA = "Cornelia"
    ANGELIKA = "Angelika"


class StatusEnum(str, enum.Enum):
    """Booking status enum."""

    PENDING = "Pending"
    DENIED = "Denied"
    CONFIRMED = "Confirmed"
    CANCELED = "Canceled"


class DecisionEnum(str, enum.Enum):
    """Approval decision enum."""

    NO_RESPONSE = "NoResponse"
    APPROVED = "Approved"
    DENIED = "Denied"

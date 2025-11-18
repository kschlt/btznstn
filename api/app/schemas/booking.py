"""Pydantic schemas for booking endpoints."""

import re
from datetime import date, datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.models.enums import AffiliationEnum, StatusEnum

# Timezone for date calculations per BR-014, BR-026
BERLIN_TZ = ZoneInfo("Europe/Berlin")

# Business rule constants
MAX_PARTY_SIZE = 10  # BR-017
MAX_FIRST_NAME_LENGTH = 40  # BR-019
MAX_DESCRIPTION_LENGTH = 500  # BR-020
FUTURE_HORIZON_MONTHS = 18  # BR-026
LONG_STAY_DAYS = 7  # BR-027

# Validation patterns
FIRST_NAME_PATTERN = re.compile(r"^[A-Za-zÀ-ÿ '\-]+$")  # BR-019 (space, not \s to exclude newlines)
LINK_PATTERNS = [
    re.compile(r"https?://", re.IGNORECASE),  # http:// or https://
    re.compile(r"www\.", re.IGNORECASE),  # www.
    re.compile(r"mailto:", re.IGNORECASE),  # mailto:
]


class BookingCreate(BaseModel):
    """
    Schema for creating a new booking (POST /api/v1/bookings).

    Validates:
    - BR-001: Inclusive end date (end >= start)
    - BR-014: No past dates (end_date >= today)
    - BR-017: Party size 1-10
    - BR-019: First name validation (letters, diacritics, space, hyphen, apostrophe; max 40)
    - BR-020: Link detection in description
    - BR-026: Future horizon (start_date <= today + 18 months)
    - BR-027: Long stay warning (total_days > 7)
    """

    requester_first_name: str = Field(
        ...,
        min_length=1,
        max_length=MAX_FIRST_NAME_LENGTH,
        description="Requester's first name (trimmed, validated per BR-019)",
    )
    requester_email: EmailStr = Field(
        ..., description="Requester's email (private, not returned in public responses)"
    )
    start_date: date = Field(..., description="Start date (inclusive)")
    end_date: date = Field(..., description="End date (inclusive per BR-001)")
    party_size: int = Field(
        ..., ge=1, le=MAX_PARTY_SIZE, description=f"Number of people (1-{MAX_PARTY_SIZE})"
    )
    affiliation: AffiliationEnum = Field(
        ..., description="Visual affiliation (does not affect approval requirements)"
    )
    description: str | None = Field(
        None,
        max_length=MAX_DESCRIPTION_LENGTH,
        description="Optional description (max 500 chars, no links per BR-020)",
    )
    long_stay_confirmed: bool = Field(
        False,
        description="User acknowledged long stay warning (BR-027: total_days > 7)",
    )

    @field_validator("requester_first_name")
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        """
        Validate first name per BR-019.

        Rules:
        - Trim whitespace
        - Letters, diacritics, space, hyphen, apostrophe only
        - Max 40 characters
        - No emojis, newlines, or special characters
        """
        # Trim whitespace
        v = v.strip()

        if not v:
            raise ValueError(
                "Bitte gib einen gültigen Vornamen an (Buchstaben, Leerzeichen, "
                "Bindestrich, Apostroph; max. 40 Zeichen)."
            )

        if len(v) > MAX_FIRST_NAME_LENGTH:
            raise ValueError(
                "Bitte gib einen gültigen Vornamen an (Buchstaben, Leerzeichen, "
                "Bindestrich, Apostroph; max. 40 Zeichen)."
            )

        if not FIRST_NAME_PATTERN.match(v):
            raise ValueError(
                "Bitte gib einen gültigen Vornamen an (Buchstaben, Leerzeichen, "
                "Bindestrich, Apostroph; max. 40 Zeichen)."
            )

        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """
        Validate description per BR-020.

        Rules:
        - Max 500 characters
        - No links (http://, https://, www, mailto:) - case insensitive
        """
        if v is None:
            return v

        if len(v) > MAX_DESCRIPTION_LENGTH:
            raise ValueError(f"Text ist zu lang (max. {MAX_DESCRIPTION_LENGTH} Zeichen).")

        # Check for links (case-insensitive)
        for pattern in LINK_PATTERNS:
            if pattern.search(v):
                raise ValueError(
                    "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden."
                )

        return v

    @model_validator(mode="after")
    def validate_dates(self) -> "BookingCreate":
        """
        Validate date logic per BR-001, BR-014, BR-026, BR-027.

        Validations:
        - BR-001: end_date >= start_date
        - BR-014: end_date >= today (Europe/Berlin)
        - BR-026: start_date <= today + 18 months (Europe/Berlin)
        - BR-027: Warn if total_days > 7 and not confirmed
        """
        # Get today in Berlin timezone
        today = datetime.now(BERLIN_TZ).date()

        # BR-001: End must be >= start
        if self.end_date < self.start_date:
            raise ValueError("Ende darf nicht vor dem Start liegen.")

        # BR-014: No past bookings (end_date >= today)
        if self.end_date < today:
            raise ValueError(
                "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."
            )

        # BR-026: Future horizon (start_date <= today + 18 months)
        from dateutil.relativedelta import relativedelta

        future_limit = today + relativedelta(months=FUTURE_HORIZON_MONTHS)
        if self.start_date > future_limit:
            raise ValueError(
                f"Anfragen dürfen nur maximal {FUTURE_HORIZON_MONTHS} Monate "
                "im Voraus gestellt werden."
            )

        # BR-027: Long stay warning (total_days > 7)
        total_days = (self.end_date - self.start_date).days + 1  # Inclusive per BR-001
        if total_days > LONG_STAY_DAYS and not self.long_stay_confirmed:
            raise ValueError(
                f"Die Anfrage ist für {total_days} Tage. "
                "Bitte bestätige, dass du einen längeren Aufenthalt planst."
            )

        return self


class ApprovalResponse(BaseModel):
    """Approval information in booking response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    party: AffiliationEnum
    decision: str  # DecisionEnum as string
    decided_at: datetime | None
    comment: str | None


class BookingResponse(BaseModel):
    """
    Schema for booking responses (POST /api/v1/bookings, GET /api/v1/bookings/{id}).

    Privacy (BR-011):
    - Excludes requester_email (only visible with valid token)
    - Includes public fields for calendar display
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    requester_first_name: str
    start_date: date
    end_date: date
    total_days: int  # Calculated per BR-001: (end - start) + 1
    party_size: int
    affiliation: AffiliationEnum
    description: str | None
    status: StatusEnum
    created_at: datetime
    updated_at: datetime
    last_activity_at: datetime

    # Related data (included in authenticated responses)
    approvals: list[ApprovalResponse] | None = None


class PublicBookingResponse(BaseModel):
    """
    Schema for public booking view (GET without token).

    Privacy (BR-004):
    - Excludes: requester_email, description, approvals, timeline
    - Only shows data needed for public calendar
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    requester_first_name: str
    start_date: date
    end_date: date
    total_days: int
    party_size: int
    affiliation: AffiliationEnum
    status: StatusEnum
    is_past: bool  # Calculated per BR-014: end_date < today (Europe/Berlin)

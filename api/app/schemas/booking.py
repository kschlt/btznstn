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


class BookingUpdate(BaseModel):
    """
    Schema for updating an existing booking (PATCH /api/v1/bookings/{id}).

    All fields are optional (partial updates allowed).

    Validates:
    - BR-005: Date extend vs shorten logic (handled in service layer)
    - BR-014: No past dates (end_date >= today)
    - BR-017: Party size 1-10
    - BR-019: First name validation
    - BR-020: Link detection in description
    - BR-025: First name edits don't reset approvals or create timeline events
    - BR-026: Future horizon
    """

    requester_first_name: str | None = Field(
        None,
        min_length=1,
        max_length=MAX_FIRST_NAME_LENGTH,
        description="Requester's first name (trimmed, validated per BR-019)",
    )
    start_date: date | None = Field(None, description="Start date (inclusive)")
    end_date: date | None = Field(None, description="End date (inclusive per BR-001)")
    party_size: int | None = Field(
        None, ge=1, le=MAX_PARTY_SIZE, description=f"Number of people (1-{MAX_PARTY_SIZE})"
    )
    affiliation: AffiliationEnum | None = Field(
        None, description="Visual affiliation (does not affect approval requirements)"
    )
    description: str | None = Field(
        None,
        max_length=MAX_DESCRIPTION_LENGTH,
        description="Optional description (max 500 chars, no links per BR-020)",
    )

    @field_validator("requester_first_name")
    @classmethod
    def validate_first_name(cls, v: str | None) -> str | None:
        """Validate first name per BR-019 (same as BookingCreate)."""
        if v is None:
            return v

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
        """Validate description per BR-020 (same as BookingCreate)."""
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


class BookingCancel(BaseModel):
    """
    Schema for canceling a booking (DELETE /api/v1/bookings/{id}).

    Validates:
    - BR-007: Comment required for Confirmed bookings
    - BR-020: Link detection in comment
    """

    comment: str | None = Field(
        None,
        min_length=1,
        max_length=500,
        description="Optional comment for Pending, required for Confirmed (BR-007)",
    )

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, v: str | None) -> str | None:
        """Validate comment per BR-020 (no links)."""
        if v is None:
            return v

        # Trim whitespace
        v = v.strip()

        if not v:
            return None  # Treat empty as None

        if len(v) > 500:
            raise ValueError("Text ist zu lang (max. 500 Zeichen).")

        # Check for links (case-insensitive) per BR-020
        for pattern in LINK_PATTERNS:
            if pattern.search(v):
                raise ValueError(
                    "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden."
                )

        return v


class CancelResponse(BaseModel):
    """Response for successful booking cancellation."""

    message: str = Field(..., description="Success message in German")


class ApprovalResponse(BaseModel):
    """Approval information in booking response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    party: AffiliationEnum
    decision: str  # DecisionEnum as string
    decided_at: datetime | None
    comment: str | None


class TimelineEventResponse(BaseModel):
    """Timeline event information in booking response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    when: datetime
    actor: str  # First name of person who performed action
    event_type: str  # "Created", "SelfApproved", "Approved", "Denied", etc.
    note: str | None


class BookingResponse(BaseModel):
    """
    Schema for authenticated booking responses (GET /api/v1/bookings/{id} with token).

    Full details including approvals and timeline for requester/approver access.

    Privacy (BR-011):
    - Excludes requester_email (not exposed in any response)
    - Includes all other fields + approvals + timeline_events
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
    is_past: bool  # Calculated per BR-014: end_date < today (Europe/Berlin)

    # Related data (included in authenticated responses)
    approvals: list[ApprovalResponse]
    timeline_events: list[TimelineEventResponse]


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

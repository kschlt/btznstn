"""Booking API endpoints."""

from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.tokens import verify_token
from app.schemas.booking import BookingCreate, BookingResponse, BookingUpdate, PublicBookingResponse
from app.services.booking_service import BookingService

router = APIRouter(prefix="/api/v1/bookings", tags=["bookings"])


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new booking",
    description="""
    Create a new booking request.

    Business Rules:
    - BR-001: Inclusive end date calculation
    - BR-002: Conflict detection with Pending/Confirmed bookings
    - BR-003: Creates 3 approval records (Ingeborg, Cornelia, Angelika)
    - BR-011: German error messages
    - BR-014: No past dates
    - BR-015: Self-approval if requester is an approver
    - BR-017: Party size 1-10
    - BR-019: First name validation
    - BR-020: No links in description
    - BR-026: Future horizon (18 months)
    - BR-027: Long stay warning (> 7 days)
    - BR-029: First-write-wins for concurrent requests

    Privacy:
    - Response excludes requester_email (public view)
    """,
)
async def create_booking(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:
    """
    Create a new booking.

    Returns:
        201: Booking created successfully
        400: Validation error
        409: Date conflict with existing booking
    """
    service = BookingService(db)

    try:
        booking = await service.create_booking(booking_data)

        # Calculate is_past (BR-014)
        berlin_tz = ZoneInfo("Europe/Berlin")
        today = datetime.now(berlin_tz).date()
        is_past = booking.end_date < today

        # Return response with calculated is_past field
        return BookingResponse(
            id=booking.id,
            requester_first_name=booking.requester_first_name,
            start_date=booking.start_date,
            end_date=booking.end_date,
            party_size=booking.party_size,
            affiliation=booking.affiliation,
            description=booking.description,
            status=booking.status,
            total_days=booking.total_days,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
            last_activity_at=booking.last_activity_at,
            is_past=is_past,
            approvals=list(booking.approvals),
            timeline_events=list(booking.timeline_events),
        )
    except ValueError as e:
        # Business logic errors (conflicts, validation)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT
            if "überschneidet" in str(e)
            else status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ein unerwarteter Fehler ist aufgetreten.",
        ) from e


@router.get(
    "/{booking_id}",
    response_model=BookingResponse | PublicBookingResponse,
    summary="Get booking by ID",
    description="""
    Retrieve a booking by ID.

    Two modes:
    - Public (no token): Limited fields, excludes Denied/Canceled bookings
    - Authenticated (with token): Full details with approvals and timeline

    Business Rules:
    - BR-004: Denied/Canceled bookings return 404 without valid token
    - BR-010: Token validation required for full details
    - BR-014: is_past calculated based on end_date vs today (Europe/Berlin)

    Privacy:
    - Public view: Only public fields (no email, no approvals, no timeline)
    - Authenticated view: Full details including approvals and timeline
    """,
)
async def get_booking(
    booking_id: UUID,
    token: str | None = Query(None, description="Access token for authenticated view"),
    db: AsyncSession = Depends(get_db),
) -> BookingResponse | PublicBookingResponse:
    """
    Get a booking by ID.

    Returns:
        200: Booking details
        401: Invalid token
        403: Token valid but for different booking
        404: Booking not found or inaccessible
    """
    service = BookingService(db)

    # Fetch booking with related data
    booking = await service.get_booking(booking_id)

    # Booking not found
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Der Eintrag konnte leider nicht gefunden werden.",
        )

    # Calculate is_past (BR-014)
    berlin_tz = ZoneInfo("Europe/Berlin")
    today = datetime.now(berlin_tz).date()
    is_past = booking.end_date < today

    # Handle authenticated view (with token)
    if token:
        # Verify token
        payload = verify_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ungültiger Zugangslink.",
            )

        # Check token belongs to this booking
        token_booking_id = payload.get("booking_id")
        if token_booking_id != str(booking_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Du hast keinen Zugriff auf diesen Eintrag.",
            )

        # Return authenticated response with full details
        return BookingResponse(
            id=booking.id,
            requester_first_name=booking.requester_first_name,
            start_date=booking.start_date,
            end_date=booking.end_date,
            party_size=booking.party_size,
            affiliation=booking.affiliation,
            description=booking.description,
            status=booking.status,
            total_days=booking.total_days,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
            last_activity_at=booking.last_activity_at,
            is_past=is_past,
            approvals=list(booking.approvals),
            timeline_events=list(booking.timeline_events),
        )

    # Handle public view (no token)
    # BR-004: Denied/Canceled bookings not visible without token
    if booking.status in ["Denied", "Canceled"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Der Eintrag konnte leider nicht gefunden werden.",
        )

    # Return public response with limited fields
    return PublicBookingResponse(
        id=booking.id,
        requester_first_name=booking.requester_first_name,
        start_date=booking.start_date,
        end_date=booking.end_date,
        party_size=booking.party_size,
        affiliation=booking.affiliation,
        status=booking.status,
        total_days=booking.total_days,
        is_past=is_past,
    )


@router.patch(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Update a booking",
    description="""
    Update an existing booking (requester only).

    Business Rules:
    - BR-001: Recalculate total_days if dates change
    - BR-002: Check conflicts excluding current booking
    - BR-005: CRITICAL - Extend resets approvals, shorten keeps approvals
    - BR-010: Token validation (requester only)
    - BR-014: Cannot edit past bookings (end_date < today)
    - BR-017: Party size 1-10
    - BR-019: First name validation
    - BR-020: No links in description
    - BR-025: First name edits don't create timeline events
    - BR-026: Future horizon (18 months)
    - BR-029: Optimistic locking via transaction

    Privacy:
    - Requires valid requester token (not approver token)
    - Response excludes requester_email
    """,
)
async def update_booking(
    booking_id: UUID,
    booking_data: BookingUpdate,
    token: str = Query(..., description="Requester access token"),
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:
    """
    Update a booking.

    Returns:
        200: Booking updated successfully
        400: Validation error or past booking
        401: Invalid token
        403: Token not for requester or wrong booking
        404: Booking not found
        409: Date conflict with existing booking
    """
    service = BookingService(db)

    # Verify token
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Zugangslink.",
        )

    # Check token is for requester role (not approver)
    token_role = payload.get("role")
    if token_role != "requester":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Du hast keinen Zugriff auf diesen Eintrag.",
        )

    # Check token belongs to this booking
    token_booking_id = payload.get("booking_id")
    if token_booking_id != str(booking_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Du hast keinen Zugriff auf diesen Eintrag.",
        )

    # Extract email from token
    requester_email = payload.get("email")
    if not requester_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Zugangslink.",
        )

    try:
        booking = await service.update_booking(booking_id, booking_data, requester_email)

        # Calculate is_past (BR-014)
        berlin_tz = ZoneInfo("Europe/Berlin")
        today = datetime.now(berlin_tz).date()
        is_past = booking.end_date < today

        # Return response with calculated is_past field
        return BookingResponse(
            id=booking.id,
            requester_first_name=booking.requester_first_name,
            start_date=booking.start_date,
            end_date=booking.end_date,
            party_size=booking.party_size,
            affiliation=booking.affiliation,
            description=booking.description,
            status=booking.status,
            total_days=booking.total_days,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
            last_activity_at=booking.last_activity_at,
            is_past=is_past,
            approvals=list(booking.approvals),
            timeline_events=list(booking.timeline_events),
        )
    except ValueError as e:
        # Business logic errors (validation, conflicts, past bookings)
        error_msg = str(e)

        # Determine appropriate status code
        if "überschneidet" in error_msg:
            status_code = status.HTTP_409_CONFLICT
        elif "zugriff" in error_msg.lower():
            status_code = status.HTTP_403_FORBIDDEN
        elif "nicht gefunden" in error_msg:
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(status_code=status_code, detail=error_msg) from e
    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ein unerwarteter Fehler ist aufgetreten.",
        ) from e

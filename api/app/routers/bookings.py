"""Booking API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.booking import BookingCreate, BookingResponse
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
    db: AsyncSession = Depends(get_db_session),
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
        return BookingResponse.model_validate(booking)
    except ValueError as e:
        # Business logic errors (conflicts, validation)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT
            if "überschneidet" in str(e)
            else status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ein unerwarteter Fehler ist aufgetreten.",
        ) from e

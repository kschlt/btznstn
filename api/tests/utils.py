"""Shared test utilities.

This module contains common helper functions used across all tests.
Import these instead of duplicating code.

Usage:
    from tests.utils import get_today, assert_booking_response_structure, booking_request
"""

from datetime import date, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

BERLIN_TZ = ZoneInfo("Europe/Berlin")


def get_today() -> date:
    """
    Get today's date in Europe/Berlin timezone.

    Use this instead of datetime.now() to ensure consistent timezone handling.

    Returns:
        Current date in Europe/Berlin timezone

    Example:
        >>> today = get_today()
        >>> future_date = today + timedelta(days=10)
    """
    return datetime.now(BERLIN_TZ).date()


def get_now() -> datetime:
    """
    Get current datetime in Europe/Berlin timezone (timezone-naive).

    Returns timezone-naive datetime for database storage.

    Returns:
        Current datetime in Europe/Berlin, with tzinfo removed

    Example:
        >>> now = get_now()
        >>> booking.created_at = now
    """
    return datetime.now(BERLIN_TZ).replace(tzinfo=None)


def booking_request(
    *,
    requester_first_name: str = "Test",
    requester_email: str = "test@example.com",
    start_date: date | None = None,
    end_date: date | None = None,
    party_size: int = 4,
    affiliation: str = "Ingeborg",
    description: str | None = None,
    long_stay_confirmed: bool = False,
) -> dict[str, Any]:
    """
    Build booking creation request payload for API tests.

    This function eliminates 13-line JSON duplication in API tests.
    Use this for ALL POST /api/v1/bookings requests instead of manual JSON dicts.

    Default dates: start = today + 10 days, end = today + 14 days (5 total days)

    Args:
        requester_first_name: First name (default: "Test")
        requester_email: Email address (default: "test@example.com")
        start_date: Start date (default: today + 10 days)
        end_date: End date (default: today + 14 days)
        party_size: Number of people (default: 4)
        affiliation: Affiliation string (default: "Ingeborg")
        description: Optional description (default: None)
        long_stay_confirmed: Long stay confirmation (default: False)

    Returns:
        JSON-serializable dict ready for client.post()

    Example:
        >>> # Test with invalid party size (only 1 line!)
        >>> response = await client.post(
        ...     "/api/v1/bookings",
        ...     json=booking_request(party_size=0)
        ... )
        >>> assert response.status_code == 422

        >>> # Test with custom dates (only 3 lines!)
        >>> response = await client.post(
        ...     "/api/v1/bookings",
        ...     json=booking_request(
        ...         start_date=get_today() - timedelta(days=1),
        ...         end_date=get_today() + timedelta(days=5)
        ...     )
        ... )
    """
    # Default dates: +10 to +14 days (5 total days, no long stay warning)
    today = get_today()
    if start_date is None:
        start_date = today + timedelta(days=10)
    if end_date is None:
        end_date = today + timedelta(days=14)

    return {
        "requester_first_name": requester_first_name,
        "requester_email": requester_email,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "party_size": party_size,
        "affiliation": affiliation,
        "description": description,
        "long_stay_confirmed": long_stay_confirmed,
    }


def assert_booking_response_structure(data: dict[str, Any]) -> None:
    """
    Assert that a booking response has all required public fields.

    Validates the structure of API responses to ensure consistency.
    Also checks that private fields (email) are NOT present.

    Args:
        data: Response JSON from API

    Raises:
        AssertionError: If required fields are missing or private fields are present

    Example:
        >>> response = await client.post("/api/v1/bookings", json={...})
        >>> assert_booking_response_structure(response.json())
    """
    # Required fields in all booking responses
    required_fields = [
        "id",
        "requester_first_name",
        "start_date",
        "end_date",
        "total_days",
        "party_size",
        "affiliation",
        "status",
        "is_past",
    ]

    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Private fields that should NEVER be in public responses
    assert "requester_email" not in data, "Email should not be in response (privacy violation)"


def assert_public_response_structure(data: dict[str, Any]) -> None:
    """
    Assert that a public booking response has ONLY public fields.

    Public responses should NOT include:
    - requester_email
    - description
    - approvals
    - timeline_events
    - created_at, updated_at, last_activity_at

    Args:
        data: Response JSON from public API call (no token)

    Raises:
        AssertionError: If private fields are present

    Example:
        >>> response = await client.get(f"/api/v1/bookings/{booking.id}")
        >>> assert_public_response_structure(response.json())
    """
    # Public fields only
    public_fields = {
        "id",
        "requester_first_name",
        "start_date",
        "end_date",
        "total_days",
        "party_size",
        "affiliation",
        "status",
        "is_past",
    }

    # All fields in response should be public
    for field in data.keys():
        assert field in public_fields, f"Private field '{field}' should not be in public response"

    # Ensure critical private fields are explicitly not present
    private_fields = [
        "requester_email",
        "description",
        "approvals",
        "timeline_events",
        "created_at",
        "updated_at",
        "last_activity_at",
    ]

    for field in private_fields:
        assert field not in data, f"Private field '{field}' leaked in public response"


def assert_authenticated_response_structure(data: dict[str, Any]) -> None:
    """
    Assert that an authenticated booking response has all fields.

    Authenticated responses (with valid token) should include:
    - All public fields
    - approvals
    - timeline_events
    - description
    - created_at, updated_at, last_activity_at

    But still NOT:
    - requester_email (never exposed)

    Args:
        data: Response JSON from authenticated API call (with token)

    Raises:
        AssertionError: If required fields are missing

    Example:
        >>> response = await client.get(
        ...     f"/api/v1/bookings/{booking.id}",
        ...     params={"token": token}
        ... )
        >>> assert_authenticated_response_structure(response.json())
    """
    # All public fields
    required_fields = [
        "id",
        "requester_first_name",
        "start_date",
        "end_date",
        "total_days",
        "party_size",
        "affiliation",
        "status",
        "is_past",
        # Plus authenticated fields
        "approvals",
        "timeline_events",
        "description",
        "created_at",
        "updated_at",
        "last_activity_at",
    ]

    for field in required_fields:
        assert field in data, f"Missing required field in authenticated response: {field}"

    # Email should NEVER be present (even in authenticated responses)
    assert "requester_email" not in data, "Email should not be in any response (privacy violation)"


def assert_german_error(response_data: dict[str, Any], expected_phrase: str) -> None:
    """
    Assert that error message is in German and contains expected phrase.

    Validates BR-011: All error messages must be in German.

    Args:
        response_data: Response JSON from API (expected to be an error)
        expected_phrase: German phrase that should appear in error message

    Raises:
        AssertionError: If error is not in German or doesn't contain phrase

    Example:
        >>> response = await client.get(f"/api/v1/bookings/{uuid4()}")
        >>> assert response.status_code == 404
        >>> assert_german_error(
        ...     response.json(),
        ...     expected_phrase="konnte leider nicht gefunden werden"
        ... )
    """
    assert "detail" in response_data, "Error response should have 'detail' field"

    detail = response_data["detail"]
    assert isinstance(detail, str), "Error detail should be a string"

    # Case-insensitive check for expected phrase
    assert expected_phrase.lower() in detail.lower(), (
        f"Expected German phrase '{expected_phrase}' not found in error message: {detail}"
    )

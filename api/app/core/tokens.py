"""Token generation and validation utilities.

Implements HMAC-SHA256 signed tokens per authentication-flow.md.
Tokens never expire (BR-010).
"""

import base64
import hashlib
import hmac
import json
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from app.core.config import settings

BERLIN_TZ = ZoneInfo("Europe/Berlin")


def generate_token(payload: dict[str, Any]) -> str:
    """
    Generate signed token from payload.

    Args:
        payload: Token payload (email, role, booking_id, party, etc.)

    Returns:
        Base64-encoded token with HMAC-SHA256 signature

    Example payload:
        {
            "email": "user@example.com",
            "role": "requester" | "approver",
            "booking_id": "uuid-string",  # Optional
            "party": "Ingeborg" | "Cornelia" | "Angelika",  # For approver role
        }
    """
    # Add issued-at timestamp
    payload_with_iat = {**payload, "iat": int(datetime.now(BERLIN_TZ).timestamp())}

    # JSON encode (sorted keys for deterministic output)
    message = json.dumps(payload_with_iat, sort_keys=True)

    # Sign with HMAC-SHA256
    signature = hmac.new(
        settings.secret_key.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()

    # Format: base64(message).signature_hex
    message_b64 = base64.urlsafe_b64encode(message.encode()).decode()
    token = f"{message_b64}.{signature}"

    return token


def verify_token(token: str) -> dict[str, Any] | None:
    """
    Verify token signature and extract payload.

    Args:
        token: Token in format base64(message).signature_hex

    Returns:
        Payload dict if valid, None if invalid

    Validation:
        - Split message_b64 and signature_hex (separated by '.')
        - Base64 decode message
        - Verify HMAC-SHA256 signature
        - Parse and return payload
    """
    try:
        # Split token: base64(message).signature_hex
        parts = token.split(".", 1)
        if len(parts) != 2:
            return None

        message_b64, signature_hex = parts

        # Base64 decode message
        message = base64.urlsafe_b64decode(message_b64.encode()).decode()

        # Verify signature using constant-time comparison
        expected_signature = hmac.new(
            settings.secret_key.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(signature_hex, expected_signature):
            return None  # Invalid signature

        # Parse payload
        payload: dict[str, Any] = json.loads(message)
        return payload

    except Exception:
        # Any decode/parsing error = invalid token
        return None

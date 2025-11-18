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
    ).digest()

    # Combine message + signature, base64 encode
    token_bytes = message.encode() + b"." + signature
    token = base64.urlsafe_b64encode(token_bytes).decode()

    return token


def verify_token(token: str) -> dict[str, Any] | None:
    """
    Verify token signature and extract payload.

    Args:
        token: Base64-encoded signed token

    Returns:
        Payload dict if valid, None if invalid

    Validation:
        - Base64 decode
        - Split message and signature
        - Verify HMAC-SHA256 signature
        - Parse and return payload
    """
    try:
        # Base64 decode
        decoded = base64.urlsafe_b64decode(token.encode())

        # Split message and signature (separated by '.')
        parts = decoded.split(b".", 1)
        if len(parts) != 2:
            return None

        message, signature = parts

        # Verify signature using constant-time comparison
        expected_signature = hmac.new(
            settings.secret_key.encode(),
            message,
            hashlib.sha256,
        ).digest()

        if not hmac.compare_digest(signature, expected_signature):
            return None  # Invalid signature

        # Parse payload
        payload: dict[str, Any] = json.loads(message.decode())
        return payload

    except Exception:
        # Any decode/parsing error = invalid token
        return None

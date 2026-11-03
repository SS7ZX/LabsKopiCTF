"""Minimal HMAC JWT implementation for the local weak-secret lab."""

import base64
import hashlib
import hmac
import json


def encode_token(claims: dict[str, str], secret: str) -> str:
    """Encode fixed JSON claims using an HS256 signature."""
    header = _encode_part({"alg": "HS256", "typ": "JWT"})
    payload = _encode_part(claims)
    message = f"{header}.{payload}"
    signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
    return f"{message}.{_encode_bytes(signature)}"


def decode_token(token: str, secret: str, secure: bool = False) -> dict[str, str] | None:
    """Verify an HS256 token with the selected lab secret."""
    try:
        header_part, payload_part, signature_part = token.split(".")
        header = json.loads(_decode_part(header_part))
        if header.get("alg") != "HS256":
            return None
        message = f"{header_part}.{payload_part}"
        signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(_encode_bytes(signature), signature_part):
            return None
        claims = json.loads(_decode_part(payload_part))
        return claims if isinstance(claims, dict) else None
    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def _encode_part(value: dict[str, str]) -> str:
    """Encode a JSON object as an unpadded URL-safe base64 segment."""
    return _encode_bytes(json.dumps(value, separators=(",", ":")).encode())


def _encode_bytes(value: bytes) -> str:
    """Encode bytes as unpadded URL-safe base64."""
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _decode_part(value: str) -> str:
    """Decode an unpadded URL-safe base64 segment."""
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding).decode()

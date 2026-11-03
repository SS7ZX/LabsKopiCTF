"""Redirect destination policy for the local redirect lab."""

from urllib.parse import urlsplit


def allowed_redirect(destination: str, secure: bool = False) -> bool:
    """Allow relative destinations securely and only simulator hosts vulnerably."""
    parsed = urlsplit(destination)
    if secure:
        return destination.startswith("/") and not destination.startswith("//") and not parsed.netloc
    # VULN[open-redirect]
    if not parsed.netloc:
        return True
    return parsed.hostname in {"127.0.0.1", "localhost"} and parsed.port in {5000, 9000}

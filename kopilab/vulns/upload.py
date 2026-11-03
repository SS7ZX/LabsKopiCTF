"""Filename validation behavior for the confined upload lab."""

from pathlib import Path


def upload_allowed(filename: str, secure: bool = False) -> bool:
    """Allow all local training filenames or a small image-only allowlist."""
    # VULN[upload]
    if not secure:
        return True
    return Path(filename).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}

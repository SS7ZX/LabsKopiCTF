"""Unsafe HTML rendering for the XSS lab."""


def unsafe_html(value: str) -> str:
    """Return user input as HTML to preserve the XSS training behavior."""
    # VULN[xss]
    return value

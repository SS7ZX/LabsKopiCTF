"""Loopback-only SSRF behavior for the local training lab."""

from urllib.parse import urlsplit
from urllib.request import ProxyHandler, build_opener


def fetch_internal_url(url: str, host: str, port: int, secure: bool = False) -> str:
    """Fetch the local internal service with stricter secure-mode destination checks."""
    # VULN[ssrf]
    parsed = urlsplit(url)
    if parsed.scheme != "http" or parsed.hostname not in {host, "localhost"}:
        raise ValueError("Lab SSRF hanya boleh menuju service lokal KopiLab")
    if parsed.port != port:
        raise ValueError("Lab SSRF hanya boleh menuju port service internal KopiLab")
    if secure and (parsed.hostname != host or parsed.path not in {"", "/"}):
        raise ValueError("Mode Secure hanya mengizinkan URL service lab yang tepat")
    opener = build_opener(ProxyHandler({}))
    with opener.open(url, timeout=3) as response:
        return response.read(3000).decode(errors="replace")

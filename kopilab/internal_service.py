"""Loopback-only simulated internal service for the SSRF lab."""

from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any

from flask import Flask


class _InternalHandler(BaseHTTPRequestHandler):
    """Return only the SSRF lab's local marker."""

    flag = ""

    def do_GET(self) -> None:
        """Serve the local training secret."""
        body = f"INTERNAL ADMIN SERVICE\n{self.flag}\n".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string: str, *args: Any) -> None:
        """Suppress access logs for this local-only service."""


def start_internal_service(app: Flask, port: int | None = None) -> tuple[HTTPServer, Thread]:
    """Start the SSRF target on loopback in a daemon thread."""
    handler = type(
        "InternalHandler",
        (_InternalHandler,),
        {"flag": app.config["FLAGS"]["ssrf"]},
    )
    server = HTTPServer(
        (app.config["INTERNAL_HOST"], port if port is not None else app.config["INTERNAL_PORT"]),
        handler,
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread

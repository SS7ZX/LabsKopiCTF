"""Shared isolated fixtures for the KopiLab test suite."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from kopilab import create_app
from kopilab.internal_service import start_internal_service


@pytest.fixture
def app(tmp_path: Path) -> Flask:
    """Create an app backed by a fresh temporary database."""
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "pytest-only-session-key",
            "DATABASE": str(tmp_path / "test.db"),
            "FILES_DIR": str(tmp_path / "files"),
            "PROJECT_DIR": str(tmp_path),
            "UPLOADS_DIR": str(tmp_path / "uploads"),
            "INTERNAL_PORT": 5001,
        }
    )


@pytest.fixture
def client(app: Flask) -> Iterator[FlaskClient]:
    """Yield a test client and run its loopback-only internal service."""
    server, thread = start_internal_service(app, port=0)
    app.config["INTERNAL_PORT"] = server.server_address[1]
    with app.test_client() as test_client:
        yield test_client
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)

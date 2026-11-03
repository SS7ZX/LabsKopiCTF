"""Password reset behavior for the predictable-token lab."""

import hashlib
import sqlite3


def reset_token(username: str) -> str:
    """Generate the intentionally predictable reset token."""
    # VULN[reset]
    return hashlib.md5(username.encode()).hexdigest()


def reset_password(connection: sqlite3.Connection, username: str, password: str) -> None:
    """Set a password after the weak reset token has been accepted."""
    # VULN[reset]
    connection.execute("UPDATE users SET password=? WHERE username=?", (password, username))

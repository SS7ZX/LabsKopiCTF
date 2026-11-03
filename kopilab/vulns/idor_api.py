"""User ownership behavior for the IDOR API lab."""

import sqlite3


def get_user(
    connection: sqlite3.Connection, user_id: int, owner_id: int | None = None
) -> sqlite3.Row | None:
    """Load a user, optionally restricting the result to the authenticated owner."""
    if owner_id is not None:
        return connection.execute(
            "SELECT * FROM users WHERE id=? AND id=?", (user_id, owner_id)
        ).fetchone()
    # VULN[idor-api]
    return connection.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()

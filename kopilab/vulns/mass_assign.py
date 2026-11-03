"""Mass assignment behavior for the profile lab."""

import sqlite3
from collections.abc import Iterable


def update_profile(
    connection: sqlite3.Connection,
    fields: Iterable[tuple[str, str]],
    user_id: int,
    secure: bool = False,
) -> None:
    """Apply submitted fields, restricting secure mode to profile attributes."""
    # VULN[mass-assign]
    for name, value in fields:
        if secure and name != "email":
            continue
        connection.execute(f"UPDATE users SET {name}=? WHERE id=?", (value, user_id))

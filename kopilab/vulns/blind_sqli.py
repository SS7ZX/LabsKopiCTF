"""Boolean-only SQLite oracle for the blind SQL injection lab."""

import sqlite3


def evaluate_condition(connection: sqlite3.Connection, condition: str, secure: bool = False) -> bool:
    """Evaluate a vulnerable local boolean expression or reject it securely."""
    if secure:
        return False
    # VULN[blind-sqli]
    row = connection.execute(
        f"SELECT CASE WHEN ({condition}) THEN 1 ELSE 0 END"
    ).fetchone()
    return bool(row[0])

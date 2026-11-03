"""Transfer behavior for the CSRF training lab."""

import sqlite3
import hmac


def transfer_money(connection: sqlite3.Connection, amount: int, sender_id: int, recipient: str) -> None:
    """Transfer funds without a CSRF token or amount validation."""
    # VULN[csrf]
    connection.execute("UPDATE users SET balance=balance-? WHERE id=?", (amount, sender_id))
    connection.execute("UPDATE users SET balance=balance+? WHERE username=?", (amount, recipient))


def valid_csrf_token(expected: str, supplied: str) -> bool:
    """Compare anti-CSRF tokens without leaking early character mismatches."""
    return bool(expected) and hmac.compare_digest(expected, supplied)

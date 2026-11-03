"""Order ownership behavior for the IDOR order lab."""

import sqlite3


def get_order(
    connection: sqlite3.Connection, order_id: int, owner_id: int | None = None
) -> sqlite3.Row | None:
    """Load an order, optionally restricting it to the authenticated owner."""
    if owner_id is not None:
        return connection.execute(
            "SELECT * FROM orders WHERE id=? AND user_id=?", (order_id, owner_id)
        ).fetchone()
    # VULN[idor-order]
    return connection.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()

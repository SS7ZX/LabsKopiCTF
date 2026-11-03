"""Per-player attempt tracking for the weak login rate-limit lab."""

import sqlite3
import time


def record_login_attempt(connection: sqlite3.Connection, player_id: str, secure: bool = False) -> int:
    """Record failed attempts, resetting the counter after a cooldown in secure mode."""
    now = int(time.time())
    row = connection.execute(
        "SELECT attempts,last_attempt FROM login_attempts WHERE player_id=?", (player_id,)
    ).fetchone()
    attempts = row["attempts"] if row else 0
    last_attempt = row["last_attempt"] if row else 0
    if secure and now - last_attempt > 60:
        attempts = 0
    if secure and attempts >= 5:
        return attempts
    # VULN[rate-limit]
    attempts += 1
    connection.execute(
        """INSERT INTO login_attempts(player_id,attempts,last_attempt) VALUES(?,?,?)
           ON CONFLICT(player_id) DO UPDATE SET attempts=excluded.attempts,last_attempt=excluded.last_attempt""",
        (player_id, attempts, now),
    )
    return attempts

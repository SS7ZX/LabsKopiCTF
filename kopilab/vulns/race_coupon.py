"""Coupon redemption behavior for the local race-condition lab."""

import sqlite3
import time


def redeem_coupon(connection: sqlite3.Connection, user_id: int, secure: bool = False) -> int:
    """Redeem a local training coupon with or without an atomic uniqueness check."""
    if secure:
        connection.execute("BEGIN IMMEDIATE")
        existing = connection.execute(
            "SELECT COUNT(*) FROM coupon_redemptions WHERE user_id=? AND coupon='KOPILAB'",
            (user_id,),
        ).fetchone()[0]
        if existing:
            return existing
        connection.execute(
            "INSERT INTO coupon_redemptions(user_id,coupon) VALUES(?,'KOPILAB')",
            (user_id,),
        )
        return 1

    # VULN[race-coupon]
    existing = connection.execute(
        "SELECT COUNT(*) FROM coupon_redemptions WHERE user_id=? AND coupon='KOPILAB'",
        (user_id,),
    ).fetchone()[0]
    time.sleep(0.02)
    connection.execute(
        "INSERT INTO coupon_redemptions(user_id,coupon) VALUES(?,'KOPILAB')",
        (user_id,),
    )
    return existing + 1

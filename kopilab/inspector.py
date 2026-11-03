"""Persist the most recent local request details for the learning inspector."""

from __future__ import annotations

import json
from typing import Any

from flask import g, session

from .db import get_db


def record_query(sql: str) -> None:
    """Keep the final SQL statement available for the current response."""
    g.last_sql = sql


def record_request(response: Any, request: Any, sql: str) -> None:
    """Store the latest request summary and response headers in SQLite."""
    player_id = session.get("player_id")
    if not player_id:
        return
    headers = json.dumps(
        {name: value for name, value in response.headers.items()},
        ensure_ascii=True,
    )
    connection = get_db()
    connection.execute(
        """INSERT INTO request_inspector(player_id,method,path,sql_text,response_headers)
           VALUES(?,?,?,?,?) ON CONFLICT(player_id) DO UPDATE SET
           method=excluded.method,path=excluded.path,sql_text=excluded.sql_text,
           response_headers=excluded.response_headers,created_at=CURRENT_TIMESTAMP""",
        (player_id, request.method, request.full_path, sql, headers),
    )
    connection.commit()

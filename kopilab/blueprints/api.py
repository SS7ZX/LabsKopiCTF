"""JSON API endpoints."""

from flask import Blueprint, current_app, jsonify, session

from .. import require_login
from ..db import get_db
from ..inspector import record_query
from ..vulns.idor_api import get_user

api_bp = Blueprint("api", __name__)


@api_bp.route("/api/user/<int:uid>")
def api_user(uid: int):
    """Return user information through the vulnerable IDOR endpoint."""
    response = require_login()
    if response:
        return response
    owner_id = session.get("uid") if session.get("secure_mode", False) else None
    record_query("SELECT * FROM users WHERE id=?" + (" AND id=?" if owner_id else ""))
    user = get_user(get_db(), uid, owner_id)
    if not user:
        return jsonify(error="not found"), 404
    return jsonify(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        role=user["role"],
        balance=user["balance"],
        api_key=current_app.config["FLAGS"]["idor-api"] if user["role"] == "admin" else None,
    )

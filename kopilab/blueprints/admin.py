"""Admin panel route."""

from flask import Blueprint, current_app, render_template, request, session

from ..db import get_db
from ..vulns.bac_cookie import cookie_is_admin

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
def admin():
    """Render the admin panel using the intentionally trusted cookie."""
    secure = session.get("secure_mode", False)
    role = None
    if secure and session.get("uid"):
        user = get_db().execute("SELECT role FROM users WHERE id=?", (session["uid"],)).fetchone()
        role = user["role"] if user else None
    if not cookie_is_admin(request.cookies.get("admin"), secure=secure, role=role):
        return render_template(
            "error.html", code=403, title="Akses ditolak",
            message="Panel ini hanya tersedia untuk admin.",
        ), 403
    users = get_db().execute("SELECT * FROM users").fetchall()
    return render_template(
        "admin.html",
        users=users,
        flag=current_app.config["FLAGS"]["bac-cookie"],
    )

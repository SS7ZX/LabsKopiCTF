"""Account, profile, transfer, and order history routes."""

from __future__ import annotations

import secrets

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from .. import require_login
from ..db import get_db
from ..vulns.csrf import transfer_money
from ..vulns.mass_assign import update_profile

account_bp = Blueprint("account", __name__)


@account_bp.route("/me")
def me():
    """Show the signed-in account and its training flags."""
    response = require_login()
    if response:
        return response
    user = get_db().execute("SELECT * FROM users WHERE id=?", (session["uid"],)).fetchone()
    flags = []
    if user["username"] == "admin":
        if not session.get("secure_mode", False):
            flags.append(current_app.config["FLAGS"]["sqli-login"])
    elif user["role"] == "admin" and not session.get("secure_mode", False):
        flags.append(current_app.config["FLAGS"]["mass-assign"])
    if user["balance"] >= 10_000_000 and not session.get("secure_mode", False):
        flags.append(current_app.config["FLAGS"]["logic-balance"])
    csrf_token = session.setdefault("csrf_token", secrets.token_urlsafe(32))
    return render_template(
        "account/profile.html", user=user, flags=flags, csrf_token=csrf_token
    )


@account_bp.route("/profile", methods=["POST"])
def profile():
    """Update profile values using the intentionally unsafe mass assignment."""
    response = require_login()
    if response:
        return response
    connection = get_db()
    update_profile(
        connection,
        request.form.items(),
        session["uid"],
        secure=session.get("secure_mode", False),
    )
    connection.commit()
    flash("Profil berhasil diperbarui.", "success")
    return redirect(url_for("account.me"))


@account_bp.route("/transfer", methods=["POST"])
def transfer():
    """Transfer funds without a CSRF token in the vulnerable lab."""
    response = require_login()
    if response:
        return response
    if session.get("secure_mode", False):
        from ..vulns.csrf import valid_csrf_token

        if not valid_csrf_token(
            session.get("csrf_token", ""), request.form.get("csrf_token", "")
        ):
            return render_template(
                "error.html", code=403, title="Token tidak valid",
                message="Transfer ditolak karena token keamanan tidak cocok.",
            ), 403
    amount = int(request.form["amount"])
    connection = get_db()
    transfer_money(connection, amount, session["uid"], request.form["to"])
    connection.commit()
    referrer = request.headers.get("Referer", "")
    flag = current_app.config["FLAGS"]["csrf"] if not session.get("secure_mode", False) else None
    cross_site = referrer and referrer.split("//", 1)[-1].split("/", 1)[0] != request.host
    return render_template(
        "account/transfer_complete.html",
        message="Transfer berhasil.",
        flag=flag if cross_site else None,
    )


@account_bp.route("/orders")
def orders():
    """Show recent orders for the signed-in user."""
    response = require_login()
    if response:
        return response
    rows = get_db().execute(
        "SELECT * FROM orders WHERE user_id=? ORDER BY id DESC", (session["uid"],)
    ).fetchall()
    return render_template("shop/orders.html", orders=rows)

"""Loopback-only endpoints for the additional training labs."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session

from .. import require_login
from ..config import ACADEMY_LAB_IDS
from ..db import get_db
from ..vulns.mass_assign import update_profile
from ..vulns.academy_labs import run_academy_lab, run_final_boss_lab
from ..vulns.blind_sqli import evaluate_condition
from ..vulns.filter_bypass import blocked_username
from ..vulns.jwt_lab import decode_token, encode_token
from ..vulns.open_redirect import allowed_redirect
from ..vulns.race_coupon import redeem_coupon
from ..vulns.rate_limit import record_login_attempt
from ..vulns.upload import upload_allowed

extra_labs_bp = Blueprint("extra_labs", __name__, url_prefix="/extra")


@extra_labs_bp.route("/academy/<lab_id>", methods=["GET", "POST"])
def academy_lab(lab_id: str):
    """Run a bounded advanced lab using only fixed local training fixtures."""
    if lab_id not in ACADEMY_LAB_IDS:
        return jsonify(error="Lab tidak ditemukan."), 404

    if lab_id == "final-boss-ledger-chain":
        outcome = run_final_boss_lab(
            request.values,
            session,
            session.get("uid"),
            secure=session.get("secure_mode", False),
            connection=get_db(),
        )
        outcome["headers"] = {}
    else:
        outcome = run_academy_lab(
            lab_id,
            request.values,
            request.headers,
            session,
            session.get("uid"),
            secure=session.get("secure_mode", False),
        )
    response = jsonify(outcome["data"])
    response.status_code = outcome["status"]
    response.headers.update(outcome["headers"])
    if outcome["finding"] and not session.get("secure_mode", False):
        response.headers["X-Lab-Flag"] = current_app.config["FLAGS"][lab_id]
    return response


@extra_labs_bp.route("/burp-profile", methods=["GET", "POST"])
def burp_profile():
    """Provide an isolated form for the Burp Repeater mass-assignment lab."""
    login_response = require_login()
    if login_response:
        return login_response

    connection = get_db()
    user_id = session["uid"]
    secure = session.get("secure_mode", False)
    if request.method == "GET":
        user = connection.execute(
            "SELECT email,role FROM users WHERE id=?", (user_id,)
        ).fetchone()
        return render_template("labs/burp_profile.html", user=user)

    submitted = request.form
    if not submitted or set(submitted) - {"email", "role"}:
        return jsonify(error="Form hanya mendukung field email dan role."), 400
    if "role" in submitted and submitted["role"] not in {"user", "admin"}:
        return jsonify(error="Role tidak dikenal."), 400

    # VULN[burp-repeater]
    update_profile(connection, submitted.items(), user_id, secure=secure)
    connection.commit()
    user = connection.execute(
        "SELECT email,role FROM users WHERE id=?", (user_id,)
    ).fetchone()
    response = jsonify(email=user["email"], role=user["role"])
    if user["role"] == "admin" and not secure:
        response.headers["X-Lab-Flag"] = current_app.config["FLAGS"]["burp-repeater"]
    return response


@extra_labs_bp.route("/blind-sqli")
def blind_sqli():
    """Expose a boolean-only SQLite oracle with no data extraction response."""
    condition = request.args.get("condition", "1=0")
    try:
        result = evaluate_condition(
            get_db(), condition, secure=session.get("secure_mode", False)
        )
    except sqlite3.Error as error:
        result = False
        error_text = str(error)
    else:
        error_text = None
    response = jsonify(result=result, error=error_text)
    if result and not session.get("secure_mode", False):
        response.headers["X-Lab-Flag"] = current_app.config["FLAGS"]["blind-sqli"]
    return response


@extra_labs_bp.route("/upload", methods=["POST"])
def upload():
    """Save an uploaded training file inside the project uploads directory."""
    uploaded = request.files.get("file")
    if uploaded is None or not uploaded.filename:
        return jsonify(error="Pilih file untuk diunggah."), 400
    secure = session.get("secure_mode", False)
    if not upload_allowed(uploaded.filename, secure=secure):
        return jsonify(error="Hanya file gambar yang diperbolehkan dalam mode Secure."), 400
    filename = Path(uploaded.filename).name
    if filename in {"", ".", ".."}:
        return jsonify(error="Nama file tidak valid."), 400
    upload_dir = Path(current_app.config["UPLOADS_DIR"]).resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)
    target = (upload_dir / filename).resolve()
    if upload_dir not in target.parents:
        return jsonify(error="File harus berada di folder upload proyek."), 400
    uploaded.save(target)
    response = jsonify(saved=filename)
    if not secure and Path(filename).suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        response.headers["X-Lab-Flag"] = current_app.config["FLAGS"]["upload"]
    return response


@extra_labs_bp.route("/jwt", methods=["GET", "POST"])
def jwt_lab():
    """Issue a local training JWT or verify a supplied token."""
    secret = (
        current_app.config["JWT_SECRET"]
        if session.get("secure_mode", False)
        # VULN[jwt]
        else "kopilab"
    )
    if request.method == "GET":
        token = encode_token({"sub": "budi", "role": "user"}, secret)
        return jsonify(token=token, warning="Token berlaku hanya untuk lab lokal.")
    token = request.form.get("token", "")
    claims = decode_token(token, secret, secure=session.get("secure_mode", False))
    if not claims:
        return jsonify(error="Token tidak valid."), 401
    response = jsonify(claims=claims)
    if claims.get("role") == "admin" and not session.get("secure_mode", False):
        response.headers["X-Lab-Flag"] = current_app.config["FLAGS"]["jwt"]
    return response


@extra_labs_bp.route("/coupon", methods=["POST"])
def coupon():
    """Redeem a local coupon, demonstrating duplicate check-and-insert behavior."""
    user_id = session.get("uid")
    if not user_id:
        return jsonify(error="Masuk dengan akun latihan terlebih dahulu."), 401
    connection = get_db()
    redemption_count = redeem_coupon(
        connection, user_id, secure=session.get("secure_mode", False)
    )
    connection.commit()
    response = jsonify(redemptions=redemption_count)
    if redemption_count > 1 and not session.get("secure_mode", False):
        response.headers["X-Lab-Flag"] = current_app.config["FLAGS"]["race-coupon"]
    return response


@extra_labs_bp.route("/redirect")
def open_redirect():
    """Redirect to a local destination under the selected mode's policy."""
    destination = request.args.get("next", "/")
    secure = session.get("secure_mode", False)
    if not allowed_redirect(destination, secure=secure):
        return jsonify(error="Tujuan redirect tidak diizinkan."), 400
    response = redirect(destination)
    if not secure and destination.startswith(("http://127.0.0.1:9000", "http://localhost:9000")):
        response.headers["X-Lab-Flag"] = current_app.config["FLAGS"]["open-redirect"]
    return response


@extra_labs_bp.route("/rate-login", methods=["POST"])
def rate_login():
    """Track local failed-login attempts and demonstrate weak throttling."""
    player_id = session["player_id"]
    connection = get_db()
    count = record_login_attempt(
        connection, player_id, secure=session.get("secure_mode", False)
    )
    connection.commit()
    if session.get("secure_mode", False) and count >= 5:
        return jsonify(error="Terlalu banyak percobaan. Coba lagi setelah jeda."), 429
    response = jsonify(attempts=count, authenticated=False)
    if count >= 6 and not session.get("secure_mode", False):
        response.headers["X-Lab-Flag"] = current_app.config["FLAGS"]["rate-limit"]
    return response


@extra_labs_bp.route("/filter")
def filter_bypass():
    """Apply a simple reserved-name filter in the local training endpoint."""
    query = request.args.get("q", "")
    secure = session.get("secure_mode", False)
    blocked = blocked_username(query, secure=secure)
    response = jsonify(blocked=blocked)
    if not blocked and query.casefold() == "admin" and not secure:
        response.headers["X-Lab-Flag"] = current_app.config["FLAGS"]["filter-bypass"]
    return response

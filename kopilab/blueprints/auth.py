"""Authentication and password-recovery routes."""

from __future__ import annotations

import hashlib
import secrets
import sqlite3
import time

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from ..db import get_db
from ..inspector import record_query
from ..vulns.reset import reset_password, reset_token
from ..vulns.sqli_login import login_query

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate using the intentionally injectable legacy query."""
    error = None
    sql = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        secure = session.get("secure_mode", False)
        sql = login_query(username, password, secure=secure)
        record_query(sql)
        try:
            parameters = (username, password) if secure else ()
            row = get_db().execute(sql, parameters).fetchone()
        except sqlite3.Error as database_error:
            error = "Kredensial tidak valid." if secure else str(database_error)
            row = None
        if row:
            session["uid"], session["user"] = row["id"], row["username"]
            response = redirect(url_for("account.me"))
            response.set_cookie("admin", "1" if row["role"] == "admin" else "0")
            return response
        if error is None:
            flash("Username atau password tidak cocok.", "error")
    return render_template(
        "auth/login.html",
        error=error,
        sql=None if session.get("secure_mode", False) else sql,
    )


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a basic customer account."""
    if request.method == "POST":
        connection = get_db()
        connection.execute(
            "INSERT INTO users(username,password,email,role,balance) VALUES(?,?,?,'user',100000)",
            (request.form["username"], request.form["password"], request.form.get("email", "")),
        )
        connection.commit()
        flash("Akun berhasil dibuat. Silakan masuk.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    """Clear the current browser session."""
    session.clear()
    flash("Kamu sudah keluar dari akun.", "info")
    return redirect(url_for("shop.index"))


@auth_bp.route("/reset", methods=["GET", "POST"])
def reset():
    """Reset an account password using the selected lab-mode token."""
    message = None
    success = False
    secure_token = None
    secure = session.get("secure_mode", False)
    if request.method == "POST":
        username = request.form["user"]
        token = request.form.get("token", "")
        if request.form.get("step") == "request":
            message = "Jika akun ada, token dikirim ke email."
            if secure:
                connection = get_db()
                user = connection.execute(
                    "SELECT id FROM users WHERE username=?", (username,)
                ).fetchone()
                if user:
                    secure_token = secrets.token_urlsafe(32)
                    token_hash = hashlib.sha256(secure_token.encode()).hexdigest()
                    connection.execute(
                        """INSERT INTO password_reset_tokens(user_id,token_hash,expires_at)
                           VALUES(?,?,?) ON CONFLICT(user_id) DO UPDATE SET
                           token_hash=excluded.token_hash, expires_at=excluded.expires_at""",
                        (user["id"], token_hash, int(time.time()) + 600),
                    )
                    connection.commit()
                    session["reset_token_display"] = secure_token
        else:
            connection = get_db()
            if secure:
                user = connection.execute(
                    "SELECT id FROM users WHERE username=?", (username,)
                ).fetchone()
                stored = (
                    connection.execute(
                        "SELECT token_hash,expires_at FROM password_reset_tokens WHERE user_id=?",
                        (user["id"],),
                    ).fetchone()
                    if user
                    else None
                )
                valid = bool(
                    stored
                    and int(time.time()) <= stored["expires_at"]
                    and secrets.compare_digest(
                        hashlib.sha256(token.encode()).hexdigest(), stored["token_hash"]
                    )
                )
                if valid and user:
                    reset_password(connection, username, request.form["password"])
                    connection.execute(
                        "DELETE FROM password_reset_tokens WHERE user_id=?", (user["id"],)
                    )
                    connection.commit()
                    message, success = "Password diubah.", True
                    session.pop("reset_token_display", None)
                else:
                    message = "Token salah atau sudah kedaluwarsa."
            elif token != reset_token(username):
                message = "Token salah."
            else:
                reset_password(connection, username, request.form["password"])
                connection.commit()
                message = "Password diubah."
                success = True
                if username == "admin":
                    message += f" {current_app.config['FLAGS']['reset']}"
    return render_template(
        "auth/reset.html",
        message=message,
        success=success,
        secure_token=secure_token or session.get("reset_token_display"),
    )

"""KopiLab application factory."""

from __future__ import annotations

import secrets
from pathlib import Path
from typing import Any

from flask import Flask, g, redirect, request, session

from .config import Config
from .db import close_db, get_db, init_db
from .inspector import record_request


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Create and configure a KopiLab Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = secrets.token_hex(32)
    app.config["JWT_SECRET"] = secrets.token_hex(32)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    if test_config:
        app.config.update(test_config)
    init_db(app)

    from .blueprints.account import account_bp
    from .blueprints.admin import admin_bp
    from .blueprints.api import api_bp
    from .blueprints.auth import auth_bp
    from .blueprints.labs import labs_bp
    from .blueprints.files import files_bp
    from .blueprints.extra_labs import extra_labs_bp
    from .blueprints.guide import guide_bp
    from .blueprints.shop import shop_bp

    for blueprint in (
        shop_bp, auth_bp, account_bp, admin_bp, api_bp, labs_bp, files_bp,
        extra_labs_bp, guide_bp
    ):
        app.register_blueprint(blueprint)
    app.teardown_appcontext(close_db)

    @app.before_request
    def assign_player() -> None:
        """Create an opaque player handle; progress itself remains in SQLite."""
        session.setdefault("player_id", secrets.token_urlsafe(24))
        g.last_sql = ""

    @app.after_request
    def vulnerable_cookie(response: Any) -> Any:
        """Set the deliberately readable XSS training cookie."""
        # VULN[xss]
        response.set_cookie(
            "xss_flag",
            app.config["FLAGS"]["xss"],
            httponly=session.get("secure_mode", False),
            samesite="Lax" if session.get("secure_mode", False) else None,
        )
        if app.config["ENABLE_INSPECTOR"]:
            record_request(response, request, g.get("last_sql", ""))
        return response

    @app.context_processor
    def shared_context() -> dict[str, Any]:
        """Expose shared navigation and the safety banner to templates."""
        return {
            "current_user": session.get("user"),
            "warning_banner": app.config["WARNING_BANNER"],
            "cart_count": sum(session.get("cart", {}).values()),
            "secure_mode": session.get("secure_mode", False),
            "inspector_enabled": app.config["ENABLE_INSPECTOR"],
            "last_inspection": (
                get_db().execute(
                    "SELECT * FROM request_inspector WHERE player_id=?",
                    (session.get("player_id", ""),),
                ).fetchone()
                if app.config["ENABLE_INSPECTOR"]
                else None
            ),
        }

    @app.errorhandler(404)
    def not_found(_: Exception) -> tuple[str, int]:
        from flask import render_template

        return render_template(
            "error.html", code=404, title="Halaman tidak ditemukan",
            message="Alamat yang kamu buka tidak tersedia.",
        ), 404

    @app.errorhandler(500)
    def server_error(_: Exception) -> tuple[str, int]:
        from flask import render_template

        return render_template(
            "error.html", code=500, title="Terjadi kesalahan",
            message="Coba lagi. Jika masalah berlanjut, periksa log lokal.",
        ), 500

    @app.route("/health")
    def health() -> tuple[str, int]:
        return "ok", 200

    return app


def require_login():
    """Redirect unauthenticated visitors to the login page."""
    return None if "uid" in session else redirect("/login")

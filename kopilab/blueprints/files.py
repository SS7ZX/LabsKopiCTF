"""File download and URL preview routes, confined to local training targets."""

from flask import Blueprint, current_app, render_template, request, session

from ..vulns.ssrf import fetch_internal_url
from ..vulns.traversal import resolve_training_file

files_bp = Blueprint("files", __name__)


@files_bp.route("/download")
def download():
    """Download a project-local file using the vulnerable path selector."""
    try:
        path = resolve_training_file(
            current_app.config["FILES_DIR"],
            current_app.config["PROJECT_DIR"],
            request.args.get("file", "welcome.txt"),
            secure=session.get("secure_mode", False),
        )
        return path.read_text(encoding="utf-8"), 200, {"Content-Type": "text/plain; charset=utf-8"}
    except (OSError, ValueError) as error:
        return str(error), 404


@files_bp.route("/preview")
def preview():
    """Fetch the simulated local internal service for the SSRF lab."""
    url = request.args.get("url")
    data = None
    error = None
    if url:
        try:
            data = fetch_internal_url(
                url,
                current_app.config["INTERNAL_HOST"],
                current_app.config["INTERNAL_PORT"],
                secure=session.get("secure_mode", False),
            )
        except (OSError, ValueError) as fetch_error:
            error = str(fetch_error)
    return render_template("files/preview.html", url=url, result=data, error=error)

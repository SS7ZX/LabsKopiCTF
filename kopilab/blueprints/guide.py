"""System-wide beginner guide for KopiLab."""

from flask import Blueprint, render_template

from ..config import BURP_LAB_GUIDES, LABS, LAB_METADATA

guide_bp = Blueprint("guide", __name__)


@guide_bp.route("/guide")
def deep_dive():
    """Render a walkthrough of all major app systems and training labs."""
    lab_entries = [
        {
            "id": lab_id,
            "title": title,
            "category": category,
            "category_id": LAB_METADATA[lab_id]["category_id"],
            "level": LAB_METADATA[lab_id]["level"],
            "endpoint": LAB_METADATA[lab_id]["endpoint"],
            "burp_guide": BURP_LAB_GUIDES[lab_id],
        }
        for lab_id, title, category, _ in LABS
    ]
    return render_template("guide.html", labs=lab_entries)

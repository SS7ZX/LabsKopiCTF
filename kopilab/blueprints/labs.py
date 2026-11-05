"""Learning lab index, details, hints, and flag submission."""

from pathlib import Path
import re
import secrets

from flask import Blueprint, Response, current_app, flash, redirect, render_template, request, session, url_for

from ..config import BURP_LAB_GUIDES, LABS, LAB_METADATA
from ..db import close_db, get_db, init_db
from ..lab_system_guides import LAB_SYSTEM_GUIDES

labs_bp = Blueprint("labs", __name__)


@labs_bp.route("/mode", methods=["POST"])
def toggle_mode():
    """Toggle the current browser session between vulnerable and secure modes."""
    session["secure_mode"] = not session.get("secure_mode", False)
    flash(
        "Mode Secure aktif." if session["secure_mode"] else "Mode Vulnerable aktif.",
        "success",
    )
    return redirect(url_for("labs.labs"))


@labs_bp.route("/labs", methods=["GET", "POST"])
def labs():
    """Display a filterable lab catalog and record submitted flags."""
    if request.method == "POST":
        submitted = request.form.get("flag", "").strip()
        hit = [key for key, value in current_app.config["FLAGS"].items() if value == submitted]
        if hit:
            connection = get_db()
            connection.executemany(
                "INSERT OR IGNORE INTO lab_solves(player_id,lab_id) VALUES(?,?)",
                [(session["player_id"], lab_id) for lab_id in hit],
            )
            connection.commit()
            flash("Benar! Flag berhasil diklaim.", "success")
        else:
            flash("Flag salah. Periksa kembali dan coba lagi.", "error")
        return redirect(url_for("labs.labs"))
    solved = solved_labs(session["player_id"])
    entries = lab_entries(solved)
    return render_template(
        "labs/index.html",
        labs=entries,
        solved_count=len(solved),
        progress=(len(solved) / len(entries) * 100) if entries else 0,
    )


@labs_bp.route("/scoreboard")
def scoreboard():
    """Display SQLite-backed lab completion totals."""
    rows = get_db().execute(
        """SELECT player_id,COUNT(*) AS solved,MAX(solved_at) AS last_solved
           FROM lab_solves GROUP BY player_id ORDER BY solved DESC,last_solved ASC"""
    ).fetchall()
    entries = [
        {
            "name": f"Pelajar-{row['player_id'][-4:]}",
            "solved": row["solved"],
            "last_solved": row["last_solved"],
        }
        for row in rows
    ]
    return render_template(
        "labs/scoreboard.html", entries=entries, lab_count=len(LABS)
    )


@labs_bp.route("/labs/reset-progress", methods=["POST"])
def reset_progress():
    """Clear only the current player's persisted completion records."""
    get_db().execute("DELETE FROM lab_solves WHERE player_id=?", (session["player_id"],))
    get_db().commit()
    flash("Progres lab kamu sudah direset.", "info")
    return redirect(url_for("labs.labs"))


@labs_bp.route("/labs/reset-database", methods=["POST"])
def reset_database():
    """Recreate all seeded local training data and clear all progress."""
    app = current_app._get_current_object()
    close_db()
    init_db(app, reset=True)
    session.clear()
    session["player_id"] = secrets.token_urlsafe(24)
    flash("Database lokal dan seluruh progres berhasil direset.", "success")
    return redirect(url_for("labs.labs"))


@labs_bp.route("/labs/<lab_id>/report.md")
def report(lab_id: str) -> Response | tuple[str, int]:
    """Generate a Markdown pentest report template for a known lab."""
    lab = next((entry for entry in lab_entries([]) if entry["id"] == lab_id), None)
    if lab is None:
        return "Lab tidak ditemukan.", 404
    lesson = read_lesson(lab_id)
    category_severity = LAB_METADATA[lab_id]["cvss"]
    content = "\n".join(
        [
            f"# Laporan Uji Keamanan: {lab['title']}",
            "",
            f"- **Kategori:** {lab['category_id']} — {lab['category']}",
            f"- **Severity / CVSS:** {category_severity}",
            f"- **Endpoint:** `{lab['endpoint']}`",
            "- **Lingkungan:** KopiLab lokal, data latihan saja",
            "",
            "## Ringkasan",
            str(lesson["concept"]),
            "",
            "## Langkah reproduksi",
            "1. Jalankan aplikasi KopiLab secara lokal dalam mode Vulnerable.",
            f"2. Buka endpoint `{lab['endpoint']}` menggunakan akun seed yang disediakan.",
            "3. Amati dampak pada data latihan dan catat bukti tanpa mengakses sistem lain.",
            "",
            "## Dampak",
            str(lesson["root_cause"]),
            "",
            "## Rekomendasi",
            str(lesson["fix"]),
            "",
            "## Catatan",
            "Sesuaikan langkah, bukti, dan penilaian CVSS dengan konteks aset sebelum menerbitkan laporan.",
            "",
        ]
    )
    return Response(content, mimetype="text/markdown")


@labs_bp.route("/labs/<lab_id>", methods=["GET", "POST"])
def lab_detail(lab_id: str):
    """Show a lesson and reveal its hints and solution progressively."""
    current_solved = solved_labs(session["player_id"])
    entry = next(
        (lab for lab in lab_entries(current_solved) if lab["id"] == lab_id),
        None,
    )
    if entry is None:
        return render_template(
            "error.html", code=404, title="Lab tidak ditemukan",
            message="Lab ini tidak tersedia.",
        ), 404
    content = read_lesson(lab_id)
    if request.method == "POST":
        action = request.form.get("action")
        if action == "hint":
            current_hint = int(session.get("lab_hints", {}).get(lab_id, 0))
            session.setdefault("lab_hints", {})[lab_id] = min(current_hint + 1, 3)
            session.modified = True
        elif action == "solution":
            session.setdefault("lab_solutions", []).append(lab_id)
            session["lab_solutions"] = sorted(set(session["lab_solutions"]))
        elif action == "flag":
            submitted = request.form.get("flag", "").strip()
            if submitted == current_app.config["FLAGS"][lab_id]:
                get_db().execute(
                    "INSERT OR IGNORE INTO lab_solves(player_id,lab_id) VALUES(?,?)",
                    (session["player_id"], lab_id),
                )
                get_db().commit()
                flash("Benar! Flag berhasil diklaim.", "success")
            else:
                flash("Flag salah. Periksa kembali dan coba lagi.", "error")
        return redirect(url_for("labs.lab_detail", lab_id=lab_id))
    hint_count = session.get("lab_hints", {}).get(lab_id, 0)
    solution_visible = lab_id in session.get("lab_solutions", [])
    return render_template(
        "labs/detail.html",
        lab=entry,
        lesson=content,
        hint_count=hint_count,
        solution_visible=solution_visible,
        solved=lab_id in current_solved,
    )


def lab_entries(solved: list[str]) -> list[dict[str, object]]:
    """Combine the original lab names with learning metadata."""
    entries = []
    for lab_id, title, category, difficulty in LABS:
        lesson = read_lesson(lab_id)
        metadata = LAB_METADATA[lab_id]
        entries.append(
            {
                "id": lab_id,
                "title": title,
                "category": category,
                "difficulty": difficulty,
                "category_id": metadata["category_id"],
                "level": metadata["level"],
                "cvss": metadata["cvss"],
                "endpoint": metadata["endpoint"],
                "burp_required": metadata.get("burp_required", False),
                "burp_guide": BURP_LAB_GUIDES[lab_id],
                "system_guide": LAB_SYSTEM_GUIDES[lab_id],
                "solved": lab_id in solved,
                "concept": lesson["concept"],
            }
        )
    return entries


def solved_labs(player_id: str) -> list[str]:
    """Return lab IDs completed by one opaque SQLite-backed player record."""
    return [
        row["lab_id"]
        for row in get_db().execute(
            "SELECT lab_id FROM lab_solves WHERE player_id=?", (player_id,)
        )
    ]


def read_lesson(lab_id: str) -> dict[str, object]:
    """Read the fixed-section Markdown lesson for one known lab."""
    path = Path(current_app.config["LABS_DIR"]) / f"{lab_id}.md"
    sections: dict[str, str] = {}
    current_section = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current_section = line[3:].strip().lower()
            sections[current_section] = ""
        elif current_section:
            sections[current_section] += line + "\n"
    return {
        "goal": sections.get("tujuan", "").strip(),
        "concept": sections.get("konsep", "").strip(),
        "hints": [sections.get(f"hint {index}", "").strip() for index in range(1, 4)],
        "solution": sections.get("solusi", "").strip(),
        "root_cause": sections.get("akar masalah", "").strip(),
        "fix": sections.get("perbaikan", "").strip(),
        "steps": [
            re.sub(r"^(?:[-*]\s+|\d+[.)]\s+)", "", line.strip())
            for line in sections.get("langkah latihan", "").splitlines()
            if line.strip()
        ],
        "analysis": [
            re.sub(r"^(?:[-*]\s+|\d+[.)]\s+)", "", line.strip())
            for line in sections.get("analisis mendalam", "").splitlines()
            if line.strip()
        ],
        "evidence": [
            re.sub(r"^(?:[-*]\s+|\d+[.)]\s+)", "", line.strip())
            for line in sections.get("bukti yang dicatat", "").splitlines()
            if line.strip()
        ],
        "stuck": sections.get("kalau masih bingung", "").strip(),
        "vulnerable_code": sections.get("contoh rentan", "").strip()
        or sections.get("akar masalah", "").strip(),
        "secure_code": sections.get("contoh aman", "").strip()
        or sections.get("perbaikan", "").strip(),
    }

"""Tests for SQLite-backed progress, inspector, and reporting."""

from kopilab.db import get_db


def test_flag_submission_and_scoreboard_are_stored_in_sqlite(client, app):
    client.post("/labs", data={"flag": "FLAG{union_select_master}"})
    response = client.get("/labs")
    assert b"1 dari 45 lab selesai" in response.data
    assert b"FLAG{union_select_master}" not in response.data
    scoreboard = client.get("/scoreboard")
    assert b"1/45" in scoreboard.data
    with app.app_context():
        count = get_db().execute("SELECT COUNT(*) FROM lab_solves").fetchone()[0]
        assert count == 1


def test_reset_progress_removes_only_current_player_solves(client, app):
    client.post("/labs", data={"flag": "FLAG{union_select_master}"})
    client.post("/labs/reset-progress")
    assert b"0 dari 45 lab selesai" in client.get("/labs").data
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM lab_solves").fetchone()[0] == 0


def test_request_inspector_persists_last_query_and_headers(client, app):
    client.get("/search", query_string={"q": "Gayo"})
    with app.app_context():
        record = get_db().execute("SELECT sql_text FROM request_inspector").fetchone()
        assert "Gayo" in record["sql_text"]
    response = client.get("/")
    assert b"Request Inspector" in response.data
    assert b"SELECT id,name,price,description FROM products WHERE name LIKE" in response.data
    assert b"Content-Type" in response.data


def test_report_template_contains_required_sections(client):
    response = client.get("/labs/sqli-union/report.md")
    assert response.status_code == 200
    assert response.mimetype == "text/markdown"
    assert b"Severity / CVSS" in response.data
    assert b"Langkah reproduksi" in response.data
    assert b"Dampak" in response.data
    assert b"Rekomendasi" in response.data


def test_database_reset_restores_seed_data_and_clears_global_progress(client, app):
    client.post("/labs", data={"flag": "FLAG{union_select_master}"})
    with app.app_context():
        get_db().execute("UPDATE users SET balance=0 WHERE username='budi'")
        get_db().commit()
    response = client.post("/labs/reset-database", follow_redirects=True)
    assert b"Database lokal dan seluruh progres berhasil direset." in response.data
    assert b"0 dari 45 lab selesai" in response.data
    with app.app_context():
        assert get_db().execute("SELECT balance FROM users WHERE username='budi'").fetchone()[0] == 500000
        assert get_db().execute("SELECT COUNT(*) FROM lab_solves").fetchone()[0] == 0

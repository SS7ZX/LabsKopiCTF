"""Tests for the system-wide beginner deep dive guide."""

from kopilab.config import BURP_LAB_GUIDES, LABS
from markupsafe import escape


def test_guide_route_renders_all_system_sections(client):
    response = client.get("/guide")
    assert response.status_code == 200
    for section in (
        "alur",
        "struktur",
        "database",
        "mode",
        "toko",
        "belajar",
        "inspector",
        "burp",
        "lokal",
        "labs",
        "tes",
    ):
        assert f'id="{section}"'.encode() in response.data
    assert b"127.0.0.1" in response.data
    assert b"HTTP history" in response.data
    assert b"Open browser" in response.data
    assert b"Intercept is off" in response.data
    assert b"alur kerja Repeater yang terukur" in response.data
    assert b"Kerangka analisis request dan response" in response.data
    assert b"Deep dive: cara berpikir saat menguji satu request" in response.data
    assert b"empat pola analisis lab Super Sulit" in response.data
    assert b"Template catatan analisis" in response.data
    for practitioner_lab in (
        "Tenant export",
        "Checkout settlement",
        "Webhook replay",
        "Nested resolver",
    ):
        assert practitioner_lab.encode() in response.data
    assert b"Playbook Burp untuk semua lab" in response.data
    for lab_id, *_ in LABS:
        assert f"/labs/{lab_id}".encode() in response.data
    assert b"Active Scan" in response.data


def test_guide_lists_every_lab_and_links_to_its_lesson(client):
    response = client.get("/guide")
    for lab_id, *_ in LABS:
        assert f"/labs/{lab_id}".encode() in response.data
        assert lab_id in BURP_LAB_GUIDES
        assert str(escape(BURP_LAB_GUIDES[lab_id]["request"])).encode() in response.data
    assert len(LABS) == 45
    assert len(BURP_LAB_GUIDES) == len(LABS)


def test_guide_is_in_global_navigation_and_uses_local_assets(client):
    home = client.get("/")
    assert b">Deep Dive</a>" in home.data
    guide = client.get("/guide")
    assert b"/static/css/style.css" in guide.data
    assert b"https://cdn" not in guide.data

"""Tests for the system-wide beginner deep dive guide."""

from kopilab.config import LABS


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


def test_guide_lists_every_lab_and_links_to_its_lesson(client):
    response = client.get("/guide")
    for lab_id, *_ in LABS:
        assert f"/labs/{lab_id}".encode() in response.data
    assert len(LABS) == 20


def test_guide_is_in_global_navigation_and_uses_local_assets(client):
    home = client.get("/")
    assert b">Deep Dive</a>" in home.data
    guide = client.get("/guide")
    assert b"/static/css/style.css" in guide.data
    assert b"https://cdn" not in guide.data

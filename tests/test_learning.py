"""Tests for structured learning pages and staged hints."""

from kopilab.config import LABS


def test_lab_index_lists_13_labs_and_progress(client):
    response = client.get("/labs")
    assert response.status_code == 200
    assert b"0 dari 20 lab selesai" in response.data
    for lab_id, *_ in LABS:
        assert f"/labs/{lab_id}".encode() in response.data


def test_every_lab_has_material_hints_solution_and_side_by_side_diff(client):
    for lab_id, *_ in LABS:
        response = client.get(f"/labs/{lab_id}")
        assert response.status_code == 200, lab_id
        assert b"Contoh kode" in response.data, lab_id
        assert b"Rentan" in response.data, lab_id
        assert b"Aman" in response.data, lab_id
        assert b"Langkah praktikum" in response.data, lab_id
        assert b"Cara melihat request untuk lab ini" in response.data, lab_id
        assert b"HTTP history" in response.data, lab_id
        assert b"Request yang menjadi fokus di lab ini" in response.data, lab_id
        assert b"Kalau masih bingung" in response.data, lab_id
        assert b"Buka solusi lengkap" in response.data, lab_id
        assert b"Petunjuk 1" not in response.data, lab_id


def test_lab_detail_starts_with_hints_and_solution_hidden(client):
    response = client.get("/labs/sqli-union")
    assert response.status_code == 200
    assert b"Tujuan belajar" in response.data
    assert b"Endpoint target" in response.data
    assert b"Petunjuk 1" not in response.data
    assert b"Akar masalah" not in response.data
    assert b"Buka solusi lengkap" in response.data


def test_hints_open_one_at_a_time_and_solution_is_revealed_on_request(client):
    first = client.post("/labs/xss", data={"action": "hint"}, follow_redirects=True)
    assert b"Petunjuk 1" in first.data
    assert b"Petunjuk 2" not in first.data
    second = client.post("/labs/xss", data={"action": "hint"}, follow_redirects=True)
    assert b"Petunjuk 2" in second.data
    assert b"Flag cookie demonstrasi" not in second.data
    third = client.post("/labs/xss", data={"action": "hint"}, follow_redirects=True)
    assert b"Petunjuk 3" in third.data
    assert b"Buka solusi lengkap" in third.data
    solution = client.post("/labs/xss", data={"action": "solution"}, follow_redirects=True)
    assert b"Akar masalah" in solution.data
    assert b"Cara memperbaiki" in solution.data


def test_student_can_open_solution_before_revealing_every_hint(client):
    response = client.post(
        "/labs/idor-order",
        data={"action": "solution"},
        follow_redirects=True,
    )
    assert b"Jawaban singkat" in response.data
    assert b"Kenapa bug ini bisa terjadi?" in response.data
    assert b"Cara memperbaiki" in response.data


def test_unknown_lab_returns_branded_not_found_page(client):
    response = client.get("/labs/not-a-lab")
    assert response.status_code == 404
    assert b"aplikasi sengaja rentan" in response.data.lower()


def test_flag_can_be_submitted_from_its_lab_detail(client):
    response = client.post(
        "/labs/sqli-union",
        data={"action": "flag", "flag": "FLAG{union_select_master}"},
        follow_redirects=True,
    )
    assert b"Flag berhasil diklaim" in response.data
    assert b"Selesai" in response.data
    assert b"FLAG{union_select_master}" not in response.data

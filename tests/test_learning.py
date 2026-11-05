"""Tests for structured learning pages and staged hints."""

from kopilab.config import LABS
from kopilab.lab_system_guides import LAB_SYSTEM_GUIDES


def test_lab_index_lists_all_labs_and_progress(client):
    response = client.get("/labs")
    assert response.status_code == 200
    assert f"0 dari {len(LABS)} lab selesai".encode() in response.data
    for lab_id, *_ in LABS:
        assert f"/labs/{lab_id}".encode() in response.data


def test_every_lab_has_material_hints_solution_and_side_by_side_diff(client):
    for lab_id, *_ in LABS:
        response = client.get(f"/labs/{lab_id}")
        assert response.status_code == 200, lab_id
        assert b"Contoh kode" in response.data, lab_id
        assert b"Tujuan pembelajaran dan cara kerja sistem" in response.data, lab_id
        assert b"Setelah latihan, kamu diharapkan bisa" in response.data, lab_id
        assert b"Alur request di aplikasi ini" in response.data, lab_id
        assert b"Data dan state yang disentuh" in response.data, lab_id
        assert b"Kenapa eksperimen Repeater dilakukan seperti itu?" in response.data, lab_id
        assert b"Rentan" in response.data, lab_id
        assert b"Aman" in response.data, lab_id
        assert b"Langkah praktikum" in response.data, lab_id
        if lab_id == "burp-repeater":
            assert b"Lab ini harus dikerjakan dengan Burp Repeater" in response.data
        else:
            assert b"Cara melihat request untuk lab ini" in response.data, lab_id
        assert b"HTTP history" in response.data, lab_id
        assert b"Request yang menjadi fokus di lab ini" in response.data, lab_id
        assert b"Playbook Burp khusus lab ini" in response.data, lab_id
        assert b"Lakukan eksperimen lab, satu perubahan saja" in response.data, lab_id
        assert b"Urutan aksi browser yang harus kamu tangkap untuk lab ini" in response.data, lab_id
        assert b"Checklist bukti khusus lab ini" in response.data, lab_id
        assert b"Kalau mentok: diagnosis langkah demi langkah" in response.data, lab_id
        assert b"Request tidak muncul di HTTP history" in response.data, lab_id
        assert b"Repeater mendapat redirect login, 401" in response.data, lab_id
        assert b"Request sukses, tetapi flag atau dampak yang diharapkan tidak terlihat" in response.data, lab_id
        assert b"Vulnerable dan Secure terlihat sama" in response.data, lab_id
        assert b"catatan pemecahan masalah yang ditulis khusus untuk materi ini" in response.data, lab_id
        assert b'href="#petunjuk"' in response.data, lab_id
        assert b"Kalau masih bingung" in response.data, lab_id
        assert b"Buka solusi lengkap" in response.data, lab_id
        assert b"Petunjuk 1" not in response.data, lab_id
    assert set(LAB_SYSTEM_GUIDES) == {lab_id for lab_id, *_ in LABS}
    burp_lab = client.get("/labs/burp-repeater")
    assert b"BURP SUITE WAJIB" in burp_lab.data
    assert b"Deep dive: analisis" in burp_lab.data
    assert b"Bukti yang perlu dicatat" in burp_lab.data


def test_system_explanations_distinguish_database_and_session_state(client):
    examples = {
        "logic-price": (b"orders", b"users.balance"),
        "oauth-state": (b"Flask session", b"bukan SQLite"),
        "race-coupon": (b"coupon_redemptions", b"BEGIN IMMEDIATE"),
        "tenant-export-chain": (b"academy_tenant_exports", b"bukan object storage"),
    }
    for lab_id, expected_terms in examples.items():
        response = client.get(f"/labs/{lab_id}")
        assert response.status_code == 200
        for term in expected_terms:
            assert term in response.data, (lab_id, term)


def test_practice_steps_do_not_repeat_their_list_numbers(client):
    for lab_id, *_ in LABS:
        response = client.get(f"/labs/{lab_id}")
        assert b"<li>1. " not in response.data, lab_id


def test_lab_detail_starts_with_hints_and_solution_hidden(client):
    response = client.get("/labs/sqli-union")
    assert response.status_code == 200
    assert b"Tujuan belajar" in response.data
    assert b"Endpoint target" in response.data
    assert b"Petunjuk 1" not in response.data
    assert b"Akar masalah" not in response.data
    assert b"Buka solusi lengkap" in response.data


def test_sqli_union_lesson_explains_burp_request_and_secure_comparison(client):
    response = client.get("/labs/sqli-union")
    assert response.status_code == 200
    assert b"HTTP history" in response.data
    assert b"UNION SELECT 1" in response.data
    assert b"FROM secrets" in response.data
    assert b"empat kolom" in response.data
    assert b"mode Vulnerable" in response.data
    assert b"mode Secure" in response.data


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

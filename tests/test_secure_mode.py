"""Verify that the original lab behaviors are blocked in secure mode."""

import hashlib


def enable_secure_mode(client):
    """Set secure mode in the browser's signed session."""
    with client.session_transaction() as browser_session:
        browser_session["secure_mode"] = True


def login(client):
    """Sign in as the seeded non-admin user."""
    return client.post("/login", data={"username": "budi", "password": "budi123"})


def test_mode_toggle_is_global_to_the_current_session(client):
    vulnerable = client.get("/")
    assert b"Vulnerable" in vulnerable.data
    response = client.post("/mode", follow_redirects=True)
    assert b"Mode Secure aktif." in response.data
    assert b"Secure" in response.data


def test_sqli_union_is_parameterized_in_secure_mode(client):
    enable_secure_mode(client)
    response = client.get(
        "/search",
        query_string={"q": "%' UNION SELECT 1,'flag',1,value FROM secrets-- "},
    )
    assert b"FLAG{union_select_master}" not in response.data


def test_sqli_login_does_not_authenticate_in_secure_mode(client):
    enable_secure_mode(client)
    response = client.post(
        "/login", data={"username": "' OR '1'='1' -- ", "password": "x"}
    )
    assert response.status_code == 200
    assert b"FLAG{auth_bypass_with_a_quote}" not in response.data
    assert b"Query yang dijalankan" not in response.data


def test_reflected_and_stored_xss_are_escaped_in_secure_mode(client):
    enable_secure_mode(client)
    reflected = client.get("/search", query_string={"q": "<script>alert(1)</script>"})
    assert b"&lt;script&gt;" in reflected.data
    assert b"<script>alert(1)</script>" not in reflected.data
    client.post("/review", data={"pid": "1", "body": "<script>alert(1)</script>", "rating": "5"})
    stored = client.get("/product/1")
    assert b"&lt;script&gt;" in stored.data
    assert "HttpOnly" in stored.headers["Set-Cookie"]


def test_order_idor_is_scoped_to_owner_in_secure_mode(client):
    enable_secure_mode(client)
    login(client)
    assert client.get("/order/1").status_code == 404


def test_api_idor_is_scoped_to_current_user_in_secure_mode(client):
    enable_secure_mode(client)
    login(client)
    response = client.get("/api/user/1")
    assert response.status_code == 404
    assert b"FLAG{idor_api_user_leak}" not in response.data


def test_client_price_is_ignored_in_secure_mode(client):
    enable_secure_mode(client)
    login(client)
    response = client.post(
        "/checkout", data={"pid": "99", "price": "0", "qty": "1"},
        follow_redirects=True,
    )
    assert b"FLAG{never_trust_client_price}" not in response.data
    assert b"Saldo tidak cukup" in response.data


def test_negative_quantity_is_rejected_in_secure_mode(client):
    enable_secure_mode(client)
    login(client)
    response = client.post(
        "/checkout", data={"pid": "1", "price": "85000", "qty": "-200"}
    )
    assert response.status_code == 400
    assert b"FLAG{negative_qty_and_coupon_stacking}" not in response.data


def test_mass_assignment_ignores_role_in_secure_mode(client):
    enable_secure_mode(client)
    login(client)
    client.post("/profile", data={"role": "admin"})
    profile = client.get("/me")
    assert b"Role</span> user" in profile.data
    assert b"FLAG{mass_assignment_role_escalation}" not in profile.data


def test_forged_admin_cookie_does_not_grant_access_in_secure_mode(client):
    enable_secure_mode(client)
    client.set_cookie("admin", "1")
    assert client.get("/admin").status_code == 403


def test_cross_site_transfer_without_token_is_rejected_in_secure_mode(client):
    enable_secure_mode(client)
    login(client)
    response = client.post(
        "/transfer",
        data={"to": "siti", "amount": "1"},
        headers={"Referer": "http://127.0.0.1:9000/attacker"},
    )
    assert response.status_code == 403
    assert b"FLAG{cross_site_request_accepted}" not in response.data


def test_project_file_cannot_be_read_by_traversal_in_secure_mode(client):
    enable_secure_mode(client)
    response = client.get("/download", query_string={"file": "../secret.txt"})
    assert response.status_code == 404
    assert b"FLAG{path_traversal_etc_passwd_vibes}" not in response.data


def test_ssrf_is_confined_to_exact_lab_service_in_secure_mode(client, app):
    enable_secure_mode(client)
    response = client.get(
        "/preview",
        query_string={
            "url": f"http://127.0.0.1:{app.config['INTERNAL_PORT']}/other"
        },
    )
    assert b"service lab yang tepat" in response.data
    assert b"FLAG{ssrf_to_internal_service}" not in response.data


def test_predictable_reset_token_is_rejected_in_secure_mode(client):
    enable_secure_mode(client)
    response = client.post(
        "/reset",
        data={
            "user": "admin",
            "token": hashlib.md5(b"admin").hexdigest(),
            "password": "local-test-password",
        },
    )
    assert b"Token salah atau sudah kedaluwarsa" in response.data
    assert b"FLAG{predictable_reset_token}" not in response.data


def test_secure_reset_token_is_random_persisted_and_single_use(client):
    enable_secure_mode(client)
    issued = client.post(
        "/reset",
        data={"user": "budi", "step": "request"},
        follow_redirects=True,
    )
    marker = b"Token demo lokal (tersimpan di database, sekali pakai): "
    assert marker in issued.data
    token = issued.data.split(marker, 1)[1].split(b"<code>", 1)[1].split(b"</code>", 1)[0].decode()
    changed = client.post(
        "/reset",
        data={"user": "budi", "token": token, "password": "secure-new-password"},
        follow_redirects=True,
    )
    assert b"Password diubah." in changed.data
    replay = client.post(
        "/reset",
        data={"user": "budi", "token": token, "password": "replay-password"},
        follow_redirects=True,
    )
    assert b"Token salah atau sudah kedaluwarsa." in replay.data

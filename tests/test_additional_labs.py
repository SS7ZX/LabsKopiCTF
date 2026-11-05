"""Exploit and secure-mode tests for the seven additional local-only labs."""

from io import BytesIO
from pathlib import Path

from kopilab.vulns.jwt_lab import encode_token


def set_mode(client, secure):
    """Set the selected mode in the test browser session."""
    with client.session_transaction() as browser_session:
        browser_session["secure_mode"] = secure


def get_flag(response):
    """Return a lab flag from the response header."""
    return response.headers.get("X-Lab-Flag", "")


def test_blind_sqli_boolean_oracle_shows_flag_only_in_vulnerable_mode(client):
    response = client.get("/extra/blind-sqli?condition=1%3D1")
    assert response.json["result"] is True
    assert get_flag(response) == "FLAG{boolean_oracle_local_only}"
    set_mode(client, True)
    secure = client.get("/extra/blind-sqli?condition=1%3D1")
    assert secure.json["result"] is False
    assert not get_flag(secure)


def test_unvalidated_upload_stays_in_project_and_secure_mode_checks_extension(client, app):
    response = client.post(
        "/extra/upload",
        data={"file": (BytesIO(b"local training note"), "lesson.txt")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert get_flag(response) == "FLAG{unvalidated_upload_confined}"
    assert (Path(app.config["UPLOADS_DIR"]) / "lesson.txt").read_bytes() == b"local training note"
    set_mode(client, True)
    secure = client.post(
        "/extra/upload",
        data={"file": (BytesIO(b"local training note"), "lesson.txt")},
        content_type="multipart/form-data",
    )
    assert secure.status_code == 400
    assert not get_flag(secure)


def test_weak_jwt_secret_forges_only_vulnerable_training_claim(client):
    token = encode_token({"sub": "student", "role": "admin"}, "kopilab")
    response = client.post("/extra/jwt", data={"token": token})
    assert response.json["claims"]["role"] == "admin"
    assert get_flag(response) == "FLAG{weak_local_jwt_secret}"
    set_mode(client, True)
    secure = client.post("/extra/jwt", data={"token": token})
    assert secure.status_code == 401
    assert not get_flag(secure)


def test_coupon_double_redemption_is_blocked_in_secure_mode(client):
    client.post("/login", data={"username": "budi", "password": "budi123"})
    assert client.post("/extra/coupon").json["redemptions"] == 1
    vulnerable = client.post("/extra/coupon")
    assert vulnerable.json["redemptions"] == 2
    assert get_flag(vulnerable) == "FLAG{coupon_redeemed_twice}"
    set_mode(client, True)
    assert client.post("/extra/coupon").json["redemptions"] == 2
    assert not get_flag(client.post("/extra/coupon"))


def test_open_redirect_allows_only_local_simulator_and_secure_paths(client):
    vulnerable = client.get("/extra/redirect?next=http://127.0.0.1:9000/")
    assert vulnerable.status_code == 302
    assert vulnerable.headers["Location"] == "http://127.0.0.1:9000/"
    assert get_flag(vulnerable) == "FLAG{local_open_redirect}"
    external = client.get("/extra/redirect?next=https://example.com/")
    assert external.status_code == 400
    set_mode(client, True)
    secure_external = client.get("/extra/redirect?next=http://127.0.0.1:9000/")
    assert secure_external.status_code == 400
    assert client.get("/extra/redirect?next=/labs").headers["Location"].endswith("/labs")


def test_weak_login_rate_limit_only_flags_vulnerable_mode(client):
    responses = [client.post("/extra/rate-login") for _ in range(6)]
    assert get_flag(responses[-1]) == "FLAG{weak_login_rate_limit}"
    set_mode(client, True)
    secure = [client.post("/extra/rate-login") for _ in range(5)]
    assert secure[-1].status_code == 429
    assert not get_flag(secure[-1])


def test_case_sensitive_filter_bypass_is_normalized_securely(client):
    vulnerable = client.get("/extra/filter?q=ADMIN")
    assert vulnerable.json["blocked"] is False
    assert get_flag(vulnerable) == "FLAG{case_filter_bypass}"
    set_mode(client, True)
    secure = client.get("/extra/filter?q=ADMIN")
    assert secure.json["blocked"] is True
    assert not get_flag(secure)


def test_burp_repeater_profile_lab_allows_role_tampering_only_in_vulnerable_mode(client):
    client.post("/login", data={"username": "budi", "password": "budi123"})
    assert client.get("/extra/burp-profile").status_code == 200
    baseline = client.post(
        "/extra/burp-profile", data={"email": "student@example.test"}
    )
    assert baseline.json == {"email": "student@example.test", "role": "user"}
    assert not get_flag(baseline)

    vulnerable = client.post(
        "/extra/burp-profile",
        data={"email": "student@example.test", "role": "admin"},
    )
    assert vulnerable.json["role"] == "admin"
    assert get_flag(vulnerable) == "FLAG{burp_repeater_mass_assignment_local}"


def test_burp_repeater_profile_lab_ignores_role_in_secure_mode(client):
    client.post("/login", data={"username": "budi", "password": "budi123"})
    set_mode(client, True)
    secure = client.post(
        "/extra/burp-profile",
        data={"email": "student@example.test", "role": "admin"},
    )
    assert secure.status_code == 200
    assert secure.json == {"email": "student@example.test", "role": "user"}
    assert not get_flag(secure)


def test_attacker_simulator_is_static_and_local_only():
    from attacker.server import PAGE

    assert "127.0.0.1:5000/transfer" in PAGE
    assert "example.com" not in PAGE
    assert "document.cookie" not in PAGE

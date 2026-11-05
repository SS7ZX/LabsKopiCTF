"""Tests for the isolated, advanced local training simulations."""

import pytest

from kopilab.config import ACADEMY_LAB_IDS, ACADEMY_LABS, Config, LABS
from kopilab.db import get_db


def enable_secure_mode(client):
    with client.session_transaction() as browser_session:
        browser_session["secure_mode"] = True


def run_case(client, lab_id, secure=False):
    if secure:
        enable_secure_mode(client)
    if lab_id == "graphql-object-access":
        client.post("/login", data={"username": "budi", "password": "budi123"})
        response = client.post(f"/extra/academy/{lab_id}", data={"id": "1"})
    elif lab_id == "tenant-export-chain":
        client.post("/login", data={"username": "budi", "password": "budi123"})
        response = client.post(
            f"/extra/academy/{lab_id}",
            data={"action": "create", "tenant_id": "tenant-roastery"},
        )
        if not secure and response.status_code == 201:
            response = client.post(
                f"/extra/academy/{lab_id}",
                data={"action": "download", "export_id": "export-tenant-roastery"},
            )
    elif lab_id == "checkout-settlement-chain":
        client.post(f"/extra/academy/{lab_id}", data={"action": "quote"})
        response = client.post(
            f"/extra/academy/{lab_id}",
            data={"action": "confirm", "quote_id": "quote-training-001", "total": "1"},
        )
    elif lab_id == "webhook-replay-chain":
        client.post(
            f"/extra/academy/{lab_id}",
            data={"event_id": "evt-training-01", "amount": "50000"},
            headers={"X-Training-Signature": "fixture-valid"},
        )
        response = client.post(
            f"/extra/academy/{lab_id}",
            data={"event_id": "evt-training-01", "amount": "50000"},
            headers={"X-Training-Signature": "fixture-valid"},
        )
    elif lab_id == "graphql-resolver-chain":
        client.post("/login", data={"username": "budi", "password": "budi123"})
        response = client.post(
            f"/extra/academy/{lab_id}",
            data={"viewer_id": "2", "invoice_id": "1", "alias": "ledger"},
        )
    elif lab_id == "final-boss-ledger-chain":
        client.post("/login", data={"username": "budi", "password": "budi123"})
        quote = client.post(f"/extra/academy/{lab_id}", data={"action": "quote"}).json
        response = client.post(
            f"/extra/academy/{lab_id}",
            data={"action": "settle", "quote_id": quote["quoteId"], "total": "1"},
        )
        if not secure and response.status_code == 200:
            response = client.post(
                f"/extra/academy/{lab_id}",
                data={"action": "receipt", "order_id": "1"},
            )
    elif lab_id == "cache-poison":
        response = client.post(
            f"/extra/academy/{lab_id}",
            data={"action": "prime", "marker": "training-marker"},
        )
    elif lab_id == "xxe-sandbox":
        response = client.post(
            f"/extra/academy/{lab_id}",
            data={"xml": '<!DOCTYPE note [<!ENTITY x SYSTEM "training://marker">]><note>&x;</note>'},
        )
    elif lab_id == "mfa-workflow":
        response = client.post(f"/extra/academy/{lab_id}", data={"action": "complete"})
    elif lab_id == "workflow-order":
        response = client.post(f"/extra/academy/{lab_id}", data={"action": "claim"})
    else:
        query = {
            "cors-policy": "origin=http://training.invalid",
            "clickjacking-headers": "",
            "security-headers": "",
            "host-reset-link": "host=training.invalid",
            "cache-deception": "path=/profile.css",
            "websocket-auth": "authenticated=true",
            "nosql-filter": "filter=$ne:user",
            "ssti-toy": "name={{7*7}}",
            "command-simulation": "value=coffee;TRAINING_MARKER",
            "oauth-redirect": "redirect_uri=http://127.0.0.1:9000/oauth-callback",
            "oauth-state": "",
            "reset-host": "host=training.invalid",
            "info-disclosure": "view=diagnostic",
            "http-parameter-pollution": "amount=1&amount=100",
        }[lab_id]
        response = client.get(f"/extra/academy/{lab_id}?{query}")
    return response


@pytest.mark.parametrize("lab_id", sorted(ACADEMY_LAB_IDS))
def test_advanced_lab_has_original_material_metadata_and_burp_guide(client, lab_id):
    page = client.get(f"/labs/{lab_id}")
    assert page.status_code == 200
    assert b"Langkah praktikum" in page.data
    assert b"Deep dive: analisis" in page.data
    assert b"Playbook Burp khusus lab ini" in page.data
    assert b"Bukti yang perlu dicatat" in page.data
    if lab_id == "final-boss-ledger-chain":
        assert b"H1" in page.data
        assert b"Expert track:" in page.data
        assert b"Template laporan latihan bergaya bug bounty" in page.data
        assert b"Rubrik mutu laporan" in page.data


@pytest.mark.parametrize("lab_id", sorted(ACADEMY_LAB_IDS))
def test_advanced_lab_vulnerable_demo_is_local_and_emits_its_flag(client, lab_id):
    response = run_case(client, lab_id)
    assert response.status_code in {200, 201, 400}
    assert response.headers["X-Lab-Flag"] == Config.FLAGS[lab_id]


@pytest.mark.parametrize("lab_id", sorted(ACADEMY_LAB_IDS))
def test_advanced_lab_secure_mode_blocks_or_hardens_demo(client, lab_id):
    response = run_case(client, lab_id, secure=True)
    assert "X-Lab-Flag" not in response.headers
    if lab_id in {"websocket-auth", "mfa-workflow", "workflow-order", "tenant-export-chain"}:
        assert response.status_code in {401, 403}
    elif lab_id in {
        "nosql-filter",
        "xxe-sandbox",
        "oauth-redirect",
        "oauth-state",
        "http-parameter-pollution",
        "checkout-settlement-chain",
        "final-boss-ledger-chain",
    }:
        assert response.status_code == 400
    elif lab_id in {"graphql-object-access", "graphql-resolver-chain"}:
        assert response.status_code == 404
    elif lab_id == "webhook-replay-chain":
        assert response.status_code == 409
    else:
        assert response.status_code == 200


def test_advanced_lab_registry_is_complete_and_flag_ids_are_unique():
    ids = {lab["id"] for lab in ACADEMY_LABS}
    assert ids == ACADEMY_LAB_IDS
    assert len(ACADEMY_LABS) == 24
    assert len(LABS) == 45
    assert len({Config.FLAGS[lab_id] for lab_id in ACADEMY_LAB_IDS}) == len(ACADEMY_LAB_IDS)


def test_simulated_command_parser_never_executes_a_command(client):
    response = run_case(client, "command-simulation")
    assert response.json["execution"] == "simulated only; no shell or subprocess"


def test_xxe_fixture_never_accesses_external_resources(client):
    response = run_case(client, "xxe-sandbox")
    assert response.json["externalAccess"] is False


def test_practitioner_tenant_export_checks_ownership_at_create_and_download(client):
    client.post("/login", data={"username": "budi", "password": "budi123"})
    created = client.post(
        "/extra/academy/tenant-export-chain",
        data={"action": "create", "tenant_id": "tenant-campus"},
    )
    assert created.status_code == 201
    own_download = client.post(
        "/extra/academy/tenant-export-chain",
        data={"action": "download", "export_id": "export-tenant-campus"},
    )
    assert own_download.json["tenantId"] == "tenant-campus"
    assert "X-Lab-Flag" not in own_download.headers

    enable_secure_mode(client)
    denied = client.post(
        "/extra/academy/tenant-export-chain",
        data={"action": "create", "tenant_id": "tenant-roastery"},
    )
    assert denied.status_code == 403
    assert "X-Lab-Flag" not in denied.headers


def test_practitioner_settlement_binds_server_total_and_consumes_quote_once(client):
    quote = client.post(
        "/extra/academy/checkout-settlement-chain", data={"action": "quote"}
    ).json
    mismatch = client.post(
        "/extra/academy/checkout-settlement-chain",
        data={"action": "confirm", "quote_id": quote["quoteId"], "total": "1"},
    )
    assert mismatch.json["underpaid"] is True
    assert "X-Lab-Flag" in mismatch.headers

    enable_secure_mode(client)
    quote = client.post(
        "/extra/academy/checkout-settlement-chain", data={"action": "quote"}
    ).json
    mismatch = client.post(
        "/extra/academy/checkout-settlement-chain",
        data={"action": "confirm", "quote_id": quote["quoteId"], "total": "1"},
    )
    assert mismatch.status_code == 400
    valid = client.post(
        "/extra/academy/checkout-settlement-chain",
        data={"action": "confirm", "quote_id": quote["quoteId"], "total": "125000"},
    )
    assert valid.json["settled"] is True
    replay = client.post(
        "/extra/academy/checkout-settlement-chain",
        data={"action": "confirm", "quote_id": quote["quoteId"], "total": "125000"},
    )
    assert replay.status_code == 409


def test_practitioner_webhook_replay_is_idempotent_in_secure_mode(client):
    event = {"event_id": "evt-training-01", "amount": "50000"}
    headers = {"X-Training-Signature": "fixture-valid"}
    client.post("/extra/academy/webhook-replay-chain", data=event, headers=headers)
    replay = client.post("/extra/academy/webhook-replay-chain", data=event, headers=headers)
    assert replay.json["creditCount"] == 2
    assert "X-Lab-Flag" in replay.headers

    enable_secure_mode(client)
    first = client.post("/extra/academy/webhook-replay-chain", data=event, headers=headers)
    assert first.json["creditCount"] == 1
    replay = client.post("/extra/academy/webhook-replay-chain", data=event, headers=headers)
    assert replay.status_code == 409
    assert replay.json["creditCount"] == 1
    assert "X-Lab-Flag" not in replay.headers


def test_practitioner_nested_invoice_authorization_is_per_object(client):
    client.post("/login", data={"username": "budi", "password": "budi123"})
    response = client.post(
        "/extra/academy/graphql-resolver-chain",
        data={"viewer_id": "2", "invoice_id": "1", "alias": "ledger"},
    )
    assert response.json["data"]["viewer"]["ledger"]["reference"] == "ADMIN-TRAINING-INVOICE"
    assert "X-Lab-Flag" in response.headers

    enable_secure_mode(client)
    denied = client.post(
        "/extra/academy/graphql-resolver-chain",
        data={"viewer_id": "2", "invoice_id": "1", "alias": "ledger"},
    )
    assert denied.status_code == 404
    assert "data" not in denied.json
    assert "X-Lab-Flag" not in denied.headers


def test_final_boss_chains_persistent_underpayment_into_foreign_receipt(client, app):
    client.post("/login", data={"username": "budi", "password": "budi123"})
    before = client.post(
        "/extra/academy/final-boss-ledger-chain", data={"action": "map"}
    ).json["balance"]
    quote = client.post(
        "/extra/academy/final-boss-ledger-chain", data={"action": "quote"}
    ).json
    settled = client.post(
        "/extra/academy/final-boss-ledger-chain",
        data={"action": "settle", "quote_id": quote["quoteId"], "total": "1"},
    )
    assert settled.json["underpaid"] is True
    assert settled.json["submittedTotal"] == 1
    assert "X-Lab-Flag" not in settled.headers
    with app.app_context():
        db = get_db()
        stored_order = db.execute(
            "SELECT user_id,total FROM orders WHERE id=?", (settled.json["orderId"],)
        ).fetchone()
        after = db.execute("SELECT balance FROM users WHERE id=2").fetchone()["balance"]
    assert stored_order["user_id"] == 2
    assert stored_order["total"] == 1
    assert before - after == 1

    receipt = client.post(
        "/extra/academy/final-boss-ledger-chain",
        data={"action": "receipt", "order_id": "1"},
    )
    assert receipt.json["receipt"]["ownerId"] == 1
    assert receipt.json["currentPrincipalId"] == 2
    assert receipt.headers["X-Lab-Flag"] == Config.FLAGS["final-boss-ledger-chain"]


def test_final_boss_secure_rejects_price_before_database_write_and_checks_receipt_owner(client, app):
    client.post("/login", data={"username": "budi", "password": "budi123"})
    enable_secure_mode(client)
    with app.app_context():
        db = get_db()
        before_balance = db.execute("SELECT balance FROM users WHERE id=2").fetchone()["balance"]
        before_orders = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]

    quote = client.post(
        "/extra/academy/final-boss-ledger-chain", data={"action": "quote"}
    ).json
    rejected = client.post(
        "/extra/academy/final-boss-ledger-chain",
        data={"action": "settle", "quote_id": quote["quoteId"], "total": "1"},
    )
    assert rejected.status_code == 400
    assert "X-Lab-Flag" not in rejected.headers
    with app.app_context():
        db = get_db()
        assert db.execute("SELECT balance FROM users WHERE id=2").fetchone()["balance"] == before_balance
        assert db.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == before_orders

    valid = client.post(
        "/extra/academy/final-boss-ledger-chain",
        data={"action": "settle", "quote_id": quote["quoteId"], "total": "85000"},
    )
    assert valid.status_code == 200
    replay = client.post(
        "/extra/academy/final-boss-ledger-chain",
        data={"action": "settle", "quote_id": quote["quoteId"], "total": "85000"},
    )
    assert replay.status_code == 409
    with app.app_context():
        db = get_db()
        assert db.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == before_orders + 1
        assert db.execute("SELECT balance FROM users WHERE id=2").fetchone()["balance"] == before_balance - 85000
    foreign = client.post(
        "/extra/academy/final-boss-ledger-chain",
        data={"action": "receipt", "order_id": "1"},
    )
    assert foreign.status_code == 404
    assert "receipt" not in foreign.json
    assert "X-Lab-Flag" not in foreign.headers


def test_final_boss_expert_track_rejects_stale_and_cross_session_quotes_without_side_effects(client, app):
    client.post("/login", data={"username": "budi", "password": "budi123"})
    old_quote = client.post(
        "/extra/academy/final-boss-ledger-chain", data={"action": "quote"}
    ).json
    active_quote = client.post(
        "/extra/academy/final-boss-ledger-chain", data={"action": "quote"}
    ).json

    with app.app_context():
        db = get_db()
        before_orders = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        before_budi = db.execute("SELECT balance FROM users WHERE id=2").fetchone()["balance"]
        before_siti = db.execute("SELECT balance FROM users WHERE id=3").fetchone()["balance"]

    stale = client.post(
        "/extra/academy/final-boss-ledger-chain",
        data={"action": "settle", "quote_id": old_quote["quoteId"], "total": "85000"},
    )
    assert stale.status_code == 409

    second_client = app.test_client()
    second_client.post("/login", data={"username": "siti", "password": "siti123"})
    foreign_quote = second_client.post(
        "/extra/academy/final-boss-ledger-chain",
        data={"action": "settle", "quote_id": active_quote["quoteId"], "total": "85000"},
    )
    assert foreign_quote.status_code == 409
    assert "X-Lab-Flag" not in foreign_quote.headers

    with app.app_context():
        db = get_db()
        assert db.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == before_orders
        assert db.execute("SELECT balance FROM users WHERE id=2").fetchone()["balance"] == before_budi
        assert db.execute("SELECT balance FROM users WHERE id=3").fetchone()["balance"] == before_siti

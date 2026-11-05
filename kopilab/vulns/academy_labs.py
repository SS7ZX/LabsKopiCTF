"""Bounded, local-only simulations for the advanced web-security labs."""

from __future__ import annotations

import secrets
import sqlite3
from collections.abc import Mapping, MutableMapping
from typing import Any


def run_academy_lab(
    lab_id: str,
    values: Mapping[str, Any],
    headers: Mapping[str, str],
    browser_session: MutableMapping[str, Any],
    user_id: int | None,
    secure: bool,
) -> dict[str, Any]:
    """Evaluate one fixed training scenario without external I/O or code execution."""
    data: dict[str, Any] = {}
    response_headers: dict[str, str] = {}
    status = 200
    finding = False

    if lab_id == "cors-policy":
        origin = str(values.get("origin") or headers.get("Origin", ""))
        allowed_origin = "http://127.0.0.1:5000"
        if origin:
            if not secure and origin != allowed_origin:
                response_headers["Access-Control-Allow-Origin"] = origin
                response_headers["Access-Control-Allow-Credentials"] = "true"
                finding = True
            elif origin == allowed_origin:
                response_headers["Access-Control-Allow-Origin"] = allowed_origin
                response_headers["Vary"] = "Origin"
        data = {"originReceived": origin or None, "policy": "reflected" if finding else "restricted"}

    elif lab_id == "clickjacking-headers":
        if secure:
            response_headers["Content-Security-Policy"] = "frame-ancestors 'none'"
            response_headers["X-Frame-Options"] = "DENY"
        else:
            finding = True
        data = {"page": "KopiLab training dashboard", "frameable": not secure}

    elif lab_id == "security-headers":
        response_headers["Content-Type"] = "application/json; charset=utf-8"
        if secure:
            response_headers.update(
                {
                    "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'",
                    "X-Content-Type-Options": "nosniff",
                    "Referrer-Policy": "no-referrer",
                    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
                }
            )
        else:
            finding = True
        data = {"message": "KopiLab static training response"}

    elif lab_id == "host-reset-link":
        supplied_host = str(values.get("host", "127.0.0.1:5000"))
        if secure:
            origin = "http://127.0.0.1:5000"
        else:
            origin = f"http://{supplied_host}"
            finding = supplied_host != "127.0.0.1:5000"
        data = {"resetLinkPreview": f"{origin}/reset?token=TRAINING-ONLY", "emailSent": False}

    elif lab_id == "cache-poison":
        action = str(values.get("action", "read"))
        marker = str(values.get("marker", "training-banner"))[:80]
        cache_key = "academy_cache_poison_secure" if secure else "academy_cache_poison_vulnerable"
        if action == "prime":
            if not secure:
                browser_session[cache_key] = marker
            data = {"action": "prime", "cached": not secure, "marker": marker if not secure else None}
            finding = not secure
        else:
            cached = browser_session.get(cache_key)
            data = {"action": "read", "cached": cached is not None, "marker": cached or "default"}
            finding = cached is not None and not secure
        response_headers["X-Cache"] = "HIT" if data["cached"] else "MISS"

    elif lab_id == "cache-deception":
        path = str(values.get("path", "/profile"))
        disguised = path.endswith((".css", ".js", ".png"))
        cacheable = disguised and not secure
        response_headers["Cache-Control"] = "public, max-age=60" if cacheable else "private, no-store"
        data = {
            "path": path,
            "body": "Training profile: student-01" if disguised else "Training profile",
            "cacheable": cacheable,
        }
        finding = cacheable

    elif lab_id == "websocket-auth":
        claimed_authenticated = str(values.get("authenticated", "false")).lower() == "true"
        authorized = claimed_authenticated if not secure else user_id is not None
        data = {
            "transport": "simulated handshake; no socket opened",
            "authorized": authorized,
            "event": "TRAINING_EVENT" if authorized else None,
        }
        finding = authorized and not secure
        status = 200 if authorized else 401

    elif lab_id == "graphql-object-access":
        if user_id is None:
            data, status = {"error": "Login dengan akun latihan terlebih dahulu."}, 401
        else:
            object_id = str(values.get("id", "2"))
            owner_id = "1" if object_id == "1" else "2"
            authorized = not secure or str(user_id) == owner_id
            if authorized:
                data = {
                    "data": {
                        "profile": {
                            "id": object_id,
                            "username": "admin" if object_id == "1" else "budi",
                            "displayLabel": "Admin training account" if object_id == "1" else "Budi training account",
                        }
                    }
                }
                finding = object_id == "1" and not secure
            else:
                data, status = {"errors": [{"message": "Object not found"}]}, 404

    elif lab_id == "nosql-filter":
        query = str(values.get("filter", "role=user"))
        if query == "role=user":
            matched = True
        elif query in {"role!=user", "$ne:user"}:
            matched = not secure
            if secure:
                status = 400
        else:
            matched = False
            if secure and query not in {"role=user", "role=admin"}:
                status = 400
        data = {"matched": matched, "filter": query, "fixture": "training-users"}
        finding = matched and query != "role=user" and not secure

    elif lab_id == "xxe-sandbox":
        xml = str(values.get("xml", "<note>KopiLab</note>"))
        has_doctype = "<!DOCTYPE" in xml.upper()
        if has_doctype and secure:
            data, status = {"error": "DOCTYPE tidak diizinkan."}, 400
        else:
            data = {
                "parsed": True,
                "expanded": "KOPILAB_LOCAL_FIXTURE" if has_doctype and "training://marker" in xml else None,
                "externalAccess": False,
            }
            finding = has_doctype

    elif lab_id == "ssti-toy":
        name = str(values.get("name", "pelajar"))
        evaluated = name == "{{7*7}}" and not secure
        data = {"rendered": "49" if evaluated else name, "engine": "fixed-marker simulator"}
        finding = evaluated

    elif lab_id == "command-simulation":
        value = str(values.get("value", "coffee"))
        parsed = ";TRAINING_MARKER" in value and not secure
        data = {
            "input": value,
            "preview": "KOPILAB_TRAINING_MARKER" if parsed else value,
            "execution": "simulated only; no shell or subprocess",
        }
        finding = parsed

    elif lab_id == "oauth-redirect":
        redirect_uri = str(values.get("redirect_uri", "/extra/academy/oauth-callback"))
        local_simulator = redirect_uri == "http://127.0.0.1:9000/oauth-callback"
        relative = redirect_uri.startswith("/") and not redirect_uri.startswith("//")
        accepted = relative or (local_simulator and not secure)
        data = {"accepted": accepted, "redirectPreview": redirect_uri if accepted else None, "tokenIssued": False}
        finding = local_simulator and accepted and not secure
        if not accepted:
            status = 400

    elif lab_id == "oauth-state":
        if str(values.get("begin", "")) == "1":
            state_value = secrets.token_urlsafe(16)
            browser_session["academy_oauth_state"] = state_value
            data = {"started": True, "state": state_value, "provider": "local fixture"}
        else:
            supplied_state = str(values.get("state", ""))
            expected_state = str(browser_session.get("academy_oauth_state", ""))
            matched = bool(expected_state and secrets.compare_digest(supplied_state, expected_state))
            accepted = matched if secure else True
            data = {"accepted": accepted, "stateMatched": matched, "providerContacted": False}
            finding = accepted and not matched and not secure
            if not accepted:
                status = 400
            browser_session.pop("academy_oauth_state", None)

    elif lab_id == "reset-host":
        supplied_host = str(values.get("host", "127.0.0.1:5000"))
        accepted_host = "127.0.0.1:5000" if secure else supplied_host
        data = {
            "linkPreview": f"http://{accepted_host}/reset?token=FIXTURE",
            "tokenIssued": False,
            "messageSent": False,
        }
        finding = supplied_host != "127.0.0.1:5000" and not secure

    elif lab_id == "mfa-workflow":
        action = str(values.get("action", "status"))
        if action == "begin":
            browser_session["academy_mfa_challenge"] = True
            data = {"stage": "challenge", "codeHint": "424242 (training fixture)"}
        elif action == "complete":
            completed = not secure or (
                bool(browser_session.get("academy_mfa_challenge"))
                and str(values.get("code", "")) == "424242"
            )
            data = {"stage": "authenticated" if completed else "challenge-required", "authenticated": completed}
            finding = completed and not bool(browser_session.get("academy_mfa_challenge")) and not secure
            status = 200 if completed else 403
            if completed:
                browser_session.pop("academy_mfa_challenge", None)
        else:
            data = {"stage": "challenge" if browser_session.get("academy_mfa_challenge") else "start"}

    elif lab_id == "workflow-order":
        action = str(values.get("action", "status"))
        if action == "verify":
            browser_session["academy_workflow_verified"] = True
            data = {"currentStage": "verified", "accepted": True}
        elif action == "claim":
            verified = bool(browser_session.get("academy_workflow_verified"))
            accepted = verified if secure else True
            data = {"currentStage": "claimed" if accepted else "start", "accepted": accepted}
            finding = accepted and not verified and not secure
            status = 200 if accepted else 403
            if accepted:
                browser_session.pop("academy_workflow_verified", None)
        else:
            data = {"currentStage": "verified" if browser_session.get("academy_workflow_verified") else "start"}

    elif lab_id == "info-disclosure":
        diagnostic = str(values.get("view", "public")) == "diagnostic"
        exposed = diagnostic and not secure
        data = {
            "service": "KopiLab training",
            "diagnostic": {"build": "local-demo", "debugHint": "fixture-only"} if exposed else None,
        }
        finding = exposed

    elif lab_id == "http-parameter-pollution":
        amounts = values.getlist("amount") if hasattr(values, "getlist") else [values.get("amount", "100")]
        amounts = [str(value) for value in amounts]
        if secure and len(amounts) > 1:
            data, status = {"error": "Parameter duplikat tidak diizinkan."}, 400
        else:
            data = {
                "valuesReceived": amounts,
                "effectiveValue": amounts[-1] if amounts else "100",
                "firstValue": amounts[0] if amounts else "100",
            }
            finding = len(amounts) > 1 and len(set(amounts)) > 1 and not secure

    elif lab_id == "tenant-export-chain":
        if user_id is None:
            data, status = {"error": "Login dengan akun latihan terlebih dahulu."}, 401
        else:
            action = str(values.get("action", "list"))
            owned_tenant = "tenant-campus" if user_id == 2 else "tenant-unknown"
            exports = browser_session.setdefault("academy_tenant_exports", {})
            if action == "list":
                data = {
                    "principal": f"user-{user_id}",
                    "tenants": [
                        {"id": "tenant-campus", "label": "KopiLab Campus"},
                        {"id": "tenant-roastery", "label": "KopiLab Roastery"},
                    ],
                    "note": "Tenant directory is a training fixture.",
                }
            elif action == "create":
                tenant_id = str(values.get("tenant_id", ""))
                if tenant_id not in {"tenant-campus", "tenant-roastery"}:
                    data, status = {"error": "Tenant fixture tidak ditemukan."}, 400
                elif secure and tenant_id != owned_tenant:
                    data, status = {"error": "Tidak berhak membuat ekspor tenant ini."}, 403
                else:
                    export_id = f"export-{tenant_id}"
                    exports[export_id] = tenant_id
                    data, status = {
                        "created": True,
                        "exportId": export_id,
                        "tenantId": tenant_id,
                        "owner": f"user-{user_id}",
                    }, 201
            elif action == "download":
                export_id = str(values.get("export_id", ""))
                tenant_id = exports.get(export_id)
                if tenant_id is None:
                    data, status = {"error": "Ekspor tidak ditemukan."}, 404
                elif secure and tenant_id != owned_tenant:
                    data, status = {"error": "Ekspor bukan milik tenant sesi ini."}, 404
                else:
                    data = {
                        "downloaded": True,
                        "exportId": export_id,
                        "tenantId": tenant_id,
                        "recordCount": 3,
                        "records": ["TRAINING-RECORD-A", "TRAINING-RECORD-B", "TRAINING-RECORD-C"],
                    }
                    finding = tenant_id != owned_tenant and not secure
            else:
                data, status = {"error": "Action tidak dikenal."}, 400

    elif lab_id == "checkout-settlement-chain":
        action = str(values.get("action", "quote"))
        quote = browser_session.get("academy_settlement_quote")
        if action == "quote":
            quote = {"id": "quote-training-001", "total": 125000, "used": False}
            browser_session["academy_settlement_quote"] = quote
            data = {"quoted": True, "quoteId": quote["id"], "total": quote["total"], "currency": "IDR"}
        elif action == "confirm":
            quote_id = str(values.get("quote_id", ""))
            try:
                submitted_total = int(str(values.get("total", "")))
            except ValueError:
                submitted_total = -1
            if not isinstance(quote, dict) or quote_id != quote.get("id"):
                data, status = {"error": "Quote tidak ditemukan pada sesi ini."}, 409
            elif quote.get("used"):
                data, status = {"error": "Quote sudah digunakan."}, 409
            elif secure and submitted_total != quote["total"]:
                data, status = {"error": "Total tidak sesuai dengan quote server."}, 400
            else:
                browser_session["academy_settlement_quote"] = {**quote, "used": True}
                data = {
                    "settled": True,
                    "quoteId": quote_id,
                    "submittedTotal": submitted_total,
                    "serverTotal": quote["total"],
                    "underpaid": submitted_total < quote["total"],
                }
                finding = submitted_total != quote["total"] and not secure
        else:
            data, status = {"error": "Action harus quote atau confirm."}, 400

    elif lab_id == "webhook-replay-chain":
        event_id = str(values.get("event_id", ""))
        try:
            amount = int(str(values.get("amount", "")))
        except ValueError:
            amount = -1
        signature_valid = headers.get("X-Training-Signature", "") == "fixture-valid"
        if event_id != "evt-training-01" or amount != 50000:
            data, status = {"error": "Event tidak cocok dengan fixture latihan."}, 400
        elif not signature_valid:
            data, status = {"error": "Signature fixture tidak valid."}, 401
        else:
            event_key = "academy_webhook_events_secure" if secure else "academy_webhook_events_vulnerable"
            processed = browser_session.setdefault(event_key, [])
            duplicate = event_id in processed
            if secure and duplicate:
                data, status = {
                    "accepted": False,
                    "duplicate": True,
                    "creditCount": len(processed),
                }, 409
            else:
                processed.append(event_id)
                data = {
                    "accepted": True,
                    "duplicate": duplicate,
                    "eventId": event_id,
                    "creditCount": len(processed),
                    "creditedAmount": amount,
                    "signatureMode": "fixed training fixture; not cryptographic",
                }
                finding = duplicate and not secure

    elif lab_id == "graphql-resolver-chain":
        if user_id is None:
            data, status = {"errors": [{"message": "Login dengan akun latihan terlebih dahulu."}]}, 401
        else:
            viewer_id = str(values.get("viewer_id", ""))
            invoice_id = str(values.get("invoice_id", ""))
            alias = str(values.get("alias", "ledger"))
            if alias not in {"ledger", "invoice"}:
                data, status = {"errors": [{"message": "Alias fixture tidak dikenal."}]}, 400
            elif viewer_id != str(user_id):
                data, status = {"errors": [{"message": "Viewer tidak diizinkan."}]}, 403
            elif secure and invoice_id != str(user_id):
                data, status = {"errors": [{"message": "Invoice tidak ditemukan."}]}, 404
            elif invoice_id not in {"1", "2"}:
                data, status = {"errors": [{"message": "Invoice tidak ditemukan."}]}, 404
            else:
                data = {
                    "data": {
                        "viewer": {
                            "id": viewer_id,
                            alias: {
                                "invoiceId": invoice_id,
                                "reference": "ADMIN-TRAINING-INVOICE" if invoice_id == "1" else "BUDI-TRAINING-INVOICE",
                                "total": 880000 if invoice_id == "1" else 125000,
                            },
                        }
                    }
                }
                finding = invoice_id != str(user_id) and not secure

    else:
        return {"data": {"error": "Lab tidak ditemukan."}, "headers": {}, "status": 404, "finding": False}

    return {"data": data, "headers": response_headers, "status": status, "finding": finding}


def run_final_boss_lab(
    values: Mapping[str, Any],
    browser_session: MutableMapping[str, Any],
    user_id: int | None,
    secure: bool,
    connection: sqlite3.Connection,
) -> dict[str, Any]:
    """Run the local checkout-to-receipt chain against the seeded SQLite records."""
    data: dict[str, Any] = {}
    status = 200
    finding = False

    if user_id is None:
        return {
            "data": {"error": "Login dengan akun latihan terlebih dahulu."},
            "status": 401,
            "finding": False,
        }

    action = str(values.get("action", "map"))
    user = connection.execute(
        "SELECT id,balance FROM users WHERE id=?", (user_id,)
    ).fetchone()
    if user is None:
        return {"data": {"error": "Akun latihan tidak ditemukan."}, "status": 401, "finding": False}

    if action == "map":
        product = connection.execute(
            "SELECT id,name,price FROM products WHERE id=1"
        ).fetchone()
        data = {
            "principalId": user["id"],
            "balance": user["balance"],
            "product": dict(product) if product else None,
            "database": "SQLite; read-only baseline",
        }
    elif action == "quote":
        product = connection.execute(
            "SELECT id,name,price FROM products WHERE id=1"
        ).fetchone()
        if product is None:
            return {"data": {"error": "Produk fixture tidak ditemukan."}, "status": 404, "finding": False}
        quote_id = secrets.token_urlsafe(12)
        connection.execute(
            "INSERT INTO final_boss_quotes(id,user_id,product_id,item,qty,total) VALUES(?,?,?,?,?,?)",
            (quote_id, user_id, product["id"], product["name"], 1, product["price"]),
        )
        connection.commit()
        browser_session["final_boss_quote_id"] = quote_id
        data = {
            "quoted": True,
            "quoteId": quote_id,
            "item": product["name"],
            "qty": 1,
            "serverTotal": product["price"],
            "currency": "IDR",
        }
    elif action == "settle":
        quote_id = str(values.get("quote_id", ""))
        try:
            submitted_total = int(str(values.get("total", "")))
        except ValueError:
            return {"data": {"error": "Total harus berupa bilangan bulat."}, "status": 400, "finding": False}

        if quote_id != browser_session.get("final_boss_quote_id"):
            return {"data": {"error": "Quote tidak ditemukan untuk sesi dan akun ini."}, "status": 409, "finding": False}
        if submitted_total < 1:
            return {"data": {"error": "Total harus lebih besar dari nol."}, "status": 400, "finding": False}

        connection.execute("BEGIN IMMEDIATE")
        quote = connection.execute(
            "SELECT id,user_id,product_id,item,qty,total,used FROM final_boss_quotes WHERE id=? AND user_id=?",
            (quote_id, user_id),
        ).fetchone()
        if quote is None:
            connection.rollback()
            return {"data": {"error": "Quote tidak ditemukan untuk sesi dan akun ini."}, "status": 409, "finding": False}
        if quote["used"]:
            connection.rollback()
            return {"data": {"error": "Quote sudah digunakan."}, "status": 409, "finding": False}
        if secure and submitted_total != quote["total"]:
            connection.rollback()
            return {
                "data": {"error": "Total tidak sesuai dengan quote server.", "serverTotal": quote["total"]},
                "status": 400,
                "finding": False,
            }
        current_user = connection.execute(
            "SELECT balance FROM users WHERE id=?", (user_id,)
        ).fetchone()
        if current_user is None or current_user["balance"] < submitted_total:
            connection.rollback()
            return {"data": {"error": "Saldo tidak mencukupi."}, "status": 409, "finding": False}
        consumed_quote = connection.execute(
            "UPDATE final_boss_quotes SET used=1 WHERE id=? AND user_id=? AND used=0",
            (quote_id, user_id),
        )
        if consumed_quote.rowcount != 1:
            connection.rollback()
            return {"data": {"error": "Quote sudah digunakan."}, "status": 409, "finding": False}
        cursor = connection.execute(
            "INSERT INTO orders(user_id,item,qty,total,note) VALUES(?,?,?,?,?)",
            (
                user_id,
                quote["item"],
                quote["qty"],
                submitted_total,
                "Hacker Class training settlement",
            ),
        )
        connection.execute(
            "UPDATE users SET balance=balance-? WHERE id=?",
            (submitted_total, user_id),
        )
        connection.commit()

        underpaid = submitted_total != quote["total"]
        browser_session["final_boss_settlement"] = {
            "order_id": cursor.lastrowid,
            "underpaid": underpaid,
        }
        data = {
            "settled": True,
            "orderId": cursor.lastrowid,
            "submittedTotal": submitted_total,
            "serverTotal": quote["total"],
            "underpaid": underpaid,
            "databaseChanged": True,
        }
    elif action == "receipt":
        settlement = browser_session.get("final_boss_settlement")
        if not isinstance(settlement, dict):
            return {"data": {"error": "Selesaikan quote latihan sebelum membaca receipt."}, "status": 409, "finding": False}
        try:
            order_id = int(str(values.get("order_id", settlement["order_id"])))
        except ValueError:
            return {"data": {"error": "order_id harus berupa bilangan bulat."}, "status": 400, "finding": False}
        if secure:
            order = connection.execute(
                "SELECT id,user_id,item,qty,total FROM orders WHERE id=? AND user_id=?",
                (order_id, user_id),
            ).fetchone()
        else:
            order = connection.execute(
                "SELECT id,user_id,item,qty,total FROM orders WHERE id=?",
                (order_id,),
            ).fetchone()
        if order is None:
            return {"data": {"error": "Receipt tidak ditemukan."}, "status": 404, "finding": False}
        data = {
            "receipt": {
                "orderId": order["id"],
                "ownerId": order["user_id"],
                "item": order["item"],
                "qty": order["qty"],
                "total": order["total"],
                "reference": "ADMIN-TRAINING-RECEIPT" if order["user_id"] == 1 else "CUSTOMER-TRAINING-RECEIPT",
            },
            "currentPrincipalId": user_id,
        }
        finding = (
            order["user_id"] != user_id
            and settlement.get("underpaid") is True
            and not secure
        )
    else:
        return {
            "data": {"error": "Action harus map, quote, settle, atau receipt."},
            "status": 400,
            "finding": False,
        }

    return {"data": data, "status": status, "finding": finding}

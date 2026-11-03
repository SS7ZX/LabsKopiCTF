"""Default application settings."""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Configuration shared by the local app and its tests."""

    DATABASE = str(BASE_DIR / "kopilab.db")
    FILES_DIR = str(BASE_DIR / "files")
    PROJECT_DIR = str(BASE_DIR)
    LABS_DIR = str(BASE_DIR / "labs")
    INTERNAL_HOST = "127.0.0.1"
    INTERNAL_PORT = 5001
    UPLOADS_DIR = str(BASE_DIR / "uploads")
    JWT_SECRET = "kopilab-secure-" + "local-server-only"
    TESTING = False
    ENABLE_INSPECTOR = True
    WARNING_BANNER = "KopiLab adalah aplikasi sengaja rentan. Hanya untuk lokal."
    FLAGS = {
        "sqli-union": "FLAG{union_select_master}",
        "sqli-login": "FLAG{auth_bypass_with_a_quote}",
        "xss": "FLAG{cookie_stolen_via_xss}",
        "idor-order": "FLAG{idor_order_enumeration}",
        "idor-api": "FLAG{idor_api_user_leak}",
        "logic-price": "FLAG{never_trust_client_price}",
        "logic-balance": "FLAG{negative_qty_and_coupon_stacking}",
        "mass-assign": "FLAG{mass_assignment_role_escalation}",
        "bac-cookie": "FLAG{admin_cookie_forged}",
        "csrf": "FLAG{cross_site_request_accepted}",
        "traversal": "FLAG{path_traversal_etc_passwd_vibes}",
        "ssrf": "FLAG{ssrf_to_internal_service}",
        "reset": "FLAG{predictable_reset_token}",
        "blind-sqli": "FLAG{boolean_oracle_local_only}",
        "upload": "FLAG{unvalidated_upload_confined}",
        "jwt": "FLAG{weak_local_jwt_secret}",
        "race-coupon": "FLAG{coupon_redeemed_twice}",
        "open-redirect": "FLAG{local_open_redirect}",
        "rate-limit": "FLAG{weak_login_rate_limit}",
        "filter-bypass": "FLAG{case_filter_bypass}",
    }


LABS = [
    ("sqli-union", "SQLi UNION di /search", "Injection", "Mudah"),
    ("sqli-login", "SQLi auth bypass di /login", "Injection", "Mudah"),
    ("xss", "Reflected XSS (/search) & Stored XSS (review)", "XSS", "Mudah"),
    ("idor-order", "IDOR /order/<id>", "Access Control", "Mudah"),
    ("idor-api", "IDOR /api/user/<id>", "Access Control", "Mudah"),
    ("logic-price", "Price tampering di checkout", "Business Logic", "Mudah"),
    ("logic-balance", "Saldo inflasi: qty negatif / coupon stacking", "Business Logic", "Sedang"),
    ("mass-assign", "Mass assignment di /profile", "Access Control", "Sedang"),
    ("bac-cookie", "Admin panel percaya cookie", "Access Control", "Mudah"),
    ("csrf", "CSRF di /transfer", "CSRF", "Sedang"),
    ("traversal", "Path traversal di /download", "File", "Mudah"),
    ("ssrf", "SSRF di /preview", "SSRF", "Sedang"),
    ("reset", "Token reset password bisa ditebak", "Auth", "Sedang"),
    ("blind-sqli", "Blind SQLi boolean pada oracle lokal", "Injection", "Sedang"),
    ("upload", "Validasi upload lemah", "File", "Mudah"),
    ("jwt", "JWT secret lemah", "Auth", "Sedang"),
    ("race-coupon", "Race condition redeem kupon", "Business Logic", "Sulit"),
    ("open-redirect", "Open redirect terbatas ke simulator", "Redirect", "Mudah"),
    ("rate-limit", "Rate limit login lemah", "Auth", "Sedang"),
    ("filter-bypass", "Bypass filter sederhana", "Injection", "Sulit"),
]

LAB_METADATA = {
    "sqli-union": {"category_id": "A03", "level": "Easy", "cvss": "8.6 High", "endpoint": "GET /search?q=..."},
    "sqli-login": {"category_id": "A03", "level": "Easy", "cvss": "9.8 Critical", "endpoint": "POST /login"},
    "xss": {"category_id": "A03", "level": "Easy", "cvss": "6.1 Medium", "endpoint": "GET /search dan POST /review"},
    "idor-order": {"category_id": "A01", "level": "Easy", "cvss": "6.5 Medium", "endpoint": "GET /order/<id>"},
    "idor-api": {"category_id": "A01", "level": "Easy", "cvss": "6.5 Medium", "endpoint": "GET /api/user/<id>"},
    "logic-price": {"category_id": "A04", "level": "Easy", "cvss": "8.1 High", "endpoint": "POST /checkout"},
    "logic-balance": {"category_id": "A04", "level": "Medium", "cvss": "8.1 High", "endpoint": "POST /checkout"},
    "mass-assign": {"category_id": "A04", "level": "Medium", "cvss": "8.1 High", "endpoint": "POST /profile"},
    "bac-cookie": {"category_id": "A01", "level": "Easy", "cvss": "8.1 High", "endpoint": "GET /admin"},
    "csrf": {"category_id": "A01", "level": "Medium", "cvss": "8.1 High", "endpoint": "POST /transfer"},
    "traversal": {"category_id": "A01", "level": "Easy", "cvss": "7.5 High", "endpoint": "GET /download?file=..."},
    "ssrf": {"category_id": "A10", "level": "Medium", "cvss": "7.5 High", "endpoint": "GET /preview?url=... (loopback lab only)"},
    "reset": {"category_id": "A07", "level": "Medium", "cvss": "8.1 High", "endpoint": "POST /reset"},
    "blind-sqli": {"category_id": "A03", "level": "Medium", "cvss": "8.6 High", "endpoint": "GET /extra/blind-sqli"},
    "upload": {"category_id": "A04", "level": "Easy", "cvss": "8.1 High", "endpoint": "POST /extra/upload"},
    "jwt": {"category_id": "A07", "level": "Medium", "cvss": "8.1 High", "endpoint": "POST /extra/jwt"},
    "race-coupon": {"category_id": "A04", "level": "Hard", "cvss": "7.5 High", "endpoint": "POST /extra/coupon"},
    "open-redirect": {"category_id": "A01", "level": "Easy", "cvss": "6.1 Medium", "endpoint": "GET /extra/redirect"},
    "rate-limit": {"category_id": "A07", "level": "Medium", "cvss": "7.5 High", "endpoint": "POST /extra/rate-login"},
    "filter-bypass": {"category_id": "A03", "level": "Hard", "cvss": "8.6 High", "endpoint": "GET /extra/filter"},
}

"""Cookie-based authorization behavior for the admin lab."""


def cookie_is_admin(value: str | None, secure: bool = False, role: str | None = None) -> bool:
    """Use a client cookie vulnerably or a server-verified role in secure mode."""
    if secure:
        return role == "admin"
    # VULN[bac-cookie]
    return value == "1"

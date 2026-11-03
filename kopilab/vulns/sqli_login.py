"""SQL injection behavior for the login lab."""


def login_query(username: str, password: str, secure: bool = False) -> str:
    """Build a vulnerable login query or a parameterized secure query."""
    if secure:
        return "SELECT * FROM users WHERE username=? AND password=?"
    # VULN[sqli-login]
    return f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"

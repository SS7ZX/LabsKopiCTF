"""Case-sensitive filter behavior for the hard filter-bypass lab."""


def blocked_username(query: str, secure: bool = False) -> bool:
    """Check a reserved admin keyword using an unsafe or normalized comparison."""
    if secure:
        return "admin" in query.casefold()
    # VULN[filter-bypass]
    return "admin" in query

"""SQL injection behavior for the product search lab."""


def search_query(query: str, secure: bool = False) -> str:
    """Build a vulnerable query or a parameterized query for secure mode."""
    if secure:
        return "SELECT id,name,price,description FROM products WHERE name LIKE ? AND id<99"
    # VULN[sqli-union]
    return f"SELECT id,name,price,description FROM products WHERE name LIKE '%{query}%' AND id<99"

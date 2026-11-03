"""Client-controlled pricing behavior for the checkout lab."""


def client_price(value: str, catalog_price: int | None = None) -> int:
    """Use a catalog price when secure mode is enabled."""
    if catalog_price is not None:
        return catalog_price
    # VULN[logic-price]
    return int(value)


def order_note(product_id: int, flag: str, secure: bool = False) -> str:
    """Attach the training flag only to vulnerable-mode special-product orders."""
    if secure:
        return "-"
    # VULN[logic-price]
    return flag if product_id == 99 else "-"

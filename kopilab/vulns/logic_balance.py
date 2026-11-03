"""Quantity and coupon behavior for the balance logic lab."""

from collections.abc import Mapping, Sequence


def calculate_total(price: int, quantity: int, coupons: Sequence[str], known_coupons: Mapping[str, int]) -> int:
    """Calculate checkout total without validating negative quantities or coupon reuse."""
    # VULN[logic-balance]
    discount = sum(known_coupons.get(code, 0) for code in coupons)
    return price * quantity - discount


def validate_checkout(quantity: int, coupons: Sequence[str], known_coupons: Mapping[str, int]) -> bool:
    """Validate positive quantity and prevent repeated discount codes."""
    return quantity > 0 and len(coupons) == len(set(coupons)) and all(
        code in known_coupons for code in coupons
    )

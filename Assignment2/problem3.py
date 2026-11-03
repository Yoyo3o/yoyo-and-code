"""
Problem 3: E-Commerce Order Management (Developed by AI)

This module implements an Order class managing cart items, tier discounts,
coupons, taxes, shipping fees, and order status transitions.
"""
from typing import Dict, Any, Optional


class Order:
    """
    An e-commerce order system tracking multi-attribute state including items,
    subtotal, tier discounts, coupon discounts, taxes, shipping, and order status.

    Attributes:
        order_id (str): Unique order ID.
        customer_tier (str): "regular", "silver", or "gold".
        items (Dict[str, Dict[str, Any]]): Map of item names to details (price, quantity, category).
        subtotal (float): Gross sum of (price * quantity).
        discount_amount (float): Total discount from membership tier and coupons.
        tax_amount (float): 8% tax applied to taxable items after discounts.
        shipping_fee (float): $0.00 if net subtotal >= $50.00, otherwise $5.99.
        final_total (float): Net total = (subtotal - discount_amount) + tax_amount + shipping_fee.
        status (str): "PENDING", "PAID", or "CANCELLED".
        applied_coupon (Optional[str]): Currently applied coupon code.
    """

    VALID_TIERS = {"regular": 0.0, "silver": 0.05, "gold": 0.10}
    TAX_RATE = 0.08
    STANDARD_SHIPPING = 5.99
    FREE_SHIPPING_THRESHOLD = 50.00

    def __init__(self, order_id: str, customer_tier: str = "regular"):
        if customer_tier.lower() not in self.VALID_TIERS:
            raise ValueError(f"Invalid customer_tier: {customer_tier}. Must be one of {list(self.VALID_TIERS.keys())}")

        self.order_id = order_id
        self.customer_tier = customer_tier.lower()
        self.items: Dict[str, Dict[str, Any]] = {}
        self.status = "PENDING"
        self.applied_coupon: Optional[str] = None

        self.subtotal = 0.0
        self.discount_amount = 0.0
        self.tax_amount = 0.0
        self.shipping_fee = 0.0
        self.final_total = 0.0

    def add_item(self, name: str, price: float, quantity: int = 1, category: str = "general") -> None:
        """Add an item to the order."""
        if self.status != "PENDING":
            raise RuntimeError("Cannot modify an order that is not PENDING")
        if price <= 0:
            raise ValueError("Item price must be positive")
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer")

        if name in self.items:
            self.items[name]["quantity"] += quantity
        else:
            self.items[name] = {
                "price": float(price),
                "quantity": int(quantity),
                "category": category.lower()
            }
        self._recalculate()

    def remove_item(self, name: str, quantity: Optional[int] = None) -> None:
        """Remove an item or decrease its quantity."""
        if self.status != "PENDING":
            raise RuntimeError("Cannot modify an order that is not PENDING")
        if name not in self.items:
            raise KeyError(f"Item '{name}' not found in order")

        if quantity is None or quantity >= self.items[name]["quantity"]:
            del self.items[name]
        elif quantity <= 0:
            raise ValueError("Quantity to remove must be positive")
        else:
            self.items[name]["quantity"] -= quantity

        self._recalculate()

    def apply_coupon(self, coupon_code: str) -> None:
        """Apply a coupon code ('SAVE10' for 10% off or 'FLAT15' for $15 off)."""
        if self.status != "PENDING":
            raise RuntimeError("Cannot apply coupon to an order that is not PENDING")

        code = coupon_code.strip().upper()
        if code not in {"SAVE10", "FLAT15"}:
            raise ValueError(f"Invalid coupon code: {coupon_code}")

        self.applied_coupon = code
        self._recalculate()

    def _recalculate(self) -> None:
        """Recalculate subtotal, discounts, taxes, shipping, and final total."""
        if not self.items:
            self.subtotal = 0.0
            self.discount_amount = 0.0
            self.tax_amount = 0.0
            self.shipping_fee = 0.0
            self.final_total = 0.0
            return

        # 1. Subtotal
        self.subtotal = round(sum(item["price"] * item["quantity"] for item in self.items.values()), 2)

        # 2. Member tier discount
        tier_rate = self.VALID_TIERS[self.customer_tier]
        tier_discount = self.subtotal * tier_rate

        # 3. Coupon discount
        coupon_discount = 0.0
        remaining_subtotal = self.subtotal - tier_discount
        if self.applied_coupon == "SAVE10":
            coupon_discount = remaining_subtotal * 0.10
        elif self.applied_coupon == "FLAT15":
            coupon_discount = min(15.0, remaining_subtotal)

        self.discount_amount = round(tier_discount + coupon_discount, 2)
        net_subtotal = max(0.0, self.subtotal - self.discount_amount)

        # 4. Tax (8% on non-grocery items, proportioned after discount)
        discount_ratio = (net_subtotal / self.subtotal) if self.subtotal > 0 else 1.0
        taxable_amount = sum(
            item["price"] * item["quantity"]
            for item in self.items.values()
            if item["category"] != "grocery"
        ) * discount_ratio
        self.tax_amount = round(taxable_amount * self.TAX_RATE, 2)

        # 5. Shipping fee
        if net_subtotal >= self.FREE_SHIPPING_THRESHOLD:
            self.shipping_fee = 0.0
        else:
            self.shipping_fee = self.STANDARD_SHIPPING

        # 6. Final total
        self.final_total = round(net_subtotal + self.tax_amount + self.shipping_fee, 2)

    def checkout(self) -> bool:
        """Complete the order checkout."""
        if self.status != "PENDING":
            raise RuntimeError("Only PENDING orders can be checked out")
        if not self.items:
            raise ValueError("Cannot checkout an empty order")

        self.status = "PAID"
        return True

    def cancel(self) -> bool:
        """Cancel the order."""
        if self.status == "PAID":
            raise RuntimeError("Cannot cancel a PAID order")
        self.status = "CANCELLED"
        return True

    def get_summary(self) -> Dict[str, Any]:
        """Return structured summary of order state."""
        return {
            "order_id": self.order_id,
            "tier": self.customer_tier,
            "status": self.status,
            "item_count": sum(item["quantity"] for item in self.items.values()),
            "subtotal": self.subtotal,
            "discount_amount": self.discount_amount,
            "tax_amount": self.tax_amount,
            "shipping_fee": self.shipping_fee,
            "final_total": self.final_total
        }

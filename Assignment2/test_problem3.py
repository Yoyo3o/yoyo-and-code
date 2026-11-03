"""
Unit tests for Problem 3: Order

Instructions:
Complete the unit test methods below using Python's unittest framework.
Your test methods must assert MULTIPLE ATTRIBUTES on the Order object
(e.g., subtotal, discount_amount, tax_amount, shipping_fee, final_total, status)
to verify state consistency under various conditions.

Running tests:
    python -m unittest test_problem3.py -v
"""
import unittest
from problem3 import Order


class TestOrder(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.regular_order = Order("ORD100", customer_tier="regular")
        self.silver_order = Order("ORD200", customer_tier="silver")
        self.gold_order = Order("ORD300", customer_tier="gold")

    def test_initial_state_and_customer_tier(self):
        """New orders start empty, pending, and with no charges or discounts."""
        for order, order_id, tier in (
            (self.regular_order, "ORD100", "regular"),
            (self.silver_order, "ORD200", "silver"),
            (self.gold_order, "ORD300", "gold"),
        ):
            self.assertEqual(order.order_id, order_id)
            self.assertEqual(order.customer_tier, tier)
            self.assertEqual(order.items, {})
            self.assertEqual(order.status, "PENDING")
            self.assertIsNone(order.applied_coupon)
            self.assertEqual(order.subtotal, 0.0)
            self.assertEqual(order.discount_amount, 0.0)
            self.assertEqual(order.tax_amount, 0.0)
            self.assertEqual(order.shipping_fee, 0.0)
            self.assertEqual(order.final_total, 0.0)
            self.assertEqual(
                order.get_summary(),
                {
                    "order_id": order_id,
                    "tier": tier,
                    "status": "PENDING",
                    "item_count": 0,
                    "subtotal": 0.0,
                    "discount_amount": 0.0,
                    "tax_amount": 0.0,
                    "shipping_fee": 0.0,
                    "final_total": 0.0,
                },
            )

    def test_add_items_calculates_tax_shipping_and_summary(self):
        """Items calculate subtotal, tax only non-grocery goods, and shipping."""
        self.regular_order.add_item("Notebook", 40, category="stationery")
        self.regular_order.add_item("Apples", 10, category="grocery")

        self.assertEqual(
            self.regular_order.items,
            {
                "Notebook": {"price": 40.0, "quantity": 1, "category": "stationery"},
                "Apples": {"price": 10.0, "quantity": 1, "category": "grocery"},
            },
        )
        self.assertEqual(self.regular_order.subtotal, 50.0)
        self.assertEqual(self.regular_order.discount_amount, 0.0)
        self.assertEqual(self.regular_order.tax_amount, 3.20)
        self.assertEqual(self.regular_order.shipping_fee, 0.0)
        self.assertEqual(self.regular_order.final_total, 53.20)
        self.assertEqual(self.regular_order.status, "PENDING")
        self.assertEqual(self.regular_order.get_summary()["item_count"], 2)
        self.assertEqual(self.regular_order.get_summary()["final_total"], 53.20)

    def test_tier_and_coupon_discounts_are_recalculated(self):
        """Gold membership and SAVE10 are applied sequentially before tax."""
        self.gold_order.add_item("Headphones", 100, category="electronics")
        self.gold_order.apply_coupon(" save10 ")

        self.assertEqual(self.gold_order.applied_coupon, "SAVE10")
        self.assertEqual(self.gold_order.subtotal, 100.0)
        self.assertEqual(self.gold_order.discount_amount, 19.0)
        self.assertEqual(self.gold_order.tax_amount, 6.48)
        self.assertEqual(self.gold_order.shipping_fee, 0.0)
        self.assertEqual(self.gold_order.final_total, 87.48)
        self.assertEqual(self.gold_order.status, "PENDING")
        self.assertEqual(self.gold_order.get_summary()["item_count"], 1)

        self.silver_order.add_item("Coat", 100, category="clothing")
        self.silver_order.apply_coupon("FLAT15")
        self.assertEqual(self.silver_order.discount_amount, 20.0)
        self.assertEqual(self.silver_order.tax_amount, 6.40)
        self.assertEqual(self.silver_order.final_total, 86.40)

    def test_add_duplicate_and_remove_items_recalculate_state(self):
        """Adding an existing item increases quantity and removing updates totals."""
        self.regular_order.add_item("Pen", 2, quantity=2)
        self.regular_order.add_item("Pen", 2, quantity=3)

        self.assertEqual(self.regular_order.items["Pen"]["quantity"], 5)
        self.assertEqual(self.regular_order.subtotal, 10.0)
        self.assertEqual(self.regular_order.tax_amount, 0.80)
        self.assertEqual(self.regular_order.shipping_fee, 5.99)
        self.assertEqual(self.regular_order.final_total, 16.79)

        self.regular_order.remove_item("Pen", quantity=2)
        self.assertEqual(self.regular_order.items["Pen"]["quantity"], 3)
        self.assertEqual(self.regular_order.subtotal, 6.0)
        self.assertEqual(self.regular_order.tax_amount, 0.48)
        self.assertEqual(self.regular_order.shipping_fee, 5.99)
        self.assertEqual(self.regular_order.final_total, 12.47)

        self.regular_order.remove_item("Pen")
        self.assertEqual(self.regular_order.items, {})
        self.assertEqual(self.regular_order.subtotal, 0.0)
        self.assertEqual(self.regular_order.tax_amount, 0.0)
        self.assertEqual(self.regular_order.shipping_fee, 0.0)
        self.assertEqual(self.regular_order.final_total, 0.0)

    def test_checkout_and_cancel_lifecycle(self):
        """Checkout pays a non-empty order and prevents further modifications."""
        self.assertTrue(self.regular_order.cancel())
        self.assertEqual(self.regular_order.status, "CANCELLED")
        self.assertEqual(self.regular_order.items, {})
        self.assertEqual(self.regular_order.final_total, 0.0)

        with self.assertRaises(RuntimeError):
            self.regular_order.add_item("Book", 20)
        with self.assertRaises(RuntimeError):
            self.regular_order.apply_coupon("SAVE10")
        with self.assertRaises(RuntimeError):
            self.regular_order.checkout()

        self.silver_order.add_item("Book", 20)
        self.assertTrue(self.silver_order.checkout())
        self.assertEqual(self.silver_order.status, "PAID")
        self.assertEqual(self.silver_order.subtotal, 20.0)
        self.assertEqual(self.silver_order.discount_amount, 1.0)
        self.assertEqual(self.silver_order.tax_amount, 1.52)
        self.assertEqual(self.silver_order.shipping_fee, 5.99)
        self.assertEqual(self.silver_order.final_total, 26.51)
        with self.assertRaises(RuntimeError):
            self.silver_order.cancel()
        with self.assertRaises(RuntimeError):
            self.silver_order.remove_item("Book")

    def test_invalid_inputs_raise_exceptions_without_state_changes(self):
        """Invalid tiers, items, coupons, removals, and empty checkout are rejected."""
        with self.assertRaises(ValueError):
            Order("ORD400", customer_tier="platinum")

        with self.assertRaises(ValueError):
            self.regular_order.add_item("Invalid", 0)
        with self.assertRaises(ValueError):
            self.regular_order.add_item("Invalid", 10, quantity=0)
        with self.assertRaises(ValueError):
            self.regular_order.apply_coupon("UNKNOWN")
        with self.assertRaises(ValueError):
            self.regular_order.checkout()
        with self.assertRaises(KeyError):
            self.regular_order.remove_item("Missing")
        self.regular_order.add_item("Existing", 10)
        with self.assertRaises(ValueError):
            self.regular_order.remove_item("Existing", quantity=0)
        self.regular_order.remove_item("Existing")

        self.assertEqual(self.regular_order.items, {})
        self.assertEqual(self.regular_order.status, "PENDING")
        self.assertIsNone(self.regular_order.applied_coupon)
        self.assertEqual(self.regular_order.subtotal, 0.0)
        self.assertEqual(self.regular_order.discount_amount, 0.0)
        self.assertEqual(self.regular_order.tax_amount, 0.0)
        self.assertEqual(self.regular_order.shipping_fee, 0.0)
        self.assertEqual(self.regular_order.final_total, 0.0)


if __name__ == "__main__":
    unittest.main()
